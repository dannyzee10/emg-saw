// Discard an interrupted in-memory schematic edit of the TARGET copy's MCU_sheet (template C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\/C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\DISCARD_SCH_DISP2_LOG.txt):
// clear the Modified flag and close without saving; the file on disk is unchanged.
Const Path='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\MCU_sheet.SchDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\DISCARD_SCH_DISP2_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;L:TStringList;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(Path);
  If D=Nil Then L.Add('NOT_OPEN') Else Begin
   L.Add('MODIFIED_BEFORE='+BoolToStr(D.Modified,True));D.Modified:=False;Client.CloseDocument(D);L.Add('CLOSED_WITHOUT_SAVE');
  End;
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
