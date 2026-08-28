# EMG bring-up — checkpoint log (Blue Pill STM32F103C8T6)

Work top to bottom. Do **not** move to the next checkpoint until the current one's
**PASS** is true. After each pass, fill in Result/Date so we have a record. If a step
fails, stop there — that's where the bug is, and it's far easier to fix in isolation.

Legend: `[ ]` todo · `[x]` done · `[!]` stuck

---

## CP1 — Blink (proves toolchain + ST-Link flash + 72 MHz clock)
- **Connect:** ST-Link only → SWD header (SWDIO=PA13, SWCLK=PA14, 3V3, GND). No FTDI yet.
- **Open:** STM32CubeIDE. New STM32 Project → part **STM32F103C8T6** → name `emg_bluepill`.
- **Config (.ioc):** SYS ▸ Debug = **Serial Wire**. RCC ▸ HSE = **Crystal/Ceramic Resonator**.
  Clock tab: HSE 8 MHz → PLL ×9 → **SYSCLK 72 MHz** (APB1 36, APB2 72). Pin **PC13 = GPIO_Output**.
- **Code** (in `while(1)`, between USER CODE BEGIN/END 3):
  ```c
  HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
  HAL_Delay(500);
  ```
- **Flash:** Run ▸ Debug (or the green ▶). Choose ST-Link/SWD.
- **PASS when:** onboard LED (PC13) blinks ~1 Hz.
- Result: **PASS — LED blinks, flashed via ST-Link/SWD**  Date: 2026-08-20

## CP2 — "hello" over USART1 → FTDI → PC (proves the data path)
- **Connect FTDI:** FTDI **RXI ← PA9**, FTDI **GND ↔ GND**. Leave FTDI 5V/VCC **unplugged**
  (ST-Link powers the board). FTDI logic jumper = **3.3 V**. BOOT0 = **0**.
- **Config:** add **USART1** = Asynchronous (PA9 TX, PA10 RX), **115200** 8-N-1 (simple for now).
- **Code** (in `while(1)`):
  ```c
  char msg[] = "hello\r\n";
  HAL_UART_Transmit(&huart1, (uint8_t*)msg, 7, 100);
  HAL_Delay(500);
  ```
- **Test:** find the FTDI COM port (`python -m serial.tools.list_ports -v`), open it at 115200
  in any terminal (or `python -c "import serial;s=serial.Serial('COMx',115200);print(s.readline())"`).
- **PASS when:** you see `hello` repeating on the PC.
- Result: **PASS — `hello` ×10 read on COM8 @115200 (CP2102 module)**  Date: 2026-08-20

## CP3 — one ADC channel, ASCII, into the live plotter (proves ADC + end-to-end UI)
- **Connect:** put a test voltage on **PA0** — a potentiometer (3V3–wiper–GND), or just
  jump PA0 to 3V3 / GND to see min/max. (AFE output can come later.)
- **Config:** ADC1 ▸ IN0 (PA0), 12-bit, Rank 1, sampling 55.5 cyc. Software trigger, polling.
- **Code** (in `while(1)`):
  ```c
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  char b[16]; int n = snprintf(b, sizeof b, "%u\n", v);
  HAL_UART_Transmit(&huart1, (uint8_t*)b, n, 100);
  HAL_Delay(2);                 // ~ a few hundred Hz, rough timing is fine here
  ```
