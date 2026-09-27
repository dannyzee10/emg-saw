# Two remaining BF opens: independent routing constraints

Native source: `GEOMETRY_C2_6L_BF.txt` and `DRC_C2_6L_BF.txt.html`. The BF independent review established unchanged Rules6/Class streams relative to the earlier native rule audit. This review performs no routing or CAD operation.

| Net | Native endpoints and existing copper | Width rule |
| --- | --- | --- |
| MCU_WIFI_UART_TX | R_WIFI_UART_TX_LINK.2 Bottom `(44.026,40.805)`, actual copper 0.45×0.45 mm; U_MCU1.92 Top `(56.08,43.238)`, actual copper 0.30×1.475 mm. No existing free tracks/vias on this net. | EMG_CONTROL priority 9: minimum 0.15, preferred 0.20, maximum 0.50 mm. |
| WIFI_SPI_CS | Existing two Top tracks, each 0.18 mm, join U_WIFI1.24 `(42.126,43.745)` to R_WIFI_CS_PD.1 `(46.68,43.2)`. Target R_SPI_CS.1 Top `(58.48,25.538)`, actual copper 0.475×0.50 mm. No existing same-net via. R_SPI_CS.2 is MCU_WIFI_CS and must remain distinct. | EMG_SPI priority 4: minimum 0.15, preferred 0.18, maximum 0.30 mm. |

The sole enabled native RoutingLayers rule applies to All/All and allows Top, Mid Layer 2, Mid Layer 4 and Bottom. Continue preserving physical L2/L4 GND planes. Existing planner L5 analog-pour reservations remain a separate planning constraint.

General same-layer copper clearance is 0.20 mm; EMG_POWER and EMG_ANALOG/ADC/REFERENCE copper pairs use 0.25 mm unless a higher-priority exact scope applies. U_MCU1 pad-to-track escape clearance is 0.15 mm only for tracks within its explicit native region. The U_MCU1 0.10 mm pad-to-pad rule is not a route or via clearance. The module antenna-boundary exception is not a signal-copper clearance waiver.

`router5.py` requires an actual pad minimum dimension of 0.50 mm for its normal filled/capped via-in-pad candidate core. Thus neither MCU_WIFI_UART_TX endpoint nor R_SPI_CS.1 qualifies; normal routing needs off-pad vias and connecting stubs. The larger U_WIFI1.24 and R_WIFI_CS_PD.1 pads can qualify, but fixed copper and drill clearances still require exact checking. Exported bounding boxes include expansion; use SX/SY plus rotation to evaluate actual copper.

The saved via-style rule remains the separately documented fixed 0.60/0.30 rule; alignment with authorized existing smaller sizes and batch via-style coverage remains a distinct pending finish step. Ordinary clearance DRC alone does not attest that rule.

For proposed reroutes, independently verify exact deletion matches, all retained same-net connections, source-to-destination connection, and any power branch's feed into the replacement. New 0.40 mm power tracks alone do not prove that retained entry tracks preserve the former power path width. Native saved geometry must match the final candidate, and DRC should remove only these requested open details without new violations or changes to pads, components, nets, rules, stack or schematic files.

## Checking helper and guidance finding

`work/astra_check_final_opens_graph.py` accepts explicit native before/adds/dels/output paths and one or both `--require-net MCU_WIFI_UART_TX` / `--require-net WIFI_SPI_CS`. It also compares retained EMG_POWER connectivity with all tracks narrower than 0.40 mm excluded. A formerly wide connection that now requires a thinner retained feed fails this extra check. The test module `test_astra_final_opens_graph` passed three fixtures: a newly required thin feed, its direct wide reinforcement, and an existing thin feed that never established a wide-path requirement. This check supplements manual junction inspection; it does not establish effective intersection widths or current capacity.

`repair.py` currently verifies guidance with whole victim groups removed. It then calls `split_group` on `LAST_PATH`, which remains the initial broad-rip path rather than the subsequent verified route. Consequently `PARTIAL=0.35` does not preserve the whole-group route feasibility proof. An immediate target no-path with no victim-first ordering exits without a reverse cascade. Existing `PARTIAL=0` disables splitting; a CS run beginning with 15 victims also needs a cascade ceiling above 15 if it is to admit additional victim groups. This is a textual explanation of the observed FINAL2 no-path, not a physical routing guarantee. No router code was changed.
