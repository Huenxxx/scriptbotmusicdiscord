"""
Funciones para buscar música desde diferentes fuentes.
Spotify se resuelve directamente con yt-dlp (sin necesidad de API Premium).
"""
import yt_dlp
import re
from config import YDL_OPTIONS

# Spotify siempre disponible a través de yt-dlp (sin API)
SPOTIFY_AVAILABLE = True

def _build_entry(entry):
    """Convierte una entrada de yt-dlp en el diccionario estándar del bot."""
    return {
        'url': entry.get('url', entry.get('webpage_url', '')),
        'title': entry.get('title', 'Unknown'),
        'duration': entry.get('duration', 0),
        'thumbnail': entry.get('thumbnail', ''),
        'webpage_url': entry.get('webpage_url', ''),
        'view_count': entry.get('view_count', 0),
        'channel': entry.get('channel', entry.get('uploader', '')),
    }

def _try_extract_entry(ydl, entry):
    """
    Intenta obtener la URL de audio de una entrada.
    Si el video no está disponible devuelve None en lugar de lanzar excepción.
    """
    try:
        webpage_url = entry.get('webpage_url') or entry.get('url', '')
        if not webpage_url:
            return None
        info = ydl.extract_info(webpage_url, download=False)
        if info and info.get('url'):
            return {
                'url': info['url'],
                'title': info.get('title', entry.get('title', 'Unknown')),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'webpage_url': info.get('webpage_url', webpage_url),
                'view_count': info.get('view_count', 0),
                'channel': info.get('channel', info.get('uploader', '')),
            }
    except Exception as e:
        print(f'Video no disponible ({entry.get("title", "?")}): {e}')
    return None

