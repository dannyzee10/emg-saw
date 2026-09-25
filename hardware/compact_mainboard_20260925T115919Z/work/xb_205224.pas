// READ-ONLY: one line per component with its 3D bodies (count, max overall height, standoff, body layer).
// Uses only API calls already proven in this project (probe_bodies.pas, place_drl_bottom.pas).
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\BODIES_EXPORT.txt';
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;C:IPCB_Component;GI:IPCB_GroupIterator;O:IPCB_Primitive;
    Bd:IPCB_ComponentBody;R:TCoordRect;NB,N:Integer;H,Hmax,So:Double;BL,Line:String;
Begin
 L:=TStringList.Create;N:=0;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('B PCB not open');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  L.Add('MODIFIED='+BoolToStr(D.Modified,True));
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
  Try C:=It.FirstPCBObject;While C<>Nil Do Begin
   NB:=0;Hmax:=0;So:=0;BL:='';
   GI:=C.GroupIterator_Create;GI.SetState_FilterAll;GI.AddFilter_LayerSet(AllLayers);GI.AddFilter_ObjectSet(MkSet(eComponentBodyObject));
   Try O:=GI.FirstPCBObject;While O<>Nil Do Begin
    Bd:=O;Inc(NB);H:=CoordToMMs(Bd.OverallHeight);If H>Hmax Then Hmax:=H;
    If CoordToMMs(Bd.StandoffHeight)>So Then So:=CoordToMMs(Bd.StandoffHeight);
    R:=Bd.BoundingRectangle;BL:=BL+Layer2String(Bd.Layer)+'@'+MM(R.Left)+','+MM(R.Bottom)+','+MM(R.Right)+','+MM(R.Top)+';';
    O:=GI.NextPCBObject;
   End;Finally C.GroupIterator_Destroy(GI);End;
   Line:='BODYC|'+C.Name.Text+'|'+Layer2String(C.Layer)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|ROT='+FloatToStr(C.Rotation)+'|SRCUID='+C.SourceUniqueId
    +'|BODIES='+IntToStr(NB)+'|HMAX='+FloatToStrF(Hmax,ffFixed,9,3)+'|STANDOFF='+FloatToStrF(So,ffFixed,9,3)+'|BODYLAYERS='+BL;
   L.Add(Line);Inc(N);If (N Mod 25)=0 Then L.SaveToFile(OutFile);
   C:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('COUNT='+IntToStr(N));L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
