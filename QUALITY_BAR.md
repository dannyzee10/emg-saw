# QUALITY_BAR.md

This is the hard gate file for the EMG Acquisition + GUI system.
All agents enforce these rules. Any change that violates a hard gate below must not advance.
Nothing is final without **Daniyal's explicit human approval**.

---

## Authority

This file takes precedence over agent defaults.
If an agent's instructions conflict with this file, this file wins.
**systems-architect** enforces compliance with this file; **test-engineer** produces the
evidence. Every gate report must cite file path, line, the measured value, and the source
artifact (test output, scope reading, graph query).

---

## Hard gate rules

### HG1 — Protocol integrity
- Binary frames must **round-trip byte-exact** between firmware `build_frame` and PC
  `protocol.py` (same CRC-16/CCITT-FALSE, same layout `AA 55 | seq | NCH×int16-LE | crc16-LE`).
- `FrameParser` must **survive a sustained noise / false-sync burst without crashing**
  (iterative resync, never recursive) and recover the next good frame.

FAIL if: a round-trip test mismatches, CRC differs firmware↔PC, or a `0xAA55` burst can raise
`RecursionError` / wedge the reader.

### HG2 — Firmware timing & delivery
- At the target rate (CP4 = 2 kHz), a sustained run shows **steady S/s** (within a few % of
  target), **drop ≈ 0** and **crc-err ≈ 0** in steady state.
- No "one batch then dead" stall (USART1 global interrupt MUST be NVIC-enabled;
  `HAL_UART_Transmit_DMA` must return the UART to READY).

FAIL if: drops accrue in steady state (bare-pin antenna touches excepted), the stream stalls,
or S/s is not paced by the hardware timer (jittery `HAL_Delay` sampling).

### HG3 — DSP correctness
- Every filter/metric has a **unit test against a known signal**: e.g. 100 Hz tone →
  median frequency ≈ 100 Hz; sine amplitude A → RMS ≈ A/√2; band-pass attenuation verified;
  notch removes 50/60 Hz.

FAIL if: any DSP metric is mathematically wrong, or ships without a passing unit test.

### HG4 — GUI robustness
- A **headless (`QT_QPA_PLATFORM=offscreen`) smoke test** must build the window, run the Qt
  event loop, and exercise the controls (mode, coupling, V/div, Time/div, autoscale, record,
  MVC, onset, spectrum, report) **without exception**.
- On live/sim data the per-channel readouts must be **non-zero** (no ring-buffer tail-index
  regression); DC coupling = true absolute volts, AC = centered on 0, GND = flat 0.

FAIL if: the offscreen test raises, readouts read 0 on non-zero data, or a coupling maps a
known constant to the wrong voltage.

### HG5 — Axes & display fidelity
- V/div and Time/div ticks reach the plot **edges** (no bare margin); Y grid includes below 0;
  sweep write-head wraps at the right edge; time axis is accurate when fs matches the hardware.

FAIL if: the grid/labels do not reach the graticule edges, or the displayed time base is wrong.

### HG6 — Signal quality baseline
- The ADC noise floor with a **low-impedance / mid-scale** input must be documented and within
  spec (Blue Pill internal ADC ≈ 9–10 ENOB; ADS1299 upgrade path noted).
- A bare/floating pin picking up ~50 Hz mains is **expected pickup**, not a defect.

FAIL if: a real low-impedance source shows excessive noise, or pickup is misdiagnosed as an
ADC/firmware fault.

### HG7 — Human-safety
- Any measurement on a **human subject** must use an **isolated / battery** supply (IEC 60601
  intent); never a mains-referenced, non-isolated connection to a person.

FAIL if: human testing is proposed/run on a mains-powered, non-isolated setup.

### HG8 — Single source of truth + fresh graph
- The code the agents/graph analyze must **equal the code that runs**. `graphify-out/` must be
  built from the current `HEAD` (`graphify update .` after edits).

FAIL if: `emg-saw` code diverges from the canonical runtime, or the graph is stale vs `HEAD`.

### HG9 — Checkpoint discipline
- No checkpoint advances until its **PASS criterion is met and logged** in
  `docs/CHECKPOINTS.md` with evidence (scope reading / test output). Gates run in order:
  protocol → firmware → DSP → GUI → integration.

FAIL if: a checkpoint is skipped or marked PASS without logged evidence.

### HG10 — No "done" without Daniyal approval
Nothing may be marked final, validated, shippable, or complete without Daniyal's explicit
human approval — including individual checkpoint passes and any agent saying "it works."

FAIL if: any agent marks work final without this approval.

---

## Supporting rules (a pattern of violations becomes blocking)

- **S1 — Facts match `PROJECT_CONTEXT.md`.** All hardware/protocol/state claims must match it.
- **S2 — Respect the locked gotchas** (see `PROJECT_CONTEXT.md` §Gotchas): F103 uses **TIM3**
  (not TIM2, no edge setting); **USART1 IRQ** enabled; **baud must match**; open the port with
  **DTR/RTS low**; the board needs an explicit **`--kick`** (no auto-start); never the IDE
  Debug/Run buttons — use `flash_run.bat`.
- **S3 — Terseness.** Narration is short; evidence fields (path, line, measured value, source
  artifact, verdict) are never shortened.

---

## Gate reference

| Gate | Hard gates enforced |
|------|---------------------|
| test-engineer | HG1, HG3, HG4, HG5 (produces the evidence) |
| firmware-engineer | HG2, HG7 |
| dsp-engineer | HG3 |
| gui-engineer | HG4, HG5 |
| hardware-engineer | HG6, HG7 |
| systems-architect | HG8, HG9, HG10 + enforces all of the above |
