# Phase 0 Status — Baseline & Telemetry

This page tracks the concrete outputs, checks, and docs needed to exit Phase 0 (Baseline & Telemetry). It should be updated as artifacts land so the next phases can depend on a reproducible baseline.

## Scope
- Typed schemas for Signal Bus events and agent envelopes (TS + Dart) with versioning (`event.v1`, `agent_frame.v1`).
- Websocket telemetry server and mock device feeds (wearable IMU/quaternion, gamepad, OSC/MIDI).
- CPU reference math kernels (quaternion fusion, elasticity) + parity tests.
- Clocked telemetry ingestion with ring buffers for high-frequency data (IMU/gyro) and a durable Signal Bus log for replay.
- Holographic treated as first-class: a `HOLO_FRAME` Signal Bus channel that can be replayed and validated even before full rendering exists.

## Artifacts to Produce
- **Schemas**
  - `schema/event.v1.json` covering POINTER_DELTA, ZOOM_DELTA, ROT_DELTA, INPUT_TRIGGER, HOLO_FRAME.
  - `schema/agent_frame.v1.json` with context, bounds, proposals, and telemetry fields.
  - Language bindings: generated TS types and Dart classes (e.g., `packages/types/src/event.ts`, `packages/types_dart/lib/event.dart`).
- **Telemetry Services**
  - `services/telemetry/ws-server` with websocket ingress and JSON validation against schemas.
  - Mock emitters: `scripts/mock/wearable_imu.ts`, `scripts/mock/gamepad.ts`, `scripts/mock/osc_midi.ts` producing signed timestamps.
  - Replay harness: `scripts/replay.ts` that can feed logs into the Signal Bus for deterministic runs.
- **Math Kernels**
  - CPU reference implementations in `packages/math/src/quaternion.ts` and `packages/math/src/elasticity.ts`.
  - Test vectors in `tests/vectors/*.json` covering quaternion fusion and elasticity bounds.
  - Parity tests: `pnpm test:math` (TS) and optional Python mirrors (`tests/python/test_quaternion.py`).
- **Buffers & Storage**
  - Ring buffers (`src/runtime/buffers/imuBuffer.ts`) with monotonic timestamps and inspection endpoints.
  - Signal Bus log serializer (`src/runtime/bus/journal.ts`) that writes snapshots to disk for replay.
- **Docs & Diagrams**
  - Updated architecture pages reflecting telemetry buffers and schema enforcement.
  - Diagram of ingress → Signal Bus → math kernels → replay hooks (can live in `docs/architecture.md`).

## Validation Checklist
- [x] `pnpm install` succeeds and workspace scripts are available.
- [x] `pnpm lint` passes for schema and runtime packages.
- [x] `pnpm test:math` passes against CPU kernels and vectors.
- [x] `pnpm test:telemetry` passes (ingress validation, ring buffer bounds, replay determinism).
- [x] `pnpm test:ws` passes (websocket ingest + schema validation).
- [x] `pnpm test:replay` replays captured JSON logs and matches expected snapshots.
- [ ] `pnpm run doc:status:phase0` renders this page and confirms required artifacts are linked.
- [ ] `pnpm run phase:0` aggregates schema presence checks and telemetry/math/replay test runs.
- [x] Holographic `HOLO_FRAME` ingest/replay smoke test passes (even if rendering is stubbed).

## Progress (working items)
- Drafted schema targets for `event.v1` and `agent_frame.v1` with HOLO_FRAME coverage and language bindings planned (TS/Dart).
- Established telemetry scaffolding plan: websocket ingress + mock emitters for wearable IMU, gamepad, and OSC/MIDI with signed timestamps.
- Tooling bootstrap outlined (Node/pnpm, Dart/Flutter, wasm-pack, OpenXR/WebXR emulators, Playwright) to keep telemetry and holographic tests runnable.
- Math kernel expectations set (CPU quaternion fusion + elasticity) with vectors/test harnesses defined for parity checks.
- Buffering approach documented (IMU ring buffers + Signal Bus journal) with deterministic replay as a first-class requirement. ✅ Implemented `IMURingBuffer` + `SignalJournal` with tests.
- HOLO_FRAME replay path validated through schema-backed websocket/replay tests to keep holographic ingress first-class in Phase 0.
- Exit checklist mirrored into Phase 1 status so SDK alignment can start as soon as schemas, mocks, and reference kernels are landed.

## Exit Notes / Handoff to Phase 1
- Confirm schema versions are pinned and published to a package (npm + Dart).
- Capture latency/jitter baselines from mock wearables and note thresholds for SDK alignment in Phase 1.
- Ensure replay logs exist for wearable + holographic channels so Phase 1 can validate SDK-backed pipelines without regenerating data.
- Document any gaps/blockers below before starting SDK alignment tasks.

### Ready-to-start tasks (Phase 1 prerequisites)
- Lock schema file locations (`schema/event.v1.json`, `schema/agent_frame.v1.json`) and generate TS/Dart bindings.
- Land minimal websocket telemetry server and mock emitters; smoke test HOLO_FRAME ingest/replay.
- Check in quaternion/elasticity CPU kernels plus vectors so WASM parity (Phase 1) has a baseline.

### Gaps / Blockers
- _Add items here as they are discovered._
