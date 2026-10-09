@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist "app.py" goto missing_files
if not exist "requirements.txt" goto missing_files
if exist ".venv\Scripts\python.exe" goto check_environment

echo Looking for 64-bit Python 3.10, 3.11, 3.12 or 3.13...
for %%V in (3.12 3.13 3.11 3.10) do (
    py -%%V -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
    if not errorlevel 1 (
        set "ST_PROJECT_PYTHON=py -%%V"
        goto create_environment
    )
)
python -c "import sys, struct; assert sys.version_info[:2] in [(3,10),(3,11),(3,12),(3,13)] and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto missing_python
set "ST_PROJECT_PYTHON=python"

:create_environment
echo Creating the project's Python environment...
%ST_PROJECT_PYTHON% --version
%ST_PROJECT_PYTHON% -m venv .venv
if errorlevel 1 goto failed

:check_environment
.venv\Scripts\python.exe -c "import sys, struct; assert sys.version_info[:2] in [(3,10),(3,11),(3,12),(3,13)] and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto broken_environment
.venv\Scripts\python.exe -c "import streamlit, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo Installing dashboard packages. This needs an internet connection...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto failed
)
echo Opening the dashboard. Keep this window open while using it.
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0

:missing_python
echo.
echo No compatible 64-bit Python installation was found.
echo Open Microsoft Store, search for Python 3.12, and install the free
echo package published by Python Software Foundation.
echo Then close this window and double-click run_windows.bat again.
echo.
echo Already installed Python? Open Command Prompt and run: py --list
echo This launcher supports Python 3.10 through 3.13. It does not use 3.14+.
pause
exit /b 1

:broken_environment
echo The existing .venv environment cannot run a compatible Python version.
echo Rename the .venv folder to .venv-old, then run this launcher again.
pause
exit /b 1

:missing_files
echo Please extract the COMPLETE ZIP first, then run this file inside
echo the extracted Severn-Trent-Streamlit folder alongside app.py.
pause
exit /b 1

:failed
echo Setup or launch failed. Read the message above and the Windows steps in README.md.
pause
exit /b 1
