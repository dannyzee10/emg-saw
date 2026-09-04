# Graph Report - emg-saw  (2026-09-04)

## Corpus Check
- 104 files · ~82,060 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 865 nodes · 1322 edges · 68 communities (46 shown, 18 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 69 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e3476274`
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
- ask
- ._apply_scaling
- AmpNormDialog
- ._prompt_save_recording
- Tomorrow — Live PA0 EMG data check (CP5 "signal sanity")
- emg_features.py
- ._activate_mvc
- ._process
- _BufferedSource
- ChannelPanel
- AcquisitionModel
- Handler
- ._update_status
- MainController
- _open_serial
- Lead-off calibration & validation — 2026-08-29
- Launcher
- launchers.md
- Features and how to explain them (intent -> answer -> action)
- EMG-SAW_Weekly_Report_2026-08-28_to_09-03_da066e19.md
- EMG Research-Centre — Web Front-End (webapp/)
- Handler
- PROJECT_CONTEXT.md
- QUALITY_BAR.md
- EMG SAW — Retrospective + Competitive Roadmap
- EMG-SAW — Beihang EMG Acquisition System + GUI

## God Nodes (most connected - your core abstractions)
1. `EmgScope` - 85 edges
2. `ReviewWindow` - 36 edges
3. `EmgFilters` - 23 edges
4. `MvcDialog` - 19 edges
5. `SimSource` - 17 edges
6. `ProcessingDialog` - 17 edges
7. `EmgPlotWidget` - 16 edges
8. `leadoff_status()` - 15 edges
9. `EMG UART Protocol Specification` - 15 edges
10. `mean_frequency()` - 14 edges

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

## Communities (68 total, 18 thin omitted)

### Community 1 - "EMG Bring-up Checkpoint Log"
Cohesion: 0.06
Nodes (64): Graphify Trigger Config (.claude/CLAUDE.md), EMG SAW Agent Roster (agents/), Round Table Collaboration, SAFe Methodology (Epic/Feature/Story), Graphify Project Instructions (CLAUDE.md), DSP Engineer Agent, Firmware Engineer Agent, GUI Engineer Agent (+56 more)

### Community 2 - "ReviewWindow"
Cohesion: 0.06
Nodes (15): NormalizeDialog, NormalizeDialog — Noraxon MR offline Amplitude Normalization config: choose the…, ProcessingDialog, Run the Signal-Processing pipeline per channel; build display array + per-…, Open the Signal Processing pipeline builder; apply the result to the review., Populate self.mvc from the latest mvc_store.json entry (the persisted 'MVC…, Compute a per-channel reference (=100 %) from the chosen source/window, then…, Img15: % axis at the chosen range, a 100 % reference line, and the green 'peak… (+7 more)

### Community 3 - "emg_plotter.py"
Cohesion: 0.20
Nodes (9): AsciiSource, Data sources for the plotter. Every source runs a background thread that fills…, Fallback for a quick STM32 `printf("%d,%d\\n", ...)` bring-up., Synthetic sEMG: baseline noise + intermittent bursts (band-limited noise…, SerialSource, SimSource, main(), Real-time EMG OSCILLOSCOPE + recorder for an STM32-based sensor. Bench-scope /… (+1 more)

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
Cohesion: 0.14
Nodes (6): EmgPlotWidget, Holds the GraphicsLayoutWidget, per-channel plots, curves, overlays, cursors,…, Show/hide the spectrum plot., Update all channel curves with new data. `data` shape (n_samples, nch)., Update onset overlay for channel c., Update spectrum curves. `psd_list` is list of arrays per channel.

### Community 38 - "RecordingController"
Cohesion: 0.17
Nodes (6): RecordingController – manages CSV recording independent of the GUI., Open a new CSV file and write metadata header., Write a chunk of raw samples to the file. `new_data` shape (n_samples, nch)., Write a marker line (preceded by #) to the file., Handles opening, writing, and closing a CSV file for raw EMG data., RecordingController

### Community 39 - "dsp.py"
Cohesion: 0.06
Nodes (56): cocontraction_index(), fatigue_trend(), iemg(), leadoff_report(), leadoff_status(), LeadoffTracker, mean_frequency(), median_frequency() (+48 more)

### Community 40 - "MvcDialog"
Cohesion: 0.09
Nodes (15): MvcDialog, MvcSaveDialog, MvcDialog — Noraxon-style MVC calibration with guided steps. Open → live RMS-…, Noraxon-style 'Save Data' step shown right after an MVC capture: name the…, Noraxon-style 'Save Data' shown after stopping a test recording: name the…, SaveRecordingDialog, _style(), _chunk() (+7 more)

### Community 41 - "ask"
Cohesion: 0.07
Nodes (24): ask(), Chat, _load_config(), main(), Michael — a one-click desktop chat window for the EMG lab assistant. Double-…, Env wins; then michael/michael.conf (KEY=value); then a localhost default., A small scrolling EMG trace shown while Michael thinks — a relaxed baseline…, _reachable() (+16 more)

### Community 42 - "._apply_scaling"
Cohesion: 0.14
Nodes (3): Img1+Img4: real-time Amplitude Normalization config — smoothing algorithm +…, Img2: real-time processing pipeline for the RMS-env view (Available ->…, % MVC target line + tolerance band (hold-a-target fatigue biofeedback). Only…

### Community 43 - "AmpNormDialog"
Cohesion: 0.14
Nodes (9): AmpNormDialog, AmpNormDialog — Noraxon MR real-time Amplitude Normalization + Smoothing…, Headless GUI smoke test (HG4): build the branded MVC instrument at 5 channels,…, HG4: the HTML report builds (with the M3 analytics columns) without exception., Img1/Img3/Img4: the live envelope honors the smoothing algorithm + window, and…, test_amp_norm_dialog_reports_config(), test_gui_builds_and_runs_5ch(), test_live_smoothing_algorithms_and_pipeline() (+1 more)

### Community 44 - "._prompt_save_recording"
Cohesion: 0.15
Nodes (5): #9 Save Data step after a test recording: name it (Save & View / Save /…, Open a saved recording in the View/Review window (playback + Operations +…, Rename the just-saved CSV to include the user's name (keeps the emg_ prefix +…, Quick numeric 'view' of a saved recording (per-channel RMS / pk-pk / lead-off)., Guide the Record -> Pause -> Stop activity with a contextual step hint.

### Community 45 - "Tomorrow — Live PA0 EMG data check (CP5 "signal sanity")"
Cohesion: 0.17
Nodes (11): 0. Pre-flight (2 min), 1. Stream, 2. Resting baseline / noise (muscle relaxed), 3. DC / scale sanity (CP5), 4. Contraction / activation — the real test, 5. Fatigue (optional), 6. Capture the data, After the session (+3 more)

### Community 46 - "emg_features.py"
Cohesion: 0.29
Nodes (9): _bp_env(), classify(), gather(), load(), main(), median_freq(), mvc_ref(), Return (band-passed signal, RMS envelope in volts). (+1 more)

### Community 47 - "._activate_mvc"
Cohesion: 0.18
Nodes (4): Persist the current per-channel MVC to mvc_store.json (the reusable 'MVC…, #6: after MVC, switch the scope to %MVC (y-axis becomes %) and confirm., Noraxon-style EMG Baseline Check: report per-channel resting RMS AND the…, Big in-window banner below the toolbar (child widget -> safe teardown, no modal…

### Community 48 - "._process"
Cohesion: 0.22
Nodes (3): Envelope smoothing per the configured Amplitude-Norm algorithm + window. `base`…, Absolute volts in -> displayed volts out (coupling + optional filters)., Highlight active (contraction) samples in white on top of the trace.

### Community 49 - "_BufferedSource"
Cohesion: 0.22
Nodes (4): _BufferedSource, ndarray, Common ring-collection + thread plumbing., Return all sample-sets collected since the last call, shape (n, nch).

### Community 50 - "ChannelPanel"
Cohesion: 0.28
Nodes (4): ChannelPanel, ChannelPanel – left sidebar with per-channel information cards and MVC controls., Encapsulates channel cards with muscle name, RMS/pk-pk labels, progress bars,…, Set the per-channel electrode status dot: 'good' | 'poor' | 'open'.

### Community 51 - "AcquisitionModel"
Cohesion: 0.22
Nodes (4): AcquisitionModel, AcquisitionModel — wraps a data source (SerialSource / SimSource / AsciiSource)…, Read new samples from the underlying source and update ring buffer., QObject

### Community 56 - "Lead-off calibration & validation — 2026-08-29"
Cohesion: 0.40
Nodes (4): Calibrated thresholds (`dsp.leadoff_report`), Findings, Lead-off calibration & validation — 2026-08-29, Notes

### Community 59 - "Features and how to explain them (intent -> answer -> action)"
Cohesion: 0.13
Nodes (14): Answer style, EMG Baseline check + electrode lead-off, Fatigue + target biofeedback, Features and how to explain them (intent -> answer -> action), Filtering, Michael — knowledge base (grounding for the EMG research-centre assistant), MVC calibration + % MVC normalization, Offline amplitude normalization (in Review) (+6 more)

### Community 60 - "EMG-SAW_Weekly_Report_2026-08-28_to_09-03_da066e19.md"
Cohesion: 0.15
Nodes (12): 1. Executive Summary, 2. Starting Point (28 August), 3.1  Electrode lead-off & signal integrity, 3.2  Noraxon-parity feature set (15-screen workflow), 3.3  New feature - %MVC target biofeedback, 3.4  UX and layout, 3.5  DSP academic verification, 3. Work Completed (+4 more)

### Community 61 - "EMG Research-Centre — Web Front-End (webapp/)"
Cohesion: 0.22
Nodes (8): Backend endpoint contract (`scripts/clinic_server.py` — extends `scripts/emg_map_server.py`), Build order (start here), Conventions, EMG Research-Centre — Web Front-End (webapp/), Folder layout, Front-end API wrappers (`src/systems/api.js`), Michael contract, Run it

### Community 62 - "Handler"
Cohesion: 0.27
Nodes (3): BaseHTTPRequestHandler, Handler, Token-auth reverse proxy for Ollama. Ollama has no authentication, so we must…

### Community 63 - "PROJECT_CONTEXT.md"
Cohesion: 0.20
Nodes (9): Architecture (locked pipeline), Current state — DONE ✅ (as of 2026-08-26), Locked gotchas (each cost hours — do NOT rediscover), Locked hardware facts, Locked wire protocol, Project identity, Roadmap, Signal facts (+1 more)

### Community 64 - "QUALITY_BAR.md"
Cohesion: 0.22
Nodes (3): Authority, Gate reference, Supporting rules (a pattern of violations becomes blocking)

### Community 65 - "EMG SAW — Retrospective + Competitive Roadmap"
Cohesion: 0.22
Nodes (9): EMG SAW — Retrospective + Competitive Roadmap, Next STM32 upgrade — all 15 electrodes (deferred; needs more/faster ADC), Now — Blue Pill, Channel 1, 3 electrodes (no mux, reuses existing software), Part 1 — What each agent shipped (retro of the build), Part 2 — Remaining goals per agent (near-term), Part 3 — Where we stand vs Delsys & Noraxon, Part 4 — The "win" roadmap (prioritized), Part 5 — Electrode lead-off / integrity plan (+1 more)

### Community 67 - "EMG-SAW — Beihang EMG Acquisition System + GUI"
Cohesion: 0.33
Nodes (6): Architecture, EMG-SAW — Beihang EMG Acquisition System + GUI, Quick start, Repo, Status, What it does

## Knowledge Gaps
- **209 isolated node(s):** `0. How to use this handoff`, `1. Mission`, `2. Quick start — open the EMG scope`, `3. Current state — DONE ✅ (as of 2026-08-27)`, `4. Repo map` (+204 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 419 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EmgScope` connect `EmgScope` to `ReviewWindow`, `emg_plotter.py`, `EmgPlotWidget`, `EmgFilters`, `dsp.py`, `MvcDialog`, `RecordingController`, `._apply_scaling`, `AmpNormDialog`, `._prompt_save_recording`, `._activate_mvc`, `._process`, `ChannelPanel`, `AcquisitionModel`, `._update_status`, `MainController`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `ReviewWindow` connect `ReviewWindow` to `EmgScope`, `emg_plotter.py`, `EmgFilters`, `dsp.py`, `._prompt_save_recording`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `EmgFilters` connect `EmgFilters` to `EmgScope`, `ReviewWindow`, `emg_plotter.py`, `dsp.py`, `MvcDialog`, `emg_features.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `EmgScope` (e.g. with `EmgFilters` and `LeadoffTracker`) actually correct?**
  _`EmgScope` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ReviewWindow` (e.g. with `EmgScope` and `EmgFilters`) actually correct?**
  _`ReviewWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `EmgFilters` (e.g. with `EmgScope` and `MvcDialog`) actually correct?**
  _`EmgFilters` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MvcDialog` (e.g. with `EmgScope` and `EmgFilters`) actually correct?**
  _`MvcDialog` has 2 INFERRED edges - model-reasoned connections that need verification._