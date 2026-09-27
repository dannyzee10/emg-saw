// Prepared only; not executed by the reviewing agent.
// Scope: the approved existing VIA_STD_060_030 minimum diameter/hole change.
// Proven API: Sept16 create_rules.pas and installed IPCB_RoutingViaStyleRule.
// Batch DRC selection is NOT changed here: no callable getter for the native
// IPCB_DesignRuleCheckerOptions object was established in the installed API.
Const PcbPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const RequiredPath='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\EMG_MainBoard_Layout.PcbDoc';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\ASTRA_ALIGN_VIA_BI.txt';
Const RuleName='VIA_STD_060_030';
Var Log:TStringList;B:IPCB_Board;R:IPCB_RoutingViaStyleRule;
    InitialRules,InitialVias,InitialStyle,InitialPriority:Integer;
    InitialScope1,InitialScope2,InitialUID:String;
    InitialPref,InitialMax,InitialHolePref,InitialHoleMax:TCoord;

Procedure Say(S:String);
Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;

Function NearMM(C:TCoord;V:Double):Boolean;
Begin Result:=Abs(CoordToMMs(C)-V)<0.00001;End;

Function RuleCount:Integer;
Var It:IPCB_BoardIterator;Q:IPCB_Rule;
Begin
 Result:=0;It:=B.BoardIterator_Create;It.SetState_FilterAll;
 It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
 Try Q:=It.FirstPCBObject;While Q<>Nil Do Begin Inc(Result);Q:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;

Procedure FindExactRule;
Var It:IPCB_BoardIterator;Q:IPCB_Rule;Matches:Integer;
Begin
 R:=Nil;Matches:=0;It:=B.BoardIterator_Create;It.SetState_FilterAll;
 It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eRuleObject));
 Try Q:=It.FirstPCBObject;While Q<>Nil Do Begin
  If Q.Name=RuleName Then Begin
   Inc(Matches);If Q.RuleKind<>eRule_RoutingViaStyle Then Raise('Wrong rule kind for '+RuleName);
   R:=Q;
  End;
  Q:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 If Matches<>1 Then Raise('Expected exactly one '+RuleName+', found '+IntToStr(Matches));
End;

Procedure LogRule(Tag:String);
Begin
 Say(Tag+'|NAME='+R.Name+'|KIND='+IntToStr(Ord(R.RuleKind))+'|ENABLED='+BoolToStr(R.DRCEnabled,True)+
  '|PRIORITY='+IntToStr(R.Priority)+'|STYLE='+IntToStr(Ord(R.ViaStyle))+
  '|MIN_DIA='+FloatToStr(CoordToMMs(R.MinWidth))+'|PREF_DIA='+FloatToStr(CoordToMMs(R.PreferedWidth))+
  '|MAX_DIA='+FloatToStr(CoordToMMs(R.MaxWidth))+'|MIN_HOLE='+FloatToStr(CoordToMMs(R.MinHoleWidth))+
  '|PREF_HOLE='+FloatToStr(CoordToMMs(R.PreferedHoleWidth))+'|MAX_HOLE='+FloatToStr(CoordToMMs(R.MaxHoleWidth))+
  '|S1='+R.Scope1Expression+'|S2='+R.Scope2Expression+'|UID='+R.UniqueId);
End;

Procedure CheckPreserved;
Begin
 If (R.Name<>RuleName) Or (R.RuleKind<>eRule_RoutingViaStyle) Then Raise('Rule identity changed');
 If Not R.DRCEnabled Then Raise('Via rule disabled');
 If R.Priority<>InitialPriority Then Raise('Priority changed');
 If Ord(R.ViaStyle)<>InitialStyle Then Raise('Via style changed');
 If (R.Scope1Expression<>InitialScope1) Or (R.Scope2Expression<>InitialScope2) Then Raise('Scope changed');
 If R.UniqueId<>InitialUID Then Raise('Rule unique ID changed');
 If (R.PreferedWidth<>InitialPref) Or (R.MaxWidth<>InitialMax) Or
    (R.PreferedHoleWidth<>InitialHolePref) Or (R.MaxHoleWidth<>InitialHoleMax) Then Raise('Preferred or maximum changed');
 If RuleCount<>InitialRules Then Raise('Rule count changed');
 If Not NearMM(R.MinWidth,0.45) Or Not NearMM(R.MinHoleWidth,0.20) Then Raise('Minimum readback mismatch');
End;

