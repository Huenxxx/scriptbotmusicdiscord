"""
Gestor de Lavalink via wavelink 3.x
Ventajas sobre FFmpeg directo:
  - Menor latencia (audio decodificado en el servidor Lavalink, no en el bot)
  - Menor uso de CPU en el bot
  - Soporte nativo: YouTube, Spotify, SoundCloud, HTTP streams...
  - Equalizer / filtros de audio
  - Reconexión automática
"""

import random
import asyncio
from collections import deque

import discord
import wavelink
from discord.ext import commands

import config as _config


# ─── Helpers ────────────────────────────────────────────────────────────────

def fmt_duration(ms: int | None) -> str:
    """Convierte milisegundos a mm:ss o hh:mm:ss."""
    if not ms:
        return '?:??'
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


# ─── Player ─────────────────────────────────────────────────────────────────

class LavalinkPlayer:
    """
    Wrapper del wavelink.Player que añade cola, loop y shuffle.
    Un objeto por servidor (guild).
    """

    def __init__(self, ctx: commands.Context, player: wavelink.Player):
        self.bot         = ctx.bot
        self.guild       = ctx.guild
        self.channel     = ctx.channel          # text channel para enviar mensajes
        self.wl          = player               # wavelink.Player subyacente
        self.queue: deque[wavelink.Playable] = deque()
        self.current: wavelink.Playable | None = None
        self.loop_mode: str | bool = False      # False | 'song' | 'queue'

    # ── Reproducción ───────────────────────────────────────────────────────

    async def play_next(self):
        if self.loop_mode == 'song' and self.current:
            track = self.current
        elif self.queue:
            self.current = self.queue.popleft()
            track = self.current
            if self.loop_mode == 'queue':
                self.queue.append(track)
        else:
            self.current = None
            await self.channel.send('✅ Cola terminada')
            return

        try:
            await self.wl.play(track)
            dur = fmt_duration(track.length)
            author = getattr(track, 'author', 'Unknown')
            await self.channel.send(
                f'🎵 **Now Playing:** [{track.title}]({track.uri})\n'
                f'⏱️ `{dur}` • 🎤 {author}'
            )
        except Exception as e:
            await self.channel.send(f'❌ Error reproduciendo: {e}')
            await self.play_next()

    # ── Cola ───────────────────────────────────────────────────────────────

    def clear_queue(self):
        self.queue.clear()
        self.current = None

    def shuffle_queue(self):
        lst = list(self.queue)
        random.shuffle(lst)
        self.queue = deque(lst)

    def remove_song(self, index: int) -> wavelink.Playable | None:
        if 0 <= index < len(self.queue):
            lst = list(self.queue)
            removed = lst.pop(index)
            self.queue = deque(lst)
            return removed
        return None


# ─── Configuración del nodo ─────────────────────────────────────────────────

async def setup_wavelink(bot: commands.Bot):
    """Conecta wavelink al servidor Lavalink. Llamar desde on_ready()."""
    host     = _config.LAVALINK_HOST
    port     = _config.LAVALINK_PORT
    password = _config.LAVALINK_PASSWORD
    node = wavelink.Node(
        uri=f'http://{host}:{port}',
        password=password,
    )
    await wavelink.Pool.connect(nodes=[node], client=bot, cache_capacity=100)
    print(f'✅ Lavalink: conectado a {host}:{port}')


# ─── Búsqueda ───────────────────────────────────────────────────────────────

async def lavalink_search(query: str, max_results: int = 1) -> list[wavelink.Playable]:
    """
    Busca tracks via Lavalink.
    - URLs directas (YouTube, Spotify, SoundCloud): las carga directamente.
    - Texto libre: busca en YouTube con ytsearch.
    Devuelve lista de hasta max_results pistas.
    """
    if query.startswith('http'):
        result = await wavelink.Playable.search(query)
    else:
        result = await wavelink.Playable.search(f'ytsearch:{query}')

    if not result:
        return []

    if isinstance(result, wavelink.Playlist):
        tracks = list(result.tracks)
    else:
        tracks = list(result)

    return tracks[:max_results]


async def lavalink_load_playlist(query: str) -> wavelink.Playlist | None:
    """Carga una playlist completa (YouTube / Spotify) via Lavalink."""
    try:
        result = await wavelink.Playable.search(query)
        if isinstance(result, wavelink.Playlist):
            return result
    except Exception as e:
        print(f'[Lavalink] Error cargando playlist: {e}')
    return None
