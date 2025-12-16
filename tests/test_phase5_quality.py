import json
import time
from unittest import IsolatedAsyncioTestCase, TestCase, mock

from src.phase4_bridge import BridgeContext, RateLimiter, ReplayRecorder, UDPSink
from src.phase5_quality import (
    ObservedRouter,
    StructuredLogger,
    buffered_logger,
    HealthMonitor,
    export_replay,
    replay_summary,
    observation_report,
)
from src.phase5_cli import build_report, health_from_logs, load_logs


class StructuredLoggerTests(TestCase):
    def test_logs_envelope_with_derived_metrics(self) -> None:
        lines: list[str] = []
        logger = StructuredLogger(writer=lines.append)
        context = BridgeContext(session_id="s1", sdk_surface="holographic", capabilities={"schema": "event.v1"})
        envelope = {
            "kind": "event.v1",
            "payload": {
                "payload": {
                    "POINTER_DELTA": {"dx": 3, "dy": 4},
                    "ZOOM_DELTA": 0.25,
                    "ROT_DELTA": 0.5,
                    "INPUT_TRIGGER": True,
                }
            },
            "bridged_at": 123.4,
        }

        logger.log("udp", envelope, context)

        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["sink"], "udp")
        self.assertEqual(record["kind"], "event.v1")
        self.assertEqual(record["minimal"].get("ZOOM_DELTA"), 0.25)
        self.assertEqual(record["derived"]["pointer_norm"], 5)
        self.assertEqual(record["bridged_at"], 123.4)

    def test_buffered_logger_records_to_buffer(self) -> None:
        buffer: list[str] = []
        logger = buffered_logger(buffer)
        context = BridgeContext(session_id="s1", sdk_surface="wearable", capabilities={"schema": "event.v1"})
        envelope = {
            "kind": "event.v1",
            "payload": {"payload": {"POINTER_DELTA": {"dx": 0, "dy": 0}, "ZOOM_DELTA": 0.0}},
        }

        logger.log("udp", envelope, context)

        self.assertEqual(len(buffer), 1)
        self.assertEqual(json.loads(buffer[0])["kind"], "event.v1")


class HealthMonitorTests(TestCase):
    def test_tracks_health_and_errors(self) -> None:
        monitor = HealthMonitor()

        with mock.patch("time.monotonic", return_value=10.0):
            monitor.record("udp", "dispatched")
        with mock.patch("time.monotonic", return_value=12.0):
            monitor.record("udp", "rate_limited")
        with mock.patch("time.monotonic", return_value=13.0):
            monitor.record("grpc", "error", error="timeout")

        pulse = monitor.pulse()
        self.assertEqual(pulse["sinks"]["udp"]["dispatched"], 1)
        self.assertEqual(pulse["sinks"]["udp"]["rate_limited"], 1)
        self.assertEqual(pulse["sinks"]["grpc"]["errors"], 1)
        self.assertEqual(pulse["errors"][0]["error"], "timeout")

    def test_rejects_unknown_status(self) -> None:
        monitor = HealthMonitor()
        with self.assertRaises(ValueError):
            monitor.record("udp", "invalid")


class ReplayExportTests(TestCase):
    def test_summary_and_export(self) -> None:
        recorder = ReplayRecorder()
        with mock.patch("time.monotonic", side_effect=[1.0, 2.0, 3.5]):
            recorder.record("udp", {"received_at": 1.0, "payload": "a"})
            recorder.record("osc", {"received_at": 2.0, "payload": "b"})
            recorder.record("udp", {"received_at": 3.5, "payload": "c"})

        summary = replay_summary(recorder)
        self.assertEqual(summary["frames"], 3)
        self.assertEqual(summary["sinks"], {"udp": 2, "osc": 1})
        self.assertAlmostEqual(summary["duration"], 2.5)
        self.assertAlmostEqual(summary["max_gap"], 1.5)

        lines: list[str] = []
        export_replay(recorder, writer=lines.append)
        ordered_frames = [json.loads(line) for line in lines]
        self.assertEqual([frame["sink"] for frame in ordered_frames], ["udp", "osc", "udp"])
        self.assertEqual(ordered_frames[0]["envelope"].get("payload"), "a")


