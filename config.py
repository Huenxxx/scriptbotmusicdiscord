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
LAVALINK_HOST     = os.getenv('LAVALINK_HOST', 'localhost')
LAVALINK_PORT     = int(os.getenv('LAVALINK_PORT', '2333'))
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')

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
