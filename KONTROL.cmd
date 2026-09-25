@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
 echo Once KURULUM.cmd dosyasini calistirin.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m purffle_shorts.factory doctor
pause
