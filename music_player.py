"""
Clase para gestionar la reproducción de música
"""
import discord
import asyncio
from collections import deque
from config import FFMPEG_OPTIONS

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.queue = deque()
        self.current = None
        self.voice_client = None
        self.loop_mode = False  # False, 'song', 'queue'

    def play_next_song(self, error=None):
        if error:
            print(f'Error en reproducción: {error}')
        
        coro = self.play_next()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f'Error al reproducir siguiente: {e}')

    async def play_next(self):
        if self.loop_mode == 'song' and self.current:
            # Repetir la canción actual
            song = self.current
        elif len(self.queue) > 0:
            self.current = self.queue.popleft()
            song = self.current
            
            # Si está en modo loop queue, añadir de nuevo al final
            if self.loop_mode == 'queue':
                self.queue.append(song)
        else:
            self.current = None
            return
        
        try:
            source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
            self.voice_client.play(source, after=self.play_next_song)
            await self.channel.send(f'🎵 Reproduciendo: **{song["title"]}**')
        except Exception as e:
            await self.channel.send(f'❌ Error al reproducir: {str(e)}')
            await self.play_next()

    def clear_queue(self):
        """Limpia la cola"""
        self.queue.clear()
        self.current = None

    def shuffle_queue(self):
        """Mezcla la cola"""
        import random
        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)

    def remove_song(self, index):
        """Elimina una canción de la cola por índice"""
        if 0 <= index < len(self.queue):
            queue_list = list(self.queue)
            removed = queue_list.pop(index)
            self.queue = deque(queue_list)
            return removed
        return None
