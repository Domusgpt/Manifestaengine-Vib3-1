"""JSON-backed persistence helpers for phase tracking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from .phase_tracker import Phase, PhaseTracker


def _coerce_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _build_current_index(phases: List[Phase], explicit: Optional[int]) -> Optional[int]:
    if explicit is not None:
        return explicit

    for idx, phase in enumerate(phases):
        if phase.status == "active":
            return idx

    return None


def load_tracker(path: str | Path) -> PhaseTracker:
    """Load a tracker from a JSON file."""

    file_path = _coerce_path(path)
    data = json.loads(file_path.read_text())

    phases = [
        Phase(
            name=phase["name"],
            objectives=list(phase.get("objectives", [])),
            status=phase.get("status", "pending"),
            notes=phase.get("notes"),
        )
        for phase in data.get("phases", [])
    ]

    current_index = _build_current_index(phases, data.get("current_index"))
    return PhaseTracker.from_existing(phases, current_index=current_index)


def save_tracker(path: str | Path, tracker: PhaseTracker) -> None:
    """Persist a tracker to a JSON file."""

    file_path = _coerce_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(tracker.to_dict(), indent=2))


def initialize_file(path: str | Path, phases: Iterable[tuple[str, List[str]]]) -> PhaseTracker:
    """Create a new tracker file with the provided phases."""

    tracker = PhaseTracker()
    for name, objectives in phases:
        tracker.add_phase(name, list(objectives))

    save_tracker(path, tracker)
    return tracker

