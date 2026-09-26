// DISPOSABLE PROBE: scratch library only (evidence\disposable_c2api\probe\PROBE_PADPROPS.PcbLib).
// Tests pad-level PasteMaskEnabled and Plated setters before they are used in the real service library.
Const LibFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\probe\PROBE_PADPROPS.PcbLib';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PROBE_PADPROPS_LOG.txt';
Var Log:TStringList;
Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;
Procedure RunFixed;
Var SD:IServerDocument;Lib:IPCB_Library;F:IPCB_LibComponent;P,H:IPCB_Pad;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  If FileExists(LibFile) Then Raise('probe library exists; refuse overwrite');
  SD:=CreateNewDocumentFromDocumentKind('PCBLIB');If SD=Nil Then Raise('no lib doc');Client.ShowDocument(SD);
  Lib:=PCBServer.GetCurrentPCBLibrary;If Lib=Nil Then Raise('no library');SD.SetFileName(LibFile);
  PCBServer.PreProcess;
  Try
   F:=PCBServer.CreatePCBLibComp;F.Name:='PROBE_FP';F.Height:=0;F.X:=0;F.Y:=0;Lib.RegisterComponent(F);Lib.CurrentComponent:=F;
   PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,F.I_ObjectAddress);
   P:=PCBServer.PCBObjectFactory(ePadObject,eNoDimension,eCreate_Default);
   P.Name:='1';P.Layer:=eTopLayer;P.X:=0;P.Y:=0;P.TopXSize:=MMsToCoord(0.787);P.TopYSize:=MMsToCoord(0.787);P.TopShape:=eRounded;P.HoleSize:=0;
   P.Board:=Lib.Board;F.AddPCBObject(P);PCBServer.SendMessageToRobots(F.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,P.I_ObjectAddress);
   Say('SMD_PAD_ADDED');
   H:=PCBServer.PCBObjectFactory(ePadObject,eNoDimension,eCreate_Default);
   H.Name:='';H.Layer:=eMultiLayer;H.X:=MMsToCoord(2.54);H.Y:=0;H.HoleSize:=MMsToCoord(0.991);
   H.TopXSize:=MMsToCoord(0.991);H.TopYSize:=MMsToCoord(0.991);H.MidXSize:=MMsToCoord(0.991);H.MidYSize:=MMsToCoord(0.991);
   H.BotXSize:=MMsToCoord(0.991);H.BotYSize:=MMsToCoord(0.991);H.TopShape:=eRounded;H.MidShape:=eRounded;H.BotShape:=eRounded;
   H.Board:=Lib.Board;F.AddPCBObject(H);PCBServer.SendMessageToRobots(F.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,H.I_ObjectAddress);
   Say('HOLE_PAD_ADDED|PLATED_BEFORE='+BoolToStr(H.Plated,True));
   H.Plated:=False;
   Say('PLATED_SET|PLATED_NOW='+BoolToStr(H.Plated,True));
   Say('PASTE_BEFORE='+BoolToStr(P.PasteMaskEnabled,True));
   P.PasteMaskEnabled:=False;
   Say('PASTE_SET|PASTE_NOW='+BoolToStr(P.PasteMaskEnabled,True));
  Finally PCBServer.PostProcess;End;
  Lib.Board.ViewManager_FullUpdate;SD.Modified:=True;
  If Not SD.DoFileSave('PCB Library Binary File (*.PcbLib)') Then Raise('save failed');
  Say('SAVED');
  Client.CloseDocument(SD);
  Say('COMPLETE');
 Finally Log.Free;End;
End;
