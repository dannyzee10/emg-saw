// DISPOSABLE COPY ONLY: prove the not-yet-proven write APIs needed for candidate B, each logged before it runs:
//  MoveByXY on a free net track, a free via, a free keep-out region and a free mechanical track;
//  reshape an existing polygon (BeginModify/PointCount/Segments/EndModify); edit an existing rule's scope;
//  redraw the board outline (Astra's outline_direct method).  Save, close, reopen and read everything back.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_flip_test\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\API_TEST_LOG.txt';
Var L:TStringList;B:IPCB_Board;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile);End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Function FirstOf(Obj:TObjectId;Lay:TLayer;NeedNet:Boolean):IPCB_Primitive;
Var It:IPCB_BoardIterator;O:IPCB_Primitive;
Begin
 Result:=Nil;It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_ObjectSet(MkSet(Obj));It.AddFilter_LayerSet(MkSet(Lay));
 Try O:=It.FirstPCBObject;While (O<>Nil) And (Result=Nil) Do Begin
  If Not O.InComponent Then If (Not NeedNet) Or (O.Net<>Nil) Then Result:=O;
  O:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
End;
Procedure Line(O:IPCB_BoardOutline;I:Integer;X,Y:Double);
Var V:TPolySegment;
Begin V.Kind:=ePolySegmentLine;V.Vx:=MMsToCoord(X);V.Vy:=MMsToCoord(Y);O.Segments[I]:=V;End;
Procedure Corner(O:IPCB_BoardOutline;I:Integer;X,Y,CX,CY,A1,A2:Double);
Var V:TPolySegment;
Begin V.Kind:=ePolySegmentArc;V.Vx:=MMsToCoord(X);V.Vy:=MMsToCoord(Y);V.Cx:=MMsToCoord(CX);V.Cy:=MMsToCoord(CY);V.Radius:=MMsToCoord(2);V.Angle1:=A1;V.Angle2:=A2;O.Segments[I]:=V;End;
Procedure RunFixed;
Var D:IServerDocument;T:IPCB_Track;V:IPCB_Via;R:IPCB_Region;MT:IPCB_Track;P:IPCB_Polygon;It:IPCB_BoardIterator;Seg:TPolySegment;
    O:IPCB_BoardOutline;Ru:IPCB_Rule;S:String;RB:TCoordRect;
Begin
 L:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board');
  T:=FirstOf(eTrackObject,eTopLayer,True);Say('TRACK_BEFORE|'+T.Net.Name+'|'+MM(T.X1)+'|'+MM(T.Y1)+'|'+MM(T.X2)+'|'+MM(T.Y2));
  V:=FirstOf(eViaObject,eMultiLayer,True);Say('VIA_BEFORE|'+V.Net.Name+'|'+MM(V.X)+'|'+MM(V.Y));
  R:=FirstOf(eRegionObject,eKeepOutLayer,False);RB:=R.BoundingRectangle;Say('KEEPOUT_BEFORE|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  MT:=FirstOf(eTrackObject,eMechanical4,False);Say('MECH4_BEFORE|'+MM(MT.X1)+'|'+MM(MT.Y1)+'|'+MM(MT.X2)+'|'+MM(MT.Y2));
  PCBServer.PreProcess;
  Try
   Say('CALL T.MoveByXY');T.MoveByXY(MMsToCoord(-2),MMsToCoord(0));
   Say('CALL V.MoveByXY');V.MoveByXY(MMsToCoord(-2),MMsToCoord(0));
   Say('CALL R.MoveByXY');R.MoveByXY(MMsToCoord(-3),MMsToCoord(-5));
   Say('CALL MT.MoveByXY');MT.MoveByXY(MMsToCoord(-2),MMsToCoord(0));
  Finally PCBServer.PostProcess;End;
  Say('MOVED|TRACK '+MM(T.X1)+','+MM(T.Y1)+'|VIA '+MM(V.X)+','+MM(V.Y)+'|MECH4 '+MM(MT.X1)+','+MM(MT.Y1));
  RB:=R.BoundingRectangle;Say('KEEPOUT_AFTER|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  // polygon reshape (first polygon found)
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(ePolyObject));
  Try P:=It.FirstPCBObject;Finally B.BoardIterator_Destroy(It);End;
  Say('POLY|'+P.Name+'|POINTS='+IntToStr(P.PointCount));
  Say('CALL P.BeginModify');P.BeginModify;
  P.PointCount:=4;
  Seg:=P.Segments[0];Seg.Kind:=ePolySegmentLine;Seg.Vx:=MMsToCoord(10.5);Seg.Vy:=MMsToCoord(10.5);P.Segments[0]:=Seg;
  Seg:=P.Segments[1];Seg.Kind:=ePolySegmentLine;Seg.Vx:=MMsToCoord(84.5);Seg.Vy:=MMsToCoord(10.5);P.Segments[1]:=Seg;
  Seg:=P.Segments[2];Seg.Kind:=ePolySegmentLine;Seg.Vx:=MMsToCoord(84.5);Seg.Vy:=MMsToCoord(49.5);P.Segments[2]:=Seg;
  Seg:=P.Segments[3];Seg.Kind:=ePolySegmentLine;Seg.Vx:=MMsToCoord(10.5);Seg.Vy:=MMsToCoord(49.5);P.Segments[3]:=Seg;
  Say('CALL P.EndModify');P.EndModify;
  Say('CALL P.Rebuild');P.SetState_CopperPourInvalid;P.Rebuild;P.CopperPourValidate;
  RB:=P.BoundingRectangle;Say('POLY_AFTER|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  // rule scope edit
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
  Try Ru:=It.FirstPCBObject;While Ru<>Nil Do Begin If Ru.Name='CLR_FINAL_VP_004' Then Break;Ru:=It.NextPCBObject;End;Finally B.BoardIterator_Destroy(It);End;
  If Ru=Nil Then Say('RULE_NOT_FOUND') Else Begin
   S:=Ru.Scope1Expression;Say('RULE_BEFORE|'+S);
   Say('CALL Ru.Scope1Expression:=');Ru.Scope1Expression:='IsVia And InNet(''GND'') And InRegionAbsolute(2578.346299,1201.456299,2579.133701,1202.243701)';
   Say('RULE_AFTER|'+Ru.Scope1Expression);
  End;
  // board outline 75 x 40
  O:=B.BoardOutline;Say('CALL O.BeginModify');O.BeginModify;O.PointCount:=8;
  Line(O,0,12,10);Corner(O,1,83,10,83,12,270,360);
  Line(O,2,85,12);Corner(O,3,85,48,83,48,0,90);
  Line(O,4,83,50);Corner(O,5,12,50,12,48,90,180);
  Line(O,6,10,48);Corner(O,7,10,12,12,12,180,270);
  O.EndModify;O.Invalidate;O.Rebuild;O.Validate;B.UpdateBoardOutline;
  RB:=B.BoardOutline.BoundingRectangle;Say('OUTLINE_AFTER|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;Say('REOPENED');
  RB:=B.BoardOutline.BoundingRectangle;Say('REOPEN_OUTLINE|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  R:=FirstOf(eRegionObject,eKeepOutLayer,False);RB:=R.BoundingRectangle;Say('REOPEN_KEEPOUT|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  D.Modified:=False;Client.CloseDocument(D);Say('CLOSED_DISPOSABLE');
  Say('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
