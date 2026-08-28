# Tomorrow — Live PA0 EMG data check (CP5 "signal sanity")

**Goal:** get live real-time EMG from **PA0** (gel electrode → AD8237 → STM32 → CP2102 → scope)
and evaluate *how good the data is*, using the tools we built (lead-off dots, RMS, median/mean
frequency, live FFT, onset, coupling, report). This is checkpoint **CP5**.

Prereqs: STM32 Blue Pill + ST-Link (SWD) + **CP2102 on COM8** (PA9→RXD, GND↔GND); gel electrode on
a muscle (e.g. biceps) → AD8237 → PA0; **DRL electrode on the body** (bony spot, e.g. elbow); venv active.

---

## 0. Pre-flight (2 min)
- Confirm the port: `python -m serial.tools.list_ports -v` (expect CP2102 = COM8).
- For a **clean single-channel** check use firmware **`NCH=1`** (PA0). Build in CubeIDE → `scripts\flash_run.bat`.
  *(If the board still has the old 1-ch CP4 build, skip. If it has the 5-ch build, run `--channels 5` and just read Ch1 — Ch2–5 will be floating noise.)*

## 1. Stream
```
python emgscope.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick
```
Expect: live trace, **S/s ≈ 2010, drop 0, crc 0**. If not → see Troubleshooting.

## 2. Resting baseline / noise (muscle relaxed)
- AC coupling, turn **Spectrum ON**.
- Read **RMS (µV)**, **pk-pk**, and the **FFT**. With the DRL working, baseline should be low and
  **50 Hz suppressed**. Toggle **Notch 50** on/off to see the mains component.
- **Lead-off dot** should be 🟢 green; pull the electrode → 🟡/🔴 (confirms it tracks contact).
- *Record:* resting RMS + the 50 Hz level.

## 3. DC / scale sanity (CP5)
- Switch to **DC coupling**: the trace should sit at the AFE bias (~**VREF/2 ≈ 1.65 V**).
- (Optional, AFE disconnected) short PA0→GND → flat 0 V; →3.3 V → flat 3.3 V (proves absolute
  scale + the "open" lead-off). Reconnect the AFE after.

## 4. Contraction / activation — the real test
- AC coupling, **RMS env ON**, **Auto V/ch ON**, **Onset ON**.
- Contract the muscle → expect clear **EMG bursts** (RMS rises, activation bar fills, onset shading marks it).
- Note **median / mean frequency** during contraction (physiological sEMG median ≈ 60–120 Hz).
- Do **2–3 repeated** contractions → check the bursts are obvious and repeatable.

## 5. Fatigue (optional)
- Hold a **sustained contraction ~30–60 s** → median/mean freq should **decline** and the live
  **`fat(1) %`** go negative (spectral compression = fatigue).

## 6. Capture the data
- Fill **Subject / Trial / Notes**. **Record** → CSV. Press **M** at each contraction (markers).
- **Report** → HTML (now includes RMS, median+mean Hz, **iEMG**, **onsets**, **fatigue**).
- Keep the CSV + HTML for review.

## What "good data" looks like (CP5 PASS)
- Resting: low RMS, mains suppressed (DRL), lead-off 🟢.
- DC lines land at the right voltage.
- Contraction: obvious, repeatable bursts; median freq in range; onset marks activation.
- If noisy: check DRL contact, enable Notch 50, improve gel/skin prep, shield the leads.

## Troubleshooting (locked gotchas)
| Symptom | Cause / fix |
|---|---|
| no stream / one batch then dead | USART1 global IRQ not enabled (gotcha #4) |
| board silent after connect | didn't auto-start → `--kick` |
| garbage / 0 frames parsed | baud mismatch (binary = **921600**) |
| huge 50 Hz everywhere | DRL not contacting / electrode floating (lead-off amber) |
| trace jumps on port open | DTR/RTS reset — already handled by `_open_serial` |

## After the session
Log the CP5 result in `docs/CHECKPOINTS.md`: resting noise (µV), contraction RMS, median freq,
mains level → decide **CP5 PASS** + the top improvement (shielding / gain / notch). Then we proceed
to **CP6 (5 channels)** and, in parallel, wire **channel-1 per-electrode lead-off** (3 buffer nodes).

*(Everything the scope needs is already built and tested — this session is about your hardware +
reading the numbers, not new code.)*
