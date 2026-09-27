// Explicit 0.20 mm free GND test-pad translation for the UART92 escape.
// Requires the checked CS detour before routing UART. No pad size/net changes.
Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';
Const OutFile='@LOG@';
Var L:TStringList;B:IPCB_Board;P:IPCB_Pad;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile+'.part');End;
Procedure FindPad;
Var It:IPCB_BoardIterator;Q:IPCB_Pad;N:Integer;
Begin
 N:=0;P:=Nil;It:=B.BoardIterator_Create;It.SetState_FilterAll;
 It.AddFilter_ObjectSet(MkSet(ePadObject));It.AddFilter_LayerSet(AllLayers);
 Try Q:=It.FirstPCBObject;While Q<>Nil Do Begin
  If (Not Q.InComponent) And (Q.Name='TP_GND_DIG') Then Begin P:=Q;Inc(N);End;
  Q:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 If N<>1 Then Raise('TP_GND_DIG free pad not unique');
 If P.Net=Nil Then Raise('Test pad net missing');
 If P.Net.Name<>'GND' Then Raise('Test pad net changed');
 If P.Layer<>eTopLayer Then Raise('Test pad layer changed');
 If Abs(CoordToMMs(P.HoleSize))>0.0001 Then Raise('Unexpected drilled test pad');
End;
Procedure RunFixed;
Var D:IServerDocument;
Begin
 L:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('Open target PCB first');
  If D.Modified Then Raise('Unsaved PCB changes');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong board');
  FindPad;
  If (Abs(CoordToMMs(P.X)-56.671)>0.0001) Or (Abs(CoordToMMs(P.Y)-44.829)>0.0001) Then Raise('Unexpected original test pad position');
  Say('PHASE1_OK|FREE_PAD=TP_GND_DIG|NET=GND|OLD=56.671,44.829|NEW=56.871,44.829');
  PCBServer.PreProcess;
  Try P.X:=MMsToCoord(56.871);Finally PCBServer.PostProcess;End;
  FindPad;B.ConnectivelyValidateNets;B.ViewManager_FullUpdate;D.Modified:=True;
  If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('Save failed');
  If D.Modified Then Raise('Still modified');Say('SAVED');Client.CloseDocument(D);
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('Reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong reopened board');FindPad;
  If D.Modified Then Raise('Reopened modified');
  If (Abs(CoordToMMs(P.X)-56.871)>0.0001) Or (Abs(CoordToMMs(P.Y)-44.829)>0.0001) Then Raise('Reopened position mismatch');
  Say('AFTER_REOPEN|FREE_PAD=TP_GND_DIG|NET='+P.Net.Name+'|X='+FloatToStr(CoordToMMs(P.X))+'|Y='+FloatToStr(CoordToMMs(P.Y)));
  Say('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
