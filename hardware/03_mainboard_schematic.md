# Main Board — 5-Channel Schematic (net-by-net) + BOM

New wireless main board: 5 active dry-electrode boards (FFC) → 5-channel AFE → STM32U575 ADC →
ST67W611M1-B Wi-Fi, on the power tree in `01_power_tree_design.md`. Analog values confirmed in
`02_afe_signal_chain.md`. Suffix `n = 1..5` = channel number.

---

## A. Per-channel AFE  (replicate ×5)

**A.1 FFC connector `J_Eln` (13-pin, per electrode board)** — pinout mirrors the electrode:
`1 GND · 2 Va_n · 3 GND · 4 Vb_n · 5 GND · 6 Vc_n · 7 GND · 8 VCM_n · 9 GND · 10 3V3_ANA · 11 GND ·
12 VREF · 13 GND`  *(9-pin variant: VREF local on electrode + shared returns — see FFC note.)*

**A.2 Double-differential network → in-amp `U1_n` (AD8237):**
| Net | Via | To |
|---|---|---|
| Va_n | R (100 k) | IN+ node `DDp_n` |
| Vc_n | R (100 k) | IN+ node `DDp_n` → U1_n **IN+** |
| Vb_n | R (50 k) | U1_n **IN−** |
| U1_n REF | — | `Vservo_n` (from A.3) |
| U1_n FB / gain | R2H 26.1 k (OUT→FB), R1 1.07 k (FB→VRf), **CH 12 nF ‖ R2H** | G = 25.4, LPF 508 Hz |
| U1_n +VS / −VS | 3V3_ANA / GND | 100 nF + 1 µF decoupling |
| U1_n OUT | — | `INA_OUT_n` |

**A.3 DC servo `U9_n` (one AD8648 amp, inverting integrator):**
`INA_OUT_n → R22 (2 MΩ) → U9_n IN−` ; `C3 (0.1 µF*) : U9_n OUT→IN−` ; `U9_n IN+ = VRf` ;
`U9_n OUT = Vservo_n → U1_n REF`.  *(*0.1 µF → 0.8 Hz for ~1 s artifact recovery; 3.3 µF = original 0.024 Hz.)*

**A.4 Interstage HPF + gain `U3_n` (one AD8648 amp, inverting ×8):**
`INA_OUT_n → CL (0.82 µF) → RL (10 k) → U3_n IN−` (HPF 19.4 Hz) ; `RG (80.6 k) : OUT→IN−` (gain −8.06) ;
`U3_n IN+ = VRf` ; `U3_n OUT = VOUT_n → STM32 ADC`.  **Total gain ≈ 205, centered on 1.65 V.**

---

## B. Shared analog blocks (once for all 5 channels)

**B.1 VREF buffer (one AD8648 amp):** `3V3_ANA → R(100 k)→ node ←R(100 k)→ GND` (+100 nF) = 1.65 V →
buffer → **VRf** to: all U1_n REF-network R1, all U9_n IN+, all U3_n IN+, and FFC pin 12 (if VREF sent).

**B.2 DRL driver (one AD8648 amp) → one DRL electrode:**
`VCM_1..5 each → R_in (50 k) → DRL amp IN−` (inverting summer, averages the 5 VCMs) ;
`R_f 10 k ‖ C_f 1 nF : OUT→IN−` ; `IN+ = VRf` ; `OUT → R_drl (1 MΩ) → J_DRL` (reference electrode on body).
Bench-tune R_in/R_f for deepest 50/60 Hz null without oscillation.

**B.3 Op-amp packing:** 5× AD8237 (U1_1..5) + **3× AD8648** = 12 amps: 5 gain (U3) + 5 servo (U9) +
1 VREF buffer + 1 DRL. *(Micropower swap: replace the 3 AD8648 with 3× MCP6404/TLV9064.)*

---

## C. STM32U575AII6Q  (ADC + host; set exact pins in CubeMX)

| Function | Peripheral / pins (suggested) | Notes |
|---|---|---|
| EMG in ×5 | ADC1_IN[] on PA0–PA4 | VOUT_1..5; DMA, ~1–2 kS/s/ch, 14-bit |
| VBAT sense | ADC1_IN on PA5 | from fuel-gauge node or divider |
| USB detect | GPIO PB2 | VBUS-sense → disable acquisition on USB |
| SPI→ST67 | SPI1: SCK PA5→(use PB3), MISO PB4, MOSI PB5, CS PA15 | ≤40 MHz full-duplex |
| ST67 ctrl | CHIP_EN PB1, SPI_RDY PB0 (EXTI), BOOT PB10 | CHIP_EN high ≥3.3 ms after ST67 power |
| I²C→gauge | I2C1: SCL PB8, SDA PB9 | MAX17048 @0x36; ALRT→PB6 |
| Clock | HSE 16–32 MHz (or HSI); **LSE 32.768 kHz** | LSE can also feed ST67 32 kHz |
| SWD | SWDIO PA13, SWCLK PA14, NRST | 5 test pads |
| Power | VDD/VDDIO = 3V3_DIG; **VDDA/VREF+ = 3V3_ANA** | 100 nF/pin + 4.7 µF bulk; VDDA 1 µF+100 nF |

