"""Run a script via runpy and print the Windows peak working set on exit (no psutil needed)."""
import ctypes, ctypes.wintypes as W, runpy, sys


class PMC(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('PageFaultCount', W.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t)]


def peak_mb():
    c = PMC(); c.cb = ctypes.sizeof(c)
    k32 = ctypes.WinDLL('kernel32'); k32.GetCurrentProcess.restype = W.HANDLE
    gpmi = ctypes.WinDLL('psapi').GetProcessMemoryInfo
    gpmi.argtypes = [W.HANDLE, ctypes.POINTER(PMC), W.DWORD]; gpmi.restype = W.BOOL
    gpmi(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize >> 20, c.PeakPagefileUsage >> 20


sys.argv = sys.argv[1:]
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
finally:
    print('PEAK_WS_MB %d PEAK_COMMIT_MB %d' % peak_mb(), flush=True)
