"""
Gestor de playlists guardadas
"""
import json
import os
from config import PLAYLISTS_FOLDER

class PlaylistManager:
    @staticmethod
    def save_playlist(name, songs):
        """Guarda una playlist"""
        filepath = os.path.join(PLAYLISTS_FOLDER, f"{name}.json")
        
        playlist_data = {
            'name': name,
            'songs': [
                {
                    'title': song['title'],
                    'url': song.get('url', ''),
                    'search_query': song.get('search_query', song['title'])
                }
                for song in songs
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, indent=2, ensure_ascii=False)
        
        return True

    @staticmethod
    def load_playlist(name):
        """Carga una playlist"""
        filepath = os.path.join(PLAYLISTS_FOLDER, f"{name}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def list_playlists():
        """Lista todas las playlists guardadas"""
        if not os.path.exists(PLAYLISTS_FOLDER):
            return []
        
        playlists = []
        for filename in os.listdir(PLAYLISTS_FOLDER):
            if filename.endswith('.json'):
                name = filename[:-5]  # Quitar .json
                filepath = os.path.join(PLAYLISTS_FOLDER, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    playlists.append({
                        'name': name,
                        'song_count': len(data.get('songs', []))
                    })
        
        return playlists

    @staticmethod
    def delete_playlist(name):
        """Elimina una playlist"""
        filepath = os.path.join(PLAYLISTS_FOLDER, f"{name}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
