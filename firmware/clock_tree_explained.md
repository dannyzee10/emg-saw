# STM32 clock tree — how to configure RCC + Clock Configuration (learning note)

The one idea: every peripheral (CPU, timers, UART, ADC, USB) runs on a clock.
There is ONE source and a tree of multipliers/dividers that fans it out. Configuring
clocks = routing that tree so each block stays under its legal max.

## 1. RCC = choosing the SOURCE ("crystal set")
RCC = Reset & Clock Control. Pick where the clock originates:

| Source | What | When |
|--------|------|------|
| HSI | internal RC ~8 MHz, drifts ±1% | quick, no precision |
| **HSE** | external crystal (Blue Pill = 8 MHz), precise/stable | USB, high-baud UART, timing-critical |
| LSI | ~40 kHz internal | watchdog |
| LSE | 32.768 kHz external | RTC |

We chose HSE = Crystal → CubeMX reserves PD0/PD1 (OSC_IN/OUT). Precision matters for
921600 baud and USB's exact 48 MHz.

## 2. The tree (F103, what we built)
```
8 MHz HSE ─► PLL ×9 ─► SYSCLK 72MHz ─► AHB /1 ─► HCLK 72MHz (CPU, RAM, DMA)
                                          ├─ APB1 /2 ─► PCLK1 36MHz (TIM2/3/4, USART2/3)
                                          ├─ APB2 /1 ─► PCLK2 72MHz (ADC, USART1, GPIO, TIM1)
                                          └─ ADC /6  ─► 12MHz (ADC core)
```
Knobs: PLL multiplier (overall speed), System Clock Mux (PLLCLK vs HSE/HSI), AHB
prescaler (HCLK), APB1/APB2 prescalers (peripheral buses), ADC prescaler.

## 3. The walls (F103 maximums — configure UNDER these)
| Clock | Max |
|-------|-----|
| SYSCLK / HCLK | 72 MHz |
| PCLK1 (APB1) | 36 MHz  ← half the rest |
| PCLK2 (APB2) | 72 MHz |
| ADC clock | 14 MHz  ← very low, why we use /6 → 12 |
| USB | exactly 48 MHz (72 ÷ 1.5) |
CubeMX turns a box RED when you exceed a wall — your safety net.

## 4. The quirk: timer ×2 rule
When an APB prescaler > 1, timers on that bus get DOUBLE the bus clock.
PCLK1 = 36 but APB1 **timer** clock = 72. That is why TIM2 math uses 72 MHz:
`rate = TimerClk / (PSC+1) / (ARR+1)` → 72e6/72/500 = 2000 Hz.
Always read the timer clock line, not the bus line.

## 5. Where to turn knobs for a requirement
| Want | Knob |
|------|------|
| more CPU speed | raise PLL mult (≤ 72) |
| lower power | lower PLL / use HSI / raise AHB prescaler |
| bus over its max | raise that APB prescaler |
| faster/slower ADC | ADC prescaler (≤14 MHz) |
| different sample rate | TIM PSC/ARR |
| precise UART/USB | HSE crystal + SYSCLK that divides to 48 MHz |

## 6. Recipe for any STM32 project
1. Pick target SYSCLK. 2. Source: HSE if precision needed, else HSI.
3. PLL mult to reach target. 4. Sys Clock Mux = PLLCLK. 5. AHB /1.
6. APB1/APB2 prescalers under their max. 7. ADC prescaler ≤ ADC max.
8. USB path to 48 MHz if used. 9. Fix any red boxes.

Method is identical on every STM32; only the wall numbers change (F4: 168/42/84/36 MHz).
Learn the recipe, look up the 4–5 maxes for your chip.

## Tie-in to this EMG project
- 72 MHz gives headroom + clean 48 MHz USB option + 72 MHz timer clock.
- TIM2 @72MHz: PSC=71, ARR=499 → 2000 Hz sample rate (ARR=249 → 4000 Hz, etc.).
- ADC ≤14 MHz → /6 → 12 MHz sets conversion speed (~5.7 µs/channel).
- Higher SYSCLK → lower baud-rate error at 921600.
