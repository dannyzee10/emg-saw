// DISPOSABLE COPY ONLY: prove native FlipComponent behaviour (pads, rotation, primitive layers incl. 3D body /
// courtyard / overlay / paste) before and after save + close + reopen.  Uses only calls proven in this project.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\disposable_flip_test\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\FLIP_TEST_LOG.txt';
Var L:TStringList;B:IPCB_Board;
Function MM(C:Integer):String;Begin Result:=FloatToStrF(CoordToMMs(C),ffFixed,9,4);End;
Function FindC(Ref:String):IPCB_Component;
Var It:IPCB_BoardIterator;C:IPCB_Component;
Begin
 Result:=Nil;It:=B.BoardIterator_Create;It.SetState_FilterAll;It.AddFilter_LayerSet(AllLayers);It.AddFilter_ObjectSet(MkSet(eComponentObject));
 Try C:=It.FirstPCBObject;While C<>Nil Do Begin If C.Name.Text=Ref Then Result:=C;C:=It.NextPCBObject;End;
 Finally B.BoardIterator_Destroy(It);End;
End;
Procedure Dump(Tag,Ref:String);
Var C:IPCB_Component;GI:IPCB_GroupIterator;O:IPCB_Primitive;S:String;P:IPCB_Pad;
Begin
 C:=FindC(Ref);If C=Nil Then Raise('missing '+Ref);
 L.Add(Tag+'|COMP|'+Ref+'|'+Layer2String(C.Layer)+'|X='+MM(C.X)+'|Y='+MM(C.Y)+'|ROT='+FloatToStr(C.Rotation)+'|UID='+C.SourceUniqueId);
 GI:=C.GroupIterator_Create;GI.SetState_FilterAll;GI.AddFilter_LayerSet(AllLayers);
 Try O:=GI.FirstPCBObject;While O<>Nil Do Begin
  If O.ObjectId=ePadObject Then Begin
   P:=O;S:='';If P.Net<>Nil Then S:=P.Net.Name;
   L.Add(Tag+'|PAD|'+Ref+'|'+P.Name+'|'+Layer2String(P.Layer)+'|X='+MM(P.X)+'|Y='+MM(P.Y)+'|NET='+S);
  End Else L.Add(Tag+'|PRIM|'+Ref+'|OBJ='+IntToStr(Ord(O.ObjectId))+'|'+Layer2String(O.Layer));
  O:=GI.NextPCBObject;
 End;Finally C.GroupIterator_Destroy(GI);End;
 L.SaveToFile(OutFile);
End;
Procedure RunFixed;
Var D:IServerDocument;I:Integer;C:IPCB_Component;Refs:TStringList;
Begin
 L:=TStringList.Create;Refs:=TStringList.Create;
 Refs.Add('U_EN1');Refs.Add('UP4');Refs.Add('R_PGOOD');Refs.Add('Q_SHDN');
 Try
  L.Add('ENTER '+DateTimeToStr(Now));L.SaveToFile(OutFile);
  D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('open failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;If UpperCase(B.FileName)<>UpperCase(Root+'EMG_MainBoard_Layout.PcbDoc') Then Raise('wrong board '+B.FileName);
  For I:=0 To Refs.Count-1 Do Dump('BEFORE',Refs[I]);
  For I:=0 To Refs.Count-1 Do Begin C:=FindC(Refs[I]);C.FlipComponent;End;
  B.ViewManager_FullUpdate;
  For I:=0 To Refs.Count-1 Do Dump('AFTER_FLIP',Refs[I]);
  D.Modified:=True;If Not D.DoFileSave('PCB Binary File (*.PcbDoc)') Then Raise('save failed');L.Add('SAVED');
  Client.CloseDocument(D);D:=Client.OpenDocument('PCB',Root+'EMG_MainBoard_Layout.PcbDoc');If D=Nil Then Raise('reopen failed');Client.ShowDocument(D);
  B:=PCBServer.GetCurrentPCBBoard;L.Add('REOPENED|MODIFIED='+BoolToStr(D.Modified,True));
  For I:=0 To Refs.Count-1 Do Dump('REOPEN',Refs[I]);
  D.Modified:=False;Client.CloseDocument(D);L.Add('CLOSED_DISPOSABLE');
  L.Add('COMPLETE');
 Finally L.SaveToFile(OutFile);L.Free;Refs.Free;End;
End;
