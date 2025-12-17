import asyncio
import json
import math
import unittest

from src.phase0_baseline import TelemetryService
from src.phase1_pipeline import (
    Phase1Normalizer,
    ProcessedFrame,
    attach_holo_alignment,
    build_normalized_stream,
    compute_derived_metrics,
    export_frames,
    replay_frames,
)


class Phase1PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_derived_metrics_and_export(self):
        payload = {
            "POINTER_DELTA": {"dx": 3.0, "dy": 4.0},
            "ZOOM_DELTA": 0.25,
            "ROT_DELTA": -0.5,
            "INPUT_TRIGGER": True,
        }
        derived = compute_derived_metrics(payload)
        self.assertAlmostEqual(derived["pointer_magnitude"], 5.0)
        self.assertAlmostEqual(derived["pointer_angle"], math.atan2(4.0, 3.0))
        self.assertEqual(derived["zoom_velocity"], 0.25)
        self.assertEqual(derived["rotation_velocity"], -0.5)

        frame = ProcessedFrame(source="event.v1", minimal=payload, derived=derived)
        blob = export_frames([frame])
        serialized = json.loads(blob.split("\n")[0])
        self.assertEqual(serialized["minimal"], payload)
        self.assertEqual(serialized["derived"], derived)

    async def test_normalizer_consumes_events(self):
        service = TelemetryService()
        normalizer = Phase1Normalizer(service)

        producer_task = asyncio.create_task(
            build_normalized_stream(
                service,
                imu_samples=[(1.0, 0.0, 0.2), (0.0, -1.0, -0.1)],
                presses=[True, False],
                zoom_values=[0.1, 0.2],
            )
        )
        frames = await producer_task
        self.assertGreaterEqual(len(frames), 4)
        self.assertTrue(all(frame.minimal["POINTER_DELTA"] for frame in frames))

    async def test_holo_alignment_and_replay(self):
        frame = ProcessedFrame(
            source="event.v1",
            minimal={"POINTER_DELTA": {"dx": 0.0, "dy": 0.0}, "ZOOM_DELTA": 0.0, "ROT_DELTA": 0.0, "INPUT_TRIGGER": False},
            derived={"pointer_magnitude": 0.0, "pointer_angle": 0.0, "zoom_velocity": 0.0, "rotation_velocity": 0.0},
            timestamp=1.0,
        )

        aligned = attach_holo_alignment(frame, "frame-001", [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        self.assertEqual(aligned.holo_frame, "frame-001")
        self.assertIn("quaternion", aligned.alignment)

        timestamps = []

        async def consume(processed: ProcessedFrame):
            timestamps.append(processed.timestamp)

        await replay_frames([aligned], consume)
        self.assertEqual(timestamps, [1.0])


if __name__ == "__main__":
    unittest.main()