- **Run:** `python emg_plotter.py --port COM8 --baud 115200 --ascii --channels 1 --fs 500 --vref 3.3 --bits 12 --no-bandpass --kick`
- **PASS when:** turning the pot moves the trace up/down; 3V3≈full-scale, GND≈bottom.
- Result: **PASS — trace tracks PA0 (3V3=up, GND=down), ~330 S/s live**  Date: 2026-08-20
- **Hard-won lessons on THIS hardware (read before CP4):**
  1. Clone ST-LINK (V2J45S7) **cannot hold a live debug session** (GDB server = "target
     not responding"; OpenOCD = "CTRL/STAT" fail). **Never press the IDE Debug/Run buttons.**
     Build in CubeIDE (Ctrl+B), then flash+run via **`flash_run.bat`** (STM32_Programmer_CLI).
  2. Board **does not auto-start** its app after reset/power-up — it must be kicked with
     `STM32_Programmer_CLI -c port=SWD mode=UR -rst -run`; the scope does this via `--kick`.
  3. **Baud must match the firmware** (USART = 115200): pass `--baud 115200` (now the default).
     Wrong baud = bytes arrive but 0 frames parse (garbage). This cost us hours.
  4. Only one program can hold COM8; close PuTTY/other scopes first.

## CP4 — timer + DMA + binary framed @ 2000 Hz (the real, jitter-free pipeline)
- **Full step-by-step (config + exact C code): `firmware/cp4_binary_dma.md`.**
- Summary: TIM3 (2000 Hz, TRGO — F103 ADC1 has no TIM2 trigger) triggers ADC1 (scan, NCH ranks) → **circular DMA split in two
  halves**; **Half-Transfer + Transfer-Complete IRQs** (hardware ping-pong / buffer-A-B swap)
  each send BLOCK frames via **USART1 921600** TX-DMA (alternating TX buffers). Smooth + gap-free.
- **Baud jumps to 921600** for binary (115200 is too slow); run **without `--ascii`**.
- **Run:** `python emg_plotter.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick`
- **PASS when:** status bar shows steady **~2000 S/s**, **drop ~0**, **crc-err ~0**.
- Result: **PASS — steady ~2010–2128 S/s, continuous smooth stream, 0 crc-err**  Date: 2026-08-26
- **CP4 gotchas (both cost time):** (a) F103 ADC1 has **no TIM2 trigger** → use **TIM3 TRGO**
  (and no "trigger edge" setting exists on F103); (b) **USART1 global interrupt MUST be enabled**
  in NVIC or `HAL_UART_Transmit_DMA` locks BUSY after the first batch (one 10-frame burst then dead).
- Drops only accrue when touching a **bare PA0** (finger antenna) — real AFE = clean.
- **Professional UI built (2026-08-26):** Beihang-branded header (logo.png), session bar
  (subject/trial/notes), per-channel panel (editable muscle name, RMS, pk-pk, median freq,
  activation meter), event markers (key M), snapshot + HTML report, MVC normalization (% MVC),
  onset highlight overlay, live FFT spectrum. All headless-tested.

## CP5 — signal sanity (before trusting EMG)
- **DC** coupling: PA0→GND = flat 0 V line; PA0→3V3 = flat 3.3 V line (proves absolute scale).
- **AC** coupling: short AFE input to VREF → flat ~0 V baseline. Inject a small ~100 Hz tone
  → clean sine at expected amplitude.
- Connect the gel EMG AFE, flex muscle → bursts. Turn on **RMS env** / **Auto V/ch** to see activation.
- **PASS when:** DC lines land at the right voltage, AC baseline is flat, tone is clean,
  muscle bursts are obvious and repeatable.
- Result: ______________________  Date: __________

## CP6 — 5 channels (PA0–PA4)   ⏭ NEXT  (matches PROJECT_CONTEXT / HANDOFF)
> Record + V/div/Time-div scaling already shipped in the MVC instrument (see CP4 / instrument) —
> not a separate open checkpoint; folded into "done".
- **Firmware:** `#define NCH 5`; ADC **Scan** enabled, `NbrOfConversion = 5`, ranks 1–5 =
  `ADC_CHANNEL_0..4` (PA0–PA4), sample time 71.5 cyc. One **TIM3 TRGO** triggers the whole scan so
  all 5 channels are time-aligned in a single DMA sweep (needed for double-differential). Build → `flash_run.bat`.
- **PC:** `python emgscope.py --port COM8 --baud 921600 --channels 5 --fs 2000 --coupling AC --kick`.
- **PASS when:** 5 live lanes; touching each of PA0–PA4 moves only that lane; **S/s ≈ 2010, drop ≈ 0,
  crc ≈ 0** sustained (HG2); HG1 round-trip @ nch=5 and HG4 offscreen 5-lane both green.
- Result: ______________________  Date: __________
## T-001 Protocol Round-trip Validation

- **Status:** PASSED
- **Test:** `tests/test_protocol_roundtrip.py`
- **Result:** 1000 frames recovered and verified
- **Note:** Protocol sequence number is 8-bit (wraps at 256). This is acceptable for current frame sizes but should be re-evaluated for long recordings.
- **Gate:** Cleared
## EPIC-2: Firmware & Protocol Enhancements — COMPLETE

- T-001 Protocol round-trip test ✅
- T-002 Sequence width evaluation ✅
- T-003 Formalize protocol spec ✅
- T-004 Implement v2 16-bit sequence ✅
- T-005 Firmware C skeleton ✅
- T-006 End-to-end HIL simulation ✅

Result: Protocol v2 implemented and validated. Firmware skeleton ready.
No open blockers.
## T-010 Recording Controller

- Added `gui/recording_controller.py`.
- `EmgScope` now delegates recording to `RecordingController`.
- Launcher `run_emg.py` works with simulation.
- Status: PASSED