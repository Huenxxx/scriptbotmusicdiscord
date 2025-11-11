# Commands Reference

Complete list of all available commands for the Discord Music Bot.

## Command Prefix

Default prefix: `!`

You can change this in `config.py` by modifying `COMMAND_PREFIX`.

## Playback Commands

### !play (aliases: !p)
Play music from YouTube or Spotify.

**Usage:**
```
!play <song name>
!play <YouTube URL>
!play <Spotify URL>
```

**Examples:**
```
!play never gonna give you up
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
!play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

**Supported:**
- YouTube videos (direct URL)
- YouTube search (by name)
- Spotify tracks
- Spotify playlists (loads up to 50 songs)
- Spotify albums

---

### !skip (aliases: !s)
Skip the current song and play the next one in queue.

**Usage:**
```
!skip
```

---

### !pause
Pause the current playback.

**Usage:**
```
!pause
```

---

### !resume (aliases: !r)
Resume paused playback.

**Usage:**
```
!resume
```

---

### !stop
Stop playback and clear the entire queue.

**Usage:**
```
!stop
```

---

### !leave (aliases: !disconnect, !dc)
Disconnect the bot from the voice channel.

**Usage:**
```
!leave
```

---

## Queue Management Commands

### !queue (aliases: !q)
Display the current queue.

**Usage:**
```
!queue
```

**Shows:**
- Currently playing song
- Next 10 songs in queue
- Total number of songs
- Current loop mode (if active)

---

### !shuffle (aliases: !mix)
Randomly shuffle the queue.

**Usage:**
```
!shuffle
```

---

### !remove (aliases: !rm)
Remove a specific song from the queue by its position.

**Usage:**
```
!remove <position>
```

**Example:**
```
!remove 3    # Removes the 3rd song in queue
```

---

### !clear
Clear the entire queue without stopping current playback.

**Usage:**
```
!clear
```

---

### !loop (aliases: !repeat)
Toggle loop mode.

**Usage:**
```
!loop              # Cycle through modes
!loop song         # Loop current song
!loop queue        # Loop entire queue
!loop off          # Disable loop
```

**Modes:**
- `song` - Repeat the current song indefinitely
- `queue` - Repeat the entire queue
- `off` - No looping (default)

---

## Playlist Commands

### !playlist_save (aliases: !pl_save, !pls)
Save the current queue as a playlist.

**Usage:**
```
!playlist_save <name>
```

**Example:**
```
!playlist_save my_favorites
```

**Note:** Playlists are saved as JSON files in the `playlists/` folder.

---

### !playlist_load (aliases: !pl_load, !pll)
Load a saved playlist into the queue.

**Usage:**
```
!playlist_load <name>
```

**Example:**
```
!playlist_load my_favorites
```

---

### !playlist_list (aliases: !pl_list, !playlists)
List all saved playlists.

**Usage:**
```
!playlist_list
```

**Shows:**
- Playlist name
- Number of songs in each playlist

---

### !playlist_delete (aliases: !pl_delete, !pld)
Delete a saved playlist.

**Usage:**
```
!playlist_delete <name>
```

**Example:**
```
!playlist_delete my_favorites
```

---

## Help Command

### !help_music (aliases: !comandos, !ayuda)
Display help message with all available commands.

**Usage:**
```
!help_music
```

---

## Command Examples

### Basic Playback
```
!play despacito
!skip
!pause
!resume
!stop
```

### Queue Management
```
!play song 1
!play song 2
!play song 3
!queue
!shuffle
!remove 2
!clear
```

### Loop Modes
```
!play my favorite song
!loop song          # Repeat this song
!skip
!loop queue         # Repeat the whole queue
!loop off           # Stop looping
```

### Playlist Workflow
```
# Create a playlist
!play song 1
!play song 2
!play song 3
!playlist_save workout

# Later...
!playlist_load workout
!shuffle
!loop queue
```

### Spotify Integration
```
# Single track
!play https://open.spotify.com/track/...

# Playlist
!play https://open.spotify.com/playlist/...

# Album
!play https://open.spotify.com/album/...
```

---

## Tips

1. **Use aliases** for faster commands:
   - `!p` instead of `!play`
   - `!s` instead of `!skip`
   - `!q` instead of `!queue`

2. **Queue multiple songs** before shuffling:
   ```
   !play song 1
   !play song 2
   !play song 3
   !shuffle
   ```

3. **Save your sessions** as playlists:
   ```
   !playlist_save friday_night
   ```

4. **Use loop for parties**:
   ```
   !playlist_load party_mix
   !shuffle
   !loop queue
   ```

5. **Remove unwanted songs** without stopping:
   ```
   !queue
   !remove 5
   ```

---

## Permissions Required

The bot needs these permissions to function:
- Send Messages
- Connect (to voice channels)
- Speak (in voice channels)
- Use Voice Activity

Make sure the bot's role has these permissions in your server settings.
