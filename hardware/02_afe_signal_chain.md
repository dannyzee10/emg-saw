# AFE Signal Chain — confirmed topology + values + 5-channel integration

Confirmed with Daniyal 2026-09-04 from the working single-channel V3 boards + LTspice schematic.
The new main board **replicates this proven per-channel analog ×5** and adds STM32U575 + ST67 Wi-Fi
+ power tree. Boards are linked by **FFC flat cable** (electrodes sit at different forearm sites).

## Per-channel chain (proven — reuse exactly)

**Dry electrode board (×5, one per channel) — AD8648 #1:**
- E1, E2, E3 → 3 unity buffers; each input node biased to VREF via **22 MΩ** (anti-float).
- 3 buffer outputs each via **100 kΩ → common VCM node** (average) → 4th amp = **VCM buffer**.
- Va(E1), Vb(E2), Vc(E3), VCM each via **100 Ω** → 13-pin FFC, GND-interleaved:
  `1 GND·2 Va·3 GND·4 Vb·5 GND·6 Vc·7 GND·8 VCM·9 GND·10 3V3·11 GND·12 VREF·13 GND`
- Receives 3V3 (pin 10) + VREF (pin 12) from the main board.

**Main board — per channel (values from the LTspice schematic):**
| Stage | Parts | Function |
|---|---|---|
| Double-diff input | Va·**R2 100 k** + Vc·**R5 100 k** → IN+ ; Vb·**R21 50 k** → IN− | 50 k = 100 k‖100 k ⇒ matched source Z ⇒ best CMRR; computes (Va+Vc)/2 − Vb |
| In-amp (U1 AD8237) | gain set by **R2H 26.1 k / R1 1.07 k** → **G = 1 + 26.1/1.07 = 25.4** | first gain |
| **500 Hz LPF** | **CH 12 n across R2H** → f = 1/(2π·26.1k·12n) = **508 Hz** | anti-alias, built into the in-amp feedback |
| DC servo (U9 AD8648) | **R22 2 MΩ + C3 3.3 µF** integrator (τ=6.6 s ⇒ corner **0.024 Hz**), non-inv=VRf → drives U1 **REF = Vservo** | removes per-channel DC offset; prevents the G≈25 stage saturating. **Consider C3=0.1 µF → 0.8 Hz for faster (~1 s) artifact recovery** (still ≪ 20 Hz) |
| **20 Hz HPF** | **CL 0.82 µF + RL 10 k** (AC-couple to stage 2) → f = 1/(2π·10k·0.82µ) = **19.4 Hz** | EMG band low edge |
| Gain stage (U3 AD8648) | inverting **RG 80.6 k / RL 10 k → ×8.06**, non-inv = **VRf (VREF)** | second gain → **VOUT** |

- **Total gain = 25.4 × 8.06 ≈ 205**, signal centered on **VREF = 1.65 V** ⇒ drops straight into the
  STM32 ADC (no level shift). Clip headroom ≈ ±1.65/205 ≈ **±8 mV input** (fine for sEMG; app does %MVC).
- Two reference nets: **VRf** = static buffered 1.65 V (gain-network return + U3 non-inv); **Vservo** =
  dynamic DC-servo output → AD8237 REF.

## Shared blocks on the main board (generate once for all 5 ch)
- **VREF buffer:** 3V3 → 100 k/100 k (+100 nF) = **1.65 V** → 1 buffer → all VRf + all electrodes (FFC pin 12).
- **DRL driver (shared, 1):** sum the **5 VCMs** (FFC pin 8 of each board) via 5 equal resistors → 1 amp
  (non-inv = VREF, feedback 10 k ‖ 1 nF) → **1 MΩ** → **one DRL electrode** (6th electrode on the body,
  wired straight to the main board — no DRL pin on the FFC). Bench-tune gain for the deepest 50/60 Hz null.

## AD8648 amp count — CORRECTION: ×3, not ×2
Per channel needs **2 AD8648 amps** (gain U3 + DC servo U9). So: 5 gain + 5 servo + 1 VREF + 1 DRL =
**12 amps = AD8648 ×3** (the earlier "×2" missed the per-channel DC servo).
⇒ Main-board AFE = **AD8237 ×5 + AD8648 ×3**. Higher analog load → the **micropower-quad swap matters
even more** (12 amps × ~2 mA vs × ~0.05 mA).

## Open items
- Confirm the two **"???" nets** in the sim (RG feedback top, VRf line) are properly connected on the board.
- **AD8237 bandwidth at G=25** must pass 508 Hz (verify curve — proven, likely OK).
- Micropower-quad choice (MCP6404 lead / TLV9064 alt) for the AD8648s, both electrode + main board.
