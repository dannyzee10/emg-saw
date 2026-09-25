// READ-ONLY baseline measurement of candidate B's PCB (identical to baseline A at this point):
// board shape vertices/area, layer stack + mechanical layer names/pairs, and one record per component with side,
// XY, rotation, footprint, UIDs, bounding boxes, pad extents, 3D bodies (count, max overall height/standoff)
// and primitive counts per layer (to see which mechanical/overlay layers each component uses).
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\BASELINE_EXPORT.txt';
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;C:IPCB_Component;GI:IPCB_GroupIterator;O:IPCB_Primitive;
    Bd:IPCB_ComponentBody;R:TCoordRect;I,NB,NP:Integer;S,Line,LayCnt:String;H,Hmax,So:Double;
    PX0,PY0,PX1,PY1:Integer;Seg:TPolySegment;Cnt:TStringList;
Begin
 L:=TStringList.Create;Cnt:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('B PCB not open');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  L.Add('MODIFIED='+BoolToStr(D.Modified,True));
  // board shape
  L.Add('BOARD_OUTLINE|POINTS='+IntToStr(B.BoardOutline.PointCount));
  For I:=0 To B.BoardOutline.PointCount-1 Do Begin
   Seg:=B.BoardOutline.Segments[I];
   L.Add('BO_V|'+IntToStr(I)+'|KIND='+IntToStr(Ord(Seg.Kind))+'|X='+MM(Seg.vx)+'|Y='+MM(Seg.vy)+'|CX='+MM(Seg.cx)+'|CY='+MM(Seg.cy)+'|R='+MM(Seg.Radius)+'|A1='+FloatToStr(Seg.Angle1)+'|A2='+FloatToStr(Seg.Angle2));
  End;
  R:=B.BoardOutline.BoundingRectangle;L.Add('BOARD_BBOX|'+MM(R.Left)+'|'+MM(R.Bottom)+'|'+MM(R.Right)+'|'+MM(R.Top));
  L.SaveToFile(OutFile);
  // components
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
  Try C:=It.FirstPCBObject;While C<>Nil Do Begin
   NB:=0;NP:=0;Hmax:=0;So:=0;PX0:=MaxInt;PY0:=MaxInt;PX1:=-MaxInt;PY1:=-MaxInt;Cnt.Clear;
   GI:=C.GroupIterator_Create;GI.SetState_FilterAll;GI.AddFilter_LayerSet(AllLayers);
   Try O:=GI.FirstPCBObject;While O<>Nil Do Begin
    S:=Layer2String(O.Layer)+':'+IntToStr(Ord(O.ObjectId));
    If Cnt.IndexOfName(S)<0 Then Cnt.Values[S]:='1' Else Cnt.Values[S]:=IntToStr(StrToInt(Cnt.Values[S])+1);
    If O.ObjectId=ePadObject Then Begin
     Inc(NP);R:=O.BoundingRectangle;
     If R.Left<PX0 Then PX0:=R.Left;If R.Bottom<PY0 Then PY0:=R.Bottom;If R.Right>PX1 Then PX1:=R.Right;If R.Top>PY1 Then PY1:=R.Top;
    End Else If O.ObjectId=eComponentBodyObject Then Begin
     Bd:=O;Inc(NB);
     Try H:=CoordToMMs(Bd.OverallHeight);If H>Hmax Then Hmax:=H;Except End;
     Try If CoordToMMs(Bd.StandoffHeight)>So Then So:=CoordToMMs(Bd.StandoffHeight);Except End;
    End;
    O:=GI.NextPCBObject;
   End;Finally C.GroupIterator_Destroy(GI);End;
   R:=C.BoundingRectangleNoNameComment;
   Line:='COMPX|'+C.Name.Text+'|'+C.Pattern+'|'+Layer2String(C.Layer)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|ROT='+FloatToStr(C.Rotation)
    +'|BBOX='+MM(R.Left)+','+MM(R.Bottom)+','+MM(R.Right)+','+MM(R.Top);
   If NP>0 Then Line:=Line+'|PADBOX='+MM(PX0)+','+MM(PY0)+','+MM(PX1)+','+MM(PY1) Else Line:=Line+'|PADBOX=';
   Line:=Line+'|PADS='+IntToStr(NP)+'|BODIES='+IntToStr(NB)+'|HMAX='+FloatToStrF(Hmax,ffFixed,9,3)+'|STANDOFF='+FloatToStrF(So,ffFixed,9,3);
   Try Line:=Line+'|SRCUID='+C.SourceUniqueId;Except End;
   Try Line:=Line+'|COMMENT='+C.Comment.Text;Except End;
   LayCnt:='';For I:=0 To Cnt.Count-1 Do LayCnt:=LayCnt+Cnt.Names[I]+'='+Cnt.ValueFromIndex[I]+';';
   Line:=Line+'|PRIMS='+LayCnt;
   L.Add(Line);
   C:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;Cnt.Free;End;
End;
