Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\PROBE_BOARD.txt';

{ READ-ONLY: outline, copper/polygon/region inventory, connection (ratsnest) list. }
Function NetOf(P:IPCB_Primitive):String;Begin Result:='-';If P.Net<>Nil Then Result:=P.Net.Name;End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;

Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;O:IPCB_Primitive;
    I,NT,NV,NA,NC,NR,NP,NF:Integer;Poly:IPCB_Polygon;Rg:IPCB_Region;Tr:IPCB_Track;V:IPCB_Via;K:IPCB_Connection;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER');L.SaveToFile(OutFile);
  D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board '+B.FileName);
  L.Add('BOARD='+B.FileName+'|MODIFIED='+BoolToStr(D.Modified,True));
  L.Add('ORIGIN|'+MM(B.XOrigin)+'|'+MM(B.YOrigin));
  For I:=0 To B.BoardOutline.PointCount-1 Do L.Add('OUTLINE|'+IntToStr(I)+'|'+MM(B.BoardOutline.Segments[I].vx-B.XOrigin)+'|'+MM(B.BoardOutline.Segments[I].vy-B.YOrigin)+'|KIND='+IntToStr(B.BoardOutline.Segments[I].Kind));
  NT:=0;NV:=0;NA:=0;NC:=0;NR:=0;NP:=0;NF:=0;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);
  It.AddFilter_ObjectSet(MkSet(eTrackObject,eViaObject,eArcObject,eFillObject,eRegionObject,ePolyObject,eConnectionObject));
  Try O:=It.FirstPCBObject;While O<>Nil Do Begin
   Case O.ObjectId Of
    eTrackObject:Begin Tr:=O;If Not Tr.InComponent Then Begin Inc(NT);L.Add('TRACK|'+Layer2String(Tr.Layer)+'|'+NetOf(Tr)+'|'+MM(Tr.x1-B.XOrigin)+'|'+MM(Tr.y1-B.YOrigin)+'|'+MM(Tr.x2-B.XOrigin)+'|'+MM(Tr.y2-B.YOrigin)+'|W='+MM(Tr.Width)+'|POLY='+BoolToStr(Tr.InPolygon,True));End;End;
    eViaObject:Begin V:=O;Inc(NV);L.Add('VIA|'+NetOf(V)+'|'+MM(V.x-B.XOrigin)+'|'+MM(V.y-B.YOrigin)+'|D='+MM(V.Size)+'|H='+MM(V.HoleSize));End;
    eArcObject:If Not O.InComponent Then Begin Inc(NA);L.Add('ARC|'+Layer2String(O.Layer)+'|'+NetOf(O)+'|POLY='+BoolToStr(O.InPolygon,True));End;
    eFillObject:If Not O.InComponent Then Begin Inc(NF);L.Add('FILL|'+Layer2String(O.Layer)+'|'+NetOf(O));End;
    eRegionObject:If Not O.InComponent Then Begin Rg:=O;Inc(NR);L.Add('REGION|'+Layer2String(Rg.Layer)+'|'+NetOf(Rg)+'|KEEPOUT='+BoolToStr(Rg.IsKeepout,True)+'|POLY='+BoolToStr(Rg.InPolygon,True)+'|KIND='+IntToStr(Ord(Rg.Kind)));End;
    ePolyObject:Begin Poly:=O;Inc(NP);L.Add('POLYGON|'+Poly.Name+'|'+Layer2String(Poly.Layer)+'|'+NetOf(Poly)+'|POUR_ORDER='+IntToStr(Poly.PourIndex)+'|SHELVED='+BoolToStr(Poly.PolygonType=eSignalLayerPolygon,True)+'|VERTS='+IntToStr(Poly.PointCount));End;
    eConnectionObject:Begin K:=O;Inc(NC);L.Add('CONN|'+NetOf(K)+'|'+MM(K.x1-B.XOrigin)+'|'+MM(K.y1-B.YOrigin)+'|'+Layer2String(K.Layer1)+'|'+MM(K.x2-B.XOrigin)+'|'+MM(K.y2-B.YOrigin)+'|'+Layer2String(K.Layer2));End;
   End;
   O:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('COUNT|TRACKS='+IntToStr(NT)+'|VIAS='+IntToStr(NV)+'|ARCS='+IntToStr(NA)+'|FILLS='+IntToStr(NF)+'|REGIONS='+IntToStr(NR)+'|POLYGONS='+IntToStr(NP)+'|CONNECTIONS='+IntToStr(NC));
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
