# Project Structure

Overview of the Discord Music Bot project organization.

## Directory Tree

```
discord-music-bot/
│
├── 📄 Core Files
│   ├── bot.py                  # Main bot application
│   ├── config.py               # Configuration and settings
│   ├── music_player.py         # Music playback logic
│   ├── music_sources.py        # YouTube/Spotify integration
│   └── playlist_manager.py     # Playlist management
│
├── 📝 Configuration
│   ├── .env                    # Environment variables (create this)
│   ├── .env.example            # Example configuration
│   ├── requirements.txt        # Python dependencies
│   └── .gitignore             # Git ignore rules
│
├── 🛠️ Utilities
│   ├── install_ffmpeg.py       # FFmpeg installer script
│   ├── start_bot.bat           # Windows startup script
│   └── ffmpeg.exe              # FFmpeg binary (after install)
│
├── 📚 Documentation
│   ├── README.md               # Main documentation
│   ├── CHANGELOG.md            # Version history
│   ├── LICENSE                 # MIT License
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   ├── PROJECT_STRUCTURE.md    # This file
│   └── docs/
│       ├── SETUP.md            # Setup guide
│       ├── COMMANDS.md         # Command reference
│       ├── EXAMPLES.md         # Usage examples
│       └── FAQ.md              # Frequently asked questions
│
└── 💾 Data
    └── playlists/              # Saved playlists (JSON files)
```

## File Descriptions

### Core Application Files

#### `bot.py`
Main bot application containing:
- Discord bot initialization
- All command definitions
- Event handlers
- Command logic

**Key Components:**
- Playback commands (!play, !skip, etc.)
- Queue management commands
- Playlist commands
- Help command

#### `config.py`
Configuration module containing:
- Environment variable loading
- FFmpeg detection
- Configuration constants
- yt-dlp options
- FFmpeg options

#### `music_player.py`
Music player class managing:
- Queue system
- Playback control
- Loop modes
- Song transitions

**Key Features:**
- Automatic queue progression
- Loop modes (song/queue)
- Queue manipulation
- Error handling

#### `music_sources.py`
Music source integration:
- YouTube search and extraction
- Spotify API integration
- URL parsing
- Track information retrieval

**Supported Sources:**
- YouTube (direct URLs)
- YouTube (search)
- Spotify (tracks)
- Spotify (playlists)
- Spotify (albums)

#### `playlist_manager.py`
Playlist management system:
- Save playlists to JSON
- Load playlists from JSON
- List available playlists
- Delete playlists

**Features:**
- JSON format for easy sharing
- Persistent storage
- Simple file-based system

### Configuration Files

#### `.env`
Environment variables (not in Git):
```env
DISCORD_TOKEN=your_token
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

#### `.env.example`
Template for `.env` file

#### `requirements.txt`
Python package dependencies:
- discord.py[voice]
- yt-dlp
- PyNaCl
- python-dotenv
- spotipy

#### `.gitignore`
Specifies files to ignore in Git:
- Python cache files
- Virtual environments
- .env file
- FFmpeg binary
- IDE files

### Utility Files

#### `install_ffmpeg.py`
Automated FFmpeg installer for Windows:
- Downloads FFmpeg
- Extracts files
- Places in project directory
- Cleans up temporary files

#### `start_bot.bat`
Windows batch script to start the bot quickly

### Documentation Files

#### `README.md`
Main project documentation:
- Project overview
- Features list
- Quick start guide
- Installation instructions
- Usage examples
- Configuration guide

#### `CHANGELOG.md`
Version history and changes:
- New features
- Bug fixes
- Breaking changes
- Migration guides

#### `LICENSE`
MIT License terms

#### `CONTRIBUTING.md`
Guidelines for contributors:
- How to report bugs
- How to suggest features
- Pull request process
- Coding standards

#### `docs/SETUP.md`
Detailed setup instructions:
- Prerequisites
- Step-by-step installation
- Configuration
- Troubleshooting

#### `docs/COMMANDS.md`
Complete command reference:
- All available commands
- Usage syntax
- Examples
- Aliases

#### `docs/EXAMPLES.md`
Real-world usage examples:
- Common scenarios
- Workflow examples
- Tips and tricks

#### `docs/FAQ.md`
Frequently asked questions:
- Common issues
- Feature questions
- Technical questions

### Data Directories

#### `playlists/`
Stores saved playlists as JSON files:
```json
{
  "name": "playlist_name",
  "songs": [
    {
      "title": "Song Title",
      "url": "audio_url",
      "search_query": "search query"
    }
  ]
}
```

## Module Dependencies

```
bot.py
├── config.py
├── music_player.py
├── music_sources.py
└── playlist_manager.py

config.py
├── os
├── shutil
└── dotenv

music_player.py
├── discord
├── asyncio
└── config

music_sources.py
├── yt_dlp
├── re
├── spotipy (optional)
└── config

playlist_manager.py
├── json
├── os
└── config
```

## Data Flow

```
User Command
    ↓
bot.py (command handler)
    ↓
music_sources.py (search/extract)
    ↓
music_player.py (queue/play)
    ↓
FFmpeg (audio processing)
    ↓
Discord Voice Channel
```

## Configuration Flow

```
.env file
    ↓
config.py (load and parse)
    ↓
bot.py (use configuration)
    ↓
Other modules (import from config)
```

## Playlist Flow

```
User: !playlist_save
    ↓
bot.py (command)
    ↓
playlist_manager.py (save to JSON)
    ↓
playlists/name.json

User: !playlist_load
    ↓
bot.py (command)
    ↓
playlist_manager.py (load from JSON)
    ↓
music_sources.py (search songs)
    ↓
music_player.py (add to queue)
```

## Extension Points

### Adding New Commands
Edit `bot.py` and add command functions

### Adding New Music Sources
Edit `music_sources.py` and add source logic

### Changing Configuration
Edit `config.py` for global settings

### Modifying Playback
Edit `music_player.py` for queue/playback logic

### Changing Playlist Format
Edit `playlist_manager.py` for storage logic

## Best Practices

### Code Organization
- Keep related code in appropriate modules
- Don't mix concerns
- Use clear function names
- Add docstrings

### Configuration
- Use environment variables for secrets
- Keep configuration centralized
- Don't hardcode values

### Error Handling
- Catch and handle exceptions
- Provide user-friendly messages
- Log errors for debugging

### Documentation
- Update docs when changing features
- Add examples for new commands
- Keep README up to date

## Development Workflow

1. Edit code in appropriate module
2. Test locally
3. Update documentation
4. Commit changes
5. Push to repository

## Deployment

1. Clone repository
2. Install dependencies
3. Configure `.env`
4. Install FFmpeg
5. Run `python bot.py`

---

This structure keeps the project organized, maintainable, and easy to extend.
