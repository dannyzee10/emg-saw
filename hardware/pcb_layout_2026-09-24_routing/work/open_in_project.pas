// Close the routing PCB (no save), open its project in the workspace, reopen the PCB inside it and
// report the Modified flag at each step. Writes nothing to disk except the log.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const PrjPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PrjPcb';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\OPEN_IN_PROJECT_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;W:IWorkspace;P:IProject;I:Integer;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);
  If D<>Nil Then Begin L.Add('OPEN_BEFORE|MODIFIED='+BoolToStr(D.Modified,True));D.Modified:=False;Client.CloseDocument(D);L.Add('CLOSED_WITHOUT_SAVE');End;
  W:=GetWorkspace;
  For I:=0 To W.DM_ProjectCount-1 Do L.Add('WS_PROJECT|'+W.DM_Projects(I).DM_ProjectFullPath);
  ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',PrjPath);RunProcess('WorkspaceManager:OpenObject');
  L.Add('PROJECT_OPEN_REQUESTED');L.SaveToFile(OutFile);
  For I:=0 To W.DM_ProjectCount-1 Do L.Add('WS_PROJECT_AFTER|'+W.DM_Projects(I).DM_ProjectFullPath);
  P:=W.DM_GetProjectFromPath(PrjPath);
  If P=Nil Then L.Add('PROJECT_NOT_FOUND') Else Begin
   L.Add('PROJECT|DOCS='+IntToStr(P.DM_LogicalDocumentCount));
   For I:=0 To P.DM_LogicalDocumentCount-1 Do L.Add('DOC|'+P.DM_LogicalDocuments(I).DM_FullPath);
  End;
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  L.Add('REOPENED|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
