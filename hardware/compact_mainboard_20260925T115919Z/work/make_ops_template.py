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
# 6-layer stack (JLC06121H-3313): Mid Layer 3 (L4 GND) and Mid Layer 4 (L5 power/signal) are addressable by name;
# SET_WIDTH covers all six copper layers; RULE_RL / SET_RL take two optional extra flags (MID3, MID4).
old_lay = " Else If S='Bottom Layer' Then Result:=eBottomLayer"
assert old_lay in s
s = s.replace(old_lay, " Else If S='Mid Layer 3' Then Result:=eMidLayer3\n Else If S='Mid Layer 4' Then Result:=eMidLayer4\n" + old_lay)
old_w = "For K:=0 To 3 Do Begin\n      If K=0 Then Lay:=eTopLayer Else If K=1 Then Lay:=eMidLayer1 Else If K=2 Then Lay:=eMidLayer2 Else Lay:=eBottomLayer;"
assert old_w in s
s = s.replace(old_w, "For K:=0 To 5 Do Begin\n      If K=0 Then Lay:=eTopLayer Else If K=1 Then Lay:=eMidLayer1 Else If K=2 Then Lay:=eMidLayer2 "
                     "Else If K=3 Then Lay:=eMidLayer3 Else If K=4 Then Lay:=eMidLayer4 Else Lay:=eBottomLayer;")
old_rl = " RL.RoutingLayers(eMidLayer2):=Fld(S,F+2)='1';RL.RoutingLayers(eBottomLayer):=Fld(S,F+3)='1';"
assert old_rl in s
s = s.replace(old_rl, old_rl + "\n If Fld(S,F+4)<>'' Then RL.RoutingLayers(eMidLayer3):=Fld(S,F+4)='1';"
                              "If Fld(S,F+5)<>'' Then RL.RoutingLayers(eMidLayer4):=Fld(S,F+5)='1';")
s = s.replace("'|BOT='+BoolToStr(RL.RoutingLayers(eBottomLayer),True)",
              "'|BOT='+BoolToStr(RL.RoutingLayers(eBottomLayer),True)+'|MID3='+BoolToStr(RL.RoutingLayers(eMidLayer3),True)+'|MID4='+BoolToStr(RL.RoutingLayers(eMidLayer4),True)")
# RENAME_POLY|old|new : rename a polygon pour (validated in phase 1: exactly one pour with the old name, none with the new)
old_fn = "Procedure SetLayers("
assert old_fn in s
s = s.replace(old_fn, "Function CountPolys(Name:String):Integer;\nVar It:IPCB_BoardIterator;P:IPCB_Polygon;\nBegin\n Result:=0;\n"
              " It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));\n"
              " Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=Name Then Inc(Result);P:=It.NextPCBObject;End;\n"
              " Finally B.BoardIterator_Destroy(It);End;\nEnd;\n\n"
              "Procedure RenamePoly(OldName,NewName:String);\nVar It:IPCB_BoardIterator;P:IPCB_Polygon;\nBegin\n"
              " It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));\n"
              " Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=OldName Then Begin P.BeginModify;P.Name:=NewName;P.EndModify;"
              "Say('POLY_RENAMED|'+OldName+'|'+NewName);End;P:=It.NextPCBObject;End;\n"
              " Finally B.BoardIterator_Destroy(It);End;\nEnd;\n\n" + old_fn, 1)
old_v = "   Else If Kind='CUTOUT' Then Begin"
assert old_v in s
s = s.replace(old_v, "   Else If Kind='RENAME_POLY' Then Begin If CountPolys(Fld(S,1))<>1 Then Begin Fail('rename source count '+Fld(S,1));Continue;End;"
                     "If CountPolys(Fld(S,2))<>0 Then Begin Fail('rename target exists '+Fld(S,2));Continue;End;End\n" + old_v, 1)
old_a = "    End Else If Kind='CUTOUT' Then Begin"
assert old_a in s
s = s.replace(old_a, "    End Else If Kind='RENAME_POLY' Then Begin\n     RenamePoly(Fld(S,1),Fld(S,2));\n" + old_a, 1)
n_final = s.count('Finally Log.SaveToFile(OutFile)')
open(os.path.join(here, 'apply_ops_T.pas'), 'w', encoding='utf-8').write(s)
print('apply_ops_T.pas written; final-save sites', n_final, '; ops path', re.search(r"Const OpsFile='([^']*)'", s).group(1)[-40:])
