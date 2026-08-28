# STM32 firmware — timer-triggered ADC → DMA → framed binary

This is the sensor side. The golden rule: **do not sample in a `while(1)` loop with
`HAL_Delay`.** Let a hardware timer trigger the ADC and DMA move the results. That
gives jitter-free timing — without it your EMG spectrum and filters are meaningless.

```
TIM2 (update @ fs) ──trigger──► ADC1 (scan, NCH channels) ──DMA──► adc_buf[NCH]
                                                          │
                                          conversion-complete IRQ
                                                          │
                                              build frame -> send (UART-DMA or USB-CDC)
```

## 1. CubeMX configuration

**Clock:** enable HSE/PLL, get a known `SystemCoreClock` (e.g. 72 or 168 MHz).

**ADC1**
- Resolution 12 bit.
- Scan Conversion Mode: **Enabled** (needed for >1 channel).
- Number Of Conversions = `NCH` (your channel count; start with 1).
- Rank 1..NCH → your EMG input pins (e.g. PA0, PA1, …).
- External Trigger Conversion Source: **Timer 2 Trigger Out (TRGO)**.
- External Trigger Conversion Edge: **Rising**.
- DMA: add ADC1 request, **Circular**, Peripheral→Memory, Data width **Half Word**.
- Sampling time: pick a long-ish value (e.g. 84–239.5 cycles) so the ADC input
  settles — EMG source impedance after your AFE is low, but longer is safer.

**TIM2** (the sample-rate clock)
- Clock source: Internal.
- Trigger Output (TRGO): **Update Event**.
- Set ARR/PSC so update rate = `fs`. With timer clock `f_tim`:
  `(PSC+1)*(ARR+1) = f_tim / fs`.
  Example: `f_tim = 72 MHz`, `fs = 2000` → divide by 36000 → `PSC=71, ARR=499`
  ((71+1)*(499+1)=36000). Check `f_tim` for your TIM2 (APB1 timer clock, often 2×PCLK1).

**Transport — pick ONE:**
- **USB_DEVICE → Communication Device Class (Virtual Port Com)** — recommended.
  Appears as a COM port, USB Full-Speed has huge headroom. Use `CDC_Transmit_FS()`.
- **or USARTx** at **921600** baud, 8N1, with **DMA TX** (Normal mode). Feed the
  ST-Link Virtual COM Port or a USB-UART. 921600 ≈ 92 kB/s ≫ needed.

Bandwidth check: frame = `5 + 2*NCH` bytes × `fs`. 5 ch @ 2 kHz = 16×2000 = 32 kB/s.
Fits UART@921600 and is trivial for USB-CDC.

## 2. Frame builder (must byte-match `protocol.py`)

```c
#include <stdint.h>
#include <string.h>

#define NCH 1                       /* keep in sync with --channels on the PC */
#define SYNC1 0xAA
#define SYNC2 0x55

/* CRC-16/CCITT-FALSE: poly 0x1021, init 0xFFFF. Identical to crc16_ccitt() in Python. */
static uint16_t crc16_ccitt(const uint8_t *d, uint32_t n) {
    uint16_t crc = 0xFFFF;
    for (uint32_t i = 0; i < n; i++) {
        crc ^= (uint16_t)d[i] << 8;
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1);
    }
    return crc;
}

/* frame = SYNC1 SYNC2 | seq | NCH*int16 LE | crc16 LE   (len = 5 + 2*NCH) */
static uint32_t build_frame(uint8_t *out, uint8_t seq, const uint16_t *codes) {
    uint8_t body[1 + 2*NCH];
    body[0] = seq;
    for (int c = 0; c < NCH; c++) {
        int16_t v = (int16_t)codes[c];          /* raw 12-bit code 0..4095 fits int16 */
        body[1 + 2*c]     = (uint8_t)(v & 0xFF);
        body[1 + 2*c + 1] = (uint8_t)((v >> 8) & 0xFF);
    }
    uint16_t crc = crc16_ccitt(body, sizeof(body));
    out[0] = SYNC1; out[1] = SYNC2;
    memcpy(out + 2, body, sizeof(body));
    out[2 + sizeof(body)]     = (uint8_t)(crc & 0xFF);
    out[2 + sizeof(body) + 1] = (uint8_t)((crc >> 8) & 0xFF);
    return 2 + sizeof(body) + 2;
}
```

## 3. Wire it up (main.c)

```c
extern ADC_HandleTypeDef hadc1;
extern TIM_HandleTypeDef htim2;
extern UART_HandleTypeDef huart1;     /* if using UART */

static volatile uint16_t adc_buf[NCH];
static uint8_t seq = 0;
static uint8_t txbuf[5 + 2*NCH];

/* --- init (after HAL_Init / MX_*_Init) --- */
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, NCH);
HAL_TIM_Base_Start(&htim2);           /* TRGO now paces the ADC */

/* Fires when the DMA has one full NCH sample-set ready. */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance != ADC1) return;
    uint16_t codes[NCH];
    for (int c = 0; c < NCH; c++) codes[c] = adc_buf[c];   /* snapshot */
    uint32_t n = build_frame(txbuf, seq++, codes);

    /* UART path (DMA, non-blocking): */
    HAL_UART_Transmit_DMA(&huart1, txbuf, n);
    /* USB-CDC path instead: while (CDC_Transmit_FS(txbuf, n) == USBD_BUSY); */
}
```

Notes:
- With **circular** ADC DMA + `NCH` conversions triggered per TIM update, the
  conv-complete callback fires once per sample-set at `fs`. Good to `fs` ≈ a few kHz.
- If you push `fs`×`NCH` very high, batch several sample-sets per USB packet instead of
  one-frame-per-sample (fewer, bigger transfers). Not needed at 2 kHz.
- Make sure UART TX-DMA has finished before the next frame (at 2 kHz each frame is 0.5 ms;
  16 bytes @ 921600 ≈ 0.17 ms, so it's clear). If you ever overrun, switch to USB-CDC or
  a small software TX ring buffer.

## 4. Quick bring-up ladder (do these in order)
1. **ASCII first:** `printf("%d\r\n", adc_buf[0]);` at ~100 Hz, open with
   `--ascii --channels 1`. Confirms wiring/port/baud with the least firmware.
2. Switch to `HAL_UART_Transmit_DMA` + `printf("%d,%d\n",...)` for N channels, still `--ascii`.
3. Move to **binary** `build_frame` + `--channels N` (drop `--ascii`). Watch `crc-err`
   and `dropped` in the status bar — both should stay ~0.
4. Feed a known signal (e.g. AFE input shorted to VREF → flat line at 0 V after DC removal;
   a small 100 Hz test tone → clean sine) to validate scale before trusting EMG.
```
```
