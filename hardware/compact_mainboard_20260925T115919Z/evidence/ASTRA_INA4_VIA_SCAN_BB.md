# INA4 pin-3 through-via feasibility — saved state BB

**No legal site was found** for a 0.45/0.20 mm through via at x=51.4251 mm, scanning y=15.30…16.40 mm in 0.05 mm steps. All 23 sites overlap Bottom pad `CL_4-1` (`NetCL_4_1`). Each also lies only **0.1501 mm** from Bottom pad `CL_4-2` (`INA_OUT_4`), below the 0.25 mm rule.

The most promising positions, y=15.65 and 15.70 mm, have **only these two Bottom-pad blockers**. Their hole lies inside the Top INA4-3 pad; the 0.45 mm annulus overhangs the 0.35 mm-wide pad. Adjacent Top INA4 pad clearances are approximately 0.2502/0.2503 mm, so the Top pin pitch itself passes the existing 0.25 mm model. The Bottom capacitor prevents a through via regardless of the router's narrow-pad VIP gate.

At the pin center (51.4251,15.8500), two L3 GND tracks also block the site: both have approximately 0.142376 mm copper clearance versus 0.25 mm required. The first runs (51.725,16.175)→(53.475,16.175), the second (50.525,17.375)→(51.725,16.175).

All 23 candidates pass modeled drill spacing, board-edge clearance and keepout overlap checks. Lower positions additionally encounter Top `Va_4` and L3 `Vservo_4`; upper positions encounter L3 GND, Bottom `NetCL_4_1`, then L5 `3V0_ANA` and Top `NetINA4_2`.

The check used `G.Index` with every existing BB object fixed and the current BK13/class clearances; it did not rip copper, move parts, edit router policy or modify CAD. Full candidate coordinates, primitive source records, distances and blockers are in [ASTRA_INA4_VIA_SCAN_BB.json](ASTRA_INA4_VIA_SCAN_BB.json). The scan ran in 2.26 seconds. Reproduce with:

```text
python astra_scan_ina4_via.py --geometry ../evidence/GEOMETRY_C2_6L_BB.txt --output ../evidence/ASTRA_INA4_VIA_SCAN_BB.json
```

A placement alternative involving `CL_4` could be investigated; moving only the Top input resistors cannot remove these particular Bottom-pad blockers. This is a via-site finding, not a complete routing proposal. Plane repour and native DRC remain necessary for any actual change.
