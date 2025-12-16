"""Utilities for defining and progressing multi-phase delivery work."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Phase:
    """Represents a single project phase with its planned objectives."""

    name: str
    objectives: List[str]
    status: str = "pending"
    notes: Optional[str] = None

    def mark_active(self) -> None:
        """Mark this phase as the active workstream."""
        self.status = "active"

    def mark_complete(self, notes: Optional[str] = None) -> None:
        """Mark this phase as complete and optionally record notes."""
        self.status = "complete"
        if notes:
            self.notes = notes


class PhaseTracker:
    """In-memory tracker for structured, phase-based delivery."""

    def __init__(self) -> None:
        self.phases: List[Phase] = []
        self.current_index: Optional[int] = None

    @classmethod
    def from_existing(
        cls, phases: List[Phase], current_index: Optional[int] = None
    ) -> "PhaseTracker":
        """Instantiate a tracker with pre-existing phases and current index."""
        tracker = cls()
        tracker.phases = phases
        tracker.current_index = current_index
        return tracker

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of the tracker state."""
        return {
            "phases": [
                {
                    "name": phase.name,
                    "objectives": phase.objectives,
                    "status": phase.status,
                    "notes": phase.notes,
                }
                for phase in self.phases
            ],
            "current_index": self.current_index,
        }

    def add_phase(self, name: str, objectives: List[str]) -> Phase:
        """Append a new phase and activate it if it's the first."""
        if any(phase.name == name for phase in self.phases):
            raise ValueError(f"Phase '{name}' already exists")

        phase = Phase(name=name, objectives=objectives)
        self.phases.append(phase)

        if self.current_index is None:
            self.current_index = 0
            phase.mark_active()

        return phase

    def current_phase(self) -> Optional[Phase]:
        """Return the currently active phase if there is one."""
        if self.current_index is None:
            return None
        return self.phases[self.current_index]

    def advance(self, notes: Optional[str] = None) -> Phase:
        """Complete the current phase and activate the next one if it exists."""
        if self.current_index is None:
            raise ValueError("No phase is currently active")

        active_phase = self.phases[self.current_index]
        active_phase.mark_complete(notes=notes)

        if self.current_index + 1 < len(self.phases):
            self.current_index += 1
            self.phases[self.current_index].mark_active()
        else:
            self.current_index = None

        return active_phase

    def set_active(self, name: str) -> Phase:
        """Switch the active phase to the given name."""
        for idx, phase in enumerate(self.phases):
            if phase.name == name:
                previous = self.current_phase()
                if previous is not None and previous.status == "active":
                    previous.status = "pending"
                self.current_index = idx
                phase.mark_active()
                return phase
        raise ValueError(f"Phase '{name}' not found")

    def summary(self) -> str:
        """Return a human-readable summary of all phases and their statuses."""
        active_lines = []
        other_lines = []

        for phase in self.phases:
            marker = "->" if phase.status == "active" else "  "
            objective_list = ", ".join(phase.objectives)
            notes_suffix = f" | notes: {phase.notes}" if phase.notes else ""
            line = f"{marker} {phase.name}: {phase.status} | objectives: {objective_list}{notes_suffix}"

            if phase.status == "active":
                active_lines.append(line)
            else:
                other_lines.append(line)

        return "\n".join(active_lines + other_lines)


__all__ = ["Phase", "PhaseTracker"]
