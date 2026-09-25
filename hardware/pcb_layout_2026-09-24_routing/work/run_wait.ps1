param([Parameter(Mandatory=$true)][string]$Script,[Parameter(Mandatory=$true)][string]$Result,[int]$TimeoutSec=180)
# Dispatch one native script into the running Altium and wait for its result file to say COMPLETE.
# Unlike dispatch_native.ps1 this never dismisses dialogs or stops scripts (the user's work may be open).
$ErrorActionPreference='Stop'
# clear stale command forwarders (a stuck X2.EXE forwarder blocks every later command)
$main=(Get-Process X2 | Sort-Object StartTime | Select-Object -First 1).Id
Get-Process X2 | Where-Object { $_.Id -ne $main } | ForEach-Object { Stop-Process -Id $_.Id -Force }
$work='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\work'
$ev='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence'
$out=Join-Path $ev $Result
if(Test-Path -LiteralPath $out){Remove-Item -LiteralPath $out -Force}
& (Join-Path $work 'run_native.ps1') -Action Run -Script $Script | Out-Null
$deadline=(Get-Date).AddSeconds($TimeoutSec);$done=$false
while((Get-Date) -lt $deadline){
 if((Test-Path -LiteralPath $out) -and ((Get-Content -LiteralPath $out -Raw) -match 'COMPLETE')){$done=$true;break}
 Start-Sleep -Seconds 2
}
$modal=(& (Join-Path $work 'run_native.ps1') -Action Windows 2>&1) | Where-Object { $_ -notmatch 'TApplication|TDocumentForm' }
"COMPLETED=$done"
if($modal){"WINDOWS:";$modal}
