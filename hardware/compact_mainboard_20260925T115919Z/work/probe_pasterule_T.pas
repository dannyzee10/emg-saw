// DISPOSABLE PROBE (template @ROOT@/@LOG@): create a PasteMaskExpansion rule, save, reopen, read it back.
Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';
Const OutFile='@LOG@';
Var Log:TStringList;
Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;R:IPCB_Rule;It:IPCB_BoardIterator;N:Integer;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  If D.Modified Then Raise('disposable has unsaved changes');
  R:=PCBServer.PCBRuleFactory(eRule_PasteMaskExpansion);If R=Nil Then Raise('factory nil');
  Say('FACTORY_OK');
  R.Name:='PROBE_PASTE_NONE';R.Scope1Expression:='IsPad And InComponent(''TP_GND'')';
  R.Expansion:=MMsToCoord(-1.0);
  Say('SET_OK|EXP='+FloatToStr(CoordToMMs(R.Expansion)));
  B.AddPCBObject(R);Say('ADDED|PRIORITY='+IntToStr(R.Priority));
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  N:=0;It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
  Try R:=It.FirstPCBObject;While R<>Nil Do Begin
    If R.Name='PROBE_PASTE_NONE' Then Begin Inc(N);Say('READBACK|KIND='+IntToStr(Ord(R.RuleKind))+'|SCOPE='+R.Scope1Expression+'|EXP='+FloatToStr(CoordToMMs(R.Expansion)));End;
    R:=It.NextPCBObject;End;
  Finally B.BoardIterator_Destroy(It);End;
  Say('READBACK_COUNT='+IntToStr(N));
  Client.CloseDocument(D);
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
