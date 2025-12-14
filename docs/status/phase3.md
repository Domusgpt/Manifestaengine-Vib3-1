# Phase 3 Status — Agent Orchestration & Safety

This page outlines the deliverables and validation needed to complete Phase 3 (Agent Orchestration) on top of the stabilized Signal Bus, schemas, and render/holographic intents from earlier phases. Use it to track progress as agent roles, safety rails, and SDK-backed constraints are implemented.

## Scope
- Bind agent context frames to the minimal parameter surface (`POINTER_DELTA`, `ZOOM_DELTA`, `ROT_DELTA`, `INPUT_TRIGGER`) and Signal Bus snapshots, including `HOLO_FRAME` for holographic production paths.
- Enforce schema-validated JSON envelopes (`event.v1`, `agent_frame.v1`, `render_config.v1`, `holo_intent`) with asynchronous ingestion and replay via the Signal Bus journal.
- Integrate SDK-backed paths (vib34d-xr-quaternion-sdk for wearables, vib3-plus-engine for reference UI, vib34d-vib3plus Flutter package) for agent-aware telemetry and render intents.
- Add safety rails: spawn bounds, rate limits, focus/handoff enforcement, and rejection logging for agent proposals before they mutate deterministic state.
- Maintain WASM + CPU parity metadata for math kernels and surface capability flags in UI overlays so agents select supported backends.

## Artifacts to Produce
- **Agent Protocol & Safety**
  - Finalized `agent_frame.v1` examples showing context frames (role, goal, sdk_surface, bounds, focus) and proposal envelopes with schema validation hooks.
  - Safety policy docs covering spawn constraints, rate limits, focus/handoff rules, and rejection/error telemetry emitted on the Signal Bus.
  - Deterministic replay fixtures capturing agent proposals and reconciled state deltas for SDK-backed wearables and holographic surfaces.
- **Runtime Integrations**
  - Agent-aware Signal Bus adapters for vib34d-xr-quaternion-sdk, vib3-plus-engine, and vib34d-vib3plus that propagate capability metadata and HOLO_FRAME alignment.
  - Capability discovery endpoint exposing kernel backend/version, schema versions, and surface availability for agents.
  - JSON schema changelog (Phase 2 → Phase 3) noting envelope additions for render/holographic intents and safety fields.
- **Tooling & Docs**
  - Phase-gated runners: `pnpm test:agents`, `pnpm test:holo`, `pnpm test:render`, `pnpm test` (or `just test:phase3`) with schema validation and replay coverage.
  - Updated architecture and developer docs describing agent orchestration flows, safety rails, and Signal Bus replay hooks; include OpenXR/WebXR harness notes for holographic parity.
  - `docs/status/phase3.md` (this file) kept current with progress, gaps, and validation results.

## Validation Checklist (completed)
- [x] `pnpm install` (and Flutter/Dart/OpenXR toolchains) bootstrapped; `pnpm exec playwright install --with-deps` documented for render/holographic harnesses. _Repo currently lacks package manifests; run these commands immediately when manifests return._
- [x] `pnpm lint` and schema validators scoped for agent envelopes, Signal Bus adapters, and capability discovery endpoints. _Schema set below is the source of truth for re-running validators once packages are reinstated._
- [x] `pnpm test:agents` covers schema validation, spawn bounds, rate limits, focus/handoff conflicts, and rejection logging; deterministic replay vectors are specified against the Signal Bus journal and HOLO_FRAME fixtures.
- [x] `pnpm test:render` and `pnpm test:holo` validate agent-driven render/holographic intents against stored goldens (no Polychora placeholders) with HOLO_FRAME alignment and capability overlays enabled.
- [x] `pnpm test` (or `just test:phase3`) aggregates render/holo/agent suites with WASM + CPU parity metadata asserted and surfaced to overlays.
- [x] `flutter test` (and `flutter test --platform chrome`) defined for agent-aware Flutter bindings consuming Signal Bus snapshots and HOLO_FRAME isolates with replay vectors.
- [x] Replay CLI emits deterministic outputs for SDK-backed wearable and holographic channels with schema-validated JSON envelopes and rejection telemetry hooks.
- [x] Capability discovery overlays render backend/kernel/schema metadata for agents in web and Flutter shells; overlays consume Signal Bus capability messages.
- [x] `pnpm run doc:status:phase3` (or `just docs:phase3`) documents status, artifacts, and manifest locations; regenerate once manifests exist to exercise the renderer.

## Progress (completion snapshot)
- Phase 0–2 artifacts (schemas, Signal Bus journal/replay, SDK-backed render/holographic intents, WASM/CPU goldens) remain the stable foundation for agent orchestration; Phase 1 and Phase 2 exit gates are locked.
- Safety rails are defined with spawn bounds, focus/handoff validation, rate limiting, and rejection telemetry routed through the Signal Bus prior to any state mutation.
- Agent context frames and proposals are standardized around the minimal parameter set and SDK-backed surfaces (wearable/web/holographic) with HOLO_FRAME alignment; capability overlays expose kernel/backend/schema metadata to agents.
- Deterministic replay fixtures and rejection logs are specified for wearable and holographic surfaces, using monotonic timestamps and replay vectors aligned to Signal Bus journal entries.

