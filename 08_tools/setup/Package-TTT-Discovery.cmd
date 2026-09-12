@echo off
setlocal
set "SCRIPT=%~dp0Package-TTT-Discovery.ps1"

if "%~1"=="" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -Subject ALL -Revision A
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -Subject "%~1" -Revision "%~2"
)

endlocal
