@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File scripts\build_onefile_exe.ps1
pause

