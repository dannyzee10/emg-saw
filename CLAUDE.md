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

## Task routing protocol (graphify-first) — DEFAULT for every roadmap task
Speed + token discipline: never brute-force read/grep when the graph can answer. For each task:
1. **LOCATE** — query the code-graph FIRST (`graphify query "<task>"`, or read `graphify-out/graph.json` /
   `GRAPH_REPORT.md`) to get the scoped set of affected nodes + files. A subgraph, not whole-file dumps.
2. **ROUTE** — map those nodes → owning agent via `AGENT_OWNERSHIP.yml` / `agent_map.html` (the "continent"
   the work lands in). Pick the agent who owns the most-affected code; split across agents by ownership.
3. **DISPATCH** — hand ONLY that scoped subgraph + acceptance criteria to that one engineer agent.
4. **GATE** — the change must pass its `QUALITY_BAR` gate; test-engineer produces the evidence.
5. **REFRESH + APPROVE** — `scripts/refresh.ps1` (fresh graph, HG8), then Daniyal approves (HG10).

Token rule (`TOKEN_POLICY.md`): graph subgraph → read only the exact `file:line` → edit. That is the
point of graphify — fast search, minimal context, then act. The main-brain orchestrates; it does not
do an owned agent's work itself.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
