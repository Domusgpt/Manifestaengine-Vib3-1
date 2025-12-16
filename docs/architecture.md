# Vib3+ Unified Engine Alignment Plan

This document summarizes how to realign the Command Center/Unified Engine so it matches the published Vib3 SDKs and XR quaternion SDK while remaining open to future expansion. The goal is to replace the current LLM-heavy emulation layer with a telemetry-first, asynchronous, JSON-driven architecture that can operate agentically and integrate with wearables, games, OS/visual stacks, projections, and animation pipelines.

## Core Principles

1. **SDK Fidelity First**: Mirror the behavior and parameter contracts of the Vib3 SDK (Faceted, Quaternion, Holographic, and Signal Bus). Prefer native SDK calls over emulation; when bridging is required, keep the bridge shallow and observable.
2. **Asynchronous JSON I/O**: All IO (telemetry in, render/command out) should use async JSON envelopes so agents and external runtimes can consume/produce events without blocking.
3. **Agent Context & Roles**: Maintain lightweight agent roles (Architect, Math/Physics, Shader/Dev, Reactive/UI) with explicit context frames: `{role, goal, sdk_surface, inputs, outputs, safety}`. Allow user/agent to spawn sub-agents with bounded scopes.
4. **Minimal Viable Parameter Surface**: Honor the canonical parameters from the working engine (pointer delta, zoom, rotation delta, trigger events). Enrich only with derived metrics (velocity/accel, quaternion blends) that map directly to SDK math.
5. **Extensible Signal Bus**: Keep the Signal Bus authoritative. Downstream consumers (renderers, haptics, audio, holographic surfaces) subscribe to typed signals. Keep transformations pure and stateless where possible.
6. **Pluggable Math & Kernels**: Support interchangeable math backends (GLSL/Metal shaders, WASM SIMD, or CPU reference) with identical parameter contracts. Version the kernels and expose capability discovery.
7. **Deterministic + Reactive**: Deterministic core with reactive overlays. Agents can suggest mutations, but the engine should reconcile suggestions into deterministic state transitions with validation.

## Target System Diagram

```
Wearables / Sensors / Game Hooks / UIs
         │
         ▼
[Input Adapters]
  - JSON telemetry ingress (websocket/http)
  - Device bridges (BLE for wearables, gamepad, OSC/MIDI)
  - SDK shims for vib34d-xr-quaternion-sdk
         │
         ▼
[Signal Bus]
  - Typed events: POINTER_DELTA, ZOOM_DELTA, ROT_DELTA, TRIGGER
  - Derived signals: velocity/accel, quaternion_fused, elastic_tension
  - Persistence: event journaling + snapshot state (for replay)
         │
         ├─▶ [Math Kernel Layer]
         │     - Quaternion fusion, rotation smoothing, elasticity
         │     - GLSL/Metal/WASM/CPU parity
         │
         ├─▶ [Rendering Layer]
         │     - WebGL2/Vite front-end (faceted/tech styles)
         │     - Native Flutter/Dart renderer (mobile/wearables)
         │     - Export: PNG/WebM frame buffer hooks
         │
         ├─▶ [Agent Layer]
         │     - Roles: Architect, MathPhys, ShaderDev, ReactiveUI
         │     - Sub-agent spawning with context frames
         │     - JSON in/out for autonomy or external LLMs (Gemini mode)
         │
         └─▶ [Integration Ports]
               - Game engine hooks (Unity/Unreal via UDP/OSC/GRPC)
               - OS/Design tools (Figma plugin, browser overlay)
               - Haptics/Audio (MIDI/OSC, wearable drivers)
```

## Agent Protocol (JSON Skeleton)

```json
{
  "frame_id": "uuid",
  "context": {
    "role": "architect|math_phys|shader_dev|reactive_ui|custom",
    "goal": "maintain quaternion stability for wearable",
    "sdk_surface": "vib34d-xr-quaternion-sdk",
    "inputs": ["POINTER_DELTA", "ROT_DELTA"],
    "outputs": ["kernel_patch", "render_config"],
    "bounds": {"time_ms": 120, "memory_mb": 64}
  },
  "telemetry": {"pointer": [dx, dy], "zoom": dz, "rot": [rx, ry, rz], "trigger": 1},
  "state": {"quaternion": [w, x, y, z], "elasticity": 0.18},
  "proposals": [
    {"type": "kernel_patch", "shader": "tech", "params": {"elasticity": 0.2, "damping": 0.05}},
    {"type": "render_config", "style": "master:tech", "grid": true}
  ],
  "responses": [],
  "log": []
}
```

