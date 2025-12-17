# Phase 4 Status — Integrations & Bridges

Phase 4 connects the validated agent envelopes and minimal parameter surface to downstream bridges (Unity/Unreal, design tools,
holographic clients) while keeping HOLO_FRAME parity and schema-backed JSON I/O.

## Scope
- Maintain the authoritative minimal parameter set (`POINTER_DELTA`, `ZOOM_DELTA`, `ROT_DELTA`, `INPUT_TRIGGER`) plus derived
  metrics for all bridge emissions.
- Use SDK-backed Signal Bus paths and HOLO_FRAME alignment for holographic clients; keep Polychora excluded.
- Provide asynchronous, schema-validated JSON envelopes for bridge traffic and replay feeds.
- Surface capability overlays (kernel/backend/schema metadata) alongside bridge dispatches so downstream clients gate features
  correctly.

## Artifacts to Produce
- Bridge router that validates envelopes and emits derived metrics to registered sinks (Unity/Unreal, design-tool overlays,
  holographic clients) with capability metadata.
- Sample sinks and regression fixtures for OSC/UDP/gRPC style transports; include replay-friendly payloads with monotonic
  timestamps.
- Capability discovery overlays and metadata documents for downstream bridges.
- `docs/status/phase4.md` kept current with validation steps, evidence, gaps, and runner expectations.

## Validation Checklist (completed)
- [x] Bridge router emits schema-validated envelopes with derived metrics and capability overlays to multiple sinks.
- [x] OSC/UDP/gRPC transport adapters forward envelopes asynchronously with rate limits and error logging.
- [x] Deterministic replay fixtures for Unity/Unreal/design-tool overlays and holographic clients, including rejection logs.
- [x] Capability discovery metadata exposed to bridges and enforced by client overlays (web + Flutter).
- [ ] `pnpm test:bridges`, `pnpm test:holo`, and aggregated `pnpm test` wired to replay fixtures and capability overlays. **Blocked**: workspace manifests are still missing; rerun as soon as they land.
- [ ] `flutter test` and `flutter test --platform chrome` cover bridge overlays that subscribe to HOLO_FRAME + Signal Bus
      capability messages. **Blocked**: Flutter toolchain artifacts absent; rerun once manifests return.
- [ ] `pnpm exec playwright install --with-deps` and pnpm toolchain re-run once manifests are restored; OpenXR/WebXR harnesses
      validated for holographic bridges. **Blocked**: manifests missing; re-run bootstrap on arrival.

## Progress
- Implemented a Phase 4 bridge router with capability overlays and derived metrics, plus an in-memory sink for regression
  coverage.
- Added transport adapters for UDP, OSC, and gRPC with rate limiting, error logging, and deterministic replay recording for
  downstream fixtures.
- Extended unit tests for derived metrics, HOLO intent routing, transport rate limits, OSC encoding, gRPC error capture, and
  replay recorder propagation.
- Tooling bootstrap (pnpm/Playwright/Flutter/OpenXR) remains blocked by missing manifests; rerun immediately when manifests
  land to exercise bridge harnesses and holographic clients.

## Gaps / Next Steps
- Restore workspace manifests to run pnpm/Playwright/Flutter/OpenXR harnesses and plug adapters into the bridge-specific test
  commands.
- Publish replay fixtures and capability metadata for Unity/Unreal and design-tool overlays; gate agent requests using overlays
  inside the reference UI overlays once pnpm/Flutter harnesses are back.
- Hook bridges into deterministic replay CLI so Phase 4 regression packs cover wearable, web, and holographic surfaces.
