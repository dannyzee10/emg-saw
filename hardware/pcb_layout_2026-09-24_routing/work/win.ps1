param([ValidateSet('List','Capture','ClickButton','Controls','SetCheck','SelectListIndex','Close')][string]$Action='List',[string]$Title='',[string]$Text='',[int]$Value=0,[string]$Out='')
# Window helper for the running Altium (X2.EXE): list windows, capture one by title,
# enumerate its child controls, click a button by caption (BM_CLICK), set a checkbox.
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;using System.Text;using System.Runtime.InteropServices;using System.Collections.Generic;
public class W{
 public delegate bool CB(IntPtr h,IntPtr p);
 [StructLayout(LayoutKind.Sequential)]public struct R{public int L,T,Ri,B;}
 [DllImport("user32.dll")]public static extern bool EnumWindows(CB c,IntPtr p);
 [DllImport("user32.dll")]public static extern bool EnumChildWindows(IntPtr h,CB c,IntPtr p);
 [DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetClassName(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out R r);
 [DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
 [DllImport("user32.dll")]public static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")]public static extern bool SetProcessDPIAware();
 public static string T(IntPtr h){var b=new StringBuilder(1024);GetWindowText(h,b,b.Capacity);return b.ToString();}
 public static string C(IntPtr h){var b=new StringBuilder(256);GetClassName(h,b,b.Capacity);return b.ToString();}
 public static List<IntPtr> Tops(uint pid){var l=new List<IntPtr>();EnumWindows((h,p)=>{uint q;GetWindowThreadProcessId(h,out q);if(q==pid&&IsWindowVisible(h))l.Add(h);return true;},IntPtr.Zero);return l;}
 public static List<IntPtr> Kids(IntPtr w){var l=new List<IntPtr>();EnumChildWindows(w,(h,p)=>{l.Add(h);return true;},IntPtr.Zero);return l;}
}
'@
[W]::SetProcessDPIAware()|Out-Null
$pid_=(Get-Process X2 | Sort-Object StartTime | Select-Object -First 1).Id
$tops=[W]::Tops([uint32]$pid_)
function Find-Top([string]$t){ foreach($h in $tops){ if([W]::T($h) -like $t){ return $h } }; throw "No window like '$t'" }
switch($Action){
 'List' { foreach($h in $tops){ $r=New-Object W+R;[W]::GetWindowRect($h,[ref]$r)|Out-Null; "{0} [{1}] '{2}' {3}x{4}" -f $h,[W]::C($h),[W]::T($h),($r.Ri-$r.L),($r.B-$r.T) } }
 'Controls' { $w=Find-Top $Title; foreach($k in [W]::Kids($w)){ $t=[W]::T($k); if($t -ne '' -or $Text -eq 'all'){ $r=New-Object W+R;[W]::GetWindowRect($k,[ref]$r)|Out-Null; "{0} [{1}] '{2}' @{3},{4} vis={5}" -f $k,[W]::C($k),$t,$r.L,$r.T,[W]::IsWindowVisible($k) } } }
 'Capture' { Add-Type -AssemblyName System.Drawing; $w=Find-Top $Title; $r=New-Object W+R;[W]::GetWindowRect($w,[ref]$r)|Out-Null; $bmp=New-Object System.Drawing.Bitmap ($r.Ri-$r.L),($r.B-$r.T); $g=[System.Drawing.Graphics]::FromImage($bmp); $dc=$g.GetHdc(); [W]::PrintWindow($w,$dc,2)|Out-Null; $g.ReleaseHdc($dc); $bmp.Save($Out); $g.Dispose(); $bmp.Dispose(); "saved $Out" }
 'ClickButton' { $w=Find-Top $Title; $hit=$null; foreach($k in [W]::Kids($w)){ if(([W]::T($k)).Replace('&','') -eq $Text -and [W]::IsWindowVisible($k)){ $hit=$k } }; if(-not $hit){ throw "No button '$Text'" }; $r=New-Object W+R;[W]::GetWindowRect($hit,[ref]$r)|Out-Null; $cx=[int](($r.Ri-$r.L)/2); $cy=[int](($r.B-$r.T)/2); $lp=[IntPtr](($cy -shl 16) -bor $cx); [W]::SendMessage($hit,0x0201,[IntPtr]1,$lp)|Out-Null; [W]::SendMessage($hit,0x0202,[IntPtr]0,$lp)|Out-Null; "clicked $Text ($hit)" }
 'Close' { $w=Find-Top $Title; [W]::PostMessage($w,0x0010,[IntPtr]0,[IntPtr]0)|Out-Null; "WM_CLOSE sent to $Title" }
 'SetCheck' { $w=Find-Top $Title; foreach($k in [W]::Kids($w)){ if(([W]::T($k)).Replace('&','') -eq $Text){ [W]::SendMessage($k,0x00F1,[IntPtr]$Value,[IntPtr]0)|Out-Null; "set $Text=$Value" } } }
}
