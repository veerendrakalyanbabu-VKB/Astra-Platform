@echo off

cd /d "%~dp0"
REM PowerShell: use .\astra.bat or .\astra.ps1


:menu

cls

echo.

echo   ==============================

echo     A S T R A   v3.2  LAUNCHER

echo   ==============================

echo.

echo   1.  Command OS Desktop   (8501)

echo   2.  Mobile Companion    (8502)

echo   3.  Portal + Free Trial (8503)

echo   4.  Terminal REPL

echo   5.  Voice Mode

echo   6.  API Server

echo   7.  Status Check

echo   8.  Run Tests

echo   9.  Setup

echo   0.  Exit

echo.

set /p choice="Choose: "



if "%choice%"=="1" python main.py --desktop & goto menu

if "%choice%"=="2" python main.py --mobile & goto menu

if "%choice%"=="3" python main.py --portal & goto menu

if "%choice%"=="4" python main.py & goto menu

if "%choice%"=="5" python main.py --voice & goto menu

if "%choice%"=="6" python main.py --serve & goto menu

if "%choice%"=="7" python main.py --status & pause & goto menu

if "%choice%"=="8" python -m pytest tests/ -q & pause & goto menu

if "%choice%"=="9" powershell -ExecutionPolicy Bypass -File setup.ps1 & pause & goto menu

if "%choice%"=="0" exit

goto menu

