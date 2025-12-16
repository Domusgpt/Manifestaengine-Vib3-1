import json
from pathlib import Path

import pytest

from app.phase_cli import main
from app.phase_storage import initialize_file, load_tracker


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def test_initialize_and_summary(tmp_path, capsys):
    data_file = tmp_path / "phases.json"

    exit_code = main(
        [
            "--file",
            str(data_file),
            "init",
            "--phase",
            "Phase 0:Baseline repo,Create plan",
            "--phase",
            "Phase 1:Ship feature",
        ]
    )

    assert exit_code == 0

    tracker_data = read_json(data_file)
    assert tracker_data["phases"][0]["status"] == "active"

    captured = capsys.readouterr().out
    assert "-> Phase 0: active" in captured


def test_add_and_advance_persist(tmp_path, capsys):
    data_file = tmp_path / "phases.json"
    initialize_file(data_file, [("Phase 0", ["Baseline repo"]), ("Phase 1", ["Ship"])] )

    exit_code = main([
        "--file",
        str(data_file),
        "add",
        "Phase 2",
        "Validate",
        "Document",
    ])
    assert exit_code == 0

    exit_code = main([
        "--file",
        str(data_file),
        "advance",
        "--notes",
        "Finished groundwork",
    ])
    assert exit_code == 0
    capsys.readouterr()  # flush previous output

    # Reload and ensure state is preserved
    tracker = load_tracker(data_file)
    assert tracker.current_phase() is not None
    assert tracker.current_phase().name == "Phase 1"
    assert tracker.phases[0].notes == "Finished groundwork"

    main(["--file", str(data_file), "summary"])
    captured_summary = capsys.readouterr().out
    assert "notes: Finished groundwork" in captured_summary


def test_set_active_does_not_clear_completion(tmp_path, capsys):
    data_file = tmp_path / "phases.json"
    initialize_file(
        data_file,
        [
            ("Phase 0", ["Baseline repo"]),
            ("Phase 1", ["Ship"]),
        ],
    )

    # advance to complete Phase 0
    main(["--file", str(data_file), "advance", "--notes", "done"])
    capsys.readouterr()

    # set active back to Phase 0 should not wipe its completion state
    main(["--file", str(data_file), "set-active", "Phase 0"])
    summary_output = capsys.readouterr().out

    tracker_data = read_json(data_file)
    assert tracker_data["phases"][0]["status"] == "active"
    assert tracker_data["phases"][0]["notes"] == "done"
    assert "notes: done" in summary_output
