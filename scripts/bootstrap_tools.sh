#!/usr/bin/env bash
set -euo pipefail

# Bootstrap core tooling for the Vib3+ Unified Engine repo.
# The script is idempotent and focuses on development-time dependencies
# that unblock phased testing (Python fast gates, pnpm/Playwright, Flutter web targets).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

missing=()
require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    missing+=("$1")
  fi
}

# Minimum runtime/tooling checks
require_cmd node
require_cmd pnpm
require_cmd python3
require_cmd pip
require_cmd dart
require_cmd flutter
require_cmd cmake
require_cmd ninja
require_cmd protoc

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing required tools: ${missing[*]}" >&2
  echo "Install the listed tools, then re-run this bootstrap script." >&2
  exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r "$ROOT_DIR/requirements-dev.txt"

# Install JS deps without executing project scripts to avoid side effects.
if [ -f "$ROOT_DIR/package.json" ]; then
  PNPM_HOME=${PNPM_HOME:-$HOME/.local/share/pnpm}
  export PNPM_HOME
  pnpm install --ignore-scripts
  pnpm exec playwright install --with-deps
fi

# Prep Flutter for web/CanvasKit snapshots if the SDK is present.
if command -v flutter >/dev/null 2>&1; then
  flutter config --enable-web
  dart --disable-analytics || true
fi

echo "Tooling bootstrap complete. Run pytest for fast gates, then phase-specific suites as manifests allow." 
