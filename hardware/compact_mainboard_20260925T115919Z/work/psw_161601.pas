// User-approved MCU pin swap (27 Sep 2026): ADC_EMG5 moves from U_MCU1 pin 29 (PA4, ADC1_IN9) to pin 33 (PC4, ADC1_IN13),
// same ADC1.  Template: C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\ / C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PINSWAP_ADC5_LOG.txt substituted by mkvariant.py.
//  1. MCU_sheet.SchDoc: the ADC_EMG5 stub wire + net label on PA4 move +400 mil onto PC4; PC4's no-ERC marker moves onto PA4.
//     Each object is matched by its exact location and must be found exactly once, else nothing is changed.
//  2. PCB: pad U_MCU1.33 -> net ADC_EMG5, pad U_MCU1.29 -> no net (no copper is attached to pin 29).
//  3. save both, reopen, read back.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\PINSWAP_ADC5_LOG.txt';
Var Log:TStringList;Brd:IPCB_Board;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Function Mi(V:Integer):Integer;Begin Result:=Round(CoordToMils(V));End;

Procedure SwapSchematic;
Var SD:IServerDocument;Doc:ISch_Document;It:ISch_Iterator;O:ISch_GraphicalObject;W:ISch_Wire;
    Lab,Wir,Nerc:ISch_GraphicalObject;NL,NW,NN:Integer;
Begin
 SD:=Client.OpenDocument('SCH',Root+'MCU_sheet.SchDoc');If SD=Nil Then Raise('cannot open MCU_sheet');
 If SD.Modified Then Raise('unsaved edits in MCU_sheet');
 Doc:=SchServer.GetSchDocumentByPath(Root+'MCU_sheet.SchDoc');
 NL:=0;NW:=0;NN:=0;
 It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetLabel,eNoERC,eWire));
 Try
  O:=It.FirstSchObject;
  While O<>Nil Do Begin
   If (O.ObjectId=eNetLabel) And (O.Text='ADC_EMG5') And (Mi(O.Location.X)=3500) And (Mi(O.Location.Y)=1500) Then Begin Lab:=O;Inc(NL);End;
   If (O.ObjectId=eNoERC) And (Mi(O.Location.X)=3900) And (Mi(O.Location.Y)=2000) Then Begin Nerc:=O;Inc(NN);End;
   If O.ObjectId=eWire Then Begin
    W:=O;
    If (W.VerticesCount=2) And (Mi(W.Vertex[1].X)=3500) And (Mi(W.Vertex[1].Y)=2000) And (Mi(W.Vertex[2].X)=3500) And (Mi(W.Vertex[2].Y)=1500) Then Begin Wir:=O;Inc(NW);End;
   End;
   O:=It.NextSchObject;
  End;
 Finally Doc.SchIterator_Destroy(It);End;
 Say('SCH_MATCH|LABEL='+IntToStr(NL)+'|WIRE='+IntToStr(NW)+'|NOERC='+IntToStr(NN));
 If (NL<>1) Or (NW<>1) Or (NN<>1) Then Raise('schematic objects not found exactly once - nothing changed');
 SchServer.ProcessControl.PreProcess(Doc,'');
 Try
  Lab.MoveByXY(MilsToCoord(400),0);
  Wir.MoveByXY(MilsToCoord(400),0);
  Nerc.MoveByXY(MilsToCoord(-400),0);
 Finally SchServer.ProcessControl.PostProcess(Doc,'');End;
 Doc.GraphicallyInvalidate;SD.Modified:=True;
 If Not SD.DoFileSave('Advanced Schematic binary (*.SchDoc)') Then Raise('MCU_sheet save failed');
 W:=Wir;
 Say('SCH_AFTER|LABEL='+Lab.Text+'@'+IntToStr(Mi(Lab.Location.X))+','+IntToStr(Mi(Lab.Location.Y))+
     '|WIRE='+IntToStr(Mi(W.Vertex[1].X))+','+IntToStr(Mi(W.Vertex[1].Y))+'-'+IntToStr(Mi(W.Vertex[2].X))+','+IntToStr(Mi(W.Vertex[2].Y))+
     '|NOERC='+IntToStr(Mi(Nerc.Location.X))+','+IntToStr(Mi(Nerc.Location.Y)));
 Client.CloseDocument(SD);
 Say('SCHEMATIC_SAVED|MCU_sheet');
