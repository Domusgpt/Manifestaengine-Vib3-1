import json
from unittest import IsolatedAsyncioTestCase, TestCase, mock

from src.phase4_bridge import BridgeContext
from src.phase6_effects import EffectEngine, EffectLayer, volumetric_slice


class EffectEngineTests(TestCase):
    def setUp(self) -> None:
        self.layers = [EffectLayer("field", intensity=1.0), EffectLayer("particles", intensity=0.5)]
        self.context = BridgeContext(session_id="s1", sdk_surface="holographic", capabilities={"schema": "event.v1"})
        self.payload = {
            "type": "pointer",
            "timestamp": 1.0,
            "payload": {
                "POINTER_DELTA": {"dx": 3, "dy": 4},
                "ZOOM_DELTA": 0.2,
                "ROT_DELTA": 0.1,
                "INPUT_TRIGGER": True,
            }
        }

    def test_generates_tiles_from_minimal_parameters(self) -> None:
        engine = EffectEngine(self.layers, tile_span=2)
        with mock.patch("time.monotonic", return_value=10.0):
            frame = engine.generate_frame("event.v1", self.payload, self.context)

        self.assertEqual(frame.frame_id, 0)
        self.assertEqual(frame.surface, "holographic")
        energies = [tile["energy"] for tile in frame.tiles]
        self.assertAlmostEqual(energies[0], 5.8)
        self.assertAlmostEqual(energies[1], 2.9)
        self.assertEqual(frame.capabilities["schema"], "event.v1")

    def test_exports_frames_in_order(self) -> None:
        engine = EffectEngine(self.layers, tile_span=3)
        with mock.patch("time.monotonic", side_effect=[1.0, 2.0, 3.0]):
            engine.generate_frame("event.v1", self.payload, self.context, surface="holographic")
            engine.generate_frame("event.v1", self.payload, self.context, surface="wearable")

        lines: list[str] = []
        engine.export_frames(lines.append)
        serialized_frames = [json.loads(line) for line in lines]

        self.assertEqual([frame["frame_id"] for frame in serialized_frames], [0, 1])
        self.assertEqual(serialized_frames[1]["surface"], "wearable")
        self.assertEqual(len(serialized_frames[0]["tiles"]), 2)


class VolumetricSliceTests(TestCase):
    def test_builds_depth_slices(self) -> None:
        engine = EffectEngine([EffectLayer("cloth", intensity=0.25)], tile_span=1)
        with mock.patch("time.monotonic", return_value=5.0):
            frame = engine.generate_frame(
                "event.v1",
                {
                    "type": "pointer",
                    "timestamp": 0.0,
                    "payload": {
                        "POINTER_DELTA": {"dx": 1, "dy": 1},
                        "ZOOM_DELTA": 0.0,
                        "ROT_DELTA": 0.0,
                        "INPUT_TRIGGER": False,
                    },
                },
                BridgeContext(session_id="s2", sdk_surface="holographic", capabilities={"schema": "event.v1"}),
            )

        slices = volumetric_slice(frame, depth=2)
        self.assertEqual(len(slices), 2)
        self.assertEqual({entry["slice"] for entry in slices}, {0, 1})
        self.assertEqual(slices[0]["frame_id"], 0)


class ValidationTests(IsolatedAsyncioTestCase):
    async def test_rejects_invalid_envelope_kind(self) -> None:
        engine = EffectEngine([EffectLayer("field")])
        with self.assertRaises(Exception):
            # Invalid kind should trigger validation failure from phase3_validator
            engine.generate_frame("unknown", {"payload": {}}, BridgeContext("s3", "web", {"schema": "event.v1"}))