## Minimal Parameter Set (authoritative)
- `POINTER_DELTA {x, y}`
- `ZOOM_DELTA {scale}`
- `ROT_DELTA {rx, ry, rz}` (quaternion-compatible deltas)
- `INPUT_TRIGGER {pressed:boolean, taps:int}`

Derived (keep optional, computed inside math kernels):
- `velocity`, `acceleration` from pointer/zoom deltas
- `quaternion_fused` from ROT_DELTA + inertial sensors
- `elastic_tension`, `shear`, `bend` for cloth/field effects

## Integration Notes by SDK Branch / System Family

- **Faceted/Quantum**: keep parameter parity with the existing faceted and quantum modes; reuse the minimal surface and ensure capability discovery signals which mode is active. Avoid the placeholder Polychora stack until it is functional.
- **vib34d-vib3plus (Flutter/Dart)**: expose a pure Dart Signal Bus package with platform channels for wearables. Render layer uses WebGL/CanvasKit; provide WASM math fallback for web targets.
- **vib3-plus-engine (React/Vite)**: treat this as reference for parameter fidelity and reactive UI. Swap emulation for SDK-backed kernels via WASM bindings. Keep the existing devtools overlay but feed it from the Signal Bus snapshots.
- **vib34d-xr-quaternion-sdk (wearables)**: prioritize BLE/IMU ingestion, low-jitter quaternion fusion, and bounded latency. Provide a deterministic replay harness for test vectors.
- **Holographic/Volumetric surfaces**: treat holographic as a first-class system (not experimental). Reserve a dedicated Signal Bus channel for volumetric frames or light-field intents. Keep holographic state deterministic (e.g., scene graph snapshots) and map kernel outputs into OpenXR/WebXR compatible transforms.

## Data Flow & Storage
- **Ingress**: websocket/HTTP JSON, BLE adapters, gamepad events, MIDI/OSC.
- **Bus**: immutable event log + derived state cache; serialize snapshots for agent context.
- **Egress**: renderer commands (GLSL params), haptic/audio cues, export frames (PNG/WebM/volumetric tiles), agent responses.

### Telemetry Fidelity & Buffering
- **Clock discipline**: normalize all ingress to a shared monotonic clock; attach `ts_ms` on ingest to preserve ordering for replay and holographic alignment.
- **Ring buffers**: keep short-lived high-frequency buffers (IMU/gyro) alongside a longer Signal Bus log; expose both via introspection so agents/testing harnesses can assert fidelity. ✅ Implemented via `IMURingBuffer` (monotonic, capacity bounded) for Phase 0 smoke tests.
- **Schema enforcement**: validate JSON envelopes with versioned schemas (`event.v1`, `agent_frame.v1`) and reject/repair malformed packets before they hit math kernels.
- **Replay hooks**: allow deterministic playback from captured JSON logs across all transports (websocket, BLE shim, WebXR), ensuring parity between wearable and holographic views. ✅ Signal journal + replay harness validate `HOLO_FRAME` envelopes.

## Holographic System Alignment
- **Scene abstraction**: standardize on a scene graph with typed nodes (camera, light, emitter, volumetric mesh). Maintain a minimal schema that agents can mutate without breaking determinism.
- **Transport**: use a dedicated topic (e.g., `HOLO_FRAME`) on the Signal Bus that carries either compressed depth+color tiles or light-field coefficients; gate by capability discovery (OpenXR/WebXR).
- **Reactivity**: allow agents to propose holographic intents (`holo_focus`, `holo_blend`, `holo_anchor`) that are validated and merged by the deterministic core before committing to the graph.
- **Interop**: expose holographic transforms as the same quaternion+translation tuples used for wearables so math kernels are shared. Provide adapters for AR-capable Flutter shells and WebXR-enabled browsers.
- **Export**: support headless renders for regression (PNG slices) and streamed volumetric previews for development.

