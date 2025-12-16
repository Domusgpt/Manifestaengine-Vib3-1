"""Phase 6 performance CLI helpers for structured bridge logs."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterable, Mapping, MutableMapping

from src.phase3_validator import ValidationError
from src.phase4_bridge import BridgeContext
from src.phase6_performance import PerformanceMonitor


def _hydrate_payload(
    kind: str, minimal: Mapping[str, Any], timestamp: float, *, sdk_surface: str
) -> Mapping[str, Any]:
    """Rebuild a minimal payload into a validation-friendly envelope payload."""

    normalized = _normalize_minimal(minimal)

    if kind == "event.v1":
        return {
            "type": "observed",
            "timestamp": timestamp,
            "payload": normalized,
        }

    if kind == "agent_frame.v1":
        return {
            "role": "observer",
            "goal": "latency_replay",
            "sdk_surface": sdk_surface,
            "bounds": {"x": 0.0, "y": 0.0, "z": 0.0},
            "focus": {"path": "observed"},
            "inputs": normalized,
            "outputs": ["telemetry"],
            "safety": {"spawn_bounds": 0.0, "rate_limit": 0.0, "rejection_reason": ""},
        }

    if kind == "render_config.v1":
        return {
            "surface": sdk_surface,
            "schema": "observed",
            "inputs": normalized,
            "overlays": {"capability": bool(minimal)},
        }

    if kind == "holo_intent":
        return {
            "holo_frame": "observed",
            "sdk_surface": sdk_surface,
            "render_config": {
                "surface": sdk_surface,
                "schema": "observed",
                "inputs": normalized,
                "overlays": {"capability": bool(minimal)},
            },
            "alignment": {"quaternion": [0.0, 0.0, 0.0, 1.0], "translation": [0.0, 0.0, 0.0]},
        }

    raise ValidationError(f"Unsupported envelope kind: {kind}")


def _context_from_log(entry: Mapping[str, Any]) -> BridgeContext:
    """Construct a BridgeContext from a structured log entry."""

    session_id = str(entry.get("session_id", "unknown"))
    sdk_surface = str(entry.get("sdk_surface", "unknown"))
    capabilities = entry.get("capabilities") or {}
    return BridgeContext(session_id=session_id, sdk_surface=sdk_surface, capabilities=capabilities)


def _timestamp_from_log(entry: Mapping[str, Any]) -> float:
    minimal = entry.get("minimal", {})
    ts = None
    if isinstance(minimal, Mapping) and "timestamp" in minimal:
        ts = minimal.get("timestamp")
    if ts is None:
        ts = entry.get("bridged_at") or entry.get("timestamp")
    try:
        return float(ts)
    except (TypeError, ValueError):
        return 0.0


def _normalize_minimal(minimal: Mapping[str, Any]) -> Mapping[str, Any]:
    base = dict(minimal)
    pointer = base.get("POINTER_DELTA") if isinstance(base.get("POINTER_DELTA"), Mapping) else {}
    pointer_dx = pointer.get("dx", 0.0)
    pointer_dy = pointer.get("dy", 0.0)

    normalized = {
        **base,
        "POINTER_DELTA": {"dx": pointer_dx, "dy": pointer_dy},
        "ZOOM_DELTA": base.get("ZOOM_DELTA", 0.0),
        "ROT_DELTA": base.get("ROT_DELTA", 0.0),
        "INPUT_TRIGGER": base.get("INPUT_TRIGGER", False),
    }
    return normalized


def performance_report(log_lines: Iterable[str]) -> Mapping[str, Any]:
    """Generate latency metrics from structured logs."""

    overall_monitor = PerformanceMonitor()
    per_kind: MutableMapping[str, PerformanceMonitor] = {}
    ingested = 0

    for line in log_lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        kind = entry.get("kind")
        minimal = entry.get("minimal")
        if not kind or minimal is None:
            raise ValidationError("Structured log line missing required fields")

        timestamp = _timestamp_from_log(entry)
        context = _context_from_log(entry)
        payload = _hydrate_payload(kind, minimal, timestamp, sdk_surface=context.sdk_surface)

        overall_monitor.ingest(kind, payload, context)
        per_kind.setdefault(kind, PerformanceMonitor()).ingest(kind, payload, context)
        ingested += 1

    return {
        "ingested": ingested,
        "overall": {"samples": len(overall_monitor.buffer), **overall_monitor.latency_metrics()},
        "by_kind": {
            kind: {"samples": len(monitor.buffer), **monitor.latency_metrics()} for kind, monitor in per_kind.items()
        },
    }


def _load_file(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.readlines()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Phase 6 latency reports from structured bridge logs."
    )
    parser.add_argument("logfile", nargs="?", help="Path to a structured log file. Reads stdin when omitted.")
    args = parser.parse_args(argv)

    lines = _load_file(args.logfile) if args.logfile else sys.stdin.readlines()
    report = performance_report(lines)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
