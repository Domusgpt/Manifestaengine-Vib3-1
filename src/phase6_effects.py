"""Phase 6 advanced effect simulation utilities.

This module introduces a deterministic effect engine that layers field, cloth,
and particle-style energies on top of the minimal parameter set. The simulator
keeps derived metrics visible, respects capability overlays from the
``BridgeContext``, and emits tile-oriented slices suitable for volumetric or
holographic exports. Payloads are validated with the existing Phase 3 schema
guards to remain aligned with the Signal Bus envelopes.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, MutableMapping, Sequence

from src.phase3_validator import validate_envelope
from src.phase4_bridge import BridgeContext, derived_metrics, _extract_minimal_parameters


@dataclass
class EffectLayer:
    """Feature-flagged effect layer with adjustable intensity."""

    name: str
    enabled: bool = True
    intensity: float = 1.0


@dataclass
class EffectFrame:
    """Structured frame output for effect tiles."""

    frame_id: int
    surface: str
    timestamp: float
    minimal: Mapping[str, object]
    derived: Mapping[str, object]
    tiles: Sequence[Mapping[str, object]]
    capabilities: Mapping[str, object]


@dataclass
class EffectEngine:
    """Deterministic effect simulator for Phase 6 surfaces."""

    layers: Sequence[EffectLayer]
    tile_span: int = 4
    frames: list[EffectFrame] = field(default_factory=list)

    def generate_frame(
        self, kind: str, payload: Mapping[str, object], context: BridgeContext, *, surface: str = "holographic"
    ) -> EffectFrame:
        """Validate input envelopes and produce a deterministic effect frame."""

        validate_envelope(kind, payload)
        minimal = _extract_minimal_parameters(kind, payload)
        derived = derived_metrics(minimal)

        frame_id = len(self.frames)
        base_energy = self._base_energy(derived)
        tiles = tuple(self._build_tiles(base_energy, surface))
        frame = EffectFrame(
            frame_id=frame_id,
            surface=surface,
            timestamp=time.monotonic(),
            minimal=minimal,
            derived=derived,
            tiles=tiles,
            capabilities=context.capabilities,
        )
        self.frames.append(frame)
        return frame

    def export_frames(self, writer: Callable[[str], None]) -> None:
        """Export accumulated frames as line-delimited JSON ordered by frame id."""

        for frame in sorted(self.frames, key=lambda item: item.frame_id):
            writer(
                json.dumps(
                    {
                        "frame_id": frame.frame_id,
                        "surface": frame.surface,
                        "timestamp": frame.timestamp,
                        "minimal": frame.minimal,
                        "derived": frame.derived,
                        "tiles": frame.tiles,
                        "capabilities": frame.capabilities,
                    }
                )
            )

    def _base_energy(self, derived: Mapping[str, object]) -> float:
        pointer_norm = float(derived.get("pointer_norm", 0.0))
        zoom_delta = abs(float(derived.get("zoom_delta", 0.0)))
        rotation_delta = abs(float(derived.get("rotation_delta", 0.0)))
        triggered = 0.5 if bool(derived.get("triggered", False)) else 0.0
        return pointer_norm + zoom_delta + rotation_delta + triggered

    def _build_tiles(self, base_energy: float, surface: str) -> Iterable[MutableMapping[str, object]]:
        for idx, layer in enumerate(self.layers):
            if not layer.enabled:
                continue

            yield {
                "layer": layer.name,
                "surface": surface,
                "tile": idx % max(1, self.tile_span),
                "energy": round(base_energy * layer.intensity, 4),
            }


def volumetric_slice(frame: EffectFrame, *, depth: int = 3) -> Sequence[Mapping[str, object]]:
    """Generate volumetric slices for holographic playback from an effect frame."""

    slices = []
    for tile in frame.tiles:
        for z in range(depth):
            slices.append(
                {
                    "layer": tile.get("layer"),
                    "slice": z,
                    "energy": float(tile.get("energy", 0.0)),
                    "surface": frame.surface,
                    "frame_id": frame.frame_id,
                }
            )
    return slices
