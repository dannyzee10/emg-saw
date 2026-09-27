// User-approved MCU pin swap (27 Sep 2026): the Wi-Fi UART moves from USART1 on PA9/PA10 (LQFP100 pins 68/69, right side)
// to USART1 on PB6/PB7 (pins 92/93, top row, Wi-Fi side) - same peripheral (USART1_TX / USART1_RX, AF7), both pairs FT I/O.
// Template: @ROOT@ / @LOG@ substituted by mkvariant.py.
//  1. MCU_sheet.SchDoc:
//     - TX wire (6100,4400)-(6000,4400)-(5900,4400): drop the last segment -> PA9 end (5900,4400) is free; the wire keeps
//       R_WIFI_UART_TX_LINK-2 (6100,4400) and the MCU_WIFI_UART_TX label branch (6000,4400).
//     - RX wire (5900,4500)-(6000,4500)-(6100,4500): drop the first segment -> PA10 end (5900,4500) free.
//     - the no-ERC markers on PB6 (4000,6000) and PB7 (3900,6000) move onto PA9 (5900,4400) and PA10 (5900,4500).
//     - new net labels MCU_WIFI_UART_TX at PB6's end (4000,6000) and MCU_WIFI_UART_RX at PB7's end (3900,6000), vertical.
//     Every object is matched by exact location and must be found exactly once, else nothing is changed.
//  2. PCB: pads U_MCU1.92 -> MCU_WIFI_UART_TX, .93 -> MCU_WIFI_UART_RX, .68 / .69 -> no net
//     (copper attached to 68/69 is ripped beforehand by a separate delete op).
//  3. save both, reopen, read back.
Const Root='@ROOT@';
Const OutFile='@LOG@';
Var Log:TStringList;Brd:IPCB_Board;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Function Mi(V:Integer):Integer;Begin Result:=Round(CoordToMils(V));End;
Function At(O:ISch_GraphicalObject;X,Y:Integer):Boolean;Begin Result:=(Mi(O.Location.X)=X) And (Mi(O.Location.Y)=Y);End;
Function WireIs(W:ISch_Wire;X1,Y1,X2,Y2,X3,Y3:Integer):Boolean;
Begin
 Result:=(W.VerticesCount=3) And (Mi(W.Vertex[1].X)=X1) And (Mi(W.Vertex[1].Y)=Y1) And (Mi(W.Vertex[2].X)=X2) And
         (Mi(W.Vertex[2].Y)=Y2) And (Mi(W.Vertex[3].X)=X3) And (Mi(W.Vertex[3].Y)=Y3);
End;
Function WireStr(W:ISch_Wire):String;
Var I:Integer;
Begin Result:='';For I:=1 To W.VerticesCount Do Result:=Result+IntToStr(Mi(W.Vertex[I].X))+','+IntToStr(Mi(W.Vertex[I].Y))+' ';End;

Procedure AddLabel(Doc:ISch_Document;Txt:String;X,Y:Integer;Orient:Integer);
Var L:ISch_NetLabel;
Begin
 L:=SchServer.SchObjectFactory(eNetLabel,eCreate_Default);If L=Nil Then Raise('label factory failed');
 L.Location:=Point(MilsToCoord(X),MilsToCoord(Y));L.Text:=Txt;L.Orientation:=Orient;
 Doc.RegisterSchObjectInContainer(L);
 SchServer.RobotManager.SendMessage(Doc.I_ObjectAddress,c_BroadCast,SCHM_PrimitiveRegistration,L.I_ObjectAddress);
End;

Procedure SwapSchematic;
Var SD:IServerDocument;Doc:ISch_Document;It:ISch_Iterator;O:ISch_GraphicalObject;W,WTX,WRX:ISch_Wire;
    N6,N7,Ref:ISch_GraphicalObject;NTX,NRX,NN6,NN7,Orient:Integer;
