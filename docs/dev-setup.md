# Development Environment & Tooling

To make the Unified Engine easy to build, test, and extend across web, mobile, and wearable targets, provision the following tools in your environment. These selections prioritize compatibility with the Vib3 SDK branches and the Signal Bus/agent architecture.

## Core Runtimes
- **Node.js 20.x** with **pnpm** (preferred for Vite/React front-end and tooling).
- **Dart 3.x / Flutter stable** for mobile/wearable bindings and CanvasKit targets.
- **Python 3.11+** for scripting, CLI automation, and reference math kernels.
- **OpenXR/WebXR runtimes** (or platform emulators) for holographic/volumetric testing.

## Suggested Global Tooling
- `pnpm` for deterministic JS package management.
- `just` or `make` for repeatable task runners (tests/builds).
- `protobuf` / `grpcurl` if gRPC is used for engine-to-game communication.
- `wasm-pack` (Rust) if building WASM math kernels.
- `ninja` / `cmake` for native builds of math libraries when required.
- `openxr-loader`/`openxr-sdk` and WebXR emulator tools for holographic validation.
- `ffmpeg` with `libvpx`/`libaom` for WebM exports and volumetric slice encoding.
- `jq` / `yq` for JSON/YAML schema validation and scripted telemetry traces.
- `just` recipes for phase-gated docs/tests (`just docs:phase1`, `just test:phase2`).
- **Bootstrap commands (Linux/debian-ish)**: 
  - `sudo apt-get update && sudo apt-get install -y build-essential ninja-build cmake protobuf-compiler ffmpeg libaom-dev libvpx-dev openxr-sdk x11-utils`.
  - `corepack enable pnpm` (or `npm i -g pnpm`) and `cargo install wasm-pack` for WASM builds.
  - `pip install pipx && pipx install yq` for YAML/JSON tooling; `pip install hypothesis` for property tests.
  - `dart --disable-analytics` after installing Flutter SDK; run `flutter config --enable-web` for CanvasKit targets.
  - `pnpm exec playwright install --with-deps` to provision browsers for snapshot testing.

## Front-end / Rendering Stack
- **Vite** + **React** with **TypeScript**.
- **WebGL2** and **regl/three.js** helpers for rapid shader prototyping.
- **Playwright** for headless visual regression (screenshots of shader outputs and UI states).
- **WebXR emulator + three.js/WebXR** shims to exercise holographic transforms from the Signal Bus.

## Mobile / Wearable Stack
- Flutter SDK + `flutter test` support.
- Platform channels for BLE/IMU ingress; recommend `flutter_blue_plus` for BLE prototyping.
- Optional Unity/Unreal bridge via OSC/UDP for game telemetry.
- OpenXR-capable Android emulator/device configuration for holographic shells.

## Quality & Testing
- **Vitest** or **Jest** for unit tests on Signal Bus logic.
- **Playwright** snapshot tests for WebGL surfaces (PNG/WEBM capture).
- **Golden tests** in Flutter for widget/layout consistency.
- **Property-based tests** (e.g., `fast-check` or `hypothesis`) for math invariants (quaternion normalization, elasticity bounds).
- **Reference test vectors** stored in `tests/vectors/*.json` for kernel parity across CPU/WASM/GLSL.
- **OpenXR conformance smoke tests** or mocked session tests to ensure holographic transports remain deterministic and production-grade (they are first-class like Faceted/Quantum).
- **Phase gates**: add per-phase test scripts (`just test:phaseN`) that align with the roadmap milestones (telemetry, SDK alignment, rendering, agents, integrations, advanced effects).
- **Docs as gates**: require updated quickstart/checklist pages per phase (e.g., `docs/status/phase2.md`) so teams know which tools and transports are validated.
- **Phase 0 specifics**: run `pnpm test:math`, `pnpm test:telemetry`, `pnpm test:ws`, and `pnpm test:replay` as soon as schemas, buffers, and mock ingestors land; wire `pnpm run doc:status:phase0` to render status updates.

## Linting & Formatting
- **ESLint** + **Prettier** for JS/TS.
- **dart format / dart analyze** for Dart.
- **clang-format** for any C++/GLSL snippets, if added.

## Local Services for Development
- Websocket dev server to stream JSON telemetry to the Signal Bus.
- Mock wearable device service emitting IMU/quaternion data for playback.
- Minimal HTTP control plane to issue agent commands and fetch state snapshots.
- Holographic/WebXR test harness that publishes/consumes `HOLO_FRAME` events without relying on placeholder stacks (omit Polychora until it is real).
- Deterministic replay CLI that can target both wearable and holographic channels for regression and benchmarking.

## Recommended VS Code Extensions
- Dart/Flutter, ESLint, Prettier, shader languages support (GLSL), Rust (if using wasm-pack), and Playwright Test for VS Code.

## Scripts to Add (future)
- `just setup` (installs Node, pnpm, Dart, Playwright browsers, wasm-pack).
- `just dev:web` (runs Vite + websocket telemetry server).
- `just dev:flutter` (runs Flutter app with mock BLE data).
- `just test` (aggregates unit + e2e + snapshot tests).
- `just lint` (runs lint/format check for TS and Dart).
- `just docs:phaseN` (renders phase-specific status pages and checks for missing test artifacts).

Keeping these tools in place ensures the engine can be validated quickly across web, desktop, and wearable targets while staying faithful to the SDK contracts.
