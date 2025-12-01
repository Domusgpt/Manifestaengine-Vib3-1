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

## Holographic System Alignment
- **Scene abstraction**: standardize on a scene graph with typed nodes (camera, light, emitter, volumetric mesh). Maintain a minimal schema that agents can mutate without breaking determinism.
- **Transport**: use a dedicated topic (e.g., `HOLO_FRAME`) on the Signal Bus that carries either compressed depth+color tiles or light-field coefficients; gate by capability discovery (OpenXR/WebXR).
- **Reactivity**: allow agents to propose holographic intents (`holo_focus`, `holo_blend`, `holo_anchor`) that are validated and merged by the deterministic core before committing to the graph.
- **Interop**: expose holographic transforms as the same quaternion+translation tuples used for wearables so math kernels are shared. Provide adapters for AR-capable Flutter shells and WebXR-enabled browsers.
- **Export**: support headless renders for regression (PNG slices) and streamed volumetric previews for development.

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
