import asyncio
import json
import unittest
from typing import List

from src.phase0_baseline import (
    ReplayHarness,
    TelemetryService,
    ValidationError,
    deterministic_service_pipeline,
    gamepad_emitter,
    osc_midi_emitter,
    validate_agent_frame,
    validate_event,
    validate_minimal_parameters,
    wearable_imu_emitter,
)


class Phase0BaselineTests(unittest.IsolatedAsyncioTestCase):
    async def test_minimal_pipeline_records_and_replays(self):
        replay, events = await deterministic_service_pipeline(
            imu_samples=[(1.0, -1.0, 0.25), (0.0, 0.5, 0.75)],
            presses=[True, False],
            zoom_values=[0.1, -0.2],
        )

        self.assertEqual(len(events), 6)
        serialized = [event.to_json() for event in replay.frames()]
        self.assertTrue(
            all("POINTER_DELTA" in json.loads(entry)["payload"]["payload"] for entry in serialized)
        )

        consumed: List[float] = []

        async def consume(event):
            consumed.append(event.timestamp)

        await replay.replay(consume)
        self.assertEqual(len(consumed), len(events))

    async def test_validation_rejections(self):
        service = TelemetryService()
        with self.assertRaises(ValidationError):
            await service.publish("event.v1", {"type": "bad", "payload": {}, "timestamp": 0})

        bad_frame = {
            "inputs": {"POINTER_DELTA": {"dx": 0, "dy": 0}, "ZOOM_DELTA": 0, "ROT_DELTA": 0, "INPUT_TRIGGER": True},
            "role": "",
            "goal": "",
            "sdk_surface": "",
            "bounds": {"x": 0, "y": 0},
            "focus": {"path": ""},
        }
        with self.assertRaises(ValidationError):
            validate_agent_frame(bad_frame)

    async def test_emitters_publish_to_subscribers(self):
        service = TelemetryService()
        queue = service.subscribe()

        await wearable_imu_emitter(service, [(0.0, 1.0, 0.0)])
        await gamepad_emitter(service, [True])
        await osc_midi_emitter(service, [0.5])

        received = []
        while not queue.empty():
            received.append(await queue.get())

        kinds = {event.kind for event in received}
        self.assertEqual(kinds, {"event.v1"})
        self.assertTrue(any(event.payload["payload"]["INPUT_TRIGGER"] for event in received))

    async def test_event_and_frame_validation_success(self):
        event = {
            "type": "imu_frame",
            "timestamp": 1.23,
            "payload": {
                "POINTER_DELTA": {"dx": 1, "dy": 2},
                "ZOOM_DELTA": 0.0,
                "ROT_DELTA": 0.1,
                "INPUT_TRIGGER": False,
            },
        }
        validate_event(event)

        frame = {
            "inputs": event["payload"],
            "role": "navigator",
            "goal": "stability",
            "sdk_surface": "wearable",
            "bounds": {"x": 0, "y": 0, "z": 0},
            "focus": {"path": "ui"},
        }
        validate_agent_frame(frame)

    async def test_replay_harness_iteration_order(self):
        service = TelemetryService()
        queue = service.subscribe()
        replay = ReplayHarness()

        await gamepad_emitter(service, [True, False])

        timestamps = []
        while not queue.empty():
            event = await queue.get()
            replay.record(event)
            timestamps.append(event.timestamp)

        self.assertEqual(timestamps, sorted(timestamps))
        seen = []

        async def consume(event):
            seen.append(event.timestamp)

        await replay.replay(consume)
        self.assertEqual(seen, timestamps)


if __name__ == "__main__":
    unittest.main()
