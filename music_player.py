"""
Clase para gestionar la reproducción de música
"""
import discord
import asyncio
from collections import deque
from config import FFMPEG_OPTIONS, YDL_OPTIONS
import yt_dlp

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
            # Check if it's a local file
            is_local = song.get('is_local', False)
            
            if is_local:
                # Local file - use direct path without streaming options
                source = discord.FFmpegPCMAudio(song['url'])
            else:
                stream_url = song.get('url', '')
                webpage_url = song.get('webpage_url', '')

                # Si la URL es de la página de YouTube (no es stream directo)
                # o si parece haber expirado, obtener URL fresca
                needs_refresh = (
                    not stream_url
                    or 'youtube.com/watch' in stream_url
                    or 'youtu.be/' in stream_url
                    or 'googlevideo.com' not in stream_url  # No es URL de stream de Google
                )

                if needs_refresh and webpage_url:
                    print(f'[DEBUG] Getting fresh URL for: {webpage_url}')
                    try:
                        loop = asyncio.get_event_loop()
                        stream_url = await loop.run_in_executor(
                            None, lambda: self._get_fresh_url(webpage_url)
                        )
                        print(f'[DEBUG] Fresh URL obtained: {stream_url[:80] if stream_url else "None"}...')
                    except Exception as e:
                        print(f'[ERROR] Error getting fresh URL: {e}')
                        stream_url = None
                else:
                    print(f'[DEBUG] Using cached stream URL')

                if not stream_url:
                    await self.channel.send('❌ Could not get stream URL')
                    await self.play_next()
                    return
                
                # Add headers for YouTube
                ffmpeg_opts = FFMPEG_OPTIONS.copy()
                ffmpeg_opts['before_options'] = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin -headers "User-Agent: Mozilla/5.0"'
                
                source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_opts)
            
            self.voice_client.play(source, after=self.play_next_song)
            await self.channel.send(f'🎵 Now Playing: **{song["title"]}**')
        except Exception as e:
            await self.channel.send(f'❌ Error playing: {str(e)}')
            await self.play_next()

    def _get_fresh_url(self, webpage_url):
        """Obtiene una URL fresca del stream desde la webpage_url"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                # Get the direct URL
                if 'url' in info:
                    return info['url']
                # Sometimes it's in formats
                if 'formats' in info:
                    for f in info['formats']:
                        if f.get('acodec') != 'none':
                            return f['url']
                return info.get('url')
        except Exception as e:
            print(f'Error getting fresh URL: {e}')
            return None

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
