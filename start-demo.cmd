@echo off
cd /d "%~dp0"
python -m home_agent %*
if errorlevel 1 pause
