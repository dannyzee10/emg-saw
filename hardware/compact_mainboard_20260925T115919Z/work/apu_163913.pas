// Generic native writer for the routing revision ONLY.
// Reads work\OPS.txt (pipe-separated), validates EVERYTHING first (phase 1, no changes),
// then applies in one PreProcess/PostProcess transaction (phase 2), rebuilds the GND polygons,
// saves, closes, reopens and reads back.  Ops:
//   RULE_CLR|name|gap_mm|scope1|scope2
//   DEL_TRACK|net|layer|x1|y1|x2|y2          (exactly one match within 2 um, either direction)
//   TRACK|net|layer|x1|y1|x2|y2|w
//   VIA|net|x|y|d|h
//   POLY|name|net|layer|x,y;x,y;...     CUTOUT|layer|x,y;x,y;...
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OpsFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\work\OPS_AU_UART.txt';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\APPLY_AU_UART_LOG.txt';
Var Log:TStringList;B:IPCB_Board;MatchCount,Failures:Integer;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Procedure Fail(S:String);Begin Inc(Failures);Say('PHASE1_FAIL|'+S);End;

Function Fld(S:String;N:Integer):String;
Var I,P:Integer;Rest:String;
Begin
 Rest:=S;
 For I:=0 To N-1 Do Begin P:=Pos('|',Rest);If P=0 Then Begin Result:='';Exit;End;Rest:=Copy(Rest,P+1,Length(Rest));End;
 P:=Pos('|',Rest);If P=0 Then Result:=Rest Else Result:=Copy(Rest,1,P-1);
End;

Function Num(S:String;N:Integer):Double;Begin Result:=StrToFloat(Fld(S,N));End;

Function Item(S,Sep:String;N:Integer):String;
Var I,P:Integer;Rest:String;
Begin
 Rest:=S;
 For I:=0 To N-1 Do Begin P:=Pos(Sep,Rest);If P=0 Then Begin Result:='';Exit;End;Rest:=Copy(Rest,P+Length(Sep),Length(Rest));End;
 P:=Pos(Sep,Rest);If P=0 Then Result:=Rest Else Result:=Copy(Rest,1,P-1);
End;

Function CountItems(S,Sep:String):Integer;
Var Rest:String;P:Integer;
Begin Result:=1;Rest:=S;P:=Pos(Sep,Rest);While P>0 Do Begin Inc(Result);Rest:=Copy(Rest,P+Length(Sep),Length(Rest));P:=Pos(Sep,Rest);End;End;

Function LayerOf(S:String):TLayer;
Begin
 If S='Top Layer' Then Result:=eTopLayer
 Else If S='Mid Layer 1' Then Result:=eMidLayer1
 Else If S='Mid Layer 2' Then Result:=eMidLayer2
 Else If S='Mid Layer 3' Then Result:=eMidLayer3
 Else If S='Mid Layer 4' Then Result:=eMidLayer4
 Else If S='Bottom Layer' Then Result:=eBottomLayer
 Else Raise('Unknown layer '+S);
End;

Function FindNet(Name:String):IPCB_Net;
Var It:IPCB_BoardIterator;N:IPCB_Net;
Begin
 Result:=Nil;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eNetObject));
 Try N:=It.FirstPCBObject;While N<>Nil Do Begin If N.Name=Name Then Begin Result:=N;Exit;End;N:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Function CloseTo(A:TCoord;V:Double):Boolean;Begin Result:=Abs(CoordToMMs(A)-V)<0.002;End;

Function FindTrack(Net,Lay:String;X1,Y1,X2,Y2:Double):IPCB_Track;
Var It:IPCB_BoardIterator;T:IPCB_Track;L:TLayer;
Begin
 Result:=Nil;MatchCount:=0;L:=LayerOf(Lay);
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(MkSet(L));It.AddFilter_ObjectSet(MkSet(eTrackObject));
 Try T:=It.FirstPCBObject;While T<>Nil Do Begin
  If (Not T.InComponent) And (T.Net<>Nil) Then If T.Net.Name=Net Then
   If ((CloseTo(T.X1,X1) And CloseTo(T.Y1,Y1) And CloseTo(T.X2,X2) And CloseTo(T.Y2,Y2)) Or (CloseTo(T.X1,X2) And CloseTo(T.Y1,Y2) And CloseTo(T.X2,X1) And CloseTo(T.Y2,Y1))) Then Begin Inc(MatchCount);Result:=T;End;
  T:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;

