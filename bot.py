"""
Bot de Música para Discord – Versión Lavalink
Usa wavelink + Lavalink para audio de alta calidad y baja latencia.
Mantiene compatibilidad con música local (FFmpeg) y playlists guardadas.
"""

import discord
from discord.ext import commands
import asyncio
import wavelink

from config import DISCORD_TOKEN, COMMAND_PREFIX
from lavalink_manager import (
    LavalinkPlayer, setup_wavelink,
    lavalink_search, lavalink_load_playlist, fmt_duration,
    lavalink_connected,
)
from music_sources import is_spotify_url, extract_spotify_id
from playlist_manager import PlaylistManager
from local_music import get_local_songs, search_local_songs, get_song_by_index, format_song_list

# ─── Bot setup ───────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# guild_id → LavalinkPlayer
lava_players: dict[int, LavalinkPlayer] = {}

# guild_id → resultados pendientes de !select
pending_searches: dict[int, dict] = {}


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def get_or_create_player(ctx: commands.Context) -> LavalinkPlayer | None:
    """Conecta el bot al canal de voz y devuelve (o crea) el LavalinkPlayer."""
    if not ctx.author.voice:
        await ctx.send('❌ Debes estar en un canal de voz')
        return None

    vc: wavelink.Player = ctx.voice_client  # type: ignore

    if vc is None:
        try:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        except Exception as e:
            await ctx.send(f'❌ No pude conectarme al canal de voz: {e}')
            return None
    elif ctx.author.voice.channel != vc.channel:
        await vc.move_to(ctx.author.voice.channel)

    if ctx.guild.id not in lava_players:
        lava_players[ctx.guild.id] = LavalinkPlayer(ctx, vc)
    else:
        lava_players[ctx.guild.id].wl = vc

    return lava_players[ctx.guild.id]


# ─── Eventos ─────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📡 Conectado a {len(bot.guilds)} servidor(es)')
    try:
        await setup_wavelink(bot)
    except Exception as e:
        print(f'⚠️  No se pudo conectar a Lavalink: {e}')
    print('=' * 60)


@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    """Reproduce la siguiente canción automáticamente al terminar."""
    player = payload.player
    if player is None:
        return
    lp = lava_players.get(player.guild.id)
    if lp and payload.reason == 'finished':
        await lp.play_next()


@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f'✅ Nodo Lavalink listo: {payload.node.uri}')


# ─── Reproducción ────────────────────────────────────────────────────────────

@bot.command(name='play', aliases=['p'])
async def play(ctx: commands.Context, *, query: str):
    """Reproduce música desde YouTube, Spotify, SoundCloud o búsqueda de texto."""
    if not lavalink_connected():
        await ctx.send(
            '❌ **Lavalink no está conectado.**\n'
            'El servidor de audio aún está iniciando o no hay nodos disponibles.\n'
            '⏳ Espera unos segundos y vuelve a intentarlo.'
        )
        return

    lp = await get_or_create_player(ctx)
    if lp is None:
        return

    await ctx.send(f'🔍 Buscando: **{query}**')

    try:
        # ── Playlist / Álbum de Spotify ───────────────────────────────────
        if is_spotify_url(query):
            tipo, _ = extract_spotify_id(query)
            if tipo in ('playlist', 'album'):
                playlist = await lavalink_load_playlist(query)
                if playlist and playlist.tracks:
                    label = 'playlist' if tipo == 'playlist' else 'álbum'
                    for track in playlist.tracks:
                        lp.queue.append(track)
                    if not lp.wl.playing:
                        await lp.play_next()
                    await ctx.send(f'✅ {len(playlist.tracks)} canciones del {label} añadidas')
                else:
                    await ctx.send('❌ No se pudo cargar la playlist de Spotify')
                return

        # ── URL directa o búsqueda ────────────────────────────────────────
        tracks = await lavalink_search(query, max_results=5)

        if not tracks:
            await ctx.send('❌ No se encontraron canciones')
            return

        if query.startswith('http') or len(tracks) == 1:
            track = tracks[0]
            lp.queue.append(track)
            if not lp.wl.playing:
                await lp.play_next()
            else:
                dur = fmt_duration(track.length)
                await ctx.send(f'➕ Añadido a la cola: **{track.title}** `[{dur}]`')
            return

        # Múltiples resultados → mostrar opciones
        msg = '🎵 **Resultados encontrados** – usa `!select <número>`:\n\n'
        for i, t in enumerate(tracks, 1):
            dur = fmt_duration(t.length)
            author = getattr(t, 'author', '')
            msg += f'**{i}.** {t.title} `[{dur}]`{" • " + author if author else ""}\n'
        msg += '\n💡 Escribe `!select <número>` o espera 30 s para elegir el #1'

        pending_searches[ctx.guild.id] = {
            'results': tracks,
            'player': lp,
            'timestamp': asyncio.get_event_loop().time(),
        }
        await ctx.send(msg)

        async def auto_select():
            await asyncio.sleep(30)
            if ctx.guild.id in pending_searches:
                data = pending_searches.pop(ctx.guild.id)
                t = data['results'][0]
                data['player'].queue.append(t)
                if not data['player'].wl.playing:
                    await data['player'].play_next()
                else:
                    await ctx.send(f'⏱️ Auto-seleccionado: **{t.title}**')

        asyncio.create_task(auto_select())

    except Exception as e:
        await ctx.send(f'❌ Error: {e}')


