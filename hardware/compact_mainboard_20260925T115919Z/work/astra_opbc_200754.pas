// Close other copies of EMG_MainBoard_Layout.PcbDoc that have NO unsaved changes, then open the target project and its PCB
// inside the project.  No edits, no saves.  (template: C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\ / C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\ASTRA_OPEN_BC.txt substituted by mkvariant.py)
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\ASTRA_OPEN_BC.txt';
Const Others='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\MainBoard\EMG_MainBoard_Layout.PcbDoc;C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\EMG_MainBoard_Layout.PcbDoc;C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2stack6\MainBoard\EMG_MainBoard_Layout.PcbDoc;C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Procedure RunFixed;
Var D:IServerDocument;L,O:TStringList;W:IWorkspace;P:IProject;B:IPCB_Board;I:Integer;
Begin
 L:=TStringList.Create;O:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  O.Delimiter:=';';O.StrictDelimiter:=True;O.DelimitedText:=Others;
  For I:=0 To O.Count-1 Do Begin
   D:=Client.GetDocumentByPath(O[I]);
   If D<>Nil Then Begin
    If D.Modified Then L.Add('OTHER_MODIFIED_LEFT_OPEN|'+O[I]) Else Begin Client.CloseDocument(D);L.Add('OTHER_CLOSED_UNMODIFIED|'+O[I]);End;
   End;
  End;
  W:=GetWorkspace;
  ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',Root+'EMG_MainBoard_Layout.PrjPcb');RunProcess('WorkspaceManager:OpenObject');
  P:=W.DM_GetProjectFromPath(Root+'EMG_MainBoard_Layout.PrjPcb');If P=Nil Then Raise('project not opened');
  L.Add('PROJECT_OPEN|DOCS='+IntToStr(P.DM_LogicalDocumentCount));
  D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board '+B.FileName);
  L.Add('PCB_OPEN|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;O.Free;End;
End;
