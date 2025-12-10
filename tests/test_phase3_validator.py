import unittest

from src.phase3_validator import (
    ValidationError,
    validate_agent_frame,
    validate_envelope,
    validate_event,
    validate_holo_intent,
    validate_minimal_parameters,
    validate_render_config,
)


def minimal_parameters(**overrides):
    base = {
        "POINTER_DELTA": {"dx": 0.1, "dy": -0.2},
        "ZOOM_DELTA": 1.0,
        "ROT_DELTA": 0.0,
        "INPUT_TRIGGER": True,
    }
    base.update(overrides)
    return base


class Phase3ValidatorTest(unittest.TestCase):
    def test_validate_agent_frame_success(self):
        payload = {
            "role": "navigator",
            "goal": "stabilize overlay",
            "sdk_surface": "wearable",
            "bounds": {"x": 1, "y": 1, "z": 1},
            "focus": {"path": "holographic.scene:anchor/base"},
            "inputs": minimal_parameters(),
            "outputs": ["render.intent.apply", "safety.log"],
            "safety": {"spawn_bounds": 10, "rate_limit": 5, "rejection_reason": ""},
        }

        validate_agent_frame(payload)

    def test_missing_minimal_parameter_raises(self):
        invalid = minimal_parameters()
        invalid.pop("POINTER_DELTA")

        with self.assertRaises(ValidationError):
            validate_minimal_parameters(invalid)

    def test_invalid_alignment_length_raises(self):
        holo_intent = {
            "holo_frame": "frame-1",
            "sdk_surface": "holographic",
            "render_config": {
                "surface": "web",
                "schema": "render_config.v1",
                "inputs": minimal_parameters(),
                "overlays": {"capability": True},
            },
            "alignment": {"quaternion": [0, 0, 0], "translation": [0, 0, 0]},
        }

        with self.assertRaises(ValidationError):
            validate_holo_intent(holo_intent)

    def test_validate_envelope_dispatch(self):
        event_payload = {
            "type": "input",
            "timestamp": 123.4,
            "payload": minimal_parameters(),
        }

        # Should not raise
        validate_envelope("event.v1", event_payload)

        with self.assertRaises(ValidationError):
            validate_envelope("unsupported", {})

    def test_validate_render_config_success(self):
        render_config = {
            "surface": "web",
            "schema": "render_config.v1",
            "inputs": minimal_parameters(),
            "overlays": {"capability": False},
        }

        validate_render_config(render_config)

    def test_validate_event_success(self):
        event_payload = {
            "type": "input", 
            "timestamp": 42.0,
            "payload": minimal_parameters(),
        }

        validate_event(event_payload)


if __name__ == "__main__":
    unittest.main()
