// CANDIDATE C2 (template C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\/C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\APPLY_C2_FIX_LOG.txt).  Applies work\C2_OPS.txt (see gen_C2_ops.py) to the C2 copy.
// Same proven machinery as apply_B.pas, plus: rotation after flip (C2 turns groups), PMOVE (native free test pads),
// RULE_PASTE (PasteMaskExpansion rule, proven on disposable 25 Sep), race-free .part progress log.
// Phase 1 resolves EVERY op to exactly one native object (components also by source UID and side) and changes nothing.
// Phase 2 applies: component flips/moves/rotations, MoveByXY/deletes of free copper, mechanical lines and the antenna
// keep-out, rule scopes, board outline, GND polygon outlines; repour; connectivity; save; close; reopen; readback.
// Every API used here was proven on a disposable copy on 25 Sep (flip_test, api_test, outline_test).
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OpsFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\work\C2_FIX_OPS.txt';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\APPLY_C2_FIX_LOG.txt';
Var Log:TStringList;B:IPCB_Board;Failures,MatchCount:Integer;Coll,MoveObjs,DelObjs:TInterfaceList;MoveVec:TStringList;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Procedure Fail(S:String);Begin Inc(Failures);Say('PHASE1_FAIL|'+S);End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Function Fld(S:String;N:Integer):String;
Var I,P:Integer;Rest:String;
Begin
 Rest:=S;
 For I:=0 To N-1 Do Begin P:=Pos('|',Rest);If P=0 Then Begin Result:='';Exit;End;Rest:=Copy(Rest,P+1,Length(Rest));End;
 P:=Pos('|',Rest);If P=0 Then Result:=Rest Else Result:=Copy(Rest,1,P-1);
End;
Function Num(S:String;N:Integer):Double;Begin Result:=StrToFloat(Fld(S,N));End;
Function CloseTo(A:TCoord;V:Double):Boolean;Begin Result:=Abs(CoordToMMs(A)-V)<0.002;End;
Function LayerOf(S:String):TLayer;
Begin
 If S='Top Layer' Then Result:=eTopLayer Else If S='Mid Layer 1' Then Result:=eMidLayer1
 Else If S='Mid Layer 2' Then Result:=eMidLayer2 Else If S='Bottom Layer' Then Result:=eBottomLayer
 Else If S='Mechanical Layer 4' Then Result:=eMechanical4 Else If S='Mechanical Layer 5' Then Result:=eMechanical5
 Else Raise('Unknown layer '+S);
End;
Function FindComp(Ref:String):IPCB_Component;
Var It:IPCB_BoardIterator;C:IPCB_Component;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
 Try C:=It.FirstPCBObject;While C<>Nil Do Begin If C.Name.Text=Ref Then Begin Inc(MatchCount);Result:=C;End;C:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;
Function FindTrack(Net,Lay:String;X1,Y1,X2,Y2:Double):IPCB_Track;
Var It:IPCB_BoardIterator;T:IPCB_Track;Ok:Boolean;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(MkSet(LayerOf(Lay)));It.AddFilter_ObjectSet(MkSet(eTrackObject));
 Try T:=It.FirstPCBObject;While T<>Nil Do Begin
  If Not T.InComponent Then Begin
   If Net='-' Then Ok:=True Else Ok:=(T.Net<>Nil);
   If Ok And (Net<>'-') Then Ok:=(T.Net.Name=Net);
   If Ok Then If ((CloseTo(T.X1,X1) And CloseTo(T.Y1,Y1) And CloseTo(T.X2,X2) And CloseTo(T.Y2,Y2)) Or (CloseTo(T.X1,X2) And CloseTo(T.Y1,Y2) And CloseTo(T.X2,X1) And CloseTo(T.Y2,Y1))) Then Begin Inc(MatchCount);Result:=T;If Coll<>Nil Then Coll.Add(T);End;
  End;
  T:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Function FindVia(Net:String;X,Y:Double):IPCB_Via;
Var It:IPCB_BoardIterator;V:IPCB_Via;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eViaObject));
 Try V:=It.FirstPCBObject;While V<>Nil Do Begin
  If CloseTo(V.X,X) Then If CloseTo(V.Y,Y) Then If V.Net<>Nil Then If V.Net.Name=Net Then Begin Inc(MatchCount);Result:=V;If Coll<>Nil Then Coll.Add(V);End;
  V:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Function FindFreePad(Name:String;X,Y:Double):IPCB_Pad;
Var It:IPCB_BoardIterator;P:IPCB_Pad;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin
  If Not P.InComponent Then If P.Name=Name Then If CloseTo(P.X,X) And CloseTo(P.Y,Y) Then Begin Inc(MatchCount);Result:=P;End;
  P:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Function FindKeepout(X0,Y0,X1,Y1:Double):IPCB_Region;
