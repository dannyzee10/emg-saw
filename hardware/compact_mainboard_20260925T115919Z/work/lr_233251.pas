// Read-only probe of the saved service library (template C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\MainBoard\/C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PROBE_LIBREAD_LOG.txt): primitive counts via LoadCompFromLibrary and via
// the opened library document.  No edits, no saves.
Const LibFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\MainBoard\Libraries\EMG_Service_C2.PcbLib';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PROBE_LIBREAD_LOG.txt';
Var Log:TStringList;
Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;
Procedure CountPrims(Tag:String;F:IPCB_LibComponent);
Var FI:IPCB_GroupIterator;Prim:IPCB_Primitive;N,NP:Integer;S:String;
Begin
 N:=0;NP:=0;S:='';FI:=F.GroupIterator_Create;FI.SetState_FilterAll;
 Try Prim:=FI.FirstPCBObject;While Prim<>Nil Do Begin Inc(N);If Prim.ObjectId=ePadObject Then Begin Inc(NP);S:=S+'['+Prim.Name+']';End;Prim:=FI.NextPCBObject;End;
 Finally F.GroupIterator_Destroy(FI);End;
 Say(Tag+'|'+F.Name+'|PRIMS='+IntToStr(N)+'|PADS='+IntToStr(NP)+'|'+S);
End;
Procedure RunFixed;
Var F:IPCB_LibComponent;SD:IServerDocument;Lib:IPCB_Library;It:IPCB_LibraryIterator;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now)+'|EXISTS='+BoolToStr(FileExists(LibFile),True));
  F:=PCBServer.LoadCompFromLibrary('EMG_TC2030_NL',LibFile);If F=Nil Then Say('LOAD_NIL') Else CountPrims('LOADCOMP',F);
  F:=PCBServer.LoadCompFromLibrary('EMG_TP_FLAT_1R2',LibFile);If F=Nil Then Say('LOAD_NIL') Else CountPrims('LOADCOMP',F);
  SD:=Client.OpenDocument('PCBLIB',LibFile);If SD=Nil Then Raise('open lib failed');Client.ShowDocument(SD);
  Lib:=PCBServer.GetCurrentPCBLibrary;If Lib=Nil Then Raise('no current lib');
  It:=Lib.LibraryIterator_Create;It.SetState_FilterAll;
  Try F:=It.FirstPCBObject;While F<>Nil Do Begin CountPrims('LIBDOC',F);F:=It.NextPCBObject;End;
  Finally Lib.LibraryIterator_Destroy(It);End;
  Client.CloseDocument(SD);
  Say('COMPLETE');
 Finally Log.Free;End;
End;
