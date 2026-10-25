@echo off
rem Build the game executable only; no disc image needed (play.bat wants one
rem because it also starts the game). Output: tmp\pc\game32\memories-pc.exe
rem with SDL3.dll, languages\ and mods\ (ow-poc.o is rebuilt and deployed by
rem this build too). Pass "nopause" to skip the final prompt in a script.
setlocal DisableDelayedExpansion
cd /d "%~dp0"

rem A Python 3.8+: the installed one (the Microsoft Store placeholder fails
rem this check), then the py launcher, then the private copy play.bat fetches.
set PYTHON=
python -c "import sys; sys.exit(sys.version_info < (3, 8))" >nul 2>&1 && set PYTHON=python
if not defined PYTHON (
    py -3 -c "import sys; sys.exit(sys.version_info < (3, 8))" >nul 2>&1 && set "PYTHON=py -3"
)
if not defined PYTHON if exist tmp\pc\tools\python\python.exe set "PYTHON=%CD%\tmp\pc\tools\python\python.exe"
if not defined PYTHON (
    echo No Python 3.8 or newer found. Install Python, or run play.bat once to
    echo let it fetch a private copy into tmp\pc\tools\python.
    goto :failed
)

echo Building with %PYTHON%
echo The first build fetches zlib, libpng, freetype, SDL3 and llvm-mingw into
echo tmp\pc ^(a few minutes, needs internet^); later builds reuse them.
echo.
%PYTHON% tools\pc\build.py --target windows || goto :failed

echo.
echo Build OK: "%CD%\tmp\pc\game32\memories-pc.exe"
echo To play, put your USA disc .bin in "%CD%\game" and run play.bat.
if /i not "%~1"=="nopause" pause
exit /b 0

:failed
echo.
echo Build FAILED; see the messages above.
if /i not "%~1"=="nopause" pause
exit /b 1
