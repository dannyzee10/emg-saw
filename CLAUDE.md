# EMG SAW — AI context

**START HERE (read in this order before doing anything):**
1. `HANDOFF.md` — complete memory: mission, how to run the scope, retro, and the deep per-agent plan.
2. `PROJECT_CONTEXT.md` — authoritative locked facts (hardware, protocol, current state, gotchas).
3. `QUALITY_BAR.md` — hard gates every change must pass.
4. `AGENT_OWNERSHIP.yml` + `agent_map.html` — who owns what; open the world-map to orient.

**Run the scope:** `python emgscope.py --sim --channels 5` (demo) or
`python emgscope.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick` (hardware).
**Flash firmware:** Build in CubeIDE → `scripts\flash_run.bat` (never the IDE Debug/Run buttons).
**After any code change:** `.\scripts\refresh.ps1` then commit (QUALITY_BAR HG8).

Agents live in `.claude/agents/`. This is a SAFe "Round Table" workflow — equal voice, evidence-based,
stop-the-line authority, nothing final without Daniyal's approval.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
