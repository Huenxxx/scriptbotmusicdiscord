import os
import queue
import asyncio
import threading
import customtkinter as ctk
from tkinter import messagebox
import database
import discord


# Configurar apariencia de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BotBridge:
    def __init__(self):
        self.bot = None
        self.loop = None
        self.status = "offline"
        self.current_song = None
        self.queue = []
        self.voice_channel = None
        self.guilds = []
        self.volume = 0.5
        self.is_paused = False
        self.logs_queue = queue.Queue()
        self.state_updated = False

    def add_log(self, msg):
        self.logs_queue.put(msg)

    def update_status(self, status):
        self.status = status
        self.state_updated = True

    def update_guilds(self, guilds):
        self.guilds = guilds
        self.state_updated = True

    def update_voice_channel(self, vc_name):
        self.voice_channel = vc_name
        self.state_updated = True

    def update_queue(self, queue_list):
        self.queue = queue_list
        self.state_updated = True

    def update_current_song(self, song):
        self.current_song = song
        self.state_updated = True

    def update_paused_state(self, is_paused):
        self.is_paused = is_paused
        self.state_updated = True

    def update_volume(self, volume):
        self.volume = volume
        self.state_updated = True

class BotThread(threading.Thread):
    def __init__(self, token, prefix, bridge):
        super().__init__()
        self.token = token
        self.prefix = prefix
        self.bridge = bridge
        self.daemon = True

    def run(self):
        self.bridge.update_status("connecting")
        self.bridge.add_log("🚀 Iniciando bucle de eventos asíncronos para Discord...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.bridge.loop = loop
        
        from bot_client import DiscordMusicBot
        try:
            bot = DiscordMusicBot(self.token, self.prefix, self.bridge)
            self.bridge.bot = bot
            
            # Ejecutar bot hasta que sea cerrado
            loop.run_until_complete(bot.start(self.token))
        except discord.errors.LoginFailure:
            self.bridge.add_log("❌ Error: El token del bot no es válido. Comprueba el token e inténtalo de nuevo.")
            self.bridge.update_status("offline")
        except Exception as e:
            self.bridge.add_log(f"⚠️ Error en ejecución del bot: {str(e)}")
            self.bridge.update_status("offline")
        finally:
            self.bridge.add_log("💤 El hilo del bot de Discord ha finalizado.")
            self.bridge.update_status("offline")
            self.bridge.bot = None
            self.bridge.loop = None
            # Cerrar el loop de forma limpia
            try:
                loop.close()
            except Exception:
                pass

class ScriptBotStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ScriptBot Studio - Discord Manager")
        self.geometry("1000x650")
        self.minsize(900, 600)
        
        self.current_user_id = None
        self.current_username = None
        self.active_bot_data = None  # Almacena el bot seleccionado
        self.bridge = BotBridge()
        self.bot_thread = None
        
        # Inicializar base de datos
        database.init_db()
        
        # Contenedor principal para cambiar de vistas
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()
        
        # Iniciar polling para logs y actualizaciones del bot
        self.poll_bot_updates()
        
        # Manejar cierre seguro de la ventana
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- PANTALLAS DE AUTENTICACION ---

    def show_login(self):
        self.clear_container()
        
        # Frame central centrado
        login_frame = ctk.CTkFrame(self.container, width=400, height=450, corner_radius=15)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        login_frame.pack_propagate(False)
        
        # Titulo y Logo alternativo
        logo_label = ctk.CTkLabel(login_frame, text="ScriptBot Studio", font=ctk.CTkFont(family="Outfit", size=26, weight="bold"), text_color="#3b82f6")
        logo_label.pack(pady=(40, 5))
        
        subtitle_label = ctk.CTkLabel(login_frame, text="Gestor Local de Bots de Discord", font=ctk.CTkFont(size=12), text_color="gray")
        subtitle_label.pack(pady=(0, 25))
        
        # Campos
        self.username_entry = ctk.CTkEntry(login_frame, width=280, placeholder_text="Nombre de usuario", height=38)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(login_frame, width=280, placeholder_text="Contraseña", show="*", height=38)
        self.password_entry.pack(pady=10)
        
        # Boton Ingresar
        login_btn = ctk.CTkButton(login_frame, text="Iniciar Sesión", width=280, height=40, font=ctk.CTkFont(weight="bold"), command=self.handle_login)
        login_btn.pack(pady=20)
        
        # Enlace a registro
        register_link = ctk.CTkLabel(login_frame, text="¿No tienes cuenta? Regístrate aquí", font=ctk.CTkFont(size=12, underline=True), cursor="hand2")
        register_link.pack(pady=10)
        register_link.bind("<Button-1>", lambda e: self.show_register())

    def show_register(self):
        self.clear_container()
        
        register_frame = ctk.CTkFrame(self.container, width=400, height=480, corner_radius=15)
        register_frame.place(relx=0.5, rely=0.5, anchor="center")
        register_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(register_frame, text="Crear Cuenta Local", font=ctk.CTkFont(family="Outfit", size=24, weight="bold"), text_color="#3b82f6")
        logo_label.pack(pady=(35, 5))
        
        subtitle_label = ctk.CTkLabel(register_frame, text="Tus tokens y bots se guardarán cifrados en tu PC.", font=ctk.CTkFont(size=11), text_color="gray")
        subtitle_label.pack(pady=(0, 25))
        
        self.reg_username_entry = ctk.CTkEntry(register_frame, width=280, placeholder_text="Nuevo usuario", height=38)
        self.reg_username_entry.pack(pady=8)
        
        self.reg_password_entry = ctk.CTkEntry(register_frame, width=280, placeholder_text="Contraseña", show="*", height=38)
        self.reg_password_entry.pack(pady=8)
        
        self.reg_confirm_entry = ctk.CTkEntry(register_frame, width=280, placeholder_text="Confirmar contraseña", show="*", height=38)
        self.reg_confirm_entry.pack(pady=8)
        
        register_btn = ctk.CTkButton(register_frame, text="Registrarse", width=280, height=40, font=ctk.CTkFont(weight="bold"), command=self.handle_register, fg_color="#10b981", hover_color="#059669")
        register_btn.pack(pady=20)
        
        login_link = ctk.CTkLabel(register_frame, text="¿Ya tienes cuenta? Inicia sesión", font=ctk.CTkFont(size=12, underline=True), cursor="hand2")
        login_link.pack(pady=10)
        login_link.bind("<Button-1>", lambda e: self.show_login())

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user_id = database.login_user(username, password)
        if user_id:
            self.current_user_id = user_id
            self.current_username = username.strip()
            self.show_dashboard()
        else:
            messagebox.showerror("Error de acceso", "Usuario o contraseña incorrectos.")

    def handle_register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
            
        success, message = database.register_user(username, password)
        if success:
            messagebox.showinfo("Éxito", message)
            self.show_login()
        else:
            messagebox.showerror("Error", message)

    # --- DASHBOARD (GESTOR DE BOTS) ---

    def show_dashboard(self):
        self.clear_container()
        
        # Grid layout: Sidebar (200px) y Contenido principal
        self.container.grid_columnconfigure(0, weight=0, minsize=220)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # --- SIDEBAR ---
        sidebar = ctk.CTkFrame(self.container, corner_radius=0, width=220, fg_color="#0f172a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        
        title_lbl = ctk.CTkLabel(sidebar, text="ScriptBot Studio", font=ctk.CTkFont(family="Outfit", size=20, weight="bold"), text_color="#3b82f6")
        title_lbl.grid(row=0, column=0, pady=(30, 5), padx=20, sticky="w")
        
        user_lbl = ctk.CTkLabel(sidebar, text=f"👤 Sesión: {self.current_username}", font=ctk.CTkFont(size=12), text_color="lightgray")
        user_lbl.grid(row=1, column=0, pady=(0, 30), padx=20, sticky="w")
        
        # Boton Cerrar Sesion
        logout_btn = ctk.CTkButton(sidebar, text="Cerrar Sesión", fg_color="#ef4444", hover_color="#dc2626", height=32, command=self.handle_logout)
        logout_btn.grid(row=5, column=0, pady=20, padx=20, sticky="ew")
        
        # --- CONTENIDO PRINCIPAL ---
        main_content = ctk.CTkFrame(self.container, corner_radius=0, fg_color="#1e293b")
        main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=0, minsize=320) # Formulario
        main_content.grid_rowconfigure(0, weight=1)
        
        # --- COLUMNA BOTS REGISTRADOS ---
        bots_list_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        bots_list_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        bots_list_frame.grid_columnconfigure(0, weight=1)
        bots_list_frame.grid_rowconfigure(1, weight=1)
        
        section_title = ctk.CTkLabel(bots_list_frame, text="Mis Bots de Discord", font=ctk.CTkFont(size=18, weight="bold"))
        section_title.grid(row=0, column=0, pady=(0, 15), sticky="w")
        
        # Frame desplazable para la lista de bots
        self.scrollable_bots = ctk.CTkScrollableFrame(bots_list_frame, fg_color="#0f172a")
        self.scrollable_bots.grid(row=1, column=0, sticky="nsew")
        self.scrollable_bots.columnconfigure(0, weight=1)
        
        self.load_bots_list()
        
        # --- COLUMNA FORMULARIO CREAR BOT ---
        form_frame = ctk.CTkFrame(main_content, fg_color="#0f172a", width=300, corner_radius=10)
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        form_frame.pack_propagate(False)
        
        form_title = ctk.CTkLabel(form_frame, text="Añadir Nuevo Bot", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3b82f6")
        form_title.pack(pady=(20, 15))
        
        self.bot_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Nombre del bot (ej: Música 24/7)", width=250)
        self.bot_name_entry.pack(pady=10)
        
        self.bot_token_entry = ctk.CTkEntry(form_frame, placeholder_text="Token del Bot de Discord", width=250, show="*")
        self.bot_token_entry.pack(pady=10)
        
        self.bot_prefix_entry = ctk.CTkEntry(form_frame, placeholder_text="Prefijo de comandos (por defecto: !)", width=250)
        self.bot_prefix_entry.pack(pady=10)
        
        add_btn = ctk.CTkButton(form_frame, text="Registrar Bot", command=self.handle_add_bot, width=250, fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(weight="bold"))
        add_btn.pack(pady=25)

    def load_bots_list(self):
        # Limpiar
        for widget in self.scrollable_bots.winfo_children():
            widget.destroy()
            
        bots = database.get_bots(self.current_user_id)
        if not bots:
            no_bots_lbl = ctk.CTkLabel(self.scrollable_bots, text="Aún no tienes bots registrados.\nUsa el panel de la derecha para añadir uno.", font=ctk.CTkFont(size=12), text_color="gray")
            no_bots_lbl.pack(pady=50)
            return
            
        for idx, bot in enumerate(bots):
            bot_card = ctk.CTkFrame(self.scrollable_bots, fg_color="#1e293b", height=80, corner_radius=8)
            bot_card.pack(fill="x", pady=6, padx=10)
            bot_card.pack_propagate(False)
            
            # Nombre e informacion
            info_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, fill="y", pady=10)
            
            b_name = ctk.CTkLabel(info_frame, text=bot["name"], font=ctk.CTkFont(size=15, weight="bold"))
            b_name.pack(anchor="w")
            
            b_details = ctk.CTkLabel(info_frame, text=f"Prefijo: '{bot['prefix']}'  •  Token: {bot['token'][:10]}...", font=ctk.CTkFont(size=11), text_color="gray")
            b_details.pack(anchor="w")
            
            # Botones de Accion
            actions_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
            actions_frame.pack(side="right", padx=15)
            
            # Pasar bot en lambda para guardar referencia local
            manage_btn = ctk.CTkButton(actions_frame, text="Gestionar", width=80, height=28, command=lambda b=bot: self.select_bot(b))
            manage_btn.pack(side="left", padx=5)
            
            delete_btn = ctk.CTkButton(actions_frame, text="Eliminar", width=60, height=28, fg_color="#ef4444", hover_color="#dc2626", command=lambda bid=bot["id"]: self.handle_delete_bot(bid))
            delete_btn.pack(side="left", padx=5)

    def handle_add_bot(self):
        name = self.bot_name_entry.get()
        token = self.bot_token_entry.get()
        prefix = self.bot_prefix_entry.get() or "!"
        
        success, message = database.add_bot(self.current_user_id, name, token, prefix)
        if success:
            messagebox.showinfo("Éxito", message)
            self.bot_name_entry.delete(0, "end")
            self.bot_token_entry.delete(0, "end")
            self.bot_prefix_entry.delete(0, "end")
            self.load_bots_list()
        else:
            messagebox.showerror("Error", message)

    def handle_delete_bot(self, bot_id):
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este bot?"):
            if database.delete_bot(bot_id, self.current_user_id):
                self.load_bots_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el bot.")

    def select_bot(self, bot_data):
        self.active_bot_data = bot_data
        self.show_bot_controls()

    def handle_logout(self):
        self.on_closing_bot() # Asegurarse de apagar el bot
        self.current_user_id = None
        self.current_username = None
        self.active_bot_data = None
        self.show_login()

    # --- PANEL DE CONTROL DEL BOT (MUSICA & LOGS) ---

    def show_bot_controls(self):
        self.clear_container()
        
        # Grid layout: Sidebar (bot info y encendido) y Zona de trabajo (Música y Logs)
        self.container.grid_columnconfigure(0, weight=0, minsize=220)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # --- SIDEBAR DEL BOT ---
        bot_sidebar = ctk.CTkFrame(self.container, corner_radius=0, width=220, fg_color="#0f172a")
        bot_sidebar.grid(row=0, column=0, sticky="nsew")
        bot_sidebar.grid_rowconfigure(6, weight=1)
        
        back_btn = ctk.CTkButton(bot_sidebar, text="◀ Dashboard", fg_color="gray", hover_color="#4b5563", height=28, command=self.go_to_dashboard)
        back_btn.grid(row=0, column=0, pady=(20, 20), padx=20, sticky="w")
        
        # Nombre del bot activo
        active_bot_title = ctk.CTkLabel(bot_sidebar, text=self.active_bot_data["name"], font=ctk.CTkFont(family="Outfit", size=18, weight="bold"), text_color="#3b82f6")
        active_bot_title.grid(row=1, column=0, padx=20, sticky="w")
        
        prefix_lbl = ctk.CTkLabel(bot_sidebar, text=f"Prefijo: '{self.active_bot_data['prefix']}'", font=ctk.CTkFont(size=12), text_color="gray")
        prefix_lbl.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Estado de conexión
        status_frame = ctk.CTkFrame(bot_sidebar, fg_color="transparent")
        status_frame.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.status_dot = ctk.CTkLabel(status_frame, text="●", font=ctk.CTkFont(size=18), text_color="red")
        self.status_dot.pack(side="left")
        
        self.status_txt = ctk.CTkLabel(status_frame, text="Desconectado", font=ctk.CTkFont(weight="bold"))
        self.status_txt.pack(side="left", padx=5)
        
        # Canales de Voz y Servidores
        self.guilds_count_lbl = ctk.CTkLabel(bot_sidebar, text="Servidores: 0", font=ctk.CTkFont(size=12), text_color="lightgray")
        self.guilds_count_lbl.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.vc_channel_lbl = ctk.CTkLabel(bot_sidebar, text="Canal de voz: Ninguno", font=ctk.CTkFont(size=12), text_color="lightgray")
        self.vc_channel_lbl.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        # Controles Encendido / Apagado
        power_frame = ctk.CTkFrame(bot_sidebar, fg_color="transparent")
        power_frame.grid(row=7, column=0, pady=20, padx=20, sticky="ew")
        
        self.start_bot_btn = ctk.CTkButton(power_frame, text="Iniciar Bot", fg_color="#10b981", hover_color="#059669", height=38, command=self.toggle_bot_power)
        self.start_bot_btn.pack(fill="x", pady=5)
        
        # --- ZONA DE TRABAJO (MÚSICA & CONSOLA) ---
        bot_workspace = ctk.CTkFrame(self.container, corner_radius=0, fg_color="#1e293b")
        bot_workspace.grid(row=0, column=1, sticky="nsew")
        bot_workspace.grid_columnconfigure(0, weight=1)
        bot_workspace.grid_rowconfigure(0, weight=3) # Música
        bot_workspace.grid_rowconfigure(1, weight=2) # Consola
        
        # --- PANEL DE MÚSICA ---
        music_panel = ctk.CTkFrame(bot_workspace, fg_color="transparent")
        music_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        music_panel.grid_columnconfigure(0, weight=1) # Controles
        music_panel.grid_columnconfigure(1, weight=1) # Cola
        music_panel.grid_rowconfigure(0, weight=1)
        
        # 1. Controles y Reproductor
        player_frame = ctk.CTkFrame(music_panel, fg_color="#0f172a", corner_radius=10)
        player_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        player_frame.pack_propagate(False)
        
        p_title = ctk.CTkLabel(player_frame, text="Reproductor de Música", font=ctk.CTkFont(size=15, weight="bold"), text_color="#3b82f6")
        p_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Entrada para buscar/URL
        search_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=5)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar canción en YouTube o pegar URL...", height=35)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.gui_action_play())
        
        play_btn = ctk.CTkButton(search_frame, text="Play", width=60, height=35, fg_color="#3b82f6", hover_color="#2563eb", command=self.gui_action_play)
        play_btn.pack(side="left", padx=(5, 0))
        
        # Canción sonando ahora
        self.now_playing_frame = ctk.CTkFrame(player_frame, fg_color="#1e293b", height=80, corner_radius=6)
        self.now_playing_frame.pack(fill="x", padx=15, pady=15)
        self.now_playing_frame.pack_propagate(False)
        
        self.song_title_lbl = ctk.CTkLabel(self.now_playing_frame, text="Ninguna canción reproduciéndose", font=ctk.CTkFont(size=13, weight="bold"), wraplength=300)
        self.song_title_lbl.pack(pady=(15, 2), padx=10)
        
        self.song_meta_lbl = ctk.CTkLabel(self.now_playing_frame, text="-", font=ctk.CTkFont(size=11), text_color="gray")
        self.song_meta_lbl.pack(pady=0)
        
        # Controles
        ctrl_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        ctrl_frame.pack(pady=10)
        
        self.pause_btn = ctk.CTkButton(ctrl_frame, text="⏸ Pausa", width=80, height=32, command=self.gui_action_pause)
        self.pause_btn.pack(side="left", padx=5)
        
        skip_btn = ctk.CTkButton(ctrl_frame, text="⏭ Skip", width=80, height=32, command=self.gui_action_skip)
        skip_btn.pack(side="left", padx=5)
        
        stop_btn = ctk.CTkButton(ctrl_frame, text="⏹ Stop", width=80, height=32, fg_color="#ef4444", hover_color="#dc2626", command=self.gui_action_stop)
        stop_btn.pack(side="left", padx=5)
        
        dc_btn = ctk.CTkButton(ctrl_frame, text="👋 Salir", width=70, height=32, fg_color="gray", hover_color="#4b5563", command=self.gui_action_disconnect)
        dc_btn.pack(side="left", padx=5)
        
        # Slider de Volumen
        vol_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        vol_frame.pack(fill="x", padx=25, pady=15)
        
        vol_lbl = ctk.CTkLabel(vol_frame, text="🔊 Volumen:", font=ctk.CTkFont(size=12))
        vol_lbl.pack(side="left", padx=5)
        
        self.vol_slider = ctk.CTkSlider(vol_frame, from_=0, to=100, number_of_steps=100, command=self.gui_action_volume)
        self.vol_slider.set(50)
        self.vol_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # 2. Cola de Reproducción
        queue_frame = ctk.CTkFrame(music_panel, fg_color="#0f172a", corner_radius=10)
        queue_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        queue_frame.grid_columnconfigure(0, weight=1)
        queue_frame.grid_rowconfigure(1, weight=1)
        
        q_title = ctk.CTkLabel(queue_frame, text="Cola de Reproducción", font=ctk.CTkFont(size=15, weight="bold"), text_color="#3b82f6")
        q_title.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Lista desplazable de canciones en cola
        self.scrollable_queue = ctk.CTkScrollableFrame(queue_frame, fg_color="#1e293b", corner_radius=6)
        self.scrollable_queue.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.update_queue_ui([])
        
        # --- CONSOLA DE LOGS ---
        console_panel = ctk.CTkFrame(bot_workspace, fg_color="#0f172a", corner_radius=10)
        console_panel.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        console_panel.grid_columnconfigure(0, weight=1)
        console_panel.grid_rowconfigure(1, weight=1)
        
        c_title = ctk.CTkLabel(console_panel, text="Consola de Logs en Tiempo Real", font=ctk.CTkFont(size=13, weight="bold"), text_color="gray")
        c_title.grid(row=0, column=0, pady=(8, 4), padx=15, sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(console_panel, fg_color="#090d16", font=ctk.CTkFont(family="Consolas", size=11), text_color="#a7f3d0")
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.log_textbox.configure(state="disabled")

    def go_to_dashboard(self):
        # Advertencia si se sale mientras el bot corre
        if self.bridge.status in ["online", "connecting"]:
            if not messagebox.askyesno("Confirmar", "El bot sigue ejecutándose en segundo plano. ¿Volver al Dashboard?"):
                return
        self.show_dashboard()

    def toggle_bot_power(self):
        if self.bridge.status == "offline":
            # Iniciar bot
            token = self.active_bot_data["token"]
            prefix = self.active_bot_data["prefix"]
            
            # Limpiar terminal de logs
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")
            
            self.bot_thread = BotThread(token, prefix, self.bridge)
            self.bot_thread.start()
            
            self.start_bot_btn.configure(text="Apagar Bot", fg_color="#ef4444", hover_color="#dc2626")
        else:
            # Apagar bot
            self.on_closing_bot()

    def on_closing_bot(self):
        if self.bridge.status in ["online", "connecting"] and self.bridge.bot and self.bridge.loop:
            self.bridge.add_log("🔌 Apagando bot de Discord de forma segura...")
            asyncio.run_coroutine_threadsafe(self.bridge.bot.close(), self.bridge.loop)
        
        self.start_bot_btn.configure(text="Iniciar Bot", fg_color="#10b981", hover_color="#059669")

    # --- ACCIONES DE MUSICA DESDE LA GUI (HILO SEGURO) ---

    def gui_action_play(self):
        query = self.search_entry.get().strip()
        if not query:
            return
            
        if self.bridge.status != "online" or not self.bridge.bot:
            messagebox.showwarning("Advertencia", "El bot debe estar encendido (Online) para reproducir música.")
            return
            
        self.search_entry.delete(0, "end")
        asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_play(query), self.bridge.loop)

    def gui_action_skip(self):
        if self.bridge.status == "online" and self.bridge.bot:
            asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_skip(), self.bridge.loop)

    def gui_action_pause(self):
        if self.bridge.status == "online" and self.bridge.bot:
            if self.bridge.is_paused:
                asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_resume(), self.bridge.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_pause(), self.bridge.loop)

    def gui_action_stop(self):
        if self.bridge.status == "online" and self.bridge.bot:
            asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_stop(), self.bridge.loop)

    def gui_action_disconnect(self):
        if self.bridge.status == "online" and self.bridge.bot:
            asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_disconnect(), self.bridge.loop)

    def gui_action_volume(self, value):
        if self.bridge.status == "online" and self.bridge.bot:
            vol = float(value) / 100.0
            asyncio.run_coroutine_threadsafe(self.bridge.bot.gui_set_volume(vol), self.bridge.loop)

    # --- POLLING Y ACTUALIZACIONES DE UI ---

    def poll_bot_updates(self):
        """Metodo periodico que lee la cola de logs y cambios de estado del hilo del bot."""
        # 1. Procesar Logs
        log_msgs = []
        while True:
            try:
                msg = self.bridge.logs_queue.get_nowait()
                log_msgs.append(msg)
            except queue.Empty:
                break
                
        if log_msgs and hasattr(self, "log_textbox") and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            for msg in log_msgs:
                self.log_textbox.insert("end", f"{msg}\n")
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")
            
        # 2. Procesar cambios de estado
        if self.bridge.state_updated:
            self.bridge.state_updated = False
            self.update_bot_ui_state()
            
        # Ejecutar de nuevo cada 100ms
        self.after(100, self.poll_bot_updates)

    def update_bot_ui_state(self):
        """Actualiza los componentes visuales de la interfaz de control según el estado actual del bot."""
        if not hasattr(self, "status_dot") or not self.status_dot.winfo_exists():
            return
            
        # Estado de conexión
        status = self.bridge.status
        if status == "online":
            self.status_dot.configure(text_color="#10b981")
            self.status_txt.configure(text="Conectado")
            self.start_bot_btn.configure(text="Apagar Bot", fg_color="#ef4444", hover_color="#dc2626", state="normal")
        elif status == "connecting":
            self.status_dot.configure(text_color="#fbbf24")
            self.status_txt.configure(text="Conectando...")
            self.start_bot_btn.configure(text="Iniciando...", state="disabled")
        else: # offline
            self.status_dot.configure(text_color="#ef4444")
            self.status_txt.configure(text="Desconectado")
            self.start_bot_btn.configure(text="Iniciar Bot", fg_color="#10b981", hover_color="#059669", state="normal")
            self.guilds_count_lbl.configure(text="Servidores: 0")
            self.vc_channel_lbl.configure(text="Canal de voz: Ninguno")
            self.update_queue_ui([])
            self.song_title_lbl.configure(text="Ninguna canción reproduciéndose")
            self.song_meta_lbl.configure(text="-")
            return
            
        # Servidores
        self.guilds_count_lbl.configure(text=f"Servidores: {len(self.bridge.guilds)}")
        
        # Canal de voz
        vc = self.bridge.voice_channel
        self.vc_channel_lbl.configure(text=f"Canal de voz: {vc or 'Ninguno'}")
        
        # Canción actual sonando
        song = self.bridge.current_song
        if song:
            self.song_title_lbl.configure(text=song["title"])
            duration_str = f"{song['duration'] // 60}:{song['duration'] % 60:02d}" if song['duration'] else "Directo"
            req = song.get("requester", "Desconocido")
            self.song_meta_lbl.configure(text=f"Duración: {duration_str}  •  Pedido por: {req}")
        else:
            self.song_title_lbl.configure(text="Ninguna canción reproduciéndose")
            self.song_meta_lbl.configure(text="-")
            
        # Boton de Pausa / Reanudar
        if self.bridge.is_paused:
            self.pause_btn.configure(text="▶ Reanudar", fg_color="#fbbf24", hover_color="#d97706")
        else:
            self.pause_btn.configure(text="⏸ Pausa", fg_color="#3b82f6", hover_color="#2563eb")
            
        # Ajustar slider de volumen si cambió externamente
        self.vol_slider.set(self.bridge.volume * 100)
        
        # Actualizar lista de cola
        self.update_queue_ui(self.bridge.queue)

    def update_queue_ui(self, queue_list):
        for widget in self.scrollable_queue.winfo_children():
            widget.destroy()
            
        if not queue_list:
            empty_lbl = ctk.CTkLabel(self.scrollable_queue, text="Cola vacía", text_color="gray")
            empty_lbl.pack(pady=30)
            return
            
        for idx, title in enumerate(queue_list, 1):
            q_item = ctk.CTkFrame(self.scrollable_queue, fg_color="#0f172a", height=35, corner_radius=4)
            q_item.pack(fill="x", pady=3, padx=5)
            q_item.pack_propagate(False)
            
            lbl = ctk.CTkLabel(q_item, text=f"{idx}. {title}", font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(side="left", padx=10, fill="both", expand=True)

    # --- CIERRE SEGURO ---

    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres cerrar ScriptBot Studio?"):
            self.on_closing_bot()
            self.destroy()
