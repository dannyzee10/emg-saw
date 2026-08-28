# EMG SAW — Retrospective + Competitive Roadmap

Two questions answered here: (1) what each agent-continent shipped so far, and
(2) what remains to **match and beat Delsys (Trigno/EMGworks) and Noraxon (Ultium/MR)**.
Facts are locked in `PROJECT_CONTEXT.md`; gates in `QUALITY_BAR.md`.

---

## Part 1 — What each agent shipped (retro of the build)

| Continent (agent) | Shipped ✅ | Evidence |
|---|---|---|
| **SYSTEMS ARCHITECT** | Pipeline + protocol contract defined; CP1–CP6 checkpoint discipline; SAW workspace, agents, QUALITY_BAR, PROJECT_CONTEXT, world-map | `CHECKPOINTS.md`, `PROJECT_CONTEXT.md`, `agent_map.html` |
| **FIRMWARE ENGINEER** | CP1 blink → CP2 UART → CP3 ADC/ASCII → **CP4 TIM3 + ADC circular-DMA (HT/TC ping-pong) → binary @ 2 kHz**, ~2010 S/s, 0 crc-err. Solved TIM3-not-TIM2, USART1-IRQ, baud, DTR, no-auto-start | `firmware/cp4_binary_dma.md`, `firmware/emg_bluepill/main.c` |
| **GUI ENGINEER** | Full branded instrument: sweep/scroll, DC/AC/GND coupling, V/div, Time/div, framed graticule, per-channel panel, markers, snapshot, HTML report, CSV | `gui/emg_plotter.py` (948 lines) |
| **DSP ENGINEER** | Band-pass 20–450, notch 50/60, RMS envelope, **median frequency (fatigue)**, **MVC %**, **live FFT spectrum**, onset highlight — all validated (100 Hz tone → 100 Hz) | `dsp/dsp.py`, `gui/emg_plotter.py` |
| **HARDWARE ENGINEER** | Discrete AFE (buffers + driven guard / INA double-diff); dry-electrode failure diagnosis; noise = antenna pickup confirmed (shorted PA0 ≈ 0) | design notes; `PROJECT_CONTEXT.md` §Signal facts |
| **TEST ENGINEER** | Headless GUI smoke tests, protocol round-trip + **noise-resync/recursion** fix, binary 5-ch parse verified, independent code review | test runs in session log |

---

## Part 2 — Remaining goals per agent (near-term)

- **SYSTEMS ARCHITECT:** wire the freshness hook everywhere; keep `emg-saw` the single source of truth; sequence the epics below; own the ADS1299 decision.
- **FIRMWARE ENGINEER:** **CP6 — 5 channels** (scan + PA0–PA4, `NCH=5`); then SPI driver for **ADS1299**; timestamp/seq robustness; optional USB-CDC.
- **GUI ENGINEER:** 5-lane view polish; MVC session workflow; per-channel calibration UI; session/trial manager; replay/review; `.exe` packaging (PyInstaller).
- **DSP ENGINEER:** iEMG (integrated EMG), mean frequency, co-contraction index, onset/offset detection with thresholds, fatigue trend over a trial, band-power ratios.
- **HARDWARE ENGINEER:** 5-channel AFE board; **ADS1299 front-end** (24-bit, PGA, DRL); shielded leads; **medical isolation** (isolated DC-DC + digital isolator) for human use; custom PCB + battery.
- **TEST ENGINEER:** unit-test suite for every filter/metric; HIL sim harness; bench validation with a signal generator; signal-quality (ENOB/noise) report; CI.

---

## Part 3 — Where we stand vs Delsys & Noraxon

| Capability | **Ours (now)** | **Delsys Trigno / EMGworks** | **Noraxon Ultium / MR** |
|---|---|---|---|
| Channels | 1 (5 planned) | up to 16 EMG | up to 16–32 EMG |
| ADC resolution / noise | 12-bit internal, ~9–10 ENOB | 16-bit, sub-µV noise | 16-bit, low noise |
| Sample rate | 2 kHz | up to ~4.3 kHz | up to ~4 kHz |
| Front-end | discrete AFE + MCU ADC | integrated, high CMRR | integrated, high CMRR |
| Connectivity | **wired USB** | **wireless** (RF) | **wireless** |
| IMU / motion | none | accel/gyro/mag per sensor | IMU + 3D motion/force sync |
| Isolation / safety | none yet | medical-grade | medical-grade (FDA/CE) |
| Real-time display | ✅ scope + sweep | ✅ | ✅ (MR) |
| RMS / envelope | ✅ | ✅ | ✅ |
| **MVC normalization** | ✅ | ✅ | ✅ |
| **Median/mean freq (fatigue)** | ✅ median+mean | ✅ | ✅ |
| **Onset detection** | ✅ highlight | ✅ | ✅ |
| **Live FFT spectrum** | ✅ | ✅ | ✅ |
| Report generation | ✅ HTML | ✅ | ✅ |
| Co-contraction / iEMG | ✅ | ✅ | ✅ |
| Session/trial DB + replay | ❌ | ✅ | ✅ |
| Export EDF/C3D | CSV only | ✅ | ✅ |
| Video / force / mocap sync | ❌ | ✅ | ✅ |
| Cost | ~$5 MCU + parts | \$\$\$\$ | \$\$\$\$ |

