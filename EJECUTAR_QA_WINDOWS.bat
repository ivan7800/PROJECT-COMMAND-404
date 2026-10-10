@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (set "PY=py") else (set "PY=python")
%PY% -c "import playwright" >nul 2>&1
if errorlevel 1 (
  echo Instalando Playwright en el Python actual...
  %PY% -m pip install playwright || goto :error
)
%PY% -m playwright install chromium || goto :error
%PY% tests\e2e.py || goto :error
echo.
echo QA AUTOMATIZADO SUPERADO.
pause
exit /b 0
:error
echo.
echo QA NO SUPERADO. No publiques como version estable.
pause
exit /b 1
