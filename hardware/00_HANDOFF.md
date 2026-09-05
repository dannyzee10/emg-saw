# 5-Channel Wireless Wearable EMG Board — Project Handoff

**Owner:** Muhammad Daniyal (MS Biomedical Engineering, Beihang University)
**Status as of 2026-09-05:** schematic ~60 % captured · power sheet **design-frozen pending 1 edit** ·
PCB layout not started · dev boards on order
**Repo:** `emg-saw`, branch **`hardware`** · docs in `hardware/`

---

## 1. What this board is

A **body-worn, battery-powered, 5-channel surface-EMG acquisition board** that streams to a laptop over
Wi-Fi. It is the wireless successor to a **working single-channel prototype** that already streams to the
`emg-saw` PyQt scope over serial via a Blue Pill.

```
5 × remote active dry-electrode boards        MAIN BOARD (this project)
  E1,E2,E3 → 3 buffers → Va,Vb,Vc  ──FFC──►  double-diff → AD8237 (G=25.4) → DC servo
  (+ local VREF buffer)                       → 20–500 Hz → ×8.06 → STM32U575 ADC
                                              → ST67W611M1 Wi-Fi → laptop emg-saw scope
                                              + USB-C charge / Li-Po / power tree
```

**Key numbers:** total gain **205** · band **19.4–508 Hz** · signal centred on **1.50 V** ·
5 ch × 1–2 kS/s × 14-bit ≈ **10–20 kB/s** (≈1 % of the radio) · 1000 mAh Li-Po → **~30–38 h** realistic.

## 2. Documents in this folder

| File | Contents |
|---|---|
| **00_HANDOFF.md** | ← this file: status, decisions, next steps |
| **01_power_tree_design.md** | power architecture rationale + formulas |
| **02_afe_signal_chain.md** | AFE topology, DRL-removal decision, amp packing |
| **03_mainboard_schematic.md** | block-by-block schematic design + BOM |
| **04_layout_rules.md** | 4-layer stack, floorplan, keep-outs, **the buck-loop rule** |
| **05_data_pipeline.md** | 5-ch simultaneous streaming feasibility + optimal config |
| **06_pin_reference.md** | ⭐ **complete pin-by-pin for every IC, as built** |
| `power_tree_diagram.html`, `power_stage2_mux_buck.html` | rendered diagrams |

## 3. Architecture decisions (and why)

| Decision | Rationale |
|---|---|
| **STM32U575 + ST67W611M1-B** | ST's own reference pairing; U5 is µA/MHz class with 14-bit ADC |
| **3V3_DIG = 3.30 V** | ST67 absolute max is **3.63 V** — this is the binding constraint, not the MCU |
| **3V3_ANA = 3.00 V via LDO** | gives the LDO **300 mV** headroom = TI's characterised 95 dB PSRR point |
| **Ratiometric ADC** (VREF+ = 3V3_ANA = the AFE rail) | rail noise cancels between the signal and the reference |
| **Buck-boost + LDO** (not LDO alone) | efficiency across the 4.2→3.0 V cell swing, then linear silence for the AFE |
| **Forced PWM (MODE high)** | fixed 2 MHz is far outside 20–500 Hz; PFM's wandering rate is not |
| **DRL removed; passive grounded reference** | Daniyal's own dry-electrode tests: grounded ref worked, DRL saturated. Literature supports omitting RLD for EMG. DRL footprint kept DNP |
| **DC servo per channel** | at G=25.4 a ±300 mV dry-electrode offset would rail the stage; the AD8237's REF-pin integrator is the datasheet's own solution |
| **Double-differential (Va+Vc)/2 − Vb** | rejects crosstalk from distant muscles; source impedances balanced at 50 kΩ |
| **1000 mAh cell** | ~30–38 h; charges at 0.3 C; thinner than 2000 mAh for a wearable |

## 4. Timeline of what was done

1. Confirmed the real topology by parsing the Altium `.PcbDoc` files + the LTspice schematic — found the
   AFE is split (buffers on the electrode, in-amp + gain on the main board).
2. Designed power tree, 5-channel AFE integration, layout rules, data pipeline.
3. **Removed the DRL** after reviewing Daniyal's results + literature; repurposed the freed op-amps
   (local VREF buffer on the electrode, second VREF buffer on the main board) — 12 amps, 3 quads, none idle.
4. Captured in Altium: 5 AFE channel sheets, Analog_Shared, Power_tree_design.
5. **Multi-agent design review** (datasheet-verified) → 14 changes → **13 applied and re-verified**.

## 5. The review that changed the design

Three independent agents audited pinouts, values, and system architecture against manufacturer datasheets.
Headline findings:

- 🔴 **3.5 V rail exceeded the ST67's 3.63 V absolute maximum** → rails re-planned to 3.30/3.00 V.
- 🔴 **Inductor Isat (2.0 A) was below the converter's 2.6 A current limit** → would saturate before the
  IC limits on a fault → swapped to DFE21CCN1R0MELL (3.3 A).
