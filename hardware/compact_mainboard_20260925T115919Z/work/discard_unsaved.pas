// User-approved (24 Sep): discard an unsaved in-memory GUI edit of the ROUTING COPY only.
// Clears the in-memory Modified flag, closes without saving, reopens the saved file.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\DISCARD_UNSAVED_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('routing PCB not open');
  L.Add('MODIFIED_BEFORE='+BoolToStr(D.Modified,True));
  D.Modified:=False;Client.CloseDocument(D);L.Add('CLOSED_WITHOUT_SAVE');
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  L.Add('REOPENED|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
