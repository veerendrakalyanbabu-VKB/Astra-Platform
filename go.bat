@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File go.ps1
pause
