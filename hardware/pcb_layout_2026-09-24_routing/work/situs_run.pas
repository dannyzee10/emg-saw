// Opens the Situs strategy dialog on the ROUTING COPY ("Route All" is clicked externally by win.ps1).
// Pre-routes are locked in the dialog (default checked). The board is NOT saved here; save_board.pas does that
// only after the result has been inspected.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\SITUS_RUN_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;L:TStringList;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  If D.Modified Then Raise('unsaved changes present - refusing to autoroute');
  L.Add('BEFORE_AUTOROUTE '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  ResetParameters;AddStringParameter('Action','All');RunProcess('PCB:AutoRoute');
  L.Add('RUNPROCESS_RETURNED '+DateTimeToStr(Now)+'|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
