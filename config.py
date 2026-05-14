"""
Configuración del bot
"""
import os
import shutil
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Token de Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Credenciales de Spotify (opcional)
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')

# ── Lavalink ────────────────────────────────────────────────────────────────
# True  → main.py arranca el Lavalink.jar local (solo en tu PC)
# False → conecta a servidor externo (cloud/Render/hosting) ← DEFAULT
LAVALINK_LOCAL    = os.getenv('LAVALINK_LOCAL', 'false').lower() == 'true'

_PUBLIC_HOST      = 'lavalink.darrennathanael.com'
_PUBLIC_PORT      = 80
_PUBLIC_PASSWORD  = 'youshallnotpass'

# Si no estamos en modo local y no se configuró un host externo → nodo público
_raw_host = os.getenv('LAVALINK_HOST', '')
if LAVALINK_LOCAL:
    LAVALINK_HOST     = _raw_host or 'localhost'
    LAVALINK_PORT     = int(os.getenv('LAVALINK_PORT', '2333'))
    LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')
else:
    LAVALINK_HOST     = _raw_host if _raw_host and _raw_host not in ('localhost', '127.0.0.1') else _PUBLIC_HOST
    LAVALINK_PORT     = int(os.getenv('LAVALINK_PORT', str(_PUBLIC_PORT)))
    LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', _PUBLIC_PASSWORD)

# Seguridad SSL: auto-detectar si el puerto es 443 o el host es de cloud (Railway, etc.)
_secure_env = os.getenv('LAVALINK_SECURE', '')
if _secure_env:
    LAVALINK_SECURE = _secure_env.lower() == 'true'
else:
    _cloud_domains = ('railway.app', 'render.com', 'herokuapp.com', 'fly.dev', 'up.railway.app')
    LAVALINK_SECURE = LAVALINK_PORT == 443 or any(LAVALINK_HOST.endswith(d) for d in _cloud_domains)


# Prefijo de comandos
COMMAND_PREFIX = '!'

# Carpeta para guardar playlists
PLAYLISTS_FOLDER = 'playlists'

# Crear carpeta de playlists si no existe
if not os.path.exists(PLAYLISTS_FOLDER):
    os.makedirs(PLAYLISTS_FOLDER)

# Buscar FFmpeg
def find_ffmpeg():
    """Busca FFmpeg en el sistema"""
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    common_paths = [
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
        os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(os.getcwd(), 'ffmpeg.exe'),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

FFMPEG_PATH = find_ffmpeg()

# Opciones para yt-dlp
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extract_flat': False,
    'noplaylist': True,
}

# Opciones para FFmpeg
FFMPEG_BEFORE = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin'

if FFMPEG_PATH:
    FFMPEG_OPTIONS = {
        'before_options': FFMPEG_BEFORE,
        'options': '-vn -bufsize 64k',
        'executable': FFMPEG_PATH
    }
else:
    FFMPEG_OPTIONS = {
        'before_options': FFMPEG_BEFORE,
        'options': '-vn -bufsize 64k'
    }