- 🔴 **16 capacitors were 01005** — unassemblable at JLCPCB → all moved to 0402.
- 🟢 **Confirmed sound:** rail ordering (VDDA derived from VDD makes ST's forbidden sequence impossible),
  the single unbroken ground plane, the ratiometric reference, the TPS2116 priority wiring, the AD8237
  choice, and — importantly — **the Wi-Fi burst noise path**: ~6 µV on 3V3_ANA → **<100 nV RTI** vs a
  1.5 µVrms noise floor. *"Your architecture already handles this. Don't redesign it."*

### Changes applied (13/14)
| # | Ref | Change |
|---|---|---|
| 1 | L1 | DFE18SAN1R0ME0L → **DFE21CCN1R0MELL** (Isat 2.0 → 3.3 A) |
| 2 | 16 caps | GRM022 (01005) → **GRM155R61C104KA88D** (0402) |
| 3 | RUP_3/RUP_4 | 604 k/100 k → **560 k/100 k** ⇒ 3.30 V |
| 4 | UP5 | TPS7A2033 → **TPS7A2030** (3.0 V) |
| 5 | CUP4 | 22 µF → **47 µF** (derating vs 10.4 µF minimum) |
| 6 | RUP_1 | 330 k → **270 kΩ** (PR1 ref is ±8 %) |
| 7 | R2_DET | 100 k → **300 kΩ** (was in the logic-indeterminate band) |
| 8 | C_CHG1/2 | 4.7 µF/10 V → **10 µF/25 V** |
| 9 | R_CHG1 | 2.0 k → **3.3 kΩ** (500 → 303 mA; less heat on skin, fits USB budget) |
| 10 | Q1 | DMG3415U-7 (NRND) → **DMP2045U-7** |
| 11 | UP5 EN | tied to IN → **STM32 GPIO + 1 MΩ pulldown** |
| 12 | CUP4_1 | **new 10 µF** at the buck VIN pin |
| 13 | UP6 pin 4 | VBAT_NEG → **GND** (net deleted) |
| — | U1–U3 | bonus: MCP6404 SOIC-14 → **TSSOP-14** |
| **14** | **Q1 gate** | ⚠️ **NOT YET APPLIED — add R_G 100 kΩ from pin 1 (G) to GND** |

## 6. Open items before design freeze

**Schematic**
- [ ] **R_G 100 kΩ** on the Q1 gate (item 14)
- [ ] Stale description on `RTT025002FTH` (reads 100 kΩ; part is **50 kΩ**)
- [ ] Clear remaining `{{_voltage}}` parameter fields
- [ ] Sheets still to draw: **MCU (STM32U575)**, **RF (ST67W611M1)**, **Connectors (5× FFC, USB-C, battery)**, **Top**
- [ ] Then Annotate → Compile → ERC → netlist

**Deferred to the electrode-board revision** (main board goes first)
- [ ] **100 kΩ series resistor in every electrode lead** — limits single-fault current to 30 µA
- [ ] RC/ferrite RF filtering at the remote op-amp inputs (the MCP6404 has no internal EMI filter; the AD8237 does)
- [ ] Electrode rail moves 3.3 → **3.0 V**, local VREF becomes **1.50 V**

**Recommended additions (not yet decided)**
- [ ] Anti-alias RC at each ADC input, or oversample ≥4 kS/s and decimate
- [ ] Lead-off detection (firmware: output within 2 % of rail for >N ms) — zero BOM cost
- [ ] Local 22–47 µF bulk at the ST67 module
- [ ] DNP footprints: DRL, test-signal injection
- [ ] Battery over-discharge cutoff via the MAX17048 ALERT (already wired)
- [ ] Charge off-body, or add an NTC / move to MCP73833

## 7. Safety position (research device, not certified)
- **Normal condition:** AD8237 input bias 250 pA typ / 1 nA over temp → ~1000× inside the IEC 60601-1
  Type CF limit (10 µA). ✅
- **Single fault:** currently limited only by the LDO's 360–520 mA current limit → **the 100 kΩ series
  resistors above are the fix** (→ 30 µA, inside the CF 50 µA single-fault limit).
- **Charging:** USB is **charge-only** — the data path is Wi-Fi, so the device never needs USB while worn.
  **Make wear and charge mechanically exclusive** and document it; that is the strongest practical answer.
- Firmware already reads `USB_DET`; with EN on a GPIO the analog rail can also be de-energised in hardware.

## 8. Next steps (in order)
1. Apply the last schematic edits; finish MCU/RF/Connector sheets; ERC clean.
2. **PCB layout** per `04_layout_rules.md` — the **#1 rule is the tiny buck switching loop**.
3. **De-risk on dev boards** (NUCLEO-U575ZI-Q + X-NUCLEO-67W61M1, ordered): 5-ch ADC + DMA, ST67 Wi-Fi
   bring-up, add a TCP source to the emg-saw scope, stream the proven 1-ch analog end-to-end.
4. **Gate:** order the PCB only after layout review **and** dev-board streaming both pass.
5. Bring-up order: rails (no load) → STM32 + SWD → ST67 (CHIP_EN ≥3.3 ms after power) → VREF → 1 channel
   → 5 channels → wireless streaming.
