# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2024-11-11

### Added
- **Smart Search System:** Intelligent search that adapts to confidence level
  - **High confidence:** Plays immediately (official channels, 50M+ views)
  - **Low confidence:** Shows 5 options with views and channel info
  - Choose the exact song you want with `!select <number>`
  - See duration, views, and channel for each result
  - Auto-selects first result after 30 seconds
- New command: `!select` (aliases: `!choose`, `!pick`)

### Intelligence Features
- **Spotify Priority:** If Spotify is configured, searches there first for better accuracy
- Recognizes official artist channels (VEVO, Official, Topic)
- Considers view count (50M+ = auto-play, 10M+ on official = auto-play)
- Matches artist name in channel name
- **Filters out:** Full albums, lyrics videos, compilations (>10 min duration)
- Only shows options when truly ambiguous

### Improved
- **Fast Spotify Loading:** Albums and playlists now start playing immediately
  - First song loads and plays right away
  - Remaining songs load in background
  - No more waiting for entire album/playlist to load
- Better search accuracy with multiple options
- All bot messages now in English

### Fixed
- Reduced loading time for Spotify albums from ~1 minute to instant playback

### Changed
- Simplified project structure (removed redundant documentation files)

---

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