@bot.command(name='select', aliases=['choose', 'pick'])
async def select(ctx: commands.Context, number: int):
    """Selecciona una canción de los resultados de búsqueda."""
    data = pending_searches.pop(ctx.guild.id, None)
    if not data:
        await ctx.send('❌ No hay búsqueda activa. Usa `!play <canción>` primero')
        return

    results = data['results']
    if number < 1 or number > len(results):
        await ctx.send(f'❌ Número inválido (1-{len(results)})')
        return

    track = results[number - 1]
    lp: LavalinkPlayer = data['player']
    lp.queue.append(track)

    if not lp.wl.playing:
        await lp.play_next()
    else:
        await ctx.send(f'➕ Añadido: **{track.title}**')


# ─── Controles básicos ───────────────────────────────────────────────────────

@bot.command(name='skip', aliases=['s'])
async def skip(ctx: commands.Context):
    """Salta la canción actual."""
    lp = lava_players.get(ctx.guild.id)
    if lp and lp.wl.playing:
        await lp.wl.stop()
        await ctx.send('⏭️ Canción saltada')
    else:
        await ctx.send('❌ No hay música reproduciéndose')


@bot.command(name='pause')
async def pause(ctx: commands.Context):
    """Pausa la reproducción."""
    lp = lava_players.get(ctx.guild.id)
    if lp and lp.wl.playing:
        await lp.wl.pause(True)
        await ctx.send('⏸️ Pausado')
    else:
        await ctx.send('❌ No hay música reproduciéndose')


@bot.command(name='resume', aliases=['r'])
async def resume(ctx: commands.Context):
    """Reanuda la reproducción."""
    lp = lava_players.get(ctx.guild.id)
    if lp and lp.wl.paused:
        await lp.wl.pause(False)
        await ctx.send('▶️ Reanudado')
    else:
        await ctx.send('❌ La música no está pausada')


@bot.command(name='stop')
async def stop(ctx: commands.Context):
    """Para la música y limpia la cola."""
    lp = lava_players.get(ctx.guild.id)
    if lp:
        lp.clear_queue()
        await lp.wl.stop()
        await ctx.send('⏹️ Detenido y cola limpiada')
    else:
        await ctx.send('❌ No hay música reproduciéndose')


@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave(ctx: commands.Context):
    """Desconecta el bot del canal de voz."""
    if ctx.voice_client:
        lava_players.pop(ctx.guild.id, None)
        pending_searches.pop(ctx.guild.id, None)
        await ctx.voice_client.disconnect()
        await ctx.send('👋 Desconectado')
    else:
        await ctx.send('❌ No estoy en un canal de voz')


# ─── Cola ────────────────────────────────────────────────────────────────────

@bot.command(name='queue', aliases=['q'])
async def queue_cmd(ctx: commands.Context):
    """Muestra la cola de reproducción."""
    lp = lava_players.get(ctx.guild.id)
    if not lp or (lp.current is None and not lp.queue):
        await ctx.send('❌ La cola está vacía')
        return

    msg = '🎵 **Cola de reproducción:**\n\n'
    if lp.current:
        msg += f'▶️ **Reproduciendo:** {lp.current.title}\n\n'
    if lp.queue:
        msg += '**Próximas canciones:**\n'
        for i, t in enumerate(list(lp.queue)[:10], 1):
            msg += f'{i}. {t.title}\n'
        if len(lp.queue) > 10:
            msg += f'\n... y {len(lp.queue) - 10} más'
    if lp.loop_mode:
        msg += f'\n\n🔁 Loop: **{lp.loop_mode}**'
    await ctx.send(msg)


