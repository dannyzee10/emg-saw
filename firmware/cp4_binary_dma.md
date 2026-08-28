# CP4 — ping-pong: TIM2 @ 2 kHz → ADC circular-DMA (HT/TC double-buffer) → binary frames

This is the jitter-free, gap-free pipeline. Your **buffer-A / buffer-B swap is done by the
DMA controller in hardware** using a circular buffer split into two halves:

```
TIM3 (2000 Hz TRGO) ─► ADC1 (scan, NCH ranks) ─DMA(circular, 2 halves)─► adc_buf[2*BLOCK*NCH]
                                    │                         │
                          Half-Transfer IRQ (HT)     Transfer-Complete IRQ (TC)
                          "half A full"              "half B full"
                                    │                         │
                          send half A  ───────────►  send half B   (while DMA fills the other half)
                                    (UART1 921600, TX-DMA, alternating txbuf[0]/[1])
```

- DMA never stops. The CPU only touches the **idle** half → zero gaps, no overruns.
- HT fires at the halfway point (BLOCK sample-sets), TC at the end (another BLOCK). That's
  your A/B ping-pong, automatic.
- Frames are the **same bytes** `protocol.py` parses (verified). Time is exact because TIM
  paces the ADC — the display time axis is now real.

**Tuning `BLOCK`:** small = smoother display + more interrupts; large = fewer interrupts +
lumpier. At 2 kHz, **BLOCK = 10** → HT/TC every 5 ms → 200 small sends/s (smooth). Data rate
for NCH=5: 15 B/frame × 2000 = 30 kB/s ≪ 92 kB/s @ 921600. ✓

## 1. CubeMX (.ioc)

**Clock:** 72 MHz; **ADC prescaler /6 → 12 MHz** (already set).

**TIM3** — Internal Clock; **PSC=71, ARR=499** (→2000 Hz); **TRGO = Update Event**.
  (Use TIM3, NOT TIM2 — the F103 ADC1 has no TIM2-TRGO trigger; its timer-TRGO option is TIM3.)

**ADC1**
- Channels: **IN0 (PA0)** now; for 5 later tick **IN0..IN4 (PA0–PA4)**.
- **Number Of Conversion = NCH**; Rank1=IN0, Rank2=IN1, … For **1 channel** leave Scan
  **Disabled**; for **≥2 channels** set **Scan Conversion Mode = Enabled**.
- **External Trigger Conversion Source = Timer 3 Trigger Out event**
  (the F103 has **no** separate "trigger edge" setting — skip it, the edge is implicit)
- **Continuous Conversion Mode = Disabled** (TIM re-triggers each scan)
- Sampling Time (each rank) = **55.5 Cycles**
- **DMA Settings** ▸ Add **ADC1** ▸ Mode **Circular**, Peripheral & Memory width **Half Word**

**USART1** — Asynchronous, **921600** baud.
- DMA Settings ▸ add **USART1_TX**, Mode **Normal**, Byte.
- **NVIC Settings ▸ check "USART1 global interrupt"** ← REQUIRED. `HAL_UART_Transmit_DMA`
  needs the USART transmit-complete IRQ to mark the UART ready again; without it the UART
  locks BUSY after the very first transfer and only ONE batch ever goes out.

**Ctrl+S** to regenerate.

## 2. Code (main.c)

`/* USER CODE BEGIN PD */`
```c
#define NCH        1                 /* 1 now; set 5 when PA0..PA4 are wired */
#define BLOCK      10                /* sample-sets per half (HT/TC granularity) */
#define SYNC1      0xAA
#define SYNC2      0x55
#define FRAME_LEN  (5 + 2*NCH)
```

`/* USER CODE BEGIN PV */`
```c
static volatile uint16_t adc_buf[2 * BLOCK * NCH];      /* DMA circular: [halfA | halfB] */
static uint8_t  txbuf[2][BLOCK * FRAME_LEN];            /* ping-pong TX buffers */
static volatile uint8_t tx_sel = 0;
static uint8_t  seq = 0;
static volatile uint32_t tx_drops = 0;                 /* frames lost if UART still busy */
```

