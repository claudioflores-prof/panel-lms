@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  Proceso nocturno: sincroniza el panel con el historial de
REM  git y lo publica. Lo ejecuta el Programador de tareas de
REM  Windows. Tambien se puede correr a mano con doble clic.
REM
REM  Deja el registro completo en  nocturno.log
REM ============================================================

cd /d "%~dp0"
set LOG=%~dp0nocturno.log
set PY=%~dp0..\venv\Scripts\python.exe

echo ================================================== >> "%LOG%"
echo  Proceso nocturno  %DATE% %TIME%                   >> "%LOG%"
echo ================================================== >> "%LOG%"

REM --- 1. Sincronizar con git ---
if not exist "%PY%" (
    echo ERROR: no encuentro el entorno virtual en %PY%          >> "%LOG%"
    echo Uso el python del sistema como respaldo.                >> "%LOG%"
    set PY=python
)

echo --- sincronizar.py --- >> "%LOG%"
"%PY%" "%~dp0sincronizar.py" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo ERROR en sincronizar.py, no se publica nada. >> "%LOG%"
    exit /b 1
)

REM --- 2. Publicar ---
echo --- publicar.bat --- >> "%LOG%"
call "%~dp0publicar.bat" /auto >> "%LOG%" 2>&1

echo. >> "%LOG%"
echo Proceso nocturno terminado. >> "%LOG%"
echo. >> "%LOG%"

REM Si se ejecuto con doble clic (no desde el Programador), mostrar el resultado.
if /i not "%~1"=="/auto" (
    type "%LOG%"
    echo.
    pause
)
