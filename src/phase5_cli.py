"""Phase 5 observation CLI helpers.

Provides small utilities to load structured bridge logs, reconstruct health
metrics, optionally hydrate replay frames, and emit consolidated observation
reports. This supplements the Phase 5 observability work while broader
workspace manifests remain unavailable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence

from src.phase4_bridge import ReplayRecorder
from src.phase5_quality import HealthMonitor, observation_report


def load_logs(paths: Sequence[str | Path]) -> list[str]:
    """Load structured log lines from the provided files."""

    lines: list[str] = []
    for path in paths:
        for line in Path(path).read_text().splitlines():
            if line.strip():
                lines.append(line)
    return lines


def _status_from_record(record: Mapping[str, object]) -> str:
    status = record.get("status")
    if isinstance(status, str) and status in {"dispatched", "rate_limited", "error"}:
        return status
    return "dispatched"


def health_from_logs(log_lines: Iterable[str]) -> HealthMonitor:
    """Reconstruct sink-level health metrics from structured logs."""

    monitor = HealthMonitor()
    for entry in log_lines:
        try:
            parsed: MutableMapping[str, object] = json.loads(entry)
        except json.JSONDecodeError:
            continue

        sink = parsed.get("sink")
        if not isinstance(sink, str):
            continue

        status = _status_from_record(parsed)
        error = parsed.get("error") if isinstance(parsed.get("error"), str) else None
        monitor.record(sink, status, error=error)

    return monitor


def _recorder_from_file(path: str | None) -> ReplayRecorder | None:
    if path is None:
        return None

    recorder = ReplayRecorder()
    content = Path(path).read_text().splitlines()
    for line in content:
        try:
            recorder.record("replay", json.loads(line))
        except json.JSONDecodeError:
            continue
    return recorder


def build_report(log_paths: Sequence[str | Path], replay_path: str | None = None) -> Mapping[str, object]:
    """Generate an observation report from structured logs and optional replay."""

    logs = load_logs(log_paths)
    monitor = health_from_logs(logs)
    recorder = _recorder_from_file(replay_path)
    return observation_report(logs, monitor, recorder)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 5 observation reports from structured logs.")
    parser.add_argument("logs", nargs="+", help="Path(s) to structured log files.")
    parser.add_argument("--replay", help="Optional path to replay frames exported as JSON lines.")
    parser.add_argument("--output", help="Optional path to write the observation report JSON. Defaults to stdout.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    report = build_report(args.logs, args.replay)
    serialized = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(serialized + "\n")
    else:
        print(serialized)


if __name__ == "__main__":
    main()
