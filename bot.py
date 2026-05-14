"""
Bot de Música para Discord - Versión Modular
Soporta YouTube, Spotify, y gestión de playlists
"""
import discord
from discord.ext import commands
import asyncio
import os

from config import DISCORD_TOKEN, COMMAND_PREFIX, FFMPEG_PATH
from music_player import MusicPlayer
from music_sources import search_song, get_spotify_playlist, get_spotify_album, extract_spotify_id, is_spotify_url, ytdl_search, SPOTIFY_AVAILABLE, search_spotify_track
from playlist_manager import PlaylistManager
from local_music import get_local_songs, search_local_songs, get_song_by_index, format_song_list

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Diccionario de players por servidor
queues = {}

# Diccionario para almacenar búsquedas pendientes por usuario
pending_searches = {}

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📡 Conectado a {len(bot.guilds)} servidor(es)')
    if FFMPEG_PATH:
        print(f'✅ FFmpeg: {FFMPEG_PATH}')
    print('✅ Spotify: Disponible vía yt-dlp (sin API)')
    print('=' * 60)

# ==================== COMANDOS DE REPRODUCCIÓN ====================

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Play music from YouTube or Spotify"""
    if not ctx.author.voice:
        await ctx.send('❌ You must be in a voice channel')
        return

    channel = ctx.author.voice.channel
    await ctx.send(f'🔍 Searching: **{query}**')

    loop = asyncio.get_event_loop()

    try:
        # Verificar si es una playlist o álbum de Spotify (manejo especial)
        if is_spotify_url(query):
            tipo, spotify_id = extract_spotify_id(query)

            if tipo in ('playlist', 'album'):
                # Conectar a voz primero para estas rutas
                if ctx.voice_client is None:
                    voice_client = await channel.connect()
                else:
                    voice_client = ctx.voice_client

                if ctx.guild.id not in queues:
                    queues[ctx.guild.id] = MusicPlayer(ctx)
                queues[ctx.guild.id].voice_client = voice_client
                player = queues[ctx.guild.id]
                player.voice_client = voice_client

                fetch_fn = get_spotify_playlist if tipo == 'playlist' else get_spotify_album
                label = 'playlist' if tipo == 'playlist' else 'album'
                tracks = await loop.run_in_executor(None, lambda: fetch_fn(query))
                if tracks:
                    await ctx.send(f'{"📋" if tipo=="playlist" else "💿"} Loading {len(tracks)} songs from Spotify {label}...')

                    if tracks:
                        first_track = tracks[0]
                        first_data = await loop.run_in_executor(None, lambda: ytdl_search(first_track['search_query']))
                        if first_data:
                            player.queue.append(first_data)
                            if not voice_client.is_playing() and not voice_client.is_paused():
                                await player.play_next()
                            await ctx.send(f'🎵 Playing first song, loading {len(tracks)-1} more in background...')

                    async def load_remaining():
                        limit = 50 if tipo == 'playlist' else len(tracks)
                        added = 1
                        for track in tracks[1:limit]:
                            try:
                                data = await loop.run_in_executor(None, lambda t=track: ytdl_search(t['search_query']))
                                if data:
                                    player.queue.append(data)
                                    added += 1
                            except:
                                continue
                        await ctx.send(f'✅ Finished loading {label}: {added} songs added')

                    asyncio.create_task(load_remaining())
                return

        # ── Canción individual ─────────────────────────────────────────────
        # Búsqueda y conexión de voz en PARALELO para reducir latencia
        async def connect_voice():
            if ctx.voice_client is None:
                return await channel.connect()
            return ctx.voice_client

        async def search_query_async():
            # URL directa de YouTube
            if 'youtube.com' in query or 'youtu.be' in query:
                return await loop.run_in_executor(None, lambda: ytdl_search(query, max_results=1)), 'direct'
            # URL de Spotify (track individual)
            if is_spotify_url(query):
                return await loop.run_in_executor(None, lambda: get_spotify_track(query)), 'spotify_track'
            # Búsqueda por texto → múltiples resultados para elegir
            results = await loop.run_in_executor(None, lambda: ytdl_search(query, max_results=5))
            return results, 'search'

        # Ejecutar en paralelo
        (voice_client, (search_result, search_type)) = await asyncio.gather(
            connect_voice(),
            search_query_async(),
        )

        # Inicializar player
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = MusicPlayer(ctx)
        player = queues[ctx.guild.id]
        player.voice_client = voice_client

        # ── Procesar resultado ─────────────────────────────────────────────
        if search_type in ('direct', 'spotify_track'):
            data = search_result
            if data:
                player.queue.append(data)
                if not voice_client.is_playing() and not voice_client.is_paused():
                    await player.play_next()
                else:
                    suffix = ' (via Spotify)' if search_type == 'spotify_track' else ''
                    await ctx.send(f'➕ Added to queue: **{data["title"]}**{suffix}')
            else:
                await ctx.send('❌ Song not found')
            return

        # search_type == 'search'
        results = search_result
        if not results:
            await ctx.send('❌ No songs found')
            return

        first_result = results[0] if isinstance(results, list) else results
        from music_sources import is_confident_result

        if is_confident_result(first_result, query):
            player.queue.append(first_result)
            if not voice_client.is_playing() and not voice_client.is_paused():
                await player.play_next()
            else:
                view_count = first_result.get('view_count', 0)
                views_str = f" ({view_count:,} views)" if view_count > 0 else ""
                await ctx.send(f'➕ Added to queue: **{first_result["title"]}**{views_str}')
            return

        # Resultados ambiguos → mostrar opciones
        message = '🎵 **Multiple results found** - Use `!select <number>` to choose:\n\n'
        for i, result in enumerate(results, 1):
            duration = result.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
            view_count = result.get('view_count', 0)
            views_str = f" • {view_count // 1_000_000}M views" if view_count > 1_000_000 else ""
            ch = result.get('channel', '')
            channel_str = f" • {ch}" if ch else ""
            message += f'**{i}.** {result["title"]} `[{duration_str}]`{views_str}{channel_str}\n'

        message += f'\n💡 Type `!select <number>` or wait 30 seconds to auto-select #1'

        pending_searches[ctx.author.id] = {
            'results': results,
            'channel': ctx.channel,
            'voice_client': voice_client,
            'player': player,
            'timestamp': asyncio.get_event_loop().time()
        }

        await ctx.send(message)

    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')


@bot.command(name='select', aliases=['choose', 'pick'])
async def select(ctx, number: int):
    """Select a song from search results"""
    user_id = ctx.author.id
    
    if user_id not in pending_searches:
        await ctx.send('❌ No active search. Use `!play <song name>` first')
        return
    
    search_data = pending_searches[user_id]
    results = search_data['results']
    
    if number < 1 or number > len(results):
        await ctx.send(f'❌ Invalid number. Choose between 1 and {len(results)}')
        return
    
    # Get selected song
    selected = results[number - 1]
    player = search_data['player']
    voice_client = search_data['voice_client']
    
    # Add to queue
    player.queue.append(selected)
    
    # Clear pending search
    del pending_searches[user_id]
    
    # Play if nothing is playing
    if not voice_client.is_playing() and not voice_client.is_paused():
        await player.play_next()
    else:
        await ctx.send(f'➕ Added to queue: **{selected["title"]}**')

# ==================== LOCAL MUSIC COMMANDS ====================

@bot.command(name='ownplay', aliases=['op', 'local'])
async def ownplay(ctx, *, query=None):
    """Play music from local files in own_songs folder"""
    if not ctx.author.voice:
        await ctx.send('❌ You must be in a voice channel')
        return

    channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        voice_client = await channel.connect()
    else:
        voice_client = ctx.voice_client

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = MusicPlayer(ctx)
        queues[ctx.guild.id].voice_client = voice_client

    player = queues[ctx.guild.id]
    player.voice_client = voice_client

    # If no query, show all local songs
    if not query:
        songs = get_local_songs()
        if not songs:
            await ctx.send('❌ No local songs found in `own_songs` folder\n💡 Add .mp3, .flac, .wav, or other audio files to the folder')
            return
        
        message = format_song_list(songs)
        message += '\n\n💡 Use `!ownplay <name>` or `!ownplay <number>` to play'
        await ctx.send(message)
        return
    
    # Try to parse as number first
    try:
        index = int(query) - 1
        song = get_song_by_index(index)
        if song:
            # Create song data for player
            song_data = {
                'url': song['path'],
                'title': f"{song['name']} (Local)",
                'duration': 0,
                'is_local': True
            }
            
            player.queue.append(song_data)
            
            if not voice_client.is_playing() and not voice_client.is_paused():
                await player.play_next()
            else:
                await ctx.send(f'➕ Added to queue: **{song["name"]}** `.{song["format"]}`')
            return
    except ValueError:
        pass
    
    # Search by name
    results = search_local_songs(query)
    
    if not results:
        await ctx.send(f'❌ No local songs found matching: **{query}**\n💡 Use `!ownplay` to see all available songs')
        return
    
    if len(results) == 1:
        # Play directly
        song = results[0]
        song_data = {
            'url': song['path'],
            'title': f"{song['name']} (Local)",
            'duration': 0,
            'is_local': True
        }
        
        player.queue.append(song_data)
        
        if not voice_client.is_playing() and not voice_client.is_paused():
            await player.play_next()
        else:
            await ctx.send(f'➕ Added to queue: **{song["name"]}** `.{song["format"]}`')
    else:
        # Multiple results - show options
        message = f'🎵 **Found {len(results)} local songs:**\n\n'
        for i, song in enumerate(results, 1):
            message += f'**{i}.** {song["name"]} `.{song["format"]}`\n'
        message += '\n💡 Use `!ownplay <number>` to play'
        await ctx.send(message)

@bot.command(name='ownlist', aliases=['ol', 'locallist'])
async def ownlist(ctx):
    """List all local music files"""
    songs = get_local_songs()
    
    if not songs:
        await ctx.send('❌ No local songs found in `own_songs` folder\n💡 Add .mp3, .flac, .wav, or other audio files to the folder')
        return
    
    message = format_song_list(songs, max_display=20)
    message += '\n\n💡 Use `!ownplay <name>` or `!ownplay <number>` to play'
    await ctx.send(message)

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Skip current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ Song skipped')
    else:
        await ctx.send('❌ No music playing')

@bot.command(name='pause')
async def pause(ctx):
    """Pause playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('⏸️ Paused')
    else:
        await ctx.send('❌ No music playing')

