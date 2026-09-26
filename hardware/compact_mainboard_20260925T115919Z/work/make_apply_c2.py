"""Derive apply_C2_T.pas from the proven apply_B.pas (text transformation only; see the header written below)."""
import os
here = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(here, 'apply_B.pas'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, 'pattern not found: ' + old[:80]
    s = s.replace(old, new) if count is None else s.replace(old, new, count)


rep(r"// CANDIDATE B ONLY.  Applies work\B_OPS.txt (see gen_B_ops.py) to B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc.",
    "// CANDIDATE C2 (template @ROOT@/@LOG@).  Applies work\\C2_OPS.txt (see gen_C2_ops.py) to the C2 copy.\n"
    "// Same proven machinery as apply_B.pas, plus: rotation after flip (C2 turns groups), PMOVE (native free test pads),\n"
    "// RULE_PASTE (PasteMaskExpansion rule, proven on disposable 25 Sep), race-free .part progress log.")
rep(r"Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';",
    "Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';")
rep(r"\work\B_OPS.txt';", r"\work\C2_OPS.txt';")
rep(r"Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\APPLY_B_LOG.txt';",
    "Const OutFile='@LOG@';")
rep("Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;",
    "Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;")
rep("Function FindKeepout(", """Function FindFreePad(Name:String;X,Y:Double):IPCB_Pad;
Var It:IPCB_BoardIterator;P:IPCB_Pad;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin
  If Not P.InComponent Then If P.Name=Name Then If CloseTo(P.X,X) And CloseTo(P.Y,Y) Then Begin Inc(MatchCount);Result:=P;End;
  P:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Function FindKeepout(""")
rep("   End Else If Kind='OUTLINE' Then Begin", """   End Else If Kind='PMOVE' Then Begin
    Pd:=FindFreePad(Fld(S,1),Num(S,2),Num(S,3));If MatchCount<>1 Then Begin Fail('free pad count '+IntToStr(MatchCount)+' '+Fld(S,1));Continue;End;
    MoveObjs.Add(Pd);MoveVec.Add(Fld(S,4)+'|'+Fld(S,5));Objs.Add(Pd);
   End Else If Kind='RULE_PASTE' Then Begin
    Ru:=FindRule(Fld(S,1));If MatchCount<>0 Then Begin Fail('rule exists '+Fld(S,1));Continue;End;Objs.Add(B.BoardOutline);
   End Else If Kind='OUTLINE' Then Begin""")
rep("R:IPCB_Region;Ru:IPCB_Rule;P:IPCB_Polygon;", "R:IPCB_Region;Ru:IPCB_Rule;P:IPCB_Polygon;Pd:IPCB_Pad;")
rep("""   If Fld(S,4)='1' Then Begin C.FlipComponent;Inc(NF);End
   Else If Fld(S,7)='1' Then C.Rotation:=Num(S,8);""",
    """   If Fld(S,4)='1' Then Begin C.FlipComponent;Inc(NF);End;
   If Fld(S,7)='1' Then C.Rotation:=Num(S,8);""")
rep("  Say('RULES_DONE');", """  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'RULE_PASTE' Then Continue;
   Ru:=PCBServer.PCBRuleFactory(eRule_PasteMaskExpansion);Ru.Name:=Fld(S,1);Ru.Scope1Expression:=Fld(S,2);Ru.Expansion:=MMsToCoord(Num(S,3));
   B.AddPCBObject(Ru);Say('RULE_PASTE_ADDED|'+Ru.Name+'|EXP_MM='+FloatToStr(CoordToMMs(Ru.Expansion)));
  End;
  Say('RULES_DONE');""")
rep("  RB:=B.BoardOutline.BoundingRectangle;Say('READBACK_OUTLINE|'", """  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePadObject));
  Try Pd:=It.FirstPCBObject;While Pd<>Nil Do Begin
   If Not Pd.InComponent Then Log.Add('READBACK_FREEPAD|'+Pd.Name+'|'+Layer2String(Pd.Layer)+'|X='+MM(Pd.X)+'|Y='+MM(Pd.Y));
   Pd:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  RB:=B.BoardOutline.BoundingRectangle;Say('READBACK_OUTLINE|'""")
rep("If D=Nil Then Raise('B PCB not open (open it inside its project first)');", "If D=Nil Then Raise('C2 PCB not open (open it inside its project first)');")
rep("If D.Modified Then Raise('B has unsaved changes - refusing');", "If D.Modified Then Raise('C2 has unsaved changes - refusing');")
open(os.path.join(here, 'apply_C2_T.pas'), 'w', encoding='utf-8').write(s)
print('apply_C2_T.pas written; placeholders', s.count('@ROOT@') + s.count('@LOG@'))
