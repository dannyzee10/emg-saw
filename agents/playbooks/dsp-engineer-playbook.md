# DSP Engineer Playbook

## Role
Signal processing: filters, metrics, onset detection.

## Knowledge Base
- `dsp/dsp.py` (existing functions)
- scipy.signal API
- EMG frequency band: 20–450 Hz, notch 50/60 Hz
- Metrics: RMS, median frequency, MVC

## Workflow
1. **Search patterns** with EMGify:
   - `graphify query "bandpass filter scipy"`
   - `graphify explain "dsp.py"`
2. Design filter coefficients (butterworth, notch).
3. Implement metrics with numpy/scipy.
4. Validate with synthetic signals:
   - Generate sine waves and noise
   - Verify filter response in frequency domain
   - Check RMS accuracy
5. Write unit tests under `tests/`.
6. Document algorithm choices in `dsp/`.

## Quality Gates
- Filter attenuates 50 Hz by >40 dB.
- Bandpass passes 20–450 Hz with <3 dB ripple.
- RMS error < 1% on known signal.
- Unit tests pass.

## Exit State
"DSP validated with unit tests"

## Common Pitfalls
- Not normalizing filter coefficients → instability
- Applying filter to whole signal (edge effects) → use lfilter with initial conditions
- Forgetting to detrend before RMS