// Read-only after-save/reopen verification of the authorized via rule envelope.
// Uses getters/iterators already used by astra_align_via_rule_T.pas; no rule writes.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const RequiredPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\ASTRA_READ_VIA_BI.txt';
Procedure RunFixed;
Var D:IServerDocument;B:IPCB_Board;L:TStringList;It:IPCB_BoardIterator;
    Q:IPCB_Rule;R:IPCB_RoutingViaStyleRule;V:IPCB_Via;
    Matches,Count,Bad:Integer;
Begin
 L:=TStringList.Create;
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.Add('READ_ONLY|BATCH_SELECTION_UNCHANGED');L.SaveToFile(OutFile+'.part');
  If UpperCase(PcbPath)<>UpperCase(RequiredPath) Then Raise('Wrong target path');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);
  If D=Nil Then Raise('Open failed');Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Raise('No board');If UpperCase(B.FileName)<>UpperCase(RequiredPath) Then Raise('Wrong board');
  If D.Modified Then Raise('Unsaved board; saved-state proof unavailable');
  Matches:=0;R:=Nil;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
  Try Q:=It.FirstPCBObject;While Q<>Nil Do Begin
   If Q.Name='VIA_STD_060_030' Then Begin
    Inc(Matches);If Q.RuleKind<>eRule_RoutingViaStyle Then Raise('Wrong rule kind');R:=Q;
   End;
   Q:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  If Matches<>1 Then Raise('Expected one named via rule');
  L.Add('RULE|NAME='+R.Name+'|UID='+R.UniqueId+'|ENABLED='+BoolToStr(R.DRCEnabled,True)+
   '|PRIORITY='+IntToStr(R.Priority)+'|STYLE='+IntToStr(Ord(R.ViaStyle))+
   '|S1='+R.Scope1Expression+'|S2='+R.Scope2Expression+
   '|MIN_DIA='+FloatToStr(CoordToMMs(R.MinWidth))+'|PREF_DIA='+FloatToStr(CoordToMMs(R.PreferedWidth))+
   '|MAX_DIA='+FloatToStr(CoordToMMs(R.MaxWidth))+'|MIN_HOLE='+FloatToStr(CoordToMMs(R.MinHoleWidth))+
   '|PREF_HOLE='+FloatToStr(CoordToMMs(R.PreferedHoleWidth))+'|MAX_HOLE='+FloatToStr(CoordToMMs(R.MaxHoleWidth)));
  If Not R.DRCEnabled Or (R.Priority<>1) Or (R.Scope1Expression<>'All') Or (R.Scope2Expression<>'All') Then Raise('Unexpected rule scope/status');
  If (Abs(CoordToMMs(R.MinWidth)-0.45)>0.00001) Or (Abs(CoordToMMs(R.MinHoleWidth)-0.20)>0.00001) Or
     (Abs(CoordToMMs(R.PreferedWidth)-0.60)>0.00001) Or (Abs(CoordToMMs(R.MaxWidth)-0.60)>0.00001) Or
     (Abs(CoordToMMs(R.PreferedHoleWidth)-0.30)>0.00001) Or (Abs(CoordToMMs(R.MaxHoleWidth)-0.30)>0.00001) Then
   Raise('Expected aligned .45/.20 minimum and .60/.30 preferred/maximum');
  Count:=0;Bad:=0;
  It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eViaObject));
  Try V:=It.FirstPCBObject;While V<>Nil Do Begin
   Inc(Count);
   If (CoordToMMs(V.Size)<0.45-0.00001) Or (CoordToMMs(V.Size)>0.60+0.00001) Or
      (CoordToMMs(V.HoleSize)<0.20-0.00001) Or (CoordToMMs(V.HoleSize)>0.30+0.00001) Or
      (V.LowLayer<>eTopLayer) Or (V.HighLayer<>eBottomLayer) Then Begin
    Inc(Bad);L.Add('BAD_VIA|X='+FloatToStr(CoordToMMs(V.X))+'|Y='+FloatToStr(CoordToMMs(V.Y))+
      '|D='+FloatToStr(CoordToMMs(V.Size))+'|H='+FloatToStr(CoordToMMs(V.HoleSize)));
   End;
   V:=It.NextPCBObject;
  End;Finally B.BoardIterator_Destroy(It);End;
  L.Add('VIAS='+IntToStr(Count)+'|OUTSIDE_ALIGNED_ENVELOPE='+IntToStr(Bad));
  If Bad<>0 Then Raise('Via dimensions/span outside aligned through-via envelope');
  If D.Modified Then Raise('Read-only inspection unexpectedly modified the board');
  L.Add('READ_ONLY; COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;End;
End;
