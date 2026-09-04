# Main Board — Power Tree, Schematic-Level Design

**Board:** 5-channel wireless EMG main board (STM32U575 + ST67W611M1-B), plugging into 5× active
dry-electrode boards (each 3.3 V, AD8237 + AD8648, over a Hirose TF31-13S mezzanine).
**Scope of this file:** the complete power section, net-by-net, with values, footprints, and formulas —
ready to capture in Altium. Companion files: `02_st67_stm32_design.md`, `03_electrode_interface.md`,
`04_layout_rules.md`, `BOM.md`.

> Status: values below are design-ready; three externals (buck-boost L / Cin / Cout) are marked
> **[confirm DS]** — copy them from the TPS631000 datasheet typical-application table before layout.

---

## 0. Rail decisions

| Rail | Voltage | Source | Feeds | Why |
|---|---|---|---|---|
| **VSYS** | 3.0–5.0 V | power-path mux (battery or USB) | buck-boost input | one input for the converter whether on battery or USB |
| **3V3_DIG** | **3.5 V** | TPS631000 buck-boost | STM32U575 VDD, ST67 VDD33/VDDIO | must sit ≥140 mV above the analog LDO output so the LDO can regulate |
| **3V3_ANA** | **3.3 V** | TPS7A2033 LDO (from 3V3_DIG) | 5× electrode boards (via TF31), STM32 VDDA/VREF+ | clean, low-noise rail for the µV analog front ends |

**Why 3.5 V digital, not 3.3 V:** the electrodes are designed for 3.3 V, so the analog LDO output must
be 3.3 V. The TPS7A20 needs ≥140 mV dropout (worst case, 300 mA); running the buck-boost at **3.5 V**
gives the LDO ~200 mV headroom **across the entire battery discharge** (the buck-boost output is
regulated regardless of cell voltage), which cleanly removes the end-of-discharge dropout worry in the
original analysis. 3.5 V is inside spec for both digital parts (STM32U575 ≤3.6 V; ST67 2.97–3.63 V).
*Lower-margin alternative:* 3V3_DIG = 3.3 V + 3V3_ANA = 3.0 V (electrodes then run at 3.0 V, VCM ≈ 1.5 V).

---

## 1. USB-C input + protection

| Ref | Part | Value / PN | Footprint | Notes |
|---|---|---|---|---|
| J_USB | USB-C receptacle, 16-pin mid-mount | power-only | per vendor | VBUS, GND, CC1, CC2, (D+/D− optional to STM32 USB) |
| R_CC1, R_CC2 | Resistor | 5.1 kΩ ×2 | 0402 | CC1→GND, CC2→GND → makes a source deliver 5 V (UFP) |
| D_VBUS | TVS diode | 5.0 V standoff, ~SMAJ5.0A / uni | SOD-323/SMA | VBUS→GND, ESD/surge clamp |
| C_VBUS | Cap | 10 µF | 0805 | VBUS bulk near the connector |

**Nets:** `VBUS`, `USB_CC1`, `USB_CC2`, `GND`.

---

## 2. Charger — MCP73831

