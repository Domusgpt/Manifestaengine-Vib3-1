# Development quickstart

These notes describe the local setup used for telemetry, replay, and math verification.

## Environment
- Node 18+ with [`pnpm`](https://pnpm.io/installation) available.
- Python 3.10+ for the `pytest` suite.
- Optional: a virtual environment (e.g., `.venv`) to isolate Python dependencies.

## Install
```sh
pnpm install
```

Verify required tooling is on your PATH before running the suites:

```sh
pnpm run tools:status
```

## Test cadence
Run fast, targeted checks before larger changes:

```sh
pnpm test:math        # CPU reference kernels against shared vectors
pnpm test:telemetry   # Schema validation for telemetry payloads
pnpm test:ws          # WebSocket server dispatch smoke test
pnpm test:replay      # Deterministic replay harness validation
pnpm lint             # TypeScript type checking
pytest -q             # Python validation helpers
pnpm run doc:status:phase0  # Render/check the Phase 0 status page references
pnpm run doc:status:phase1  # Sanity-check Phase 1 status/scoping references
pnpm run phase:0      # Aggregated Phase 0 runner (schemas + telemetry/math/replay tests)
pnpm run phase:1      # Aggregated Phase 1 runner (Phase 0 baseline + doc status)
```

## Notes
- The schema validators rely on `schema/event.v1.json` and `schema/agent_frame.v1.json`; keep them in sync with generated bindings.
- Telemetry mocks live in `scripts/mock/` and the replay harness in `scripts/replay.ts`.
- Buffering utilities for IMU data and Signal Bus journals live under `src/runtime/`.
