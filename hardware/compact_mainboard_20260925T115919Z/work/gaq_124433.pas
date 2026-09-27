Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\GEOMETRY_C2_6L_AQ.txt';

{ READ-ONLY: every pad (bbox per layer), free copper, keepouts, component bboxes. mm, board-origin relative. }
Function NetOf(P:IPCB_Primitive):String;Begin Result:='-';If P.Net<>Nil Then Result:=P.Net.Name;End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Function RectS(B:IPCB_Board;R:TCoordRect):String;
Begin Result:=MM(R.Left-B.XOrigin)+'|'+MM(R.Bottom-B.YOrigin)+'|'+MM(R.Right-B.XOrigin)+'|'+MM(R.Top-B.YOrigin);End;

Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;O:IPCB_Primitive;P:IPCB_Pad;C:IPCB_Component;Own:String;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER');L.SaveToFile(OutFile+'.part');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);
  It.AddFilter_ObjectSet(MkSet(ePadObject,eViaObject,eTrackObject,eArcObject,eRegionObject,eFillObject,eComponentObject));
  Try O:=It.FirstPCBObject;While O<>Nil Do Begin
   Case O.ObjectId Of
    ePadObject:Begin P:=O;Own:='FREE';If P.InComponent Then Own:=P.Component.Name.Text;
      L.Add('PAD|'+Own+'|'+P.Name+'|'+NetOf(P)+'|'+Layer2String(P.Layer)+'|'+MM(P.X-B.XOrigin)+'|'+MM(P.Y-B.YOrigin)+'|'+RectS(B,P.BoundingRectangle)+'|HOLE='+MM(P.HoleSize)+'|ROT='+FloatToStr(P.Rotation)+'|SX='+MM(P.TopXSize)+'|SY='+MM(P.TopYSize)+'|SHAPE='+IntToStr(Ord(P.TopShape)));End;
    eViaObject:L.Add('VIA|'+NetOf(O)+'|'+MM(O.x-B.XOrigin)+'|'+MM(O.y-B.YOrigin)+'|'+MM(O.Size)+'|'+MM(O.HoleSize));
    eTrackObject:If Layer2String(O.Layer)<>'' Then L.Add('TRACK|'+Layer2String(O.Layer)+'|'+NetOf(O)+'|'+MM(O.x1-B.XOrigin)+'|'+MM(O.y1-B.YOrigin)+'|'+MM(O.x2-B.XOrigin)+'|'+MM(O.y2-B.YOrigin)+'|'+MM(O.Width)+'|INCOMP='+BoolToStr(O.InComponent,True)+'|INPOLY='+BoolToStr(O.InPolygon,True)+'|KEEPOUT='+BoolToStr(O.IsKeepout,True));
    eArcObject:L.Add('ARC|'+Layer2String(O.Layer)+'|'+NetOf(O)+'|'+RectS(B,O.BoundingRectangle)+'|INCOMP='+BoolToStr(O.InComponent,True)+'|INPOLY='+BoolToStr(O.InPolygon,True)+'|KEEPOUT='+BoolToStr(O.IsKeepout,True));
    eRegionObject:L.Add('REGION|'+Layer2String(O.Layer)+'|'+NetOf(O)+'|'+RectS(B,O.BoundingRectangle)+'|INCOMP='+BoolToStr(O.InComponent,True)+'|INPOLY='+BoolToStr(O.InPolygon,True)+'|KEEPOUT='+BoolToStr(O.IsKeepout,True)+'|KIND='+IntToStr(Ord(O.Kind)));
    eFillObject:L.Add('FILL|'+Layer2String(O.Layer)+'|'+NetOf(O)+'|'+RectS(B,O.BoundingRectangle)+'|INCOMP='+BoolToStr(O.InComponent,True)+'|KEEPOUT='+BoolToStr(O.IsKeepout,True));
    eComponentObject:Begin C:=O;L.Add('COMP|'+C.Name.Text+'|'+Layer2String(C.Layer)+'|'+MM(C.X-B.XOrigin)+'|'+MM(C.Y-B.YOrigin)+'|'+FloatToStr(C.Rotation)+'|'+RectS(B,C.BoundingRectangleNoNameComment));End;
   End;
   O:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