def ytdl_search(query, max_results=1):
    """
    Busca en YouTube y devuelve resultados con URL de audio verificada.
    Cuando un video no está disponible prueba automáticamente el siguiente.
    """
    # Opciones para la fase de búsqueda (sólo metadatos, sin verificar disponibilidad)
    search_opts = {
        **YDL_OPTIONS,
        'extract_flat': True,   # Solo metadatos, sin descargar streams
        'quiet': True,
        'no_warnings': True,
    }
    # Opciones para la fase de extracción real de la URL de audio
    extract_opts = {
        **YDL_OPTIONS,
        'extract_flat': False,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # --- URL directa de YouTube ---
        if 'youtube.com' in query or 'youtu.be' in query:
            with yt_dlp.YoutubeDL(extract_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if info and info.get('url'):
                    return {
                        'url': info['url'],
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail', ''),
                        'webpage_url': info.get('webpage_url', query),
                        'view_count': info.get('view_count', 0),
                        'channel': info.get('channel', ''),
                    }
            return None

        # --- Búsqueda por texto ---
        # Pedimos más candidatos de los necesarios para poder saltar los no disponibles
        candidates = max(max_results * 3, 8)
        search_query = f"ytsearch{candidates}:{query}"

        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

        if not info or 'entries' not in info:
            return None if max_results == 1 else []

        entries = [e for e in info['entries'] if e]

        if max_results == 1:
            # Devolver el primer candidato disponible
            with yt_dlp.YoutubeDL(extract_opts) as ydl:
                for entry in entries:
                    result = _try_extract_entry(ydl, entry)
                    if result:
                        return result
            print(f'No se encontró ningún video disponible para: {query}')
            return None
        else:
            # Devolver hasta max_results candidatos disponibles
            results = []
            with yt_dlp.YoutubeDL(extract_opts) as ydl:
                for entry in entries:
                    if len(results) >= max_results:
                        break
                    result = _try_extract_entry(ydl, entry)
                    if result:
                        results.append(result)
            return results

    except Exception as e:
        print(f'Error in ytdl_search: {e}')
        return None if max_results == 1 else []

def is_confident_result(result, query):
    """
    Determine if we're confident this is the right song.
    Returns True if:
    - Very high view count (>10M views)
    - Official artist channel (contains 'VEVO', 'Official', or artist name)
    - Very popular (>50M views)
    - NOT a full album, lyrics video, or playlist
    """
    if not result:
        return False
    
    view_count = result.get('view_count', 0)
    channel = result.get('channel', '').lower()
    title = result.get('title', '').lower()
    duration = result.get('duration', 0)
    query_lower = query.lower()
    
    # Filter out unwanted content
    unwanted_keywords = [
        'full album', 'álbum completo', 'album completo',
        'letra', 'lyrics', 'lyric video',
        'playlist', 'compilation', 'mix',
        'hours', 'horas', 'hour'
    ]
    
    # Check if it's likely a full album or compilation (too long)
    if duration > 600:  # More than 10 minutes is suspicious for a single song
        return False
    
    # Check for unwanted keywords in title
    if any(keyword in title for keyword in unwanted_keywords):
        return False
    
    # Very popular videos (50M+ views) are usually the right one
    if view_count > 50_000_000 and duration < 600:
        return True
    
    # Official channels
    official_indicators = ['vevo', 'official', 'topic']
    if any(indicator in channel for indicator in official_indicators):
        if view_count > 10_000_000 and duration < 600:  # Official + popular = confident
            return True
    
    # Check if artist name is in channel name
    # Extract potential artist name from query (first word or two)
    query_words = query_lower.split()
    if len(query_words) >= 2:
        potential_artist = ' '.join(query_words[:2])
        if potential_artist in channel and view_count > 5_000_000 and duration < 600:
            return True
    
    return False

def is_spotify_url(url):
    """Verifica si es una URL de Spotify"""
    return 'spotify.com' in url

def extract_spotify_id(url):
    """Extrae el ID de una URL de Spotify"""
    patterns = {
        'track': r'track/([a-zA-Z0-9]+)',
        'playlist': r'playlist/([a-zA-Z0-9]+)',
        'album': r'album/([a-zA-Z0-9]+)',
    }
    
    for tipo, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return tipo, match.group(1)
    
    return None, None

def get_spotify_track(spotify_url):
    """
    Resuelve una canción de Spotify usando yt-dlp directamente
    (sin necesidad de API ni suscripción Premium).
    Extrae el título y artista y busca en YouTube.
    """
    try:
        ydl_opts = {
            **YDL_OPTIONS,
            'extract_flat': False,
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(spotify_url, download=False)
            if info:
                artist = ''
                title = info.get('title', '')
                # yt-dlp devuelve 'uploader' como artista en Spotify
                if info.get('uploader'):
                    artist = info['uploader']
                search_query = f"{artist} {title}".strip() if artist else title
                return ytdl_search(search_query)
    except Exception as e:
        print(f'Error al obtener track de Spotify via yt-dlp: {e}')
    return None

def get_spotify_playlist(spotify_url):
    """
    Obtiene todas las canciones de una playlist de Spotify usando yt-dlp
    (sin necesidad de API ni suscripción Premium).
    """
    try:
        ydl_opts = {
            **YDL_OPTIONS,
            'extract_flat': True,
            'noplaylist': False,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(spotify_url, download=False)
            if not info or 'entries' not in info:
                return []
            tracks = []
            for entry in info['entries']:
                if entry:
                    title = entry.get('title', '')
                    artist = entry.get('uploader', entry.get('artist', ''))
                    search_q = f"{artist} {title}".strip() if artist else title
                    tracks.append({
                        'artist': artist,
                        'title': title,
                        'search_query': search_q
                    })
            return tracks
    except Exception as e:
        print(f'Error al obtener playlist de Spotify via yt-dlp: {e}')
        return []

def get_spotify_album(spotify_url):
    """
    Obtiene todas las canciones de un álbum de Spotify usando yt-dlp
    (sin necesidad de API ni suscripción Premium).
    """
    return get_spotify_playlist(spotify_url)  # Mismo mecanismo para álbumes

def search_spotify_track(query):
    """Ya no se usa Spotify API para búsqueda. Devuelve None para forzar búsqueda en YouTube."""
    return None

async def search_song(query):
    """Busca una canción desde cualquier fuente"""
    # Si es URL de Spotify, resolverla via yt-dlp
    if is_spotify_url(query):
        tipo, spotify_id = extract_spotify_id(query)
        if tipo == 'track':
            return get_spotify_track(query), None
        elif tipo == 'playlist':
            return None, 'playlist'
        elif tipo == 'album':
            return None, 'album'

    # Buscar directamente en YouTube
    return ytdl_search(query), None
