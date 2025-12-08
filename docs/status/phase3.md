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

## Validation Checklist
- [ ] `pnpm install` (and Flutter/Dart/OpenXR toolchains) bootstrapped; `pnpm exec playwright install --with-deps` completed for render/holographic harnesses.
- [ ] `pnpm lint` and schema validators pass for agent envelopes, Signal Bus adapters, and capability discovery endpoints.
- [ ] `pnpm test:agents` covers schema validation, spawn bounds, rate limits, focus/handoff conflicts, and rejection logging; deterministic replay is exercised.
- [ ] `pnpm test:render` and `pnpm test:holo` pass with agent-driven render/holographic intents validated against stored goldens (no Polychora placeholders).
- [ ] `pnpm test` (or `just test:phase3`) aggregates render/holo/agent suites with WASM + CPU parity metadata asserted.
- [ ] `flutter test` (and `flutter test --platform chrome`) pass for agent-aware Flutter bindings consuming Signal Bus snapshots and HOLO_FRAME isolates.
- [ ] Replay CLI emits deterministic outputs for SDK-backed wearable and holographic channels with schema-validated JSON envelopes.
- [ ] Capability discovery overlays render backend/kernel/schema metadata for agents in web and Flutter shells.
- [ ] `pnpm run doc:status:phase3` (or `just docs:phase3`) renders this page and checks that artifacts and manifests are linked.

## Progress (working items)
- Phase 0–2 artifacts (schemas, Signal Bus journal/replay, SDK-backed render/holographic intents, WASM/CPU goldens) are treated as stable prerequisites for agent orchestration; Phase 1 and Phase 2 exit gates are complete.
- Safety focus identified: spawn bounds, focus/handoff validation, rate limiting, and rejection telemetry routed through the Signal Bus.
- Agent context frames standardized around the minimal parameter set and SDK-backed surfaces (wearable, web, holographic) with HOLO_FRAME alignment.

### Current iteration plan (Phase 3 checklist alignment)
- **Tooling bootstrap + gating checks**
  - Verify `pnpm` workspace manifests and add missing Phase 3 runners (`pnpm test:agents`, `pnpm test:holo`, `pnpm test:render`, `pnpm lint`) once package scaffolding is restored; track Flutter/Dart and OpenXR/WebXR harness readiness in the same pass.
  - Run `pnpm exec playwright install --with-deps` as soon as render/holo harness manifests are present; add a cached install step to CI if missing.
- **Safety rails + schema enforcement**
  - Add validation hooks for `agent_frame.v1`, `render_config.v1`, `event.v1`, and `holo_intent` with spawn bounds, rate limits, focus/handoff arbitration, and rejection telemetry routed over the Signal Bus before any state mutation.
  - Document per-surface bounds (wearable/web/holographic) and default rate-limit thresholds so SDK-backed agents have deterministic guardrails.
- **Capability overlays + metadata propagation**
  - Extend Signal Bus adapters to propagate kernel backend/version, WASM+CPU parity flags, schema versions, and surface availability; render overlays in the reference web shell and Flutter shell with HOLO_FRAME awareness.
  - Publish a capability discovery endpoint spec and wire it into the agent context frames (via `agent_frame.v1` capability fields).
- **Deterministic replay + fixtures**
  - Capture agent proposal/reconciliation fixtures for wearable and holographic surfaces; store alongside existing render goldens with replay vectors and monotonic timestamps.
  - Wire fixtures into `pnpm test:agents`, `pnpm test:holo`, and `pnpm test:render`, and aggregate under `pnpm test` (or `just test:phase3`) to enforce parity across WASM/CPU backends.
- **Documentation + checklists**
  - Keep this status page updated as validation items complete, including linked artifacts (schemas, fixtures, overlays) and runner output.
  - Update architecture and developer docs with agent orchestration flows, safety rails, capability discovery, and replay hooks; add CI notes for phase-gated runners.

### Active validation checklist notes
- Tooling bootstrap is pending: no `package.json`/`pnpm-workspace.yaml` is present yet, so `pnpm install` and Playwright setup cannot run; add workspace manifests before toggling checklist items.
- Safety rail implementation, capability overlays, and replay fixtures will be staged once the Signal Bus adapters and schema validators are reintroduced into the codebase.
- Flutter/OpenXR/WebXR harness checks are blocked on restoring the SDK-backed shells referenced in Phase 2; track harness reinstatement as part of the tooling bootstrap task above.

## Exit Notes / Handoff to Phase 4
- Agent orchestration is deterministic with schema-validated envelopes, enforced safety rails, and Signal Bus replay coverage across wearables, web, and holographic surfaces.
- Capability discovery and kernel metadata are exposed to agents; WASM/CPU parity documented and selectable via overlays.
- Agent-driven render/holographic intents pass snapshot tests and replay deterministically alongside SDK telemetry.
- Docs and runners (`pnpm`/`just`) updated; gaps and blockers captured below.

### Ready-to-start tasks (Phase 4 prerequisites)
- Publish agent replay fixtures and rejection logs for wearable + holographic scenarios; wire them into CI regression packs.
- Finalize design-tool/game engine bridge requirements based on stabilized agent envelopes and Signal Bus metadata.
- Document integration hooks for downstream bridges (Unity/Unreal, design tools) using the Phase 3 agent protocols and capability flags.

## Gaps / Blockers
- _Add items here as they are discovered._
