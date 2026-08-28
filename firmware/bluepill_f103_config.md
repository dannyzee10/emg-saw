# Blue Pill (STM32F103C8T6) — exact CubeIDE config for the EMG streamer

Part: **STM32F103C8Tx**. Cortex-M3 @ 72 MHz, 2× 12-bit ADC (max ADC clock 14 MHz),
USB-FS device. New project in STM32CubeIDE → select this part.

## Transport decision (this board)
- **Flash + debug:** ST-Link over **SWD** → SYS ▸ Debug = **Serial Wire** (keeps PA13/PA14).
- **Data to PC:** **USART1 (PA9/PA10)** into your FTDI → a COM port. BOOT0 = 0 to run.
  (USB-CDC on PA11/PA12 is possible but the Blue Pill USB pull-up is often wrong — do FTDI first.)

## Clock tree (RCC + Clock Configuration tab)
Blue Pill has an **8 MHz** HSE crystal (Y2).
- RCC ▸ High Speed Clock (HSE) = **Crystal/Ceramic Resonator**
- Clock Config: PLL source = HSE, **PLLMUL = ×9** → **SYSCLK = 72 MHz**
- AHB /1 = 72 MHz
- **APB1 /2 = 36 MHz**  → **TIM2 timer clock = 72 MHz** (×2 because APB1 presc > 1)
- APB2 /1 = 72 MHz (ADC1, USART1, GPIOA)
- **ADC prescaler = /6 → 12 MHz** (must stay ≤ 14 MHz — /4 would be 18 MHz, illegal)

## TIM2 — the sample clock (fs = 2000 Hz)
Timer clock 72 MHz, need 2000 Hz → divide by 36000 = **(PSC+1)·(ARR+1)**.
- **Prescaler PSC = 71**  (÷72 → 1 MHz)
- **Counter Period ARR = 499**  (÷500 → 2000 Hz)
- Trigger Event Selection (TRGO) = **Update Event**
- Other fs: ARR = (1e6 / fs) − 1 with PSC = 71. e.g. fs=1000 → ARR=999; fs=1500 → ARR=665.

## ADC1
- Resolution 12 bit; External Trigger Conv = **Timer 2 Trigger Out (T2 TRGO)**, edge **Rising**.
- **1 channel now:** Scan mode off, Rank 1 = **IN0 (PA0)**.
- **5 channels later:** Scan mode **on**, Number Of Conversions = **5**,
  Ranks 1..5 = **IN0..IN4 = PA0,PA1,PA2,PA3,PA4**.
- Sampling time = **55.5 cycles** (plenty; at 12 MHz that's ~5.7 µs/ch → 5 ch ≈ 28 µs ≪ 500 µs).
- DMA: add **ADC1** request, **Circular**, Peripheral-to-Memory, both widths **Half Word**.
- **ADC reference = VDDA = 3.3 V** on this package (no separate VREF+ pin) → run the PC app
  with `--vref 3.3 --bits 12`. (VDDA is a bit noisy on Blue Pill; fine for bring-up.)

## USART1 (data out)
- Mode = Asynchronous → **PA9 = TX, PA10 = RX**.
- Baud **921600**, 8-N-1.
- DMA Settings: add **USART1_TX**, **Normal** mode, Memory-to-Peripheral, Byte.

## Pin map summary
| Pin | Use |
|-----|-----|
| PA0 | ADC1_IN0 — EMG ch1 (add PA1..PA4 for ch2..5) |
| PA9  | USART1_TX → FTDI RXI (EMG data to PC) |
| PA10 | USART1_RX ← FTDI TXO (optional) |
| PA13/PA14 | SWDIO/SWCLK → ST-Link (flash + debug) |
| PA11/PA12 | USB D-/D+ (only if you later try USB-CDC) |
| G / GND | common ground with FTDI **and** your EMG AFE |

## Generate code, then paste the frame builder
Use the C in `stm32_firmware.md` (`build_frame` + `crc16_ccitt` +
`HAL_ADC_ConvCpltCallback`), with:
```c
#define NCH 1        // 1 now; set 5 when you wire 5 electrodes
extern UART_HandleTypeDef huart1;   // send via HAL_UART_Transmit_DMA(&huart1, ...)
```
In `main()` after init:
```c
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, NCH);
HAL_TIM_Base_Start(&htim2);
```

## Bring-up order (least firmware first)
1. `--ascii`: in a slow loop `printf`→USART1 one ADC value; open
   `python emg_plotter.py --port COMx --ascii --channels 1`. Proves FTDI/port/baud.
2. Move to TIM/DMA + binary `build_frame`, drop `--ascii`. Watch **crc-err/dropped** ≈ 0.
3. Short the AFE input to VREF → flat 0 V line; inject a small 100 Hz tone → clean sine.
   Then trust the EMG.

## Gotchas specific to this board
- **One power source at a time** — ST-Link 3.3 V **or** FTDI 5 V, never both.
- Blue Pill 3.3 V regulator is weak/noisy; for clean EMG later, power the analog AFE from
  its own quiet supply and share only GND.
- Set FTDI to **3.3 V** logic. Lower the FTDI **latency timer to 1 ms** (Device Manager ▸
  COM port ▸ Advanced) for snappier display — throughput is fine either way.
