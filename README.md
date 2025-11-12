# 🎵 Discord Music Bot

A feature-rich Discord music bot with support for YouTube, Spotify, and playlist management. Built with Python and discord.py.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎵 **YouTube Support** - Play music from YouTube (URLs and search)
- 🧠 **Smart Search** - Intelligent search that plays popular songs instantly, shows options when ambiguous
- 🎧 **Spotify Integration** - Play tracks, playlists, and albums from Spotify
- 📁 **Local Music** - Play your own audio files from `own_songs` folder (all formats supported)
- ⚡ **Instant Playback** - Albums/playlists start playing immediately
- 💾 **Playlist Management** - Save and load custom playlists
- 🔀 **Advanced Queue** - Shuffle, remove songs, and loop modes
- 🎮 **Easy Controls** - Intuitive commands for playback control
- 🏗️ **Modular Code** - Clean, organized, and easy to extend

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Discord Bot Token
- (Optional) Spotify API credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/discord-music-bot.git
cd discord-music-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg**
```bash
python install_ffmpeg.py
```
Or install manually from [ffmpeg.org](https://ffmpeg.org/download.html)

4. **Configure your bot**

Edit `.env` file:
```env
DISCORD_TOKEN=your_discord_token_here

# Optional: For Spotify support
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

5. **Run the bot**
```bash
python bot.py
```

## 🎮 Commands

### Playback
- `!play <song/url>` - Play music from YouTube or Spotify
- `!skip` or `!s` - Skip current song
- `!pause` - Pause playback
- `!resume` or `!r` - Resume playback
- `!stop` - Stop and clear queue
- `!leave` or `!dc` - Disconnect from voice channel

### Queue Management
- `!queue` or `!q` - Show current queue
- `!shuffle` or `!mix` - Shuffle the queue
- `!remove <number>` - Remove specific song from queue
- `!clear` - Clear the entire queue
- `!loop [song/queue/off]` - Toggle loop mode

### Playlists
- `!playlist_save <name>` - Save current queue as playlist
- `!playlist_load <name>` - Load a saved playlist
- `!playlist_list` - List all saved playlists
- `!playlist_delete <name>` - Delete a playlist

### Help
- `!help_music` - Show all available commands

## 📝 Usage Examples

### Smart Search
```
# Popular songs play instantly
!play despacito
# Plays immediately (5B views)

# Ambiguous searches show options
!play believer
# Shows Imagine Dragons, Ozzy Osbourne, etc.
!select 1
# Plays your choice
```

### Play from YouTube
```
!play never gonna give you up
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Play from Spotify
```
!play https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
!play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

### Play Local Files
```
# Add files to own_songs/ folder
!ownplay              # List all local songs
!ownplay my_song      # Play by name
!ownplay 1            # Play by number
```

### Create and Use Playlists
```
!play song 1
!play song 2
!play song 3
!playlist_save my_favorites
!playlist_load my_favorites
!shuffle
!loop queue
```

## 🔧 Configuration

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token
5. Enable these intents:
   - MESSAGE CONTENT INTENT ✅
   - SERVER MEMBERS INTENT ✅
6. Invite bot to your server:
   - OAuth2 > URL Generator
   - Scopes: `bot`
   - Permissions: `Connect`, `Speak`, `Send Messages`, `Use Voice Activity`

### Spotify Setup (Optional)

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Copy Client ID and Client Secret
4. Add them to `.env` file

**Note:** The bot works perfectly with YouTube only. Spotify is optional.

## 📁 Project Structure

```
discord-music-bot/
├── 🤖 Core Files
│   ├── bot.py                  # Main bot application
│   ├── config.py               # Configuration
│   ├── music_player.py         # Playback logic
│   ├── music_sources.py        # YouTube/Spotify integration
│   └── playlist_manager.py     # Playlist management
│
├── 📚 Documentation
│   ├── README.md               # This file
│   ├── CHANGELOG.md            # Version history
│   ├── CONTRIBUTING.md         # Contribution guide
│   └── docs/                   # Detailed guides
│       ├── SETUP.md
│       ├── COMMANDS.md
│       ├── EXAMPLES.md
│       └── FAQ.md
│
├── ⚙️ Configuration
│   ├── .env                    # Your tokens (create this)
│   ├── .env.example            # Template
│   ├── requirements.txt        # Dependencies
│   └── .gitignore             # Git ignore rules
│
└── 🛠️ Utilities
    ├── install_ffmpeg.py       # FFmpeg installer
    ├── start_bot.bat           # Quick start (Windows)
    └── playlists/              # Saved playlists
```

## 🛠️ Technologies

- **discord.py** - Discord API wrapper
- **yt-dlp** - YouTube audio extraction
- **spotipy** - Spotify API wrapper
- **FFmpeg** - Audio processing
- **PyNaCl** - Voice encoding

## 🐛 Troubleshooting

### Bot doesn't respond
- Verify MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- Check bot has proper permissions in your server

### FFmpeg not found
- Run `python install_ffmpeg.py`
- Or install manually and add to system PATH

### Spotify not working
- Verify credentials in `.env`
- Install spotipy: `pip install spotipy`
- Spotify is optional, YouTube always works

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [spotipy](https://github.com/plamere/spotipy)

## 📞 Support

If you need help:
1. Check the [documentation](docs/)
2. Open an issue on GitHub
3. Read the troubleshooting section

---

Made with ❤️ for Discord music lovers
