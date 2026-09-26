// Approved C2 service-access change (template: C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\ / C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\SVC_SWAP_DISP2_LOG.txt substituted by mkvariant.py).
//  1. native library Libraries\EMG_Service_C2.PcbLib: EMG_TC2030_NL (Tag-Connect TC2030-IDC-NL-FP rev B), EMG_TP_FLAT_1R2, EMG_SJ_2P_NO
//  2. add it to the project
//  3. MCU_sheet: replace the PCBLIB model of J_SWD, JP_WIFI_BOOT and the six TP_* (same symbols, pins, nets, designators, UIDs)
//  4. PCB: replace those 8 components by footprint-identical new components (same designator, source UID/path/library refs),
//     re-assign every pad net by pad designator; save, close, reopen, read back.
// Only calls proven in this AD22 install are used (library build, model swap, component build, net assign, save/reopen).
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\SVC_SWAP_DISP2_LOG.txt';
Const LibFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_c2api2\MainBoard\Libraries\EMG_Service_C2.PcbLib';
Const MODE='MIXED';
Var Log:TStringList;Lib:IPCB_Library;Target:IPCB_LibComponent;Brd:IPCB_Board;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile);End;
Function MM(V:Integer):String;Begin Result:=FormatFloat('0.0000',CoordToMMs(V));End;

// ---------------------------------------------------------------- library
Procedure NewFP(Name,Desc:String);
Begin
 Target:=PCBServer.CreatePCBLibComp;Target.Name:=Name;Target.Description:=Desc;Target.Height:=0;Target.X:=0;Target.Y:=0;
 Lib.RegisterComponent(Target);Lib.CurrentComponent:=Target;
 PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,Target.I_ObjectAddress);
End;
Procedure AddSmd(Num:String;X,Y,SX,SY:Double;IsRound:Boolean);
Var P:IPCB_Pad;
Begin
 P:=PCBServer.PCBObjectFactory(ePadObject,eNoDimension,eCreate_Default);
 P.Name:=Num;P.Layer:=eTopLayer;P.X:=MMsToCoord(X);P.Y:=MMsToCoord(Y);P.TopXSize:=MMsToCoord(SX);P.TopYSize:=MMsToCoord(SY);
 If IsRound Then P.TopShape:=eRounded Else P.TopShape:=eRectangular;
 P.HoleSize:=0;Lib.Board.AddPCBObject(P);
 PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,P.I_ObjectAddress);
End;
Procedure AddNpth(X,Y,D:Double);
Var H:IPCB_Pad;
Begin
 H:=PCBServer.PCBObjectFactory(ePadObject,eNoDimension,eCreate_Default);
 H.Name:='';H.Layer:=eMultiLayer;H.X:=MMsToCoord(X);H.Y:=MMsToCoord(Y);H.HoleSize:=MMsToCoord(D);
 H.TopXSize:=MMsToCoord(D);H.TopYSize:=MMsToCoord(D);H.MidXSize:=MMsToCoord(D);H.MidYSize:=MMsToCoord(D);
 H.BotXSize:=MMsToCoord(D);H.BotYSize:=MMsToCoord(D);H.TopShape:=eRounded;H.MidShape:=eRounded;H.BotShape:=eRounded;
 Lib.Board.AddPCBObject(H);
 PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,H.I_ObjectAddress);
 H.Plated:=False;
End;
Procedure Line(X1,Y1,X2,Y2:Double;Layer:Integer);
Var T:IPCB_Track;
Begin
 T:=PCBServer.PCBObjectFactory(eTrackObject,eNoDimension,eCreate_Default);
 T.X1:=MMsToCoord(X1);T.Y1:=MMsToCoord(Y1);T.X2:=MMsToCoord(X2);T.Y2:=MMsToCoord(Y2);T.Width:=MMsToCoord(0.10);T.Layer:=Layer;
 Lib.Board.AddPCBObject(T);
 PCBServer.SendMessageToRobots(Lib.Board.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,T.I_ObjectAddress);
End;
Procedure Rect(X1,Y1,X2,Y2:Double;Layer:Integer);
Begin Line(X1,Y1,X2,Y1,Layer);Line(X2,Y1,X2,Y2,Layer);Line(X2,Y2,X1,Y2,Layer);Line(X1,Y2,X1,Y1,Layer);End;