Function AuditVias(Tag:String):Integer;
Var It:IPCB_BoardIterator;V:IPCB_Via;Bad,Count:Integer;
Begin
 Bad:=0;Count:=0;It:=B.BoardIterator_Create;It.SetState_FilterAll;
 It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eViaObject));
 Try V:=It.FirstPCBObject;While V<>Nil Do Begin
  Inc(Count);
  If (CoordToMMs(V.Size)<0.45-0.00001) Or (CoordToMMs(V.Size)>0.60+0.00001) Or
     (CoordToMMs(V.HoleSize)<0.20-0.00001) Or (CoordToMMs(V.HoleSize)>0.30+0.00001) Or
     (V.LowLayer<>eTopLayer) Or (V.HighLayer<>eBottomLayer) Then Begin
   Inc(Bad);Say('VIA_OUTSIDE_APPROVED_ENVELOPE|X='+FloatToStr(CoordToMMs(V.X))+
    '|Y='+FloatToStr(CoordToMMs(V.Y))+'|D='+FloatToStr(CoordToMMs(V.Size))+
    '|H='+FloatToStr(CoordToMMs(V.HoleSize)));
  End;
  V:=It.NextPCBObject;
 End;Finally B.BoardIterator_Destroy(It);End;
 Say(Tag+'|COUNT='+IntToStr(Count)+'|OUTSIDE_PROPOSED_ENVELOPE='+IntToStr(Bad));
 If Bad<>0 Then Raise('Existing vias fall outside approved through-via envelope');
 Result:=Count;
End;

Procedure RunFixed;
Var D:IServerDocument;ReopenedVias:Integer;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  Say('SCOPE=VIA_RULE_MINIMUMS_ONLY|BATCH_SELECTION=UNCHANGED');
  If UpperCase(PcbPath)<>UpperCase(RequiredPath) Then Raise('Target must be exact compact C2 worktree PCB');
  D:=Client.GetDocumentByPath(PcbPath);If D=Nil Then D:=Client.OpenDocument('PCB',PcbPath);
  If D=Nil Then Raise('Open failed');Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Raise('No current PCB');
  If UpperCase(B.FileName)<>UpperCase(RequiredPath) Then Raise('Wrong board');
  If D.Modified Then Raise('Unsaved PCB changes; refusing mutation');
  FindExactRule;LogRule('BEFORE');InitialRules:=RuleCount;
  If Not R.DRCEnabled Or (R.Priority<>1) Or (R.Scope1Expression<>'All') Or (R.Scope2Expression<>'All') Then
   Raise('Unexpected rule scope/priority/enabled state');
  If Not NearMM(R.PreferedWidth,0.60) Or Not NearMM(R.MaxWidth,0.60) Or
     Not NearMM(R.PreferedHoleWidth,0.30) Or Not NearMM(R.MaxHoleWidth,0.30) Then
   Raise('Unexpected preferred/maximum limits');
  If Not ((NearMM(R.MinWidth,0.60) And NearMM(R.MinHoleWidth,0.30)) Or
          (NearMM(R.MinWidth,0.45) And NearMM(R.MinHoleWidth,0.20))) Then
   Raise('Unexpected existing minimum limits');
  InitialStyle:=Ord(R.ViaStyle);InitialPriority:=R.Priority;
  InitialScope1:=R.Scope1Expression;InitialScope2:=R.Scope2Expression;InitialUID:=R.UniqueId;
  InitialPref:=R.PreferedWidth;InitialMax:=R.MaxWidth;
  InitialHolePref:=R.PreferedHoleWidth;InitialHoleMax:=R.MaxHoleWidth;
  InitialVias:=AuditVias('PREFLIGHT_VIAS');
  Say('PHASE1_OK|RULES='+IntToStr(InitialRules)+'|VIAS='+IntToStr(InitialVias));
  PCBServer.PreProcess;
  Try
   R.BeginModify;
   Try R.MinWidth:=MMsToCoord(0.45);R.MinHoleWidth:=MMsToCoord(0.20);
   Finally R.EndModify;End;
  Finally PCBServer.PostProcess;End;
  CheckPreserved;LogRule('AFTER_APPLY');
  B.ViewManager_FullUpdate;D.Modified:=True;
  If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('Save failed');
  If D.Modified Then Raise('Still modified after save');Say('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',PcbPath);
  If D=Nil Then Raise('Reopen failed');Client.ShowDocument(D);B:=PCBServer.GetCurrentPCBBoard;
  If B=Nil Then Raise('No reopened board');
  If UpperCase(B.FileName)<>UpperCase(RequiredPath) Then Raise('Wrong reopened board');
  If D.Modified Then Raise('Reopened board is modified');
  FindExactRule;CheckPreserved;LogRule('AFTER_REOPEN');
  ReopenedVias:=AuditVias('REOPENED_VIAS');
  If ReopenedVias<>InitialVias Then Raise('Via count changed');
  Say('RULE_LIMITS_VERIFIED|BATCH_ROUTINGVIASTYLE_CHECK_STILL_REQUIRES_NATIVE_SELECTION');
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
