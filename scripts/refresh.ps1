# EMG SAW — refresh the knowledge graph and the agent world-map after code changes.
# Run from the repo root:   .\scripts\refresh.ps1
# (Satisfies QUALITY_BAR.md HG8: the graph agents read must match HEAD.)

Write-Host "[refresh] graphify update ." -ForegroundColor Cyan
graphify update .

Write-Host "[refresh] rebuilding agent world-map" -ForegroundColor Cyan
python scripts\agent_map.py

Write-Host "[refresh] done. Remember to: git add graphify-out ; git commit" -ForegroundColor Green
