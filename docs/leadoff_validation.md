# Lead-off calibration & validation — 2026-08-29

Bench experiment on the real front end: **1 channel (PA0 = double-differential montage,
2 active electrodes + DRL reference)**, AC coupling, 8–12 s recordings per condition.
Analyzed with `scripts/analyze_capture.py` (which uses `dsp.leadoff_report`).

| Condition | RMS | pk-pk | medF | mains | centroid | Verdict |
|---|---|---|---|---|---|---|
| `all_connected` (rest) | **8.6 mV** | 143 mV | 216 | 4 % | 222 | 🟢 GOOD |
| `contraction` | **59 mV** | 1047 mV | **127** | 6 % | 145 | 🟢 GOOD |
| `no_active1` | 181 mV | 1609 mV | 183 | 30 % | 203 | 🔴 POOR |
| `no_active2` | 901 mV | 2981 mV | 100 | **85 %** | 105 | 🔴 POOR |
| `no_ref` (DRL off) | 835 mV | 2725 mV | 200 | 18 % | 226 | 🔴 POOR |

## Findings
- **Good band = rest 8.6 mV → strong contraction 59 mV RMS.** Real EMG confirmed: medF fell
  216 → **127 Hz** under contraction with only 6 % mains — the physiological signature.
- **All faults ≥ 181 mV RMS** → clean separation from good (≤ 59 mV).
- `no_active2` also floods mains (85 %); `no_ref` and `no_active1` are EMG-ish spectrally but
  20–100× too big — caught by the amplitude ceiling.

## Calibrated thresholds (`dsp.leadoff_report`)
- `rms_hi = 0.12 V` — amplitude ceiling (2× the measured contraction, well below the 181 mV fault floor)
- `mains_dom = 0.5` — mains-band power fraction → mains flood
- `emg_hi = 250 Hz` — spectral-centroid ceiling → non-physiological (floating) noise
- `rail_frac = 0.20` — fraction near 0 V/Vref → open/short
- **Result: 5/5 conditions classify correctly** (rest & contraction GOOD; all 3 electrode faults POOR).

## Notes
- `rms_hi` is **AFE-gain-dependent** — recalibrate (re-run this experiment) if the analog gain changes.
- **DD limitation:** the single PA0 channel flags *that a fault exists*, not *which* electrode. Per-electrode
  isolation needs the 3-node buffer taps / 16:1 mux — see roadmap Part 5.
- Re-analyze any recording: `python scripts/analyze_capture.py [path/to/emg_*.csv]`.
