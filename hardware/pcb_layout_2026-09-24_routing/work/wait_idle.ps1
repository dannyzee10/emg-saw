param([int]$TimeoutSec=3600,[int]$IdleSamples=4,[double]$IdleCpuSec=0.4,[int]$StepSec=5)
# Wait until Altium (X2.EXE) has been CPU-idle for IdleSamples consecutive StepSec windows.
$deadline=(Get-Date).AddSeconds($TimeoutSec);$idle=0
$prev=(Get-Process X2).TotalProcessorTime.TotalSeconds
$start=Get-Date
while((Get-Date) -lt $deadline){
 Start-Sleep -Seconds $StepSec
 $now=(Get-Process X2).TotalProcessorTime.TotalSeconds
 $d=$now-$prev;$prev=$now
 if($d -lt $IdleCpuSec){$idle++}else{$idle=0}
 if($idle -ge $IdleSamples){ "IDLE after {0:n0}s" -f ((Get-Date)-$start).TotalSeconds; exit 0 }
}
"TIMEOUT"; exit 1
