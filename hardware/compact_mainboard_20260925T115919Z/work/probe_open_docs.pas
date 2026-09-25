// Read-only: list every project in the workspace and, for each PCB/SCH document that is open, its path and
// Modified flag.  Then bring the worktree routing PCB to the front and zoom to fit.  No edits, no saves.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\OPEN_DOCS_LOG.txt';
Procedure RunFixed;
Var W:IWorkspace;P:IProject;I,J:Integer;F:String;D:IServerDocument;L:TStringList;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));
  W:=GetWorkspace;
  For I:=0 To W.DM_ProjectCount-1 Do Begin
   P:=W.DM_Projects(I);L.Add('PROJECT|'+P.DM_ProjectFullPath);
   For J:=0 To P.DM_LogicalDocumentCount-1 Do Begin
    F:=P.DM_LogicalDocuments(J).DM_FullPath;D:=Client.GetDocumentByPath(F);
    If D<>Nil Then L.Add('  OPEN|MODIFIED='+BoolToStr(D.Modified,True)+'|'+F);
   End;
   For J:=0 To P.DM_PhysicalDocumentCount-1 Do Begin
    F:=P.DM_PhysicalDocuments(J).DM_FullPath;D:=Client.GetDocumentByPath(F);
    If D<>Nil Then L.Add('  OPEN_PHYS|MODIFIED='+BoolToStr(D.Modified,True)+'|'+F);
   End;
  End;
  D:=Client.GetDocumentByPath(PcbPath);
  If D<>Nil Then Begin Client.ShowDocument(D);ResetParameters;AddStringParameter('Action','All');RunProcess('PCB:Zoom');L.Add('SHOWN_WORKTREE_PCB');End;
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
