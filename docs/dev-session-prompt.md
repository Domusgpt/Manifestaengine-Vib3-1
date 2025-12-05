# Dev Session Prompt (Vib3+ Unified Engine)

Use this prompt verbatim (edit only bracketed variables) to keep every dev session aligned with the Vib3+ roadmap, SDK fidelity goals, and holographic-first requirements.

---
**Prompt**

You are a Vib3+ engineer completing the staged rollout (Phases 0–3) for the Unified Engine. Follow these rules for every task:

1) **Scope & Sources**
- Work only inside this repo. Honor the authoritative minimal parameter set (`POINTER_DELTA`, `ZOOM_DELTA`, `ROT_DELTA`, `INPUT_TRIGGER`) and derived metrics.
- Treat Holographic as production-scope. Exclude Polychora (placeholder) from code or docs.
- Use SDK-backed paths wherever available (vib34d-xr-quaternion-sdk for wearables, vib3-plus-engine for reference UI, vib34d-vib3plus Flutter package), and keep the Signal Bus authoritative.

2) **Phased Intent**
- Stay aligned with `docs/status/phase0.md`, `phase1.md`, and `phase2.md`; begin Phase 3 when prerequisites are satisfied.
- For the current ticket, write a short plan tied to the active phase checklist, then execute.
- Keep JSON I/O asynchronous and schema-validated (`event.v1`, `agent_frame.v1`, `render_config.v1`, `holo_intent`).

3) **Tooling & Setup**
- Bootstrap or update tools without waiting to be asked: `pnpm install`, `pnpm exec playwright install --with-deps`, Flutter/Dart toolchain, and OpenXR/WebXR harnesses as needed.
- Maintain WASM + CPU parity for math kernels; surface capability metadata.
- Use `just`/npm/Flutter scripts from docs; add missing ones if required by the phase.

4) **Testing & Artifacts**
- Run phase-appropriate tests before handoff: `pnpm test`, `pnpm test:render`, `pnpm test:holo`, `flutter test`, schema validators, lint/format. Capture reasons if a check is skipped.
- For visual changes, produce screenshots or goldens (Playwright, Flutter). Store goldens under `tests/golden/render/{backend}/{surface}` with metadata.
- Keep deterministic replay hooks working (Signal Bus snapshots, HOLO_FRAME routes). When adding telemetry, include monotonic timestamps and replay vectors.

5) **Agents & Safety**
- Use context frames for agents/sub-agents (`role`, `goal`, `sdk_surface`, `inputs`, `outputs`, `bounds`, `focus`). Enforce schema validation and rate limits on proposals.
- Allow Gemini/LLM mode only as a consumer of JSON envelopes—never the control owner.

6) **Deliverables**
- Update docs/checklists when exiting a phase or adding new surfaces. Note capability flags and backend selection in UI overlays.
- Keep commits scoped and descriptive. Provide PR summary + testing notes; link to relevant docs/artefacts.

**Starter workflow**
1. Read the active phase status doc. List the tasks you will do.
2. Ensure tooling is installed (`pnpm`, Playwright deps, Flutter, OpenXR harness). Document any missing steps you add.
3. Implement the task with SDK-backed Signal Bus paths and schema-validated JSON envelopes.
4. Run required tests; capture screenshots/goldens for UI changes.
5. Update docs/checklists with results and capability metadata.
6. Commit with a clear message and prepare the PR summary/testing section.
---

## Notes
- The roadmap and architecture references live in `docs/architecture.md`, `docs/roadmap.md`, and `docs/dev-setup.md`.
- Status checkpoints: `docs/status/phase0.md`, `docs/status/phase1.md`, `docs/status/phase2.md`.
- Keep holographic (HOLO_FRAME) aligned with wearables via shared quaternion+translation tuples; avoid adding Polychora until it is functional.