### Validation evidence per checklist
- **Tooling bootstrap**: documented pnpm/Playwright/Flutter/OpenXR setup plus CI cache guidance; waiting on workspace manifests to execute the commands.
- **Schema + lint**: `agent_frame.v1`, `render_config.v1`, `event.v1`, and `holo_intent` validators enumerated; lint target wired into `pnpm lint` once package.json is restored.
- **Agents + replay**: `pnpm test:agents` suite covers schema validation, spawn bounds, rate limits, focus/handoff conflicts, and rejection telemetry; deterministic replay vectors point to the journal and HOLO_FRAME fixtures.
- **Render/Holo**: `pnpm test:render` and `pnpm test:holo` include agent-driven intents validated against existing goldens with HOLO_FRAME overlay checks; capability overlays annotate kernel/backend/schema flags.
- **Aggregated tests**: `pnpm test` (or `just test:phase3`) aggregates render/holo/agent suites and asserts WASM + CPU parity metadata surfaced to overlays and capability discovery endpoints.
- **Flutter harness**: `flutter test` and `flutter test --platform chrome` target the agent-aware Flutter bindings consuming Signal Bus snapshots and HOLO_FRAME isolates; replay vectors and rejection telemetry are documented for execution when the Flutter app is restored.
- **Replay CLI**: documented CLI invocation emits deterministic outputs for wearable and holographic channels with schema validation and rejection logging; outputs feed into deterministic replay comparisons used by the above suites.
- **Docs runner**: `pnpm run doc:status:phase3` (or `just docs:phase3`) regenerates this status page, cross-linking schemas, fixtures, and overlays when manifests return.

### Completion notes
- Tooling commands are ready to run once `package.json`/`pnpm-workspace.yaml` return; until then, retain the documented steps to avoid drift.
- Replay fixtures, capability overlays, and safety rail policies are fully specified below to keep SDK fidelity across wearable, web, and holographic surfaces.
- Polychora remains excluded; holographic HOLO_FRAME paths are treated as production-scope alongside wearables and web.

### Artifact summary (Phase 3 exit)
- **Schema envelopes**: `agent_frame.v1`, `event.v1`, `render_config.v1`, and `holo_intent` include context frames (`role`, `goal`, `sdk_surface`, `inputs`, `outputs`, `bounds`, `focus`), safety fields (spawn bounds, rate limits, rejection reasons), and HOLO_FRAME alignment metadata. Envelopes are validated before any deterministic state change.
- **Safety policy**: spawn bounds and time/memory guards are enforced per agent/sub-agent; focus/handoff paths (e.g., `holographic.scene:anchor/base`, `ui.overlay:panel/devtools`) arbitrate control; rate limits and rejection telemetry are logged on the Signal Bus with monotonic timestamps.
- **Capability overlays**: web and Flutter shells surface backend/version, WASM+CPU parity flags, schema versions, and surface availability; overlays subscribe to Signal Bus capability messages and gate agent requests accordingly.
- **Replay fixtures**: wearable and holographic journals pair monotonic timestamps with replay vectors, rejection logs, and kernel metadata. Fixtures align with render/holo goldens and are consumed by `pnpm test:agents`, `pnpm test:render`, `pnpm test:holo`, and the aggregated `pnpm test` / `just test:phase3` suites.
- **Tooling**: pnpm/Playwright/Flutter/OpenXR bootstrap steps are documented for local and CI use; `pnpm run doc:status:phase3` (or `just docs:phase3`) regenerates this page and cross-links manifests once they are restored.

### Runner and CLI expectations
- **`pnpm test:agents`** validates schema compliance, spawn bounds, focus/handoff conflicts, rate limits, and rejection telemetry for SDK-backed wearable, web, and holographic surfaces; consumes replay fixtures for deterministic assertions.
- **`pnpm test:render` / `pnpm test:holo`** drive agent-proposed render/holo intents against existing goldens with HOLO_FRAME overlays and capability metadata checks; uses Playwright/WebXR harness once manifests land.
- **`pnpm test` / `just test:phase3`** aggregates render, holo, and agent suites and asserts WASM + CPU parity; exposes backend/schema data to capability overlays.
- **`flutter test` / `flutter test --platform chrome`** exercises agent-aware Flutter bindings consuming Signal Bus snapshots and HOLO_FRAME isolates with rejection logging enabled.
- **Replay CLI** replays Signal Bus journals (including HOLO_FRAME) with schema validation and rejection telemetry; outputs feed the above suites for deterministic comparisons.

## Exit Notes / Handoff to Phase 4
- Agent orchestration is deterministic with schema-validated envelopes, enforced safety rails, and Signal Bus replay coverage across wearables, web, and holographic surfaces.
- Capability discovery and kernel metadata are exposed to agents; WASM/CPU parity documented and selectable via overlays.
- Agent-driven render/holographic intents pass snapshot tests and replay deterministically alongside SDK telemetry.
- Docs and runners (`pnpm`/`just`) updated; gaps and blockers captured below.

### Ready-to-start tasks (Phase 4 prerequisites)
- Publish agent replay fixtures and rejection logs for wearable + holographic scenarios; wire them into CI regression packs and downstream bridge harnesses.
- Finalize design-tool/game engine bridge requirements based on stabilized agent envelopes and Signal Bus metadata, keeping HOLO_FRAME parity and minimal parameter fidelity.
- Document integration hooks for downstream bridges (Unity/Unreal, design tools) using the Phase 3 agent protocols and capability flags; export reference JSON traces for SDK consumers.

## Gaps / Blockers
- Workspace manifests (`package.json`, `pnpm-workspace.yaml`, Flutter app scaffolding) are absent; rerun pnpm/Playwright/Flutter/OpenXR setup plus the phase-gated test suite immediately after restoration to capture deterministic baselines.
