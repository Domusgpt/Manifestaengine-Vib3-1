import asyncio
import math
import unittest

from src.phase3_validator import ValidationError
from src.phase4_bridge import BridgeContext, BridgeRouter, InMemorySink, derived_metrics


def minimal_parameters(**overrides):
    base = {
        "POINTER_DELTA": {"dx": 0.3, "dy": 0.4},
        "ZOOM_DELTA": 1.5,
        "ROT_DELTA": -0.25,
        "INPUT_TRIGGER": True,
    }
    base.update(overrides)
    return base


def sample_event_payload():
    return {
        "type": "input",
        "timestamp": 101.0,
        "payload": minimal_parameters(),
    }


def sample_render_config():
    return {
        "surface": "web",
        "schema": "render_config.v1",
        "inputs": minimal_parameters(),
        "overlays": {"capability": True},
    }


def sample_agent_frame():
    return {
        "role": "navigator",
        "goal": "align holographic anchor",
        "sdk_surface": "holographic",
        "bounds": {"x": 1, "y": 1, "z": 1},
        "focus": {"path": "holographic.scene:anchor/base"},
        "inputs": minimal_parameters(),
        "outputs": ["render.intent.apply"],
        "safety": {"spawn_bounds": 10, "rate_limit": 5, "rejection_reason": ""},
    }


class Phase4BridgeTest(unittest.TestCase):
    def setUp(self):
        self.context = BridgeContext(
            session_id="session-1",
            sdk_surface="wearable",
            capabilities={"backend": "cpu", "schema": "event.v1"},
        )

    def test_derived_metrics_include_pointer_norm(self):
        metrics = derived_metrics(minimal_parameters())
        self.assertAlmostEqual(metrics["pointer_norm"], math.hypot(0.3, 0.4))
        self.assertTrue(metrics["triggered"])

    def test_dispatch_routes_to_all_sinks(self):
        sink = InMemorySink(name="unity")
        router = BridgeRouter([sink])

        asyncio.run(router.dispatch("event.v1", sample_event_payload(), self.context))

        self.assertEqual(len(sink.received), 1)
        envelope = sink.received[0]["envelope"]
        self.assertEqual(envelope["kind"], "event.v1")
        self.assertIn("derived", envelope)
        self.assertIn("context", envelope)

    def test_duplicate_sink_name_raises(self):
        router = BridgeRouter([InMemorySink(name="unity")])

        with self.assertRaises(ValidationError):
            router.add_sink(InMemorySink(name="unity"))

    def test_invalid_payload_rejected(self):
        sink = InMemorySink(name="unity")
        router = BridgeRouter([sink])

        with self.assertRaises(ValidationError):
            asyncio.run(router.dispatch("event.v1", {"type": "input"}, self.context))

    def test_holo_intent_paths_use_nested_inputs(self):
        sink = InMemorySink(name="holo")
        router = BridgeRouter([sink])
        holo_payload = {
            "holo_frame": "frame-1",
            "sdk_surface": "holographic",
            "render_config": sample_render_config(),
            "alignment": {"quaternion": [0, 0, 0, 1], "translation": [0, 0, 0]},
        }

        asyncio.run(router.dispatch("holo_intent", holo_payload, self.context))

        envelope = sink.received[0]["envelope"]
        self.assertAlmostEqual(
            envelope["derived"]["pointer_norm"], math.hypot(0.3, 0.4)
        )

    def test_agent_frame_routes_with_capability_overlay(self):
        sink = InMemorySink(name="agent")
        router = BridgeRouter([sink])
        asyncio.run(router.dispatch("agent_frame.v1", sample_agent_frame(), self.context))

        envelope = sink.received[0]["envelope"]
        self.assertEqual(envelope["context"]["capabilities"], self.context.capabilities)


if __name__ == "__main__":
    unittest.main()
