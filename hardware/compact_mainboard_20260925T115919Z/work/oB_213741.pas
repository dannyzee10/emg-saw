// Close the (saved) routing-revision PCB if it has no unsaved changes, open candidate B's project and PCB,
// bring B to the front and zoom to the board.  No edits, no saves.
Const RoutingPcb='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_applyB\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PrjPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PrjPcb';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\OPEN_B_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;W:IWorkspace;P:IProject;B:IPCB_Board;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(RoutingPcb);
  If D<>Nil Then Begin
   If D.Modified Then L.Add('ROUTING_PCB_MODIFIED_LEFT_OPEN') Else Begin Client.CloseDocument(D);L.Add('ROUTING_PCB_CLOSED_UNMODIFIED');End;
  End;
  W:=GetWorkspace;
  ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',PrjPath);RunProcess('WorkspaceManager:OpenObject');
  P:=W.DM_GetProjectFromPath(PrjPath);If P=Nil Then Raise('B project not opened');
  L.Add('B_PROJECT_OPEN|DOCS='+IntToStr(P.DM_LogicalDocumentCount));
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  ResetParameters;AddStringParameter('Action','Board');RunProcess('PCB:Zoom');
  L.Add('B_OPEN|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
