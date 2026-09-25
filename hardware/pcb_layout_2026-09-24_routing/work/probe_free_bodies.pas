// READ-ONLY: every 3D body on the board whose bounding box lies in x 11..31, y 19..36 mm (DRL area),
// attached (component name) or free.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\PROBE_FREE_BODIES.txt';
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Procedure RunFixed;
Var L:TStringList;D:IServerDocument;B:IPCB_Board;It:IPCB_BoardIterator;Bd:IPCB_ComponentBody;R:TCoordRect;Line,Own:String;M:IPCB_Model;N,NAll:Integer;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER');L.SaveToFile(OutFile);
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_ObjectSet(MkSet(eComponentBodyObject));It.AddFilter_Method(eProcessAll);
  N:=0;NAll:=0;
  Try Bd:=It.FirstPCBObject;While Bd<>Nil Do Begin
   Inc(NAll);R:=Bd.BoundingRectangle;
   If (CoordToMMs(R.Left-B.XOrigin)>11) And (CoordToMMs(R.Right-B.XOrigin)<31) And (CoordToMMs(R.Bottom-B.YOrigin)>19) And (CoordToMMs(R.Top-B.YOrigin)<36) Then Begin
    Inc(N);Own:='FREE';If Bd.InComponent Then Own:=Bd.Component.Name.Text;
    Line:='BODY|OWNER='+Own+'|LAYER='+Layer2String(Bd.Layer)+'|BBOX='+MM(R.Left-B.XOrigin)+','+MM(R.Bottom-B.YOrigin)+','+MM(R.Right-B.XOrigin)+','+MM(R.Top-B.YOrigin);
    Try Line:=Line+'|H='+MM(Bd.OverallHeight);Except End;
    Try M:=Bd.Model;If M<>Nil Then Line:=Line+'|MODEL='+M.FileName;Except End;
    L.Add(Line);
   End;
   Bd:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('COUNT_IN_AREA='+IntToStr(N)+'|ALL_BODIES='+IntToStr(NAll));
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
