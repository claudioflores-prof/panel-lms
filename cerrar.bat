@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  Cierra una tarea del plan en el panel de estado.
REM  Doble clic para usarlo.
REM ============================================================

cd /d "%~dp0"
set PY=%~dp0..\venv\Scripts\python.exe

if not exist "%PY%" (
    echo.
    echo   AVISO: no encuentro el entorno virtual del proyecto.
    echo   Uso el python del sistema.
    echo.
    set PY=python
)

"%PY%" "%~dp0cerrar.py"

echo.
set /p PUB="Publicar ahora el panel actualizado? (S/N): "
if /i "%PUB%"=="S" (
    call "%~dp0publicar.bat"
) else (
    echo.
    echo   No se publico. Puedes hacerlo despues con publicar.bat,
    echo   o dejar que lo haga el proceso nocturno.
    echo.
    pause
)