End;

Function FindComp(Ref:String):IPCB_Component;
Var It:IPCB_BoardIterator;C:IPCB_Component;N:Integer;
Begin
 Result:=Nil;N:=0;It:=Brd.BoardIterator_Create;
 It.AddFilter_ObjectSet(MkSet(eComponentObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
 Try C:=It.FirstPCBObject;While C<>Nil Do Begin If C.Name.Text=Ref Then Begin Result:=C;Inc(N);End;C:=It.NextPCBObject;End;
 Finally Brd.BoardIterator_Destroy(It);End;
 If N<>1 Then Raise('PCB component count <> 1 for '+Ref);
End;
Function FindNet(Name:String):IPCB_Net;
Var It:IPCB_BoardIterator;N:IPCB_Net;
Begin
 Result:=Nil;It:=Brd.BoardIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
 Try N:=It.FirstPCBObject;While N<>Nil Do Begin If N.Name=Name Then Begin Result:=N;Exit;End;N:=It.NextPCBObject;End;
 Finally Brd.BoardIterator_Destroy(It);End;
End;
Function PadNet(C:IPCB_Component;Name:String):String;
Var It:IPCB_GroupIterator;P:IPCB_Pad;
Begin
 Result:='?';It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin If P.Name=Name Then Begin If P.Net=Nil Then Result:='(none)' Else Result:=P.Net.Name;End;P:=It.NextPCBObject;End;
 Finally C.GroupIterator_Destroy(It);End;
End;

Procedure SwapPads;
Var C:IPCB_Component;It:IPCB_GroupIterator;P:IPCB_Pad;N,Old:IPCB_Net;Done29,Done33:Integer;
Begin
 C:=FindComp('U_MCU1');N:=FindNet('ADC_EMG5');If N=Nil Then Raise('net ADC_EMG5 missing');
 Say('PCB_BEFORE|29='+PadNet(C,'29')+'|33='+PadNet(C,'33'));
 If PadNet(C,'29')<>'ADC_EMG5' Then Raise('pin 29 is not ADC_EMG5');
 If PadNet(C,'33')<>'(none)' Then Raise('pin 33 is not free');
 Done29:=0;Done33:=0;It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try
  P:=It.FirstPCBObject;
  While P<>Nil Do Begin
   If P.Name='33' Then Begin
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);
    P.Net:=N;N.RegisterWithGroupWarehouse(P);
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
    Inc(Done33);
   End Else If P.Name='29' Then Begin
    Old:=P.Net;
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);
    P.Net:=Nil;
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
    Inc(Done29);
   End;
   P:=It.NextPCBObject;
  End;
 Finally C.GroupIterator_Destroy(It);End;
 If (Done29<>1) Or (Done33<>1) Then Raise('pad count mismatch');
 N.Rebuild;
 Say('PCB_AFTER|29='+PadNet(C,'29')+'|33='+PadNet(C,'33'));
End;

Procedure RunFixed;
Var D:IServerDocument;C:IPCB_Component;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('PCB not open (run open_proj first)');
  If D.Modified Then Raise('PCB has unsaved changes; refusing');
  SwapSchematic;
  D:=Client.GetDocumentByPath(Root+'EMG_MainBoard_Layout.PcbDoc');Client.ShowDocument(D);
  Brd:=PCBServer.GetCurrentPCBBoard;If UpperCase(Brd.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board');
  PCBServer.PreProcess;
  Try SwapPads;Finally PCBServer.PostProcess;End;
  Brd.ConnectivelyValidateNets;Brd.ViewManager_FullUpdate;
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('PCB save failed');
  Say('PCB_SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  Brd:=PCBServer.GetCurrentPCBBoard;C:=FindComp('U_MCU1');
  Say('READBACK|29='+PadNet(C,'29')+'|33='+PadNet(C,'33')+'|MODIFIED='+BoolToStr(D.Modified,True));
  Say('COMPLETE');
 Except
  Say('ERROR '+ExceptionMessage);Say('COMPLETE');
 End;
 Log.SaveToFile(OutFile);Log.Free;
End;
