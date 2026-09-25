param([ValidateSet('Run','Capture','CaptureModal','CapturePopup','SelectPDF','GeneratePDF','Windows','StopScript','RunMenu','DismissError','StopMenu','CloseWatch','CloseRunSelect','Click','ClickModal','RightClickModal','ClickPopup','SetDrcLimit','SetModalText','StopNative','EditRulesNative','DrcNative','PhysicalClick','KeysModal','KeysMain','CaptureViewPanel','ClickViewPanel','ResizeViewPanel','ScrollViewPanel')][string]$Action='Run',[string]$Script='stage_a.PrjScr',[int]$X=0,[int]$Y=0,[string]$Value="")
$ErrorActionPreference='Stop'
$ntcWork='C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\compact_mainboard_20260925T115919Z\work'
if($Action -in @('EditRulesNative','DrcNative')){$ntcCommand=if($Action -eq 'EditRulesNative'){'-RPCB:EditRules'}else{'-RPCB:DesignRuleCheck'};Start-Process -FilePath 'C:/Program Files/Altium/AD22/X2.EXE' -ArgumentList $ntcCommand -WindowStyle Hidden -PassThru | Select-Object Id,ProcessName;exit}
if($Action -eq 'StopNative'){Start-Process -FilePath 'C:/Program Files/Altium/AD22/X2.EXE' -ArgumentList '-REditScript:Stop' -WindowStyle Normal -PassThru | Select-Object Id,ProcessName; Start-Sleep -Milliseconds 2000; exit}
if($Action -eq 'Run'){
 if($Script -notmatch '^[a-zA-Z0-9_]+\.PrjScr$'){throw 'Invalid script basename'}
 $ntcScript=Join-Path $ntcWork $Script
 if(-not(Test-Path -LiteralPath $ntcScript)){throw 'Missing native script'}
 $ntcArg='-RScriptingSystem:RunScript(ProjectName='+$ntcScript+'|ProcName=RunFixed)'
 Add-Content -LiteralPath (Join-Path $ntcWork 'RUN_DISPATCH_LOG.txt') -Value ((Get-Date -Format o)+' BEGIN '+$ntcArg)
 $ntcLaunched=Start-Process -FilePath 'C:/Program Files/Altium/AD22/X2.EXE' -ArgumentList $ntcArg -WindowStyle Normal -PassThru
 Add-Content -LiteralPath (Join-Path $ntcWork 'RUN_DISPATCH_LOG.txt') -Value ((Get-Date -Format o)+' PID '+$ntcLaunched.Id)
 Start-Sleep -Milliseconds 2000
 $ntcLaunched | Select-Object Id,ProcessName
 exit
}
Add-Type -TypeDefinition @'
using System;using System.Text;using System.Runtime.InteropServices;
public class NtcWindows{
 public delegate bool CB(IntPtr h,IntPtr p);
 [StructLayout(LayoutKind.Sequential)]public struct Rect{public int L,T,R,B;}
 [StructLayout(LayoutKind.Sequential)]public struct Pt{public int X,Y;}
 [DllImport("user32.dll")]public static extern bool EnumWindows(CB c,IntPtr p);
 [DllImport("user32.dll")]public static extern bool EnumChildWindows(IntPtr h,CB c,IntPtr p);
 [DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetClassName(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out Rect r);
 [DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
 [DllImport("user32.dll")]public static extern bool SetWindowPos(IntPtr h,IntPtr a,int x,int y,int w,int z,uint f);
 [DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
 [DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")]public static extern IntPtr GetForegroundWindow(); [DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
 [DllImport("kernel32.dll")]public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")]public static extern bool AttachThreadInput(uint a,uint b,bool v);
 [DllImport("user32.dll")]public static extern void keybd_event(byte v,byte s,uint f,UIntPtr e);
 [DllImport("user32.dll")]public static extern bool SetProcessDPIAware(); [DllImport("user32.dll")]public static extern void mouse_event(uint flags,uint dx,uint dy,uint data,UIntPtr extra); public static void PhysicalClick(int x,int y){Rect r;GetWindowRect(Main,out r);SetCursorPos(r.L+x*(r.R-r.L)/2048,r.T+y*(r.B-r.T)/1116);mouse_event(2,0,0,0,UIntPtr.Zero);mouse_event(4,0,0,0,UIntPtr.Zero);}
 [DllImport("user32.dll")]public static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")]public static extern bool ScreenToClient(IntPtr h,ref Pt p);
 [DllImport("user32.dll")]public static extern bool ClientToScreen(IntPtr h,ref Pt p);
 [DllImport("user32.dll")]public static extern IntPtr ChildWindowFromPointEx(IntPtr h,Pt p,uint f);
 public static IntPtr Main,Modal,ErrorOK,Popup,Watch,RunSelect,ViewPanel;
 public static void Focus(){uint p;var other=GetWindowThreadProcessId(GetForegroundWindow(),out p);var current=GetCurrentThreadId();AttachThreadInput(current,other,true);ShowWindow(Main,3);SetForegroundWindow(Main);AttachThreadInput(current,other,false);Console.WriteLine("FOREGROUND="+GetForegroundWindow()+" MAIN="+Main);}
 public static string Text(IntPtr h){var b=new StringBuilder(4096);GetWindowText(h,b,b.Capacity);return b.ToString();}
 public static void Find(uint pid){EnumWindows((h,p)=>{uint q;GetWindowThreadProcessId(h,out q);if(q==pid){var t=Text(h);var c=new StringBuilder(300);GetClassName(h,c,300);if(t.Contains("Altium Designer"))Main=h;if(t=="Add New Watch")Watch=h;if(t=="Select Item To Run")RunSelect=h;if(IsWindowVisible(h)){Rect vr;GetWindowRect(h,out vr);if(c.ToString()=="TClientBarControl" && vr.R-vr.L>300 && vr.R-vr.L<800 && vr.B-vr.T>250)ViewPanel=h;if(t=="Error"||t=="Information"||t=="Warning"||t.StartsWith("Design Rule Checker")||t.StartsWith("PCB Rules and Constraints Editor")||t=="Add New Watch"||t=="Engineering Change Order")Modal=h;if(t=="Error"||t=="Information"||t=="Warning"||t.StartsWith("Design Rule Checker")||t.StartsWith("PCB Rules and Constraints Editor")||t=="Add New Watch"||t=="Engineering Change Order")EnumChildWindows(h,(k,z)=>{var u=Text(k);Console.WriteLine(" CHILD "+k+" "+u);if(u.Replace("&","")==(t=="Add New Watch"?"Cancel":"OK"))ErrorOK=k;return true;},IntPtr.Zero);Console.WriteLine(h+" "+c+" "+t);if(c.ToString().Contains("SubMenu"))Popup=h;}}return true;},IntPtr.Zero);}
 public static void SetTextAt(int x,int y,string value){Rect r;GetWindowRect(Main,out r);var p=new Pt{X=r.L+x*(r.R-r.L)/2048,Y=r.T+y*(r.B-r.T)/1116};SetCursorPos(p.X,p.Y);var h=Main;ScreenToClient(h,ref p);for(int i=0;i<20;i++){var c=ChildWindowFromPointEx(h,p,3);if(c==IntPtr.Zero||c==h)break;ClientToScreen(h,ref p);ScreenToClient(c,ref p);h=c;}var cls=new StringBuilder(200);GetClassName(h,cls,200);Console.WriteLine("EDIT_TARGET="+h+" CLASS="+cls+" BEFORE="+Text(h));var s=Marshal.StringToHGlobalAnsi(value);try{SendMessage(h,12,IntPtr.Zero,s);}finally{Marshal.FreeHGlobal(s);}Console.WriteLine("AFTER="+Text(h));}
 public static void Click(int x,int y){Rect r;GetWindowRect(Main,out r);var p=new Pt{X=r.L+x*(r.R-r.L)/2048,Y=r.T+y*(r.B-r.T)/1116};SetCursorPos(p.X,p.Y);var h=Main;ScreenToClient(h,ref p);for(int i=0;i<20;i++){var c=ChildWindowFromPointEx(h,p,3);if(c==IntPtr.Zero||c==h)break;ClientToScreen(h,ref p);ScreenToClient(c,ref p);h=c;}var cs=new StringBuilder(100);GetClassName(h,cs,100);Console.WriteLine("CLICK_TARGET="+h+" CLASS="+cs+" X="+p.X+" Y="+p.Y);var lp=new IntPtr((p.Y<<16)|(p.X&65535));SendMessage(h,0x201,new IntPtr(1),lp);SendMessage(h,0x202,IntPtr.Zero,lp);}
 public static void RightClick(int x,int y){Rect r;GetWindowRect(Main,out r);SetCursorPos(r.L+x*(r.R-r.L)/2048,r.T+y*(r.B-r.T)/1116);mouse_event(8,0,0,0,UIntPtr.Zero);mouse_event(16,0,0,0,UIntPtr.Zero);}
}
'@
[NtcWindows]::SetProcessDPIAware()|Out-Null
foreach($ntcProcess in Get-Process X2){[NtcWindows]::Find($ntcProcess.Id)}
if($Action -eq 'Windows'){exit}
if($Action -eq 'ResizeViewPanel'){if([NtcWindows]::ViewPanel -eq [IntPtr]::Zero){throw 'No floating view panel'};[NtcWindows]::SetWindowPos([NtcWindows]::ViewPanel,[IntPtr]::Zero,100,100,520,850,4)|Out-Null;exit}
if($Action -eq 'ScrollViewPanel'){if([NtcWindows]::ViewPanel -eq [IntPtr]::Zero){throw 'No floating view panel'};$vr=New-Object NtcWindows+Rect;[NtcWindows]::GetWindowRect([NtcWindows]::ViewPanel,[ref]$vr)|Out-Null;[NtcWindows]::SetCursorPos($vr.L+350,$vr.T+500)|Out-Null;$wheel=[BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$X),0);[NtcWindows]::mouse_event(2048,0,0,$wheel,[UIntPtr]::Zero);exit}
if($Action -eq 'ClickViewPanel'){if([NtcWindows]::ViewPanel -eq [IntPtr]::Zero){throw 'No floating view panel'};[NtcWindows]::Main=[NtcWindows]::ViewPanel;[NtcWindows]::ShowWindow([NtcWindows]::ViewPanel,5)|Out-Null;[NtcWindows]::SetForegroundWindow([NtcWindows]::ViewPanel)|Out-Null;Start-Sleep -Milliseconds 150;[NtcWindows]::PhysicalClick($X,$Y);exit}
if($Action -eq 'KeysMain'){if([NtcWindows]::Main -eq [IntPtr]::Zero){throw 'No main window'};[NtcWindows]::Focus();Add-Type -AssemblyName System.Windows.Forms;[System.Windows.Forms.SendKeys]::SendWait($Value);exit}
if($Action -eq 'KeysModal'){if([NtcWindows]::Modal -eq [IntPtr]::Zero){throw 'No modal'};[NtcWindows]::SetForegroundWindow([NtcWindows]::Modal)|Out-Null;Add-Type -AssemblyName System.Windows.Forms;[System.Windows.Forms.SendKeys]::SendWait($Value);exit}
if($Action -eq 'ClickPopup'){if([NtcWindows]::Popup -eq [IntPtr]::Zero){throw 'No popup'};$ntcPopRect=New-Object NtcWindows+Rect;[NtcWindows]::GetWindowRect([NtcWindows]::Popup,[ref]$ntcPopRect)|Out-Null;if($X -lt 0 -or $Y -lt 0 -or $X -ge ($ntcPopRect.R-$ntcPopRect.L) -or $Y -ge ($ntcPopRect.B-$ntcPopRect.T)){throw 'Popup coordinates outside observed bounds'};[NtcWindows]::SetCursorPos(($ntcPopRect.L+$X),($ntcPopRect.T+$Y))|Out-Null;[NtcWindows]::mouse_event(2,0,0,0,[UIntPtr]::Zero);[NtcWindows]::mouse_event(4,0,0,0,[UIntPtr]::Zero);exit}
if($Action -eq 'SetDrcLimit'){
 if([NtcWindows]::Modal -eq [IntPtr]::Zero -or -not([NtcWindows]::Text([NtcWindows]::Modal).StartsWith('Design Rule Checker'))){throw 'DRC dialog not active'}
 $ntcPrior=[NtcWindows]::Main
 [NtcWindows]::Main=[NtcWindows]::Modal
 [NtcWindows]::Focus()
 [NtcWindows]::Click(440,309)
 Add-Type -AssemblyName System.Windows.Forms
 [NtcWindows]::SetTextAt(440,309,'10000')
 [NtcWindows]::Main=$ntcPrior
 exit
}
if($Action -eq 'SetModalText'){if([NtcWindows]::Modal -eq [IntPtr]::Zero){throw 'No modal'};$ntcOrig=[NtcWindows]::Main;[NtcWindows]::Main=[NtcWindows]::Modal;[NtcWindows]::SetTextAt($X,$Y,$Value);[NtcWindows]::Main=$ntcOrig;exit}
if($Action -eq 'PhysicalClick'){[NtcWindows]::PhysicalClick($X,$Y);exit}
if($Action -eq 'Click'){[NtcWindows]::Click($X,$Y);exit}
if($Action -eq 'RightClickModal'){if([NtcWindows]::Modal -eq [IntPtr]::Zero){throw 'No modal'};[NtcWindows]::Main=[NtcWindows]::Modal;[NtcWindows]::RightClick($X,$Y);exit}
if($Action -eq 'ClickModal'){
 if([NtcWindows]::Modal -eq [IntPtr]::Zero){throw 'No modal found'}
 $ntcOrig=[NtcWindows]::Main
 [NtcWindows]::Main=[NtcWindows]::Modal
 [NtcWindows]::Click($X,$Y)
 [NtcWindows]::Main=$ntcOrig
 exit
}
if($Action -in @('CloseWatch','CloseRunSelect')){$ntcClose=if($Action -eq 'CloseRunSelect'){[NtcWindows]::RunSelect}else{[NtcWindows]::Watch};if($ntcClose -ne [IntPtr]::Zero){[NtcWindows]::PostMessage($ntcClose,16,[IntPtr]0,[IntPtr]0)|Out-Null};exit}
if($Action -eq 'StopMenu'){
 if([NtcWindows]::Popup -eq [IntPtr]::Zero){throw 'Debugger Run menu must be open'}
 $ntcPopupRect=New-Object NtcWindows+Rect; [NtcWindows]::GetWindowRect([NtcWindows]::Popup,[ref]$ntcPopupRect)|Out-Null; [NtcWindows]::SetCursorPos(($ntcPopupRect.L+60),($ntcPopupRect.T+204))|Out-Null; $ntcPoint=[IntPtr]((204 -shl 16) -bor 60)
 [NtcWindows]::PostMessage([NtcWindows]::Popup,513,[IntPtr]1,$ntcPoint)|Out-Null
 [NtcWindows]::PostMessage([NtcWindows]::Popup,514,[IntPtr]0,$ntcPoint)|Out-Null
 exit
}
if($Action -eq 'DismissError'){if([NtcWindows]::ErrorOK -ne [IntPtr]::Zero){[NtcWindows]::PostMessage([NtcWindows]::ErrorOK,513,[IntPtr]1,[IntPtr]655370)|Out-Null;[NtcWindows]::PostMessage([NtcWindows]::ErrorOK,514,[IntPtr]0,[IntPtr]655370)|Out-Null};exit}
if([NtcWindows]::Main -eq [IntPtr]::Zero){throw 'No Altium window'}
[NtcWindows]::SetProcessDPIAware()|Out-Null
if($Action -notin @('CaptureModal','CapturePopup','CaptureViewPanel')){[NtcWindows]::Focus()}
Start-Sleep -Milliseconds 300
if($Action -eq 'StopScript'){
 [NtcWindows]::Focus()
 Start-Sleep -Milliseconds 250
 [NtcWindows]::keybd_event(17,0,0,[UIntPtr]::Zero)
 [NtcWindows]::keybd_event(114,0,0,[UIntPtr]::Zero)
 [NtcWindows]::keybd_event(114,0,2,[UIntPtr]::Zero)
 [NtcWindows]::keybd_event(17,0,2,[UIntPtr]::Zero)
 exit
}
if($Action -eq 'SelectPDF'){[NtcWindows]::Click(1770,282);exit}
if($Action -eq 'RunMenu'){if([NtcWindows]::Text([NtcWindows]::Main) -notlike '*.PrjScr - Altium*'){throw 'Activate the paused script tab before opening its Run menu'};[NtcWindows]::Click(175,35);exit}
if($Action -eq 'GeneratePDF'){[NtcWindows]::Click(1950,300);exit}
Add-Type -AssemblyName System.Drawing
$ntcWindow=[NtcWindows]::Main
if($Action -eq 'CaptureViewPanel'){$ntcWindow=[NtcWindows]::ViewPanel;if($ntcWindow -eq [IntPtr]::Zero){throw 'No floating view panel'}}
if($Action -eq 'CaptureModal'){$ntcWindow=[NtcWindows]::Modal;if($ntcWindow -eq [IntPtr]::Zero){throw 'No modal found'};[NtcWindows]::ShowWindow($ntcWindow,5)|Out-Null}
if($Action -eq 'CapturePopup'){$ntcWindow=[NtcWindows]::Popup;if($ntcWindow -eq [IntPtr]::Zero){throw 'No popup found'}}
$ntcRect=New-Object NtcWindows+Rect
[NtcWindows]::GetWindowRect($ntcWindow,[ref]$ntcRect)|Out-Null
$ntcBitmap=New-Object System.Drawing.Bitmap ($ntcRect.R-$ntcRect.L),($ntcRect.B-$ntcRect.T)
$ntcGraphics=[System.Drawing.Graphics]::FromImage($ntcBitmap)
$ntcDC=$ntcGraphics.GetHdc()
[NtcWindows]::PrintWindow($ntcWindow,$ntcDC,2)|Out-Null
$ntcGraphics.ReleaseHdc($ntcDC)
$ntcBitmap.Save((Join-Path $ntcWork 'altium_current.png'))
$ntcGraphics.Dispose();$ntcBitmap.Dispose()
