Function CountPads(F:IPCB_LibComponent):Integer;
Var FI:IPCB_GroupIterator;Prim:IPCB_Primitive;
Begin
 Result:=0;FI:=F.GroupIterator_Create;FI.SetState_FilterAll;
 Try Prim:=FI.FirstPCBObject;While Prim<>Nil Do Begin If Prim.ObjectId=ePadObject Then Inc(Result);Prim:=FI.NextPCBObject;End;
 Finally F.GroupIterator_Destroy(FI);End;
End;
Procedure VerifyLibrary;
Var SD:IServerDocument;L:IPCB_Library;
Begin
 SD:=Client.OpenDocument('PCBLIB',LibFile);If SD=Nil Then Raise('library reopen failed');Client.ShowDocument(SD);L:=PCBServer.GetCurrentPCBLibrary;
 Say('LIB_VERIFY|TC='+IntToStr(CountPads(L.GetComponentByName('EMG_TC2030_NL')))+'|TP='+IntToStr(CountPads(L.GetComponentByName('EMG_TP_FLAT_1R2')))+
     '|SJ='+IntToStr(CountPads(L.GetComponentByName('EMG_SJ_2P_NO'))));
 If (CountPads(L.GetComponentByName('EMG_TC2030_NL'))<>9) Or (CountPads(L.GetComponentByName('EMG_TP_FLAT_1R2'))<>1) Or
    (CountPads(L.GetComponentByName('EMG_SJ_2P_NO'))<>2) Then Raise('library pad counts wrong after reopen');
 Client.CloseDocument(SD);
End;
Procedure BuildLibrary;
Var SD:IServerDocument;
Begin
 If FileExists(LibFile) Then Begin Say('LIBRARY_EXISTS_REUSED|'+LibFile);VerifyLibrary;Exit;End;
 SD:=CreateNewDocumentFromDocumentKind('PCBLIB');If SD=Nil Then Raise('no lib doc');Client.ShowDocument(SD);
 Lib:=PCBServer.GetCurrentPCBLibrary;If Lib=Nil Then Raise('no library');SD.SetFileName(LibFile);
 PCBServer.PreProcess;
 Try
  // Tag-Connect TC2030-IDC-NL-FP rev B: contact pads 0.787 on 1.27 grid (TC1..TC6 = 1-3-5 lower row, 2-4-6 upper row),
  // NPTH alignment holes 0.991 at (-2.54,0) (+2.54,+-1.016).  Pad designators = J_SWD schematic pins at the ARM TC2030-CTX
  // positions: TC1 VTref=1, TC2 SWDIO=2, TC3 nRESET=5, TC4 SWCLK=4, TC5 GND=3, TC6 SWO = unconnected contact pad.
  NewFP('EMG_TC2030_NL','Tag-Connect TC2030-NL plug-of-nails footprint (DNL, no paste via rule); J_SWD pins at TC2030-CTX positions');
  AddSmd('1',-1.27,-0.635,0.787,0.787,True);AddSmd('2',-1.27,0.635,0.787,0.787,True);
  AddSmd('5',0,-0.635,0.787,0.787,True);AddSmd('4',0,0.635,0.787,0.787,True);
  AddSmd('3',1.27,-0.635,0.787,0.787,True);AddSmd('',1.27,0.635,0.787,0.787,True);
  AddNpth(-2.54,0,0.991);AddNpth(2.54,1.016,0.991);AddNpth(2.54,-1.016,0.991);
  Rect(-4.953,-3.048,4.953,3.048,eMechanical15);     // plug face envelope (courtyard)
  Line(-2.0,-1.35,-1.6,-1.35,eTopOverlay);            // pin-1 mark
  Say('FP|EMG_TC2030_NL');
  NewFP('EMG_TP_FLAT_1R2','Flat 1.2 mm probe pad (no paste via rule)');
  AddSmd('TP',0,0,1.2,1.2,True);Rect(-0.8,-0.8,0.8,0.8,eMechanical15);
  Say('FP|EMG_TP_FLAT_1R2');
  NewFP('EMG_SJ_2P_NO','Normally-open 2-pad solder jumper, 0.3 mm gap (no paste via rule)');
  AddSmd('1',-0.6,0,0.9,1.2,False);AddSmd('2',0.6,0,0.9,1.2,False);Rect(-1.2,-0.8,1.2,0.8,eMechanical15);
  Say('FP|EMG_SJ_2P_NO');
 Finally PCBServer.PostProcess;End;
 Lib.Board.ViewManager_FullUpdate;SD.Modified:=True;
 If Not SD.DoFileSave('PCB Library Binary File (*.PcbLib)') Then Raise('library save failed');
 Client.CloseDocument(SD);
 Say('LIBRARY_SAVED|'+LibFile);
 VerifyLibrary;