@bot.command(name='resume', aliases=['r'])
async def resume(ctx):
    """Resume playback"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('▶️ Resumed')
    else:
        await ctx.send('❌ Music is not paused')

@bot.command(name='stop')
async def stop(ctx):
    """Stop music and clear queue"""
    if ctx.guild.id in queues:
        player = queues[ctx.guild.id]
        player.clear_queue()
    
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send('⏹️ Stopped and queue cleared')
    else:
        await ctx.send('❌ Not in a voice channel')

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave(ctx):
    """Disconnect from voice channel"""
    if ctx.voice_client:
        if ctx.guild.id in queues:
            del queues[ctx.guild.id]
        await ctx.voice_client.disconnect()
        await ctx.send('👋 Disconnected')
    else:
        await ctx.send('❌ Not in a voice channel')

@bot.command(name='queue', aliases=['q'])
async def queue_command(ctx):
    """Muestra la cola de reproducción"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ La cola está vacía')
        return
    
    player = queues[ctx.guild.id]
    
    if player.current is None and len(player.queue) == 0:
        await ctx.send('❌ La cola está vacía')
        return
    
    message = '🎵 **Cola de reproducción:**\n\n'
    
    if player.current:
        message += f'▶️ **Reproduciendo:** {player.current["title"]}\n\n'
    
    if len(player.queue) > 0:
        message += '**Próximas canciones:**\n'
        for i, song in enumerate(list(player.queue)[:10], 1):
            message += f'{i}. {song["title"]}\n'
        
        if len(player.queue) > 10:
            message += f'\n... y {len(player.queue) - 10} más'
    
    if player.loop_mode:
        message += f'\n\n🔁 Modo loop: **{player.loop_mode}**'
    
    await ctx.send(message)

