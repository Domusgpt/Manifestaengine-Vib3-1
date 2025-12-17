"""Phase 6 performance and latency hardening utilities."""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Mapping, MutableSequence, Sequence

from src.phase3_validator import ValidationError, validate_envelope
from src.phase4_bridge import BridgeContext, derived_metrics, _extract_minimal_parameters


@dataclass
class TelemetrySample:
    """Recorded telemetry sample with latency/derived metrics."""

    kind: str
    timestamp: float
    received_at: float
    latency: float
    minimal: Mapping[str, object]
    derived: Mapping[str, object]
    capabilities: Mapping[str, object]


@dataclass
class TelemetryBuffer:
    """Ring buffer for high-frequency telemetry samples."""

    capacity: int
    samples: MutableSequence[TelemetrySample] = field(default_factory=list)

    def append(self, sample: TelemetrySample) -> None:
        if self.capacity <= 0:
            return
        if len(self.samples) >= self.capacity:
            self.samples.pop(0)
        self.samples.append(sample)

    def __iter__(self):  # pragma: no cover - trivial
        return iter(self.samples)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.samples)


class PerformanceMonitor:
    """Aggregates latency metrics for minimal-parameter envelopes."""

    def __init__(self, *, buffer_capacity: int = 256) -> None:
        self.buffer = TelemetryBuffer(buffer_capacity)

    def ingest(self, kind: str, payload: Mapping[str, object], context: BridgeContext) -> TelemetrySample:
        """Validate and record a telemetry sample with derived metrics and latency."""

        validate_envelope(kind, payload)
        source_ts = float(payload.get("timestamp", time.monotonic()))
        received_at = time.monotonic()
        minimal = _extract_minimal_parameters(kind, payload)
        derived = derived_metrics(minimal)
        latency = max(0.0, received_at - source_ts)

        sample = TelemetrySample(
            kind=kind,
            timestamp=source_ts,
            received_at=received_at,
            latency=latency,
            minimal=minimal,
            derived=derived,
            capabilities=context.capabilities,
        )
        self.buffer.append(sample)
        return sample

    def latency_metrics(self) -> Mapping[str, float]:
        """Compute latency aggregates (mean, max, jitter) from the buffer."""

        latencies = [sample.latency for sample in self.buffer.samples]
        if not latencies:
            return {"mean_ms": 0.0, "max_ms": 0.0, "jitter_ms": 0.0}

        mean = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        jitter = math.sqrt(sum((lat - mean) ** 2 for lat in latencies) / len(latencies))
        return {"mean_ms": mean * 1000.0, "max_ms": max_latency * 1000.0, "jitter_ms": jitter * 1000.0}

    def export_samples(self) -> Sequence[Mapping[str, object]]:
        """Export buffered samples for replay or downstream processing."""

        return [
            {
                "kind": sample.kind,
                "timestamp": sample.timestamp,
                "received_at": sample.received_at,
                "latency": sample.latency,
                "minimal": sample.minimal,
                "derived": sample.derived,
                "capabilities": sample.capabilities,
            }
            for sample in self.buffer.samples
        ]

    def assert_capacity(self) -> None:
        """Ensure the buffer can store at least one sample."""

        if self.buffer.capacity <= 0:
            raise ValidationError("Buffer capacity must be positive for telemetry monitoring")
