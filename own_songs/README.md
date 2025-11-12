# Own Songs Folder

Place your personal music files here to play them with the bot.

## Supported Formats

- **Common:** mp3, wav, flac, ogg, m4a
- **Advanced:** aac, wma, opus, mpeg, mpga
- **Video:** mp4, webm (audio only)

## How to Use

1. **Add Files:** Copy your audio files to this folder
2. **List Songs:** Use `!ownplay` or `!ownlist` in Discord
3. **Play:** Use `!ownplay <name>` or `!ownplay <number>`

## Examples

```
own_songs/
├── my_favorite_song.mp3
├── rare_track.flac
├── custom_mix.wav
└── unreleased_demo.m4a
```

Then in Discord:
```
!ownplay                    # List all
!ownplay my_favorite        # Play by name
!ownplay 1                  # Play first song
```

## Tips

- Use descriptive filenames (they become the song names)
- Organize with subfolders if needed (bot searches recursively)
- High-quality formats (FLAC, WAV) work great
- Mix local files with YouTube/Spotify in the same queue

## Commands

- `!ownplay` or `!op` - Play local music
- `!ownlist` or `!ol` - List all local songs
- `!queue` - See queue (includes local files)

---

**Note:** Files in this folder are not uploaded to Git (in .gitignore)