Function FindVia(Net:String;X,Y:Double):IPCB_Via;
Var It:IPCB_BoardIterator;V:IPCB_Via;
Begin
 Result:=Nil;MatchCount:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eViaObject));
 Try V:=It.FirstPCBObject;While V<>Nil Do Begin
  If CloseTo(V.X,X) Then If CloseTo(V.Y,Y) Then Begin
   If Net='*' Then Begin Inc(MatchCount);Result:=V;End
   Else If V.Net<>Nil Then If V.Net.Name=Net Then Begin Inc(MatchCount);Result:=V;End;
  End;
  V:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;

Function RuleExists(Name:String):Boolean;
Var It:IPCB_BoardIterator;R:IPCB_Rule;
Begin
 Result:=False;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
 Try R:=It.FirstPCBObject;While R<>Nil Do Begin If R.Name=Name Then Result:=True;R:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Function FindRule(Name:String):IPCB_Rule;
Var It:IPCB_BoardIterator;R:IPCB_Rule;
Begin
 Result:=Nil;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
 Try R:=It.FirstPCBObject;While R<>Nil Do Begin If R.Name=Name Then Result:=R;R:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Function CountPolys(Name:String):Integer;
Var It:IPCB_BoardIterator;P:IPCB_Polygon;
Begin
 Result:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=Name Then Inc(Result);P:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Procedure RenamePoly(OldName,NewName:String);
Var It:IPCB_BoardIterator;P:IPCB_Polygon;
Begin
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=OldName Then Begin P.BeginModify;P.Name:=NewName;P.EndModify;Say('POLY_RENAMED|'+OldName+'|'+NewName);End;P:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Procedure SetLayers(RL:IPCB_RoutingLayersRule;S:String;F:Integer);
Begin
 RL.RoutingLayers(eTopLayer):=Fld(S,F)='1';RL.RoutingLayers(eMidLayer1):=Fld(S,F+1)='1';
 RL.RoutingLayers(eMidLayer2):=Fld(S,F+2)='1';RL.RoutingLayers(eBottomLayer):=Fld(S,F+3)='1';
 If Fld(S,F+4)<>'' Then RL.RoutingLayers(eMidLayer3):=Fld(S,F+4)='1';If Fld(S,F+5)<>'' Then RL.RoutingLayers(eMidLayer4):=Fld(S,F+5)='1';
 Say('RL|'+RL.Name+'|TOP='+BoolToStr(RL.RoutingLayers(eTopLayer),True)+'|MID1='+BoolToStr(RL.RoutingLayers(eMidLayer1),True)+'|MID2='+BoolToStr(RL.RoutingLayers(eMidLayer2),True)+'|BOT='+BoolToStr(RL.RoutingLayers(eBottomLayer),True)+'|MID3='+BoolToStr(RL.RoutingLayers(eMidLayer3),True)+'|MID4='+BoolToStr(RL.RoutingLayers(eMidLayer4),True)+'|PRIORITY='+IntToStr(RL.Priority));
End;

Procedure Counts(Tag:String);
Var It:IPCB_BoardIterator;O:IPCB_Primitive;NT,NV,NR,NTT:Integer;
Begin
 NT:=0;NV:=0;NR:=0;NTT:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eTrackObject,eViaObject,eRuleObject));
 Try O:=It.FirstPCBObject;While O<>Nil Do Begin
  If O.ObjectId=eTrackObject Then Begin If (Not O.InComponent) And (O.Net<>Nil) Then Inc(NT);End
  Else If O.ObjectId=eViaObject Then Begin Inc(NV);If O.IsTenting_Top And O.IsTenting_Bottom Then Inc(NTT);End Else Inc(NR);
  O:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 Say(Tag+'|NET_TRACKS='+IntToStr(NT)+'|VIAS='+IntToStr(NV)+'|TENTED_BOTH='+IntToStr(NTT)+'|RULES='+IntToStr(NR));
End;

Procedure AddPoly(S:String);
Var P:IPCB_Polygon;V:TPolySegment;Pts:String;I,NP:Integer;N:IPCB_Net;
Begin
 N:=FindNet(Fld(S,2));Pts:=Fld(S,4);NP:=CountItems(Pts,';');
 P:=PCBServer.PCBObjectFactory(ePolyObject,eNoDimension,eCreate_Default);
 P.Name:=Fld(S,1);P.Net:=N;P.Layer:=LayerOf(Fld(S,3));P.PolyHatchStyle:=ePolySolid;
 P.RemoveDead:=True;P.PourOver:=ePolygonPourOver_SameNet;P.RemoveNarrowNecks:=True;P.NeckWidthThreshold:=MMsToCoord(0.20);
 P.RemoveIslandsByArea:=False;P.ArcApproximation:=MMsToCoord(0.025);
 P.PointCount:=NP;
 For I:=0 To NP-1 Do Begin
  V:=P.Segments[I];V.Kind:=ePolySegmentLine;
  V.Vx:=MMsToCoord(StrToFloat(Item(Item(Pts,';',I),',',0)));V.Vy:=MMsToCoord(StrToFloat(Item(Item(Pts,';',I),',',1)));
  P.Segments[I]:=V;
 End;
 B.AddPCBObject(P);Say('POLY_ADDED|'+P.Name+'|'+Fld(S,2)+'|'+Fld(S,3)+'|VERTS='+IntToStr(NP));
