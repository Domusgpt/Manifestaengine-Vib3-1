"""
Phase 3 validation utilities for agent orchestration and safety envelopes.

These helpers validate the minimal parameter surface and envelope-specific
requirements for agent_frame.v1, event.v1, render_config.v1, and holo_intent
payloads. Validation is intentionally strict to keep Signal Bus interactions
safe and deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence


@dataclass
class ValidationError(Exception):
    """Raised when a payload fails validation."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def _assert_number(value: Any, path: str) -> None:
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a number")


def _assert_bool(value: Any, path: str) -> None:
    if not isinstance(value, bool):
        raise ValidationError(f"{path} must be a boolean")


def _assert_str(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")


def _assert_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return value


def _assert_sequence(value: Any, path: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValidationError(f"{path} must be an array")
    return value


def _assert_holo_frame(frame: Mapping[str, Any]) -> None:
    """Validate a HOLO_FRAME payload with quaternion + translation."""

    quaternion = _assert_sequence(frame.get("quaternion"), "HOLO_FRAME.quaternion")
    translation = _assert_sequence(frame.get("translation"), "HOLO_FRAME.translation")
    if len(quaternion) != 4:
        raise ValidationError("HOLO_FRAME.quaternion must have 4 entries")
    if len(translation) != 3:
        raise ValidationError("HOLO_FRAME.translation must have 3 entries")
    for index, value in enumerate(quaternion):
        _assert_number(value, f"HOLO_FRAME.quaternion[{index}]")
    for index, value in enumerate(translation):
        _assert_number(value, f"HOLO_FRAME.translation[{index}]")
    _assert_str(frame.get("surface"), "HOLO_FRAME.surface")


def validate_minimal_parameters(payload: Mapping[str, Any]) -> None:
    """Validate the minimal parameter set used across envelopes.

    Required fields:
      - POINTER_DELTA: object with numeric dx/dy entries
      - ZOOM_DELTA: numeric zoom delta
      - ROT_DELTA: numeric rotation delta
      - INPUT_TRIGGER: boolean trigger flag
    """

    data = _assert_mapping(payload, "payload")

    pointer = _assert_mapping(data.get("POINTER_DELTA"), "POINTER_DELTA")
    for axis in ("dx", "dy"):
        _assert_number(pointer.get(axis), f"POINTER_DELTA.{axis}")

    _assert_number(data.get("ZOOM_DELTA"), "ZOOM_DELTA")
    _assert_number(data.get("ROT_DELTA"), "ROT_DELTA")
    _assert_bool(data.get("INPUT_TRIGGER"), "INPUT_TRIGGER")

    holo_frame = data.get("HOLO_FRAME")
    if holo_frame is not None:
        _assert_holo_frame(_assert_mapping(holo_frame, "HOLO_FRAME"))


def validate_agent_frame(frame: Mapping[str, Any]) -> None:
    """Validate an agent_frame.v1 payload."""

    data = _assert_mapping(frame, "agent_frame")
    for field in ("role", "goal", "sdk_surface"):
        _assert_str(data.get(field), field)

    bounds = _assert_mapping(data.get("bounds"), "bounds")
    for bound_field in ("x", "y", "z"):
        _assert_number(bounds.get(bound_field), f"bounds.{bound_field}")

    focus = _assert_mapping(data.get("focus"), "focus")
    _assert_str(focus.get("path"), "focus.path")

    inputs = _assert_mapping(data.get("inputs"), "inputs")
    validate_minimal_parameters(inputs)

    outputs = _assert_sequence(data.get("outputs"), "outputs")
    for index, output in enumerate(outputs):
        _assert_str(output, f"outputs[{index}]")

    safety = _assert_mapping(data.get("safety"), "safety")
    for safety_field in ("spawn_bounds", "rate_limit", "rejection_reason"):
        if safety_field == "rejection_reason":
            # optional string, empty when no rejection occurred
            reason = safety.get(safety_field, "")
            if reason:
                _assert_str(reason, safety_field)
            continue
        _assert_number(safety.get(safety_field), safety_field)


def validate_event(event: Mapping[str, Any]) -> None:
    """Validate an event.v1 payload."""

    data = _assert_mapping(event, "event")
    _assert_str(data.get("type"), "type")
    _assert_number(data.get("timestamp"), "timestamp")

    payload = _assert_mapping(data.get("payload"), "payload")
    validate_minimal_parameters(payload)


def validate_render_config(config: Mapping[str, Any]) -> None:
    """Validate a render_config.v1 payload."""

    data = _assert_mapping(config, "render_config")
    _assert_str(data.get("surface"), "surface")
    _assert_str(data.get("schema"), "schema")
    validate_minimal_parameters(_assert_mapping(data.get("inputs"), "inputs"))

    overlays = _assert_mapping(data.get("overlays"), "overlays")
    _assert_bool(overlays.get("capability"), "overlays.capability")


def validate_holo_intent(intent: Mapping[str, Any]) -> None:
    """Validate a holo_intent payload for holographic alignment."""

    data = _assert_mapping(intent, "holo_intent")
    _assert_str(data.get("holo_frame"), "holo_frame")
    _assert_str(data.get("sdk_surface"), "sdk_surface")
    validate_render_config(_assert_mapping(data.get("render_config"), "render_config"))

    alignment = _assert_mapping(data.get("alignment"), "alignment")
    expectations = {"quaternion": 4, "translation": 3}
    for field, expected_len in expectations.items():
        values = _assert_sequence(alignment.get(field), f"alignment.{field}")
        if len(values) != expected_len:
            raise ValidationError(f"alignment.{field} must have {expected_len} entries")
        for index, value in enumerate(values):
            _assert_number(value, f"alignment.{field}[{index}]")


def validate_holo_frame(frame: Mapping[str, Any]) -> None:
    """Validate a HOLO_FRAME envelope for holographic transport."""

    data = _assert_mapping(frame, "holo_frame")
    validate_minimal_parameters(_assert_mapping(data.get("inputs", {}), "inputs"))
    _assert_holo_frame(_assert_mapping(data.get("frame"), "frame"))


VALIDATORS: Dict[str, Any] = {
    "event.v1": validate_event,
    "agent_frame.v1": validate_agent_frame,
    "render_config.v1": validate_render_config,
    "holo_intent": validate_holo_intent,
    "holo_frame.v1": validate_holo_frame,
}


def validate_envelope(kind: str, payload: Mapping[str, Any]) -> None:
    """Validate a payload by schema name.

    Raises:
        ValidationError: when no validator exists for the kind or validation fails.
    """

    if kind not in VALIDATORS:
        raise ValidationError(f"Unsupported envelope kind: {kind}")
    VALIDATORS[kind](payload)