Begin
 SD:=Client.OpenDocument('SCH',Root+'MCU_sheet.SchDoc');If SD=Nil Then Raise('cannot open MCU_sheet');
 If SD.Modified Then Raise('unsaved edits in MCU_sheet');
 Doc:=SchServer.GetSchDocumentByPath(Root+'MCU_sheet.SchDoc');
 NTX:=0;NRX:=0;NN6:=0;NN7:=0;Orient:=-1;
 It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetLabel,eNoERC,eWire));
 Try
  O:=It.FirstSchObject;
  While O<>Nil Do Begin
   If O.ObjectId=eWire Then Begin
    W:=O;
    If WireIs(W,6100,4400,6000,4400,5900,4400) Then Begin WTX:=W;Inc(NTX);End;
    If WireIs(W,5900,4500,6000,4500,6100,4500) Then Begin WRX:=W;Inc(NRX);End;
   End;
   If (O.ObjectId=eNoERC) And At(O,4000,6000) Then Begin N6:=O;Inc(NN6);End;
   If (O.ObjectId=eNoERC) And At(O,3900,6000) Then Begin N7:=O;Inc(NN7);End;
   If (O.ObjectId=eNetLabel) And (O.Text='WIFI_BOOT') And At(O,4100,6100) Then Orient:=O.Orientation;
   O:=It.NextSchObject;
  End;
 Finally Doc.SchIterator_Destroy(It);End;
 Say('SCH_MATCH|TXWIRE='+IntToStr(NTX)+'|RXWIRE='+IntToStr(NRX)+'|NOERC_PB6='+IntToStr(NN6)+'|NOERC_PB7='+IntToStr(NN7)+'|REF_ORIENT='+IntToStr(Orient));
 If (NTX<>1) Or (NRX<>1) Or (NN6<>1) Or (NN7<>1) Or (Orient<0) Then Raise('schematic objects not found exactly once - nothing changed');
 SchServer.ProcessControl.PreProcess(Doc,'');
 Try
  WTX.VerticesCount:=2;                                                   // keep (6100,4400)-(6000,4400)
  WRX.Vertex[1]:=Point(MilsToCoord(6000),MilsToCoord(4500));
  WRX.Vertex[2]:=Point(MilsToCoord(6100),MilsToCoord(4500));
  WRX.VerticesCount:=2;
  N6.MoveByXY(MilsToCoord(1900),MilsToCoord(-1600));                      // (4000,6000) -> (5900,4400)
  N7.MoveByXY(MilsToCoord(2000),MilsToCoord(-1500));                      // (3900,6000) -> (5900,4500)
  AddLabel(Doc,'MCU_WIFI_UART_TX',4000,6000,Orient);
  AddLabel(Doc,'MCU_WIFI_UART_RX',3900,6000,Orient);
 Finally SchServer.ProcessControl.PostProcess(Doc,'');End;
 Doc.GraphicallyInvalidate;SD.Modified:=True;
 If Not SD.DoFileSave('Advanced Schematic binary (*.SchDoc)') Then Raise('MCU_sheet save failed');
 Say('SCH_AFTER|TXWIRE='+WireStr(WTX)+'|RXWIRE='+WireStr(WRX)+'|NOERC_A='+IntToStr(Mi(N6.Location.X))+','+IntToStr(Mi(N6.Location.Y))+
     '|NOERC_B='+IntToStr(Mi(N7.Location.X))+','+IntToStr(Mi(N7.Location.Y)));
 // read back the new labels
 NTX:=0;It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetLabel));
 Try
  O:=It.FirstSchObject;
  While O<>Nil Do Begin
   If ((O.Text='MCU_WIFI_UART_TX') And At(O,4000,6000)) Or ((O.Text='MCU_WIFI_UART_RX') And At(O,3900,6000)) Then Inc(NTX);
   O:=It.NextSchObject;
  End;
 Finally Doc.SchIterator_Destroy(It);End;
 Say('SCH_NEW_LABELS='+IntToStr(NTX));
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
Procedure SetPad(C:IPCB_Component;Name:String;N:IPCB_Net);
Var It:IPCB_GroupIterator;P:IPCB_Pad;K:Integer;
Begin
 K:=0;It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try
  P:=It.FirstPCBObject;
  While P<>Nil Do Begin
   If P.Name=Name Then Begin
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);
    P.Net:=N;If N<>Nil Then N.RegisterWithGroupWarehouse(P);
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
    Inc(K);
   End;
   P:=It.NextPCBObject;
  End;
 Finally C.GroupIterator_Destroy(It);End;
 If K<>1 Then Raise('pad count <> 1 for '+Name);
End;
Function Nets(C:IPCB_Component):String;
Begin Result:='68='+PadNet(C,'68')+'|69='+PadNet(C,'69')+'|92='+PadNet(C,'92')+'|93='+PadNet(C,'93');End;

Procedure SwapPads;
Var C:IPCB_Component;TX,RX:IPCB_Net;
Begin
 C:=FindComp('U_MCU1');TX:=FindNet('MCU_WIFI_UART_TX');RX:=FindNet('MCU_WIFI_UART_RX');
 If (TX=Nil) Or (RX=Nil) Then Raise('UART nets missing');
 Say('PCB_BEFORE|'+Nets(C));
 If (PadNet(C,'68')<>'MCU_WIFI_UART_TX') Or (PadNet(C,'69')<>'MCU_WIFI_UART_RX') Then Raise('pins 68/69 are not the UART');
 If (PadNet(C,'92')<>'(none)') Or (PadNet(C,'93')<>'(none)') Then Raise('pins 92/93 are not free');
 SetPad(C,'92',TX);SetPad(C,'93',RX);SetPad(C,'68',Nil);SetPad(C,'69',Nil);
 TX.Rebuild;RX.Rebuild;
 Say('PCB_AFTER|'+Nets(C));
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
  Say('READBACK|'+Nets(C)+'|MODIFIED='+BoolToStr(D.Modified,True));
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
