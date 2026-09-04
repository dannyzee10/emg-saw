# AFE Signal Chain — confirmed topology + values + 5-channel integration

Confirmed with Daniyal 2026-09-04 from the working single-channel V3 boards + LTspice schematic.
The new main board **replicates this proven per-channel analog ×5** and adds STM32U575 + ST67 Wi-Fi
+ power tree. Boards are linked by **FFC flat cable** (electrodes sit at different forearm sites).

## Per-channel chain (proven — reuse exactly)

**Dry electrode board (×5, one per channel) — quad op-amp #1:**
- E1, E2, E3 → 3 unity buffers; each input node biased to **local VREF** via **22 MΩ** (anti-float).
- **4th amp = LOCAL VREF buffer** (see "DRL removed" below): FFC VREF → **RC (10 k + 1 µF)** → buffer →
  the board's local VREF (feeds the three 22 MΩ bias resistors).
  *(Was the VCM buffer + 3× 100 kΩ averaging — deleted with the DRL.)*
- Va(E1), Vb(E2), Vc(E3) each via **100 Ω** → 13-pin FFC, GND-interleaved:
  `1 GND·2 Va·3 GND·4 Vb·5 GND·6 Vc·7 GND·8 GND*·9 GND·10 3V3·11 GND·12 VREF·13 GND`
  *(pin 8 was VCM → now GND / spare.)*
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

## DECISION 2026-09-04 — **DRL REMOVED** (grounded reference instead)
Evidence: (a) Daniyal's own tests — grounded reference works with **dry** electrodes; DRL saturated /
added noise; (b) literature — for EMG the RLD "can be omitted", direct grounding matches it with good
filtering (*Optimizing sEMG Acquisition without Right Leg Drive*); (c) DRL is a body-loop feedback system
with documented **instability** at high loop gain. The double-differential front end already rejects
common mode, so the passive reference is the robust choice.

**What is deleted:** the DRL amp + its resistors/cap, the electrode-board **VCM node (3× 100 kΩ) and VCM
buffer**, and the **VCM wire (FFC pin 8)**.
**What replaces it:** **one shared reference electrode → series R (10 kΩ default, 0 Ω = Daniyal's tested
config) → GND**, common to all 5 channels (the body has one common-mode; a single reference serves any
number of differential channels — standard practice in commercial multichannel EMG).
**Future hedge (free):** leave an **unpopulated DRL footprint + GND↔DRL jumper** on the reference line.
No VCM circuitry is needed to revive it — Va/Vb/Vc of every channel are already on the main board, so a
common-mode sense can be resistively summed there if a DRL is ever wanted.
> Do **not** run a grounded reference and a DRL at the same time — two biases fight (the low-Z ground
> shorts out the DRL). A *unipolar* system's "REF" is a signal input, a different role; ours is differential.

## Shared blocks on the main board (generate once for all 5 ch)
- **VREF generation:** 3V3_ANA → 100 k/100 k divider (+100 nF, +10 µF at the divider node) = **1.65 V**.
- **TWO VREF buffers** (instead of 1 + DRL): buffer A → channels 1–3, buffer B → channels 4–5 + the FFC
  VREF pins. Splitting the load halves the shared-impedance path between channels ⇒ **less inter-channel
  crosstalk**, and it uses the amp the DRL freed (no extra cost, nothing left idle).

## Amp count after the change — packs perfectly into 3 quads
Per channel = **2 amps** (gain + DC servo). Total = 5 gain + 5 servo + **2 VREF buffers = 12 amps =
exactly 3 quads, all 12 used, none wasted.**
⇒ Main-board AFE = **AD8237 ×5 + quad ×3** (MCP6404 micropower, or AD8648).
Electrode board = **quad ×1 per board**: 3 electrode buffers + **1 local VREF buffer** (all 4 used).

## Open items
- Confirm the two **"???" nets** in the sim (RG feedback top, VRf line) are properly connected on the board.
- **AD8237 bandwidth at G=25** must pass 508 Hz (verify curve — proven, likely OK).
- Micropower-quad choice (MCP6404 lead / TLV9064 alt) for the AD8648s, both electrode + main board.
