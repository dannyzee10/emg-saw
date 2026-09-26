// DISPOSABLE PROBE (template C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\MainBoard\/C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PROBE_LIBADD_LOG.txt): which pad-add method persists in a PcbLib?
//  A: F.AddPCBObject(P) without P.Board          (Altium reference example)
//  B: Lib.Board.AddPCBObject(P) with F current
// then save, close, reopen and count.  Only the disposable service library is touched.
Const LibFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api\MainBoard\Libraries\EMG_Service_C2.PcbLib';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PROBE_LIBADD_LOG.txt';
Var Log:TStringList;
Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;
Function NewPad(Name:String;X,Y:Double):IPCB_Pad;
Begin
 Result:=PCBServer.PCBObjectFactory(ePadObject,eNoDimension,eCreate_Default);
 Result.Name:=Name;Result.Layer:=eTopLayer;Result.X:=MMsToCoord(X);Result.Y:=MMsToCoord(Y);
 Result.TopXSize:=MMsToCoord(1.2);Result.TopYSize:=MMsToCoord(1.2);Result.TopShape:=eRounded;Result.HoleSize:=0;
End;
Function Count(F:IPCB_LibComponent):Integer;
Var FI:IPCB_GroupIterator;Prim:IPCB_Primitive;
Begin
 Result:=0;FI:=F.GroupIterator_Create;FI.SetState_FilterAll;
 Try Prim:=FI.FirstPCBObject;While Prim<>Nil Do Begin Inc(Result);Prim:=FI.NextPCBObject;End;Finally F.GroupIterator_Destroy(FI);End;
End;
Procedure RunFixed;
Var SD:IServerDocument;Lib:IPCB_Library;FA,FB:IPCB_LibComponent;P:IPCB_Pad;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  SD:=Client.OpenDocument('PCBLIB',LibFile);If SD=Nil Then Raise('open failed');Client.ShowDocument(SD);
  Lib:=PCBServer.GetCurrentPCBLibrary;
  FA:=Lib.GetComponentByName('EMG_TP_FLAT_1R2');FB:=Lib.GetComponentByName('EMG_SJ_2P_NO');
  If (FA=Nil) Or (FB=Nil) Then Raise('components missing');
  Say('BEFORE|A='+IntToStr(Count(FA))+'|B='+IntToStr(Count(FB)));
  PCBServer.PreProcess;
  Try
   Lib.CurrentComponent:=FA;
   P:=NewPad('TP',0,0);FA.AddPCBObject(P);
   PCBServer.SendMessageToRobots(FA.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,P.I_ObjectAddress);
   Say('A_ADDED|COUNT='+IntToStr(Count(FA)));
   Lib.CurrentComponent:=FB;
   P:=NewPad('1',-0.6,0);Lib.Board.AddPCBObject(P);
   PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,P.I_ObjectAddress);
   Say('B_ADDED|COUNT='+IntToStr(Count(FB)));
  Finally PCBServer.PostProcess;End;
  Lib.Board.ViewManager_FullUpdate;SD.Modified:=True;
  If Not SD.DoFileSave('PCB Library Binary File (*.PcbLib)') Then Raise('save failed');
  Client.CloseDocument(SD);Say('SAVED_CLOSED');
  SD:=Client.OpenDocument('PCBLIB',LibFile);Client.ShowDocument(SD);Lib:=PCBServer.GetCurrentPCBLibrary;
  FA:=Lib.GetComponentByName('EMG_TP_FLAT_1R2');FB:=Lib.GetComponentByName('EMG_SJ_2P_NO');
  Say('REOPEN|A='+IntToStr(Count(FA))+'|B='+IntToStr(Count(FB)));
  Client.CloseDocument(SD);
  Say('COMPLETE');
 Finally Log.Free;End;
End;