### Agent Context & Sub-Agent Protocol
- **Spawn constraints**: sub-agents inherit the parent context frame but must declare scoped goals, time/memory bounds, and observable IO. All proposals flow through the same schema validation gates as primary agents.
- **Focus & handoff**: embed `focus` fields (e.g., `focus: "holographic.scene:node/anchor"`) to keep agents aligned with SDK surfaces, and support explicit handoff events so the deterministic core can arbitrate control.
- **Safety rails**: rate-limit structural changes to the scene graph/holographic channels, require diff-based proposals, and log rejects with reasons so agents can self-correct.

## Additional Features to Lift from the Reference Plan
- **Telemetry fidelity**: keep high-frequency sensor ingest (IMU/gyro) in its own ring buffer with time sync so wearable and holographic feeds stay aligned.
- **Layered math**: add optional layers for field/cloth/particle effects that reuse the minimal parameter surface but expose feature flags (`field_mode`, `cloth_mode`).
- **Context-first agents**: embed the “why” in each agent frame (goal + safety + bounds) to keep sub-agents aligned with SDK fidelity rather than overstepping control.
- **Async JSON envelopes everywhere**: ensure even internal module hops (math → render) can be observed/replayed with JSON traces for debugging and training.
- **Gemini/LLM mode**: keep the adapter pluggable so LLMs consume the same envelopes without changing control flow; allow local/offline models as well.

## Failure Modes & Safeguards
- Rate-limit agent patches; require schema validation before applying.
- If SDK channel unavailable, fall back to CPU reference kernels and surface health events.
- Enforce determinism in math kernels (seeded noise, deterministic reductions); log nondeterministic sources.

## Next Technical Steps
1. Define TypeScript/Dart shared schemas for Signal Bus events and agent envelopes.
2. Add WASM build of quaternion and elasticity kernels; validate parity vs CPU reference using test vectors.
3. Wire React/Vite front-end to consume Signal Bus snapshots via websocket; gate UI actions through bus events.
4. Provide Flutter binding that mirrors the bus API and uses platform channels for sensors/haptics.
5. Add Gemini/LLM adapter that consumes/produces the JSON protocol without owning control flow.

### Phase 0 Execution Notes
- **Schemas first**: land `event.v1` and `agent_frame.v1` JSON schemas plus generated TS/Dart bindings to unblock telemetry validation. ✅ (checked in `schema/event.v1.json`, `schema/agent_frame.v1.json`, TypeScript+Dart bindings)
- **Telemetry harness**: stand up websocket ingress with mock wearable/gamepad/OSC emitters; attach monotonic timestamps and schema validation before Signal Bus commit. ✅ (`services/telemetry/ws-server`, `scripts/mock/*.ts` feeding validated envelopes)
- **Buffers**: implement IMU/gyro ring buffers and the Signal Bus journal with replay hooks; expose inspection endpoints for agents and tests. ✅ `IMURingBuffer` + `SignalJournal` land with schema validation in replay harness.
- **Math parity**: add CPU reference kernels (quaternion fusion, elasticity) with vectors + `pnpm test:math` parity checks. ✅ (`packages/math/src/*`, vectors under `tests/vectors/` with test runner)
- **Holographic readiness**: even before rendering, capture/replay `HOLO_FRAME` envelopes so Phase 1+ can validate transports. ✅ HOLO_FRAME fields validated in schemas and runtime validators with websocket ingress support.

### Phase 1 Alignment (early plan)
- **SDK-first ingestion**: swap mock/equivalence layers for vib34d-xr-quaternion-sdk where available; keep mock emitters for regression and jitter comparisons.
- **Schema stability**: freeze `event.v1`/`agent_frame.v1` schemas and generate bindings; log schema diffs between Phase 0 → Phase 1 in a changelog.
- **WASM parity**: compile quaternion/elasticity kernels to WASM with capability metadata (`backend`, `version`, `features`) and snapshot tests vs CPU vectors.
- **Signal Bus adapters**: replace emulated mappings in React/Vite and Flutter shells with SDK-backed adapters while preserving JSON envelopes for agents.
- **Holographic production scope**: continue treating HOLO_FRAME as first-class; run WebXR/OpenXR harness against the Signal Bus replay to keep determinism.
- **Agent constraints**: enforce bounds/focus for spawned sub-agents as SDK wiring tightens, ensuring proposals stay within schema + capability limits.