**Honest read:** on **software/analytics** we're already surprisingly close (MVC, median-freq,
onset, spectrum, report — the clinical staples). The real gaps are **hardware**: channel count,
**ADC quality (ADS1299)**, **wireless**, **IMU**, and **medical isolation**.

---

## Part 4 — The "win" roadmap (prioritized)

**Tier 1 — close the credibility gap (biggest wins per effort):**
1. **CP6: 5 channels** (firmware NCH=5, GUI 5-lane) — *firmware, gui*.
2. **ADS1299 front-end** — 24-bit, integrated PGA + DRL, 8-ch chainable to 16. This single upgrade
   erases the ENOB/noise gap and the channel gap at once — *hardware, firmware*.
3. **Analytics parity:** iEMG, mean freq, co-contraction, onset/offset timing, fatigue trend — *dsp, gui*.

**Tier 2 — reach feature parity:**
4. **Wireless** (ESP32/BLE or a wireless MCU) — the headline Delsys/Noraxon feature — *firmware, hardware*.
5. **IMU per channel** (accel/gyro) for movement context — *hardware, firmware, dsp*.
6. **Session manager + replay + EDF/C3D export** — *gui*.
7. **Medical isolation + custom wearable PCB + battery** (IEC 60601 intent) — *hardware*.

**Tier 3 — differentiate / "win":**
8. **Open + ~1–2 orders of magnitude cheaper** than Delsys/Noraxon — our structural advantage.
9. On-device / real-time **fatigue & activation analytics**, scriptable pipeline, open data formats.
10. Optional: video/force sync, gait-cycle segmentation, cloud session store.

**Milestone ladder:** M1 done (SAW + CP4 + instrument) → **M2: 5-ch** → **M3: analytics parity** →
**M4: ADS1299 24-bit** → **M5: wireless + IMU** → **M6: isolation + PCB + packaging** → M7: validation study.

---

## Part 5 — Electrode lead-off / integrity plan

Each recording channel is a **double-differential montage of 3 electrodes** (E1,E2,E3) →
buffers → DD network → AD8237 → **one** ADC pin. Every electrode node has a **22 MΩ→VREF**
bias resistor; a **combined DRL** (all nodes averaged → buffer → **1 MΩ safety** → body,
≈3.3 µA worst case, IEC-60601-safe) drives the common mode. Because the DD collapses 3
electrodes into 1 ADC channel, **per-electrode status must come from the buffered node
signals**, not the montage output.

**Detection basis (with the DRL running):** a *connected* node has its mains actively
cancelled (low 50/60 Hz); a *disconnected* node floats to VREF via 22 MΩ and picks up mains
as an antenna + DC-drifts. So **mains-ratio + DC-drift** are the cues (`dsp.leadoff_report`).
Passive limit: an open node can sit quietly at VREF (false "good"); truly definitive
open-detection needs a switched pull-probe or current injection (→ ADS1299).

### Now — Blue Pill, Channel 1, 3 electrodes (no mux, reuses existing software)
- Wire channel-1 buffers **BUF1/BUF2/BUF3 (E1/E2/E3) → 3 ADC pins** (e.g. PA0/PA1/PA2).
- Firmware: `#define NCH 3`, ranks = those pins; stream the 3 nodes.
- PC: `python emgscope.py --port COM8 --baud 921600 --channels 3 --fs 2000 --coupling DC --kick`
  → the existing per-channel lead-off dots **are** E1/E2/E3 (rename the 3 channels). Reuses
  `LeadoffTracker` (hysteresis + quality) unchanged.
- Optional firmware enhancement: brief **GPIO pull-probe** at each node for a definitive open test.

### Next STM32 upgrade — all 15 electrodes (deferred; needs more/faster ADC)
The Blue Pill runs out of pins (5 DD + 15 nodes = 20 > ~10 ADC). On a bigger STM32
(F303 / G4 / F4) or via a **16:1 analog mux** (15 buffered nodes → 1 ADC pin + 4 GPIO select):
- Firmware **"check mode"** (paused): scan 15 nodes → per-electrode status; recording still
  uses the 5 DD outputs.
- Protocol: low-rate **status word** = 15 electrode bits + 1 reference bit (designed to match
  the ADS1299 LOFF layout, so the swap is drop-in).
- GUI: **3 sub-dots per channel card** (E1/E2/E3) → 15 total.

### Ultimate — ADS1299 (M4)
Built-in lead-off: **6 nA AC injection**, per-channel `LOFF_STATP/N` status, true kΩ,
medical-grade. Drop-in replaces the heuristic *source*; the GUI dots + status word stay identical.
