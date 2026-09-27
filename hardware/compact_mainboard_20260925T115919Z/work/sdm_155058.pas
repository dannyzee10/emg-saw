// Read-only dump of MCU_sheet.SchDoc around U_MCU1 (template: C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\ / C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\SCH_DUMP_MCU.txt substituted by mkvariant.py).
// Lists every U_MCU1 pin (designator, name, connection point), and every net label, wire, no-ERC marker and power port
// with its location (mils), so a pin swap can be planned exactly.  Nothing is modified or saved.
Const Root='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\C2_COMPACT_4L_2SIDE\MainBoard\';
Const OutFile='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\evidence\SCH_DUMP_MCU.txt';
Var Log:TStringList;

Procedure Say(S:String);Begin Log.Add(S);Log.SaveToFile(OutFile+'.part');End;
Function Mi(V:Integer):String;Begin Result:=IntToStr(Round(CoordToMils(V)));End;

Procedure RunFixed;
Var SD:IServerDocument;Doc:ISch_Document;It,PIt:ISch_Iterator;O:ISch_GraphicalObject;C:ISch_Component;P:ISch_Pin;
    W:ISch_Wire;I:Integer;S:String;
Begin
 Log:=TStringList.Create;
 Try
  Say('ENTER '+DateTimeToStr(Now));
  SD:=Client.OpenDocument('SCH',Root+'MCU_sheet.SchDoc');If SD=Nil Then Begin Say('ERR open');Exit;End;
  Say('SCH_OPEN|MODIFIED='+BoolToStr(SD.Modified,True));
  Doc:=SchServer.GetSchDocumentByPath(Root+'MCU_sheet.SchDoc');
  If Doc=Nil Then Begin Say('ERR doc');Exit;End;
  It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eSchComponent));
  Try
   C:=It.FirstSchObject;
   While C<>Nil Do Begin
    If C.Designator.Text='U_MCU1' Then Begin
     Say('COMP|U_MCU1|'+C.LibReference+'|X='+Mi(C.Location.X)+'|Y='+Mi(C.Location.Y));
     PIt:=C.SchIterator_Create;PIt.AddFilter_ObjectSet(MkSet(ePin));
     Try
      P:=PIt.FirstSchObject;
      While P<>Nil Do Begin
       Say('PIN|'+P.Designator+'|'+P.Name+'|X='+Mi(P.Location.X)+'|Y='+Mi(P.Location.Y)+'|LEN='+Mi(P.PinLength)+'|ORIENT='+IntToStr(P.Orientation)+'|HIDDEN='+BoolToStr(P.IsHidden,True));
       P:=PIt.NextSchObject;
      End;
     Finally C.SchIterator_Destroy(PIt);End;
    End;
    C:=It.NextSchObject;
   End;
  Finally Doc.SchIterator_Destroy(It);End;
  It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eNetLabel,ePowerObject,eNoERC,ePort));
  Try
   O:=It.FirstSchObject;
   While O<>Nil Do Begin
    S:='';
    If O.ObjectId=eNetLabel Then S:='NETLABEL|'+O.Text
    Else If O.ObjectId=ePowerObject Then S:='POWER|'+O.Text
    Else If O.ObjectId=ePort Then S:='PORT|'+O.Name
    Else S:='NOERC|';
    Say(S+'|X='+Mi(O.Location.X)+'|Y='+Mi(O.Location.Y));
    O:=It.NextSchObject;
   End;
  Finally Doc.SchIterator_Destroy(It);End;
  It:=Doc.SchIterator_Create;It.AddFilter_ObjectSet(MkSet(eWire));
  Try
   W:=It.FirstSchObject;
   While W<>Nil Do Begin
    S:='WIRE';
    For I:=1 To W.VerticesCount Do S:=S+'|'+Mi(W.Vertex[I].X)+','+Mi(W.Vertex[I].Y);
    Say(S);
    W:=It.NextSchObject;
   End;
  Finally Doc.SchIterator_Destroy(It);End;
  Say('COMPLETE');
 Finally Log.SaveToFile(OutFile);Log.Free;End;
End;
