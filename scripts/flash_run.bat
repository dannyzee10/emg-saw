@echo off
REM ===================================================================
REM  Flash + run the Blue Pill firmware via the ST-LINK Programmer CLI.
REM  Use this INSTEAD of the CubeIDE Debug/Run buttons (the clone
REM  ST-LINK can't hold a live debug connection, but the Programmer
REM  works reliably).
REM
REM  Workflow:  edit code -> Build in CubeIDE (Ctrl+B) -> double-click me
REM ===================================================================
setlocal

set "CLI=C:\ST\STM32CubeIDE_1.16.1\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.1.400.202404281720\tools\bin\STM32_Programmer_CLI.exe"
set "ELF=C:\Users\PMLS\STM32CubeIDE\workspace_1.16.1\emg_bluepill\Debug\emg_bluepill.elf"

echo.
echo === Flashing %ELF%
echo.
"%CLI%" -c port=SWD mode=UR -w "%ELF%" -v -rst -run

echo.
echo If you see "Core run" above, the firmware is flashing and running.
echo (If you see a connect error, unplug/replug the ST-LINK USB and retry.)
echo.
pause
