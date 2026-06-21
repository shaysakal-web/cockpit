@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_run_desk.ps1"
if errorlevel 1 pause
