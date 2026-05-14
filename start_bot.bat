@echo off
echo ========================================
echo   DISCORD MUSIC BOT  ^|  Lavalink Mode
echo ========================================
echo.

:: ── Verificar Java ───────────────────────────────────────────────────────────
where java >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Java no encontrado. Instala Java 17+ para usar Lavalink.
    echo         https://adoptium.net/
    echo.
    echo Iniciando bot en modo FFmpeg ^(sin Lavalink^)...
    echo.
    python bot.py
    pause
    exit /b
)

:: ── Verificar Lavalink.jar ───────────────────────────────────────────────────
if not exist "lavalink\Lavalink.jar" (
    echo [AVISO] No se encontro lavalink\Lavalink.jar
    echo         Descargalo desde: https://github.com/lavalink-devs/Lavalink/releases
    echo.
    echo Iniciando bot en modo FFmpeg ^(sin Lavalink^)...
    echo.
    python bot.py
    pause
    exit /b
)

:: ── Arrancar Lavalink en ventana separada ────────────────────────────────────
echo [1/2] Iniciando servidor Lavalink...
start "Lavalink Server" cmd /k "cd /d %~dp0lavalink && java -jar Lavalink.jar"

:: Esperar 8 segundos para que Lavalink levante antes de arrancar el bot
echo       Esperando 8s para que Lavalink arranque...
timeout /t 8 /nobreak >nul

:: ── Arrancar el bot ──────────────────────────────────────────────────────────
echo [2/2] Iniciando bot...
echo.
python bot_lavalink.py

pause
