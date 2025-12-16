import json

import pytest

from src.phase3_validator import ValidationError
from src.phase6_cli import performance_report


@pytest.fixture
def structured_logs():
    base = {
        "session_id": "sesh-123",
        "sdk_surface": "wearable",
        "capabilities": {"haptics": True},
        "bridged_at": 5.0,
        "timestamp": 5.0,
    }
    event_log = json.dumps(
        {
            **base,
            "sink": "unity",
            "kind": "event.v1",
            "minimal": {"POINTER_DELTA": {"dx": 1.0, "dy": 0.0}, "timestamp": 2.0},
        }
    )
    agent_log = json.dumps(
        {
            **base,
            "sink": "overlay",
            "kind": "agent_frame.v1",
            "minimal": {"INPUT_TRIGGER": True, "timestamp": 3.5},
        }
    )
    return [event_log, agent_log]


def test_performance_report_aggregates_latency(structured_logs):
    report = performance_report(structured_logs)

    assert report["ingested"] == 2
    overall = report["overall"]
    assert overall["samples"] == 2
    assert overall["max_ms"] > 1000  # 5.0 - 2.0 seconds -> > 3000ms, conservative bound
    assert set(report["by_kind"]) == {"event.v1", "agent_frame.v1"}


def test_performance_report_rejects_missing_fields():
    logs = [json.dumps({"kind": "event.v1"})]
    with pytest.raises(ValidationError):
        performance_report(logs)
