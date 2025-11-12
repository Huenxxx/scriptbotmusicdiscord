# Frequently Asked Questions (FAQ)

## General Questions

### What is this bot?
A Discord music bot that plays music from YouTube and Spotify in voice channels. It includes features like queue management, playlists, and loop modes.

### Is it free?
Yes! This is an open-source project under the MIT license.

### Do I need coding knowledge?
No, just follow the setup guide. Basic command-line knowledge is helpful.

### Can I use this on multiple servers?
Yes! Once invited, the bot works on all servers it's in.

---

## Setup Questions

### How do I get a Discord bot token?
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Click "Add Bot"
5. Copy the token

### Do I need Spotify?
No! Spotify is completely optional. The bot works perfectly with YouTube only.

### How do I install FFmpeg?
Run `python install_ffmpeg.py` or install manually from [ffmpeg.org](https://ffmpeg.org/download.html)

### Where do I put my token?
In the `.env` file in the project root. Never share this file!

### What Python version do I need?
Python 3.8 or higher.

---

## Usage Questions

### How do I play music?
Join a voice channel and type `!play song name` or `!play youtube_url`

### Can I play Spotify playlists?
Yes! Use `!play spotify_playlist_url` (requires Spotify configuration). The first song starts playing immediately while the rest load in the background.

### How do I save playlists?
Use `!playlist_save name` to save the current queue.

### Can I shuffle the queue?
Yes! Use `!shuffle` command.

### How do I loop songs?
Use `!loop song` for current song or `!loop queue` for entire queue.

### Can multiple people add songs?
Yes! Anyone with permissions can use the bot commands.

---

## Technical Questions

### Why isn't the bot responding?
- Check MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- Verify bot has "Send Messages" permission
- Make sure bot is online

### Why can't I hear music?
- Check bot has "Connect" and "Speak" permissions
- Verify you're in a voice channel
- Make sure FFmpeg is installed
- Check your Discord voice settings

### Why is Spotify not working?
- Spotify is optional and requires API credentials
- Check credentials in `.env` file
- Verify spotipy is installed: `pip install spotipy`
- YouTube always works as fallback

### Can I change the command prefix?
Yes! Edit `COMMAND_PREFIX` in `config.py`

### How do I update the bot?
```bash
git pull
pip install -r requirements.txt --upgrade
```

### Where are playlists stored?
In the `playlists/` folder as JSON files.

---

## Error Messages

### "Token invalid"
- Check your token in `.env`
- Make sure there are no spaces
- Regenerate token if needed

### "FFmpeg not found"
- Run `python install_ffmpeg.py`
- Or install FFmpeg manually
- Add FFmpeg to system PATH

### "No module named 'discord'"
```bash
pip install discord.py
```

### "No module named 'yt_dlp'"
```bash
pip install yt-dlp
```

### "Could not find opus"
```bash
pip install PyNaCl
```

### "Song not found"
- Try being more specific in your search
- Use direct YouTube URLs
- Check your internet connection

---

## Feature Questions

### Can I control volume?
Not currently implemented. This is a planned feature.

### Can I see song lyrics?
Not currently implemented. This is a planned feature.

### Can I use SoundCloud?
Not currently. Only YouTube and Spotify are supported.

### Can I download songs?
No, the bot streams music without downloading.

### Is there a web dashboard?
No, all control is through Discord commands.

### Can I set up auto-play?
Use `!loop queue` for continuous playback.

---

## Playlist Questions

### How many songs can a playlist have?
No limit! But Spotify playlists are capped at 50 songs per load.

### Can I share playlists?
Yes! Playlist files are in `playlists/` folder as JSON. Share the file.

### Can I edit playlists?
Yes! Edit the JSON file directly or use bot commands.

### Where are playlists saved?
In the `playlists/` folder in the project directory.

---

## Performance Questions

### How many servers can it handle?
Depends on your hosting. For personal use, dozens of servers is fine.

### Does it use a lot of bandwidth?
Yes, streaming music uses bandwidth. Consider your internet plan.

### Can I host it 24/7?
Yes! Use a VPS or cloud service for 24/7 hosting.

### What are the system requirements?
- Python 3.8+
- ~100MB RAM
- Stable internet connection
- FFmpeg installed

---

## Hosting Questions

### Can I host on Heroku?
Yes, but you'll need to configure buildpacks for FFmpeg.

### Can I host on Replit?
Yes, but keep-alive services are needed for 24/7 uptime.

### Can I host on my computer?
Yes! Just keep the script running.

### What's the best hosting option?
- Personal use: Your computer
- 24/7: VPS (DigitalOcean, AWS, etc.)
- Free: Replit with keep-alive

---

## Customization Questions

### Can I change the bot's name?
Yes, in Discord Developer Portal under your application.

### Can I change the command prefix?
Yes, edit `COMMAND_PREFIX` in `config.py`

### Can I add custom commands?
Yes! Edit `bot.py` and add new command functions.

### Can I change the bot's avatar?
Yes, in Discord Developer Portal under your application.

---

## Security Questions

### Is my token safe?
Keep your `.env` file private. Never share it or commit to Git.

### Can others see my Spotify credentials?
No, if you keep `.env` private.

### Should I share my bot token?
Never! Anyone with your token can control your bot.

### What if my token leaks?
Regenerate it immediately in Discord Developer Portal.

---

## Contribution Questions

### Can I contribute?
Yes! Pull requests are welcome.

### How do I report bugs?
Open an issue on GitHub with details.

### Can I suggest features?
Yes! Open an issue with your suggestion.

### Is there a roadmap?
Check the GitHub issues for planned features.

---

## Legal Questions

### Can I use this commercially?
Yes, under MIT license terms.

### Do I need to credit the original?
Not required, but appreciated!

### Can I modify the code?
Yes! It's open source.

### Can I sell this bot?
Yes, under MIT license terms.

---

## Still Have Questions?

- Check the [documentation](.)
- Open an issue on GitHub
- Read the [setup guide](SETUP.md)
- Check [examples](EXAMPLES.md)

---

**Didn't find your answer?** Open an issue on GitHub!
