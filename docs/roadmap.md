# Implementation Roadmap (Phased)

A pragmatic sequence to migrate from the current emulation-heavy build to a SDK-faithful, extensible engine.

## Phase 0: Baseline & Telemetry
- Add typed schemas for Signal Bus events and agent envelopes (TS + Dart).
- Stand up websocket telemetry server; ingest mock wearables/gamepad/OSC data.
- Implement CPU reference math kernels (quaternion fusion, elasticity) with test vectors.
- Establish phase-gated test runners (`just test:phase0`) and documentation checkpoints per phase.
- Publish `docs/status/phase0.md` capturing ingress adapters, schema versions, replay harness status, and holographic `HOLO_FRAME` ingest notes.
- **Current work**: define schema targets, telemetry mocks, and buffers in Phase 0 status doc while preparing Phase 1 alignment inputs.

## Phase 1: SDK Alignment
- Integrate vib34d-xr-quaternion-sdk for wearable pipelines; validate latency and jitter budgets.
- Replace emulated parameter mapping with SDK-backed values (pointer/zoom/rotation/trigger).
- Build WASM math module for parity with CPU reference; snapshot tests across backends.
- Mark holographic transport as production-scope alongside Faceted/Quantum; explicitly exclude placeholder Polychora paths.
- Ship `just docs:phase1` to assert updated SDK mappings, schema revisions, and OpenXR/WebXR harness readiness.

## Phase 2: Rendering & UI
- Wire Signal Bus snapshots to React/Vite devtools overlay; ensure deterministic playback/replay.
- Add Flutter UI shell that mirrors controls and consumes the same Signal Bus via platform channels.
- Introduce PNG/WebM export hooks for visualization/testing (headless Playwright harness).
- Add holographic transport shim (WebXR/OpenXR) driven from the Signal Bus for volumetric production testing.
- Extend `just test:phase2` to cover holographic scenes, UI goldens, and render snapshot comparisons.
- Produce `docs/status/phase2.md` summarizing renderer parity, holographic coverage, and export harness steps.

## Phase 3: Agent Orchestration
- Implement context-frame JSON protocol; allow user/agent to spawn scoped sub-agents.
- Gemini/LLM adapter that reads/writes JSON envelopes without owning control flow.
- Safety: schema validation + rate limits before applying agent proposals.
- Add agent-focused regression packs and documentation that highlight holographic/Faceted/Quantum role bindings.
- Update status doc (`docs/status/phase3.md`) detailing agent spawn constraints, focus/handoff rules, and failure logging.

## Phase 4: Integrations
- Game engine bridges (Unity/Unreal) via OSC/UDP/gRPC with sample scenes.
- Wearable haptics/audio bridges using MIDI/OSC; add latency tracing and back-pressure handling.
- Design-tool overlays (Figma plugin or browser overlay) consuming Signal Bus state.
- Holographic clients: WebXR and Flutter/AR shells that subscribe to `HOLO_FRAME` events and share quaternion math kernels.
- Add `docs/status/phase4.md` to track bridge coverage (Unity/Unreal, design-tool overlays) and holographic client readiness.

## Phase 5: Quality, Ops, and Docs
- Unified test suite: unit (Vitest/Jest), property-based, integration (Playwright), Flutter goldens.
- Deterministic replay CLI for telemetry logs and shader outputs.
- Observability: structured logs, health pings, and kernel capability reporting.
- Developer docs with examples for web, mobile, wearable, and agentic usage.
- Formalize `just docs:phase5` to verify observability dashboards, replay CLI examples, and per-surface quickstarts.

## Phase 6: Expansion & Advanced Effects
- Layered field/cloth/particle effects gated by feature flags; keep deterministic kernel variants for regression.
- Volumetric/holographic rendering modes with exportable slices/tiles for playback and testing.
- AI/agent enhancements that prioritize SDK fidelity (goal/safety/bound limits) while enabling sub-agent specialization per device class (wearable, web, holographic).
- Performance/latency hardening for high-frequency telemetry (IMU/gyro) with synchronized ring buffers across transports.
