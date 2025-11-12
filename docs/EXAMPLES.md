# Usage Examples

Real-world scenarios and examples for using the Discord Music Bot.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Queue Management](#queue-management)
- [Playlists](#playlists)
- [Spotify Integration](#spotify-integration)
- [Advanced Scenarios](#advanced-scenarios)

---

## Basic Usage

### Playing Your First Song

**Option 1: Direct URL (fastest)**
```
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Bot Response:**
```
🔍 Searching: https://www.youtube.com/watch?v=...
🎵 Now Playing: Rick Astley - Never Gonna Give You Up
```

**Option 2: Search by name (smart search)**

**Popular song (plays immediately):**
```
!play despacito
```

**Bot Response:**
```
🔍 Searching: despacito
➕ Added to queue: Luis Fonsi - Despacito (5,000,000,000 views)
🎵 Now Playing: Luis Fonsi - Despacito
```

**Ambiguous search (shows options):**
```
!play believer
```

**Bot Response:**
```
🔍 Searching: believer
🎵 Multiple results found - Use !select <number> to choose:

1. Imagine Dragons - Believer [3:24] • 800M views • Imagine Dragons
2. Ozzy Osbourne - Believer [5:15] • 50M views • Ozzy Osbourne
3. Believer (Piano Version) [3:30] • 2M views • Piano Covers
4. Imagine Dragons - Believer (Live) [3:45] • 10M views • Live Nation
5. Believer (8D Audio) [3:24] • 5M views • 8D Tunes

💡 Type !select <number> or wait 30 seconds to auto-select #1
```

**Then select:**
```
!select 1
```

**Bot Response:**
```
➕ Added to queue: Imagine Dragons - Believer
🎵 Now Playing: Imagine Dragons - Believer
```

### Search with Multiple Artists

When searching for a common song name:

```
!play believer
```

**Bot shows options:**
```
🎵 Search Results - Use !select <number> to choose:

1. Imagine Dragons - Believer [3:24]
2. Ozzy Osbourne - Believer [5:15]
3. Believer (Piano Version) [3:30]
4. Imagine Dragons - Believer (Live) [3:45]
5. Believer (8D Audio) [3:24]

💡 Type !select <number> or wait 30 seconds to auto-select #1
```

**Choose the one you want:**
```
!select 1    # For Imagine Dragons version
```

### Basic Controls

```
!pause          # Pause the music
!resume         # Resume playback
!skip           # Skip to next song
!stop           # Stop everything
!leave          # Disconnect bot
```

---

## Queue Management

### Building a Queue

```
!play despacito
!play shape of you
!play uptown funk
!play happy pharrell williams
!queue
```

**Bot shows:**
```
🎵 Queue:

▶️ Now Playing: Despacito

Next songs:
1. Shape of You
2. Uptown Funk
3. Happy - Pharrell Williams
```

### Shuffling the Queue

```
!shuffle
```

**Bot Response:**
```
🔀 Queue shuffled
```

### Removing Songs

```
!queue
# See that song #3 is not what you want
!remove 3
```

**Bot Response:**
```
🗑️ Removed: Uptown Funk
```

### Clearing the Queue

```
!clear
```

**Bot Response:**
```
🗑️ Queue cleared (3 songs removed)
```

---

## Playlists

### Creating a Playlist

```
# Add some songs
!play bohemian rhapsody
!play stairway to heaven
!play hotel california
!play sweet child o mine

# Save as playlist
!playlist_save classic_rock
```

**Bot Response:**
```
💾 Playlist classic_rock saved with 4 songs
```

### Loading a Playlist

```
!playlist_load classic_rock
```

**Bot Response:**
```
📋 Loading playlist classic_rock (4 songs)...
✅ Added 4 songs to queue
🎵 Now Playing: Bohemian Rhapsody
```

### Managing Playlists

```
# List all playlists
!playlist_list
```

**Bot shows:**
```
📚 Saved Playlists:

• classic_rock - 4 songs
• workout - 12 songs
• chill_vibes - 8 songs
```

```
# Delete a playlist
!playlist_delete old_playlist
```

---

## Spotify Integration

### Playing a Spotify Track

```
!play https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
```

**Bot Response:**
```
🔍 Searching: https://open.spotify.com/track/...
🎵 Now Playing: [Song Name]
```

### Loading a Spotify Playlist

```
!play https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

**Bot Response:**
```
📋 Loading 50 songs from Spotify playlist...
🎵 Playing first song, loading 49 more in background...
🎵 Now Playing: [First Song]
✅ Finished loading playlist: 50 songs added
```

**Note:** The first song starts playing immediately while the rest load in the background!

### Loading a Spotify Album

```
!play https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy
```

**Bot Response:**
```
💿 Loading 12 songs from album...
🎵 Playing first song, loading 11 more in background...
🎵 Now Playing: [First Track]
✅ Finished loading album: 12 songs added
```

**Note:** Instant playback! No waiting for the entire album to load.

---

## Advanced Scenarios

### Scenario 1: Party Mode

```
# Load party playlist
!playlist_load party_mix

# Shuffle for variety
!shuffle

# Loop so it never ends
!loop queue

# If a song isn't working
!skip
```

### Scenario 2: Study Session

```
# Play study music
!play lofi hip hop
!play study music
!play concentration music

# Loop the queue
!loop queue

# Save for next time
!playlist_save study_session
```

### Scenario 3: Workout Playlist

```
# High energy songs
!play eye of the tiger
!play lose yourself eminem
!play stronger kanye west
!play till i collapse

# Save and shuffle
!playlist_save workout
!shuffle
!loop queue
```

### Scenario 4: Karaoke Night

```
# Play a song
!play bohemian rhapsody

# Loop it for multiple attempts
!loop song

# Pause for breaks
!pause
# ... singing ...
!resume

# Next song
!loop off
!skip
```

### Scenario 5: DJ Mode

```
# Prepare queue before event
!play song 1
!play song 2
!play song 3
# ... add 20-30 songs ...

# Save for the event
!playlist_save friday_event

# During event
!shuffle
!loop queue

# Skip songs if needed
!skip

# Pause for announcements
!pause
!resume
```

### Scenario 6: Mixed Sources

```
# YouTube song
!play https://www.youtube.com/watch?v=...

# Spotify track
!play https://open.spotify.com/track/...

# Search query
!play imagine dragons believer

# Check the mix
!queue
```

### Scenario 7: Collaborative Playlist

```
User1: !play song 1
User2: !play song 2
User3: !play song 3

# Anyone can save it
!playlist_save group_favorites

# Load it later
!playlist_load group_favorites
!shuffle
```

### Scenario 8: Genre-Based Sessions

**Rock Session:**
```
!play ac/dc thunderstruck
!play metallica enter sandman
!play guns n roses sweet child o mine
!playlist_save rock_session
```

**Chill Session:**
```
!play lofi beats
!play chill vibes
!play relaxing music
!loop queue
!playlist_save chill_session
```

**Electronic Session:**
```
!play daft punk
!play deadmau5
!play avicii levels
!playlist_save electronic_session
```

### Scenario 9: Queue Cleanup

```
# Check current queue
!queue

# Remove unwanted songs
!remove 3
!remove 5
!remove 7

# Or start fresh
!clear
!playlist_load my_favorites
```

### Scenario 10: Loop Modes

**Loop Single Song:**
```
!play my favorite song
!loop song
# Song repeats indefinitely
!loop off  # When done
```

**Loop Entire Queue:**
```
!playlist_load party_mix
!loop queue
# Entire playlist repeats
```

**Toggle Loop:**
```
!loop      # Activates song loop
!loop      # Changes to queue loop
!loop      # Turns off loop
```

---

## Tips and Tricks

### 1. Quick Commands
Use aliases for speed:
```
!p song name    # Instead of !play
!s              # Instead of !skip
!q              # Instead of !queue
```

### 2. Specific Searches
Be specific for better results:
```
!play imagine dragons believer official video
!play ed sheeran shape of you acoustic
```

### 3. Playlist Organization
Create themed playlists:
```
!playlist_save gym
!playlist_save work
!playlist_save sleep
!playlist_save party
```

### 4. Queue Management
Build queue, then shuffle:
```
!play song 1
!play song 2
!play song 3
!shuffle
```

### 5. Loop Strategies
- Use `!loop song` for a favorite track
- Use `!loop queue` for continuous playback
- Use `!loop` to cycle through modes

---

## Common Workflows

### Morning Routine
```
!playlist_load morning_vibes
!shuffle
!loop queue
```

### Work/Study
```
!playlist_load focus_music
!loop queue
# Minimal distractions
```

### Party
```
!playlist_load party_hits
!shuffle
!loop queue
# Let it run!
```

### Relaxation
```
!play relaxing music
!play meditation music
!loop queue
```

---

## Troubleshooting Examples

### Song Not Found
```
# Too vague
!play song

# Better
!play never gonna give you up rick astley
```

### Wrong Song Playing
```
!skip
# Or
!stop
!play correct song name
```

### Queue Too Long
```
!clear
!playlist_load shorter_playlist
```

---

Happy listening! 🎵
