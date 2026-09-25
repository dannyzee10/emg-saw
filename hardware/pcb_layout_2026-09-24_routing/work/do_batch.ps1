param([Parameter(Mandatory=$true)][string]$Tag,[int]$TimeoutSec=2400)
# One write batch on the ROUTING COPY: backup -> apply_ops_v6 (validate all, apply, repour, save, reopen)
# -> geometry export -> native batch DRC -> parsed JSON.  work\OPS.txt must already be verified by build_ops.py.
$ErrorActionPreference='Stop'
$r='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing'
$pcb="$r\MainBoard\EMG_MainBoard_Layout.PcbDoc"
Copy-Item -LiteralPath $pcb -Destination "$r\evidence\backups\BEFORE_$Tag.PcbDoc" -Force
"backup BEFORE_$Tag " + (Get-FileHash "$r\evidence\backups\BEFORE_$Tag.PcbDoc").Hash
$n='ap_'+(Get-Date -Format 'HHmmss')
Copy-Item -LiteralPath "$r\work\apply_ops_v6.pas" -Destination "$r\work\$n.pas"
Set-Content -LiteralPath "$r\work\$n.PrjScr" -Value "[Design]`r`nVersion=1.0`r`n[Document1]`r`nDocumentPath=$n.pas" -Encoding ascii
& "$r\work\run_wait.ps1" -Script "$n.PrjScr" -Result APPLY_OPS_LOG.txt -TimeoutSec $TimeoutSec | Select-Object -Last 3
Get-Content "$r\evidence\APPLY_OPS_LOG.txt" | Where-Object { $_ -notmatch '^POLY_REBUILT' -or $_ -match 'INVALID=True' } | Select-Object -Last 25
Copy-Item "$r\evidence\APPLY_OPS_LOG.txt" "$r\evidence\APPLY_OPS_LOG_$Tag.txt" -Force
if(-not ((Get-Content "$r\evidence\APPLY_OPS_LOG.txt" -Raw) -match '(?m)^COMPLETE\s*$')){ 'WRITE DID NOT COMPLETE - stopping'; exit 1 }
& "$r\work\run_wait.ps1" -Script export_geometry.PrjScr -Result GEOMETRY.txt -TimeoutSec 600 | Select-Object -Last 1
Copy-Item "$r\evidence\GEOMETRY.txt" "$r\evidence\GEOMETRY_AFTER_$Tag.txt" -Force
& "$r\work\run_wait.ps1" -Script run_drc.PrjScr -Result DRC_RUN_STATUS.txt -TimeoutSec 1200 | Select-Object -Last 1
Copy-Item "$r\evidence\DRC_LATEST.html" "$r\evidence\DRC_$Tag.html" -Force
python "$r\work\parse_drc.py" "$r\evidence\DRC_$Tag.html" "$r\evidence\DRC_$Tag.json"
