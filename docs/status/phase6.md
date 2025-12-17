# Phase 6 Status — Expansion & Advanced Effects

Phase 6 expands the Unified Engine with layered effects, volumetric/holographic
exports, and performance hardening. Work continues to exclude Polychora while
keeping SDK-backed Signal Bus paths authoritative.

## Scope
- Simulate layered field/cloth/particle effects with deterministic outputs
  driven by the minimal parameter set and derived metrics.
- Produce volumetric and holographic slices/tiles suitable for playback and
  regression packs.
- Preserve capability overlays and schema validation across new surfaces.
- Maintain CPU/WASM parity expectations for math kernels once manifests and
  runners are restored.

## Validation Checklist (in progress)
- [x] Effect simulator generates deterministic tiles from validated
      `event.v1` envelopes and derived metrics.
- [x] Volumetric slice helper exports holographic-ready slices with frame
      metadata for replay/regression harnesses.
- [ ] Latency/throughput harness exercised for high-frequency telemetry with
      ring buffer protection. **Blocked**: awaiting pnpm/Flutter/OpenXR runner
      manifests to wire end-to-end transports.
- [ ] `pnpm test`, `pnpm test:render`, `pnpm test:holo`, and OpenXR/WebXR
      harnesses for volumetric exports. **Blocked**: manifests are still
      missing; run immediately upon restoration.
- [ ] `flutter test` and goldens for capability overlays that consume the new
      effect tiles. **Blocked**: Flutter toolchain and workspace descriptors are
      absent; rerun once available.
- [ ] WASM + CPU parity checks for the effect math kernels. **Blocked**:
      requires restored build manifests and runners.

## Progress
- Added a deterministic effect engine that layers configurable effects and
  emits tile-oriented outputs from minimal parameters.
- Export helper now provides volumetric slices to feed holographic playback and
  regression packs with capability overlays intact.
- Performance monitor records validated envelopes in a ring buffer, computes
  latency/jitter aggregates from derived metrics, and exports replay-ready
  samples for downstream overlays.

## Gaps / Next Steps
- Restore pnpm/Flutter/OpenXR/WebXR manifests to exercise end-to-end runners
  and goldens for volumetric overlays.
- Wire the effect tiles into reference UI/CLI overlays once JavaScript
  workspaces return.
- Add WASM parity checks for the effect kernels when build infrastructure is
  available.
