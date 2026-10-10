@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  start "PROJECT COMMAND 404" cmd /k "py -m http.server 8765 --bind 127.0.0.1"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Necesitas Python 3 o un servidor HTTP local. Consulta README.md
    pause
    exit /b 1
  )
  start "PROJECT COMMAND 404" cmd /k "python -m http.server 8765 --bind 127.0.0.1"
)
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"
endlocal