End;

Procedure AddCutout(S:String);
Var R:IPCB_Region;C:IPCB_Contour;Pts:String;I,NP:Integer;
Begin
 Pts:=Fld(S,2);NP:=CountItems(Pts,';');C:=PCBServer.PCBContourFactory;
 For I:=0 To NP-1 Do C.AddPoint(MMsToCoord(StrToFloat(Item(Item(Pts,';',I),',',0))),MMsToCoord(StrToFloat(Item(Item(Pts,';',I),',',1))));
 R:=PCBServer.PCBObjectFactory(eRegionObject,eNoDimension,eCreate_Default);R.SetOutlineContour(C);R.Layer:=LayerOf(Fld(S,1));R.Kind:=eRegionKind_Cutout;
 B.AddPCBObject(R);Say('CUTOUT_ADDED|'+Fld(S,1)+'|VERTS='+IntToStr(NP));
End;

Procedure RebuildPolys;
Var It:IPCB_BoardIterator;P:IPCB_Polygon;Polys:TInterfaceList;I:Integer;
Begin
 Polys:=TInterfaceList.Create;
 Try
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
  Try P:=It.FirstPCBObject;While P<>Nil Do Begin Polys.Add(P);P:=It.NextPCBObject;End;Finally B.BoardIterator_Destroy(It);End;
  PCBServer.PreProcess;
  Try
   For I:=0 To Polys.Count-1 Do Begin
    P:=Polys.Items(I);P.SetState_CopperPourInvalid;P.Rebuild;P.CopperPourValidate;
    Say('POLY_REBUILT|'+P.Name+'|INVALID='+BoolToStr(P.GetState_CopperPourInvalid,True)+'|AREA='+FloatToStr(P.AreaSize));
   End;
  Finally PCBServer.PostProcess;End;
 Finally Polys.Free;End;
End;

Procedure RunFixed;
Var D:IServerDocument;Ops:TStringList;I,K,Cnt:Integer;S,Kind:String;N:IPCB_Net;T:IPCB_Track;V:IPCB_Via;R:IPCB_ClearanceConstraint;
    RL:IPCB_RoutingLayersRule;WR:IPCB_MaxMinWidthConstraint;Lay:TLayer;NTent:Integer;SR:IPCB_Rule;
    NTrack,NVia,NDel,NRule:Integer;
