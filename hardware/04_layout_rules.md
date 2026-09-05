# Main Board — PCB Layout Rules (floorplan, stack-up, keep-outs, guard, vias)

The Altium-ready placement/routing guide for the 5-channel wireless board. This is the reference for the
interactive layout review (you place → snapshot → I check against this). Companion: `01/02/03`.

---

## 1. Stack-up — YES, 4-layer (2-layer cannot do Wi-Fi + µV EMG)
Wearable-thin ~1.0 mm total (or standard 1.6 mm). The point of 4 layers is a **solid ground plane right
under the components** for clean return currents + EMI control; the ST67 is a **module with its own
antenna**, so you carry **no controlled-impedance RF traces** — that simplifies the stack.

| Layer | Use | Copper |
|---|---|---|
| **L1 top** | ALL components + connectors; local GND pour in gaps, via-stitched to L2 | signal + GND pour |
| **L2** | **ONE solid GND plane — no splits, no traces, no cuts** (single AGND=DGND reference) | 100 % GND (except antenna keep-out) |
| **L3** | 3V3_DIG + 3V3_ANA pours + a few slow signals | power pours |
| **L4 bottom** | routing, decoupling caps, SWD/UART test pads, GND pour (stitched) | signal + GND pour |

Keep **L1↔L2 thin** (~0.1–0.2 mm prepreg) so every component's return path is tight.

---

## 2. Floorplan — where everything goes
```
  TOP EDGE (antenna radiates off-board here)
+-------------------------------------------------------------+
| [RF]  ST67-B + antenna      [DIGITAL]        [POWER — dirty] |
|  board corner,              STM32U575         buck-boost+L,  |
|  ALL-LAYER keep-out,        (ADC side faces   charger,USB-C, |
|  far from power+analog       analog↓)         mux, rev-pol   |
|                             SPI→ST67 short    ↕ diagonal from|
|                             SWD/UART pads       analog+antenna|
|- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -|
| [ANALOG QUIET ISLAND]                          [BATTERY]     |
|  each FFC → its AD8237 → servo → gain           Li-Po area,  |
|  VREF buffer + DRL driver + DRL pad             JST, fuel gauge|
|  ** LDO (3V3_ANA) lives HERE **                             |
|  J_El1  J_El2  J_El3  J_El4  J_El5   <- 5× FFC along this edge|
+-------------------------------------------------------------+
  BOTTOM EDGE (electrode flat-cables exit here)
        L2 = one solid GND plane under EVERYTHING
```
**Principle:** analog bottom-left, power top-right (**diagonal = max separation**), RF/antenna a third
corner (off-board edge, away from both), digital in the middle bridging them. Return currents self-
separate by placement — analog stays bottom/left, digital/switching stays top/right.

---

## 3. Placement rules per block
**Analog quiet island (bottom, electrode edge):**
- **5× FFC connectors in a row along the bottom edge**, each directly in front of **its own AD8237**
  (channel n's connector → channel n's in-amp, ~short). Then that channel's **servo + gain** cluster right
  behind the AD8237. Keep each channel's parts together — don't interleave channels.
- **Shared VREF buffer** central to the analog island (short, equal-ish runs to all 5 AD8237 REF nets).
- **DRL driver + DRL electrode pad** at the analog edge (1 MΩ series next to the pad).
- **LDO (TPS7A2033) sits INSIDE this zone** — it is the analog rail's source (its "power fence"), *not*
  in the power corner.
- The **first gain (AD8237) must be as close to its FFC as mechanically possible** — the Va/Vb/Vc inputs
  are the most sensitive nodes.

**Digital (middle):** STM32U575 with its **ADC pins facing the analog island** and its **SPI pins facing
ST67**. SPI bus (CLK/MOSI/MISO/CS/RDY) short + direct — treat as a noisy bus, never toward the electrodes.
SWD + ST67 UART/BOOT pads at the zone edge.

**RF (corner):** ST67-B in a **board corner**, antenna pointing **off the board edge**, with the full
**all-layer keep-out** (§4). Nothing under/around the antenna on any layer.

**Power (dirty corner, diagonal from analog + antenna):** buck-boost + its inductor (tight switch loop),
charger, USB-C, power-path mux, reverse-polarity FET. **Battery** in its own area (bottom-right), JST +
fuel gauge at the edge; keep battery metal off the antenna diagonal.

