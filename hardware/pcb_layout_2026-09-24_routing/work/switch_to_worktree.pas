// Move the Altium session from the main-checkout routing copy (left untouched, batch-3 state) to the
// worktree routing copy: close the old PCB without saving, open the worktree project, reopen its PCB inside it.
Const OldPcb='C:\Users\PMLS\Desktop\emg-saw\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PrjPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PrjPcb';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\SWITCH_TO_WORKTREE_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;W:IWorkspace;P:IProject;I:Integer;B:IPCB_Board;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(OldPcb);
  If D<>Nil Then Begin L.Add('OLD_OPEN|MODIFIED='+BoolToStr(D.Modified,True));D.Modified:=False;Client.CloseDocument(D);L.Add('OLD_CLOSED_WITHOUT_SAVE');End
  Else L.Add('OLD_NOT_OPEN');
  W:=GetWorkspace;
  ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',PrjPath);RunProcess('WorkspaceManager:OpenObject');
  P:=W.DM_GetProjectFromPath(PrjPath);
  If P=Nil Then Raise('worktree project not in workspace');
  L.Add('PROJECT_OPEN|DOCS='+IntToStr(P.DM_LogicalDocumentCount));
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  L.Add('OPENED|'+B.FileName+'|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
