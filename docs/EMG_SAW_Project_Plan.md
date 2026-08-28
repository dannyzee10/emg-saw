# EMG-SAW — Project Plan (consolidated, current)

Owner: **Muhammad Daniyal**, MS Biomedical Engineering, Beihang University.
Goal: an open, ~100× cheaper, agentic-workflow-built alternative to **Noraxon MR / Delsys Trigno**.
Single source of truth for *what we do next*. Milestone ladder aligns with
`EMG_SAW_Retro_and_Competitive_Roadmap.md`; hard gates in `QUALITY_BAR.md`.

---

## Where we are (2026-08-28)
- **CP1–CP4 done** — TIM3 + ADC circular-DMA (HT/TC ping-pong) → 2 kHz binary, ~2010 S/s, 0 crc-err.
- **Branded MVC instrument** — sweep/scroll, DC/AC/GND, V/div, Time/div, per-channel RMS/pk-pk/median-freq/activation, MVC %, onset, live FFT, HTML report, CSV.
- **CP6 (5 channels)** — firmware + tests committed *in software* (`0b8504f`); needs flash + live verify.
- **Phase A electrode lead-off** — PC-side detector + hysteresis + 0–100 quality + DC-drift (`50ec3d9`, `f3d07a5`). Channel-1/3-electrode works today via `--channels 3`.
- **Infra** — 6-agent SAW, code world-map, graphify-first routing, **13 tests green**, pushed to `github.com/dannyzee10/emg-saw`.

## Milestone ladder
| M | What | State |
|---|------|-------|
| **M1** | SAW + CP4 + instrument | ✅ done |
| **M2** | 5 channels (CP6) | ⏳ software done → flash + verify |
| **M3** | analytics parity (iEMG, mean-freq, co-contraction, onset/offset, fatigue trend) | next |
| **M4** | ADS1299 24-bit (SPI, PGA, DRL, **LOFF** lead-off, true kΩ) | later |
| **M5** | wireless (BLE) + IMU per channel | later |
| **M6** | medical isolation + custom PCB + battery + `.exe` | later |
| **M7** | validation study (noise table, func-gen NMSE/PCC/THD) → the paper | later |

---

## NOW (this iteration)
1. **Finish CP6 (M2).** Daniyal: CubeIDE `.ioc` ADC Scan + `NCH=5` + ranks PA0–PA4 → `flash_run.bat`; verify 5 live lanes, S/s≈2010, drop≈0, crc≈0 (**HG2**). → log CP6 PASS (HG9) → **approve (HG10)**.
2. **Channel-1 per-electrode lead-off.** Daniyal: wire BUF1/2/3 (E1/E2/E3) → 3 ADC pins, `NCH=3`, `--channels 3`. Reuses `LeadoffTracker`. *(optional: GPIO pull-probe for a definitive open test.)*
3. **Push + freshen graph.** `scripts\refresh.ps1` (HG8) → `git push`.

## NEXT
4. **M3 analytics parity** — *biggest software gap vs Delsys/Noraxon.* dsp: **iEMG, mean frequency, co-contraction index, onset/offset timing (thresholds), fatigue trend**; gui: display them; test: unit tests on known signals (HG3).
5. **Session / trial manager + replay + EDF/C3D export** — gui.
6. **15-electrode lead-off** (with a bigger STM32) — 16:1 mux + firmware "check mode" + 3 sub-dots/channel + low-rate status word (matches ADS1299 LOFF layout).

## LATER
7. **M4 ADS1299** — hardware + firmware: SPI 24-bit, PGA, DRL, LOFF; PC protocol kept backward-compatible; lead-off dots swap to the LOFF source (drop-in). Erases the ENOB + channel gap at once.
8. **M5 wireless + IMU** — ESP32/BLE or wireless MCU; per-channel accel/gyro for movement context.
9. **M6 isolation + PCB + battery + packaging** — isolated DC-DC + digital isolator (IEC 60601 intent, **HG7**); custom wearable PCB; PyInstaller `.exe`.
10. **M7 validation** — bench: input-referred noise per channel/gain/fs; function-generator sine sweep scored by NMSE% + Pearson + THD; complex-signal time+freq (Luiz 2025 template) → publishable methods paper.

---

## Ownership (route graphify-first per `AGENT_OWNERSHIP.yml`)
- **firmware-engineer** — CP6, ADC/mux/pull-probe, ADS1299 SPI, wireless MCU, wire protocol
- **gui-engineer** — 5-lane polish, per-electrode sub-dots, analytics display, session manager, `.exe`
- **dsp-engineer** — lead-off, M3 analytics, per-channel calibration, validation metrics
- **hardware-engineer** — AFE, mux, ADS1299 board, DRL, isolation, PCB/battery
- **test-engineer** — HG1/HG3/HG4 evidence, HIL harness, bench validation
- **systems-architect** — gates, protocol/status-word design, checkpoint + graph freshness, sequencing

## Split of work
- **Me (main-brain, software):** PC code, firmware *reference*, tests, docs — built, gated, committed.
- **Daniyal (hardware):** flashing, wiring, live verification, **HG10 approval**, `git push` (proxy).

## Gates
Every change passes **HG1–HG10** (`QUALITY_BAR.md`); nothing is "done" without Daniyal (HG10);
graph rebuilt after edits (HG8); checkpoints logged with evidence (HG9).
