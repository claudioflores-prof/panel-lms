@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  Registra el proceso nocturno en el Programador de tareas
REM  de Windows. Ejecutar UNA sola vez, con doble clic.
REM ============================================================

set TAREA=Panel LMS - sincronizar y publicar
set HORA=22:30

echo.
echo ============================================
echo   Instalar el proceso nocturno del panel
echo ============================================
echo.
echo   Tarea : %TAREA%
echo   Hora  : %HORA% todos los dias
echo   Accion: leer el historial de git, actualizar el
echo           panel y publicarlo en GitHub Pages.
echo.
echo   IMPORTANTE: si el equipo esta apagado a esa hora,
echo   la tarea NO se ejecuta y no se recupera sola.
echo   Elige una hora en que el equipo suele estar encendido.
echo.
echo   Para cambiar la hora: edita la linea  set HORA=  de
echo   este archivo y vuelve a ejecutarlo.
echo.
set /p SEGUIR="Instalar la tarea? (S/N): "
if /i not "%SEGUIR%"=="S" (
    echo.
    echo   Cancelado. No se instalo nada.
    echo.
    pause
    exit /b 0
)

echo.
schtasks /create /tn "%TAREA%" /tr "\"%~dp0nocturno.bat\" /auto" /sc daily /st %HORA% /f

if errorlevel 1 (
    echo.
    echo   ERROR al crear la tarea.
    echo   Prueba ejecutando este archivo como administrador:
    echo   clic derecho ^> Ejecutar como administrador.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Tarea instalada.
echo.
echo   Para verla, cambiarla o borrarla:
echo   Menu Inicio ^> Programador de tareas ^>
echo   Biblioteca del Programador de tareas ^>
echo   "%TAREA%"
echo.
echo   Para desinstalarla desde aqui, ejecuta:
echo   schtasks /delete /tn "%TAREA%" /f
echo.
echo   Para probarla ahora sin esperar a la noche,
echo   haz doble clic en  nocturno.bat
echo ============================================
echo.
pause
