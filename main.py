"""
Punto de entrada del Bot de Música.

Arranca automáticamente:
  1. El servidor Lavalink (en background) si existe lavalink/Lavalink.jar
  2. El bot de Discord

Uso: python main.py
"""

import subprocess
import sys
import time
import shutil
import os
import urllib.request
import urllib.error

from config import DISCORD_TOKEN, LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD

# ─── Rutas ───────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
LAVALINK_DIR = os.path.join(BASE_DIR, 'lavalink')
LAVALINK_JAR = os.path.join(LAVALINK_DIR, 'Lavalink.jar')

# ─── Arranque de Lavalink ─────────────────────────────────────────────────────

def _java_available() -> bool:
    return shutil.which('java') is not None


def _lavalink_ready(timeout: int = 30) -> bool:
    """Espera hasta que el endpoint HTTP de Lavalink responda."""
    url = f'http://{LAVALINK_HOST}:{LAVALINK_PORT}/version'
    headers = {'Authorization': LAVALINK_PASSWORD}
    req = urllib.request.Request(url, headers=headers)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=2):
                return True
        except Exception:
            time.sleep(1)
    return False


def start_lavalink() -> subprocess.Popen | None:
    """
    Lanza el servidor Lavalink como proceso hijo.
    Devuelve el proceso o None si no es posible arrancarlo.
    """
    if not _java_available():
        print('⚠️  Java no encontrado – Lavalink no se iniciará.')
        print('   Instala Java 17+: https://adoptium.net/')
        return None

    if not os.path.exists(LAVALINK_JAR):
        print('⚠️  lavalink/Lavalink.jar no encontrado – Lavalink no se iniciará.')
        print('   Descárgalo de: https://github.com/lavalink-devs/Lavalink/releases')
        return None

    print('🚀 Iniciando servidor Lavalink...')
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


# ─── Arranque del bot ─────────────────────────────────────────────────────────

def main():
    print('=' * 60)
    print('   DISCORD MUSIC BOT  |  Lavalink Mode')
    print('=' * 60)

    if not DISCORD_TOKEN or DISCORD_TOKEN == 'PEGA_TU_TOKEN_AQUI':
        print('❌ Token de Discord no configurado en .env')
        sys.exit(1)

    lavalink_proc = start_lavalink()

    try:
        # Importar bot aquí para que config ya esté cargada
        import discord
        from bot import bot

        print('🤖 Iniciando bot...')
        bot.run(DISCORD_TOKEN)

    except discord.LoginFailure:
        print('❌ Token de Discord inválido')
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
