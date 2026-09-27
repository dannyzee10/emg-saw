Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\';
Procedure RunFixed;
Var W:IWorkspace;P:IProject;D:IServerDocument;L:TStringList;I,J,N:Integer;F:String;
Begin
 L:=TStringList.Create;N:=0;
 Try
  W:=GetWorkspace;
  For I:=0 To W.DM_ProjectCount-1 Do Begin
   P:=W.DM_Projects(I);L.Add('PROJECT|'+P.DM_ProjectFullPath);
   D:=P.DM_ServerDocument;If D<>Nil Then Begin L.Add('PROJECT_MODIFIED='+BoolToStr(D.Modified,True));If D.Modified Then Inc(N);End;
   For J:=0 To P.DM_LogicalDocumentCount-1 Do Begin
    F:=P.DM_LogicalDocuments(J).DM_FullPath;D:=Client.GetDocumentByPath(F);
    If D<>Nil Then Begin L.Add('OPEN|MODIFIED='+BoolToStr(D.Modified,True)+'|'+F);If D.Modified Then Inc(N);End;
   End;
  End;
  D:=Client.GetDocumentByPath(Root+'C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc');
  If D=Nil Then Raise('C2 board must be open');L.Add('C2_MODIFIED='+BoolToStr(D.Modified,True));If D.Modified Then Inc(N);
  L.Add('UNSAVED_COUNT='+IntToStr(N));L.Add('COMPLETE');
 Finally L.SaveToFile('@LOG@');L.Free;End;
End;

