# Complete Pin-by-Pin Connection Reference — AS BUILT

**Board:** 5-channel wireless wearable EMG main board
**Date:** 2026-09-05 · **Source:** `EMG_MainBoard.PrjPcb` (Altium), verified against the exported PDF
**Rails:** `VBUS` 5 V · `VBAT_RAW`/`VBAT` 3.0–4.2 V · `VSYS` 3.0–5.0 V · **`3V3_DIG` = 3.30 V** ·
**`3V3_ANA` = 3.00 V** · `VREF_A`/`VREF_B` = **1.50 V**

> **Golden rule used throughout:** components are wired by **pin NAME**, then the pin NUMBER is verified
> against the manufacturer datasheet for that exact orderable part number and package. Every pinout below
> has been datasheet-verified.

---

## 1. J1 — USB4105-GF-A-060 (USB-C receptacle, 16 contacts + 8 dummy)
| Pin(s) | Name | Connects to | Notes |
|---|---|---|---|
| A4_B9, B4_A9 | VBUS ×2 | **joined → `VBUS`** | both must be joined |
| A1_B12, B1_A12 | GND ×2 | `GND` | |
| SH1–SH4 | SHELL_GND | `GND` | all four |
| A5 | CC1 | → **RJ1 5.1 kΩ** → `GND` | Rd sink termination — without it, no power |
| B5 | CC2 | → **RJ2 5.1 kΩ** → `GND` | one per CC pin (cable flip) |
| A6/B6, A7/B7, A8/B8 | DP1/2, DN1/2, SBU1/2 | **unconnected** | No-ERC ✗ · power-only design |

**On the VBUS net:** `D_VBUS` PESD5V0S1BA (TVS, cathode→VBUS) · `C_VBUS` 10 µF
**USB detect:** `VBUS →` **R1_DET 200 kΩ** `→ USB_DET →` **R2_DET 300 kΩ** `→ GND` → STM32 GPIO/ADC
(0.6 × VBUS = 2.85–3.15 V — clears VIH = 0.7 × 3.30 = 2.31 V, stays under VDD)

## 2. UP1 — MCP73831T-2ACI/MC (Li-Po charger, **DFN-8** — *not* the SOT-23-5 pinout)
| Pin | Name | Connects to | Component |
|---|---|---|---|
| 1, 2 | VDD ×2 | **joined →** `VBUS` | `C_CHG1` **10 µF** → GND |
| 3, 4 | VBAT ×2 | **joined →** `VBAT` | `C_CHG2` **10 µF** → GND |
| 5 | STAT | `VSTAT` | chain: `VBUS →` **R_STAT 1 kΩ** `→ LED1 anode → cathode → VSTAT` |
| 6 | VSS | `GND` | |
| 7 | NC | unconnected | No-ERC ✗ |
| 8 | PROG | → **R_CHG1 3.3 kΩ** → `GND` | **I = 1000/R(kΩ) = 303 mA** |
| 9 | EP | **`GND`** | thermal pad — needs vias |

## 3. J_Li-Po (Header 2) + Q1 — DMP2045U-7 (reverse-polarity, SOT-23 P-MOS)
| Pin | Connects to |
|---|---|
| J_Li-Po 2 | `VBAT_RAW` (battery **+**) |
| J_Li-Po 1 | `GND` (battery **−**) |
| **Q1 pin 3 (D)** | **`VBAT_RAW`** ← battery side |
| **Q1 pin 2 (S)** | **`VBAT`** ← system side |
| **Q1 pin 1 (G)** | → **R_G 100 kΩ** → `GND` ⚠️ *(R_G still to be added)* |

> **Why D→battery, S→load:** the P-MOS body diode's anode is at D. Correct polarity forward-biases it,
> the source rises, Vgs = −Vbat → channel on. Reversed battery back-biases the diode **and** leaves
> Vgs = 0 → fully blocked. **Source-to-battery is a *load-switch* orientation and gives NO reverse
> protection** — the body diode would conduct in the fault case.

