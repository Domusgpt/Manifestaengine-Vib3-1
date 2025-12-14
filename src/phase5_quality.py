"""Phase 5 quality, observability, and replay helpers.

These utilities layer structured logging, health pulses, and deterministic
replay exports on top of the Phase 4 bridge router. They keep the minimal
parameter set and derived metrics visible to downstream operators while
preserving schema validation performed earlier in the pipeline.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence

from src.phase3_validator import validate_envelope
from src.phase4_bridge import (
    BridgeContext,
    BridgeRouter,
    ReplayRecorder,
    TransportSink,
    _extract_minimal_parameters,
    derived_metrics,
)

Writer = Callable[[str], None]


@dataclass
class StructuredLogger:
    """Emit line-delimited JSON records for bridge dispatches."""

    writer: Writer

    def log(self, sink: str, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        payload = envelope.get("payload", {})
        kind = envelope.get("kind", "unknown")
        minimal = _extract_minimal(payload)
        record = {
            "timestamp": time.time(),
            "sink": sink,
            "kind": kind,
            "session_id": context.session_id,
            "sdk_surface": context.sdk_surface,
            "capabilities": context.capabilities,
            "derived": envelope.get("derived") or derived_metrics(minimal),
            "minimal": minimal,
            "bridged_at": envelope.get("bridged_at"),
        }
        self.writer(json.dumps(record))


def _extract_minimal(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    candidates = (
        payload.get("payload"),
        payload.get("inputs"),
        payload.get("render_config", {}).get("inputs") if isinstance(payload.get("render_config"), Mapping) else None,
    )
    for candidate in candidates:
        if isinstance(candidate, Mapping) and candidate:
            return candidate
    return {}


@dataclass
class HealthMonitor:
    """Track per-sink health metrics for operational visibility."""

    sink_stats: MutableMapping[str, MutableMapping[str, Any]] = field(default_factory=dict)
    error_log: list[Mapping[str, Any]] = field(default_factory=list)

    def record(self, sink: str, status: str, *, error: str | None = None) -> None:
        stats = self.sink_stats.setdefault(
            sink,
            {
                "dispatched": 0,
                "rate_limited": 0,
                "errors": 0,
                "last_updated": None,
            },
        )
        if status not in ("dispatched", "rate_limited", "error"):
            raise ValueError("Unknown status provided")

        if status == "dispatched":
            stats["dispatched"] += 1
        elif status == "rate_limited":
            stats["rate_limited"] += 1
        else:
            stats["errors"] += 1
        stats["last_updated"] = time.monotonic()

        if error:
            self.error_log.append({"sink": sink, "error": error, "recorded_at": time.monotonic()})

    def pulse(self) -> Mapping[str, Any]:
        return {
            "timestamp": time.monotonic(),
            "sinks": {
                name: {
                    "dispatched": stats["dispatched"],
                    "rate_limited": stats["rate_limited"],
                    "errors": stats["errors"],
                    "last_updated": stats["last_updated"],
                }
                for name, stats in self.sink_stats.items()
            },
            "errors": list(self.error_log),
        }


class ObservedRouter(BridgeRouter):
    """Bridge router with structured logging, health, and optional replay."""

    def __init__(
        self,
        *,
        logger: StructuredLogger,
        monitor: HealthMonitor,
        recorder: ReplayRecorder | None = None,
        sinks: Iterable[Any] | None = None,
    ) -> None:
        super().__init__(sinks)
        self.logger = logger
        self.monitor = monitor
        self.recorder = recorder

    async def dispatch(self, kind: str, payload: Mapping[str, Any], context: BridgeContext) -> None:  # type: ignore[override]
        validate_envelope(kind, payload)
        minimal = _extract_minimal_parameters(kind, payload)
        derived = derived_metrics(minimal)
        envelope = {
            "kind": kind,
            "payload": payload,
            "derived": derived,
            "context": context.metadata(),
            "bridged_at": time.monotonic(),
        }

        await asyncio.gather(
            *(self._send_observed(sink, envelope, context, minimal) for sink in self._sinks.values())
        )

    async def _send_observed(
        self, sink: Any, envelope: Mapping[str, Any], context: BridgeContext, minimal: Mapping[str, Any]
    ) -> None:
        dispatched = False
        rate_limited = False

        original_hook = getattr(sink, "status_hook", None) if isinstance(sink, TransportSink) else None

        def _hook(name: str, status: str, error: str | None) -> None:
            nonlocal dispatched, rate_limited
            if status == "dispatched":
                dispatched = True
            elif status == "rate_limited":
                rate_limited = True
            self.monitor.record(name, status if status in {"dispatched", "rate_limited"} else "error", error=error)

        if isinstance(sink, TransportSink):
            sink.status_hook = _hook

        try:
            await sink.send(envelope, context)
            if not isinstance(sink, TransportSink):
                dispatched = True
                self.monitor.record(sink.name, "dispatched")
            if dispatched:
                self.logger.log(sink.name, envelope, context)
                if self.recorder:
                    self.recorder.record(sink.name, envelope)
        except Exception as exc:  # pragma: no cover - exercised via tests
            if not isinstance(sink, TransportSink):
                self.monitor.record(sink.name, "error", error=str(exc))
            raise
        finally:
            if isinstance(sink, TransportSink):
                sink.status_hook = original_hook
            if rate_limited and not dispatched:
                self.logger.writer(
                    json.dumps(
                        {
                            "timestamp": time.time(),
                            "sink": sink.name,
                            "kind": envelope.get("kind", "unknown"),
                            "session_id": context.session_id,
                            "sdk_surface": context.sdk_surface,
                            "capabilities": context.capabilities,
                            "minimal": minimal,
                            "status": "rate_limited",
                        }
                    )
                )


def replay_summary(recorder: ReplayRecorder) -> Mapping[str, Any]:
    """Summarize recorded replay frames with deterministic ordering."""

    frames = list(recorder.frames)
    sink_counts: MutableMapping[str, int] = {}
    for frame in frames:
        sink_counts[frame.get("sink", "unknown")] = sink_counts.get(frame.get("sink", "unknown"), 0) + 1

    durations = _frame_gaps([frame.get("received_at") for frame in frames])
    return {
        "frames": len(frames),
        "sinks": sink_counts,
        "duration": durations["duration"],
        "max_gap": durations["max_gap"],
    }


def export_replay(recorder: ReplayRecorder, writer: Writer) -> None:
    """Export replay frames as line-delimited JSON ordered by receipt time."""

    for frame in sorted(recorder.frames, key=lambda entry: entry.get("received_at", 0)):
        writer(json.dumps(frame))


def _frame_gaps(timestamps: Sequence[float | None]) -> Mapping[str, float]:
    valid = [ts for ts in timestamps if isinstance(ts, (int, float))]
    if not valid:
        return {"duration": 0.0, "max_gap": 0.0}

    start, end = min(valid), max(valid)
    sorted_ts = sorted(valid)
    gaps = [b - a for a, b in zip(sorted_ts, sorted_ts[1:])]
    return {
        "duration": end - start,
        "max_gap": max(gaps) if gaps else 0.0,
    }
