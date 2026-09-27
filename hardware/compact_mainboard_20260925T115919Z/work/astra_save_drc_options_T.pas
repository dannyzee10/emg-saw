// Save native DRC batch option changes. No geometry operations.
Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';
Const OutFile='@LOG@';
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;L:TStringList;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('Target must already be open');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Raise('No current PCB');If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong PCB');
  L.Add('PHASE1_OK|SAVE_DRC_OPTIONS_ONLY|MODIFIED_BEFORE='+BoolToStr(D.Modified,True));
  L.SaveToFile(OutFile+'.part');
  If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('Save failed');
  If D.Modified Then Raise('Still modified');L.Add('SAVED');L.SaveToFile(OutFile+'.part');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('Reopen failed');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong reopened PCB');
  If D.Modified Then Raise('Reopened modified');
  L.Add('AFTER_REOPEN|MODIFIED=False|DRC_OPTIONS_SAVED');L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;