class ObservationReportTests(TestCase):
    def test_combines_logs_health_and_replay(self) -> None:
        buffer: list[str] = []
        logger = buffered_logger(buffer)
        monitor = HealthMonitor()
        recorder = ReplayRecorder()
        context = BridgeContext(session_id="s2", sdk_surface="web", capabilities={"schema": "event.v1"})

        envelope = {
            "kind": "event.v1",
            "payload": {"payload": {"POINTER_DELTA": {"dx": 2, "dy": 1}, "ZOOM_DELTA": 0.2}},
            "bridged_at": 5.0,
        }
        logger.log("udp", envelope, context)
        monitor.record("udp", "dispatched")
        recorder.record("udp", envelope)

        report = observation_report(buffer, monitor, recorder)

        self.assertIn("health", report)
        self.assertIn("logs", report)
        self.assertIn("replay", report)
        self.assertEqual(report["health"]["sinks"]["udp"]["dispatched"], 1)
        self.assertEqual(report["replay"]["frames"], 1)
        self.assertEqual(report["logs"][0]["sink"], "udp")


class ObservationCliTests(TestCase):
    def test_health_rebuilds_from_logs(self) -> None:
        lines = [
            json.dumps({"sink": "udp", "status": "dispatched"}),
            json.dumps({"sink": "udp", "status": "rate_limited"}),
            json.dumps({"sink": "grpc", "status": "error", "error": "timeout"}),
            "not-json",
        ]

        monitor = health_from_logs(lines)
        self.assertEqual(monitor.sink_stats["udp"]["dispatched"], 1)
        self.assertEqual(monitor.sink_stats["udp"]["rate_limited"], 1)
        self.assertEqual(monitor.sink_stats["grpc"]["errors"], 1)
        self.assertEqual(monitor.error_log[0]["error"], "timeout")

    def test_build_report_from_files(self) -> None:
        with mock.patch("time.time", return_value=50.0):
            with mock.patch("time.monotonic", return_value=40.0):
                log_path = self._write_tmp([json.dumps({"sink": "udp", "status": "dispatched"})])
                replay_path = self._write_tmp([json.dumps({"sink": "udp", "received_at": 1.0, "payload": "a"})])

                report = build_report([log_path], replay_path)

        self.assertIn("health", report)
        self.assertIn("replay", report)
        self.assertEqual(report["replay"]["frames"], 1)
        self.assertEqual(report["health"]["sinks"]["udp"]["dispatched"], 1)

    def _write_tmp(self, lines: list[str]) -> str:
        import tempfile

        handle, path = tempfile.mkstemp()
        with open(handle, "w") as file:
            file.write("\n".join(lines))
        return path


class ObservedRouterTests(IsolatedAsyncioTestCase):
    async def test_observed_router_logs_and_tracks_health(self) -> None:
        lines: list[str] = []
        logger = StructuredLogger(writer=lines.append)
        monitor = HealthMonitor()
        recorder = ReplayRecorder()

        udp_sink = UDPSink(
            name="udp",
            host="localhost",
            port=9000,
            sender=mock.AsyncMock(),
            rate_limiter=RateLimiter(rate_per_sec=0.0, burst=0),
        )

        router = ObservedRouter(logger=logger, monitor=monitor, recorder=recorder, sinks=[udp_sink])
        context = BridgeContext(session_id="s9", sdk_surface="holographic", capabilities={"schema": "event.v1"})
        payload = {
            "type": "pointer",
            "timestamp": 123.0,
            "payload": {
                "POINTER_DELTA": {"dx": 1, "dy": 2},
                "ZOOM_DELTA": 0.1,
                "ROT_DELTA": 0.2,
                "INPUT_TRIGGER": False,
            },
        }

        await router.dispatch("event.v1", payload, context)

        self.assertEqual(monitor.sink_stats["udp"]["rate_limited"], 1)
        self.assertEqual(len(lines), 1)
        rate_limited_record = json.loads(lines[0])
        self.assertEqual(rate_limited_record["status"], "rate_limited")

        udp_sink.rate_limiter = RateLimiter(rate_per_sec=10.0, burst=1)
        await router.dispatch("event.v1", payload, context)

        self.assertEqual(monitor.sink_stats["udp"]["dispatched"], 1)
        success_record = json.loads(lines[-1])
        self.assertEqual(success_record["minimal"]["ZOOM_DELTA"], 0.1)
        self.assertEqual(len(recorder.frames), 1)
