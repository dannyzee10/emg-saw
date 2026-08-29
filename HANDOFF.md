# EMG SAW — HANDOFF (read this first)

**You are a new agentic session or a human coworker opening this repo cold.**
This file is your complete memory: what the system is, how to run it, what each agent
built, and exactly what to do next. Facts are locked in `PROJECT_CONTEXT.md`; the hard
gates are in `QUALITY_BAR.md`; the code-by-agent map is `agent_map.html`.

---

## 0. How to use this handoff
1. Read this file top-to-bottom (10 min).
2. Read `PROJECT_CONTEXT.md` (locked facts) and `QUALITY_BAR.md` (hard gates).
3. Open `agent_map.html` to see the code-by-agent world map.
4. Pick up the **Deep Plan (§6)** for your agent.

---

## 1. Mission
Build a **5-channel dry-electrode surface-EMG (sEMG) acquisition system + real-time GUI** —
a self-owned, open, ~100× cheaper alternative to **Noraxon MR / Delsys Trigno**.
Owner: **Muhammad Daniyal**, MS Biomedical Engineering, **Beihang University**.
Stack: **Python + PyQt5 + pyqtgraph + pyserial + numpy/scipy** (PC) · **STM32 HAL/C** (firmware).

## 2. Quick start — open the EMG scope
Prereqs: Python 3.12; `python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt`.
Hardware: STM32 flashed with CP4 firmware, **CP2102 on COM8**, ST-Link connected.

```powershell
# 1. NO HARDWARE — see the full UI immediately (demo):
python emgscope.py --sim --channels 5

# 2. REAL HARDWARE (CP4 binary firmware @ 2 kHz):
#    (first, if the board isn't running:  Build in CubeIDE, then  .\scripts\flash_run.bat)
python emgscope.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick
```
**Always launch via `emgscope.py`** (it sets the package path for the MVC layout).
`--kick` wakes the board (it does not auto-start). Never use the CubeIDE Debug/Run buttons —
use `scripts\flash_run.bat`. If COM8 changed after a reboot: `python -m serial.tools.list_ports -v`.

## 3. Current state — DONE ✅ (as of 2026-08-27)
| CP | What | Status |
|----|------|--------|
| CP1 | blink / toolchain / ST-Link flash / 72 MHz | ✅ |
| CP2 | USART1 → CP2102 → PC | ✅ |
| CP3 | 1× ADC → live scope tracks PA0 | ✅ |
| CP4 | **TIM3 → ADC circular-DMA (HT/TC ping-pong) → binary @ 2 kHz** | ✅ ~2010 S/s, 0 crc-err |
| CP5 | signal sanity | partial (noise = antenna, confirmed) |
| CP6 | **5 channels + real gel AFE** | ⏭ NEXT |

**GUI = branded MVC instrument** (`gui/`): sweep/scroll, DC/AC/GND coupling, V/div, Time/div,
framed graticule, per-channel panel (muscle name, RMS, pk-pk, **median freq**, activation meter),
**MVC % normalization**, **onset highlight**, **live FFT spectrum**, markers, snapshot, HTML report,
metadata-rich CSV. Recently refactored into **MVC** (`model.py`, `controller.py`, `plot_widget.py`,
`channel_panel.py`, `recording_controller.py`).

## 4. Repo map
```
emg-saw/
  emgscope.py            ← LAUNCH THE SCOPE via this
  HANDOFF.md PROJECT_CONTEXT.md QUALITY_BAR.md AGENT_OWNERSHIP.yml TOKEN_POLICY.md CLAUDE.md
  gui/        emg_plotter.py + MVC (model/controller/plot_widget/channel_panel/recording_controller)
  dsp/        dsp.py (filters, RMS, median-freq, envelope)
  communication/ protocol.py (frames+CRC) · sources.py (Serial/Ascii/Sim readers)
  firmware/   *.md guides + emg_bluepill/main.c, stm32f1xx_it.c (CP4 source of truth)
  scripts/    agent_map.py (world-map) · refresh.ps1 · flash_run.bat · hooks/pre-commit
  docs/       CHECKPOINTS.md · EMG_System_Architecture.md · EMG_SAW_Project_Plan.md
              · EMG_SAW_Retro_and_Competitive_Roadmap.md · EMG_REALTIME_README.md
  .claude/agents/  the 6 agents · graphify-out/ graph + GRAPH_REPORT · agent_map.html
```

## 5. What each agent did (retro) — the memory of the build
- **SYSTEMS-ARCHITECT:** pipeline + protocol contract, CP checkpoint discipline, SAW workspace,
  QUALITY_BAR, PROJECT_CONTEXT, agent world-map, freshness rule.
- **FIRMWARE-ENGINEER:** CP1→CP4 (blink→UART→ADC→**TIM3+DMA ping-pong 2 kHz binary**); solved
  TIM3-not-TIM2, USART1-IRQ lockup, baud, DTR-reset, no-auto-start.
- **GUI-ENGINEER:** full branded instrument, then **MVC refactor**.
- **DSP-ENGINEER:** band-pass/notch/RMS-envelope, **median frequency**, **MVC %**, **live FFT**,
  onset — validated (100 Hz tone → 100 Hz).
- **HARDWARE-ENGINEER:** discrete AFE + driven guard; dry-electrode failure diagnosis; noise =
  antenna pickup (shorted PA0 ≈ 0).
