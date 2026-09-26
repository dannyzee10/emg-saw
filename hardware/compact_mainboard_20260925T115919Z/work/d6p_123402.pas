// Headless native batch DRC on the routing revision (read-only w.r.t. design data).
// The Boolean is processing status only; the HTML report is the evidence.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2stack6\MainBoard\STACK6_PROBE.PcbDoc';
Const Report='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\DRC_PROBE6L.txt.html';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\DRC_PROBE6L.txt';
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;L:TStringList;Ok:Boolean;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile+'.part');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  L.Add('MODIFIED_BEFORE='+BoolToStr(D.Modified,True));
  Ok:=B.RunBatchDesignRuleCheck(Report,eDRC_HTML,False,False);
  L.Add('RETURNED='+BoolToStr(Ok,True)+' '+DateTimeToStr(Now));
  L.Add('MODIFIED_AFTER='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
