@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if not exist ".venv\Scripts\python.exe" (
 echo Once KURULUM.cmd dosyasini calistirin.
 pause
 exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\start-ollama.ps1"
if errorlevel 1 (
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m purffle_shorts.factory studio
pause
