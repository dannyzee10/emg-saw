# Graph Report - emg-saw  (2026-08-27)

## Corpus Check
- 69 files · ~41,463 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 446 nodes · 597 edges · 38 communities (27 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `697dba51`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EmgScope
- EMG Bring-up Checkpoint Log
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
- PROJECT_CONTEXT.md
- agent_map.py
- EMG SAW — Retrospective + Competitive Roadmap
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

## God Nodes (most connected - your core abstractions)
1. `EmgScope` - 47 edges
2. `EmgPlotWidget` - 16 edges
3. `EMG UART Protocol Specification` - 15 edges
4. `EMG UART Protocol Specification` - 14 edges
5. `FrameParser` - 13 edges
6. `EmgFilters` - 12 edges
7. `_BufferedSource` - 11 edges
8. `RecordingController` - 11 edges
9. `Hard gate rules` - 11 edges
10. `AcquisitionModel` - 10 edges

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

## Communities (38 total, 11 thin omitted)

### Community 0 - "EmgScope"
Cohesion: 0.08
Nodes (4): EmgScope, EMG median frequency (Hz) over the 20-450 Hz band — a fatigue indicator., Highlight active (contraction) samples in white on top of the trace., Absolute volts in -> displayed volts out (coupling + optional filters).

### Community 1 - "EMG Bring-up Checkpoint Log"
Cohesion: 0.06
Nodes (64): Graphify Trigger Config (.claude/CLAUDE.md), EMG SAW Agent Roster (agents/), Round Table Collaboration, SAFe Methodology (Epic/Feature/Story), Graphify Project Instructions (CLAUDE.md), DSP Engineer Agent, Firmware Engineer Agent, GUI Engineer Agent (+56 more)

### Community 3 - "emg_plotter.py"
Cohesion: 0.06
Nodes (24): AsciiSource, _BufferedSource, _open_serial(), ndarray, Data sources for the plotter. Every source runs a background thread that fills…, Fallback for a quick STM32 `printf("%d,%d\\n", ...)` bring-up., Synthetic sEMG: baseline noise + intermittent bursts (band-limited noise…, Open the serial port exactly like a plain read that is known to work here. Open… (+16 more)

### Community 4 - "graphify query"
Cohesion: 0.09
Nodes (24): graphify add (URL ingest), Watch debounce, graphify --watch folder watcher, MCP server, Confidence tiers (EXTRACTED/INFERRED/AMBIGUOUS), Confidence score rubric, Hyperedges, Node ID format (+16 more)

### Community 5 - "emg_bluepill/main.c"
Cohesion: 0.25
Nodes (14): build_frame(), ADC_HandleTypeDef, crc16_ccitt(), Error_Handler(), HAL_ADC_ConvCpltCallback(), HAL_ADC_ConvHalfCpltCallback(), main(), MX_ADC1_Init() (+6 more)

### Community 6 - "EmgFilters"
Cohesion: 0.13
Nodes (9): EmgFilters, ndarray, Display-side signal processing (done on the laptop, so you can tweak live —…, Linear envelope: moving-RMS of the (already band-passed) signal., Unit tests for EmgFilters DSP functions. Validates: - Notch filter attenuation…, 50 Hz sine should be attenuated by more than 20 dB., RMS envelope of a 100 Hz sine (amplitude 1) should be ~0.707 V., RMS envelope should preserve number of channels. (+1 more)

### Community 7 - "Beihang University Logo (logo.png)"
Cohesion: 1.00
Nodes (3): Beihang University Logo (logo.png), Beihang University Logo (R.png), Beihang-branded UI Header

### Community 18 - "Hard gate rules"
Cohesion: 0.12
Nodes (14): Authority, Gate reference, Hard gate rules, HG10 — No "done" without Daniyal approval, HG1 — Protocol integrity, HG2 — Firmware timing & delivery, HG3 — DSP correctness, HG4 — GUI robustness (+6 more)

### Community 19 - "PROJECT_CONTEXT.md"
Cohesion: 0.18
Nodes (9): Architecture (locked pipeline), Current state — DONE ✅ (as of 2026-08-26), Locked gotchas (each cost hours — do NOT rediscover), Locked hardware facts, Locked wire protocol, Project identity, Roadmap, Signal facts (+1 more)

### Community 20 - "agent_map.py"
Cohesion: 0.83
Nodes (3): load_ownership(), main(), owner_of()

### Community 22 - "EMG SAW — Retrospective + Competitive Roadmap"
Cohesion: 0.33
Nodes (5): EMG SAW — Retrospective + Competitive Roadmap, Part 1 — What each agent shipped (retro of the build), Part 2 — Remaining goals per agent (near-term), Part 3 — Where we stand vs Delsys & Noraxon, Part 4 — The "win" roadmap (prioritized)

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
Cohesion: 0.16
Nodes (16): crc16_ccitt(), encode_frame(), FrameParser, Wire protocol shared by the STM32 firmware and the laptop plotter. Version 1…, CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF). Matches the C code in firmware/., Build one frame. `version` = 1 for legacy 8-bit seq, 2 for 16-bit seq., Streaming parser that auto-detects protocol version per frame. Yields (seq,…, main() (+8 more)

### Community 36 - "GUI Architecture Proposal (EMG Instrument)"
Cohesion: 0.22
Nodes (8): Controller, Current State, Data Flow, GUI Architecture Proposal (EMG Instrument), Immediate Refactoring Steps, Model, Proposed Modular Architecture, View

### Community 37 - "EmgPlotWidget"
Cohesion: 0.14
Nodes (6): EmgPlotWidget, Holds the GraphicsLayoutWidget, per-channel plots, curves, overlays, cursors,…, Show/hide the spectrum plot., Update all channel curves with new data. `data` shape (n_samples, nch)., Update onset overlay for channel c., Update spectrum curves. `psd_list` is list of arrays per channel.

### Community 38 - "RecordingController"
Cohesion: 0.17
Nodes (6): RecordingController – manages CSV recording independent of the GUI., Open a new CSV file and write metadata header., Write a chunk of raw samples to the file. `new_data` shape (n_samples, nch)., Write a marker line (preceded by #) to the file., Handles opening, writing, and closing a CSV file for raw EMG data., RecordingController

## Knowledge Gaps
- **145 isolated node(s):** `Project identity`, `Architecture (locked pipeline)`, `Locked hardware facts`, `Locked wire protocol`, `Current state — DONE ✅ (as of 2026-08-26)` (+140 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EmgScope` connect `EmgScope` to `RecordingController`, `emg_plotter.py`, `EmgPlotWidget`, `EmgFilters`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `EmgFilters` connect `EmgFilters` to `EmgScope`, `emg_plotter.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `EmgPlotWidget` connect `EmgPlotWidget` to `EmgScope`, `emg_plotter.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `EmgScope` (e.g. with `EmgFilters` and `ChannelPanel`) actually correct?**
  _`EmgScope` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project identity`, `Architecture (locked pipeline)`, `Locked hardware facts` to the rest of the system?**
  _145 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `EmgScope` be split into smaller, more focused modules?**
  _Cohesion score 0.08478513356562137 - nodes in this community are weakly interconnected._
- **Should `EMG Bring-up Checkpoint Log` be split into smaller, more focused modules?**
  _Cohesion score 0.057539682539682536 - nodes in this community are weakly interconnected._