End;

// ---------------------------------------------------------------- project + schematic
Procedure AddLibToProject;
Var W:IWorkspace;P:IProject;SD:IServerDocument;
Begin
 W:=GetWorkspace;P:=W.DM_GetProjectFromPath(Root+'EMG_MainBoard_Layout.PrjPcb');If P=Nil Then Raise('project not open');
 If P.DM_IndexOfSourceDocument(LibFile)<0 Then Begin
  P.DM_AddSourceDocument(LibFile);Say('PROJECT_LIBRARY_ADDED');
 End Else Say('PROJECT_LIBRARY_PRESENT_IN_MEMORY');
 SD:=P.DM_ServerDocument;SD.Modified:=True;
 If Not SD.DoFileSave('PCB Projects (*.PrjPcb)') Then Raise('project save failed');
 Say('PROJECT_SAVED');
End;

Procedure ReplaceModel(Component:ISch_Component;Pattern:String);
Var Iterator:ISch_Iterator;ModelImpl:ISch_Implementation;Discard:TInterfaceList;Idx:Integer;
Begin
 Discard:=TInterfaceList.Create;
 Iterator:=Component.SchIterator_Create;Iterator.AddFilter_ObjectSet(MkSet(eImplementation));
 Try
  ModelImpl:=Iterator.FirstSchObject;
  While ModelImpl<>Nil Do Begin
   If UpperCase(ModelImpl.ModelType)='PCBLIB' Then Begin Discard.Add(ModelImpl);Say('OLD_MODEL|'+Component.Designator.Text+'|'+ModelImpl.ModelName);End;
   ModelImpl:=Iterator.NextSchObject;
  End;
 Finally Component.SchIterator_Destroy(Iterator);End;
 For Idx:=0 To Discard.Count-1 Do Component.RemoveSchImplementation(Discard.Items(Idx));
 Discard.Free;
 ModelImpl:=Component.AddSchImplementation;
 ModelImpl.DatalinksLocked:=False;ModelImpl.DatabaseDatalinksLocked:=False;
 ModelImpl.ModelType:='PCBLIB';ModelImpl.ModelName:=Pattern;ModelImpl.IsCurrent:=True;
 ModelImpl.SetState_ModelVaultGUID('');ModelImpl.SetState_ModelItemGUID('');ModelImpl.SetState_ModelRevisionGUID('');
 ModelImpl.SetState_UseComponentLibrary(False);ModelImpl.IntegratedModel:=False;ModelImpl.DatabaseModel:=False;
 ModelImpl.ClearAllDatafileLinks;ModelImpl.AddDataFileLink(Pattern,LibFile,'PCBLIB');ModelImpl.MapAsString:='';
 ModelImpl.DatalinksLocked:=True;
 Say('NEW_MODEL|'+Component.Designator.Text+'|'+Pattern);
End;

Procedure SwapSchematic(Refs,Pats:TStringList);
Var SD:IServerDocument;Doc:ISch_Document;It:ISch_Iterator;C:ISch_Component;I,Found:Integer;
Begin
 SD:=Client.OpenDocument('SCH',Root+'MCU_sheet.SchDoc');If SD=Nil Then Raise('cannot open MCU_sheet');
 If SD.Modified Then Raise('unsaved edits in MCU_sheet');
 Doc:=SchServer.GetSchDocumentByPath(Root+'MCU_sheet.SchDoc');
 SchServer.ProcessControl.PreProcess(Doc,'');
 Try
  For I:=0 To Refs.Count-1 Do Begin
   Found:=0;It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eSchComponent));
   Try
    C:=It.FirstSchObject;
    While C<>Nil Do Begin
     If C.Designator.Text=Refs[I] Then Begin Inc(Found);ReplaceModel(C,Pats[I]);End;
     C:=It.NextSchObject;
    End;
   Finally Doc.SchIterator_Destroy(It);End;
   If Found<>1 Then Raise('schematic component count <> 1 for '+Refs[I]);
  End;
 Finally SchServer.ProcessControl.PostProcess(Doc,'');End;
 Doc.GraphicallyInvalidate;SD.Modified:=True;
 If Not SD.DoFileSave('Advanced Schematic binary (*.SchDoc)') Then Raise('MCU_sheet save failed');
 Client.CloseDocument(SD);
 Say('SCHEMATIC_SAVED|MCU_sheet');
End;