# ==================== COMANDOS DE COLA ====================

@bot.command(name='shuffle', aliases=['mix'])
async def shuffle(ctx):
    """Mezcla la cola de reproducción"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ La cola está vacía')
        return
    
    player = queues[ctx.guild.id]
    if len(player.queue) == 0:
        await ctx.send('❌ No hay canciones en la cola para mezclar')
        return
    
    player.shuffle_queue()
    await ctx.send('🔀 Cola mezclada')

@bot.command(name='remove', aliases=['rm'])
async def remove(ctx, index: int):
    """Elimina una canción de la cola por su número"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ La cola está vacía')
        return
    
    player = queues[ctx.guild.id]
    removed = player.remove_song(index - 1)
    
    if removed:
        await ctx.send(f'🗑️ Eliminado: **{removed["title"]}**')
    else:
        await ctx.send('❌ Número de canción inválido')

@bot.command(name='clear')
async def clear(ctx):
    """Limpia toda la cola sin detener la canción actual"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ La cola está vacía')
        return
    
    player = queues[ctx.guild.id]
    count = len(player.queue)
    player.queue.clear()
    await ctx.send(f'🗑️ Cola limpiada ({count} canciones eliminadas)')

@bot.command(name='loop', aliases=['repeat'])
async def loop(ctx, mode: str = None):
    """Activa/desactiva el modo loop (song/queue/off)"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ No hay música reproduciéndose')
        return
    
    player = queues[ctx.guild.id]
    
    if mode is None:
        # Toggle entre off -> song -> queue -> off
        if not player.loop_mode:
            player.loop_mode = 'song'
            await ctx.send('🔂 Loop activado: **Canción actual**')
        elif player.loop_mode == 'song':
            player.loop_mode = 'queue'
            await ctx.send('🔁 Loop activado: **Cola completa**')
        else:
            player.loop_mode = False
            await ctx.send('➡️ Loop desactivado')
    else:
        mode = mode.lower()
        if mode in ['song', 'cancion', 'track']:
            player.loop_mode = 'song'
            await ctx.send('🔂 Loop activado: **Canción actual**')
        elif mode in ['queue', 'cola', 'all']:
            player.loop_mode = 'queue'
            await ctx.send('🔁 Loop activado: **Cola completa**')
        elif mode in ['off', 'no', 'disable']:
            player.loop_mode = False
            await ctx.send('➡️ Loop desactivado')
        else:
            await ctx.send('❌ Modo inválido. Usa: song, queue, o off')