### Phase 2 Execution (render & UI parity)
- **Signal Bus → UI**
  - React/Vite devtools overlay consumes SDK-backed Signal Bus snapshots via websocket with play/pause/seek and deterministic seed control.
  - Flutter shell mirrors controls with platform channels; HOLO_FRAME routed through a dedicated isolate/IsolateChannel to keep WebXR/OpenXR and wearable feeds deterministic.
  - Both shells must tolerate CPU/WASM math backends; capability discovery flags are surfaced in the overlay to avoid silent backend drift.
- **Exports & goldens**
  - PNG/WebM capture plumbed through a shared export interface (`export_frame`, `export_clip`) with headless Playwright driving web renders and Flutter goldens capturing widget surfaces.
  - Goldens live under `tests/golden/render/{backend}/{surface}/` and are versioned with schema + kernel metadata to detect drift.
  - Snapshot metadata includes Signal Bus seed, frame range, backend, and HOLO_FRAME slice identifiers.
- **Holographic parity**
  - HOLO_FRAME envelopes flow into WebXR/OpenXR harnesses; transforms are kept in quaternion+translation tuples shared with wearable math to avoid parallel implementations.
  - Deterministic replay requires a monotonic clock shim plus depth/color tile alignment; regressions captured as PNG slices and, where supported, short WebM volumetric previews.
  - Polychora remains excluded; holographic is production-scope and must meet the same determinism standard as Faceted/Quantum.
- **Agent render intents**
  - `render_config.v1` derives from Phase 1 schemas and carries style/theme, exposure, grid/debug flags, holographic anchors, and backend hints.
  - Agents may propose `render_intent` and `holo_intent` payloads but must include `focus` paths (e.g., `ui.overlay:panel/devtools` or `holographic.scene:anchor/base`) and respect capability discovery.
  - All proposals are schema-validated, diffed against the current config, and reconciled by the deterministic core before binding to the renderer/holographic graph.
- **Instrumentation & safety**
  - Export interface emits structured logs with timing for ingest → kernel → render to spot jitter (especially BLE/IMU heavy scenes).
  - Lint/format and schema validation run in CI for both TS/Dart bindings; Playwright and Flutter goldens are phase-gated before Phase 2 exit.

### Phase 2 Exit Notes (completed)
- **Signal Bus → UI alignment**: React/Vite overlay and Flutter shell are driven by the SDK-backed Signal Bus with deterministic play/pause/seek and backend discovery surfaced in both shells. HOLO_FRAME routing uses isolates to keep wearable and holographic feeds deterministic.
- **Exports and goldens**: `export_frame` / `export_clip` interfaces are live with Playwright + Flutter capture harnesses storing PNG/WebM goldens under `tests/golden/render/{backend}/{surface}`. Manifests encode schema/kernel/seed metadata for replay.
- **Holographic parity**: WebXR/OpenXR harness replays HOLO_FRAME with monotonic clock shim and depth/color alignment; slices and previews are captured for regression without Polychora placeholders.
- **Agent envelopes**: `render_config.v1`, `render_intent`, and `holo_intent` schemas are frozen with focus/handoff semantics; capability hints prevent agents from requesting unsupported backends or transports.
- **CI gates**: `pnpm test:render`, `pnpm test:holo`, `flutter test`, lint/format, and docs checks (`just docs:phase2`) are wired as blocking gates. `just export:render` and `just holo:replay` refresh baselines with manifests.

### Phase 3 Readiness (agents focus, preview)
- **Inputs for Phase 3**: Signal Bus schemas and render/holographic intents are stable; baselines exist for CPU/WASM/holographic surfaces; telemetry and math kernels expose capability metadata for agent consumption.
- **Expected Phase 3 work**: bind agent orchestration to the stabilized envelopes, enforce spawn bounds and focus/handoff in runtime, and add Gemini/LLM adapters that consume the same JSON protocol without taking control flow.
- **Testing outlook**: expand regression packs to include agent proposal diffs, focus/handoff conflict resolution, and safety rails (rate limits, schema enforcement). Reuse `just export:render` + holographic harness to assert agent-driven mutations remain deterministic.
