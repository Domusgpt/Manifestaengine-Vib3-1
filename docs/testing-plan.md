# Testing Plan (Phased)

This repository is staged across the roadmap phases documented in `docs/status/`. Use the following plan to keep tests and tooling aligned with the available manifests.

## Current Environment (Python-only fast gates)
- Run the bootstrap script to verify tooling and install dependencies: `./scripts/bootstrap_tools.sh`.
- Run quick validation: `pytest -q` (covers Phase 3 validation, Phase 4 bridge routing, and Phase 6 effects/performance helpers).
- These checks keep Signal Bus schema guards and derived metric calculations honest while pnpm/Flutter/OpenXR runners are unavailable.

## When Web/Flutter/Holo manifests return
- Re-enable pnpm + Playwright: `pnpm install && pnpm exec playwright install --with-deps`, then run `pnpm test`, `pnpm test:render`, and `pnpm test:holo` for UI/overlay and holographic coverage.
- Restore Flutter toolchain and execute `flutter test` (plus goldens) for capability overlays that consume bridge outputs and effect tiles.
- Re-run OpenXR/WebXR harnesses for holographic exports and HOLO_FRAME replays once runners are provisioned.

## Per-phase guidance
- **Phase 3 (Agent orchestration)**: prioritize schema validation via the Python suite; add property-based tests when SDK manifests return.
- **Phase 4 (Bridges)**: pair the Python bridge tests with UDP/OSC/gRPC harnesses and replay fixtures once toolchains are restored.
- **Phase 5 (Quality/Ops)**: keep observation/replay CLIs covered by unit tests and extend to end-to-end pnpm/Flutter/OpenXR once manifests land. Structured logs from the observed router can be replayed into latency reports with `python -m src.phase6_cli observed.log`.
- **Phase 6 (Effects/Performance)**: retain deterministic effect frame tests here; add WASM parity and performance harnesses when build runners are back. Pipe live structured logs into `python -m src.phase6_cli` for quick latency spot checks while heavier harnesses are unavailable.
