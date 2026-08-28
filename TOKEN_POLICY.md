# EMG SAW Token Policy

> Goal: reduce token use in SAW sessions without weakening any quality gate.
> This policy governs narration length, ignore/archive scope, and gate read paths.
> It never overrides QUALITY_BAR.md. If in conflict, QUALITY_BAR.md wins.

## Protected source-of-truth (never ignore, archive, summarize, or hide)
- PROJECT_CONTEXT.md
- QUALITY_BAR.md
- docs/EMG_System_Architecture.md
- docs/EMG_SAW_Project_Plan.md
- specs/ (all active specs and checkpoints)
- firmware/ (current STM32 source)
- gui/ (current PyQt5 source)
- dsp/ (current filter/metrics code)
- hardware/ (schematics, BOM, AFE design docs)
- tests/ (all validation scripts)
- agents/EMG_SAW_Agent_Roster.md
- Any live gate report or checkpoint file

## Safe to ignore/archive
- Build artifacts: **/__pycache__/, *.pyc, *.log, .DS_Store, Thumbs.db
- Old hardware revisions (move to hardware/_archive/)
- Superseded firmware builds (firmware/_archive/)
- Retired test data (data/_archive/)

## Chat output terseness rule
- Narration (status updates, reasoning recap) must be short.
- Evidence fields in gate reports are NEVER shortened or dropped:
  - file path, line number, measured value, source artifact, checker verdict, escalation.
- Terseness applies to narration only, never to evidence tables or status labels.

## Gate read-path invariant
- Gate agents always read the real current repo bytes of the file under test.
- No cached, compressed, summarized, or archived copy may substitute.
- Untouchable read paths: firmware, gui, dsp, hardware, test validation.

## Archive policy
- Only superseded planning/iteration docs may move to _archive/ subfolders.
- Live specs, checkpoints, and current source stay in root.
- Archive = move within repo, never delete.

## EMGify (Graphify) Integration
- Before reading a source file, agents MUST run:
  - `graphify query "<question about code/docs>"`
  - `graphify path "SourceA" "TargetB"`
  - `graphify explain "NodeName"`
- Use `GRAPH_REPORT.md` for broad architecture review.
- Raw file reads are allowed only after graph queries fail or when exact line-level evidence is required.
- Commit `graphify-out/` to the repo; add `graphify-out/cost.json` to .gitignore.


## How to test a proposed ignore/archive change
1. List every file the pattern matches.
2. Check each against the protected list above. Any match => reject.
3. Confirm the file is superseded/retired, not an active input.
4. Ask: if the relevant gate were rerun, would verdict change? If yes => reject.
5. Only after all four pass may the change be proposed to Daniyal for approval.