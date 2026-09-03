<!-- converted from EMG-SAW_Weekly_Report_2026-08-28_to_09-03.docx -->

EMG-SAW - Weekly Progress Report
Real-time surface-EMG acquisition system + Noraxon-style analysis GUI
Week of 28 August - 3 September 2026   |   Muhammad Daniyal, MS Biomedical Engineering, Beihang University
Platform: STM32F103 Blue Pill + AD8237 AFE  ->  PyQt5 / pyqtgraph scope  (2 kHz, 921600 baud)

# 1. Executive Summary
This week the EMG-SAW instrument reached feature parity with a commercial clinical EMG workflow (Noraxon MR): full MVC calibration and %MVC amplitude normalization, a configurable signal-processing pipeline, an offline review/playback mode, and reporting. In parallel, the electrode lead-off detection was hardened against real disconnection faults, the DSP was audited against the standard biomechanics literature, and the complete feature set was validated hardware-in-the-loop on real forearm EMG. All 55 automated tests pass. The system is now ready for the exoskeleton no-load / assisted comparison study.
# 2. Starting Point (28 August)
The week began from the SAW hand-off baseline:
- Acquisition -  a 5-channel STM32 sEMG acquisition firmware streaming to a real-time PyQt5 scope;
- Analytics -  RMS, median/mean frequency, iEMG, co-contraction, onset/offset and a live fatigue readout (M3);
- Signal quality -  a PC-side electrode lead-off indicator (rail / mains heuristic), not yet calibrated to real hardware.
# 3. Work Completed
## 3.1  Electrode lead-off & signal integrity
- Calibration -  amplitude ceiling and spectral-shape cues tuned against five real electrode conditions (5/5 correct).
- 200/400 Hz signature -  discovered and encoded the empirical disconnection signature - a floating signal lead loses its 50/100 Hz mains pickup and jumps to 200/400 Hz - giving an amplitude-independent lead-off flag that a plain RMS test misses.
- Baseline-follows-dot -  the resting-baseline check now follows the same latched lead-off state that colours the channel dot (green = connected+relaxed, amber = poor/ref issue, red = signal lead off).
## 3.2  Noraxon-parity feature set (15-screen workflow)
- MVC calibration -  guided MVC dialog (baseline check to record max to capture peak to use), saved to a persistent MVC stack.
- %MVC normalization -  live normalized view (rest ~ 0 %, max ~ 100 %) for raw EMG and RMS envelope, with an amplitude display range.
- Amplitude/Smoothing config -  selectable smoothing algorithm (RMS / mean-absolute) and window (ms), plus a real-time processing pipeline.
- Guided recording -  Record to Pause to Stop step hints, a Show-Raw override, and Save-Data dialogs after both MVC and test recordings.
- Review mode -  offline playback of a saved recording with a scrub cursor, switchable operations and an HTML report.
- Signal Processing -  an Available-to-Selected pipeline builder (rectify, band-pass, notch, smoothing, normalization) with per-channel scope.
- Offline amplitude normalization -  normalize to Peak / Mean / MVC / Manual / Other-record, optionally restricted to a picked time window, with the green peak-window and % axis result view.
## 3.3  New feature - %MVC target biofeedback
Added a live target line + tolerance band on the %MVC view so the user can hold a constant effort. This enabled a textbook constant-force fatigue demonstration (see section 4, C4).
## 3.4  UX and layout
- italic step hints, large green action buttons, colour-coded result banners.
- the control toolbar was split into two rows so the live rate/quality readout and the Record/Pause actions are always visible (they previously clipped on window resize).
## 3.5  DSP academic verification
Every metric was checked against the standard literature and against signals with a known analytical answer; citations were added to the code and one canonical implementation is now shared across the scope, review and scripts. The formulas match those used by Noraxon / Delsys (see section 5).
# 4. Hardware-in-the-Loop Validation (real forearm EMG)
Each feature was validated on live single-channel forearm-flexor EMG; recordings were analysed with the project tools (analyze_capture.py, emg_features.py, analyze_graded.py).
Highlight: with the new target-guide holding the force constant, the fatigue trial produced the classic curve - median frequency down 18 % while RMS was maintained - versus a declining-force trial without it, confirming both the analytics and the biofeedback feature.
# 5. Academic Standing - formulas vs. literature
Each row is covered by an automated test that verifies the formula against a signal with a known answer (e.g. a 150 Hz tone returns MDF = MNF = 150 Hz).
# 6. Software Quality
- Tests - 55 automated tests passing (headless GUI smoke, MVC/dialogs, lead-off, DSP metrics, pipeline, review).
- Traceability - 25 commits this week; knowledge-graph (graphify) rebuilt - 767 nodes across the gui / dsp / firmware / test continents.
# 7. Next Steps
- Exoskeleton demo -  record the loaded forearm task with and without the exoskeleton/support and run the No-Exo vs Exo %MVC / iEMG comparison (the muscle demand reduced by X % result).
- Extension -  multi-channel agonist/antagonist co-contraction during the assisted task.
- Packaging -  re-compile the standalone build and confirm the two-row toolbar and target-guide on the packaged app.

EMG-SAW - SAFe Agentic Workflow - report generated 3 September 2026
| # | Test | Result | Verdict |
| --- | --- | --- | --- |
| A0 | Lead-off dot + baseline vs electrode state | green rest / red signal-off (200-400 Hz) / amber ref-off | PASS |
| A1 | Quiet resting baseline | RMS 6.9 mV, mains 1 %, GOOD | PASS |
| B1 | MVC capture (max hold) | medF 129 Hz, mains 6 %, GOOD; MVCref 56 mV | PASS |
| C1 | %MVC linearity (graded squeeze) | 8 - 14 - 18 - 30 - 63 %, strictly monotonic | PASS |
| C2/C3 | %MVC repeatability (x2) | mean 10.3 % vs 10.0 % (delta 3 %) | PASS |
| C4 | Fatigue (constant-force + target) | medF 76 -> 62 Hz (-18 %), RMS held (+5 %) | PASS (TEXTBOOK) |
| D1 | Smoothing / amplitude config | 250 ms smoother; %MVC stable; axis rescales | PASS |
| E1 | Review playback + report | playback, operations, HTML report all work | PASS |
| F | Offline normalize (Peak/Window/MVC/Manual) | green window + % axis; pick-window rescales; ref-driven | PASS |
| Metric | Formula | Reference |
| --- | --- | --- |
| RMS envelope | sqrt(mean x^2), moving window | Basmajian & De Luca 1985; SENIAM |
| iEMG | integral |EMG| dt | Basmajian & De Luca 1985 |
| Mean freq (MNF) | Sum f*P / Sum P | De Luca 1997; Merletti & Parker 2004 |
| Median freq (MDF) | f where Sum(<=f) P = 1/2 Sum P | De Luca 1997; Merletti & Parker 2004 |
| Co-contraction | 2*Sum min(a,b) / Sum(a+b) * 100 | Falconer & Winter 1985 |
| Onset detection | threshold + minimum duration | Hodges & Bui 1996 |
| Fatigue index | linear slope of MDF(t) | Merletti et al. 1991; De Luca 1997 |
| Band-pass | 20-450 Hz Butterworth, zero-phase | SENIAM / Hermens 2000 |