## 4. UP3 — TPS2116DRLR (power mux, SOT-583) — USB priority
| Pin | Name | Connects to | Component |
|---|---|---|---|
| 3 | VIN1 | `VBUS` | `CUP3_1` 1 µF → GND |
| 6 | VIN2 | `VBAT` | `CUP3_2` 1 µF → GND |
| 5 | **MODE** | **`VBUS`** | high ⇒ priority mode |
| 4 | **PR1** | divider node | `VBUS →` **RUP_1 270 kΩ** `→ PR1 →` **RUP_2 100 kΩ** `→ GND` |
| 2, 7 | VOUT ×2 | **joined →** `VSYS` | `CUP3_3` 10 µF → GND |
| 8 | ST | unconnected | No-ERC ✗ *(optional: pull-up → GPIO = source telemetry)* |
| 1 | GND | `GND` | |

**Logic:** PR1 > VREF(0.92/1.0/1.08 V) ⇒ VIN1 (USB). 270 k/100 k ⇒ trips at **3.70 V nominal**
(worst-case 4.08 V) — safely below any real USB-C VBUS. USB removed ⇒ PR1 = 0 **and** MODE = 0 ⇒
auto-mode picks the higher supply = battery. **Two independent paths to the battery.**

## 5. UP4 — TPS631000DRLR (buck-boost, SOT-583) → 3V3_DIG = 3.30 V
| Pin | Name | Connects to | Component |
|---|---|---|---|
| 4 | VIN | `VSYS` | **`CUP4_1` 10 µF** at the pin |
| 5 | EN | → **R_EN 100 kΩ** → `VSYS` | must never float |
| 6 | MODE | `3V3_DIG` | high ⇒ forced PWM (fixed 2 MHz, out of the EMG band) |
| 7 | GND | `GND` | |
| 1 | VOUT | `3V3_DIG` | **`CUP4` 47 µF** at the pin |
| 3 ↔ 2 | LX1 ↔ LX2 | **`L1` DFE21CCN1R0MELL** | 1 µH, **Isat 3.3 A**, 60 mΩ, shielded, 0805 |
| 8 | FB | divider | `3V3_DIG →` **RUP_3 560 kΩ** `→ FB →` **RUP_4 100 kΩ** `→ GND`, **CUP4_FB 10 pF C0G across RUP_3** |

**V_OUT = 0.5 × (1 + 560/100) = 3.300 V.** Worst case 3.212–3.390 V → 240 mV under the ST67's
**3.63 V absolute max**, 212 mV above the 3.0 V LDO. ✅

## 6. UP5 — TPS7A2030PDBVR (analog LDO, SOT-23-5) → 3V3_ANA = 3.00 V
| Pin | Name | Connects to | Component |
|---|---|---|---|
| 1 | IN | `3V3_DIG` | `CUP5_1` 1 µF |
| 2 | GND | `GND` | |
| 3 | **EN** | **STM32 GPIO** + **R_EN_PD 1 MΩ** → GND | defaults OFF (internal 500 kΩ pulldown) |
| 4 | N/C | unconnected | "no internal electrical connection" |
| 5 | OUT | `3V3_ANA` | `CUP5_2` 1 µF + `CUP5_3` 10 µF |

**300 mV headroom** = exactly TI's lowest characterised PSRR condition (95 dB @ 1 kHz).
`3V3_ANA` fans out to: 5× AD8237 +VS, 3× MCP6404 VDD, **5 electrode boards via FFC**, STM32 VDDA/VREF+.

## 7. UP6 — MAX17048G+T10 (fuel gauge, TDFN-8)
| Pin | Name | Connects to | Component |
|---|---|---|---|
| 1 | **CTG** | `GND` | datasheet: "Connect to Ground" |
| 2 | CELL | `VBAT` | *not internally connected on the '48* — harmless, keeps '49 compatibility |
| 3 | **VDD** | **`VBAT`** | ⚠️ on the MAX17048 **VDD is the battery sense input**; `CU6_1` **0.1 µF** at the pin |
| 4 | GND | `GND` | |
| 5 | ALERT | `FG_ALRT` → STM32 GPIO | open-drain → **R_AL 10 kΩ** → `3V3_DIG` |
| 6 | QSTRT | `GND` | "connect to GND if not used" |
| 7 | SCL | `I2C_SCL` | **R_SCL 4.7 kΩ** → `3V3_DIG` |
| 8 | SDA | `I2C_SDA` | **R_SDA 4.7 kΩ** → `3V3_DIG` |
| 9 | EP | `GND` | exposed pad |

