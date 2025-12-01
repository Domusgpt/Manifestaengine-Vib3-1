# Implementation Roadmap (Phased)

A pragmatic sequence to migrate from the current emulation-heavy build to a SDK-faithful, extensible engine.

## Phase 0: Baseline & Telemetry
- Add typed schemas for Signal Bus events and agent envelopes (TS + Dart).
- Stand up websocket telemetry server; ingest mock wearables/gamepad/OSC data.
- Implement CPU reference math kernels (quaternion fusion, elasticity) with test vectors.

## Phase 1: SDK Alignment
- Integrate vib34d-xr-quaternion-sdk for wearable pipelines; validate latency and jitter budgets.
- Replace emulated parameter mapping with SDK-backed values (pointer/zoom/rotation/trigger).
- Build WASM math module for parity with CPU reference; snapshot tests across backends.

## Phase 2: Rendering & UI
- Wire Signal Bus snapshots to React/Vite devtools overlay; ensure deterministic playback/replay.
- Add Flutter UI shell that mirrors controls and consumes the same Signal Bus via platform channels.
- Introduce PNG/WebM export hooks for visualization/testing (headless Playwright harness).

## Phase 3: Agent Orchestration
- Implement context-frame JSON protocol; allow user/agent to spawn scoped sub-agents.
- Gemini/LLM adapter that reads/writes JSON envelopes without owning control flow.
- Safety: schema validation + rate limits before applying agent proposals.

## Phase 4: Integrations
- Game engine bridges (Unity/Unreal) via OSC/UDP/gRPC with sample scenes.
- Wearable haptics/audio bridges using MIDI/OSC; add latency tracing and back-pressure handling.
- Design-tool overlays (Figma plugin or browser overlay) consuming Signal Bus state.

## Phase 5: Quality, Ops, and Docs
- Unified test suite: unit (Vitest/Jest), property-based, integration (Playwright), Flutter goldens.
- Deterministic replay CLI for telemetry logs and shader outputs.
- Observability: structured logs, health pings, and kernel capability reporting.
- Developer docs with examples for web, mobile, wearable, and agentic usage.
