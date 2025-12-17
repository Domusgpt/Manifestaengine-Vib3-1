import time
from unittest import TestCase, mock

from src.phase4_bridge import BridgeContext
from src.phase6_performance import PerformanceMonitor, TelemetryBuffer


class TelemetryBufferTests(TestCase):
    def test_rolls_over_when_full(self) -> None:
        buffer = TelemetryBuffer(capacity=2)
        sample = mock.Mock()
        buffer.append(sample)
        buffer.append(sample)
        buffer.append(sample)

        self.assertEqual(len(buffer.samples), 2)


class PerformanceMonitorTests(TestCase):
    def setUp(self) -> None:
        self.context = BridgeContext(session_id="s-perf", sdk_surface="holo", capabilities={"schema": "event.v1"})
        self.payload = {
            "type": "pointer",
            "timestamp": 1.0,
            "payload": {
                "POINTER_DELTA": {"dx": 3, "dy": 4},
                "ZOOM_DELTA": 0.2,
                "ROT_DELTA": 0.1,
                "INPUT_TRIGGER": False,
            },
        }

    def test_ingest_records_latency_and_metrics(self) -> None:
        monitor = PerformanceMonitor(buffer_capacity=4)
        with mock.patch("time.monotonic", side_effect=[1.5, 1.6, 2.0, 2.1]):
            monitor.ingest("event.v1", self.payload, self.context)
            monitor.ingest("event.v1", self.payload, self.context)

        metrics = monitor.latency_metrics()
        self.assertGreater(metrics["mean_ms"], 0)
        self.assertGreaterEqual(metrics["max_ms"], metrics["mean_ms"])
        self.assertIn("jitter_ms", metrics)

        export = monitor.export_samples()
        self.assertEqual(len(export), 2)
        self.assertEqual(export[0]["derived"]["pointer_norm"], 5.0)

    def test_invalid_capacity_raises(self) -> None:
        monitor = PerformanceMonitor(buffer_capacity=0)
        with self.assertRaises(Exception):
            monitor.assert_capacity()

    def test_invalid_envelope_rejected(self) -> None:
        monitor = PerformanceMonitor()
        with self.assertRaises(Exception):
            monitor.ingest("unknown", {"payload": {}}, self.context)
