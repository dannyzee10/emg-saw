"""apply_ops_T.pas = apply_ops_v6.pas (proven track/via/rule writer) templated: @ROOT@ board, @OPS@ ops file in work/,
@LOG@ result file (progress to <log>.part, result written once at the end)."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(here, 'apply_ops_v6.pas'), encoding='utf-8').read()
s = re.sub(r"Const PcbPath='[^']*';", "Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';", s)
s = re.sub(r"Const OpsFile='[^']*';", "Const OpsFile='" + here.replace('\\', '\\\\') + "\\\\@OPS@';", s)
s = re.sub(r"Const OutFile='[^']*';", "Const OutFile='@LOG@';", s)
s = s.replace("Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;",
              "Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;")
# the final Finally-block save goes to OutFile (the polled file), on both the COMPLETE and the abort path
assert ' Finally Ops.Free;Log.Free;End;' in s
s = s.replace(' Finally Ops.Free;Log.Free;End;', ' Finally Log.SaveToFile(OutFile);Ops.Free;Log.Free;End;')
n_final = s.count('Finally Log.SaveToFile(OutFile)')
open(os.path.join(here, 'apply_ops_T.pas'), 'w', encoding='utf-8').write(s)
print('apply_ops_T.pas written; final-save sites', n_final, '; ops path', re.search(r"Const OpsFile='([^']*)'", s).group(1)[-40:])
