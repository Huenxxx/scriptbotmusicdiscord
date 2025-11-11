# Setup Guide

Complete guide to set up the Discord Music Bot.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Discord account
- (Optional) Spotify account for Spotify features

## Step-by-Step Installation

### 1. Install Python

Download and install Python from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### 2. Clone or Download the Project

```bash
git clone https://github.com/yourusername/discord-music-bot.git
cd discord-music-bot
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- discord.py - Discord API
- yt-dlp - YouTube downloader
- PyNaCl - Voice encoding
- python-dotenv - Environment variables
- spotipy - Spotify API (optional)

### 4. Install FFmpeg

#### Option A: Automatic (Windows)
```bash
python install_ffmpeg.py
```

#### Option B: Manual Installation

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the archive
3. Add the `bin` folder to your system PATH

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 5. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name
4. Go to "Bot" section
5. Click "Add Bot"
6. Copy the token (keep it secret!)

### 6. Enable Bot Intents

In the Bot section, enable:
- ✅ MESSAGE CONTENT INTENT
- ✅ SERVER MEMBERS INTENT

### 7. Invite Bot to Server

1. Go to OAuth2 > URL Generator
2. Select scopes:
   - ✅ bot
3. Select permissions:
   - ✅ Send Messages
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
4. Copy the generated URL
5. Open it in your browser
6. Select your server
7. Authorize

### 8. Configure Environment Variables

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_token_here

# Optional: Spotify credentials
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

**Important:** Never share your `.env` file or commit it to Git!

### 9. (Optional) Configure Spotify

If you want Spotify support:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the details
5. Copy the Client ID and Client Secret
6. Add them to your `.env` file

### 10. Run the Bot

```bash
python bot.py
```

You should see:
```
✅ FFmpeg found at: ...
🤖 Starting bot...
📡 Connecting to Discord...
✅ Bot connected as YourBotName
```

### 11. Test the Bot

1. Join a voice channel in your Discord server
2. Type: `!play never gonna give you up`
3. Enjoy! 🎵

## Troubleshooting

### Bot doesn't start

**Error: "Token invalid"**
- Check your token in `.env`
- Make sure there are no extra spaces
- Regenerate token if needed

**Error: "FFmpeg not found"**
- Run `python install_ffmpeg.py`
- Or install FFmpeg manually
- Make sure it's in your system PATH

### Bot doesn't respond to commands

**Check intents:**
- Go to Discord Developer Portal
- Bot section
- Enable MESSAGE CONTENT INTENT
- Restart the bot

**Check permissions:**
- Make sure bot has "Send Messages" permission
- Check bot role is above other roles

### Music doesn't play

**Check voice permissions:**
- Bot needs "Connect" and "Speak" permissions
- Make sure you're in a voice channel
- Try rejoining the voice channel

**Check FFmpeg:**
```bash
ffmpeg -version
```

### Spotify doesn't work

**This is optional!** The bot works perfectly with YouTube only.

If you want Spotify:
- Verify credentials in `.env`
- Make sure spotipy is installed: `pip install spotipy`
- Check your Spotify app is active in the dashboard

## Next Steps

- Read [COMMANDS.md](COMMANDS.md) for all available commands
- Check [EXAMPLES.md](EXAMPLES.md) for usage examples
- See [FAQ.md](FAQ.md) for common questions

## Need Help?

- Check the [FAQ](FAQ.md)
- Open an issue on GitHub
- Read the troubleshooting section above
