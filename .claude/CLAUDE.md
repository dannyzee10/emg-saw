# graphify
- **graphify** (`.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

## Freshness rule (QUALITY_BAR HG8)
After ANY code change, run `.\scripts\refresh.ps1` (= `graphify update .` + `python scripts\agent_map.py`)
so both the graph and the **agent world-map** (`agent_map.html`) match HEAD, then commit `graphify-out/`.
Optional: `git config core.hooksPath scripts/hooks` installs a pre-commit hook that does this automatically.

## Agent world-map
`agent_map.html` (built by `scripts/agent_map.py` from `AGENT_OWNERSHIP.yml` + `graphify-out/graph.json`)
shows each agent as a continent, code as cities, dependencies as arcing trails. Use it to see ownership,
cross-agent coupling, and where work is missing (thin/absent continents = under-built areas).