# ==================== COMANDOS DE PLAYLISTS ====================

@bot.command(name='playlist_save', aliases=['pl_save', 'pls'])
async def playlist_save(ctx, name: str):
    """Save current queue as a playlist (includes local songs)"""
    if ctx.guild.id not in queues:
        await ctx.send('❌ Queue is empty')
        return
    
    player = queues[ctx.guild.id]
    
    if len(player.queue) == 0 and player.current is None:
        await ctx.send('❌ No songs to save')
        return
    
    songs = []
    if player.current:
        songs.append(player.current)
    songs.extend(list(player.queue))
    
    # Count local vs online
    local_count = sum(1 for s in songs if s.get('is_local', False))
    online_count = len(songs) - local_count
    
    PlaylistManager.save_playlist(name, songs)
    
    summary = f'💾 Playlist **{name}** saved with {len(songs)} songs'
    if local_count > 0 and online_count > 0:
        summary += f' ({local_count} local, {online_count} online)'
    elif local_count > 0:
        summary += f' (all local)'
    
    await ctx.send(summary)

@bot.command(name='playlist_load', aliases=['pl_load', 'pll'])
async def playlist_load(ctx, name: str):
    """Carga una playlist guardada"""
    if not ctx.author.voice:
        await ctx.send('❌ Debes estar en un canal de voz')
        return
    
    playlist = PlaylistManager.load_playlist(name)
    
    if not playlist:
        await ctx.send(f'❌ No se encontró la playlist **{name}**')
        return
    
    channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        voice_client = await channel.connect()
    else:
        voice_client = ctx.voice_client
    
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = MusicPlayer(ctx)
        queues[ctx.guild.id].voice_client = voice_client
    
    player = queues[ctx.guild.id]
    player.voice_client = voice_client
    
    songs = playlist['songs']
    await ctx.send(f'📋 Loading playlist **{name}** ({len(songs)} songs)...')
    
    loop = asyncio.get_event_loop()
    added = 0
    local_count = 0
    online_count = 0
    
    for song in songs:
        try:
            # Check if it's a local song
            if song.get('is_local', False):
                local_path = song.get('local_path')
                if local_path and os.path.exists(local_path):
                    # Add local song directly
                    data = {
                        'url': local_path,
                        'title': song['title'],
                        'duration': 0,
                        'is_local': True
                    }
                    player.queue.append(data)
                    added += 1
                    local_count += 1
                else:
                    # Local file not found, skip
                    continue
            else:
                # Online song - search on YouTube
                search_query = song.get('search_query', song['title'])
                data = await loop.run_in_executor(None, lambda q=search_query: ytdl_search(q))
                if data:
                    player.queue.append(data)
                    added += 1
                    online_count += 1
        except:
            continue
    
    summary = f'✅ Added {added} songs'
    if local_count > 0 and online_count > 0:
        summary += f' ({local_count} local, {online_count} online)'
    elif local_count > 0:
        summary += f' (all local)'
    elif online_count > 0:
        summary += f' (all online)'
    
    await ctx.send(summary)
    
    if not voice_client.is_playing() and not voice_client.is_paused():
        await player.play_next()

