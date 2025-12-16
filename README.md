<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
  <h1>Built with AI Studio</h2>
  <p>The fastest path from prompt to production with Gemini.</p>
  <a href="https://aistudio.google.com/apps">Start building</a>
</div>

## Overview
This repository follows a phased delivery approach to ensure every change ships with clear objectives, end-of-phase testing, and recorded analysis. The initial Phase 0 establishes the baseline utilities and plan to support future phases.

## Getting Started
1. Ensure Python 3.10+ is available.
2. Install test dependencies (pytest):
   ```bash
   pip install pytest
   ```
3. Run the automated tests:
   ```bash
   python -m pytest
   ```

## CLI Usage
Use the bundled CLI to manage phases with a JSON-backed tracker (defaults to `phases.json`).

```bash
# Initialize a tracker file with two phases
python -m app.phase_cli --file phases.json init \
  --phase "Phase 0:Baseline repo,Create plan" \
  --phase "Phase 1:Ship feature"

# Add a new phase later
python -m app.phase_cli --file phases.json add "Phase 2" "Validate" "Document"

# Advance the current phase with notes
python -m app.phase_cli --file phases.json advance --notes "Baseline complete"

# Switch active work
python -m app.phase_cli --file phases.json set-active "Phase 1"

# Print the summary view
python -m app.phase_cli --file phases.json summary
```

## Phase Tracking Utility
A lightweight `PhaseTracker` (in `src/app/phase_tracker.py`) models the lifecycle of phases:
- **Add phases** with objectives and automatically activate the first phase.
- **Advance** to complete the current phase and activate the next, while optionally capturing notes.
- **Switch** active phases manually via `set_active`.
- **Summarize** all phases and statuses for quick reporting.

See `docs/PHASE_PLAN.md` for the current roadmap, objectives, and analysis for each phase.
