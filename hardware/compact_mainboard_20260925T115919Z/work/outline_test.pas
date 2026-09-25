// DISPOSABLE PROJECT COPY ONLY: change the board outline to 75 x 40 mm (r = 2 mm) inside its project, logging after
// every statement (read-modify-write of each segment, as in the proven polygon reshape).  Save, close, reopen, read back.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_outline\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\OUTLINE_TEST_LOG.txt';
Var L:TStringList;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile);End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Procedure SetSeg(O:IPCB_BoardOutline;I:Integer;IsArc:Boolean;X,Y,CX,CY,A1,A2:Double);
Var V:TPolySegment;
Begin
 V:=O.Segments[I];
 If IsArc Then V.Kind:=ePolySegmentArc Else V.Kind:=ePolySegmentLine;
 V.Vx:=MMsToCoord(X);V.Vy:=MMsToCoord(Y);
 If IsArc Then Begin V.Cx:=MMsToCoord(CX);V.Cy:=MMsToCoord(CY);V.Radius:=MMsToCoord(2);V.Angle1:=A1;V.Angle2:=A2;End;
 O.Segments[I]:=V;Say('SEG_SET|'+IntToStr(I));
End;
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;O:IPCB_BoardOutline;W:IWorkspace;P:IProject;RB:TCoordRect;I:Integer;V:TPolySegment;
Begin
 L:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  W:=GetWorkspace;
  ResetParameters;AddStringParameter('ObjectKind','Project');AddStringParameter('FileName',Root+'EMG_MainBoard_Layout.PrjPcb');RunProcess('WorkspaceManager:OpenObject');
  P:=W.DM_GetProjectFromPath(Root+'EMG_MainBoard_Layout.PrjPcb');If P=Nil Then Raise('project not open');Say('PROJECT_OPEN');
  D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board');
  Say('BOARD_OPEN|MODIFIED='+BoolToStr(D.Modified,True));
  O:=B.BoardOutline;Say('GOT_OUTLINE|POINTS='+IntToStr(O.PointCount));
  O.BeginModify;Say('BEGINMODIFY_OK');
  O.PointCount:=8;Say('POINTCOUNT_OK');
  SetSeg(O,0,False,12,10,0,0,0,0);
  SetSeg(O,1,True,83,10,83,12,270,360);
  SetSeg(O,2,False,85,12,0,0,0,0);
  SetSeg(O,3,True,85,48,83,48,0,90);
  SetSeg(O,4,False,83,50,0,0,0,0);
  SetSeg(O,5,True,12,50,12,48,90,180);
  SetSeg(O,6,False,10,48,0,0,0,0);
  SetSeg(O,7,True,10,12,12,12,180,270);
  O.EndModify;Say('ENDMODIFY_OK');
  O.Invalidate;Say('INVALIDATE_OK');
  O.Rebuild;Say('REBUILD_OK');
  O.Validate;Say('VALIDATE_OK');
  B.UpdateBoardOutline;Say('UPDATEBOARDOUTLINE_OK');
  RB:=B.BoardOutline.BoundingRectangle;Say('OUTLINE_AFTER|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top));
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;RB:=B.BoardOutline.BoundingRectangle;
  Say('REOPEN_OUTLINE|'+MM(RB.Left)+'|'+MM(RB.Bottom)+'|'+MM(RB.Right)+'|'+MM(RB.Top)+'|POINTS='+IntToStr(B.BoardOutline.PointCount));
  For I:=0 To B.BoardOutline.PointCount-1 Do Begin V:=B.BoardOutline.Segments[I];Say('REOPEN_SEG|'+IntToStr(I)+'|KIND='+IntToStr(Ord(V.Kind))+'|'+MM(V.Vx)+'|'+MM(V.Vy));End;
  D.Modified:=False;Client.CloseDocument(D);Say('CLOSED_DISPOSABLE');
  Say('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
