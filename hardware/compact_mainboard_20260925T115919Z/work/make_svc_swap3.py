"""svc_swap3_T.pas = svc_swap2_T.pas with library primitives placed relative to the PcbLib origin (the saved footprint
reference point is the library board origin, 50000 mil; absolute-from-zero pads came out 1270 mm off on the board),
a new library file name (no clash with the first library still cached by the running Altium) and an offset check."""
import os
here = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(here, 'svc_swap2_T.pas'), encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, 'missing: ' + old[:90]
    s = s.replace(old, new)


rep(r"Const LibFile='@ROOT@Libraries\EMG_Service_C2.PcbLib';", r"Const LibFile='@ROOT@Libraries\EMG_Service_C2B.PcbLib';")
rep("Var Log:TStringList;Lib:IPCB_Library;Target:IPCB_LibComponent;Brd:IPCB_Board;",
    "Var Log:TStringList;Lib:IPCB_Library;Target:IPCB_LibComponent;Brd:IPCB_Board;BX,BY:Integer;")
rep(" Target:=PCBServer.CreatePCBLibComp;Target.Name:=Name;Target.Description:=Desc;Target.Height:=0;Target.X:=0;Target.Y:=0;",
    " BX:=Lib.Board.XOrigin;BY:=Lib.Board.YOrigin;\n Target:=PCBServer.CreatePCBLibComp;Target.Name:=Name;Target.Description:=Desc;Target.Height:=0;Target.X:=BX;Target.Y:=BY;")
rep("P.Name:=Num;P.Layer:=eTopLayer;P.X:=MMsToCoord(X);P.Y:=MMsToCoord(Y);",
    "P.Name:=Num;P.Layer:=eTopLayer;P.X:=BX+MMsToCoord(X);P.Y:=BY+MMsToCoord(Y);")
rep("H.Name:='';H.Layer:=eMultiLayer;H.X:=MMsToCoord(X);H.Y:=MMsToCoord(Y);",
    "H.Name:='';H.Layer:=eMultiLayer;H.X:=BX+MMsToCoord(X);H.Y:=BY+MMsToCoord(Y);")
rep("T.X1:=MMsToCoord(X1);T.Y1:=MMsToCoord(Y1);T.X2:=MMsToCoord(X2);T.Y2:=MMsToCoord(Y2);",
    "T.X1:=BX+MMsToCoord(X1);T.Y1:=BY+MMsToCoord(Y1);T.X2:=BX+MMsToCoord(X2);T.Y2:=BY+MMsToCoord(Y2);")
# offset check in the library verification: every pad within 6 mm of its footprint reference point
rep("Function CountPads(F:IPCB_LibComponent):Integer;", """Function MaxOffset(F:IPCB_LibComponent):Double;
Var FI:IPCB_GroupIterator;Prim:IPCB_Primitive;P:IPCB_Pad;D:Double;
Begin
 Result:=0;FI:=F.GroupIterator_Create;FI.SetState_FilterAll;
 Try Prim:=FI.FirstPCBObject;While Prim<>Nil Do Begin
   If Prim.ObjectId=ePadObject Then Begin P:=Prim;D:=Abs(CoordToMMs(P.X-F.X))+Abs(CoordToMMs(P.Y-F.Y));If D>Result Then Result:=D;End;
   Prim:=FI.NextPCBObject;End;
 Finally F.GroupIterator_Destroy(FI);End;
End;
Function CountPads(F:IPCB_LibComponent):Integer;""")
rep(" Client.CloseDocument(SD);\nEnd;\nProcedure BuildLibrary;", """ Say('LIB_OFFSETS|TC='+FloatToStr(MaxOffset(L.GetComponentByName('EMG_TC2030_NL')))+'|TP='+FloatToStr(MaxOffset(L.GetComponentByName('EMG_TP_FLAT_1R2')))+
     '|SJ='+FloatToStr(MaxOffset(L.GetComponentByName('EMG_SJ_2P_NO')))+'|ORIGIN='+FloatToStr(CoordToMMs(L.Board.XOrigin))+','+FloatToStr(CoordToMMs(L.Board.YOrigin)));
 If (MaxOffset(L.GetComponentByName('EMG_TC2030_NL'))>6) Or (MaxOffset(L.GetComponentByName('EMG_TP_FLAT_1R2'))>0.01) Or
    (MaxOffset(L.GetComponentByName('EMG_SJ_2P_NO'))>1) Then Raise('library pads not relative to the footprint origin');
 Client.CloseDocument(SD);
End;
Procedure BuildLibrary;""")
open(os.path.join(here, 'svc_swap3_T.pas'), 'w', encoding='utf-8').write(s)
# apply template with a selectable ops file
a = open(os.path.join(here, 'apply_C2_T.pas'), encoding='utf-8').read()
a = a.replace(r"\work\C2_OPS.txt';", r"\work\@OPS@';")
open(os.path.join(here, 'apply_C2_T.pas'), 'w', encoding='utf-8').write(a)
m = open(os.path.join(here, 'mkvariant.py')).read()
if '@OPS@' not in m:
    m = m.replace(".replace('@MODE@', os.environ.get('SWAP_MODE', 'MIXED'))",
                  ".replace('@MODE@', os.environ.get('SWAP_MODE', 'MIXED')).replace('@OPS@', os.environ.get('OPS_FILE', 'C2_OPS.txt'))")
    open(os.path.join(here, 'mkvariant.py'), 'w').write(m)
print('svc_swap3_T.pas + @OPS@ ready')
