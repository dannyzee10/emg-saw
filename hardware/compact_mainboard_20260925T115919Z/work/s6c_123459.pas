// 4 -> 6 layer conversion (JLC06121H-3313, 1.2 mm): inserts Mid Layer 3 / Mid Layer 4 into the legacy V7 stack, names the
// six copper layers, sets copper and dielectric thickness, saves, closes, reopens and reads the stack back.
// Aborts BEFORE saving when the inserted order is not Top, Mid1, Mid2, Mid3, Mid4, Bottom.  Primitives are not touched.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\STACK6_C2_LOG.txt';
Var Log:TStringList;B:IPCB_Board;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;

Function Order(S:IPCB_LayerStack_V7):String;
Var L:IPCB_LayerObject_V7;I:Integer;
Begin
 Result:='';I:=0;L:=S.FirstLayer;
 While L<>Nil Do Begin Result:=Result+IntToStr(Ord(L.LayerID))+',';Inc(I);If I>20 Then Raise('stack traversal');L:=S.NextLayer(L);End;
End;

Procedure Dump(S:IPCB_LayerStack_V7;Tag:String);
Var L:IPCB_LayerObject_V7;D:IPCB_DielectricObject;I:Integer;
Begin
 Say(Tag+'|SIGNAL_COUNT='+IntToStr(S.SignalLayerCount)+'|LAYERS_IN_STACK='+IntToStr(S.LayersInStackCount)+'|ORDER='+Order(S));
 I:=0;L:=S.FirstLayer;
 While L<>Nil Do Begin
  D:=L.Dielectric;
  If D<>Nil Then Say(Tag+'|L'+IntToStr(I+1)+'|ID='+IntToStr(Ord(L.LayerID))+'|NAME='+L.Name+'|CU_MM='+FloatToStr(CoordToMMs(L.CopperThickness))+
                     '|DIEL='+D.DielectricMaterial+'|H_MM='+FloatToStr(CoordToMMs(D.DielectricHeight))+'|DK='+FloatToStr(D.DielectricConstant))
  Else Say(Tag+'|L'+IntToStr(I+1)+'|ID='+IntToStr(Ord(L.LayerID))+'|NAME='+L.Name+'|CU_MM='+FloatToStr(CoordToMMs(L.CopperThickness)));
  Inc(I);If I>20 Then Raise('stack traversal');L:=S.NextLayer(L);
 End;
End;

Procedure Cu(S:IPCB_LayerStack_V7;ID:TLayer;Name:String;T:Double);
Var L:IPCB_LayerObject_V7;
Begin L:=S.LayerObject[ID];L.Name:=Name;L.CopperThickness:=MMsToCoord(T);End;

Procedure Diel(S:IPCB_LayerStack_V7;ID:TLayer;Mat:String;T,Dk:Double;Core:Boolean);
Var D:IPCB_DielectricObject;
Begin
 D:=S.LayerObject[ID].Dielectric;If D=Nil Then Raise('no dielectric below layer '+IntToStr(Ord(ID)));
 D.DielectricMaterial:=Mat;D.DielectricHeight:=MMsToCoord(T);D.DielectricConstant:=Dk;
 If Core Then D.DielectricType:=eCore Else D.DielectricType:=ePrePreg;
End;

Procedure RunFixed;
Var D:IServerDocument;S:IPCB_LayerStack_V7;Want:String;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now)+' basis JLC06121H-3313 (1.2 mm)');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Begin Say('ERR_OPEN');Exit;End;Say('OPENED');
  Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Begin Say('ERR_NO_BOARD');Exit;End;Say('BOARD='+B.FileName);
  If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Begin Say('ERR_WRONG_BOARD');Exit;End;
  If D.Modified Then Begin Say('ERR_MODIFIED');Exit;End;
  S:=B.LayerStack_V7;If S=Nil Then Begin Say('ERR_NO_V7');Exit;End;Say('V7_OK');
  Dump(S,'BEFORE');
  Say('BEFORE_INSERT');
  If Not S.LayerObject[eMidLayer3].IsInLayerStack Then Begin S.InsertLayer(eMidLayer3);Say('INSERTED_MID3');End;
  If Not S.LayerObject[eMidLayer4].IsInLayerStack Then Begin S.InsertLayer(eMidLayer4);Say('INSERTED_MID4');End;
  Want:=IntToStr(Ord(eTopLayer))+','+IntToStr(Ord(eMidLayer1))+','+IntToStr(Ord(eMidLayer2))+','+IntToStr(Ord(eMidLayer3))+','+
        IntToStr(Ord(eMidLayer4))+','+IntToStr(Ord(eBottomLayer))+',';
  Say('ORDER_AFTER_INSERT='+Order(S)+'|WANT='+Want);
  If Order(S)<>Want Then Begin Dump(S,'BAD_ORDER');Say('ABORT_NOT_SAVED');Exit;End;
  Cu(S,eTopLayer,'L1 TOP',0.035);Cu(S,eMidLayer1,'L2 GND',0.0152);Cu(S,eMidLayer2,'L3 SIGNAL',0.0152);
  Cu(S,eMidLayer3,'L4 GND',0.0152);Cu(S,eMidLayer4,'L5 POWER SIGNAL',0.0152);Cu(S,eBottomLayer,'L6 BOTTOM',0.035);
  Diel(S,eTopLayer,'JLC 3313 prepreg',0.0994,4.1,False);
  Diel(S,eMidLayer1,'JLC core',0.35,4.36,True);
  Diel(S,eMidLayer2,'JLC 2116 prepreg',0.1164,4.16,False);
  Diel(S,eMidLayer3,'JLC core',0.35,4.36,True);
  Diel(S,eMidLayer4,'JLC 3313 prepreg',0.0994,4.1,False);
  Dump(S,'SET');
  B.ViewManager_UpdateLayerTabs;
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong reopened board');
  Dump(B.LayerStack_V7,'REOPEN');
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
