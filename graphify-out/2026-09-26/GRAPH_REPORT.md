# Graph Report - pcb-routing-0925  (2026-09-25)

## Corpus Check
- 247 files · ~1,037,272 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1926 nodes · 2970 edges · 200 communities (105 shown, 58 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 73 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cacb9911`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EmgScope
- EMG Bring-up Checkpoint Log
- ReviewWindow
- emg_plotter.py
- graphify query
- emg_bluepill/main.c
- EmgFilters
- Beihang University Logo (logo.png)
- graphify clone (GitHub)
- Patterns Library (11 production patterns)
- Token reduction benchmark
- FalkorDB export
- GraphML export
- Neo4j export
- SVG export
- Wiki export
- MVC Normalization (% MVC)
- MetricsCalculator
- Hard gate rules
- EMG SAW — HANDOFF (read this first)
- agent_map.py
- pre-commit
- DSP Engineer Playbook
- Firmware Engineer Playbook
- GUI Engineer Playbook
- Hardware Engineer Playbook
- Test Engineer Playbook
- Systems Architect Playbook (Brain Agent)
- EMG UART Protocol Specification
- Sequence Number Width Evaluation
- EMG Firmware
- src/main.c
- FrameParser
- GUI Architecture Proposal (EMG Instrument)
- EmgPlotWidget
- RecordingController
- dsp.py
- MvcDialog
- Cited Findings
- ._apply_scaling
- AmpNormDialog
- ._prompt_save_recording
- Tomorrow — Live PA0 EMG data check (CP5 "signal sanity")
- Cited Findings
- ._activate_mvc
- ._process
- _BufferedSource
- ChannelPanel
- AcquisitionModel
- Handler
- ._update_status
- router4.py
- compact_mainboard_20260925T115919Z/work/router5.py
- Lead-off calibration & validation — 2026-08-29
- Launcher
- launchers.md
- Data Pipeline — 5-Channel Simultaneous EMG Streaming (feasibility + optimal design)
- Complete Pin-by-Pin Connection Reference — AS BUILT
- 5-Channel Wireless Wearable EMG Board — Project Handoff
- PROJECT_CONTEXT.md
- Main Board — PCB Layout Rules (floorplan, stack-up, keep-outs, guard, vias)
- Main Board — Power Tree, Schematic-Level Design
- Main Board — 5-Channel Schematic (net-by-net) + BOM
- AFE Signal Chain — confirmed topology + values + 5-channel integration
- QUALITY_BAR.md
- EMG SAW — Retrospective + Competitive Roadmap
- EMG-SAW — Beihang EMG Acquisition System + GUI
- pcb_layout_2026-09-24_routing/work/router5.py
- Analog front-end PCB layout and routing requirements: AD8237 / MCP6404 / MCP6401 / VREF distribution / ADC-input RC / Hirose BK13C (5-ch sEMG main board)
- Fabrication & stack-up limits for the 4-layer JLCPCB EMG main board (80 × 45 mm, FR-4, ENIG, through vias)
- STM32U575VIT6 (LQFP100, non-SMPS): ST layout and routing requirements for U_MCU1 on the EMG main board
- ST67W611M1A6BTR (integrated PCB antenna) on the EMG main board: manufacturer layout requirements for the antenna, grounding, decoupling, 32.768 kHz crystal and SPI host interface
- grid_router.py
- router3.py
- EMG main-board PCB implementation brief — Astra
- compact_mainboard_20260925T115919Z/work/geom.py
- pcb_layout_2026-09-24_routing/work/geom.py
- compact_mainboard_20260925T115919Z/work/apply_ops_v6.pas
- tn_215701.pas
- tr_215530.pas
- ap_171624.pas
- pcb_layout_2026-09-24_routing/work/apply_ops_v6.pas
- aB_213758.pas
- apply_B.pas
- dB_212322.pas
- dC_213555.pas
- fx_214355.pas
- ab2_201729.pas
- ab3_203355.pas
- apply_ops_b2.pas
- apply_ops_b3.pas
- apply_ops_b4.pas
- apply_ops_b5.pas
- apply_ops.pas
- dA_212014.pas
- apply_ops_b1.pas
- EMG main-board placement checkpoint — 24 September 2026
- Unbroken Planes and Tight Loops Govern Routing
- Compact two-sided main board — change audit (R2)
- plan_gnd_fanout2.py
- Remote battery NTC assembly — PROTO_1_REMOTE_NTC
- plan_gnd_fanout.py
- api_test.pas
- at_210845.pas
- Next-agent checkpoint — compact main board (R2)
- apply_fp.pas
- fpB_214118.pas
- fpd_214035.pas
- gen_evidence.py
- compact_mainboard_20260925T115919Z/work/export_geometry.pas
- flip_test.pas
- ft_210529.pas
- gen_B_ops.py
- ot_211603.pas
- outline_test.pas
- Opus continuation changelog — routing revision
- pcb_layout_2026-09-24_routing/work/export_geometry.pas
- plan_bk13_escape.py
- classify_copper.py
- plan_B.py
- compact_mainboard_20260925T115919Z/work/render_area.py
- render_compare.py
- partial_status.py
- peak_mem.py
- probe_board.pas
- pcb_layout_2026-09-24_routing/work/render_area.py
- save_board.pas
- verify_readback.py
- compact_mainboard_20260925T115919Z/work/audit_plan.py
- compact_mainboard_20260925T115919Z/work/build_ops.py
- compare_pads.py
- eb_201019.pas
- export_baseline.pas
- export_bodies.pas
- flip_probe2.pas
- fp_210726.pas
- xb2_214149.pas
- xb_205224.pas
- pcb_layout_2026-09-24_routing/work/audit_plan.py
- pcb_layout_2026-09-24_routing/work/build_ops.py
- probe_bodies.pas
- probe_free_bodies.pas
- replan_pads.py
- route_quality.py
- split_plan.py
- analyze_baseline.py
- analyze_flip.py
- compare_readback.py
- list_sheet.py
- make_trial_ops.py
- compact_mainboard_20260925T115919Z/work/parse_drc.py
- render_placement.py
- repoint_prjpcb.py
- setup_kit.py
- summarize_bodies.py
- build_batch2.py
- build_rule_ops.py
- clean_partial.py
- make_router5.py
- make_writer_test.py
- pcb_layout_2026-09-24_routing/work/parse_drc.py
- render_plan.py
- render_zoom.py

## God Nodes (most connected - your core abstractions)
1. `EmgScope` - 85 edges
2. `ReviewWindow` - 36 edges
3. `EmgFilters` - 23 edges
4. `EMG main-board PCB implementation brief — Astra` - 20 edges
5. `MvcDialog` - 19 edges
6. `SimSource` - 17 edges
7. `ProcessingDialog` - 17 edges
8. `RunFixed()` - 17 edges
9. `RunFixed()` - 17 edges
10. `RunFixed()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Test Engineer (team note)` --semantically_similar_to--> `Test Engineer Agent`  [INFERRED] [semantically similar]
  team/test-engineer.md → .claude/agents/test-engineer.md
- `EMG SAW Agent Roster (agents/)` --semantically_similar_to--> `EMG SAW Agent Roster (docs/)`  [INFERRED] [semantically similar]
  agents/EMG_SAW_Agent_Roster.md → docs/EMG_SAW_Agent_Roster.md
- `DSP Engineer (team note)` --semantically_similar_to--> `DSP Engineer Agent`  [INFERRED] [semantically similar]
  team/dsp-engineer.md → .claude/agents/dsp-engineer.md
- `Firmware Engineer (team note)` --semantically_similar_to--> `Firmware Engineer Agent`  [INFERRED] [semantically similar]
  team/firmware-engineer.md → .claude/agents/firmware-engineer.md
- `GUI Engineer (team note)` --semantically_similar_to--> `GUI Engineer Agent`  [INFERRED] [semantically similar]
  team/gui-engineer.md → .claude/agents/gui-engineer.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **EMG SAW Agent Team** — claude_agents_systems_architect, claude_agents_firmware_engineer, claude_agents_gui_engineer, claude_agents_dsp_engineer, claude_agents_hardware_engineer, claude_agents_test_engineer [EXTRACTED 0.90]
- **CP4 TIM-ADC-DMA Ping-Pong Pipeline** — firmware_cp4_binary_dma_tim3, firmware_bluepill_f103_config_adc1, firmware_bluepill_f103_config_dma, firmware_cp4_binary_dma_hal_adc_convhalfcpltcallback, firmware_cp4_binary_dma_send_half, firmware_stm32_firmware_build_frame [EXTRACTED 0.90]
- **Graphify extra export formats** — _claude_skills_graphify_references_exports_wiki, _claude_skills_graphify_references_exports_neo4j, _claude_skills_graphify_references_exports_falkordb, _claude_skills_graphify_references_exports_svg, _claude_skills_graphify_references_exports_graphml, _claude_skills_graphify_references_exports_mcp [INFERRED 0.85]
- **Extraction schema rules** — _claude_skills_graphify_references_extraction_spec_subagent, _claude_skills_graphify_references_extraction_spec_confidence, _claude_skills_graphify_references_extraction_spec_confidence_score, _claude_skills_graphify_references_extraction_spec_node_id_format, _claude_skills_graphify_references_extraction_spec_semantic_similarity, _claude_skills_graphify_references_extraction_spec_hyperedges [INFERRED 0.85]
- **Query/answer flow** — _claude_skills_graphify_references_query_query, _claude_skills_graphify_references_query_path, _claude_skills_graphify_references_query_explain, _claude_skills_graphify_references_query_expansion, _claude_skills_graphify_references_query_save_result, _claude_skills_graphify_references_query_reflect [INFERRED 0.85]

## Communities (200 total, 58 thin omitted)

### Community 1 - "EMG Bring-up Checkpoint Log"
Cohesion: 0.06
Nodes (64): Graphify Trigger Config (.claude/CLAUDE.md), EMG SAW Agent Roster (agents/), Round Table Collaboration, SAFe Methodology (Epic/Feature/Story), Graphify Project Instructions (CLAUDE.md), DSP Engineer Agent, Firmware Engineer Agent, GUI Engineer Agent (+56 more)

### Community 2 - "ReviewWindow"
Cohesion: 0.06
Nodes (15): NormalizeDialog, NormalizeDialog — Noraxon MR offline Amplitude Normalization config: choose the…, ProcessingDialog, Run the Signal-Processing pipeline per channel; build display array + per-…, Open the Signal Processing pipeline builder; apply the result to the review., Populate self.mvc from the latest mvc_store.json entry (the persisted 'MVC…, Compute a per-channel reference (=100 %) from the chosen source/window, then…, Img15: % axis at the chosen range, a 100 % reference line, and the green 'peak… (+7 more)

### Community 3 - "emg_plotter.py"
Cohesion: 0.13
Nodes (12): AsciiSource, Data sources for the plotter. Every source runs a background thread that fills…, Fallback for a quick STM32 `printf("%d,%d\\n", ...)` bring-up., Synthetic sEMG: baseline noise + intermittent bursts (band-limited noise…, SerialSource, SimSource, ChannelPanel – left sidebar with per-channel information cards and MVC controls., MainController (+4 more)

### Community 4 - "graphify query"
Cohesion: 0.09
Nodes (24): graphify add (URL ingest), Watch debounce, graphify --watch folder watcher, MCP server, Confidence tiers (EXTRACTED/INFERRED/AMBIGUOUS), Confidence score rubric, Hyperedges, Node ID format (+16 more)

### Community 5 - "emg_bluepill/main.c"
Cohesion: 0.25
Nodes (14): build_frame(), ADC_HandleTypeDef, crc16_ccitt(), Error_Handler(), HAL_ADC_ConvCpltCallback(), HAL_ADC_ConvHalfCpltCallback(), main(), MX_ADC1_Init() (+6 more)

### Community 6 - "EmgFilters"
Cohesion: 0.05
Nodes (38): EmgFilters, ndarray, Moving-RMS linear envelope, sqrt(mean(x^2)) over a `win_ms` window — the…, _ac(), apply_pipeline(), compute_reference(), op_mean(), op_norm_mvc() (+30 more)

### Community 7 - "Beihang University Logo (logo.png)"
Cohesion: 1.00
Nodes (3): Beihang University Logo (logo.png), Beihang University Logo (R.png), Beihang-branded UI Header

### Community 18 - "Hard gate rules"
Cohesion: 0.18
Nodes (11): Hard gate rules, HG10 — No "done" without Daniyal approval, HG1 — Protocol integrity, HG2 — Firmware timing & delivery, HG3 — DSP correctness, HG4 — GUI robustness, HG5 — Axes & display fidelity, HG6 — Signal quality baseline (+3 more)

### Community 19 - "EMG SAW — HANDOFF (read this first)"
Cohesion: 0.15
Nodes (13): 0. How to use this handoff, 10. Push to GitHub (for your coworker), 11. Doc index, 1. Mission, 2. Quick start — open the EMG scope, 3. Current state — DONE ✅ (as of 2026-08-27), 4. Repo map, 5. What each agent did (retro) — the memory of the build (+5 more)

### Community 20 - "agent_map.py"
Cohesion: 0.83
Nodes (3): load_ownership(), main(), owner_of()

### Community 25 - "DSP Engineer Playbook"
Cohesion: 0.25
Nodes (7): Common Pitfalls, DSP Engineer Playbook, Exit State, Knowledge Base, Quality Gates, Role, Workflow

### Community 26 - "Firmware Engineer Playbook"
Cohesion: 0.25
Nodes (7): Common Pitfalls, Exit State, Firmware Engineer Playbook, Knowledge Base, Quality Gates, Role, Workflow

### Community 27 - "GUI Engineer Playbook"
Cohesion: 0.25
Nodes (7): Common Pitfalls, Exit State, GUI Engineer Playbook, Knowledge Base, Quality Gates, Role, Workflow

### Community 28 - "Hardware Engineer Playbook"
Cohesion: 0.25
Nodes (7): Common Pitfalls, Exit State, Hardware Engineer Playbook, Knowledge Base, Quality Gates, Role, Workflow

### Community 29 - "Test Engineer Playbook"
Cohesion: 0.25
Nodes (7): Common Pitfalls, Exit State, Knowledge Base, Quality Gates, Role, Test Engineer Playbook, Workflow

### Community 30 - "Systems Architect Playbook (Brain Agent)"
Cohesion: 0.29
Nodes (6): Core Workflow (Task Delegation), Quality Gates, Role, Stop-the-Line Rules, Systems Architect Playbook (Brain Agent), Token Discipline

### Community 31 - "EMG UART Protocol Specification"
Cohesion: 0.07
Nodes (29): Channel Data Format, Channel Data Format, CRC Algorithm, CRC Algorithm, EMG UART Protocol Specification, EMG UART Protocol Specification, Error Handling, Error Handling (+21 more)

### Community 32 - "Sequence Number Width Evaluation"
Cohesion: 0.22
Nodes (8): Action Items, Calculation, Context, Date, Impact, Recommendation, Sequence Number Width Evaluation, Status

### Community 33 - "EMG Firmware"
Cohesion: 0.29
Nodes (6): Build Tools, Configuration, EMG Firmware, Protocol, Status, TODO

### Community 34 - "src/main.c"
Cohesion: 0.47
Nodes (4): ADC_HandleTypeDef, crc16_ccitt(), HAL_ADC_ConvCpltCallback(), send_frame()

### Community 35 - "FrameParser"
Cohesion: 0.15
Nodes (18): crc16_ccitt(), encode_frame(), FrameParser, Wire protocol shared by the STM32 firmware and the laptop plotter. Version 1…, CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF). Matches the C code in firmware/., Build one frame. `version` = 1 for legacy 8-bit seq, 2 for 16-bit seq., Streaming parser that auto-detects protocol version per frame. Yields (seq,…, main() (+10 more)

### Community 36 - "GUI Architecture Proposal (EMG Instrument)"
Cohesion: 0.22
Nodes (8): Controller, Current State, Data Flow, GUI Architecture Proposal (EMG Instrument), Immediate Refactoring Steps, Model, Proposed Modular Architecture, View

### Community 37 - "EmgPlotWidget"
Cohesion: 0.12
Nodes (7): EmgPlotWidget, EmgPlotWidget – encapsulates all real-time plotting and spectrum views., Holds the GraphicsLayoutWidget, per-channel plots, curves, overlays, cursors,…, Show/hide the spectrum plot., Update all channel curves with new data. `data` shape (n_samples, nch)., Update onset overlay for channel c., Update spectrum curves. `psd_list` is list of arrays per channel.

### Community 38 - "RecordingController"
Cohesion: 0.17
Nodes (6): RecordingController – manages CSV recording independent of the GUI., Open a new CSV file and write metadata header., Write a chunk of raw samples to the file. `new_data` shape (n_samples, nch)., Write a marker line (preceded by #) to the file., Handles opening, writing, and closing a CSV file for raw EMG data., RecordingController

### Community 39 - "dsp.py"
Cohesion: 0.05
Nodes (65): cocontraction_index(), fatigue_trend(), iemg(), leadoff_report(), leadoff_status(), LeadoffTracker, mean_frequency(), median_frequency() (+57 more)

### Community 40 - "MvcDialog"
Cohesion: 0.09
Nodes (15): MvcDialog, MvcSaveDialog, MvcDialog — Noraxon-style MVC calibration with guided steps. Open → live RMS-…, Noraxon-style 'Save Data' step shown right after an MVC capture: name the…, Noraxon-style 'Save Data' shown after stopping a test recording: name the…, SaveRecordingDialog, _style(), _chunk() (+7 more)

### Community 41 - "Cited Findings"
Cohesion: 0.06
Nodes (33): 1. BQ24072T (UP1): IN/OUT/BAT capacitor placement, high-current paths, exposed-pad vias and via-in-pad treatment, ISET/ILIM/TMR/TS placement and quiet ground, thermal guidance, 2. GCT USB4105-GF-A (J_USB_C): which pins carry VBUS/GND, shell and stake grounding, copper/vias for the charger input current, keep-outs, 3. ESD protection layout (D_VBUS = Nexperia PESD5V0S1BA,115 SOD-323; D_CC_ESD = Nexperia PESD5V0X2UTR SOT-23), 4. MAX17048 (UP4): CELL/VDD sensing (Kelvin at the battery terminal, avoiding charge-current IR drop), VDD bypass, exposed pad, I2C pull-ups, 5. TS/NTC sensing: routing the remote 103AT-2 leads and noise on TS, Charger / USB-C input / ESD / fuel gauge / battery-NTC: PCB routing requirements (UP1 BQ24072T, J_USB_C USB4105-GF-A, D_VBUS PESD5V0S1BA, D_CC_ESD PESD5V0X2UT, UP4 MAX17048, R_TH_BAT 103AT-2), Cited Findings, Cited Findings (+25 more)

### Community 43 - "AmpNormDialog"
Cohesion: 0.12
Nodes (10): AmpNormDialog, AmpNormDialog — Noraxon MR real-time Amplitude Normalization + Smoothing…, Img1+Img4: real-time Amplitude Normalization config — smoothing algorithm +…, Headless GUI smoke test (HG4): build the branded MVC instrument at 5 channels,…, HG4: the HTML report builds (with the M3 analytics columns) without exception., Img1/Img3/Img4: the live envelope honors the smoothing algorithm + window, and…, test_amp_norm_dialog_reports_config(), test_gui_builds_and_runs_5ch() (+2 more)

### Community 44 - "._prompt_save_recording"
Cohesion: 0.15
Nodes (5): #9 Save Data step after a test recording: name it (Save & View / Save /…, Open a saved recording in the View/Review window (playback + Operations +…, Rename the just-saved CSV to include the user's name (keeps the emg_ prefix +…, Quick numeric 'view' of a saved recording (per-channel RMS / pk-pk / lead-off)., Guide the Record -> Pause -> Stop activity with a contextual step hint.

### Community 45 - "Tomorrow — Live PA0 EMG data check (CP5 "signal sanity")"
Cohesion: 0.17
Nodes (11): 0. Pre-flight (2 min), 1. Stream, 2. Resting baseline / noise (muscle relaxed), 3. DC / scale sanity (CP5), 4. Contraction / activation — the real test, 5. Fatigue (optional), 6. Capture the data, After the session (+3 more)

### Community 46 - "Cited Findings"
Cohesion: 0.06
Nodes (33): 1. TPS631000 layout guidelines, layout example and EVM: critical loops, CIN/COUT/inductor placement, LX copper, GND vias, FB and feed-forward placement, thermal copper, vias under the IC, 2. Peak inductor/switch currents at 3.3 V / 0.6 A from 3.0–4.2 V, and the resulting trace widths and via counts (1 oz outer, 0.5 oz inner), 3. TPS7A2030 (UP3) layout: capacitor placement, ground return, PSRR when fed from the switching 3V3_DIG rail, distributing 3V0_ANA to the analog bank, 4. TPS3808G33 (U_UV1, CT open) and LTC2954-1 (U_EN1): layout notes, timing pins, pull-ups, noise susceptibility, keep-away from switch nodes, 5. Separating the switching converter from sensitive analog: minimum distances, what must not run under the inductor or switch node, and whether L2 must stay unbroken under the switcher, Cited Findings, Cited Findings, Cited Findings (+25 more)

### Community 47 - "._activate_mvc"
Cohesion: 0.18
Nodes (4): Persist the current per-channel MVC to mvc_store.json (the reusable 'MVC…, #6: after MVC, switch the scope to %MVC (y-axis becomes %) and confirm., Noraxon-style EMG Baseline Check: report per-channel resting RMS AND the…, Big in-window banner below the toolbar (child widget -> safe teardown, no modal…

### Community 48 - "._process"
Cohesion: 0.28
Nodes (3): Envelope smoothing per the configured Amplitude-Norm algorithm + window. `base`…, Absolute volts in -> displayed volts out (coupling + optional filters)., Highlight active (contraction) samples in white on top of the trace.

### Community 49 - "_BufferedSource"
Cohesion: 0.15
Nodes (6): _BufferedSource, _open_serial(), ndarray, Open the serial port exactly like a plain read that is known to work here. Open…, Common ring-collection + thread plumbing., Return all sample-sets collected since the last call, shape (n, nch).

### Community 50 - "ChannelPanel"
Cohesion: 0.38
Nodes (3): ChannelPanel, Encapsulates channel cards with muscle name, RMS/pk-pk labels, progress bars,…, Set the per-channel electrode status dot: 'good' | 'poor' | 'open'.

### Community 51 - "AcquisitionModel"
Cohesion: 0.29
Nodes (3): AcquisitionModel, Read new samples from the underlying source and update ring buffer., QObject

### Community 54 - "router4.py"
Cohesion: 0.11
Nodes (29): Render router4's view of one unrouted connection: free cells per layer, entry…, Plan the pour stage (offline; Altium DRC is the authority). Emits…, allowed_layers(), astar(), cell_xy(), cls(), edt(), end_copper() (+21 more)

### Community 55 - "compact_mainboard_20260925T115919Z/work/router5.py"
Cohesion: 0.13
Nodes (30): allowed_layers(), astar(), cell_xy(), cls(), comp_nodes(), component(), edt(), end_copper() (+22 more)

### Community 56 - "Lead-off calibration & validation — 2026-08-29"
Cohesion: 0.40
Nodes (4): Calibrated thresholds (`dsp.leadoff_report`), Findings, Lead-off calibration & validation — 2026-08-29, Notes

### Community 59 - "Data Pipeline — 5-Channel Simultaneous EMG Streaming (feasibility + optimal design)"
Cohesion: 0.22
Nodes (8): 1. The data rate is tiny, 2. "All 5 at the same time" is easy on the U575, 3. What actually makes it "work well" (the 4 keys), 4. Better option? Wi-Fi vs BLE vs USB, 5. The one honest risk + the fix, 6. Recommended optimal config, 7. This is exactly what the dev-board step (Step 3) proves, Data Pipeline — 5-Channel Simultaneous EMG Streaming (feasibility + optimal design)

### Community 60 - "Complete Pin-by-Pin Connection Reference — AS BUILT"
Cohesion: 0.15
Nodes (12): 10. FFC to each electrode board (13-pin, GND-interleaved), 11. Still to do on the schematic, 1. J1 — USB4105-GF-A-060 (USB-C receptacle, 16 contacts + 8 dummy), 2. UP1 — MCP73831T-2ACI/MC (Li-Po charger, **DFN-8** — *not* the SOT-23-5 pinout), 3. J_Li-Po (Header 2) + Q1 — DMP2045U-7 (reverse-polarity, SOT-23 P-MOS), 4. UP3 — TPS2116DRLR (power mux, SOT-583) — USB priority, 5. UP4 — TPS631000DRLR (buck-boost, SOT-583) → 3V3_DIG = 3.30 V, 6. UP5 — TPS7A2030PDBVR (analog LDO, SOT-23-5) → 3V3_ANA = 3.00 V (+4 more)

### Community 61 - "5-Channel Wireless Wearable EMG Board — Project Handoff"
Cohesion: 0.18
Nodes (10): 1. What this board is, 2. Documents in this folder, 3. Architecture decisions (and why), 4. Timeline of what was done, 5-Channel Wireless Wearable EMG Board — Project Handoff, 5. The review that changed the design, 6. Open items before design freeze, 7. Safety position (research device, not certified) (+2 more)

### Community 62 - "PROJECT_CONTEXT.md"
Cohesion: 0.20
Nodes (9): Architecture (locked pipeline), Current state — DONE ✅ (as of 2026-08-26), Locked gotchas (each cost hours — do NOT rediscover), Locked hardware facts, Locked wire protocol, Project identity, Roadmap, Signal facts (+1 more)

### Community 63 - "Main Board — PCB Layout Rules (floorplan, stack-up, keep-outs, guard, vias)"
Cohesion: 0.17
Nodes (11): 10. Layout review checklist (I'll check each snapshot against this), 1. Stack-up — YES, 4-layer (2-layer cannot do Wi-Fi + µV EMG), 2. Floorplan — where everything goes, 3. Placement rules per block, 4. Keep-outs, 5. Ground = ONE solid plane, separation by placement, 6. Guard ring (per channel), 7. Decoupling & vias (+3 more)

### Community 64 - "Main Board — Power Tree, Schematic-Level Design"
Cohesion: 0.18
Nodes (10): 0. Rail decisions — REVISED 2026-09-05, 1. USB-C input + protection, 2. Charger — MCP73831, 3. Battery + reverse-polarity + power-path mux, 4. Buck-boost pre-regulator — TPS631000 → 3V3_DIG (3.5 V), 5. Analog LDO — TPS7A2033 → 3V3_ANA (3.3 V, fixed), 6. Fuel gauge — MAX17048 (on the battery node), 7. Power-section BOM (subtotal) (+2 more)

### Community 65 - "Main Board — 5-Channel Schematic (net-by-net) + BOM"
Cohesion: 0.22
Nodes (8): A. Per-channel AFE  (replicate ×5), B. Shared analog blocks (once for all 5 channels) — **DRL-free, see `02` decision**, C. STM32U575AII6Q  (ADC + host; set exact pins in CubeMX), D. ST67W611M1-B  (Wi-Fi/BLE module; pins per ST datasheet / B2413 ref), E. Connectors, F. Consolidated BOM (main board), G. Verify, Main Board — 5-Channel Schematic (net-by-net) + BOM

### Community 66 - "AFE Signal Chain — confirmed topology + values + 5-channel integration"
Cohesion: 0.29
Nodes (6): AFE Signal Chain — confirmed topology + values + 5-channel integration, Amp count after the change — packs perfectly into 3 quads, DECISION 2026-09-04 — **DRL REMOVED** (grounded reference instead), Open items, Per-channel chain (proven — reuse exactly), Shared blocks on the main board (generate once for all 5 ch)

### Community 67 - "QUALITY_BAR.md"
Cohesion: 0.22
Nodes (3): Authority, Gate reference, Supporting rules (a pattern of violations becomes blocking)

### Community 68 - "EMG SAW — Retrospective + Competitive Roadmap"
Cohesion: 0.22
Nodes (9): EMG SAW — Retrospective + Competitive Roadmap, Next STM32 upgrade — all 15 electrodes (deferred; needs more/faster ADC), Now — Blue Pill, Channel 1, 3 electrodes (no mux, reuses existing software), Part 1 — What each agent shipped (retro of the build), Part 2 — Remaining goals per agent (near-term), Part 3 — Where we stand vs Delsys & Noraxon, Part 4 — The "win" roadmap (prioritized), Part 5 — Electrode lead-off / integrity plan (+1 more)

### Community 69 - "EMG-SAW — Beihang EMG Acquisition System + GUI"
Cohesion: 0.33
Nodes (6): Architecture, EMG-SAW — Beihang EMG Acquisition System + GUI, Quick start, Repo, Status, What it does

### Community 70 - "pcb_layout_2026-09-24_routing/work/router5.py"
Cohesion: 0.13
Nodes (30): allowed_layers(), astar(), cell_xy(), cls(), comp_nodes(), component(), edt(), end_copper() (+22 more)

### Community 71 - "Analog front-end PCB layout and routing requirements: AD8237 / MCP6404 / MCP6401 / VREF distribution / ADC-input RC / Hirose BK13C (5-ch sEMG main board)"
Cohesion: 0.07
Nodes (26): Analog front-end PCB layout and routing requirements: AD8237 / MCP6404 / MCP6401 / VREF distribution / ADC-input RC / Hirose BK13C (5-ch sEMG main board), Cited Findings, Cited Findings, Cited Findings, Cited Findings, Cited Findings, Gaps, Gaps (+18 more)

### Community 72 - "Fabrication & stack-up limits for the 4-layer JLCPCB EMG main board (80 × 45 mm, FR-4, ENIG, through vias)"
Cohesion: 0.07
Nodes (26): Cited Findings, Cited Findings, Cited Findings, Cited Findings, Cited Findings, Fabrication & stack-up limits for the 4-layer JLCPCB EMG main board (80 × 45 mm, FR-4, ENIG, through vias), Gaps, Gaps (+18 more)

### Community 73 - "STM32U575VIT6 (LQFP100, non-SMPS): ST layout and routing requirements for U_MCU1 on the EMG main board"
Cohesion: 0.07
Nodes (26): 1. AN5373 (current revision): decoupling per VDD/VSS pair, VCAP, VDDA/VREF+, VBAT, VDDUSB/VDDIO2, NRST/BOOT0 and the PCB-layout section, 2. DS13737: LQFP100 pinout facts and electrical limits that matter for routing, 3. AN2834 and U5 ADC data: analog input routing, separation from digital, RC at the pin, VREF+ decoupling, ground return, 4. SWD routing and SPI-master routing (series termination, trace length), 5. ST reference hardware: how decoupling and VCAP are actually placed on 4-layer boards, Cited Findings, Cited Findings, Cited Findings (+18 more)

### Community 74 - "ST67W611M1A6BTR (integrated PCB antenna) on the EMG main board: manufacturer layout requirements for the antenna, grounding, decoupling, 32.768 kHz crystal and SPI host interface"
Cohesion: 0.07
Nodes (26): 1. Datasheet, application note and user manual: antenna keep-out, module location, ground plane, ground under the module, GND vias, decoupling, traces under the module, 2. ST wiki "Connectivity:ST67W611M1_Antenna_and_RF" and related ST wiki pages: every layout rule, figure and dimension, and any statement about stitching vias near the antenna, 3. ST reference and evaluation boards using ST67W611M1 (STDES-67W61BU-U5 / B2413; X-NUCLEO-67W61M1 / MB2230): what their layout does around the module, 4. 32.768 kHz crystal layout (Epson FC-135 Q13FC13500003 on ST67 pins 13/14): trace length, guard ring grounding, no signals underneath, parasitic capacitance, 5. SPI host interface: clock frequency used by the ST host stack, series termination, trace length and impedance, return path; UART, BOOT and CHIP_EN notes, Cited Findings, Cited Findings, Cited Findings (+18 more)

### Community 75 - "grid_router.py"
Cohesion: 0.13
Nodes (13): astar(), end_copper(), end_nodes(), main(), maps(), parse_conn(), Rule-aware windowed grid router for the remaining connections (offline planner;…, all copper as (geom, net, layerset, wide, finepad) with a spatial index; new… (+5 more)

### Community 76 - "router3.py"
Cohesion: 0.18
Nodes (22): allowed_layers(), astar(), cell_xy(), cls(), edt(), end_copper(), end_nodes(), layer_cost() (+14 more)

### Community 77 - "EMG main-board PCB implementation brief — Astra"
Cohesion: 0.10
Nodes (20): 10. STM32 and ADC details, 11. ST67, SPI, crystal, and antenna, 12. USB, charger, converter, gauge, and remote NTC, 13. Copper pours, vias, and return paths, 14. Test access and connector serviceability, 15. BK13 mechanical contract, 16. Following routing stage: sequence and checks, 17. Verification and honest acceptance criteria (+12 more)

### Community 78 - "compact_mainboard_20260925T115919Z/work/geom.py"
Cohesion: 0.14
Nodes (13): base_clr(), in_zone(), Index, _inside(), load(), Obj, pad_poly(), Shared offline geometry/rule model for planning and pre-write verification.… (+5 more)

### Community 79 - "pcb_layout_2026-09-24_routing/work/geom.py"
Cohesion: 0.14
Nodes (13): base_clr(), in_zone(), Index, _inside(), load(), Obj, pad_poly(), Shared offline geometry/rule model for planning and pre-write verification.… (+5 more)

### Community 80 - "compact_mainboard_20260925T115919Z/work/apply_ops_v6.pas"
Cohesion: 0.29
Nodes (19): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule() (+11 more)

### Community 81 - "tn_215701.pas"
Cohesion: 0.29
Nodes (19): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule() (+11 more)

### Community 82 - "tr_215530.pas"
Cohesion: 0.29
Nodes (19): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule() (+11 more)

### Community 83 - "ap_171624.pas"
Cohesion: 0.29
Nodes (19): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule() (+11 more)

### Community 84 - "pcb_layout_2026-09-24_routing/work/apply_ops_v6.pas"
Cohesion: 0.29
Nodes (19): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule() (+11 more)

### Community 85 - "aB_213758.pas"
Cohesion: 0.23
Nodes (18): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+10 more)

### Community 86 - "apply_B.pas"
Cohesion: 0.23
Nodes (18): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+10 more)

### Community 87 - "dB_212322.pas"
Cohesion: 0.23
Nodes (18): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+10 more)

### Community 88 - "dC_213555.pas"
Cohesion: 0.23
Nodes (18): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+10 more)

### Community 89 - "fx_214355.pas"
Cohesion: 0.23
Nodes (18): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+10 more)

### Community 90 - "ab2_201729.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 91 - "ab3_203355.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 92 - "apply_ops_b2.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 93 - "apply_ops_b3.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 94 - "apply_ops_b4.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 95 - "apply_ops_b5.pas"
Cohesion: 0.28
Nodes (18): AddPoly(), CloseTo(), CountItems(), Counts(), Fail(), FindNet(), FindRule(), FindTrack() (+10 more)

### Community 96 - "apply_ops.pas"
Cohesion: 0.32
Nodes (17): AddCutout(), AddPoly(), CloseTo(), CountItems(), Counts(), FindNet(), FindRule(), FindTrack() (+9 more)

### Community 97 - "dA_212014.pas"
Cohesion: 0.26
Nodes (16): CloseTo(), Fail(), FindComp(), FindKeepout(), FindPoly(), FindRule(), FindTrack(), FindVia() (+8 more)

### Community 98 - "apply_ops_b1.pas"
Cohesion: 0.31
Nodes (16): AddPoly(), CloseTo(), CountItems(), Counts(), FindNet(), FindRule(), FindTrack(), Fld() (+8 more)

### Community 99 - "EMG main-board placement checkpoint — 24 September 2026"
Cohesion: 0.13
Nodes (13): Placement checkpoint files, 10. Deliverable status, 11. Native image package — 24 September 2026, 1. Open this working revision, 2. Actual physical-board partition and assembly, 3. Changes and preservation, 4. Verification evidence and its dates, 5. Placement, stack and rule decisions (+5 more)

### Community 100 - "Unbroken Planes and Tight Loops Govern Routing"
Cohesion: 0.15
Nodes (12): A 205× gain makes VREF taps as sensitive as electrode inputs, Charger, USB-C and ESD belong in one connector-edge power zone, Conclusion, Every return path depends on an unbroken L2 and L4, LDO and supervisors, Ordering the wrong JLC stack would shift impedance by 40 %, Six schematic issues that no amount of routing can fix, Stop-the-line checks in review order (+4 more)

### Community 101 - "Compact two-sided main board — change audit (R2)"
Cohesion: 0.17
Nodes (11): 10. Open issues (ranked), 1. Source recovery and protection, 2. Native capability proof (disposable copies only), 3. Baseline A measurement, 4. What changed in candidate B, 5. Verification (saved state), 6. Why not 70 × 40 (limiting objects) — candidate C not attempted, 7. Return-path strategy (R2 §8, option A retained) (+3 more)

### Community 102 - "plan_gnd_fanout2.py"
Cohesion: 0.22
Nodes (6): connected(), near_pad(), GND fanout v2 on the shared rule model (true copper, rule priorities, BK13 plan…, first VALID via position along each of 24 rays (true copper, rule model); best…, pad already reaches a GND via directly or through an existing top GND track., search()

### Community 103 - "Remote battery NTC assembly — PROTO_1_REMOTE_NTC"
Cohesion: 0.22
Nodes (8): Cell attachment and wiring, Electrical and physical arrangement, Installation and charger checks, Open qualification items, Procurement and assembly reconciliation, Remote battery NTC assembly — PROTO_1_REMOTE_NTC, Required sensor and manufacturer limits, Termination and strain relief

### Community 104 - "plan_gnd_fanout.py"
Cohesion: 0.31
Nodes (6): clear(), clr_for(), clr_obs(), connected(), padrect(), Plan GND fanout: one short top-layer stub + 0.6/0.3 via per unconnected top-…

### Community 105 - "api_test.pas"
Cohesion: 0.52
Nodes (6): Corner(), FirstOf(), Line(), MM(), RunFixed(), Say()

### Community 106 - "at_210845.pas"
Cohesion: 0.52
Nodes (6): Corner(), FirstOf(), Line(), MM(), RunFixed(), Say()

### Community 107 - "Next-agent checkpoint — compact main board (R2)"
Cohesion: 0.33
Nodes (5): Completed operations (25 Sep 2026), Next-agent checkpoint — compact main board (R2), Next authorized step (after the user's review), Open this, Tooling (all in `work/`)

### Community 108 - "apply_fp.pas"
Cohesion: 0.67
Nodes (5): Fld(), MM(), Num(), RunFixed(), Say()

### Community 109 - "fpB_214118.pas"
Cohesion: 0.67
Nodes (5): Fld(), MM(), Num(), RunFixed(), Say()

### Community 110 - "fpd_214035.pas"
Cohesion: 0.67
Nodes (5): Fld(), MM(), Num(), RunFixed(), Say()

### Community 112 - "compact_mainboard_20260925T115919Z/work/export_geometry.pas"
Cohesion: 0.80
Nodes (4): MM(), NetOf(), RectS(), RunFixed()

### Community 113 - "flip_test.pas"
Cohesion: 0.80
Nodes (4): Dump(), FindC(), MM(), RunFixed()

### Community 114 - "ft_210529.pas"
Cohesion: 0.80
Nodes (4): Dump(), FindC(), MM(), RunFixed()

### Community 115 - "gen_B_ops.py"
Cohesion: 0.40
Nodes (3): gvec(), Generate work/B_OPS.txt for apply_B.pas from the verified plan…, translation vector of a component that stays on its side, else None

### Community 116 - "ot_211603.pas"
Cohesion: 0.80
Nodes (4): MM(), RunFixed(), Say(), SetSeg()

### Community 117 - "outline_test.pas"
Cohesion: 0.80
Nodes (4): MM(), RunFixed(), Say(), SetSeg()

### Community 118 - "Opus continuation changelog — routing revision"
Cohesion: 0.40
Nodes (4): 24 Sep 2026, 25 Sep 2026 (resumed; this copy lives in worktree `.claude/worktrees/pcb-routing-0925`, branch `pcb-routing-0925`), Method, Opus continuation changelog — routing revision

### Community 119 - "pcb_layout_2026-09-24_routing/work/export_geometry.pas"
Cohesion: 0.80
Nodes (4): MM(), NetOf(), RectS(), RunFixed()

### Community 120 - "plan_bk13_escape.py"
Cohesion: 0.40
Nodes (3): pattern(), BK13 (0.35 mm pitch) socket escape pattern, identical for J_FPC1..5. Top row 1…, v2: keepout-clearance-correct (0.13 mm to the between-row keepout), 0.15 mm…

### Community 124 - "render_compare.py"
Cohesion: 0.67
Nodes (3): board(), draw(), Same-scale baseline-vs-candidate renders and an X-ray projection, from saved…

### Community 126 - "peak_mem.py"
Cohesion: 0.67
Nodes (3): peak_mb(), PMC, Run a script via runpy and print the Windows peak working set on exit (no…

### Community 127 - "probe_board.pas"
Cohesion: 0.83
Nodes (3): MM(), NetOf(), RunFixed()

### Community 129 - "save_board.pas"
Cohesion: 1.00
Nodes (3): Counts(), RunFixed(), Say()

### Community 130 - "verify_readback.py"
Cohesion: 0.67
Nodes (3): load(), Readback check after a native write: expected end state = BEFORE - deletions +…, tkey()

## Knowledge Gaps
- **433 isolated node(s):** `0. How to use this handoff`, `1. Mission`, `2. Quick start — open the EMG scope`, `3. Current state — DONE ✅ (as of 2026-08-27)`, `4. Repo map` (+428 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 829 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EmgScope` connect `EmgScope` to `ReviewWindow`, `emg_plotter.py`, `EmgPlotWidget`, `EmgFilters`, `dsp.py`, `MvcDialog`, `RecordingController`, `._apply_scaling`, `AmpNormDialog`, `._prompt_save_recording`, `._activate_mvc`, `._process`, `ChannelPanel`, `AcquisitionModel`, `._update_status`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `ReviewWindow` connect `ReviewWindow` to `EmgScope`, `emg_plotter.py`, `EmgFilters`, `dsp.py`, `._prompt_save_recording`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `EmgFilters` connect `EmgFilters` to `EmgScope`, `ReviewWindow`, `emg_plotter.py`, `dsp.py`, `MvcDialog`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `EmgScope` (e.g. with `EmgFilters` and `LeadoffTracker`) actually correct?**
  _`EmgScope` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ReviewWindow` (e.g. with `EmgScope` and `EmgFilters`) actually correct?**
  _`ReviewWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `EmgFilters` (e.g. with `EmgScope` and `MvcDialog`) actually correct?**
  _`EmgFilters` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MvcDialog` (e.g. with `EmgScope` and `EmgFilters`) actually correct?**
  _`MvcDialog` has 2 INFERRED edges - model-reasoned connections that need verification._