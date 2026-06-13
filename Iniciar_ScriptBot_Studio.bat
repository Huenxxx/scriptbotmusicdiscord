@echo off
title ScriptBot Studio - Cargando...
color 0b
echo ==========================================
echo       SCRIPTBOT STUDIO - INICIANDO
echo ==========================================
echo.
echo [*] Comprobando e instalando dependencias (por favor, espera)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [X] Error al instalar las dependencias con pip.
    echo Asegurate de tener Python instalado y anadido al PATH.
    pause
    exit /b
)
echo [*] Dependencias listas.
echo [*] Iniciando ScriptBot Studio...
echo.
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [X] La aplicacion se ha cerrado con un error.
    pause
)
