// Local channel-4 escape correction authorized by the user on 27 September.
// Same CL_4 package, pins, nets, rotation and side. Coordinates supplied only
// after offline placement checking. No other object is explicitly moved.
Const PcbPath='@ROOT@EMG_MainBoard_Layout.PcbDoc';
Const OutFile='@LOG@';
Const MoveFile='@ROOT@..\..\work\ASTRA_CL4_TARGET.txt';
Var L:TStringList;B:IPCB_Board;C:IPCB_Component;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile+'.part');End;
Function PadNet(Pin:String):String;
Var It:IPCB_GroupIterator;P:IPCB_Pad;N:Integer;
Begin
 N:=0;Result:='';It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin
  If P.Name=Pin Then Begin Inc(N);If P.Net<>Nil Then Result:=P.Net.Name;End;
  P:=It.NextPCBObject;
 End;Finally C.GroupIterator_Destroy(It);End;
 If N<>1 Then Raise('CL_4 pad is not unique: '+Pin);
End;
Procedure FindCap;
Var It:IPCB_BoardIterator;Q:IPCB_Component;N:Integer;
Begin
 N:=0;C:=Nil;It:=B.BoardIterator_Create;It.SetState_FilterAll;
 It.AddFilter_ObjectSet(MkSet(eComponentObject));It.AddFilter_LayerSet(AllLayers);
 Try Q:=It.FirstPCBObject;While Q<>Nil Do Begin
  If Q.Name.Text='CL_4' Then Begin C:=Q;Inc(N);End;Q:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 If N<>1 Then Raise('CL_4 component count mismatch');
 If C.SourceUniqueId<>'\KJVBWSRF' Then Raise('CL_4 UID mismatch');
 If C.Layer<>eBottomLayer Then Raise('CL_4 side mismatch');
 If Abs(C.Rotation-180)>0.001 Then Raise('CL_4 rotation mismatch');
 If (PadNet('1')<>'NetCL_4_1') Or (PadNet('2')<>'INA_OUT_4') Then Raise('CL_4 pin/net mismatch');
End;
Procedure RunFixed;
Var D:IServerDocument;T:TStringList;NX,NY:Double;
Begin
 L:=TStringList.Create;T:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));T.LoadFromFile(MoveFile);
  If T.Count<>2 Then Raise('Target must have exactly X and Y lines');
  NX:=StrToFloat(T[0]);NY:=StrToFloat(T[1]);
  If (NX<43) Or (NX>57) Or (NY<12.5) Or (NY>22) Then Raise('Target outside local channel-4 placement area');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('Open C2 project and PCB first');
  If D.Modified Then Raise('Unsaved PCB changes');Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong board');FindCap;
  If (Abs(CoordToMMs(C.X)-51.3)>0.0001) Or (Abs(CoordToMMs(C.Y)-16.05)>0.0001) Then Raise('Unexpected original position');
  Say('PHASE1_OK|CL_4|UID='+C.SourceUniqueId+'|OLD=51.3,16.05|NEW='+FloatToStr(NX)+','+FloatToStr(NY));
  C.X:=MMsToCoord(NX);C.Y:=MMsToCoord(NY);FindCap;
  B.ConnectivelyValidateNets;B.ViewManager_FullUpdate;D.Modified:=True;
  If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('Save failed');
  If D.Modified Then Raise('Still modified');Say('SAVED');Client.CloseDocument(D);
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('Reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('Wrong reopened board');FindCap;
  If D.Modified Then Raise('Reopened modified');
  If (Abs(CoordToMMs(C.X)-NX)>0.0001) Or (Abs(CoordToMMs(C.Y)-NY)>0.0001) Then Raise('Reopened location mismatch');
  Say('AFTER_REOPEN|CL_4|X='+FloatToStr(CoordToMMs(C.X))+'|Y='+FloatToStr(CoordToMMs(C.Y))+'|PIN1='+PadNet('1')+'|PIN2='+PadNet('2'));
  Say('COMPLETE');
 Finally T.Free;L.SaveToFile(OutFile);L.Free;End;
End;
