"""
Utilidades para detectar y parsear URLs de Spotify.
La búsqueda y reproducción de audio se gestiona via Lavalink (lavalink_manager.py).
"""

import re


def is_spotify_url(url: str) -> bool:
    """Devuelve True si la URL es de Spotify."""
    return 'spotify.com' in url


def extract_spotify_id(url: str) -> tuple[str | None, str | None]:
    """Extrae el tipo (track/playlist/album) e ID de una URL de Spotify."""
    patterns = {
        'track':    r'track/([a-zA-Z0-9]+)',
        'playlist': r'playlist/([a-zA-Z0-9]+)',
        'album':    r'album/([a-zA-Z0-9]+)',
    }
    for tipo, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return tipo, match.group(1)
    return None, None