- **TEST-ENGINEER:** headless GUI smoke tests, protocol round-trip + noise-resync (recursion) fix,
  5-ch binary parse verified, independent review.

## 6. DEEP PLAN — what each agent does NEXT (backlogs)
> Gate everything through `QUALITY_BAR.md`. Log every checkpoint in `docs/CHECKPOINTS.md`.

**SYSTEMS-ARCHITECT**
1. Keep `emg-saw` the single source of truth; enforce freshness (`scripts/refresh.ps1`, hook).
2. Sequence the milestone ladder (below); own the ADS1299 go/no-go decision.
3. Add `__init__.py` to gui/dsp/communication OR keep namespace-package + `emgscope.py` (done) as the
   supported launch path; document it in README.

**FIRMWARE-ENGINEER**
1. **CP6 — 5 channels:** ADC Scan Enabled, ranks PA0–PA4, `#define NCH 5`, rebuild → `flash_run.bat`.
2. Verify 5-ch @ 2 kHz: steady S/s, drop≈0, crc≈0 (HG2).
3. Later: **ADS1299 SPI driver** (24-bit); seq/timestamp robustness; optional USB-CDC.

**GUI-ENGINEER**
1. Finish/verify the **MVC refactor** (remove leftover `DEBUG:` print in `emg_plotter.py`); headless
   smoke test must pass (HG4).
2. 5-lane view polish + per-channel muscle labels; session/trial manager; replay/review; MVC workflow UX.
3. Package a one-click **`.exe`** (PyInstaller) for the coworker.

**DSP-ENGINEER**
1. Add **iEMG**, **mean frequency**, **co-contraction index**, onset/offset timing with thresholds,
   fatigue trend over a trial. Unit-test each (HG3).
2. Per-channel calibration (gain/offset) utilities.

**HARDWARE-ENGINEER**
1. 5-channel AFE board; then **ADS1299 front-end** (PGA + DRL, 24-bit).
2. Shielded leads; **medical isolation** (isolated DC-DC + digital isolator) before any human test (HG7).
3. Custom wearable PCB + battery.

**TEST-ENGINEER**
1. Build the unit-test suite (`tests/`) for DSP + protocol; wire a HIL sim harness.
2. Signal-quality report (ENOB/noise floor); bench validation with a signal generator; CI.

## 7. Milestones / competitive (beat Delsys & Noraxon)
On **software/analytics we're already close** (MVC, median-freq, onset, FFT, reports). Gaps are
**hardware**: channels, ADC quality, wireless, IMU, isolation. Full matrix:
`docs/EMG_SAW_Retro_and_Competitive_Roadmap.md`.

**Ladder:** M1 done (SAW+CP4+instrument) → **M2 5-ch** → **M3 analytics parity** (iEMG, mean-freq,
co-contraction) → **M4 ADS1299 24-bit** → **M5 wireless + IMU** → **M6 isolation + PCB** → M7 validation.
Our edge: **open + ~100× cheaper**.

## 8. Critical gotchas (locked — do NOT rediscover)
1. Clone ST-Link can't debug → never IDE Debug/Run; Build → `flash_run.bat`.
2. Board won't auto-start → `--kick` (ST-Link reset-run).
3. F103 ADC1 has **no TIM2 trigger** → **TIM3 TRGO**; no trigger-edge setting.
4. **USART1 global interrupt MUST be NVIC-enabled** or UART locks after 1 batch.
5. **Baud must match** (binary 921600, ASCII 115200).
6. Open serial with **DTR/RTS low** (`_open_serial`) so port-open can't reset the board.
7. Bare PA0 ≈ 187 mV mains **antenna pickup** (not a defect); real AFE = clean.

## 9. SAW workflow
- **6 agents** in `.claude/agents/` (systems-architect, firmware, gui, dsp, hardware, test).
- **graphify** = code-structure graph (`graphify-out/`); query it before raw reads.
- **agent_map.html** = agents-as-continents world map (run `scripts/agent_map.py`; refresh with `scripts/refresh.ps1`).
  Open it as a **dashboard with one-click launch buttons** (Ch1/Ch5 · sim/live): `python scripts/emg_map_server.py`.
- **QUALITY_BAR.md** hard gates; **PROJECT_CONTEXT.md** locked facts; **TOKEN_POLICY.md** read discipline.
- After any code change: `.\scripts\refresh.ps1` then commit (HG8).

## 10. Push to GitHub (for your coworker)
```powershell
# from emg-saw, with a repo created on GitHub:
git add -A
git commit -m "docs(saw): complete handoff, launcher, world-map, roadmap"
git branch -M main
git remote add origin https://github.com/<you>/emg-saw.git   # once
git push -u origin main
```
Coworker then: `git clone … ; cd emg-saw ; python -m venv venv ; .\venv\Scripts\activate ;
pip install -r requirements.txt ; python emgscope.py --sim --channels 5` — and reads this HANDOFF.

## 11. Doc index
`PROJECT_CONTEXT.md` (facts) · `QUALITY_BAR.md` (gates) · `docs/CHECKPOINTS.md` (bring-up) ·
`docs/EMG_SAW_Project_Plan.md` (epics) · `docs/EMG_SAW_Retro_and_Competitive_Roadmap.md` ·
`firmware/cp4_binary_dma.md` (firmware) · `AGENT_OWNERSHIP.yml` (who owns what).
