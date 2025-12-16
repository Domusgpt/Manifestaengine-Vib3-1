"""Phase 4 integration bridge utilities.

This module routes validated Signal Bus envelopes to downstream bridge sinks
(Unity/Unreal, design-tool overlays, holographic clients) while preserving the
minimal parameter set and derived metrics. Dispatch is asynchronous to align
with the schema-backed JSON I/O requirements for Phase 4.
"""
from __future__ import annotations

import asyncio
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Iterable, Mapping, MutableMapping, Protocol

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
    if kind == "holo_frame.v1":
        return payload.get("inputs", {})
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


@dataclass
class RateLimiter:
    """Token bucket rate limiter for transport sinks."""

    rate_per_sec: float
    burst: int = 1
    _tokens: float = field(init=False)
    _last_checked: float = field(default_factory=time.monotonic, init=False)

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        self._tokens = float(self.burst)

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self._last_checked
        self._last_checked = now

        self._tokens = min(self.burst, self._tokens + elapsed * self.rate_per_sec)
        if self._tokens < 1:
            return False

        self._tokens -= 1
        return True


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


@dataclass
class ReplayRecorder:
    """Deterministic replay recorder for dispatched envelopes."""

    frames: list[Mapping[str, Any]] = field(default_factory=list)

    def record(self, sink: str, envelope: Mapping[str, Any]) -> None:
        self.frames.append(
            {
                "sink": sink,
                "envelope": envelope,
                "received_at": time.monotonic(),
            }
        )


class TransportSink(BridgeSink):
    """Base sink that adds rate limits, error logging, and replay hooks."""

    name: str

    def __init__(
        self,
        name: str,
        rate_limiter: RateLimiter | None = None,
        error_log: list[Mapping[str, Any]] | None = None,
        recorder: ReplayRecorder | None = None,
        status_hook: Callable[[str, str, str | None], None] | None = None,
    ) -> None:
        self.name = name
        self.rate_limiter = rate_limiter
        self.error_log = error_log if error_log is not None else []
        self.recorder = recorder
        self.status_hook = status_hook

    async def send(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        if self.rate_limiter and not self.rate_limiter.allow():
            self.error_log.append(
                {
                    "sink": self.name,
                    "error": "rate_limited",
                    "context": context.metadata(),
                }
            )
            if self.status_hook:
                self.status_hook(self.name, "rate_limited", "rate_limited")
            return

        try:
            await self.send_data(envelope, context)
            if self.status_hook:
                self.status_hook(self.name, "dispatched", None)
            if self.recorder:
                self.recorder.record(self.name, envelope)
        except Exception as exc:  # pragma: no cover - exercised via tests
            self.error_log.append(
                {
                    "sink": self.name,
                    "error": str(exc),
                    "context": context.metadata(),
                }
            )
            if self.status_hook:
                self.status_hook(self.name, "error", str(exc))

    async def send_data(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        raise NotImplementedError


class UDPSink(TransportSink):
    """UDP adapter that emits JSON envelopes to a host/port pair."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        sender: Callable[[str, int, bytes], Awaitable[None]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self.host = host
        self.port = port
        self._sender = sender or self._default_sender

    async def _default_sender(self, host: str, port: int, payload: bytes) -> None:
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(lambda: asyncio.DatagramProtocol(), remote_addr=(host, port))
        try:
            transport.sendto(payload)
        finally:
            transport.close()

    async def send_data(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        payload = json.dumps({"context": context.metadata(), "envelope": envelope}).encode("utf-8")
        await self._sender(self.host, self.port, payload)


class OSCSink(TransportSink):
    """OSC adapter built on top of UDP packets with address patterns."""

    def __init__(
        self,
        name: str,
        address: str,
        udp_sink: UDPSink,
        encoder: Callable[[str, Mapping[str, Any]], bytes] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self.address = address
        self.udp_sink = udp_sink
        self.encoder = encoder or self._encode

    def _encode(self, address: str, envelope: Mapping[str, Any]) -> bytes:
        return json.dumps({"address": address, "envelope": envelope}).encode("utf-8")

    async def send_data(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        payload = self.encoder(self.address, {"context": context.metadata(), "payload": envelope})
        await self.udp_sink._sender(self.udp_sink.host, self.udp_sink.port, payload)


class GRPCSink(TransportSink):
    """Lightweight gRPC-style adapter using an async callable stub."""

    def __init__(
        self,
        name: str,
        stub: Callable[[Mapping[str, Any]], Awaitable[None]],
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self.stub = stub

    async def send_data(self, envelope: Mapping[str, Any], context: BridgeContext) -> None:
        payload = {"context": context.metadata(), "envelope": envelope, "capabilities": context.capabilities}
        await self.stub(payload)
