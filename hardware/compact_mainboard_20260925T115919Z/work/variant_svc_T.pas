// Approved C2 service change, BOM side (template @ROOT@/@LOG@): the Tag-Connect footprint, the six flat probe pads and the
// solder jumper have no purchased part -> Not Fitted in assembly variant PROTO_1_REMOTE_NTC (pads stay on the board;
// BOM / pick-and-place exclude them).  Same proven calls as add_optional_drl_v8.pas (compile, flattened parts, variation).
Const PrjPath='@ROOT@EMG_MainBoard_Layout.PrjPcb';
Const OutFile='@LOG@';
Var Log:TStringList;
Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Procedure RunFixed;
Var W:IWorkspace;Project:IProject;V:IProjectVariant;Var2:IComponentVariation;Flat:IDocument;Part:IPart;Refs:TStringList;
    I,K,N,Before:Integer;SD:IServerDocument;Ok:Boolean;
Begin
 Log:=TStringList.Create;Refs:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  Refs.Add('J_SWD');Refs.Add('JP_WIFI_BOOT');Refs.Add('TP_GND');Refs.Add('TP_MCU_BOOT0');Refs.Add('TP_WIFI_BOOT');
  Refs.Add('TP_WIFI_CHIP_EN');Refs.Add('TP_WIFI_UART_RX');Refs.Add('TP_WIFI_UART_TX');
  W:=GetWorkspace;Project:=W.DM_GetProjectFromPath(PrjPath);If Project=Nil Then Raise('project not open');
  Ok:=Project.DM_Compile;Say('COMPILE_RETURN='+BoolToStr(Ok,True));
  Flat:=Project.DM_DocumentFlattened;If Flat=Nil Then Raise('no flattened document after compile');
  V:=Project.DM_FindProjectVariant('PROTO_1_REMOTE_NTC');If V=Nil Then Raise('variant PROTO_1_REMOTE_NTC missing');
  Before:=V.DM_VariationCount;Say('VARIATIONS_BEFORE='+IntToStr(Before));
  For I:=0 To Refs.Count-1 Do Begin
   N:=0;
   For K:=0 To Flat.DM_PartCount-1 Do Begin
    Part:=Flat.DM_Parts(K);
    If Part.DM_PhysicalDesignator=Refs[I] Then Begin
     Inc(N);
     Var2:=V.DM_FindComponentVariationByDesignator(Refs[I]);
     If Var2=Nil Then Var2:=V.DM_AddComponentVariation;
     Var2.DM_SetPhysicalDesignator(Refs[I]);Var2.DM_SetUniqueId(Part.DM_UniqueId);Var2.DM_SetVariationKind(eVariation_NotFitted);
     Say('NOT_FITTED|'+Refs[I]+'|'+Part.DM_UniqueId);
    End;
   End;
   If N<>1 Then Raise('expected one flattened part for '+Refs[I]+', found '+IntToStr(N));
  End;
  Say('VARIATIONS_AFTER='+IntToStr(V.DM_VariationCount));
  Var2:=V.DM_FindComponentVariationByDesignator('R_TH_BAT');
  If Var2<>Nil Then If Ord(Var2.DM_VariationKind)=1 Then Raise('remote thermistor must remain fitted');
  Project.DM_SetCurrentProjectVariant(V);Project.DM_SetModified;
  SD:=Project.DM_ServerDocument;SD.Modified:=True;If Not SD.DoFileSave('PCB Projects (*.PrjPcb)') Then Raise('project save failed');
  Say('PROJECT_SAVED');
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;Refs.Free;End;
End;
