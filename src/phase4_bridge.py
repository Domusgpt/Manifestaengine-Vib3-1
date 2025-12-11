"""Phase 4 integration bridge utilities.

This module routes validated Signal Bus envelopes to downstream bridge sinks
(Unity/Unreal, design-tool overlays, holographic clients) while preserving the
minimal parameter set and derived metrics. Dispatch is asynchronous to align
with the schema-backed JSON I/O requirements for Phase 4.
"""
from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Protocol

from src.phase3_validator import ValidationError, validate_envelope

MinimalParameters = Mapping[str, Any]


class BridgeSink(Protocol):
    """Protocol for downstream bridge sinks."""

    name: str

    async def send(self, envelope: Mapping[str, Any], context: "BridgeContext") -> None:
        ...


@dataclass
class BridgeContext:
    """Context for bridge dispatches with capability overlays."""

    session_id: str
    sdk_surface: str
    capabilities: Mapping[str, Any]
    started_at: float = field(default_factory=time.monotonic)

    def metadata(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "sdk_surface": self.sdk_surface,
            "capabilities": self.capabilities,
        }


def _extract_minimal_parameters(kind: str, payload: Mapping[str, Any]) -> MinimalParameters:
    if kind == "event.v1":
        return payload.get("payload", {})
    if kind == "agent_frame.v1":
        return payload.get("inputs", {})
    if kind == "render_config.v1":
        return payload.get("inputs", {})
    if kind == "holo_intent":
        render_config = payload.get("render_config", {})
        return render_config.get("inputs", {})
    raise ValidationError(f"Unsupported envelope kind: {kind}")


def derived_metrics(minimal: MinimalParameters) -> Dict[str, Any]:
    pointer = minimal.get("POINTER_DELTA", {})
    dx = float(pointer.get("dx", 0))
    dy = float(pointer.get("dy", 0))
    pointer_norm = math.hypot(dx, dy)

    zoom_delta = float(minimal.get("ZOOM_DELTA", 0))
    rotation_delta = float(minimal.get("ROT_DELTA", 0))
    triggered = bool(minimal.get("INPUT_TRIGGER", False))

    return {
        "pointer_norm": pointer_norm,
        "zoom_delta": zoom_delta,
        "rotation_delta": rotation_delta,
        "triggered": triggered,
    }


class BridgeRouter:
    """Asynchronous dispatcher for validated envelopes."""

    def __init__(self, sinks: Iterable[BridgeSink] | None = None) -> None:
        self._sinks: MutableMapping[str, BridgeSink] = {}
        if sinks:
            for sink in sinks:
                self.add_sink(sink)

    @property
    def sinks(self) -> Mapping[str, BridgeSink]:
        return dict(self._sinks)

    def add_sink(self, sink: BridgeSink) -> None:
        if sink.name in self._sinks:
            raise ValidationError(f"Duplicate sink name: {sink.name}")
        self._sinks[sink.name] = sink

    async def dispatch(self, kind: str, payload: Mapping[str, Any], context: BridgeContext) -> None:
        validate_envelope(kind, payload)
        minimal = _extract_minimal_parameters(kind, payload)
        metrics = derived_metrics(minimal)

        envelope = {
            "kind": kind,
            "payload": payload,
            "derived": metrics,
            "context": context.metadata(),
            "bridged_at": time.monotonic(),
        }

        await asyncio.gather(*(sink.send(envelope, context) for sink in self._sinks.values()))


@dataclass
class InMemorySink:
    """Test sink that records envelopes for assertions."""

    name: str
    received: list[Mapping[str, Any]] = field(default_factory=list)

    async def send(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        self.received.append({"envelope": envelope, "context": context})
