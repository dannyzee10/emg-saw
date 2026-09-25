// Save the ROUTING COPY after an inspected native operation (e.g. Situs), rebuild the GND pours first,
// then close/reopen and read back counts.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\SAVE_BOARD_LOG.txt';
Var L:TStringList;B:IPCB_Board;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile);End;
Procedure Counts(Tag:String);
Var It:IPCB_BoardIterator;O:IPCB_Primitive;NT,NV,NC:Integer;
Begin
 NT:=0;NV:=0;NC:=0;
 It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eTrackObject,eViaObject,eConnectionObject));
 Try O:=It.FirstPCBObject;While O<>Nil Do Begin
  If O.ObjectId=eTrackObject Then Begin If (Not O.InComponent) And (O.Net<>Nil) Then Inc(NT);End
  Else If O.ObjectId=eViaObject Then Inc(NV) Else Inc(NC);
  O:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 Say(Tag+'|NET_TRACKS='+IntToStr(NT)+'|VIAS='+IntToStr(NV)+'|CONNECTION_LINES='+IntToStr(NC));
End;
Procedure RunFixed;
Var D:IServerDocument;It:IPCB_BoardIterator;P:IPCB_Polygon;Polys:TInterfaceList;I:Integer;
Begin
 L:=TStringList.Create;Polys:=TInterfaceList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('routing PCB not open');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  Say('MODIFIED_BEFORE='+BoolToStr(D.Modified,True));Counts('IN_MEMORY');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
  Try P:=It.FirstPCBObject;While P<>Nil Do Begin Polys.Add(P);P:=It.NextPCBObject;End;Finally B.BoardIterator_Destroy(It);End;
  PCBServer.PreProcess;
  Try For I:=0 To Polys.Count-1 Do Begin P:=Polys.Items(I);P.SetState_CopperPourInvalid;P.Rebuild;P.CopperPourValidate;Say('POLY_REBUILT|'+P.Name);End;
  Finally PCBServer.PostProcess;End;
  B.ConnectivelyValidateNets;Counts('AFTER_REPOUR');
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If D.Modified Then Raise('reopened modified');Counts('AFTER_REOPEN');
  Say('COMPLETE');
 Finally Polys.Free;L.Free;End;
End;
