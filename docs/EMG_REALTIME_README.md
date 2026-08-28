# EMG Oscilloscope

Real-time EMG acquisition + **oscilloscope/MR4-style display** + recording for an
STM32-based sensor — the pipeline a research system (Noraxon MR4, Delsys) uses under
the hood, in a form you own and can extend.

```
[EMG AFE] → [STM32: TIM→ADC→DMA] → [framed binary (or csv) over UART/CP2102]
         → [PC: reader thread → ring buffer → pyqtgraph scope + scipy DSP → CSV]
```

## Install
```
pip install -r requirements.txt
```

## Run

**Try the full UI now, no hardware:**
```
python emg_plotter.py --sim --channels 1
python emg_plotter.py --sim --channels 5      # preview the 5-channel MR4-style layout
```

**Real board — CP3 ASCII bring-up (single channel, 115200):**
```
python emg_plotter.py --port COM8 --baud 115200 --ascii --channels 1 --fs 500 --kick
```

**Real board — CP4 binary/DMA (recommended, 2 kHz, 921600):**
```
python emg_plotter.py --port COM8 --baud 921600 --channels 1 --fs 2000 --kick
python emg_plotter.py --port COM8 --baud 921600 --channels 5 --fs 2000 --kick   # 5-ch
```

Find your port: `python -m serial.tools.list_ports -v`.

> **This hardware (clone ST-LINK + Blue Pill):** never use the CubeIDE Debug/Run
> buttons — the clone probe can't hold a debug session. Build in CubeIDE (Ctrl+B),
> then **double-click `flash_run.bat`** to flash+run. `--kick` revives the board via
> the ST-LINK before opening the port (the board doesn't auto-start). Baud **must
> match** the firmware. See `CHECKPOINTS.md` for the full story.

## Oscilloscope controls (top bar)
- **Mode: Sweep / Scroll** — *Sweep* = hospital-monitor / MR4 style: fixed screen, a
  write-head sweeps left→right painting new data, old data wraps at the edge. *Scroll* =
  strip-chart slide.
- **Coupling: DC / AC / GND** — *DC* = true absolute voltage (GND=0 V, 3.3 V=3.3 V line);
  *AC* = DC blocked, centered on 0 (EMG view); *GND* = 0 baseline.
- **V/div** — vertical scale (5 mV … 2 V per division, 8 divisions).
- **Time/div** — sweep speed (10 ms … 2 s per division, 10 divisions).
- **Vpos** — vertical position; **Autoset** — auto-fit the trace.
- **Auto V/ch** — auto-scale each channel's lane to its own signal (MR4 style); each lane
  shows a live **RMS + pk-pk** readout in its title.
- **Probe x** — set 2.0 with a ÷2 divider to read a 5 V rail (ADC only reads 0–3.3 V; PA0
  is not 5 V tolerant — divider required).
- **Notch 50/60**, **RMS env**, **Pause**, **Record** (raw codes + timestamps to CSV).

## Files
| file | role |
|------|------|
| `emg_plotter.py` | oscilloscope GUI: sweep/scroll, coupling, V/div, T/div, per-ch autoscale+RMS, record |
| `protocol.py`    | binary frame format + streaming parser (matches firmware) |
| `sources.py`     | `SerialSource` (binary), `AsciiSource` (csv), `SimSource` (threaded) |
| `dsp.py`         | notch / band-pass / RMS-envelope (scipy) |
| `flash_run.bat`  | flash + reset-run the firmware via ST-LINK (replaces the IDE Run button) |
| `firmware/cp4_binary_dma.md` | CP4: TIM+ADC-DMA+binary frame builder (C) for 1→5 ch |
| `firmware/bluepill_f103_config.md` | exact Blue Pill clock/ADC/timer settings |
| `firmware/clock_tree_explained.md` | how to configure any STM32 clock tree |
| `CHECKPOINTS.md` | bring-up log CP1–CP6 + the hardware gotchas |

## Matching PC ↔ STM32
`--channels` **must equal** `NCH` in the firmware; `--fs / --vref / --bits / --baud`
must match the firmware. The CRC in `protocol.py` and `firmware/cp4_binary_dma.md`
is the same algorithm (CRC-16/CCITT-FALSE) — verified by round-trip tests.

## Scaling to 5 channels
Channel-count agnostic end to end: set `NCH=5` in firmware (5 ADC ranks, PA0–PA4) and
run `--channels 5`. One STM32 samples all 5 in a single DMA scan, so channels stay
time-aligned — needed for the double-differential montage. Turn on **Auto V/ch** for the
MR4-style per-lane view.
