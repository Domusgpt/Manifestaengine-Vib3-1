# Tooling Bootstrap and Phased Test Gates

This guide pairs with `scripts/bootstrap_tools.sh` to provision the core runtimes needed for the Unified Engine and to stage testing as manifests return.

## Quick start
1. Ensure your shell can execute the bootstrap script: `chmod +x scripts/bootstrap_tools.sh` (already set in repo).
2. Run the script from repo root: `./scripts/bootstrap_tools.sh`.
   - Verifies required runtimes (Node, pnpm, Python, Dart/Flutter, cmake/ninja/protoc).
   - Installs Python dev dependencies for the fast pytest gates.
   - Installs pnpm packages and Playwright browsers when a `package.json` is present.
   - Enables Flutter web targets for CanvasKit-based overlays.
3. Follow the final line for the next test command (typically `pytest -q` as a fast gate).

## When tools are missing
The script exits with a list of missing commands. Install them via your platform package manager (e.g., `apt`, `brew`, or SDK installers) and rerun the script. Keep pnpm, Flutter, and Playwright aligned with the versions referenced in `docs/dev-setup.md`.

## Phased testing handoff
- **Phase 0–2 catch-up**: After bootstrapping, prioritize Python `pytest -q` while pnpm/Flutter manifests are unavailable.
- **Phase 3**: Add schema/property tests once pnpm installs succeed; keep Python validators as the fast gate.
- **Phase 4**: Layer bridge harnesses (UDP/OSC/gRPC) after pnpm/Playwright install completes; re-run Python bridge tests to guard regressions.
- **Phase 5**: Fold in quality/ops e2e runners plus Flutter goldens; keep pytest for quick confidence before heavier runs.
- **Phase 6**: Re-enable WASM parity/performance harnesses; export telemetry traces with `pnpm test:render`/`pnpm test:holo` once the toolchains are healthy.

## Artifact expectations
- **Python**: `requirements-dev.txt` drives the fast gates; failures should block until resolved.
- **JavaScript**: pnpm lockfiles and Playwright installs are expected when `package.json` lands.
- **Flutter**: Web enablement is required for CanvasKit snapshotting and HOLO_FRAME replay surfaces.

Document test outcomes in the relevant `docs/status/phaseN.md` files whenever you exit a phase or restore a toolchain.
