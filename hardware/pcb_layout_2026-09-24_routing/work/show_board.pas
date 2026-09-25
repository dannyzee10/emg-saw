// Open the worktree routing project, open its PCB inside the project, bring it to the front and zoom to fit.
// Read-only: no edits, no save.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PrjPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PrjPcb';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\SHOW_BOARD_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;W:IWorkspace;P:IProject;B:IPCB_Board;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  W:=GetWorkspace;P:=W.DM_GetProjectFromPath(PrjPath);
  If P=Nil Then Begin
   ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',PrjPath);RunProcess('WorkspaceManager:OpenObject');
   P:=W.DM_GetProjectFromPath(PrjPath);
  End;
  If P=Nil Then Raise('project not opened');
  L.Add('PROJECT_OPEN');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');
  Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  ResetParameters;AddStringParameter('Action','All');RunProcess('PCB:Zoom');
  L.Add('SHOWN|'+B.FileName+'|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