---

## 4. Keep-outs
| Area | Rule |
|---|---|
| **Antenna** | ST67-B in a corner; **no copper/traces/vias/parts on ANY layer** under the antenna clearance; keep far from power + metal + battery |
| **Under electrode/Va-Vb-Vc inputs** | no power pours on L3/L4 beneath the high-impedance input segment; guard ring on L1 instead |
| **Buck switch node** | short, wide, small copper (it radiates); output-cap GND via right at the cap |

---

## 5. Ground = ONE solid plane, separation by placement
- L2 is **one continuous GND** under everything (except the antenna keep-out). **Do NOT cut it** into
  AGND/DGND islands — a slot just forces return currents to detour and makes *more* noise.
- Separate analog/digital by **floorplan** (§2): analog parts clustered bottom/left, digital top/right, so
  their plane return currents never overlap.
- Route the STM32's **analog pins toward the analog zone, digital pins toward the digital zone.**
- Optional: label nets `AGND`/`DGND` and join with a **0 Ω / net-tie under the ADC corner** for schematic
  clarity — but physically the same plane. **No ferrite in the ground.**

---

## 6. Guard ring (per channel)
Around each AD8237's **Va/Vb/Vc input pads + short input traces**, a **continuous** copper loop
(0.25–0.5 mm wide, 0.1–0.3 mm gap), driven from that channel's reference (VREF / the buffered CM). No
trace crosses the moat; any gap = a new leakage path. Ground-referenced guard sections tie to the plane
with multiple vias.

---

## 7. Decoupling & vias
- **ST67:** 10 µF per VDD pin (VDD33, VDDIO×2), **each with its own via**; **≥5 vias in the center pad**;
  many GND vias top+bottom around the module.
- **STM32:** 100 nF per VDD pin + 4.7 µF bulk; VDDA 1 µF + 100 nF; VREF+ 1 µF + 100 nF. Vias in/beside
  the pad, never on a trace stub.
- **AFE:** 100 nF + 1 µF at each AD8237/AD8648 supply pin.
- **Stitching vias** along board edges (~2–3 mm) and along zone boundaries (a via fence between analog and
  digital helps contain digital return currents) — except across the antenna keep-out.

---

## 8. Routing rules (the big ones)
> ### ⚠️⚠️ #1 PRIORITY AT LAYOUT — THE BUCK SWITCHING LOOP
> Keep the loop **C_IN → VIN → L(1 µH) → VOUT → C_OUT → back to GND** as **physically tiny** as possible.
> This is the **only** fast-switching (2 MHz) current loop on the board and by far the biggest source of
> radiated noise — loop *area* is what radiates. Place C_IN and C_OUT hard against the TPS631000 pins,
> put the inductor immediately beside L1/L2, and give each cap its **own GND via right at the pad**.
> Everything else on this board is slow; get this one loop right and the EMG baseline stays clean.
> *(Daniyal asked to be reminded of this at layout time — 2026-09-05.)*

- **No electrode/analog trace ever crosses the digital, RF, or power zones** — not even "just a bit." If a
  trace leaves the analog island it is the **already-amplified, low-Z VOUT → ADC**, never a raw input.
- Keep **VOUT→ADC** runs short and guarded; group each channel.
- **SPI** short between STM32 and ST67; **buck switch loop** tiny; **I²C** slow, route freely.
- No controlled-impedance traces needed (antenna is on-module).

---

## 9. DFM / fab notes
- 4-layer, ~1.0 mm (wearable) or 1.6 mm; 0.5 mm FFC footprints (Hirose TF31 class) verified against DS.
- Board size estimate ≈ **50 × 55 mm** (5× FFC dominate the analog edge) — refine to the enclosure.
- ENIG finish (fine-pitch + skin-adjacent), min via/trace per fab (JLC 0.2/0.2 mm ok).

## 10. Layout review checklist (I'll check each snapshot against this)
1. L2 solid + unbroken?  2. Antenna keep-out clean, corner, off-board?  3. 5 FFC → their AD8237s, no
channel crossings?  4. LDO in analog zone, buck in power corner, diagonal separation?  5. No analog trace
over digital/RF/power?  6. Guard rings continuous?  7. ST67 10 µF/pin own via + ≥5 center-pad vias?
8. Switch-node loop tight?  9. SPI short?  10. Edge/boundary stitching?
