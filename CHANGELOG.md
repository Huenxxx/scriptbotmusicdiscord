# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024-11-11

### Added
- **Spotify Integration**
  - Play individual tracks from Spotify
  - Load complete playlists from Spotify
  - Load complete albums from Spotify
  - Automatic YouTube search for Spotify tracks

- **Playlist Management System**
  - Save current queue as playlist
  - Load saved playlists
  - List all playlists
  - Delete playlists
  - JSON format for easy sharing

- **Advanced Queue Management**
  - Shuffle queue randomly
  - Remove specific songs
  - Clear queue without stopping playback
  - Loop modes (song/queue/off)

- **Modular Architecture**
  - Separated code into logical modules
  - Centralized configuration
  - Better code organization
  - Easier to maintain and extend

### Changed
- Improved error handling
- Better async search implementation
- Enhanced user feedback messages
- Optimized playback system

### New Commands
- `!shuffle` / `!mix` - Shuffle queue
- `!remove <n>` / `!rm <n>` - Remove song
- `!clear` - Clear queue
- `!loop [mode]` - Loop mode (song/queue/off)
- `!playlist_save <name>` - Save playlist
- `!playlist_load <name>` - Load playlist
- `!playlist_list` - List playlists
- `!playlist_delete <name>` - Delete playlist
- `!help_music` - Complete help

## [1.0.0] - 2024-11-10

### Added
- Basic YouTube playback
- Queue system
- Basic commands (play, skip, pause, resume, stop)
- Multi-server support
- Automatic FFmpeg installer

### Commands
- `!play` - Play music
- `!skip` - Skip song
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop playback
- `!queue` - Show queue
- `!leave` - Disconnect bot
