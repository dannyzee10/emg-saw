# BF testpad relocation and MCU92 escape: planning evidence

Moving only the free Top GND pad `TP_GND_DIG` from **(56.671, 44.829) to (56.871, 44.829)** opens a local MCU92 escape in saved BF. It does **not** open an escape when the pending CS candidate is included: its Bottom trace is the remaining blocker at the otherwise clear TX via site. No CAD or native state was changed.

## Exact sources

- Compact work area: `C:/Users/PMLS/Desktop/emg-saw/.claude/worktrees/pcb-routing-0925/hardware/compact_mainboard_20260925T115919Z`.
- Saved board: `C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc`; SHA256 `e9b86b7cfb3448f1d7f6cf7053087bbcbc9a2c833a66abee8b0b98a258873e16`.
- Native BF export: `GEOMETRY_C2_6L_BF.txt`; SHA256 `95662332096e888b7d20b3e8bcd4df59af21af8ed7dd5d67409cce30bda61151`.
- Pending additions: `ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv`, 90 primitives; SHA256 `4071ec69f37d419c35ce2f5377a84d9d192c007ab40af2529981319d646ff4c9`.
- Pending deletions supplied for this review: `ASTRA_BF_FINAL_LOCAL_DELS.csv`, 46 uniquely matched primitives; SHA256 `a57a22a64436100f5de7cf431484f25aee274c3f2e82e0fdd8eb872af3516b5d`.
- Reproducible script: `../work/astra_tp_gnd_dig_move_scan.py`; initial report `ASTRA_BF_TP_GND_DIG_MOVE_SCAN.json`; joint pending-CS report `ASTRA_BF_CS_TP_GND_DIG_MOVE_SCAN.json` (`--cs`). The first report predates the script's expanded 242-site grid; its recorded original grid has 136 sites.

## Saved-BF pad-only move

The testpad is `PAD|FREE|TP_GND_DIG|GND|Top Layer`, round, 1.000 mm copper diameter, no hole, rotation 0. Its exported bounding rectangle is 1.100 mm square. These existing dimensions are translated without changing them. MCU92 is centered at (56.08, 43.238), Top, net `MCU_WIFI_UART_TX`.

With the testpad moved +0.200 mm X, this local escape clears retained BF copper, drills, board edge and keepouts:

- Through via: **(56.08, 44.30), diameter 0.45 mm, hole 0.20 mm**.
- Top track: **(56.08, 43.238) to (56.08, 44.30), width 0.20 mm**.
- Via to moved-testpad copper gap: **0.226589 mm**, against 0.200 mm required.
- Stub to moved-testpad copper gap: **0.351589 mm**, against 0.200 mm required.
- Moved-testpad copper to nearest existing drill: **0.063885 mm**; preserved rectangular bounding envelope to that drill: **0.004900 mm**. These are nonintersection checks, not invented probe or manufacturing tolerances.
- The translated envelope clears the modeled board edge, keepouts, all other Top pad envelopes and Top component bounding envelopes.

The pad already has an attached nonpolygon Top GND track, **(56.671, 44.829) to (57.5759, 44.941), width 0.25 mm** (`GEOMETRY_C2_6L_BF.txt:4857`). It terminates at the retained GND via **(57.5759, 44.941), diameter 0.60/hole 0.30 mm** (line 1194). The moved pad still intersects this track; the track and GND via need no movement or rerouting for this hypothetical +0.200 mm pad move. No other exported nonpolygon Top GND object touches the original pad.

Moving the pad +1.000 mm X is invalid: it overlaps Top `WIFI_SPI_RDY` copper and the existing GND drill. A larger displacement must not be substituted without rechecking.

## Joint pending-CS result

The joint model removes exactly the supplied deletions, including their via holes, adds all 90 pending primitives and via holes, and removes only `TP_GND_DIG` for the initial escape search. Every other retained object remains fixed. **No via-plus-Top-stub escape passed among 242 sites**, even before choosing a replacement pad location. Grid: x = 55.5 through 56.4 in 0.1 mm steps plus x = 56.08; y = 44.0 through 45.0 in 0.05 mm steps plus y = 44.275. Both 0.20 and 0.15 mm stubs were eligible where a via passed; direct and eligible vertical-then-45-degree paths were tested.

At (56.08, 44.30), the only remaining via blocker is the pending **Bottom `WIFI_SPI_CS` track (53.275, 44.025) to (58.525, 44.025), width 0.18 mm**. Its copper overlaps the 0.45 mm TX via. This is independent of the testpad move.

At (56.08, 44.60), retained `MCU_BOOT0` copper blocks the via: the via at (55.575, 45.025), diameter 0.60 mm, has only 0.1353 mm copper gap; `R_MCU_BOOT0_PD.2` has 0.0719 mm gap, both against 0.20 mm. At y = 44.80 those gaps reduce to 0.0281 and 0.0250 mm. Moving farther left also encounters the retained UART_RX escape and MCU_BOOT0 routing.

For the original TX via at (56.08, 44.30), a horizontal CS centerline at that X must be **y <= 43.785 or y >= 44.815** to provide the required 0.225 + 0.090 + 0.200 = 0.515 mm separation. This is a necessary local separation bound, not a verified CS detour. Its connecting segments and all other copper still require checking.

## Limits

This proves local modeled collisions and a conditional pad-only BF escape. It does not prove a complete TX connection or approve the joint candidate. The source exporter records native pad bounding rectangles and copper dimensions, but does not separately export explicit solder-mask settings; the original 1.100 mm envelope is preserved conservatively, without claiming it is the exact mask opening. Component envelopes screen basic access; no probe diameter or fixture specification has been assumed. Polygon fill topology, local return paths and native DRC remain outside this offline scan. The existing native RoutingVias-rule alignment requirement is unchanged.
