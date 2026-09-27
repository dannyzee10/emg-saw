# BF final-net escape seeds and reference stitch

All scans retain the native BF fixed copper, pads and components. Geometry SHA-256: `95662332096e888b7d20b3e8bcd4df59af21af8ed7dd5d67409cce30bda61151`. No router or CAD operation was performed by these checkers.

| Candidate | Proven geometry | Planning CSV / evidence |
| --- | --- | --- |
| CS destination escape | 0.45/0.20 through via `(58.38,25.838)` with a 0.18 mm Top stub from R_SPI_CS.1 center `(58.48,25.538)`. Via partly overlaps its own pad; filled/capped VIP group tag included. All fixed copper, drill and edge checks pass. | `ASTRA_BF_CS_ESCAPE_SEED_ADDS.csv`; `ASTRA_BF_FINAL_ESCAPE_SITES.json` |
| MCU TX source escape | 0.45/0.20 through via exactly at R_WIFI_UART_TX_LINK.2 center `(44.026,40.805)`. No track stub required. Filled/capped VIP tag included. All fixed copper, drill and edge checks pass. | `ASTRA_BF_TX_LINK_ESCAPE_SEED_ADDS.csv`; `ASTRA_BF_TX_LINK_SEED_CHECK.json` |
| CS reference stitch | 0.60/0.30 GND via `(58.88,24.638)`, 1.30 mm from the proposed CS via. Checked with the future CS seed/stub present; no pad overlap. Nearest limiting copper ADC_EMG5 has 0.2911 mm gap against 0.25 mm required. No site passed within 1.02 mm on the 0.10 mm grid; this was the single separated site found within 1.50 mm. | `ASTRA_BF_CS_GND_STITCH_ADDS.csv`; `ASTRA_BF_CS_GND_STITCH_SITES.json` |

No MCU pin-92 destination seed was found: 177 outward sites and 496 inward sites failed via-stage checks. The outward area is blocked by TP_GND_DIG and BOOT0 copper; the inward box includes WIFI_CHIP_EN, TP_MCU_BOOT0, WIFI_BOOT, SYS_EN and some VSYS blockers. See `ASTRA_BF_MCU92_INWARD_SITES.json`. This is a bounded fixed-copper result, not proof that no route is possible with local rerouting.

No fixed-copper CS source seed was found among 238 checked source-pad and track-stub sites. The new BF I2C_SDA Mid Layer 2 bus `(42.475,43.975)`→`(48.525,43.975)`, width 0.20 mm, obstructs nearby via sites along the existing CS Top track. The source pad areas also contain 3V3_DIG L5 and Bottom VSYS/testpoint obstructions. Root is adding the proven BF/BE plans to the next planner's rip inventory; CH4 and Vc_1 remain fixed.

Reference evidence: Top lies 0.0994 mm from L2 GND; L3 lies 0.1164 mm from L4 GND. Bottom lies 0.0994 mm from L5 copper. At x58.48, the nominal L5 3V0_ANA outline ends at y25.3 and GND starts at y25.6, so the CS resistor endpoint lies in the nominal gap. The nearest preexisting GND via to the new CS seed is 3.4504 mm away. The proposed nearby stitch is intended to provide a closer ground transition; **native repour and actual L2/L4 attachment must be confirmed before treating it as an established return path**.

The CSVs are planning additions, not native exports or completed routes. Any final combined route must be checked again against all its additions/deletions, then saved and verified with native geometry and DRC. A changed ADC or neighboring route can invalidate a formerly legal stitch site.
