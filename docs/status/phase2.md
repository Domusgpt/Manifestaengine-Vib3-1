# Phase 2 Status — Rendering & UI (Completed)

This page tracks renderer/UI alignment with the Signal Bus and SDK-backed pipelines. The focus is deterministic playback, cross-platform parity (React/Vite, Flutter), and production-scoped holographic transport. All exit criteria are complete and recorded here as the handoff reference for Phase 3 agent orchestration.

## Completion Snapshot
- **Outcome**: Rendering and UI bindings are production-ready with deterministic replay across web, Flutter, and holographic surfaces. Exports/goldens, schemas, and replay harnesses are in place with CPU/WASM parity metadata.
- **Primary evidence**: Validation checklist (below) marked complete; export/replay manifests live under `tests/golden/render/{backend}/{surface}` with kernel/schema metadata; HOLO_FRAME regression slices are captured for holographic transport.
- **Handoff note**: Phase 3 can rely on stabilized Signal Bus adapters, render/holographic intents, and schema-frozen envelopes (`render_config.v1`, `holo_intent`) without introducing Polychora placeholders.

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

## Validation Checklist (completed)
- [x] `pnpm dev:web` or equivalent runs React/Vite overlay against SDK-backed Signal Bus snapshots with deterministic play/pause/seek. Snapshots seeded from the Phase 1 Signal Bus journal and inspected via devtools overlay controls.
- [x] `pnpm test:render` (Vitest/Playwright) passes with PNG/WebM snapshots for CPU and WASM kernels; goldens tagged with backend + schema metadata and stored under `tests/golden/render/web`.
- [x] `flutter test` (and `flutter test --platform chrome`) passes UI goldens consuming Signal Bus data and HOLO_FRAME isolates for wearables and holographic shells.
- [x] `pnpm test:holo` (WebXR/OpenXR harness) replays HOLO_FRAME deterministically with stored baselines and telemetry-aligned clocks; baselines live under `tests/golden/render/holographic`.
- [x] `pnpm lint` and `dart analyze` pass for UI bindings and adapters across web + Flutter packages.
- [x] `just export:render` and `just holo:replay` generate/update goldens with manifests under `tests/golden/render/{backend}/{surface}` including kernel, schema, and seed metadata.
- [x] `just docs:phase2` renders docs and confirms artifact links and manifests are up to date.

## Workstreams (completed)
- **Signal Bus → UI bindings**: React/Vite devtools overlay consumes SDK-backed bus snapshots via websocket with play/pause/seek and backend discovery; Flutter shell mirrors controls over platform channels and isolates for HOLO_FRAME. CPU/WASM kernels surfaced via capability flags on both shells.
- **Exports & goldens**: shared export interface (`export_frame`, `export_clip`) feeds Playwright and Flutter captures; metadata manifests stored with goldens and linked from docs. PNG/WebM exports tagged with schema/kernel/seed to ensure reproducibility.
- **Holographic harness**: WebXR/OpenXR replay with HOLO_FRAME depth/color alignment and monotonic clock shim; Polychora omitted. Deterministic slices plus short WebM previews are captured for regression.
- **Agent envelopes**: `render_config.v1`, `render_intent`, and `holo_intent` schemas published; focus/handoff and capability hints documented for agent proposals bound to SDK-safe surfaces.
- **Instrumentation**: structured logs for ingest → kernel → render timings land in CI; lint/format/schema validation enforced for TS/Dart bindings and wired into phase gate runners.

## Ready-to-Start Tasks
- (Completed) Stand up websocket-fed Signal Bus snapshot server for React/Vite overlay; expose play/pause/seek and backend flags.
- (Completed) Add Flutter platform channel + isolate to ingest Signal Bus events and HOLO_FRAME; bind to UI controls and widget goldens.
- (Completed) Implement export interface and CLI (`just export:render`) that captures PNG/WebM for CPU/WASM across surfaces and writes metadata manifests.
- (Completed) Create WebXR/OpenXR harness script (`pnpm test:holo`) that replays HOLO_FRAME logs with deterministic clocks and stores slices under `tests/golden/render/holographic`.
- (Completed) Finalize `render_config.v1` docs + JSON schema; add agent examples for render/holographic intents with focus paths.
- (Completed) Wire `just holo:replay` and `just docs:phase2` into CI to block merge until holographic + doc artifacts are current.

## Sequencing / Dependencies
- Phase 1 exit: SDK-backed telemetry, schemas frozen/published, WASM parity recorded, HOLO_FRAME replay validated.
- Signal Bus journal + replay CLI available from Phase 0/1 for deterministic render tests.
- Playwright browsers installed (`pnpm exec playwright install --with-deps`) and Flutter/web targets enabled (`flutter config --enable-web`).

## Progress (complete)
- Scope, artifacts, validation gates, and dependencies documented and implemented to match Phase 1 outputs with concrete capture/export interfaces.
- Phase 1/2 normalization frames can be ingested for render/export harnesses, providing derived metrics and HOLO alignment details for deterministic replay even while SDK package manifests are unavailable.
- Holographic transport treated as production-scope with deterministic replay requirements, monotonic clock shim, and exclusion of Polychora placeholders; HOLO_FRAME baselines available for regression.
- Export/snapshot harnesses operational (PNG/WebM + WebXR/OpenXR slices) with metadata manifest requirements for reproducible baselines.
- Agent render/holographic intent schemas finalized from Phase 1 envelopes with focus/handoff expectations; capability hints present in examples.

## Gaps / Blockers
- None for Phase 2 exit. CI wiring, endpoints, and baselines are in place; Phase 2 is ready to hand off.

## Exit Notes / Handoff to Phase 3
- Render/UI overlays consume SDK-backed Signal Bus data with deterministic replay and snapshot coverage.
- Holographic/WebXR harness produces reproducible goldens for HOLO_FRAME events.
- Agent render/holographic intents validated through schema checks and focus/handoff rules.
- Export/CLI tooling (PNG/WebM + replay) documented and wired into phase-gated tests.
