# Phase 2 Status — Rendering & UI

This page tracks renderer/UI alignment with the Signal Bus and SDK-backed pipelines. The focus is deterministic playback, cross-platform parity (React/Vite, Flutter), and production-scoped holographic transport.

## Scope
- Drive React/Vite devtools overlay from Signal Bus snapshots (SDK-backed) with deterministic replay.
- Mirror controls and telemetry consumption in a Flutter shell using platform channels for wearables and holographic surfaces.
- Enable PNG/WebM exports and snapshot harnesses for regression (Playwright) across CPU/WASM math backends.
- Add WebXR/OpenXR holographic shims that ingest `HOLO_FRAME` events and preserve determinism; no Polychora placeholders.
- Maintain agent-aware JSON envelopes (schemas frozen from Phase 1) for render-config proposals and focus/handoff.

## Artifacts to Produce
- **Signal Bus → UI adapters**
  - React/Vite overlay bound to Signal Bus snapshots with replay controls (`packages/web/devtools` or equivalent).
  - Flutter platform-channel binding for Signal Bus events + HOLO_FRAME ingest (`packages/flutter_signal_bus`).
- **Exports & Harnesses**
  - Render export hooks for PNG/WebM with CLI entry point (headless Playwright).
  - Snapshot baselines stored under `tests/golden/render/` keyed by backend (CPU/WASM) and surface (web/flutter/holographic).
  - WebXR/OpenXR harness to consume HOLO_FRAME and produce deterministic slices/goldens for regression.
- **Schemas & Agents**
  - Render-config envelope documented (`render_config.v1` derived from Phase 1 schemas) with validation.
  - Agent focus/handoff examples showing render/holographic intents bound to SDK-safe surfaces.
- **Docs & Diagrams**
  - Updated architecture diagram highlighting Signal Bus → UI bindings and holographic flows.
  - Status doc (this file) kept current with progress, gaps, and validation results.

## Validation Checklist
- [ ] `pnpm dev:web` or equivalent runs React/Vite overlay against SDK-backed Signal Bus snapshots.
- [ ] `pnpm test:render` (Vitest/Playwright) passes with PNG/WebM snapshots for CPU and WASM kernels.
- [ ] `flutter test` (or `flutter test --platform chrome`) passes UI goldens consuming Signal Bus data.
- [ ] `pnpm test:holo` (WebXR/OpenXR harness) replays HOLO_FRAME deterministically with stored baselines.
- [ ] `pnpm lint` and `dart analyze` pass for UI bindings and adapters.
- [ ] `just docs:phase2` renders docs and confirms artifact links.

## Sequencing / Dependencies
- Phase 1 exit: SDK-backed telemetry, schemas frozen/published, WASM parity recorded, HOLO_FRAME replay validated.
- Signal Bus journal + replay CLI available from Phase 0/1 for deterministic render tests.
- Playwright browsers installed (`pnpm exec playwright install --with-deps`) and Flutter/web targets enabled (`flutter config --enable-web`).

## Progress (working items)
- Scope, artifacts, validation gates, and dependencies documented to match Phase 1 outputs.
- Holographic transport listed as production-scope with deterministic replay requirements and exclusion of Polychora placeholders.
- Export/snapshot harness expectations defined (PNG/WebM + WebXR/OpenXR slices) to keep regression baselines portable.

## Gaps / Blockers
- _Add items here as they are discovered._

## Exit Notes / Handoff to Phase 3
- Render/UI overlays consume SDK-backed Signal Bus data with deterministic replay and snapshot coverage.
- Holographic/WebXR harness produces reproducible goldens for HOLO_FRAME events.
- Agent render/holographic intents validated through schema checks and focus/handoff rules.
- Export/CLI tooling (PNG/WebM + replay) documented and wired into phase-gated tests.