Single-cell linear Li-Po charger. **Charge current set by R_PROG:** `I_reg(mA) = 1000 / R_PROG(kΩ)`
→ **R_PROG = 2.0 kΩ ⇒ 500 mA** (0.5 C for a 1000 mAh cell). *(For a 2000 mAh cell, 500 mA = 0.25 C,
~8–10 h charge — MCP73831 max is 500 mA; go to a switching charger only if that's too slow.)*

| Ref | Part | Value / PN | Footprint | Connection |
|---|---|---|---|---|
| U_CHG | MCP73831T-2ACI/OT | — | SOT-23-5 | VDD=VBUS, VSS=GND |
| R_PROG | Resistor | 2.0 kΩ | 0402 | PROG → GND (sets 500 mA) |
| C_IN_CHG | Cap | 4.7 µF | 0603 | VBUS → GND at VDD pin |
| C_BAT_CHG | Cap | 4.7 µF | 0603 | VBAT → GND at the battery output |
| D_STAT | LED | green | 0603 | VBUS → R_STAT → STAT (sinks when charging) |
| R_STAT | Resistor | 1 kΩ | 0402 | LED series |

**Nets:** `VBUS`, `VBAT_CHG` (charger output → battery node), `GND`, `CHG_STAT` (optional → STM32 GPIO).

---

## 3. Battery + reverse-polarity + power-path mux

Battery: 3.7 V Li-Po **with integrated PCM**, 1000 mAh default (JST-PH). The charger output and the
battery tie at `VBAT`. Reverse-polarity via a P-MOSFET; USB-vs-battery selection via an automatic mux.

| Ref | Part | Value / PN | Footprint | Connection |
|---|---|---|---|---|
| J_BAT | JST-PH 2-pin | — | TH | +→VBAT_RAW, −→GND; **verify polarity vs cell vendor** |
| Q_RP | P-MOSFET (rev-pol) | e.g. DMG3415U / SI2301 | SOT-23 | source=VBAT_RAW, drain=VBAT, gate=GND (blocks reversed insert) |
| U_MUX | TPS2116 (auto power mux, 1.6–5.5 V) | — | VSSOP-8 | IN1=VBUS (priority), IN2=VBAT, OUT=VSYS |
| C_MUX | Cap | 1 µF | 0402 | VSYS → GND |

**Behaviour:** USB present → mux delivers **VBUS (5 V)** to VSYS (system runs from USB) while the charger
tops up the battery; USB absent → mux delivers **VBAT**. `VBUS` also drives a sense divider to the STM32
so firmware **disables acquisition while USB is connected** (see §7 of the analysis doc).
**Nets:** `VBAT_RAW`, `VBAT`, `VSYS`, `GND`.

*VBUS-sense:* R divider VBUS→(R 200 k)→node→(R 100 k)→GND into an STM32 ADC/GPIO = `USB_DET`.

---

## 4. Buck-boost pre-regulator — TPS631000 → 3V3_DIG (3.5 V)

Output set by a divider on FB: **VFB = 0.5 V**, `R1 = R2 · (VOUT/VFB − 1)`, R2 ≤ 100 kΩ.
For **3.5 V**: R1 = 100 k · (3.5/0.5 − 1) = **600 kΩ** → use **R1 = 604 kΩ (E96)**, **R2 = 100 kΩ**
(gives 3.52 V). ([TI TPS631000 datasheet](https://www.mouser.com/datasheet/2/405/1/tps631000-3383876.pdf))

| Ref | Part | Value / PN | Footprint | Connection |
|---|---|---|---|---|
| U_BB | TPS631000DRLR | — | SOT-583 | VIN/VINA=VSYS, VOUT=3V3_DIG, EN=VSYS (or STM32 GPIO), PGND/GND=GND |
| L_BB | Inductor (shielded) | **1 µH** [confirm DS] | ~2.0×1.6 mm | between L1/L2 switch pins |
| C_IN_BB | Cap | **10 µF** [confirm DS] | 0805 | VIN → GND, tight |
| C_OUT_BB | Cap | **22 µF** [confirm DS] | 0805 | VOUT(3V3_DIG) → GND, tight |
| R1_BB | Resistor | 604 kΩ | 0402 | VOUT → FB |
| R2_BB | Resistor | 100 kΩ | 0402 | FB → GND |

2 MHz fixed switching, Iq 8 µA, up to 1.5 A — far above our ~100 mW load. Keep the switch-node loop
(VIN cap → IC → inductor → VOUT cap) **tiny**; this is the only dirty loop on the board.
**Nets:** `VSYS`, `3V3_DIG`, `SW1`/`SW2` (switch node), `FB_BB`, `GND`.

---

## 5. Analog LDO — TPS7A2033 → 3V3_ANA (3.3 V, fixed)

Post-regulates 3V3_DIG down to a quiet 3.3 V for the electrodes + STM32 analog. **7 µVrms, 95 dB PSRR
@ 1 kHz, no NR cap required.** ([TI TPS7A20 datasheet](https://www.ti.com/lit/ds/symlink/tps7a20.pdf))

| Ref | Part | Value / PN | Footprint | Connection |
|---|---|---|---|---|
| U_LDO | TPS7A2033PDBVR (3.3 V fixed) | — | SOT-23-5 | IN=3V3_DIG, OUT=3V3_ANA, EN=3V3_DIG (or GPIO), GND=GND |
| C_IN_LDO | Cap | 1 µF | 0402 | IN → GND |
| C_OUT_LDO | Cap | 1 µF (+ 10 µF bulk) | 0402/0805 | OUT → GND |

3V3_ANA fans out to the **5× TF31 connectors** (electrode supply) and to **STM32 VDDA/VREF+**. Load ≈
5 × (AD8237 0.575 mA + AD8648) ≈ well under the 300 mA rating; dropout at that load ≈ tens of mV.
**Nets:** `3V3_DIG`, `3V3_ANA`, `GND`.

---

## 6. Fuel gauge — MAX17048 (on the battery node)

| Ref | Part | Value / PN | Footprint | Connection |
|---|---|---|---|---|
| U_FG | MAX17048G+T10 | — | µDFN-8 | CELL=VBAT, GND=GND, SDA/SCL→STM32 I²C, ALRT→STM32 GPIO |
| C_FG | Cap | 1 µF | 0402 | CELL → GND |
| R_SDA, R_SCL | Resistor | 4.7 kΩ ×2 | 0402 | I²C pull-ups to 3V3_DIG |

ModelGauge (no sense resistor), 23 µA, low-battery ALRT → firmware warns before dropout.
**Nets:** `VBAT`, `I2C_SDA`, `I2C_SCL`, `FG_ALRT`, `GND`.

---

## 7. Power-section BOM (subtotal)

| Qty | Ref(s) | Part | Package |
|---|---|---|---|
| 1 | U_CHG | MCP73831T-2ACI/OT | SOT-23-5 |
| 1 | U_MUX | TPS2116DMWR | VSSOP-8 |
| 1 | U_BB | TPS631000DRLR | SOT-583 |
| 1 | U_LDO | TPS7A2033PDBVR | SOT-23-5 |
| 1 | U_FG | MAX17048G+T10 | µDFN-8 |
| 1 | Q_RP | DMG3415U (P-MOS) | SOT-23 |
| 1 | L_BB | 1 µH shielded [confirm DS] | 2016 |
| 1 | D_VBUS | SMAJ5.0A TVS | SMA |
| 1 | D_STAT | LED green | 0603 |
| — | Rs | 5.1 k×2, 2 k, 1 k, 604 k, 100 k, 200 k, 100 k, 4.7 k×2 | 0402 |
| — | Cs | 10 µF×2, 22 µF, 4.7 µF×2, 1 µF×4 | 0402–0805 |

---

## 8. Verification (power)

- **Rail check:** VSYS 3.0–5.0 V → 3V3_DIG = 3.5 V (±) → 3V3_ANA = 3.3 V; confirm LDO headroom = 3.5−3.3
  = 200 mV > dropout at load.
- **Charge:** R_PROG 2 kΩ ⇒ 500 mA; STAT LED on while charging; MCP73831 thermal (~0.4–0.65 W) → copper pour.
- **Power-path:** plug/unplug USB → VSYS stays up (mux glitch-free); `USB_DET` reads high on USB.
- **Fuel gauge:** I²C responds at 0x36; SOC tracks discharge.
- **Budget (recompute in the doc):** duty-cycled ≈31 mA → ~28 h on 1000 mAh; verify with the actual
  5×(AD8237+AD8648) electrode load added.
