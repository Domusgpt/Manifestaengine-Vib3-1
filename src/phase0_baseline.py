"""
Phase 0 baseline telemetry, schemas, and deterministic replay helpers.

The intent is to provide a concrete, testable implementation of the minimal
parameter surface (POINTER_DELTA, ZOOM_DELTA, ROT_DELTA, INPUT_TRIGGER) that can
feed basic telemetry services and deterministic replays. All functionality is
pure Python to avoid external runtime dependencies while still delivering a
real, executable baseline that later phases can extend.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from time import monotonic
from typing import Any, AsyncIterator, Callable, Dict, Iterable, List, Mapping, Tuple


class ValidationError(Exception):
    """Raised when a payload fails validation."""


MinimalPayload = Mapping[str, Any]
EventPayload = Mapping[str, Any]
AgentFramePayload = Mapping[str, Any]


REQUIRED_MINIMAL_KEYS = {"POINTER_DELTA", "ZOOM_DELTA", "ROT_DELTA", "INPUT_TRIGGER"}


def _assert_number(value: Any, path: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a number")


def _assert_bool(value: Any, path: str) -> None:
    if not isinstance(value, bool):
        raise ValidationError(f"{path} must be a boolean")


def _assert_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return value


def validate_minimal_parameters(payload: MinimalPayload) -> None:
    data = _assert_mapping(payload, "payload")
    missing = REQUIRED_MINIMAL_KEYS - data.keys()
    if missing:
        raise ValidationError(f"Missing minimal parameters: {sorted(missing)}")

    pointer = _assert_mapping(data.get("POINTER_DELTA"), "POINTER_DELTA")
    for axis in ("dx", "dy"):
        _assert_number(pointer.get(axis), f"POINTER_DELTA.{axis}")

    _assert_number(data.get("ZOOM_DELTA"), "ZOOM_DELTA")
    _assert_number(data.get("ROT_DELTA"), "ROT_DELTA")
    _assert_bool(data.get("INPUT_TRIGGER"), "INPUT_TRIGGER")


def validate_event(event: EventPayload) -> None:
    data = _assert_mapping(event, "event")
    validate_minimal_parameters(data.get("payload", {}))
    _assert_number(data.get("timestamp"), "timestamp")
    if not isinstance(data.get("type"), str) or not data["type"].strip():
        raise ValidationError("type must be a non-empty string")


def validate_agent_frame(frame: AgentFramePayload) -> None:
    data = _assert_mapping(frame, "agent_frame")
    validate_minimal_parameters(data.get("inputs", {}))
    for key in ("role", "goal", "sdk_surface"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValidationError(f"{key} must be a non-empty string")

    bounds = _assert_mapping(data.get("bounds"), "bounds")
    for axis in ("x", "y", "z"):
        _assert_number(bounds.get(axis), f"bounds.{axis}")

    focus = _assert_mapping(data.get("focus"), "focus")
    if not isinstance(focus.get("path"), str) or not focus["path"].strip():
        raise ValidationError("focus.path must be a non-empty string")


@dataclass
class TelemetryEvent:
    """Normalized telemetry event used by the in-memory service."""

    kind: str
    payload: Dict[str, Any]
    timestamp: float

    def to_json(self) -> str:
        return json.dumps({"type": self.kind, "payload": self.payload, "timestamp": self.timestamp})


class TelemetryService:
    """In-memory telemetry distribution service with validation."""

    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue[TelemetryEvent]] = []

    def subscribe(self) -> "asyncio.Queue[TelemetryEvent]":
        queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    async def publish(self, kind: str, payload: Mapping[str, Any]) -> TelemetryEvent:
        if kind == "event.v1":
            validate_event(payload)
        elif kind == "agent_frame.v1":
            validate_agent_frame(payload)
        else:
            raise ValidationError(f"Unsupported telemetry kind: {kind}")

        event = TelemetryEvent(kind=kind, payload=dict(payload), timestamp=monotonic())
        for queue in self._subscribers:
            await queue.put(event)
        return event


async def wearable_imu_emitter(service: TelemetryService, samples: Iterable[Tuple[float, float, float]]) -> None:
    """Emit POINTER_DELTA updates based on IMU-like dx/dy and rotation triples."""

    for dx, dy, rot in samples:
        payload = {
            "type": "imu_frame",
            "timestamp": monotonic(),
            "payload": {
                "POINTER_DELTA": {"dx": dx, "dy": dy},
                "ZOOM_DELTA": 0.0,
                "ROT_DELTA": rot,
                "INPUT_TRIGGER": False,
            },
        }
        await service.publish("event.v1", payload)


async def gamepad_emitter(service: TelemetryService, presses: Iterable[bool]) -> None:
    """Emit INPUT_TRIGGER toggles from a gamepad button."""

    for pressed in presses:
        payload = {
            "type": "gamepad_button",
            "timestamp": monotonic(),
            "payload": {
                "POINTER_DELTA": {"dx": 0.0, "dy": 0.0},
                "ZOOM_DELTA": 0.0,
                "ROT_DELTA": 0.0,
                "INPUT_TRIGGER": pressed,
            },
        }
        await service.publish("event.v1", payload)


async def osc_midi_emitter(service: TelemetryService, zoom_values: Iterable[float]) -> None:
    """Emit ZOOM_DELTA samples mimicking OSC/MIDI control input."""

    for zoom in zoom_values:
        payload = {
            "type": "osc_midi",
            "timestamp": monotonic(),
            "payload": {
                "POINTER_DELTA": {"dx": 0.0, "dy": 0.0},
                "ZOOM_DELTA": zoom,
                "ROT_DELTA": 0.0,
                "INPUT_TRIGGER": False,
            },
        }
        await service.publish("event.v1", payload)


class ReplayHarness:
    """Record and replay telemetry events deterministically."""

    def __init__(self) -> None:
        self._recorded: List[TelemetryEvent] = []

    def record(self, event: TelemetryEvent) -> None:
        self._recorded.append(event)

    def frames(self) -> List[TelemetryEvent]:
        return list(self._recorded)

    async def replay(self, consumer: Callable[[TelemetryEvent], Any]) -> None:
        for event in self._recorded:
            result = consumer(event)
            if asyncio.iscoroutine(result):
                await result
            await asyncio.sleep(0)


async def deterministic_service_pipeline(
    imu_samples: Iterable[Tuple[float, float, float]],
    presses: Iterable[bool],
    zoom_values: Iterable[float],
) -> Tuple[ReplayHarness, List[TelemetryEvent]]:
    """Spin up a telemetry service, emit baseline streams, and return recorded frames."""

    service = TelemetryService()
    replay = ReplayHarness()
    sink = service.subscribe()

    producers = (
        wearable_imu_emitter(service, imu_samples),
        gamepad_emitter(service, presses),
        osc_midi_emitter(service, zoom_values),
    )

    await asyncio.gather(*producers)

    events: List[TelemetryEvent] = []
    while not sink.empty():
        event = await sink.get()
        replay.record(event)
        events.append(event)
    return replay, events
