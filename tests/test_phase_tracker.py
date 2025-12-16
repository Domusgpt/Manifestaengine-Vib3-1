import pytest

from app.phase_tracker import PhaseTracker


def test_add_phase_sets_first_active():
    tracker = PhaseTracker()
    phase = tracker.add_phase("Phase 0", ["Baseline repo", "Create plan"])

    assert tracker.current_phase() == phase
    assert phase.status == "active"


def test_advance_marks_complete_and_activates_next():
    tracker = PhaseTracker()
    tracker.add_phase("Phase 0", ["Baseline repo"])
    tracker.add_phase("Phase 1", ["Build feature"])

    completed = tracker.advance(notes="Documented plan")
    assert completed.status == "complete"
    assert completed.notes == "Documented plan"

    active = tracker.current_phase()
    assert active is not None
    assert active.name == "Phase 1"
    assert active.status == "active"


def test_set_active_switches_phase():
    tracker = PhaseTracker()
    tracker.add_phase("Phase 0", ["Baseline repo"])
    tracker.add_phase("Phase 1", ["Build feature"])

    tracker.set_active("Phase 1")

    assert tracker.current_phase().name == "Phase 1"
    assert tracker.summary().startswith("-> Phase 1: active")


def test_summary_lists_notes_when_present():
    tracker = PhaseTracker()
    tracker.add_phase("Phase 0", ["Baseline repo"])
    tracker.advance(notes="Initial setup done")

    summary = tracker.summary()

    assert "notes: Initial setup done" in summary


def test_error_on_duplicate_phase_names():
    tracker = PhaseTracker()
    tracker.add_phase("Phase 0", ["Baseline repo"])

    with pytest.raises(ValueError):
        tracker.add_phase("Phase 0", ["Duplicate"])


def test_error_when_advancing_without_phases():
    tracker = PhaseTracker()

    with pytest.raises(ValueError):
        tracker.advance()
