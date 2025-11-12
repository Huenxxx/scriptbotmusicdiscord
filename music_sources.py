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

def ytdl_search(query, max_results=1):
    """Search and extract information from YouTube"""
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            if 'youtube.com' in query or 'youtu.be' in query:
                info = ydl.extract_info(query, download=False)
                return {
                    'url': info['url'],
                    'title': info['title'],
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'view_count': info.get('view_count', 0),
                    'channel': info.get('channel', ''),
                }
            else:
                # Search with multiple results
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if max_results == 1:
                    # Return single result
                    if 'entries' in info and info['entries']:
                        entry = info['entries'][0]
                        return {
                            'url': entry['url'],
                            'title': entry['title'],
                            'duration': entry.get('duration', 0),
                            'thumbnail': entry.get('thumbnail', ''),
                            'view_count': entry.get('view_count', 0),
                            'channel': entry.get('channel', ''),
                        }
                else:
                    # Return multiple results
                    results = []
                    if 'entries' in info:
                        for entry in info['entries'][:max_results]:
                            if entry:
                                results.append({
                                    'url': entry['url'],
                                    'title': entry['title'],
                                    'duration': entry.get('duration', 0),
                                    'thumbnail': entry.get('thumbnail', ''),
                                    'webpage_url': entry.get('webpage_url', ''),
                                    'view_count': entry.get('view_count', 0),
                                    'channel': entry.get('channel', ''),
                                })
                    return results
            
            return None
        except Exception as e:
            print(f'Error in ytdl_search: {e}')
            return None

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
    """Get all songs from a Spotify album"""
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
        print(f'Error getting Spotify album: {e}')
        return []

def search_spotify_track(query):
    """Search for a track on Spotify and return formatted search query"""
    if not SPOTIFY_AVAILABLE:
        return None
    
    try:
        results = spotify.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            artist = track['artists'][0]['name']
            title = track['name']
            # Return formatted query: "Artist - Title" for better YouTube search
            return f"{artist} {title} official audio"
        return None
    except Exception as e:
        print(f'Error searching Spotify: {e}')
        return None

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