`/* USER CODE BEGIN 0 */`  (CRC + frame builder — identical bytes to protocol.py)
```c
static uint16_t crc16_ccitt(const uint8_t *d, uint32_t n) {
    uint16_t crc = 0xFFFF;
    for (uint32_t i = 0; i < n; i++) {
        crc ^= (uint16_t)d[i] << 8;
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021)
                                 : (uint16_t)(crc << 1);
    }
    return crc;
}

/* frame = AA 55 | seq | NCH*int16 LE | crc16 LE   (len = 5 + 2*NCH) */
static uint32_t build_frame(uint8_t *out, uint8_t s, const volatile uint16_t *codes) {
    uint8_t body[1 + 2*NCH];
    body[0] = s;
    for (int c = 0; c < NCH; c++) {
        uint16_t v = codes[c];
        body[1 + 2*c]     = (uint8_t)(v & 0xFF);
        body[1 + 2*c + 1] = (uint8_t)((v >> 8) & 0xFF);
    }
    uint16_t crc = crc16_ccitt(body, sizeof(body));
    out[0] = SYNC1; out[1] = SYNC2;
    for (uint32_t i = 0; i < sizeof(body); i++) out[2 + i] = body[i];
    out[2 + sizeof(body)]     = (uint8_t)(crc & 0xFF);
    out[2 + sizeof(body) + 1] = (uint8_t)((crc >> 8) & 0xFF);
    return FRAME_LEN;
}

/* Build BLOCK frames from one DMA half and fire one UART-DMA transfer. */
static void send_half(int half) {
    const volatile uint16_t *src = &adc_buf[half * BLOCK * NCH];
    uint8_t *tx = txbuf[tx_sel];
    uint32_t off = 0;
    for (int s = 0; s < BLOCK; s++)
        off += build_frame(tx + off, seq++, &src[s * NCH]);
    if (HAL_UART_Transmit_DMA(&huart1, tx, off) != HAL_OK)
        tx_drops += BLOCK;                 /* previous TX not done -> lost (shouldn't happen) */
    else
        tx_sel ^= 1;                       /* swap TX buffer for the next half */
}
```

`/* USER CODE BEGIN 2 */`  (after the MX_*_Init calls)
```c
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, 2 * BLOCK * NCH);
HAL_TIM_Base_Start(&htim3);               /* TIM3 TRGO now paces the ADC at 2 kHz */
```
Leave the `while (1)` body **empty** — everything is DMA/IRQ driven.

`/* USER CODE BEGIN 4 */`  (the two ping-pong callbacks)
```c
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {   /* half A ready */
    if (hadc->Instance == ADC1) send_half(0);
}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {       /* half B ready */
    if (hadc->Instance == ADC1) send_half(1);
}
```

## 3. Flash + run + view
- Build (Ctrl+B) → **double-click `flash_run.bat`** (never the IDE Debug button).
- PC (binary — **no `--ascii`**, baud **921600**, fs **2000**):
```
python emg_plotter.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick
```
- Status bar: steady **~2000 S/s**, **drop 0**, **crc-err 0**. The sweep is now smooth and the
  time axis is accurate.

## 4. Scale to 5 channels
1. Wire inputs to **PA0–PA4**. `.ioc`: ADC scan, Number Of Conversion = 5, Rank1..5 = IN0..IN4. Ctrl+S.
2. `#define NCH 5`. Rebuild, `flash_run.bat`.
3. PC: `... --channels 5 --fs 2000 ...`, turn on **Auto V/ch** for per-lane MR4 view.
All 5 sampled in one scan → perfectly time-aligned (needed for double-differential).

## 5. Sanity + notes
- **Byte format is verified** against `protocol.py` (round-trip + resync + CRC on the PC side,
  and the parser is now crash-proof against noise bursts).
- **If `drop`/`tx_drops` climbs:** BLOCK×FRAME_LEN bytes must send faster than BLOCK/fs seconds.
  At 2 kHz, 921600 baud: NCH=5 → 150 B in 1.6 ms vs a 5 ms budget. Fine. If you raise fs or NCH
  a lot, either raise the baud or reduce BLOCK.
- **adc_buf is `volatile`** so the compiler always re-reads the DMA-written values.
- **No cache maintenance needed** on Cortex-M3 (no data cache), unlike F7/H7.
```
