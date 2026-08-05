@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM  Publica el panel de estado en GitHub Pages.
REM  Repo: https://github.com/claudioflores-prof/panel-lms
REM  Deja un registro completo en  publicar.log
REM ============================================================

cd /d "%~dp0"
set LOG=%~dp0publicar.log

echo ================================================== > "%LOG%"
echo  Registro de publicacion  %DATE% %TIME%           >> "%LOG%"
echo  Carpeta: %CD%                                    >> "%LOG%"
echo ================================================== >> "%LOG%"
echo. >> "%LOG%"

echo.
echo ============================================
echo   Publicando el panel de estado
echo   Carpeta: %CD%
echo ============================================
echo.

REM --- 0. Diagnostico previo ---
echo --- git disponible --- >> "%LOG%"
where git >> "%LOG%" 2>&1
git --version >> "%LOG%" 2>&1
echo. >> "%LOG%"

echo --- identidad configurada --- >> "%LOG%"
git config user.name >> "%LOG%" 2>&1
git config user.email >> "%LOG%" 2>&1
echo. >> "%LOG%"

echo --- archivos presentes --- >> "%LOG%"
dir /b >> "%LOG%" 2>&1
echo. >> "%LOG%"

REM --- 1. Repo local ---
echo [1/6] Repositorio local...
echo --- paso 1: git init --- >> "%LOG%"
if not exist ".git" (
    git init >> "%LOG%" 2>&1
    git branch -M main >> "%LOG%" 2>&1
    echo   creado. >> "%LOG%"
) else (
    echo   ya existia. >> "%LOG%"
)
echo. >> "%LOG%"

REM --- 2. Remoto ---
echo [2/6] Conexion con GitHub...
echo --- paso 2: remote --- >> "%LOG%"
git remote remove origin >nul 2>&1
git remote add origin https://github.com/claudioflores-prof/panel-lms.git >> "%LOG%" 2>&1
git remote -v >> "%LOG%" 2>&1
echo. >> "%LOG%"

REM --- 3. Agregar archivos ---
echo [3/6] Preparando archivos...
echo --- paso 3: git add --- >> "%LOG%"
git add index.html README.md publicar.bat >> "%LOG%" 2>&1
git status --short >> "%LOG%" 2>&1
echo. >> "%LOG%"

REM --- 4. Commit ---
echo [4/6] Guardando version...
echo --- paso 4: git commit --- >> "%LOG%"
git commit -m "Actualiza panel de estado" >> "%LOG%" 2>&1
echo   codigo de salida commit: !errorlevel! >> "%LOG%"
git log --oneline >> "%LOG%" 2>&1
echo. >> "%LOG%"

REM --- 5. Rama ---
echo [5/6] Verificando rama...
echo --- paso 5: rama actual --- >> "%LOG%"
git branch -M main >> "%LOG%" 2>&1
git branch -a >> "%LOG%" 2>&1
echo. >> "%LOG%"

REM --- 6. Push ---
echo [6/6] Subiendo a GitHub...
echo.
echo   Si se abre una ventana de inicio de sesion,
echo   entra con la cuenta  claudioflores-prof
echo.
echo --- paso 6: git push --- >> "%LOG%"
git push -u origin main >> "%LOG%" 2>&1
set PUSHERR=!errorlevel!
echo   codigo de salida push: !PUSHERR! >> "%LOG%"
echo. >> "%LOG%"

echo --- estado final --- >> "%LOG%"
git log --oneline -3 >> "%LOG%" 2>&1
git remote -v >> "%LOG%" 2>&1
git status >> "%LOG%" 2>&1

echo.
echo ============================================
echo   RESULTADO
echo ============================================
type "%LOG%"
echo.
echo ============================================
if "!PUSHERR!"=="0" (
    echo   Push completado.
    echo   https://claudioflores-prof.github.io/panel-lms/
) else (
    echo   El push FALLO. Codigo: !PUSHERR!
    echo   El detalle quedo en publicar.log
)
echo ============================================
echo.
pause