Begin
 Log:=TStringList.Create;Ops:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  Ops.LoadFromFile(OpsFile);Say('OPS_LINES='+IntToStr(Ops.Count));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Raise('no board');If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  If D.Modified Then Raise('PCB has unsaved changes - refusing to write');
  Counts('BEFORE');
  // ---------- phase 1: validate everything, change nothing
  NTrack:=0;NVia:=0;NDel:=0;NRule:=0;NTent:=0;Failures:=0;
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];If (S='') Or (Copy(S,1,1)='#') Then Continue;Kind:=Fld(S,0);
   If Kind='TRACK' Then Begin If FindNet(Fld(S,1))=Nil Then Begin Fail('line '+IntToStr(I)+' unknown net '+Fld(S,1));Continue;End;LayerOf(Fld(S,2));Num(S,7);Inc(NTrack);End
   Else If Kind='VIA' Then Begin If FindNet(Fld(S,1))=Nil Then Begin Fail('line '+IntToStr(I)+' unknown net '+Fld(S,1));Continue;End;Num(S,5);Inc(NVia);End
   Else If Kind='DEL_TRACK' Then Begin T:=FindTrack(Fld(S,1),Fld(S,2),Num(S,3),Num(S,4),Num(S,5),Num(S,6));Cnt:=MatchCount;If Cnt<>1 Then Begin Fail('line '+IntToStr(I)+' delete match count '+IntToStr(Cnt));Continue;End;Inc(NDel);End
   Else If Kind='RULE_CLR' Then Begin If RuleExists(Fld(S,1)) Then Begin Fail('rule exists '+Fld(S,1));Continue;End;Num(S,2);Inc(NRule);End
   Else If Kind='RULE_RL' Then Begin If RuleExists(Fld(S,1)) Then Begin Fail('rule exists '+Fld(S,1));Continue;End;Inc(NRule);End
   Else If Kind='RULE_SMX' Then Begin If RuleExists(Fld(S,1)) Then Begin Fail('rule exists '+Fld(S,1));Continue;End;Num(S,3);Inc(NRule);End
   Else If (Kind='SET_WIDTH') Or (Kind='SET_RL') Then Begin If FindRule(Fld(S,1))=Nil Then Begin Fail('missing rule '+Fld(S,1));Continue;End;Inc(NRule);End
   Else If Kind='DEL_VIA' Then Begin V:=FindVia(Fld(S,1),Num(S,2),Num(S,3));If MatchCount<>1 Then Begin Fail('line '+IntToStr(I)+' del via match '+IntToStr(MatchCount));Continue;End;Inc(NDel);End
   Else If Kind='TENT_VIA' Then Begin V:=FindVia('*',Num(S,1),Num(S,2));If MatchCount<>1 Then Begin Fail('line '+IntToStr(I)+' tent via match '+IntToStr(MatchCount));Continue;End;End
   Else If Kind='POLY' Then Begin If FindNet(Fld(S,2))=Nil Then Begin Fail('poly net '+Fld(S,2));Continue;End;LayerOf(Fld(S,3));If CountItems(Fld(S,4),';')<3 Then Begin Fail('poly vertices');Continue;End;End
   Else If Kind='RENAME_POLY' Then Begin If CountPolys(Fld(S,1))<>1 Then Begin Fail('rename source count '+Fld(S,1));Continue;End;If CountPolys(Fld(S,2))<>0 Then Begin Fail('rename target exists '+Fld(S,2));Continue;End;End
   Else If Kind='CUTOUT' Then Begin LayerOf(Fld(S,1));If CountItems(Fld(S,2),';')<3 Then Begin Fail('cutout vertices');Continue;End;End
   Else If Kind='WIDEN_TRACK' Then Begin T:=FindTrack(Fld(S,1),Fld(S,2),Num(S,3),Num(S,4),Num(S,5),Num(S,6));Cnt:=MatchCount;If Cnt<>1 Then Begin Fail('line '+IntToStr(I)+' widen match count '+IntToStr(Cnt));Continue;End;Num(S,7);End
   Else Begin Fail('line '+IntToStr(I)+' unknown op '+Kind);Continue;End;
  End;
  If Failures>0 Then Begin Say('ABORTED_NO_CHANGES|FAILURES='+IntToStr(Failures));Say('COMPLETE_WITH_ABORT');Exit;End;
  Say('PHASE1_OK|TRACKS='+IntToStr(NTrack)+'|VIAS='+IntToStr(NVia)+'|DELETES='+IntToStr(NDel)+'|RULES='+IntToStr(NRule));
  // ---------- phase 2: apply
  PCBServer.PreProcess;
  Try
   For I:=0 To Ops.Count-1 Do Begin
    S:=Ops[I];If (S='') Or (Copy(S,1,1)='#') Then Continue;Kind:=Fld(S,0);
    If Kind='DEL_TRACK' Then Begin
     T:=FindTrack(Fld(S,1),Fld(S,2),Num(S,3),Num(S,4),Num(S,5),Num(S,6));Cnt:=MatchCount;B.RemovePCBObject(T);
    End Else If Kind='TRACK' Then Begin
     N:=FindNet(Fld(S,1));T:=PCBServer.PCBObjectFactory(eTrackObject,eNoDimension,eCreate_Default);
     T.Layer:=LayerOf(Fld(S,2));T.X1:=MMsToCoord(Num(S,3));T.Y1:=MMsToCoord(Num(S,4));T.X2:=MMsToCoord(Num(S,5));T.Y2:=MMsToCoord(Num(S,6));
     T.Width:=MMsToCoord(Num(S,7));T.Net:=N;B.AddPCBObject(T);
    End Else If Kind='VIA' Then Begin
     N:=FindNet(Fld(S,1));V:=PCBServer.PCBObjectFactory(eViaObject,eNoDimension,eCreate_Default);
     V.X:=MMsToCoord(Num(S,2));V.Y:=MMsToCoord(Num(S,3));V.Size:=MMsToCoord(Num(S,4));V.HoleSize:=MMsToCoord(Num(S,5));
     V.LowLayer:=eTopLayer;V.HighLayer:=eBottomLayer;V.Net:=N;
     B.AddPCBObject(V);
     If Fld(S,6)='T' Then Begin V.IsTenting_Top:=True;V.IsTenting_Bottom:=True;End;
    End Else If Kind='RULE_CLR' Then Begin
     R:=PCBServer.PCBRuleFactory(eRule_Clearance);If R=Nil Then Raise('rule factory');
     R.Name:=Fld(S,1);R.Gap:=MMsToCoord(Num(S,2));R.Scope1Expression:=Fld(S,3);R.Scope2Expression:=Fld(S,4);R.DRCEnabled:=True;
     B.AddPCBObject(R);Say('RULE_ADDED|'+R.Name+'|PRIORITY='+IntToStr(R.Priority)+'|GAP_MM='+FloatToStr(CoordToMMs(R.Gap)));
    End Else If Kind='DEL_VIA' Then Begin
     V:=FindVia(Fld(S,1),Num(S,2),Num(S,3));B.RemovePCBObject(V);
    End Else If Kind='TENT_VIA' Then Begin
     V:=FindVia('*',Num(S,1),Num(S,2));V.IsTenting_Top:=Fld(S,3)='1';V.IsTenting_Bottom:=Fld(S,4)='1';Inc(NTent);
    End Else If Kind='POLY' Then Begin
     AddPoly(S);
    End Else If Kind='RENAME_POLY' Then Begin
     RenamePoly(Fld(S,1),Fld(S,2));
    End Else If Kind='CUTOUT' Then Begin
     AddCutout(S);
    End Else If Kind='WIDEN_TRACK' Then Begin
     T:=FindTrack(Fld(S,1),Fld(S,2),Num(S,3),Num(S,4),Num(S,5),Num(S,6));Cnt:=MatchCount;T.Width:=MMsToCoord(Num(S,7));
    End Else If Kind='RULE_SMX' Then Begin
     SR:=PCBServer.PCBRuleFactory(eRule_SolderMaskExpansion);SR.Name:=Fld(S,1);SR.Scope1Expression:=Fld(S,2);SR.Expansion:=MMsToCoord(Num(S,3));SR.DRCEnabled:=True;B.AddPCBObject(SR);
     Say('RULE_ADDED|'+SR.Name+'|PRIORITY='+IntToStr(SR.Priority)+'|EXP_MM='+FloatToStr(CoordToMMs(SR.Expansion)));
    End Else If Kind='RULE_RL' Then Begin
     RL:=PCBServer.PCBRuleFactory(eRule_RoutingLayers);If RL=Nil Then Raise('RL factory');
     RL.Name:=Fld(S,1);RL.Scope1Expression:=Fld(S,2);RL.DRCEnabled:=True;B.AddPCBObject(RL);SetLayers(RL,S,3);
    End Else If Kind='SET_RL' Then Begin
     RL:=FindRule(Fld(S,1));SetLayers(RL,S,2);
    End Else If Kind='SET_WIDTH' Then Begin
     WR:=FindRule(Fld(S,1));
     For K:=0 To 5 Do Begin
      If K=0 Then Lay:=eTopLayer Else If K=1 Then Lay:=eMidLayer1 Else If K=2 Then Lay:=eMidLayer2 Else If K=3 Then Lay:=eMidLayer3 Else If K=4 Then Lay:=eMidLayer4 Else Lay:=eBottomLayer;
      WR.MinWidth(Lay):=MMsToCoord(Num(S,2));WR.MaxWidth(Lay):=MMsToCoord(Num(S,4));WR.FavoredWidth(Lay):=MMsToCoord(Num(S,3));
     End;
     Say('WIDTH|'+WR.Name+'|TOP_MIN='+FloatToStr(CoordToMMs(WR.MinWidth(eTopLayer)))+'|FAV='+FloatToStr(CoordToMMs(WR.FavoredWidth(eTopLayer)))+'|MAX='+FloatToStr(CoordToMMs(WR.MaxWidth(eTopLayer))));
    End;
   End;
  Finally PCBServer.PostProcess;End;
  Say('PHASE2_APPLIED|TENTED='+IntToStr(NTent));
  RebuildPolys;
  B.ConnectivelyValidateNets;B.ViewManager_FullUpdate;
  Counts('AFTER_APPLY');
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');
  If D.Modified Then Raise('still modified after save');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong reopened board');
  If D.Modified Then Raise('reopened modified');
  Counts('AFTER_REOPEN');
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Ops.Free;Log.Free;End;
End;
