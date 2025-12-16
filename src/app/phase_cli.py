"""Command-line interface for managing phases with persistent storage."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from .phase_storage import initialize_file, load_tracker, save_tracker


def _parse_phase_definition(phase_arg: str) -> tuple[str, List[str]]:
    if ":" not in phase_arg:
        raise ValueError(
            "Phase definitions must be formatted as 'Name:objective1,objective2'"
        )

    name, raw_objectives = phase_arg.split(":", 1)
    objectives = [obj.strip() for obj in raw_objectives.split(",") if obj.strip()]
    if not name.strip() or not objectives:
        raise ValueError("Phase name and at least one objective are required")

    return name.strip(), objectives


def _parse_phase_list(raw_phases: Iterable[str]) -> List[tuple[str, List[str]]]:
    return [_parse_phase_definition(value) for value in raw_phases]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage delivery phases")
    parser.add_argument(
        "--file",
        default="phases.json",
        help="Path to the JSON file backing the phase tracker",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a new tracker file")
    init_parser.add_argument(
        "--phase",
        action="append",
        required=True,
        help="Phase definition formatted as 'Name:objective1,objective2'",
    )

    add_parser = subparsers.add_parser("add", help="Append a new phase to the tracker")
    add_parser.add_argument("name", help="Name of the new phase")
    add_parser.add_argument(
        "objectives",
        nargs="+",
        help="Objectives for the phase (provide one or more strings)",
    )

    advance_parser = subparsers.add_parser(
        "advance", help="Complete the current phase and activate the next one"
    )
    advance_parser.add_argument(
        "--notes", default=None, help="Optional notes recorded during completion"
    )

    set_active_parser = subparsers.add_parser(
        "set-active", help="Mark the provided phase as active"
    )
    set_active_parser.add_argument("name", help="Name of the phase to activate")

    subparsers.add_parser("summary", help="Print the current tracker summary")

    return parser


def _handle_init(args: argparse.Namespace) -> str:
    tracker = initialize_file(args.file, _parse_phase_list(args.phase))
    return tracker.summary()


def _handle_add(args: argparse.Namespace) -> str:
    tracker = load_tracker(args.file)
    tracker.add_phase(args.name, list(args.objectives))
    save_tracker(args.file, tracker)
    return tracker.summary()


def _handle_advance(args: argparse.Namespace) -> str:
    tracker = load_tracker(args.file)
    tracker.advance(notes=args.notes)
    save_tracker(args.file, tracker)
    return tracker.summary()


def _handle_set_active(args: argparse.Namespace) -> str:
    tracker = load_tracker(args.file)
    tracker.set_active(args.name)
    save_tracker(args.file, tracker)
    return tracker.summary()


def _handle_summary(args: argparse.Namespace) -> str:
    tracker = load_tracker(args.file)
    return tracker.summary()


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "init": _handle_init,
        "add": _handle_add,
        "advance": _handle_advance,
        "set-active": _handle_set_active,
        "summary": _handle_summary,
    }

    output = handlers[args.command](args)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

