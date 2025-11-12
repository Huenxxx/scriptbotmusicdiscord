"""
Local music file management
"""
import os
from pathlib import Path

# Folder for local music files
LOCAL_MUSIC_FOLDER = 'own_songs'

# Supported audio formats
SUPPORTED_FORMATS = [
    '.mp3', '.wav', '.ogg', '.flac', '.m4a', 
    '.aac', '.wma', '.opus', '.mpeg', '.mpga',
    '.mp4', '.webm'
]

def get_local_songs():
    """Get all local music files"""
    if not os.path.exists(LOCAL_MUSIC_FOLDER):
        os.makedirs(LOCAL_MUSIC_FOLDER)
        return []
    
    songs = []
    for file in os.listdir(LOCAL_MUSIC_FOLDER):
        file_path = os.path.join(LOCAL_MUSIC_FOLDER, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_FORMATS:
                songs.append({
                    'filename': file,
                    'path': os.path.abspath(file_path),
                    'name': os.path.splitext(file)[0],
                    'format': ext[1:]  # Remove the dot
                })
    
    return sorted(songs, key=lambda x: x['name'].lower())

def search_local_songs(query):
    """Search for local songs by name"""
    all_songs = get_local_songs()
    query_lower = query.lower()
    
    # Exact matches first
    exact_matches = [s for s in all_songs if query_lower == s['name'].lower()]
    if exact_matches:
        return exact_matches
    
    # Partial matches
    partial_matches = [s for s in all_songs if query_lower in s['name'].lower()]
    if partial_matches:
        return partial_matches
    
    return []

def get_song_by_index(index):
    """Get a song by its index in the list"""
    songs = get_local_songs()
    if 0 <= index < len(songs):
        return songs[index]
    return None

def format_song_list(songs, max_display=10):
    """Format song list for display"""
    if not songs:
        return "No local songs found"
    
    message = f"🎵 **Local Songs** ({len(songs)} total):\n\n"
    
    for i, song in enumerate(songs[:max_display], 1):
        message += f"**{i}.** {song['name']} `.{song['format']}`\n"
    
    if len(songs) > max_display:
        message += f"\n... and {len(songs) - max_display} more"
    
    return message