> ADC references the **quiet 3V3_ANA** (VDDA/VREF+), same rail as the electrodes ⇒ ratiometric, low-noise.

---

## D. ST67W611M1-B  (Wi-Fi/BLE module; pins per ST datasheet / B2413 ref)

| Function | Pin(s) | Connection |
|---|---|---|
| Power | VDD33 (16), VDDIO (9, 25) | 3V3_DIG; **10 µF each pin, own via** |
| Ground | GND (10,15,18,26,30,32) + center pad | solid plane; **≥5 vias in center pad** |
| Enable | CHIP_EN | STM32 GPIO + **100 nF to GND**; high ≥3.3 ms after power |
| SPI (host) | CLK, MOSI, MISO, CS, SPI_RDY | to STM32 SPI1 (≤40 MHz) |
| Boot/test | UART_TX (22), UART_RX (23), BOOT | 3 test pads (factory FW / recovery) |
| 32 kHz | 32K_IN | optional from STM32 LSE (3.3 V swing) or use internal osc |
| Antenna | on-module PCB antenna (-B) | **all-layer keep-out, board corner** (see 04) |

---

## E. Connectors

| Ref | Type | Purpose |
|---|---|---|
| J_El1..5 | 13-pin (or 9) FFC, 0.5 mm | 5 electrode boards |
| J_DRL | 1-pin pad / snap | shared DRL reference electrode on body |
| J_USB | USB-C 16-pin | charge + optional DFU (power tree §1) |
| J_BAT | JST-PH 2-pin | Li-Po (power tree §3) |
| TP_SWD | 5 pads | SWDIO/SWCLK/NRST/3V3/GND |
| TP_ST67 | 3 pads | UART_TX/RX/BOOT |

---

## F. Consolidated BOM (main board)

| Qty | Ref | Part | Pkg |
|---|---|---|---|
| 1 | U_MCU | STM32U575AII6Q | UFBGA-169 |
| 1 | U_RF | ST67W611M1-B | module |
| 5 | U1_1..5 | AD8237ARMZ | MSOP-8 |
| 3 | U2_A..C | AD8648ARUZ *(or MCP6404/TLV9064)* | TSSOP-14 |
| 1 | U_CHG | MCP73831T-2ACI/OT | SOT-23-5 |
| 1 | U_MUX | TPS2116DMWR | VSSOP-8 |
| 1 | U_BB | TPS631000DRLR | SOT-583 |
| 1 | U_LDO | TPS7A2033PDBVR | SOT-23-5 |
| 1 | U_FG | MAX17048G+T10 | µDFN-8 |
| 1 | Q_RP | DMG3415U | SOT-23 |
| 1 | L_BB | 1 µH shielded [confirm DS] | 2016 |
| 5 | — | FFC 13-pin 0.5 mm (Hirose TF31 class) | — |
| — | R (per ch ×5) | 100 k×2, 50 k, 26.1 k, 1.07 k, 2 M, 10 k, 80.6 k | 0402 |
| — | R (shared) | 100 k×2 (VREF), 50 k×5 + 10 k + 1 M (DRL) | 0402 |
| — | C (per ch ×5) | 12 nF, 0.1 µF (servo), 0.82 µF, +decoupling | 0402 |
| — | C/R (digital) | ST67 10 µF×3, 100 nF×many, 4.7 µF bulk, I²C 4.7 k×2 | 0402/0805 |
| — | Power passives | per `01_power_tree_design.md` | — |

---

## G. Verify
- Per channel: DC at every node ≈ 1.65 V; VOUT swings ±≤1.65 V, no clip at MVC.
- Servo holds baseline at 1.65 V; recovers <2 s after a forced saturation.
- DRL: 50/60 Hz residual drops with DRL connected (tune R_in/R_f).
- ADC: 5 channels stream cleanly into the emg-saw scope; VDDA = 3V3_ANA quiet.
- ST67: CHIP_EN timing, SPI enumerates, Wi-Fi associates; antenna keep-out clean.