@bot.command(name='shuffle', aliases=['mix'])
async def shuffle(ctx: commands.Context):
    """Mezcla la cola."""
    lp = lava_players.get(ctx.guild.id)
    if not lp or not lp.queue:
        await ctx.send('❌ La cola está vacía')
        return
    lp.shuffle_queue()
    await ctx.send('🔀 Cola mezclada')


@bot.command(name='remove', aliases=['rm'])
async def remove(ctx: commands.Context, index: int):
    """Elimina una canción de la cola por número."""
    lp = lava_players.get(ctx.guild.id)
    if not lp:
        await ctx.send('❌ La cola está vacía')
        return
    removed = lp.remove_song(index - 1)
    if removed:
        await ctx.send(f'🗑️ Eliminado: **{removed.title}**')
    else:
        await ctx.send('❌ Número inválido')


@bot.command(name='clear')
async def clear(ctx: commands.Context):
    """Limpia la cola sin detener la canción actual."""
    lp = lava_players.get(ctx.guild.id)
    if not lp:
        await ctx.send('❌ La cola está vacía')
        return
    count = len(lp.queue)
    lp.queue.clear()
    await ctx.send(f'🗑️ Cola limpiada ({count} canciones)')


@bot.command(name='loop', aliases=['repeat'])
async def loop(ctx: commands.Context, mode: str = None):
    """Activa/desactiva loop (song / queue / off)."""
    lp = lava_players.get(ctx.guild.id)
    if not lp:
        await ctx.send('❌ No hay música reproduciéndose')
        return

    if mode is None:
        if not lp.loop_mode:
            lp.loop_mode = 'song'
            await ctx.send('🔂 Loop: **canción actual**')
        elif lp.loop_mode == 'song':
            lp.loop_mode = 'queue'
            await ctx.send('🔁 Loop: **cola completa**')
        else:
            lp.loop_mode = False
            await ctx.send('➡️ Loop desactivado')
    else:
        mode = mode.lower()
        if mode in ('song', 'cancion', 'track'):
            lp.loop_mode = 'song'
            await ctx.send('🔂 Loop: **canción actual**')
        elif mode in ('queue', 'cola', 'all'):
            lp.loop_mode = 'queue'
            await ctx.send('🔁 Loop: **cola completa**')
        elif mode in ('off', 'no', 'disable'):
            lp.loop_mode = False
            await ctx.send('➡️ Loop desactivado')
        else:
            await ctx.send('❌ Modo inválido. Usa: song, queue, o off')


# ─── Música local ─────────────────────────────────────────────────────────────

@bot.command(name='ownplay', aliases=['op', 'local'])
async def ownplay(ctx: commands.Context, *, query: str = None):
    """Reproduce archivos locales de la carpeta own_songs."""
    if not ctx.author.voice:
        await ctx.send('❌ Debes estar en un canal de voz')
        return

    if not query:
        songs = get_local_songs()
        if not songs:
            await ctx.send('❌ No hay canciones en `own_songs/`')
            return
        await ctx.send(format_song_list(songs) + '\n\n💡 Usa `!ownplay <nombre o número>`')
        return

    try:
        idx = int(query) - 1
        song = get_song_by_index(idx)
        if not song:
            raise ValueError
    except ValueError:
        results = search_local_songs(query)
        if not results:
            await ctx.send(f'❌ No encontré canciones para: **{query}**')
            return
        if len(results) > 1:
            msg = f'🎵 **{len(results)} canciones encontradas:**\n\n'
            for i, s in enumerate(results, 1):
                msg += f'**{i}.** {s["name"]} `.{s["format"]}`\n'
            await ctx.send(msg + '\n💡 Usa `!ownplay <número>`')
            return
        song = results[0]

    vc = ctx.voice_client
    if vc is None:
        vc = await ctx.author.voice.channel.connect()

    if vc.is_playing() or vc.is_paused():
        await ctx.send('⚠️ El bot ya está reproduciendo. Usa `!stop` primero para música local.')
        return

    source = discord.FFmpegPCMAudio(song['path'])
    vc.play(source)
    await ctx.send(f'🎵 Reproduciendo (local): **{song["name"]}**')


