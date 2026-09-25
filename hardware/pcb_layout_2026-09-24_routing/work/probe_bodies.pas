// READ-ONLY: pads and 3D component bodies of selected components (DRL parts + a top-side reference).
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\PROBE_BODIES.txt';
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;C:IPCB_Component;GI:IPCB_GroupIterator;O:IPCB_Primitive;
    Bd:IPCB_ComponentBody;R:TCoordRect;M:IPCB_Model;Nm,MName,Line:String;NB:Integer;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER');L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
  Try C:=It.FirstPCBObject;While C<>Nil Do Begin
   Nm:=C.Name.Text;
   If (Pos('DRL',Nm)>0) Or (Nm='INA1') Or (Nm='CU_11') Then Begin
    NB:=0;
    L.Add('COMP|'+Nm+'|'+C.Pattern+'|LAYER='+Layer2String(C.Layer)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|ROT='+FloatToStr(C.Rotation));
    GI:=C.GroupIterator_Create;GI.SetState_FilterAll;GI.AddFilter_LayerSet(AllLayers);GI.AddFilter_ObjectSet(MkSet(ePadObject,eComponentBodyObject));
    Try O:=GI.FirstPCBObject;While O<>Nil Do Begin
     If O.ObjectId=ePadObject Then L.Add('  PAD|'+O.Name+'|'+Layer2String(O.Layer)+'|X='+MM(O.X)+'|Y='+MM(O.Y)+'|SX='+MM(O.TopXSize)+'|SY='+MM(O.TopYSize)+'|ROT='+FloatToStr(O.Rotation))
     Else Begin
      Bd:=O;Inc(NB);R:=Bd.BoundingRectangle;
      Line:='  BODY|LAYER='+Layer2String(Bd.Layer)+'|BBOX='+MM(R.Left)+','+MM(R.Bottom)+','+MM(R.Right)+','+MM(R.Top);
      Try Line:=Line+'|H='+MM(Bd.OverallHeight);Except Line:=Line+'|H=?';End;
      Try Line:=Line+'|STANDOFF='+MM(Bd.StandoffHeight);Except Line:=Line+'|STANDOFF=?';End;
      Try M:=Bd.Model;If M<>Nil Then Line:=Line+'|MODEL='+M.FileName Else Line:=Line+'|MODEL=(none)';Except Line:=Line+'|MODEL=?';End;
      Try Line:=Line+'|ID='+Bd.Identifier;Except Line:=Line+'|ID=?';End;
      L.Add(Line);L.SaveToFile(OutFile);
     End;
     O:=GI.NextPCBObject;
    End;Finally C.GroupIterator_Destroy(GI);End;
    L.Add('  BODIES='+IntToStr(NB));
   End;
   C:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
