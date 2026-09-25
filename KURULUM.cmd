@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\setup.ps1" %*
set "result=%errorlevel%"
pause
exit /b %result%