*Abs max on SDA/SCL/ALRT is +6 V **independent of VDD**, so 3.3 V pull-ups are safe even at a 3.0 V cell.*

---

## 8. Per-channel AFE ×5 (`AFE_Channel_1..5.SchDoc`)
Identical in all 5; only the net suffix and op-amp part letter change.

**INA1..5 — AD8237ARMZ (MSOP-8):**
| Pin | Connects to |
|---|---|
| BW | `3V3_ANA` |
| +IN | `Vb_n` via **RDD2 50 kΩ** (RTT025002FTH) |
| −IN | `Va_n` via **RDD1 100 kΩ** ⊕ `Vc_n` via **RDD3 100 kΩ** (joined) |
| REF | **`Vservo_n`** ← DC servo output |
| FB | junction of **RH_1 26.1 kΩ** (from VOUT) and **RL_1 1.07 kΩ** (to `VREF_x`) |
| VOUT | `INA_OUT_n`; **CH_n 12 nF across RH_1** ⇒ LPF 508 Hz |
| +VS / −VS | `3V3_ANA` (CCU 100 nF + 1 µF) / `GND` |

**Gain = 1 + 26.1/1.07 = 25.4.** Source impedance is balanced: +IN sees 50 k, −IN sees 100 k‖100 k = 50 k.

**DC servo (one MCP6404 amp):** `INA_OUT_n →` **Rservo 2 MΩ** `→ (−)`; **Cservo 100 nF** (out→−);
`(+) = VREF_x`; out = **`Vservo_n` → INA REF**. τ = 0.2 s ⇒ 0.8 Hz.

**Gain stage (one MCP6404 amp):** `INA_OUT_n →` **CL 0.82 µF** `→` **RGN 10 kΩ** `→ (−)`;
**RG 80.6 kΩ** (out→−); `(+) = VREF_x`; out = **`VOUT_n` → STM32 ADC**.
HPF = 19.4 Hz · gain = −8.06 · **total gain ≈ 205**, centred on 1.50 V.

**Op-amp packing (3 quads, 12 amps, none wasted):**
| Chip | A | B | C | D |
|---|---|---|---|---|
| **U1** | ch1 gain | ch1 servo | **VREF_A buffer** | **VREF_B buffer** |
| **U2** | ch2 gain | ch2 servo | ch3 gain | ch3 servo |
| **U3** | ch4 gain | ch4 servo | ch5 gain | ch5 servo |
`VREF_A` → channels 1–3 · `VREF_B` → channels 4–5 + all FFC pin 12

## 9. Analog_Shared.SchDoc
- Divider: `3V3_ANA →` **RV2 100 kΩ** `→ VDiv →` **RV1 100 kΩ** `→ GND` = **1.50 V**
- At VDiv: **Cdiv_10uF 10 µF + Cdiv_1 100 nF** to GND · on the rail: **Cdiv 100 nF**
- **U1C** (+ = VDiv, unity gain) → `VREF_A` · **U1D** (+ = VDiv, unity gain) → `VREF_B`
- **J_REF** (reference electrode) → **R_ref 0 Ω** → `GND`  *(footprint allows 10 kΩ later)*

## 10. FFC to each electrode board (13-pin, GND-interleaved)
`1 GND · 2 Va · 3 GND · 4 Vb · 5 GND · 6 Vc · 7 GND · 8 GND* · 9 GND · 10 3V3_ANA · 11 GND · 12 VREF · 13 GND`
*(pin 8 was VCM before the DRL was removed)*

---

## 11. Still to do on the schematic
- [ ] **R_G 100 kΩ** between Q1 pin 1 (gate) and GND — use the existing `AC0402FR-7D100KL`
- [ ] Fix stale description on `RTT025002FTH` (says 100 kΩ, part is **50 kΩ**)
- [ ] Resolve remaining `{{_voltage}}` parameter fields before generating the BOM
- [ ] MCU sheet (STM32U575), RF sheet (ST67W611M1), Connectors sheet (5× FFC), Top sheet
- [ ] Then: Annotate → Compile → ERC → netlist → PCB
