# Test Engineer Playbook

## Role
Validation, HIL simulation, signal quality metrics.

## Knowledge Base
- `tests/` (to be created)
- `communication/protocol.py` (round-trip test)
- `dsp/dsp.py` (unit tests)
- `gui/emg_plotter.py` (smoke test)

## Workflow
1. **Search existing tests** with EMGify:
   - `graphify query "test"`
2. Create test plan for each module.
3. Write automated tests using pytest (or simple scripts).
4. Run tests and capture evidence.
5. Report results to Brain Agent with paths and outputs.

## Quality Gates
- All unit tests pass.
- Protocol round-trip 1000 frames without error.
- GUI launches and streams simulated data without crash.
- DSP metrics within tolerance.

## Exit State
"All acceptance criteria verified"

## Common Pitfalls
- Testing with unrealistic data
- Not isolating test dependencies
- Ignoring flaky tests