@bot.command(name='playlist_list', aliases=['pl_list', 'playlists'])
async def playlist_list(ctx):
    """Lista todas las playlists guardadas"""
    playlists = PlaylistManager.list_playlists()
    
    if not playlists:
        await ctx.send('❌ No hay playlists guardadas')
        return
    
    message = '📚 **Playlists guardadas:**\n\n'
    for pl in playlists:
        message += f'• **{pl["name"]}** - {pl["song_count"]} canciones\n'
    
    await ctx.send(message)

@bot.command(name='playlist_delete', aliases=['pl_delete', 'pld'])
async def playlist_delete(ctx, name: str):
    """Elimina una playlist guardada"""
    if PlaylistManager.delete_playlist(name):
        await ctx.send(f'🗑️ Playlist **{name}** eliminada')
    else:
        await ctx.send(f'❌ No se encontró la playlist **{name}**')

# ==================== COMANDO DE AYUDA ====================

@bot.command(name='help_music', aliases=['comandos', 'ayuda'])
async def help_music(ctx):
    """Muestra todos los comandos disponibles"""
    help_text = """
🎵 **COMANDOS DEL BOT DE MÚSICA**

**Reproducción:**
`!play <canción/url>` - Reproduce desde YouTube o Spotify
`!skip` - Salta la canción actual
`!pause` - Pausa la reproducción
`!resume` - Reanuda la reproducción
`!stop` - Detiene y limpia la cola
`!leave` - Desconecta el bot

**Cola:**
`!queue` - Muestra la cola
`!shuffle` - Mezcla la cola
`!remove <número>` - Elimina una canción
`!clear` - Limpia la cola
`!loop [song/queue/off]` - Activa loop

**Playlists:**
`!playlist_save <nombre>` - Guarda la cola actual
`!playlist_load <nombre>` - Carga una playlist
`!playlist_list` - Lista playlists guardadas
`!playlist_delete <nombre>` - Elimina una playlist

**Soporta:**
✅ YouTube (URLs y búsqueda)
✅ Spotify (tracks, playlists, álbumes) - sin API
✅ Playlists guardadas
    """
    await ctx.send(help_text)

# ==================== INICIAR BOT ====================

if __name__ == '__main__':
    if not DISCORD_TOKEN or DISCORD_TOKEN == 'PEGA_TU_TOKEN_AQUI':
        print('=' * 60)
        print('❌ ERROR: Token de Discord no configurado')
        print('=' * 60)
        print('Edita el archivo .env y añade tu token:')
        print('DISCORD_TOKEN=tu_token_aqui')
        print('=' * 60)
    else:
        try:
            if FFMPEG_PATH:
                print(f'✅ FFmpeg encontrado en: {FFMPEG_PATH}')
            else:
                print('⚠️ FFmpeg no encontrado')
            
            print('🤖 Iniciando bot...')
            bot.run(DISCORD_TOKEN)
        except discord.LoginFailure:
            print('❌ Token de Discord inválido')
        except KeyboardInterrupt:
            print('\n👋 Bot detenido')
        except Exception as e:
            print(f'❌ Error: {e}')
