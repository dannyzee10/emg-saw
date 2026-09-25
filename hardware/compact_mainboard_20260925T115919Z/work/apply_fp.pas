// CANDIDATE B (or its disposable copy): move the 15 native free test pads with their groups.
// work\FP_OPS.txt lines: FP|name|x|y|dx|dy  (current position, vector).  Phase 1 resolves each to exactly one free pad
// (not in a component) by name AND position; phase 2 MoveByXY; save; close; reopen; read back.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\B_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OpsFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\work\FP_OPS.txt';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\APPLY_FP_LOG.txt';
Var L:TStringList;B:IPCB_Board;
Procedure Say(S:String);Begin L.Add(S);L.SaveToFile(OutFile);End;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Function Fld(S:String;N:Integer):String;
Var I,P:Integer;Rest:String;
Begin
 Rest:=S;
 For I:=0 To N-1 Do Begin P:=Pos('|',Rest);If P=0 Then Begin Result:='';Exit;End;Rest:=Copy(Rest,P+1,Length(Rest));End;
 P:=Pos('|',Rest);If P=0 Then Result:=Rest Else Result:=Copy(Rest,1,P-1);
End;
Function Num(S:String;N:Integer):Double;Begin Result:=StrToFloat(Fld(S,N));End;
Procedure RunFixed;
Var D:IServerDocument;Ops:TStringList;Objs:TInterfaceList;It:IPCB_BoardIterator;P:IPCB_Pad;Found:IPCB_Pad;I,Cnt,Fails:Integer;S:String;
Begin
 L:=TStringList.Create;Ops:=TStringList.Create;Objs:=TInterfaceList.Create;Fails:=0;
 Try
  Say('ENTER '+DateTimeToStr(Now));Ops.LoadFromFile(OpsFile);Say('OPS_LINES='+IntToStr(Ops.Count));
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then Raise('PCB not open');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(PcbPath) Then Raise('wrong board');
  If D.Modified Then Raise('unsaved changes - refusing');
  For I:=0 To Ops.Count-1 Do Begin
   S:=Ops[I];Cnt:=0;Found:=Nil;
   It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(MkSet(eTopLayer));It.AddFilter_ObjectSet(MkSet(ePadObject));
   Try P:=It.FirstPCBObject;While P<>Nil Do Begin
    If Not P.InComponent Then If P.Name=Fld(S,1) Then If Abs(CoordToMMs(P.X)-Num(S,2))<0.002 Then If Abs(CoordToMMs(P.Y)-Num(S,3))<0.002 Then Begin Inc(Cnt);Found:=P;End;
    P:=It.NextPCBObject;
   End;Finally B.BoardIterator_Destroy(It);End;
   If Cnt<>1 Then Begin Inc(Fails);Say('PHASE1_FAIL|'+Fld(S,1)+'|count '+IntToStr(Cnt));Continue;End;
   Objs.Add(Found);
  End;
  If Fails>0 Then Begin Say('ABORTED_NO_CHANGES');Say('COMPLETE_WITH_ABORT');Exit;End;
  Say('PHASE1_OK');
  PCBServer.PreProcess;
  Try For I:=0 To Ops.Count-1 Do Begin S:=Ops[I];P:=Objs.Items(I);Say('CALL MoveByXY '+Fld(S,1));P.MoveByXY(MMsToCoord(Num(S,4)),MMsToCoord(Num(S,5)));End;
  Finally PCBServer.PostProcess;End;
  B.ConnectivelyValidateNets;
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;Say('REOPENED|MODIFIED='+BoolToStr(D.Modified,True));
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(MkSet(eTopLayer));It.AddFilter_ObjectSet(MkSet(ePadObject));
  Try P:=It.FirstPCBObject;While P<>Nil Do Begin
   If Not P.InComponent Then Say('FP_READBACK|'+P.Name+'|X='+MM(P.X)+'|Y='+MM(P.Y));
   P:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  Say('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;Ops.Free;Objs.Free;End;
End;
