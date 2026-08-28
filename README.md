# EMG-SAW — Beihang EMG Acquisition System + GUI

An open, low-cost, **5-channel dry-electrode surface-EMG** acquisition system with a
real-time, research-grade GUI — a self-owned alternative to Noraxon MR / Delsys Trigno.
Built and run as a **SAFe Agentic Workflow (SAW)**: 6 specialist agents, a code
knowledge-graph, and an agent "world-map".

<p align="center"><img src="assets/logo.png" height="60" alt="Beihang University"></p>

## Quick start
```bash
python -m venv venv
# Windows:  .\venv\Scripts\activate      # macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt

# see the full UI with no hardware:
python emgscope.py --sim --channels 5

# real hardware (STM32 flashed with CP4 firmware, CP2102 on COMx):
python emgscope.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick
```

## What it does
Real-time multi-channel scope (sweep/scroll, DC/AC/GND coupling, V/div, Time/div) with
per-channel **RMS, pk-pk, median frequency (fatigue), activation meter**, **MVC % normalization**,
**onset highlight**, **live FFT spectrum**, event markers, snapshot, and one-click HTML reports.
Firmware: STM32F103 timer-paced ADC + DMA ping-pong streaming binary frames @ 2 kHz.

## Architecture
```
skin → dry electrodes → analog front-end → STM32 ADC (TIM+DMA) → binary/UART → PC GUI (PyQt5/pyqtgraph)
```

## Repo
- `emgscope.py` — launch the scope · `gui/` (MVC) · `dsp/` · `communication/` · `firmware/`
- `scripts/` — `flash_run.bat`, `refresh.ps1`, `agent_map.py` (world-map)
- **New here? Read [`HANDOFF.md`](HANDOFF.md) first** — complete context, run guide, and roadmap.
- Facts: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) · Gates: [`QUALITY_BAR.md`](QUALITY_BAR.md) ·
  Roadmap: [`docs/EMG_SAW_Retro_and_Competitive_Roadmap.md`](docs/EMG_SAW_Retro_and_Competitive_Roadmap.md)

## Status
CP1–CP4 complete (2 kHz binary pipeline, full instrument). Next: 5 channels, then ADS1299 24-bit
front-end, wireless, IMU. See `HANDOFF.md` §6–7.

_Owner: Muhammad Daniyal · MS Biomedical Engineering · Beihang University._
