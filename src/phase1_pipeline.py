"""
Phase 1/2 processing pipeline that normalizes minimal parameters, computes
derived metrics, and synchronizes frames with HOLO frame metadata.

This module builds on the Phase 0 telemetry service to provide a concrete,
asynchronous processing layer that can be reused by higher phases. The
implementation intentionally keeps state in memory while exposing deterministic
JSON exports for replay or downstream SDK consumption.
"""
from __future__ import annotations

import asyncio
import json
import math
from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

from .phase0_baseline import TelemetryEvent, TelemetryService, ValidationError

MinimalPayload = Mapping[str, Any]
DerivedMetrics = Dict[str, float]
HOLOQuaternion = Sequence[float]
HOLOTranslation = Sequence[float]


@dataclass
class ProcessedFrame:
    """Normalized frame containing minimal parameters and derived metrics."""

    source: str
    minimal: Dict[str, Any]
    derived: DerivedMetrics
    timestamp: float = field(default_factory=monotonic)
    holo_frame: str | None = None
    alignment: Dict[str, Sequence[float]] | None = None

    def to_json(self) -> str:
        payload: Dict[str, Any] = {
            "source": self.source,
            "timestamp": self.timestamp,
            "minimal": self.minimal,
            "derived": self.derived,
        }
        if self.holo_frame and self.alignment:
            payload["holo_frame"] = self.holo_frame
            payload["alignment"] = self.alignment
        return json.dumps(payload)


def compute_derived_metrics(payload: MinimalPayload) -> DerivedMetrics:
    """Compute derived metrics from the minimal parameter surface."""

    pointer = payload.get("POINTER_DELTA", {})
    dx = float(pointer.get("dx", 0.0))
    dy = float(pointer.get("dy", 0.0))
    zoom = float(payload.get("ZOOM_DELTA", 0.0))
    rotation = float(payload.get("ROT_DELTA", 0.0))

    pointer_magnitude = math.hypot(dx, dy)
    pointer_angle = math.atan2(dy, dx) if pointer_magnitude else 0.0

    return {
        "pointer_magnitude": pointer_magnitude,
        "pointer_angle": pointer_angle,
        "zoom_velocity": zoom,
        "rotation_velocity": rotation,
    }


class Phase1Normalizer:
    """Subscribe to telemetry events and normalize them into ProcessedFrames."""

    def __init__(self, service: TelemetryService) -> None:
        self._service = service
        self._queue = service.subscribe()

    async def drain(self, limit: int | None = None, timeout: float | None = None) -> List[ProcessedFrame]:
        frames: List[ProcessedFrame] = []
        deadline = monotonic() + timeout if timeout else None

        while True:
            if deadline is not None and monotonic() >= deadline:
                break
            if limit is not None and len(frames) >= limit:
                break

            try:
                event: TelemetryEvent = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            except asyncio.TimeoutError:
                break

            minimal = _extract_minimal(event.payload)
            derived = compute_derived_metrics(minimal)
            frames.append(ProcessedFrame(source=event.kind, minimal=minimal, derived=derived, timestamp=event.timestamp))

        return frames

    async def flush(self, limit: int | None = None) -> List[ProcessedFrame]:
        """Drain all currently buffered telemetry events without blocking."""

        frames: List[ProcessedFrame] = []
        while not self._queue.empty():
            if limit is not None and len(frames) >= limit:
                break
            event = await self._queue.get()
            minimal = _extract_minimal(event.payload)
            derived = compute_derived_metrics(minimal)
            frames.append(ProcessedFrame(source=event.kind, minimal=minimal, derived=derived, timestamp=event.timestamp))
        return frames


def _extract_minimal(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Extract the minimal parameter set from a validated event payload."""

    envelope_payload = payload.get("payload") if "payload" in payload else payload
    if not isinstance(envelope_payload, Mapping):
        raise ValidationError("Payload must be a mapping containing minimal parameters")

    required_keys = {"POINTER_DELTA", "ZOOM_DELTA", "ROT_DELTA", "INPUT_TRIGGER"}
    missing = required_keys - envelope_payload.keys()
    if missing:
        raise ValidationError(f"Missing minimal parameters: {sorted(missing)}")

    pointer_delta = envelope_payload.get("POINTER_DELTA", {})
    if not isinstance(pointer_delta, Mapping):
        raise ValidationError("POINTER_DELTA must be an object")

    return {
        "POINTER_DELTA": {"dx": float(pointer_delta.get("dx", 0.0)), "dy": float(pointer_delta.get("dy", 0.0))},
        "ZOOM_DELTA": float(envelope_payload.get("ZOOM_DELTA", 0.0)),
        "ROT_DELTA": float(envelope_payload.get("ROT_DELTA", 0.0)),
        "INPUT_TRIGGER": bool(envelope_payload.get("INPUT_TRIGGER", False)),
    }


def attach_holo_alignment(
    frame: ProcessedFrame,
    holo_frame: str,
    quaternion: HOLOQuaternion,
    translation: HOLOTranslation,
) -> ProcessedFrame:
    """Return a new frame augmented with HOLO frame alignment metadata."""

    if len(quaternion) != 4:
        raise ValidationError("Quaternion must contain 4 entries")
    if len(translation) != 3:
        raise ValidationError("Translation must contain 3 entries")

    for index, value in enumerate(quaternion):
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Quaternion index {index} must be numeric")
    for index, value in enumerate(translation):
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Translation index {index} must be numeric")

    aligned = ProcessedFrame(
        source=frame.source,
        minimal=dict(frame.minimal),
        derived=dict(frame.derived),
        timestamp=frame.timestamp,
        holo_frame=holo_frame,
        alignment={"quaternion": list(quaternion), "translation": list(translation)},
    )
    return aligned


def export_frames(frames: Iterable[ProcessedFrame]) -> str:
    """Export frames into a deterministic JSONL blob."""

    lines = [frame.to_json() for frame in frames]
    return "\n".join(lines)


async def replay_frames(frames: Iterable[ProcessedFrame], consumer: Any) -> None:
    """Replay processed frames to a callable or coroutine consumer."""

    for frame in frames:
        result = consumer(frame)
        if asyncio.iscoroutine(result):
            await result
        await asyncio.sleep(0)


async def build_normalized_stream(
    service: TelemetryService,
    imu_samples: Iterable[Tuple[float, float, float]],
    presses: Iterable[bool],
    zoom_values: Iterable[float],
) -> List[ProcessedFrame]:
    """Produce a set of processed frames from the baseline emitters."""

    normalizer = Phase1Normalizer(service)
    await _wrap_producer(service, imu_samples, presses, zoom_values)
    return await normalizer.flush(limit=32)


async def _wrap_producer(
    service: TelemetryService,
    imu_samples: Iterable[Tuple[float, float, float]],
    presses: Iterable[bool],
    zoom_values: Iterable[float],
) -> None:
    from .phase0_baseline import gamepad_emitter, osc_midi_emitter, wearable_imu_emitter

    await asyncio.gather(
        wearable_imu_emitter(service, imu_samples),
        gamepad_emitter(service, presses),
        osc_midi_emitter(service, zoom_values),
    )
