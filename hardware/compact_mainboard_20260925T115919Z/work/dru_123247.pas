// Read-only dump of every design rule: name, kind, priority, enabled, scopes; routing-layer flags and per-layer widths
// for all six copper layers.  Nothing is changed or saved.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2stack6\MainBoard\STACK6_PROBE.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\RULES_PROBE6L.txt';
Var Log:TStringList;B:IPCB_Board;

Procedure Say(S:String);Begin Log.Add(S);End;

Function LName(L:TLayer):String;
Begin
 If L=eTopLayer Then Result:='TOP' Else If L=eMidLayer1 Then Result:='MID1' Else If L=eMidLayer2 Then Result:='MID2'
 Else If L=eMidLayer3 Then Result:='MID3' Else If L=eMidLayer4 Then Result:='MID4' Else Result:='BOT';
End;

Procedure RunFixed;
Var D:IServerDocument;It:IPCB_BoardIterator;R:IPCB_Rule;RL:IPCB_RoutingLayersRule;WR:IPCB_MaxMinWidthConstraint;S,X:String;K:Integer;L:TLayer;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
  Try
   R:=It.FirstPCBObject;
   While R<>Nil Do Begin
    S:='RULE|'+R.Name+'|KIND='+IntToStr(Ord(R.RuleKind))+'|PRI='+IntToStr(R.Priority)+'|DRC='+BoolToStr(R.DRCEnabled,True)+
       '|S1='+R.Scope1Expression+'|S2='+R.Scope2Expression;
    If R.RuleKind=eRule_RoutingLayers Then Begin
     RL:=R;X:='';
     For K:=0 To 5 Do Begin
      If K=0 Then L:=eTopLayer Else If K=1 Then L:=eMidLayer1 Else If K=2 Then L:=eMidLayer2 Else If K=3 Then L:=eMidLayer3 Else If K=4 Then L:=eMidLayer4 Else L:=eBottomLayer;
      X:=X+'|'+LName(L)+'='+BoolToStr(RL.RoutingLayers(L),True);
     End;
     S:=S+X;
    End;
    If R.RuleKind=eRule_MaxMinWidth Then Begin
     WR:=R;X:='';
     For K:=0 To 5 Do Begin
      If K=0 Then L:=eTopLayer Else If K=1 Then L:=eMidLayer1 Else If K=2 Then L:=eMidLayer2 Else If K=3 Then L:=eMidLayer3 Else If K=4 Then L:=eMidLayer4 Else L:=eBottomLayer;
      X:=X+'|'+LName(L)+'='+FloatToStr(CoordToMMs(WR.MinWidth(L)))+'/'+FloatToStr(CoordToMMs(WR.FavoredWidth(L)))+'/'+FloatToStr(CoordToMMs(WR.MaxWidth(L)));
     End;
     S:=S+X;
    End;
    Say(S);
    R:=It.NextPCBObject;
   End;
  Finally B.BoardIterator_Destroy(It);End;
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
