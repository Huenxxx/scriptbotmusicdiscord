"""
Funciones para buscar música desde diferentes fuentes
"""
import yt_dlp
import re
from config import YDL_OPTIONS, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Intentar importar spotipy
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
    
    if SPOTIFY_AVAILABLE:
        spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
except ImportError:
    SPOTIFY_AVAILABLE = False
    print('⚠️ Spotipy no instalado. Instala con: pip install spotipy')

def ytdl_search(query):
    """Busca y extrae información de YouTube"""
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            if 'youtube.com' in query or 'youtu.be' in query:
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
            
            return {
                'url': info['url'],
                'title': info['title'],
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
        except Exception as e:
            print(f'Error en ytdl_search: {e}')
            return None

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

def get_spotify_track(track_id):
    """Obtiene información de una canción de Spotify"""
    if not SPOTIFY_AVAILABLE:
        return None
    
    try:
        track = spotify.track(track_id)
        artist = track['artists'][0]['name']
        title = track['name']
        search_query = f"{artist} {title}"
        
        # Buscar en YouTube
        return ytdl_search(search_query)
    except Exception as e:
        print(f'Error al obtener track de Spotify: {e}')
        return None

def get_spotify_playlist(playlist_id):
    """Obtiene todas las canciones de una playlist de Spotify"""
    if not SPOTIFY_AVAILABLE:
        return []
    
    try:
        results = spotify.playlist_tracks(playlist_id)
        tracks = []
        
        for item in results['items']:
            track = item['track']
            if track:
                artist = track['artists'][0]['name']
                title = track['name']
                tracks.append({
                    'artist': artist,
                    'title': title,
                    'search_query': f"{artist} {title}"
                })
        
        return tracks
    except Exception as e:
        print(f'Error al obtener playlist de Spotify: {e}')
        return []

def get_spotify_album(album_id):
    """Obtiene todas las canciones de un álbum de Spotify"""
    if not SPOTIFY_AVAILABLE:
        return []
    
    try:
        results = spotify.album_tracks(album_id)
        album_info = spotify.album(album_id)
        artist = album_info['artists'][0]['name']
        tracks = []
        
        for track in results['items']:
            title = track['name']
            tracks.append({
                'artist': artist,
                'title': title,
                'search_query': f"{artist} {title}"
            })
        
        return tracks
    except Exception as e:
        print(f'Error al obtener álbum de Spotify: {e}')
        return []

async def search_song(query):
    """Busca una canción desde cualquier fuente"""
    # Si es URL de Spotify
    if is_spotify_url(query):
        if not SPOTIFY_AVAILABLE:
            return None, 'Spotify no está configurado. Configura SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET'
        
        tipo, spotify_id = extract_spotify_id(query)
        
        if tipo == 'track':
            return get_spotify_track(spotify_id), None
        elif tipo == 'playlist':
            return None, 'playlist'
        elif tipo == 'album':
            return None, 'album'
    
    # Buscar en YouTube
    return ytdl_search(query), None