@bot.command(name='ownlist', aliases=['ol'])
async def ownlist(ctx: commands.Context):
    """Lista las canciones locales."""
    songs = get_local_songs()
    if not songs:
        await ctx.send('❌ No hay canciones en `own_songs/`')
        return
    await ctx.send(format_song_list(songs, max_display=20))


# ─── Playlists guardadas ─────────────────────────────────────────────────────

@bot.command(name='playlist_save', aliases=['pl_save', 'pls'])
async def playlist_save(ctx: commands.Context, name: str):
    """Guarda la cola actual como playlist."""
    lp = lava_players.get(ctx.guild.id)
    if not lp or (lp.current is None and not lp.queue):
        await ctx.send('❌ La cola está vacía')
        return

    songs = []
    if lp.current:
        songs.append({'title': lp.current.title, 'url': lp.current.uri,
                      'webpage_url': lp.current.uri, 'duration': (lp.current.length or 0) // 1000,
                      'search_query': lp.current.title})
    for t in lp.queue:
        songs.append({'title': t.title, 'url': t.uri,
                      'webpage_url': t.uri, 'duration': (t.length or 0) // 1000,
                      'search_query': t.title})

    PlaylistManager.save_playlist(name, songs)
    await ctx.send(f'💾 Playlist **{name}** guardada con {len(songs)} canciones')


@bot.command(name='playlist_load', aliases=['pl_load', 'pll'])
async def playlist_load(ctx: commands.Context, name: str):
    """Carga una playlist guardada."""
    lp = await get_or_create_player(ctx)
    if not lp:
        return

    playlist = PlaylistManager.load_playlist(name)
    if not playlist:
        await ctx.send(f'❌ No se encontró la playlist **{name}**')
        return

    songs = playlist['songs']
    await ctx.send(f'📋 Cargando playlist **{name}** ({len(songs)} canciones)...')

    added = 0
    for song in songs:
        try:
            tracks = await lavalink_search(song.get('webpage_url') or song.get('search_query', song['title']))
            if tracks:
                lp.queue.append(tracks[0])
                added += 1
        except Exception:
            continue

    await ctx.send(f'✅ {added} canciones añadidas')
    if not lp.wl.playing:
        await lp.play_next()


@bot.command(name='playlist_list', aliases=['pl_list', 'playlists'])
async def playlist_list(ctx: commands.Context):
    """Lista las playlists guardadas."""
    pls = PlaylistManager.list_playlists()
    if not pls:
        await ctx.send('❌ No hay playlists guardadas')
        return
    msg = '📚 **Playlists guardadas:**\n\n'
    for pl in pls:
        msg += f'• **{pl["name"]}** – {pl["song_count"]} canciones\n'
    await ctx.send(msg)


@bot.command(name='playlist_delete', aliases=['pl_delete', 'pld'])
async def playlist_delete(ctx: commands.Context, name: str):
    """Elimina una playlist guardada."""
    if PlaylistManager.delete_playlist(name):
        await ctx.send(f'🗑️ Playlist **{name}** eliminada')
    else:
        await ctx.send(f'❌ No se encontró la playlist **{name}**')


# ─── Ayuda ────────────────────────────────────────────────────────────────────

@bot.command(name='help_music', aliases=['comandos', 'ayuda'])
async def help_music(ctx: commands.Context):
    """Muestra todos los comandos disponibles."""
    await ctx.send("""
🎵 **BOT DE MÚSICA – COMANDOS** (powered by Lavalink)

**Reproducción:**
`!play <canción/url>` – YouTube, Spotify, SoundCloud, texto
`!skip` – Salta la canción actual
`!pause` / `!resume` – Pausa / reanuda
`!stop` – Detiene y limpia la cola
`!leave` – Desconecta el bot

**Cola:**
`!queue` – Muestra la cola
`!shuffle` – Mezcla la cola
`!remove <n>` – Elimina una canción
`!clear` – Limpia la cola
`!loop [song/queue/off]` – Activa loop

**Música local:**
`!ownplay [nombre/número]` – Reproduce archivo local
`!ownlist` – Lista canciones locales

**Playlists:**
`!playlist_save <nombre>` – Guarda la cola actual
`!playlist_load <nombre>` – Carga una playlist
`!playlist_list` – Lista las playlists
`!playlist_delete <nombre>` – Elimina una playlist

✅ YouTube | ✅ Spotify | ✅ SoundCloud | ✅ HTTP streams
⚡ Audio via **Lavalink** – máxima calidad y mínima latencia
""")
