"""
Punto de entrada del Bot de Música.

Modo LOCAL  (LAVALINK_LOCAL=true, por defecto):
  - Arranca el servidor Lavalink desde lavalink/Lavalink.jar
  - Espera a que esté listo, luego inicia el bot

Modo CLOUD  (LAVALINK_LOCAL=false):
  - No intenta arrancar ningún proceso Java
  - El bot se conecta directamente al servidor indicado
    en LAVALINK_HOST / LAVALINK_PORT / LAVALINK_PASSWORD

Uso: python main.py
"""

import subprocess
import sys
import time
import shutil
import os
import urllib.request
import asyncio
from aiohttp import web

from config import (
    DISCORD_TOKEN,
    LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD,
    LAVALINK_LOCAL,
)

# ─── Rutas ───────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
LAVALINK_DIR = os.path.join(BASE_DIR, 'lavalink')
LAVALINK_JAR = os.path.join(LAVALINK_DIR, 'Lavalink.jar')


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _java_available() -> bool:
    return shutil.which('java') is not None


def _lavalink_ready(timeout: int = 45) -> bool:
    """Espera hasta que el endpoint HTTP de Lavalink responda."""
    url = f'http://{LAVALINK_HOST}:{LAVALINK_PORT}/version'
    req = urllib.request.Request(url, headers={'Authorization': LAVALINK_PASSWORD})
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=2):
                return True
        except Exception:
            time.sleep(1)
    return False


# ─── Arranque de Lavalink (solo modo local) ──────────────────────────────────

def start_lavalink() -> subprocess.Popen | None:
    """
    Lanza el servidor Lavalink como proceso hijo (solo en modo LOCAL).
    Devuelve el proceso o None si no fue posible.
    """
    if not LAVALINK_LOCAL:
        return None  # modo cloud: nada que arrancar aquí

    if not _java_available():
        print('⚠️  Java no encontrado – Lavalink no se iniciará localmente.')
        print('   Instala Java 17+: https://adoptium.net/')
        print('   O usa un servidor externo con LAVALINK_LOCAL=false')
        return None

    if not os.path.exists(LAVALINK_JAR):
        print('⚠️  lavalink/Lavalink.jar no encontrado.')
        print('   Descárgalo de: https://github.com/lavalink-devs/Lavalink/releases')
        print('   O usa un servidor externo con LAVALINK_LOCAL=false')
        return None

    print('🚀 Iniciando servidor Lavalink local...')
    proc = subprocess.Popen(
        ['java', '-jar', LAVALINK_JAR],
        cwd=LAVALINK_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print('   Esperando a que Lavalink esté listo', end='', flush=True)
    if _lavalink_ready(timeout=45):
        print(' ✅')
    else:
        print(' ⚠️  (timeout – el bot intentará conectarse igualmente)')

    return proc

# ─── Health-check HTTP server (para Render Web Service) ──────────────────────

async def start_health_server():
    """
    Servidor HTTP mínimo que responde 200 OK en /health.
    Render necesita que el proceso escuche en un puerto para no matarlo.
    Escucha en el puerto indicado por la variable PORT (Render lo asigna automáticamente).
    """
    port = int(os.getenv('PORT', '10000'))

    async def health(request):
        return web.Response(text='OK')

    app = web.Application()
    app.router.add_get('/', health)
    app.router.add_get('/health', health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f'🌐 Health server escuchando en puerto {port}')


# ─── Arranque del bot ─────────────────────────────────────────────────────────

async def run_bot():
    """Arranca el bot de Discord de forma asíncrona."""
    import discord
    from bot import bot

    try:
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        print('❌ Token de Discord inválido')
        sys.exit(1)


def main():
    print('=' * 60)
    print('   DISCORD MUSIC BOT  |  Lavalink Mode')
    print('=' * 60)

    if not DISCORD_TOKEN or DISCORD_TOKEN == 'PEGA_TU_TOKEN_AQUI':
        print('❌ Token de Discord no configurado en .env')
        sys.exit(1)

    if LAVALINK_LOCAL:
        print('📦 Modo: LOCAL  (arrancando Lavalink.jar)')
    else:
        if LAVALINK_HOST in ('localhost', '127.0.0.1'):
            print('⚠️  LAVALINK_HOST=localhost en modo cloud, usando nodo público de fallback.')
            import config as _cfg
            _cfg.LAVALINK_HOST     = 'lavalink.darrennathanael.com'
            _cfg.LAVALINK_PORT     = 80
            _cfg.LAVALINK_PASSWORD = 'youshallnotpass'
        else:
            print(f'☁️  Modo: CLOUD  (conectando a {LAVALINK_HOST}:{LAVALINK_PORT})')

    lavalink_proc = start_lavalink()

    async def async_main():
        # Arrancar health server y bot en paralelo
        on_render = bool(os.getenv('PORT'))
        if on_render:
            await start_health_server()
        await run_bot()

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print('\n👋 Bot detenido')
    finally:
        if lavalink_proc and lavalink_proc.poll() is None:
            print('🛑 Deteniendo servidor Lavalink...')
            lavalink_proc.terminate()
            try:
                lavalink_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                lavalink_proc.kill()


if __name__ == '__main__':
    main()
