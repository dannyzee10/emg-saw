// Rebuild the GND polygons of the ROUTING COPY in memory only (no save), for inspection/DRC.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\REPOUR_ONLY_LOG.txt';
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;P:IPCB_Polygon;Polys:TInterfaceList;I:Integer;L:TStringList;
Begin
 L:=TStringList.Create;Polys:=TInterfaceList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('routing PCB not open');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
  Try P:=It.FirstPCBObject;While P<>Nil Do Begin Polys.Add(P);P:=It.NextPCBObject;End;Finally B.BoardIterator_Destroy(It);End;
  PCBServer.PreProcess;
  Try For I:=0 To Polys.Count-1 Do Begin P:=Polys.Items(I);P.SetState_CopperPourInvalid;P.Rebuild;P.CopperPourValidate;L.Add('POLY_REBUILT|'+P.Name);End;
  Finally PCBServer.PostProcess;End;
  B.ConnectivelyValidateNets;B.ViewManager_FullUpdate;
  L.Add('NOT_SAVED|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);Polys.Free;L.Free;End;
End;
