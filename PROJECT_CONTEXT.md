# PROJECT_CONTEXT.md

Authoritative reference for all **locked facts** about the EMG Acquisition + GUI system.
All agents must read this before any design, code, or checkpoint decision.
Agents must not accept claims that contradict this file. `QUALITY_BAR.md` gates against it.

---

## Project identity
- System: **5-channel dry-electrode surface-EMG (sEMG) acquisition + real-time GUI**
- Owner: **Muhammad Daniyal**, MS Biomedical Engineering, **Beihang University**
- Stack: **Python + PyQt5 + pyqtgraph + pyserial + numpy/scipy** (GUI/DSP); **STM32 HAL/C** (firmware)
- Goal: a self-owned Noraxon-MR / Delsys-class research instrument
- Canonical code home: **`emg-saw/`** (this repo). Legacy runtime mirror: `Desktop\emg-realtime`
  (must be kept in sync or retired — see §Source of truth).

## Architecture (locked pipeline)
```
skin → dry electrodes → analog front-end (AFE: buffers + driven guard / INA double-diff, VREF-biased)
     → STM32 internal 12-bit ADC (timer-paced, DMA) → framed binary over UART/CP2102
     → PC GUI (pyqtgraph scope + DSP + analytics + report)
```

## Locked hardware facts
| Item | Value |
|---|---|
| MCU | STM32F103C8T6 "Blue Pill", Cortex-M3 @ **72 MHz**, 12-bit ADC (≤14 MHz → prescaler **/6 = 12 MHz**), 20 KB RAM |
| Sample-rate timer | **TIM3** TRGO, PSC=71 / ARR=499 → **2000 Hz** (F103 ADC1 has NO TIM2 trigger; no edge setting) |
| ADC input(s) | **PA0** (IN0) now; **PA0–PA4** for 5 ch |
| UART | USART1, **PA9 TX** → CP2102 RXD, GND↔GND; **921600** baud (binary), 115200 (ASCII bring-up) |
| USB-UART | **CP2102** ("USB TO TTL"), enumerates as **COM8** (3.3 V logic, no jumper) |
| Programmer | **clone ST-Link** (fw V2J45S7), SWD PA13/PA14 — **flash only, cannot debug** |
| ADC reference | VDDA = 3.3 V (noisy) → internal ADC ≈ **9–10 ENOB**; upgrade path = **ADS1299** (24-bit, PGA, DRL, SPI) |

## Locked wire protocol
- Frame: `AA 55 | seq(u8) | NCH×int16-LE | crc16-LE`  (len = 5 + 2·NCH)
- CRC: **CRC-16/CCITT-FALSE** (poly 0x1021, init 0xFFFF) — byte-identical in firmware `crc16_ccitt`
  and PC `communication/protocol.py` (round-trip verified).
- Firmware emits **BLOCK=10-frame batches** from a **circular-DMA HT/TC ping-pong** (buffer A/B).

## Current state — DONE ✅ (as of 2026-08-26)
| CP | What | Status / evidence |
|----|------|-------------------|
| CP1 | blink / toolchain / ST-Link flash / 72 MHz | PASS |
| CP2 | USART1 → CP2102 → PC "hello" | PASS |
| CP3 | 1× ADC → ASCII → live scope tracks PA0 | PASS |
| CP4 | **TIM3 → ADC-DMA ping-pong → binary @ 2 kHz** | **PASS — ~2010 S/s, 0 crc-err, continuous** |
| CP5 | signal sanity (DC lines, AC baseline, tone) | partial — noise = antenna (confirmed: shorted PA0→GND ≈ 0) |
| CP6 | **5 channels + real gel AFE** | ⏭ NEXT |

**GUI = full branded research instrument** (`gui/emg_plotter.py`, headless-tested):
Beihang-branded header (logo), session bar (subject/trial/notes), oscilloscope core
(Sweep/Scroll, DC/AC/GND coupling, V/div, Time/div, Vpos, Autoset, Probe, framed graticule),
per-channel panel (editable muscle name, RMS, pk-pk, **median frequency**, activation meter),
**MVC % normalization**, **onset highlight**, **live FFT spectrum**, markers (key M), snapshot,
one-click **HTML report**, metadata-rich CSV recording, Notch 50/60, RMS envelope, Auto V/ch.

## Locked gotchas (each cost hours — do NOT rediscover)
1. **Clone ST-Link can't hold a debug session** → never use CubeIDE Debug/Run buttons; Build (Ctrl+B) → **`flash_run.bat`**.
2. **Board does not auto-start** after reset/power/sleep → kick it: `STM32_Programmer_CLI -c port=SWD mode=UR -rst -run` (GUI `--kick`).
3. **F103 ADC1 has no TIM2 trigger** → **TIM3 TRGO**; F103 has **no trigger-edge** setting.
4. **USART1 global interrupt MUST be NVIC-enabled** or `HAL_UART_Transmit_DMA` locks BUSY after the first 10-frame batch (one burst then dead).
5. **Baud must match** firmware (binary 921600, ASCII 115200). Wrong baud = bytes arrive, 0 frames parse.
6. Open the serial port with **DTR/RTS low** (`_open_serial`) so port-open can't reset the board.
7. Bare/floating **PA0** ≈ 187 mV of 50 Hz **antenna pickup** (not a defect); low-Z AFE = clean.

## Signal facts
- Shorted PA0→GND → ≈ 0 pk-pk (rail-clipped); mid-scale short shows the true few-mV floor.
- Floating pin pickup dominated by mains; **Notch 50/60** removes most.

## Roadmap
- **CP6 (next):** 5 channels — firmware `#define NCH 5`, ADC **Scan Enabled** + ranks PA0–PA4, `--channels 5`.
- Real **gel AFE → PA0** validation; double-differential montage across 5 ch.
- Signal quality: oversample/average, VDDA filtering, shielded leads, per-channel calibration.
- **ADS1299** front-end (SPI, 24-bit, PGA, DRL) — biggest signal-quality milestone.
- Product: USB-CDC option (1.5 kΩ pull-up), custom PCB, battery/isolation, port auto-detect, session DB, replay/review.
- **Agent world-map** enabler: `AGENT_OWNERSHIP.yml` + `scripts/agent_map.py` → zoomable code-by-agent graph over graphify.

## Source of truth
- **Canonical = `emg-saw/`** (git). `gui/`, `dsp/`, `communication/` hold the live PC code;
  `firmware/` holds the STM32 config + the imported `main.c`.
- Legacy `Desktop\emg-realtime` is a runtime mirror — either sync into `emg-saw` on every change
  or retire it. **Two out-of-sync copies is a HG8 FAIL.**
- Detailed narrative: `docs/CHECKPOINTS.md`; firmware steps: `firmware/cp4_binary_dma.md`;
  GUI usage: `docs/EMG_REALTIME_README.md`; structure: `graphify-out/` (keep fresh).
