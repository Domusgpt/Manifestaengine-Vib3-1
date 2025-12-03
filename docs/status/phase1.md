# Phase 1 Status — SDK Alignment

This page captures the deliverables, validation, and documentation needed to complete Phase 1 (SDK Alignment). Use it to track progress as the engine transitions from the baseline telemetry/mocks to SDK-backed pipelines across wearable, web, and holographic surfaces.

## Scope
- Integrate vib34d-xr-quaternion-sdk for wearable ingress and math fidelity (quaternion fusion, rotation smoothing).
- Replace emulated parameter mapping with SDK-backed values for POINTER_DELTA, ZOOM_DELTA, ROT_DELTA, INPUT_TRIGGER, and HOLO_FRAME.
- Produce WASM math module with parity to CPU reference kernels and publish capability metadata.
- Treat holographic transport as production-scope alongside Faceted/Quantum; maintain deterministic HOLO_FRAME ingest/replay.
- Maintain agent context frames and sub-agent spawning with SDK-aware constraints (goal/bounds/focus fields).

## Artifacts to Produce
- **Schemas & Bindings**
  - Finalized `schema/event.v1.json` and `schema/agent_frame.v1.json` plus generated TS/Dart bindings published to packages.
  - Schema changelog noting Phase 0 → Phase 1 revisions (field additions/removals).
- **SDK Integrations**
  - Wearable pipeline wired to vib34d-xr-quaternion-sdk with BLE/IMU adapters and latency/jitter tracing.
  - WebXR/OpenXR harness consuming HOLO_FRAME events with deterministic playback and snapshot capture.
  - Signal Bus adapters replacing emulation layers in the React/Vite and Flutter shells.
- **Math Backends**
  - WASM math build for quaternion/elasticity kernels with snapshot tests vs CPU reference vectors.
  - Capability discovery endpoint exposing kernel versions/backends (CPU/WASM/GLSL) for agents and clients.
- **Replay & Diagnostics**
  - Deterministic replay CLI targeting SDK-backed pipelines (wearable + holographic) with JSON logs.
  - Latency budgets and observed metrics for wearable ingress, Signal Bus dispatch, and holographic transport.
- **Docs & Harnesses**
  - Updated architecture diagrams showing SDK surfaces and HOLO_FRAME alignment.
  - `docs/status/phase1.md` (this file) updated with progress, gaps, and validation results.
  - `just docs:phase1` to render and lint Phase 1 docs.

## Validation Checklist
- [ ] `pnpm install` + workspace bootstraps succeed with SDK dependencies.
- [ ] `pnpm lint` passes for Signal Bus, telemetry, and SDK adapters.
- [ ] `pnpm test:math` passes for CPU + WASM parity (vectors in `tests/vectors`).
- [ ] `pnpm test:telemetry` passes with SDK-backed wearable ingress and timestamp discipline.
- [ ] `pnpm test:ws` passes with schema enforcement using finalized JSON schemas.
- [ ] `pnpm test:replay` passes against SDK-generated logs for wearable and HOLO_FRAME channels.
- [ ] `pnpm run doc:status:phase1` renders docs and checks for missing artifacts.
- [ ] Holographic/WebXR harness runs deterministically against HOLO_FRAME snapshots (no Polychora placeholders).

## Progress (working items)
- Captured SDK alignment scope, artifacts, validation gates, and risks; checklist now mirrors Phase 0 exit items for continuity.
- Phase 0 ready-to-start items propagated (schemas, telemetry server, CPU kernels) to ensure SDK wiring has baselines.
- Holographic is treated as production scope with HOLO_FRAME ingest/replay baked into the validation criteria.
- WASM parity expectations defined (quaternion/elasticity) with capability discovery so agents/clients can pick backends.
- Gemini/agent adapters kept pluggable; JSON envelopes remain deterministic and schema-validated.

## Exit Notes / Handoff to Phase 2
- Verify SDK-backed telemetry replaces mocks for wearables and matches latency/jitter baselines from Phase 0 logs.
- Run WASM parity tests against CPU vectors and record kernel capability metadata for downstream clients.
- Demonstrate HOLO_FRAME replay through WebXR/OpenXR harness with deterministic snapshots.
- Publish schema bindings (TS/Dart) and note any diffs in the schema changelog.
- Update dev setup with SDK-specific install notes (Flutter/Dart, wasm-pack, OpenXR/WebXR runtimes) and confirm `just docs:phase1` renders.

### Ready-to-start tasks (Phase 2 prerequisites)
- Wire Signal Bus snapshots into React/Vite devtools overlay and Flutter shell using SDK-backed adapters.
- Stand up PNG/WebM export + Playwright harness for render snapshot comparisons across CPU/WASM backends.
- Add holographic/WebXR shim that consumes HOLO_FRAME from the Signal Bus and records deterministic replays.
- Draft `docs/status/phase2.md` with scope, artifacts, validation checklist, and sequencing for UI/holographic parity.

## Gaps / Blockers
- _Add items here as they are discovered._

## Sequencing / Dependencies
- Phase 0 artifacts (schemas, CPU kernels, ring buffers, replay logs) checked in and versioned.
- SDK binaries or source pulled and available for local builds (Flutter/Dart, Node/WASM bindings as needed).
- Mock emitters retained for regression alongside SDK sources to compare jitter/latency deltas.

## Risks / Watch-outs
- Latency regression when switching from emulated to SDK pipelines; monitor BLE/IMU jitter and HOLO_FRAME throughput.
- Schema drift between CPU reference and SDK outputs; enforce contract tests to keep parity.
- Holographic transport must remain deterministic and production-scoped; avoid placeholder stacks (e.g., Polychora) until real.

## Gaps / Blockers
- _Add items here as they are discovered._
