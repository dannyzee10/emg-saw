// DISPOSABLE COPY ONLY (read-only): list every primitive of the flipped test components WITHOUT a layer filter,
// to find where FlipComponent put the 3D bodies and mechanical (courtyard/assembly) primitives.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_flip_test\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\FLIP_PROBE2_LOG.txt';
Var L:TStringList;B:IPCB_Board;
Procedure Dump(Ref:String);
Var It:IPCB_BoardIterator;C:IPCB_Component;GI:IPCB_GroupIterator;O:IPCB_Primitive;N:Integer;
Begin
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_ObjectSet(MkSet(eComponentObject));
 Try C:=It.FirstPCBObject;While C<>Nil Do Begin
  If C.Name.Text=Ref Then Begin
   N:=0;L.Add('COMP|'+Ref+'|'+Layer2String(C.Layer)+'|ROT='+FloatToStr(C.Rotation));
   GI:=C.GroupIterator_Create;GI.SetState_FilterAll;
   Try O:=GI.FirstPCBObject;While O<>Nil Do Begin
    Inc(N);L.Add('  PRIM|OBJ='+IntToStr(Ord(O.ObjectId))+'|LAYERORD='+IntToStr(Ord(O.Layer))+'|'+Layer2String(O.Layer));
    O:=GI.NextPCBObject;
   End;Finally C.GroupIterator_Destroy(GI);End;
   L.Add('  TOTAL='+IntToStr(N));
  End;
  C:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 L.SaveToFile(OutFile);
End;
Procedure RunFixed;
Var D:IServerDocument;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board');
  Dump('U_EN1');Dump('UP4');Dump('R_PGOOD');Dump('INA1');
  D.Modified:=False;Client.CloseDocument(D);L.Add('CLOSED_NO_SAVE');
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