Var It:IPCB_BoardIterator;R:IPCB_Region;RB:TCoordRect;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_ObjectSet(MkSet(eRegionObject));It.AddFilter_LayerSet(MkSet(eKeepOutLayer));
 Try R:=It.FirstPCBObject;While R<>Nil Do Begin
  If Not R.InComponent Then Begin RB:=R.BoundingRectangle;
   If CloseTo(RB.Left,X0) And CloseTo(RB.Bottom,Y0) And CloseTo(RB.Right,X1) And CloseTo(RB.Top,Y1) Then Begin Inc(MatchCount);Result:=R;End;End;
  R:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Function FindRule(Name:String):IPCB_Rule;
Var It:IPCB_BoardIterator;R:IPCB_Rule;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
 Try R:=It.FirstPCBObject;While R<>Nil Do Begin If R.Name=Name Then Begin Inc(MatchCount);Result:=R;End;R:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;
Function FindPoly(Name:String):IPCB_Polygon;
Var It:IPCB_BoardIterator;P:IPCB_Polygon;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=Name Then Begin Inc(MatchCount);Result:=P;End;P:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;
Procedure SetSeg(O:IPCB_BoardOutline;I:Integer;IsArc:Boolean;X,Y,CX,CY,A1,A2:Double);
Var V:TPolySegment;
Begin
 V:=O.Segments[I];If IsArc Then V.Kind:=ePolySegmentArc Else V.Kind:=ePolySegmentLine;
 V.Vx:=MMsToCoord(X);V.Vy:=MMsToCoord(Y);
 If IsArc Then Begin V.Cx:=MMsToCoord(CX);V.Cy:=MMsToCoord(CY);V.Radius:=MMsToCoord(2);V.Angle1:=A1;V.Angle2:=A2;End;
 O.Segments[I]:=V;
End;
Procedure SetPolySeg(P:IPCB_Polygon;I:Integer;X,Y:Double);
Var V:TPolySegment;
Begin V:=P.Segments[I];V.Kind:=ePolySegmentLine;V.Vx:=MMsToCoord(X);V.Vy:=MMsToCoord(Y);P.Segments[I]:=V;End;

Function OpN(S:String):Integer;
Var P:Integer;
Begin P:=Pos('|N=',S);If P=0 Then Result:=1 Else Result:=StrToInt(Copy(S,P+3,10));End;
Procedure Queue(IsDel:Boolean;V:String);
Var K:Integer;
Begin
 For K:=0 To Coll.Count-1 Do Begin
  If IsDel Then DelObjs.Add(Coll.Items(K)) Else Begin MoveObjs.Add(Coll.Items(K));MoveVec.Add(V);End;
 End;
End;

Procedure RunFixed;
Var D:IServerDocument;Ops:TStringList;Objs:TInterfaceList;I,K,NC,NF:Integer;S,Kind:String;C:IPCB_Component;T:IPCB_Track;V:IPCB_Via;
    R:IPCB_Region;Ru:IPCB_Rule;P:IPCB_Polygon;Pd:IPCB_Pad;O:IPCB_BoardOutline;It:IPCB_BoardIterator;RB:TCoordRect;Wd,Ht:Double;Polys:TInterfaceList;Prim:IPCB_Primitive;
