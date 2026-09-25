// READ-ONLY: via tenting / mask state for all vias (first 8 printed in full) + tally.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\PROBE_VIAS.txt';
Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;V:IPCB_Via;N,NT,NB:Integer;S:String;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER');L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eViaObject));
  N:=0;NT:=0;NB:=0;
  Try V:=It.FirstPCBObject;While V<>Nil Do Begin
   Inc(N);
   S:='VIA|'+FloatToStr(CoordToMMs(V.X))+','+FloatToStr(CoordToMMs(V.Y));
   Try S:=S+'|TENT_TOP='+BoolToStr(V.IsTenting_Top,True)+'|TENT_BOT='+BoolToStr(V.IsTenting_Bottom,True);If V.IsTenting_Top Then Inc(NT);If V.IsTenting_Bottom Then Inc(NB);Except S:=S+'|TENT=?';End;
   Try S:=S+'|TENT='+BoolToStr(V.IsTenting,True);Except End;
   If N<=8 Then L.Add(S);
   V:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('VIAS='+IntToStr(N)+'|TENTED_TOP='+IntToStr(NT)+'|TENTED_BOT='+IntToStr(NB));
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