// ---------------------------------------------------------------- PCB
Function FindComp(Ref:String):IPCB_Component;
Var It:IPCB_BoardIterator;C:IPCB_Component;N:Integer;
Begin
 Result:=Nil;N:=0;It:=Brd.BoardIterator_Create;
 It.AddFilter_ObjectSet(MkSet(eComponentObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
 Try C:=It.FirstPCBObject;While C<>Nil Do Begin If C.Name.Text=Ref Then Begin Result:=C;Inc(N);End;C:=It.NextPCBObject;End;
 Finally Brd.BoardIterator_Destroy(It);End;
 If N<>1 Then Raise('PCB component count <> 1 for '+Ref+' ('+IntToStr(N)+')');
End;
Function FindNet(Name:String):IPCB_Net;
Var It:IPCB_BoardIterator;N:IPCB_Net;
Begin
 Result:=Nil;It:=Brd.BoardIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
 Try N:=It.FirstPCBObject;While N<>Nil Do Begin If N.Name=Name Then Begin Result:=N;Exit;End;N:=It.NextPCBObject;End;
 Finally Brd.BoardIterator_Destroy(It);End;
End;
Function PadNets(C:IPCB_Component):String;
Var It:IPCB_GroupIterator;P:IPCB_Pad;S:String;
Begin
 S:='';It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try P:=It.FirstPCBObject;While P<>Nil Do Begin
   If P.Net<>Nil Then S:=S+P.Name+'='+P.Net.Name+';' Else S:=S+P.Name+'=-;';P:=It.NextPCBObject;End;
 Finally C.GroupIterator_Destroy(It);End;
 Result:=S;
End;
Function NetOfPad(Map,PadName:String):String;
Var K:Integer;S,Key:String;
Begin
 Result:='';S:=Map;Key:=PadName+'=';
 While Length(S)>0 Do Begin
  K:=Pos(';',S);If K=0 Then K:=Length(S)+1;
  If Copy(S,1,Length(Key))=Key Then Begin Result:=Copy(S,Length(Key)+1,K-Length(Key)-1);Exit;End;
  S:=Copy(S,K+1,Length(S));
 End;
End;

Procedure AssignNets(C:IPCB_Component;Ref,OldNets:String);
Var It:IPCB_GroupIterator;P:IPCB_Pad;N:IPCB_Net;NetName:String;NP:Integer;
Begin
 NP:=0;It:=C.GroupIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));
 Try
  P:=It.FirstPCBObject;
  While P<>Nil Do Begin
   Inc(NP);NetName:='';If P.Name<>'' Then NetName:=NetOfPad(OldNets,P.Name);
   If (NetName<>'') And (NetName<>'-') Then Begin
    N:=FindNet(NetName);If N=Nil Then Raise('net missing '+NetName);
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);
    P.Net:=N;N.RegisterWithGroupWarehouse(P);
    PCBServer.SendMessageToRobots(P.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
    If P.Net.Name<>NetName Then Raise('net assign mismatch '+Ref+'.'+P.Name);
    N.Rebuild;
   End Else If P.Name<>'' Then Raise('no recorded net for '+Ref+'.'+P.Name);
   P:=It.NextPCBObject;
  End;
 Finally C.GroupIterator_Destroy(It);End;
 If NP=0 Then Raise('component has no pads after swap: '+Ref);
End;

Procedure CopyFootprint(C:IPCB_Component;FP:IPCB_LibComponent;DX,DY:Integer);
Var FI:IPCB_GroupIterator;Prim,Clone:IPCB_Primitive;N:Integer;
Begin
 N:=0;FI:=FP.GroupIterator_Create;FI.SetState_FilterAll;
 Try
  Prim:=FI.FirstPCBObject;
  While Prim<>Nil Do Begin
   If Prim.ObjectId<>eTextObject Then Begin
    Clone:=Prim.Replicate;Clone.Board:=Brd;If (DX<>0) Or (DY<>0) Then Clone.MoveByXY(DX,DY);
    C.AddPCBObject(Clone);
    PCBServer.SendMessageToRobots(C.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,Clone.I_ObjectAddress);
    Inc(N);
   End;
   Prim:=FI.NextPCBObject;
  End;
 Finally FP.GroupIterator_Destroy(FI);End;
 If N=0 Then Raise('library footprint has no primitives');
 Say('COPIED_PRIMS|'+C.Name.Text+'|'+IntToStr(N));
End;

Procedure SwapNew(Ref,Pattern:String);
Var Old,Comp:IPCB_Component;FP:IPCB_LibComponent;OldNets,U,HP,SD:String;OX,OY:Integer;
Begin
 Old:=FindComp(Ref);OldNets:=PadNets(Old);OX:=Old.X;OY:=Old.Y;U:=Old.SourceUniqueId;HP:=Old.SourceHierarchicalPath;SD:=Old.SourceDesignator;
 Say('OLD|'+Ref+'|PATTERN='+Old.Pattern+'|UID='+U+'|PATH='+HP+'|X='+MM(OX)+'|Y='+MM(OY)+'|NETS='+OldNets);
 FP:=PCBServer.LoadCompFromLibrary(Pattern,LibFile);If FP=Nil Then Raise('footprint load failed '+Pattern);
 Comp:=PCBServer.PCBObjectFactory(eComponentObject,eNoDimension,eCreate_Default);
 Comp.Pattern:=Pattern;Comp.SourceFootprintLibrary:=LibFile;Comp.SourceComponentLibrary:=Old.SourceComponentLibrary;
 Comp.SourceLibReference:=Old.SourceLibReference;Comp.SourceDesignator:=SD;Comp.SourceUniqueId:=U;Comp.SourceHierarchicalPath:=HP;
 Comp.ComponentKind:=Old.ComponentKind;Comp.Name.Text:=Old.Name.Text;Comp.Comment.Text:=Old.Comment.Text;Comp.Layer:=eTopLayer;
 Comp.X:=FP.X;Comp.Y:=FP.Y;Comp.Height:=FP.Height;
 Say('UID_BEFORE_ADD|'+Ref+'|'+Comp.SourceUniqueId);
 CopyFootprint(Comp,FP,0,0);
 Comp.X:=OX;Comp.Y:=OY;
 PCBServer.SendMessageToRobots(Brd.I_ObjectAddress,c_Broadcast,PCBM_BoardRegisteration,Comp.I_ObjectAddress);Brd.AddPCBObject(Comp);
 Say('UID_AFTER_ADD|'+Ref+'|'+Comp.SourceUniqueId);
 PCBServer.SendMessageToRobots(Comp.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);
 Comp.SourceUniqueId:=U;Comp.SourceDesignator:=SD;Comp.SourceHierarchicalPath:=HP;
 PCBServer.SendMessageToRobots(Comp.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
 Say('UID_AFTER_SET|'+Ref+'|'+Comp.SourceUniqueId);
 Brd.RemovePCBObject(Old);Say('OLD_REMOVED|'+Ref);
 AssignNets(Comp,Ref,OldNets);
 Say('NEW|'+Ref+'|MODE=NEW|PATTERN='+Comp.Pattern+'|UID='+Comp.SourceUniqueId+'|X='+MM(Comp.X)+'|Y='+MM(Comp.Y)+'|NETS='+PadNets(Comp));
End;

Procedure SwapInPlace(Ref,Pattern:String);
Var C:IPCB_Component;FP:IPCB_LibComponent;It:IPCB_GroupIterator;Prim:IPCB_Primitive;Kill:TInterfaceList;I:Integer;OldNets:String;
Begin
 C:=FindComp(Ref);OldNets:=PadNets(C);
 Say('OLD|'+Ref+'|PATTERN='+C.Pattern+'|UID='+C.SourceUniqueId+'|ROT='+FloatToStr(C.Rotation)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|NETS='+OldNets);
 FP:=PCBServer.LoadCompFromLibrary(Pattern,LibFile);If FP=Nil Then Raise('footprint load failed '+Pattern);
 If C.Rotation<>0 Then Begin
  PCBServer.SendMessageToRobots(C.I_ObjectAddress,c_Broadcast,PCBM_BeginModify,c_NoEventData);C.Rotation:=0;
  PCBServer.SendMessageToRobots(C.I_ObjectAddress,c_Broadcast,PCBM_EndModify,c_NoEventData);
 End;
 Kill:=TInterfaceList.Create;
 It:=C.GroupIterator_Create;It.SetState_FilterAll;
 Try Prim:=It.FirstPCBObject;While Prim<>Nil Do Begin If Prim.ObjectId<>eTextObject Then Kill.Add(Prim);Prim:=It.NextPCBObject;End;
 Finally C.GroupIterator_Destroy(It);End;
 Say('REMOVE_PRIMS|'+Ref+'|N='+IntToStr(Kill.Count));
 For I:=0 To Kill.Count-1 Do Begin Prim:=Kill.Items(I);C.RemovePCBObject(Prim);Brd.RemovePCBObject(Prim);End;
 Kill.Free;
 Say('REMOVED_PRIMS|'+Ref);
 CopyFootprint(C,FP,C.X-FP.X,C.Y-FP.Y);
 C.Pattern:=Pattern;C.SourceFootprintLibrary:=LibFile;C.Height:=FP.Height;
 AssignNets(C,Ref,OldNets);
 Say('NEW|'+Ref+'|MODE=INPLACE|PATTERN='+C.Pattern+'|UID='+C.SourceUniqueId+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|NETS='+PadNets(C));
End;

Procedure SwapOne(Ref,Pattern:String);
Begin
 If (MODE='INPLACE') Or ((MODE='MIXED') And (Copy(Ref,1,3)='TP_')) Then SwapInPlace(Ref,Pattern) Else SwapNew(Ref,Pattern);
End;

Procedure RunFixed;
Var Refs,Pats:TStringList;D:IServerDocument;I:Integer;C:IPCB_Component;It:IPCB_BoardIterator;NC,NP,NF:Integer;Pd:IPCB_Pad;
Begin
 Log:=TStringList.Create;Refs:=TStringList.Create;Pats:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  Refs.Add('J_SWD');Pats.Add('EMG_TC2030_NL');
  Refs.Add('JP_WIFI_BOOT');Pats.Add('EMG_SJ_2P_NO');
  Refs.Add('TP_GND');Pats.Add('EMG_TP_FLAT_1R2');Refs.Add('TP_MCU_BOOT0');Pats.Add('EMG_TP_FLAT_1R2');
  Refs.Add('TP_WIFI_BOOT');Pats.Add('EMG_TP_FLAT_1R2');Refs.Add('TP_WIFI_CHIP_EN');Pats.Add('EMG_TP_FLAT_1R2');
  Refs.Add('TP_WIFI_UART_RX');Pats.Add('EMG_TP_FLAT_1R2');Refs.Add('TP_WIFI_UART_TX');Pats.Add('EMG_TP_FLAT_1R2');
  D:=Client.GetDocumentByPath(Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('PCB not open (run open_proj first)');
  If D.Modified Then Raise('PCB has unsaved changes; refusing');
  BuildLibrary;
  AddLibToProject;
  SwapSchematic(Refs,Pats);
  D:=Client.GetDocumentByPath(Root+'EMG_MainBoard_Layout.PcbDoc');Client.ShowDocument(D);
  Brd:=PCBServer.GetCurrentPCBBoard;If UpperCase(Brd.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board');
  PCBServer.PreProcess;
  Try
   For I:=0 To Refs.Count-1 Do SwapOne(Refs[I],Pats[I]);
  Finally PCBServer.PostProcess;End;
  Brd.ConnectivelyValidateNets;Brd.ViewManager_FullUpdate;
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('PCB save failed');
  Say('PCB_SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  Brd:=PCBServer.GetCurrentPCBBoard;
  NC:=0;It:=Brd.BoardIterator_Create;It.AddFilter_ObjectSet(MkSet(eComponentObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
  Try C:=It.FirstPCBObject;While C<>Nil Do Begin Inc(NC);C:=It.NextPCBObject;End;Finally Brd.BoardIterator_Destroy(It);End;
  Say('READBACK_COMPONENTS='+IntToStr(NC)+'|MODIFIED='+BoolToStr(D.Modified,True));
  NP:=0;NF:=0;It:=Brd.BoardIterator_Create;It.AddFilter_ObjectSet(MkSet(ePadObject));It.AddFilter_LayerSet(AllLayers);It.AddFilter_Method(eProcessAll);
  Try Pd:=It.FirstPCBObject;While Pd<>Nil Do Begin Inc(NP);If Not Pd.InComponent Then Inc(NF);Pd:=It.NextPCBObject;End;Finally Brd.BoardIterator_Destroy(It);End;
  Say('READBACK_PADS='+IntToStr(NP)+'|FREE_PADS='+IntToStr(NF));
  For I:=0 To Refs.Count-1 Do Begin
   C:=FindComp(Refs[I]);
   Say('READBACK|'+Refs[I]+'|PATTERN='+C.Pattern+'|LIB='+C.SourceFootprintLibrary+'|UID='+C.SourceUniqueId+'|PATH='+C.SourceHierarchicalPath+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|NETS='+PadNets(C));
  End;
  Say('COMPLETE');
 Finally Log.Free;Refs.Free;Pats.Free;End;
End;
