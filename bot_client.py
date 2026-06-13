import asyncio
import discord
from discord.ext import commands
import yt_dlp
import os
import logging

# Configurar logs
logger = logging.getLogger("ScriptBot")
logger.setLevel(logging.INFO)

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class DiscordMusicBot(commands.Bot):
    def __init__(self, token, prefix, bridge):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        
        super().__init__(command_prefix=prefix, intents=intents)
        
        self.bot_token = token
        self.bridge = bridge
        self.queue = []
        self.current_track = None
        self.volume = 0.5
        self.voice_client = None
        
        # Control de tiempo para sincronizar letras
        self.track_start_time = None
        self.track_paused_time = None
        self.total_paused_duration = 0
        
        # Enlazar este bot al bridge
        self.bridge.bot = self
        
        self.add_commands()

    def log(self, message):
        """Registra un mensaje tanto en consola como en el bridge para la GUI."""
        logger.info(message)
        self.bridge.add_log(message)

    async def on_ready(self):
        self.log(f"🟢 Bot conectado en Discord como: {self.user.name}#{self.user.discriminator}")
        self.bridge.update_status("online")
        self.bridge.update_guilds([{"id": g.id, "name": g.name} for g in self.guilds])

    async def on_disconnect(self):
        self.log("🔴 Bot desconectado de Discord.")
        self.bridge.update_status("offline")

    async def get_stream_source(self, query):
        """Extrae la informacion del stream de audio usando yt-dlp."""
        # Si es un archivo local en own_songs o ruta valida
        if os.path.exists(query):
            self.log(f"🎵 Cargando archivo local: {os.path.basename(query)}")
            return {
                'title': os.path.basename(query),
                'url': query,
                'duration': 0, # Desconocido o calculado
                'webpage_url': '',
                'thumbnail': '',
                'is_local': True
            }
            
        # Si es un nombre en own_songs sin ruta completa
        local_path = os.path.join("own_songs", query)
        if os.path.exists(local_path):
            self.log(f"🎵 Cargando archivo local desde own_songs: {query}")
            return {
                'title': query,
                'url': local_path,
                'duration': 0,
                'webpage_url': '',
                'thumbnail': '',
                'is_local': True
            }
            
        self.log(f"🔍 Buscando en YouTube: {query}")
        loop = self.loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            if not data:
                return None
                
            if 'entries' in data:
                if not data['entries']:
                    return None
                data = data['entries'][0]
                
            return {
                'title': data.get('title', 'Canción Desconocida'),
                'url': data.get('url'), # Streaming URL
                'duration': data.get('duration', 0),
                'webpage_url': data.get('webpage_url', ''),
                'thumbnail': data.get('thumbnail', ''),
                'is_local': False
            }
        except Exception as e:
            self.log(f"⚠️ Error en la búsqueda de audio: {str(e)}")
            return None

    async def join_voice_channel(self, channel):
        """Conecta el bot a un canal de voz."""
        if self.voice_client and self.voice_client.is_connected():
            if self.voice_client.channel.id != channel.id:
                await self.voice_client.move_to(channel)
                self.log(f"🔊 Movido al canal de voz: {channel.name}")
        else:
            self.voice_client = await channel.connect()
            self.log(f"🔊 Conectado al canal de voz: {channel.name}")
            
        self.bridge.update_voice_channel(channel.name)
        return self.voice_client

    async def play_next(self):
        """Reproduce la siguiente cancion de la cola."""
        if not self.voice_client or not self.voice_client.is_connected():
            self.current_track = None
            self.bridge.update_current_song(None)
            return
            
        if len(self.queue) == 0:
            self.log("📭 La cola de reproducción está vacía.")
            self.current_track = None
            self.bridge.update_current_song(None)
            if self.voice_client.is_playing():
                self.voice_client.stop()
            return
            
        self.current_track = self.queue.pop(0)
        self.bridge.update_queue([t['title'] for t in self.queue])
        self.bridge.update_current_song(self.current_track)
        
        ffmpeg_path = os.path.abspath("ffmpeg.exe")
        if not os.path.exists(ffmpeg_path):
            # Fallback al path global si no está en la raíz
            ffmpeg_path = "ffmpeg"
            
        self.log(f"▶️ Reproduciendo ahora: {self.current_track['title']}")
        
        try:
            if self.current_track.get('is_local'):
                source = discord.FFmpegPCMAudio(self.current_track['url'], executable=ffmpeg_path)
            else:
                source = discord.FFmpegPCMAudio(self.current_track['url'], executable=ffmpeg_path, **FFMPEG_OPTIONS)
                
            volume_source = discord.PCMVolumeTransformer(source, volume=self.volume)
            
            import time
            self.track_start_time = time.time()
            self.track_paused_time = None
            self.total_paused_duration = 0
            
            def after_playing(error):
                if error:
                    self.log(f"⚠️ Error durante la reproducción: {error}")
                asyncio.run_coroutine_threadsafe(self.play_next(), self.loop)
                
            self.voice_client.play(volume_source, after=after_playing)
            
        except Exception as e:
            self.log(f"⚠️ Error al iniciar reproducción: {str(e)}")
            await self.play_next()

    async def play_song_query(self, query, voice_channel=None, requester="Sistema"):
        """Busca y añade una canción a la cola. Si no se está reproduciendo nada, la inicia."""
        track = await self.get_stream_source(query)
        if not track:
            self.log(f"❌ No se pudo encontrar ningún audio para: {query}")
            return False
            
        track['requester'] = requester
        self.queue.append(track)
        self.log(f"📥 Añadido a la cola: {track['title']} (por {requester})")
        self.bridge.update_queue([t['title'] for t in self.queue])
        
        if voice_channel:
            await self.join_voice_channel(voice_channel)
            
        if self.voice_client and not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_next()
            
        return True

    def add_commands(self):
        """Registra los comandos de chat para el bot en Discord."""
        
        @self.command(name="play", aliases=["p"])
        async def play(ctx, *, query: str):
            if not ctx.author.voice:
                await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
                return
                
            await ctx.send(f"🔍 Buscando: `{query}`...")
            success = await self.play_song_query(query, ctx.author.voice.channel, ctx.author.display_name)
            if success:
                await ctx.send(f"📥 Añadido a la cola: **{self.queue[-1]['title'] if self.queue else self.current_track['title']}**")
            else:
                await ctx.send("❌ No se encontró la canción o hubo un error.")
                
        @self.command(name="skip", aliases=["s"])
        async def skip(ctx):
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.stop()
                await ctx.send("⏭️ Canción saltada.")
                self.log(f"⏭️ Canción saltada por comando de {ctx.author.display_name}")
            else:
                await ctx.send("No hay ninguna canción reproduciéndose actualmente.")

        @self.command(name="pause")
        async def pause(ctx):
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.pause()
                import time
                self.track_paused_time = time.time()
                self.bridge.update_paused_state(True)
                await ctx.send("⏸️ Reproducción pausada.")
                self.log(f"⏸️ Pausado por comando de {ctx.author.display_name}")
            else:
                await ctx.send("No hay audio reproduciéndose.")

        @self.command(name="resume")
        async def resume(ctx):
            if self.voice_client and self.voice_client.is_paused():
                self.voice_client.resume()
                import time
                if self.track_paused_time:
                    self.total_paused_duration += time.time() - self.track_paused_time
                    self.track_paused_time = None
                self.bridge.update_paused_state(False)
                await ctx.send("▶️ Reproducción reanudada.")
                self.log(f"▶️ Reanudado por comando de {ctx.author.display_name}")
            else:
                await ctx.send("El bot no está pausado.")

        @self.command(name="stop")
        async def stop(ctx):
            self.queue.clear()
            self.bridge.update_queue([])
            self.track_start_time = None
            self.track_paused_time = None
            self.total_paused_duration = 0
            if self.voice_client:
                if self.voice_client.is_playing() or self.voice_client.is_paused():
                    self.voice_client.stop()
                await ctx.send("⏹️ Reproducción detenida y cola limpiada.")
                self.log(f"⏹️ Detenido por comando de {ctx.author.display_name}")
            else:
                await ctx.send("El bot no está conectado a un canal de voz.")

        @self.command(name="leave", aliases=["disconnect", "dc"])
        async def leave(ctx):
            self.track_start_time = None
            self.track_paused_time = None
            self.total_paused_duration = 0
            if self.voice_client:
                await self.voice_client.disconnect()
                self.voice_client = None
                self.current_track = None
                self.queue.clear()
                self.bridge.update_queue([])
                self.bridge.update_current_song(None)
                self.bridge.update_voice_channel(None)
                await ctx.send("👋 Desconectado del canal de voz.")
                self.log(f"👋 Desconectado por comando de {ctx.author.display_name}")
            else:
                await ctx.send("No estoy conectado a ningún canal de voz.")

        @self.command(name="volume", aliases=["vol"])
        async def volume(ctx, vol: int):
            if vol < 0 or vol > 100:
                await ctx.send("El volumen debe estar entre 0 y 100.")
                return
                
            self.volume = vol / 100.0
            if self.voice_client and self.voice_client.source:
                self.voice_client.source.volume = self.volume
            
            self.bridge.update_volume(self.volume)
            await ctx.send(f"🔊 Volumen ajustado a {vol}%.")
            self.log(f"🔊 Volumen ajustado a {vol}% por comando de {ctx.author.display_name}")

        @self.command(name="queue", aliases=["q"])
        async def show_queue(ctx):
            if not self.queue and not self.current_track:
                await ctx.send("La cola está vacía.")
                return
                
            msg = f"🎶 **Reproduciendo ahora:** {self.current_track['title']}\n"
            if self.queue:
                msg += "\n📋 **Próximas canciones:**\n"
                for idx, track in enumerate(self.queue[:10], 1):
                    msg += f"{idx}. {track['title']} (pedido por: {track['requester']})\n"
                if len(self.queue) > 10:
                    msg += f"... y {len(self.queue) - 10} canciones más."
            await ctx.send(msg)

    # Métodos llamados directamente por la GUI desde el hilo principal

    async def gui_play(self, query, channel_name=None):
        """Reproduce una canción iniciada desde la GUI."""
        if not self.guilds:
            self.log("⚠️ El bot no está en ningún servidor de Discord.")
            return
            
        guild = self.guilds[0] # Usar el primer servidor disponible
        
        # Buscar el canal de voz
        voice_channel = None
        if channel_name:
            voice_channel = discord.utils.get(guild.voice_channels, name=channel_name)
            
        if not voice_channel:
            # Si no se especifica o no se encuentra, buscar un canal donde haya miembros conectados
            # o simplemente tomar el primero
            for ch in guild.voice_channels:
                if len(ch.members) > 0:
                    voice_channel = ch
                    break
            if not voice_channel and guild.voice_channels:
                voice_channel = guild.voice_channels[0]
                
        if not voice_channel:
            self.log("⚠️ No se encontró ningún canal de voz disponible en el servidor.")
            return
            
        self.log(f"📥 Reproducción iniciada desde la GUI para: {query}")
        await self.play_song_query(query, voice_channel, "GUI Admin")

    async def gui_skip(self):
        """Salta la canción actual desde la GUI."""
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
            self.voice_client.stop()
            self.log("⏭️ Canción saltada desde la GUI.")

    async def gui_pause(self):
        """Pausa la canción desde la GUI."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            import time
            self.track_paused_time = time.time()
            self.bridge.update_paused_state(True)
            self.log("⏸️ Canción pausada desde la GUI.")

    async def gui_resume(self):
        """Reanuda la canción desde la GUI."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            import time
            if self.track_paused_time:
                self.total_paused_duration += time.time() - self.track_paused_time
                self.track_paused_time = None
            self.bridge.update_paused_state(False)
            self.log("▶️ Canción reanudada desde la GUI.")

    async def gui_stop(self):
        """Detiene y limpia la cola desde la GUI."""
        self.queue.clear()
        self.bridge.update_queue([])
        self.track_start_time = None
        self.track_paused_time = None
        self.total_paused_duration = 0
        if self.voice_client:
            self.voice_client.stop()
            self.log("⏹️ Reproducción detenida y cola limpiada desde la GUI.")

    async def gui_disconnect(self):
        """Desconecta el bot del canal de voz desde la GUI."""
        self.track_start_time = None
        self.track_paused_time = None
        self.total_paused_duration = 0
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.current_track = None
            self.queue.clear()
            self.bridge.update_queue([])
            self.bridge.update_current_song(None)
            self.bridge.update_voice_channel(None)
            self.log("👋 Desconectado del canal de voz desde la GUI.")

    async def gui_set_volume(self, vol_float):
        """Ajusta el volumen desde la GUI (vol_float entre 0.0 y 1.0)."""
        self.volume = vol_float
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = self.volume
        self.bridge.update_volume(self.volume)

    def get_elapsed_time(self):
        """Retorna el tiempo transcurrido de la cancion actual en segundos."""
        import time
        if not self.voice_client or (not self.voice_client.is_playing() and not self.voice_client.is_paused()):
            return 0
        if not self.track_start_time:
            return 0
        if self.voice_client.is_paused():
            return self.track_paused_time - self.track_start_time - self.total_paused_duration
        return time.time() - self.track_start_time - self.total_paused_duration
