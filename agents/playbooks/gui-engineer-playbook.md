# GUI Engineer Playbook

## Role
PyQt5 + pyqtgraph real-time instrument GUI.

## Knowledge Base
- `gui/emg_plotter.py` (current monolithic implementation)
- PyQt5 MVC patterns
- pyqtgraph performance tips (e.g., `setDownsampling`, `setClipToView`)

## Workflow
1. **Search patterns** with EMGify:
   - `graphify query "pyqtgraph real-time plot"`
   - `graphify path "emg_plotter.py" "sources.py"`
2. Identify GUI responsibilities: display, controls, recording, report.
3. Refactor into Model/View/Controller if needed.
4. Validate:
   - Run `python gui/emg_plotter.py` (simulated source)
   - Check frame rate ≥ 30 FPS
   - Test recording and playback
5. Document changes and update checkpoints.

## Quality Gates
- GUI remains responsive during data acquisition.
- No memory leak over 10 minutes.
- Recording produces valid CSV with expected samples.

## Exit State
"GUI ready for acceptance test"

## Common Pitfalls
- Blocking the UI thread with serial reads
- Not using pyqtgraph's downsampling → sluggish
- Improper signal/slot connections → memory leaks