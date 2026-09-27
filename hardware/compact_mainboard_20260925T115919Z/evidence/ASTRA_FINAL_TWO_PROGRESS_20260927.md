# Final two routes — in progress, 27 Sep 2026

User task: complete both MCU_WIFI_UART_TX and WIFI_SPI_CS.

Saved native PCB is STILL BF, SHA256 E9B86B7CFB3448F1D7F6CF7053087BBCBC9A2C833A66ABEE8B0B98A258873E16. No routing applied this turn yet. Altium reopened PID11664; ASTRA_OPEN_BG.txt confirms correct PCB unmodified. Backup source BF in ASTRA_BG_BEFORE_20260927 (PCB, eight SchDocs, PrjPcb, hashes).

CS candidate found by ASTRA_BF_FINAL_LOCAL (345s; only CS solved). Raw87adds46dels is NOT approved: power-feed regression. Do not apply OPS_BG_CS_TRIAL, OPS_BG_CS_READY, raw or WITH_SEED plans. Root exact checks passed geometry only, not power preservation.

Independent agent /root/routing_handoff_check is repairing that candidate. Latest planning additions ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv (90 rows) center MCU6 feed at y39.000 with0.40mm and add0.40 Top bridge(47.075,42.375)->(47.275,42.575)->(48.675,42.575). This restores real MCU100 supply branch; two x52.675 wide dangling stubs under review for explicit pruning. Power verifier checks original-width connectivity and actual source/load thresholds. Candidate remains UNAPPLIED.

Seed CSVs proved legal at BF: CS target .45/.20via58.38,25.838 withshortTopstub; UART link .45/.20via44.026,40.805. Neither seed applied. CS route does not require either seed; raw CS graph already passes connectivity. Ground candidate near CS seed58.88,24.638 unused.

Agent child /root/routing_handoff_check/via_api_search found FREE GND pad TP_GND_DIG move+0.20X (56.671,44.829)->(56.871,44.829) opens MCU92 Top .20stub to .45/.20via56.08,44.30. Existing GND track/pad contact retained. BUT candidate CS Bottom track y44.025,x53.275..58.525 collides with that throughvia. Child is testing alternatives against post-CS candidate including possibly y44.6..44.8 withsmallpadshift. No pad or CAD change yet.

Native scripts already generated: astra_opbg_220654 (RUN), astra_apbg_220654 (NOT RUN; references currently unapproved OPS_BG_CS_READY), astra_dbg_220655 and astra_gbg_220655 (NOT RUN). Generate a new final apply script/ops after approval; use existing DRC/export scripts once final BG saved.

Planner changes actually made (not CAD): repair.py now uses verified r2 path for partial rip-up; astra_route_seed.py honors EXTRA_PLANS, validates basenames, records manifest. Nine tests passed; ASTRA_GUIDED_PATH_FIX.md/.patch. Agent gloss_guard completed. Recent accepted trace inventory requires EXTRA_PLANS=ASTRA_MCU_RX_REINFORCED_ADDS,ASTRA_UART_READY_ADDS. CH4/Vc1 copper remains fixed. Code graph refresh pending.

No offline routing process remains. Root owns all CAD writers. Read agents/new evidence before proceeding. Do not claim either route saved until fresh native apply/save/reopen/DRC and geometry proofs complete.
