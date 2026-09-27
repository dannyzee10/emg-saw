param([Parameter(Mandatory=$true)][string]$Script,[Parameter(Mandatory=$true)][string]$Result,[ValidateSet('Read','Apply')][string]$Kind='Read',[int]$TimeoutSec=500)
$ErrorActionPreference='Stop'
if($Script -notmatch '^[a-zA-Z0-9_]+\.PrjScr$' -or $Result -notmatch '^[a-zA-Z0-9_]+\.txt$'){throw 'Basenames only'}
$emgWork=$PSScriptRoot
$emgOut=Join-Path (Split-Path $emgWork -Parent) ('evidence/'+$Result)
if(Test-Path -LiteralPath $emgOut){throw 'Refusing to replace previous result; use a fresh result name'}
if(@(Get-Process X2 -ErrorAction SilentlyContinue).Count -ne 1){throw 'Expected exactly one Altium process; no process will be stopped'}
& (Join-Path $emgWork 'run_native.ps1') -Action Run -Script $Script | Out-Null
$emgDeadline=(Get-Date).AddSeconds($TimeoutSec)
while((Get-Date) -lt $emgDeadline){
 if(Test-Path -LiteralPath $emgOut){
  $emgText=Get-Content -LiteralPath $emgOut -Raw
  if($emgText -match 'PHASE1_FAIL|ABORTED_NO_CHANGES|COMPLETE_WITH_ABORT'){throw 'Native script rejected operations; inspect result'}
  if($emgText -match '(?m)^COMPLETE\s*$' -or $emgText -match '(?m)^READ_ONLY; COMPLETE\s*$'){
   if($Kind -eq 'Apply' -and ($emgText -notmatch '(?m)^PHASE1_OK\|' -or $emgText -notmatch '(?m)^SAVED\s*$' -or $emgText -notmatch '(?m)^AFTER_REOPEN\|')){throw 'Missing native apply/save/reopen evidence'}
   Write-Output ('VERIFIED_SCRIPT_COMPLETION='+$emgOut)
   Get-Content -LiteralPath $emgOut -Tail 9
   exit 0
  }
 }
 Start-Sleep -Seconds 2
}
throw 'Timed out; Altium left untouched. Inspect partial log and live state before another dispatch.'