Begin
 Log:=TStringList.Create;Ops:=TStringList.Create;Objs:=TInterfaceList.Create;Coll:=Nil;MoveObjs:=TInterfaceList.Create;DelObjs:=TInterfaceList.Create;MoveVec:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  Ops.LoadFromFile(OpsFile);Say('OPS_LINES='+IntToStr(Ops.Count));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('C2 PCB not open (open it inside its project first)');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  If D.Modified Then Raise('C2 has unsaved changes - refusing');
  // ---------------- phase 1: resolve every op to exactly one object; change nothing
  Failures:=0;
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];Kind:=Fld(S,0);
   If Kind='COMP' Then Begin
    C:=FindComp(Fld(S,1));If MatchCount<>1 Then Begin Fail('comp count '+IntToStr(MatchCount)+' '+Fld(S,1));Continue;End;
    If C.SourceUniqueId<>Fld(S,2) Then Begin Fail('uid '+Fld(S,1));Continue;End;
    If Layer2String(C.Layer)<>Fld(S,3)+' Layer' Then Begin Fail('side '+Fld(S,1)+' is '+Layer2String(C.Layer));Continue;End;
    Objs.Add(C);
   End Else If (Kind='TMOVE') Or (Kind='TDEL') Then Begin
    Coll:=TInterfaceList.Create;T:=FindTrack(Fld(S,1),Fld(S,2),Num(S,3),Num(S,4),Num(S,5),Num(S,6));
    If MatchCount<>OpN(S) Then Begin Fail('track count '+IntToStr(MatchCount)+'<>'+IntToStr(OpN(S))+' line '+IntToStr(I));Coll.Free;Coll:=Nil;Continue;End;
    Queue(Kind='TDEL',Fld(S,7)+'|'+Fld(S,8));Coll.Free;Coll:=Nil;Objs.Add(T);
   End Else If (Kind='VMOVE') Or (Kind='VDEL') Then Begin
    Coll:=TInterfaceList.Create;V:=FindVia(Fld(S,1),Num(S,2),Num(S,3));
    If MatchCount<>OpN(S) Then Begin Fail('via count '+IntToStr(MatchCount)+'<>'+IntToStr(OpN(S))+' line '+IntToStr(I));Coll.Free;Coll:=Nil;Continue;End;
    Queue(Kind='VDEL',Fld(S,4)+'|'+Fld(S,5));Coll.Free;Coll:=Nil;Objs.Add(V);
   End Else If (Kind='MMOVE') Or (Kind='MDEL') Then Begin
    Coll:=TInterfaceList.Create;T:=FindTrack('-',Fld(S,1),Num(S,2),Num(S,3),Num(S,4),Num(S,5));
    If MatchCount<>OpN(S) Then Begin Fail('mech track count '+IntToStr(MatchCount)+'<>'+IntToStr(OpN(S))+' line '+IntToStr(I));Coll.Free;Coll:=Nil;Continue;End;
    Queue(Kind='MDEL',Fld(S,6)+'|'+Fld(S,7));Coll.Free;Coll:=Nil;Objs.Add(T);
   End Else If Kind='KMOVE' Then Begin
    R:=FindKeepout(Num(S,1),Num(S,2),Num(S,3),Num(S,4));If MatchCount<>1 Then Begin Fail('keepout count '+IntToStr(MatchCount));Continue;End;Objs.Add(R);
   End Else If Kind='RULE' Then Begin
    Ru:=FindRule(Fld(S,1));If MatchCount<>1 Then Begin Fail('rule count '+IntToStr(MatchCount)+' '+Fld(S,1));Continue;End;Objs.Add(Ru);
   End Else If Kind='POLY' Then Begin
    P:=FindPoly(Fld(S,1));If MatchCount<>1 Then Begin Fail('poly count '+IntToStr(MatchCount)+' '+Fld(S,1));Continue;End;Objs.Add(P);
   End Else If Kind='PMOVE' Then Begin
    Pd:=FindFreePad(Fld(S,1),Num(S,2),Num(S,3));If MatchCount<>1 Then Begin Fail('free pad count '+IntToStr(MatchCount)+' '+Fld(S,1));Continue;End;
    MoveObjs.Add(Pd);MoveVec.Add(Fld(S,4)+'|'+Fld(S,5));Objs.Add(Pd);
   End Else If Kind='RULE_PASTE' Then Begin
    Ru:=FindRule(Fld(S,1));If MatchCount<>0 Then Begin Fail('rule exists '+Fld(S,1));Continue;End;Objs.Add(B.BoardOutline);
   End Else If Kind='OUTLINE' Then Begin
    If B.BoardOutline=Nil Then Begin Fail('no outline');Continue;End;Objs.Add(B.BoardOutline);
   End Else Fail('unknown op '+Kind);
  End;
  If Failures>0 Then Begin Say('ABORTED_NO_CHANGES|FAILURES='+IntToStr(Failures));Say('COMPLETE_WITH_ABORT');Exit;End;
  Say('PHASE1_OK|ALL '+IntToStr(Ops.Count)+' OPS RESOLVED|PRIM_MOVES='+IntToStr(MoveObjs.Count)+'|PRIM_DELETES='+IntToStr(DelObjs.Count));
  // ---------------- phase 2a: components (same pattern as the proven place_drl_bottom/flip_test)
  NC:=0;NF:=0;
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'COMP' Then Continue;
   C:=Objs.Items(I);
   If Fld(S,4)='1' Then Begin C.FlipComponent;Inc(NF);End;
   If Fld(S,7)='1' Then C.Rotation:=Num(S,8);
   C.X:=MMsToCoord(Num(S,5));C.Y:=MMsToCoord(Num(S,6));Inc(NC);
  End;
  Say('COMPONENTS_DONE|MOVED='+IntToStr(NC)+'|FLIPPED='+IntToStr(NF));
  // ---------------- phase 2b: free primitives, keep-out, deletes
  PCBServer.PreProcess;
  Try
   For K:=0 To MoveObjs.Count-1 Do Begin
    Prim:=MoveObjs.Items(K);Prim.MoveByXY(MMsToCoord(StrToFloat(Fld(MoveVec[K],0))),MMsToCoord(StrToFloat(Fld(MoveVec[K],1))));
   End;
   For I:=0 To Ops.Count-1 Do Begin
    S:=Ops[I];If Fld(S,0)='KMOVE' Then Begin R:=Objs.Items(I);R.MoveByXY(MMsToCoord(Num(S,5)),MMsToCoord(Num(S,6)));End;
   End;
   For K:=0 To DelObjs.Count-1 Do Begin Prim:=DelObjs.Items(K);B.RemovePCBObject(Prim);End;
  Finally PCBServer.PostProcess;End;
  Say('PRIMITIVES_DONE|MOVED='+IntToStr(MoveObjs.Count)+'|DELETED='+IntToStr(DelObjs.Count));
  // ---------------- phase 2c: rules
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'RULE' Then Continue;
   Ru:=Objs.Items(I);If Fld(S,2)='1' Then Ru.Scope1Expression:=Fld(S,3) Else Ru.Scope2Expression:=Fld(S,3);
  End;
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'RULE_PASTE' Then Continue;
   Ru:=PCBServer.PCBRuleFactory(eRule_PasteMaskExpansion);Ru.Name:=Fld(S,1);Ru.Scope1Expression:=Fld(S,2);Ru.Expansion:=MMsToCoord(Num(S,3));
   B.AddPCBObject(Ru);Say('RULE_PASTE_ADDED|'+Ru.Name+'|EXP_MM='+FloatToStr(CoordToMMs(Ru.Expansion)));
  End;
  Say('RULES_DONE');
  // ---------------- phase 2d: board outline (proven RMW pattern, project context)
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'OUTLINE' Then Continue;
   Wd:=Num(S,1);Ht:=Num(S,2);O:=B.BoardOutline;
   O.BeginModify;O.PointCount:=8;
   SetSeg(O,0,False,12,10,0,0,0,0);SetSeg(O,1,True,8+Wd,10,8+Wd,12,270,360);
   SetSeg(O,2,False,10+Wd,12,0,0,0,0);SetSeg(O,3,True,10+Wd,8+Ht,8+Wd,8+Ht,0,90);
   SetSeg(O,4,False,8+Wd,10+Ht,0,0,0,0);SetSeg(O,5,True,12,10+Ht,12,8+Ht,90,180);
   SetSeg(O,6,False,10,8+Ht,0,0,0,0);SetSeg(O,7,True,10,12,12,12,180,270);
   O.EndModify;O.Invalidate;O.Rebuild;O.Validate;B.UpdateBoardOutline;
   RB:=B.BoardOutline.BoundingRectangle;Say('OUTLINE_DONE|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  End;
  // ---------------- phase 2e: GND polygon outlines, then repour everything
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If Fld(S,0)<>'POLY' Then Continue;
   P:=Objs.Items(I);P.BeginModify;P.PointCount:=4;
   SetPolySeg(P,0,Num(S,2),Num(S,3));SetPolySeg(P,1,Num(S,4),Num(S,3));SetPolySeg(P,2,Num(S,4),Num(S,5));SetPolySeg(P,3,Num(S,2),Num(S,5));
   P.EndModify;Say('POLY_RESHAPED|'+P.Name);
  End;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
  Polys:=TInterfaceList.Create;
  Try P:=It.FirstPCBObject;While P<>Nil Do Begin Polys.Add(P);P:=It.NextPCBObject;End;Finally B.BoardIterator_Destroy(It);End;
  PCBServer.PreProcess;
  Try For K:=0 To Polys.Count-1 Do Begin P:=Polys.Items(K);P.SetState_CopperPourInvalid;P.Rebuild;P.CopperPourValidate;RB:=P.BoundingRectangle;
   Say('POLY_REBUILT|'+P.Name+'|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));End;
  Finally PCBServer.PostProcess;End;
  B.ConnectivelyValidateNets;B.ViewManager_FullUpdate;
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');
  If D.Modified Then Raise('still modified after save');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong reopened board');
  Say('REOPENED|MODIFIED='+BoolToStr(D.Modified,True));
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
  Try C:=It.FirstPCBObject;While C<>Nil Do Begin
   Log.Add('READBACK|'+C.Name.Text+'|'+Layer2String(C.Layer)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|ROT='+FloatToStr(C.Rotation)+'|UID='+C.SourceUniqueId);
   C:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePadObject));
  Try Pd:=It.FirstPCBObject;While Pd<>Nil Do Begin
   If Not Pd.InComponent Then Log.Add('READBACK_FREEPAD|'+Pd.Name+'|'+Layer2String(Pd.Layer)+'|X='+MM(Pd.X)+'|Y='+MM(Pd.Y));
   Pd:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  RB:=B.BoardOutline.BoundingRectangle;Say('READBACK_OUTLINE|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Ops.Free;Objs.Free;Log.Free;End;
End;
