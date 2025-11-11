# Quick Start Guide

Get your Discord Music Bot running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Discord account
- 5 minutes of your time

## Step 1: Download

```bash
git clone https://github.com/YOUR_USERNAME/discord-music-bot.git
cd discord-music-bot
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Install FFmpeg

```bash
python install_ffmpeg.py
```

Type `y` when prompted.

## Step 4: Get Discord Token

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" → "Add Bot"
4. Copy the token
5. Enable these intents:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT

## Step 5: Configure Bot

Edit `.env` file:
```env
DISCORD_TOKEN=paste_your_token_here
```

## Step 6: Invite Bot

1. In Discord Developer Portal: OAuth2 → URL Generator
2. Select: `bot`
3. Select permissions: `Send Messages`, `Connect`, `Speak`
4. Copy URL and open in browser
5. Select your server

## Step 7: Run Bot

```bash
python bot.py
```

You should see:
```
✅ Bot connected as YourBotName
```

## Step 8: Test

1. Join a voice channel
2. Type: `!play never gonna give you up`
3. Enjoy! 🎵

## Common Commands

```
!play <song>        Play music
!skip               Skip song
!queue              Show queue
!pause              Pause
!resume             Resume
!stop               Stop
!leave              Disconnect
```

## Need Help?

- Full setup: [docs/SETUP.md](docs/SETUP.md)
- All commands: [docs/COMMANDS.md](docs/COMMANDS.md)
- Examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- FAQ: [docs/FAQ.md](docs/FAQ.md)

## Optional: Spotify

Want Spotify support?

1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Copy Client ID and Secret
4. Add to `.env`:
```env
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

Then you can use:
```
!play https://open.spotify.com/track/...
!play https://open.spotify.com/playlist/...
```

## Troubleshooting

**Bot doesn't respond?**
- Check MESSAGE CONTENT INTENT is enabled
- Verify bot has permissions

**No music?**
- Make sure FFmpeg installed: `ffmpeg -version`
- Check you're in a voice channel

**Still stuck?**
- Read [docs/FAQ.md](docs/FAQ.md)
- Open an issue on GitHub

---

That's it! You're ready to rock! 🎸
