import os
import queue
import asyncio
import threading
import json
import base64
import urllib.request
import urllib.parse
import customtkinter as ctk
from tkinter import messagebox
import database
import discord
import colorsys

# Configurar apariencia de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Fuentes globales premium
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_BODY = ("Segoe UI", 12)
FONT_BODY_BOLD = ("Segoe UI", 12, "bold")

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
        self.amplitude = 0.0

    def update_amplitude(self, amp):
        self.amplitude = amp

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
            try:
                loop.close()
            except Exception:
                pass

class ScriptBotStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ScriptBot Studio - Discord Manager")
        self.geometry("1020x680")
        self.minsize(920, 620)
        self.configure(fg_color="#090d16") # Fondo oscuro premium
        
        self.current_user_id = None
        self.current_username = None
        self.active_bot_data = None  
        self.bridge = BotBridge()
        self.bot_thread = None
        self.last_song_title = None
        self.current_song_lrc = []
        self.lyrics_offset = 0.0
        self.visual_amplitude = 0.0
        self.song_color_base = "#a5b4fc"
        self.song_color_punch = "#f43f5e"
        self.lyrics_hue = 0.0
        self.in_lyric_transition = False
        self.last_curr_line = ""
        
        # Inicializar base de datos
        database.init_db()
        
        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        self.show_login()
        
        # Iniciar polling para logs
        self.poll_bot_updates()
        
        # Cierre seguro
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- LÓGICA DE RECORDAR CUENTA ---

    def save_remember_credentials(self, username, password):
        data = {
            "username": username,
            "password_obf": base64.b64encode(password.encode("utf-8")).decode("utf-8"),
            "remember": True
        }
        try:
            with open("remember.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al guardar credenciales recordadas: {e}")

    def load_remember_credentials(self):
        if os.path.exists("remember.json"):
            try:
                with open("remember.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("remember"):
                        username = data.get("username")
                        pw_obf = data.get("password_obf")
                        password = base64.b64decode(pw_obf.encode("utf-8")).decode("utf-8")
                        return username, password
            except Exception as e:
                print(f"Error al cargar credenciales recordadas: {e}")
        return None, None

    # --- PANTALLAS DE AUTENTICACION ---

    def show_login(self):
        self.clear_container()
        
        # Reset grid layout
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Frame central centrado
        login_frame = ctk.CTkFrame(self.container, width=420, height=480, corner_radius=15, fg_color="#131d30")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        login_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(login_frame, text="ScriptBot Studio", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color="#5850ec")
        logo_label.pack(pady=(45, 5))
        
        subtitle_label = ctk.CTkLabel(login_frame, text="Gestor Local de Bots de Discord", font=FONT_SUBTITLE, text_color="#94a3b8")
        subtitle_label.pack(pady=(0, 25))
        
        # Campos
        self.username_entry = ctk.CTkEntry(login_frame, width=300, placeholder_text="Nombre de usuario", height=40, fg_color="#090d16", border_color="#1e293b")
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(login_frame, width=300, placeholder_text="Contraseña", show="*", height=40, fg_color="#090d16", border_color="#1e293b")
        self.password_entry.pack(pady=10)
        
        # Checkbox Recordar cuenta
        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_cb = ctk.CTkCheckBox(login_frame, text="Recordar cuenta", variable=self.remember_var, font=FONT_SUBTITLE, text_color="#94a3b8")
        self.remember_cb.pack(pady=5)
        
        # Boton Ingresar
        login_btn = ctk.CTkButton(login_frame, text="Iniciar Sesión", width=300, height=42, fg_color="#5850ec", hover_color="#4f46e5", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), command=self.handle_login)
        login_btn.pack(pady=15)
        self.apply_fade_hover(login_btn, "#5850ec", "#4f46e5")
        
        # Enlace a registro
        register_link = ctk.CTkLabel(login_frame, text="¿No tienes cuenta? Regístrate aquí", font=ctk.CTkFont(family="Segoe UI", size=12, underline=True), text_color="#94a3b8", cursor="hand2")
        register_link.pack(pady=8)
        register_link.bind("<Button-1>", lambda e: self.switch_screen_with_fade(self.show_register))
        
        # Intentar cargar credenciales recordadas
        saved_user, saved_pw = self.load_remember_credentials()
        if saved_user and saved_pw:
            self.remember_var.set(True)
            self.username_entry.insert(0, saved_user)
            self.password_entry.insert(0, saved_pw)

    def show_register(self):
        self.clear_container()
        
        register_frame = ctk.CTkFrame(self.container, width=420, height=480, corner_radius=15, fg_color="#131d30")
        register_frame.place(relx=0.5, rely=0.5, anchor="center")
        register_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(register_frame, text="Crear Cuenta Local", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color="#5850ec")
        logo_label.pack(pady=(35, 5))
        
        subtitle_label = ctk.CTkLabel(register_frame, text="Tus tokens y bots se guardarán cifrados en tu PC.", font=FONT_SUBTITLE, text_color="#94a3b8")
        subtitle_label.pack(pady=(0, 25))
        
        self.reg_username_entry = ctk.CTkEntry(register_frame, width=300, placeholder_text="Nuevo usuario", height=40, fg_color="#090d16", border_color="#1e293b")
        self.reg_username_entry.pack(pady=8)
        
        self.reg_password_entry = ctk.CTkEntry(register_frame, width=300, placeholder_text="Contraseña", show="*", height=40, fg_color="#090d16", border_color="#1e293b")
        self.reg_password_entry.pack(pady=8)
        
        self.reg_confirm_entry = ctk.CTkEntry(register_frame, width=300, placeholder_text="Confirmar contraseña", show="*", height=40, fg_color="#090d16", border_color="#1e293b")
        self.reg_confirm_entry.pack(pady=8)
        
        register_btn = ctk.CTkButton(register_frame, text="Registrarse", width=300, height=42, fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), command=self.handle_register)
        register_btn.pack(pady=18)
        self.apply_fade_hover(register_btn, "#10b981", "#059669")
        
        login_link = ctk.CTkLabel(register_frame, text="¿Ya tienes cuenta? Inicia sesión", font=ctk.CTkFont(family="Segoe UI", size=12, underline=True), text_color="#94a3b8", cursor="hand2")
        login_link.pack(pady=10)
        login_link.bind("<Button-1>", lambda e: self.switch_screen_with_fade(self.show_login))

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        user_id = database.login_user(username, password)
        if user_id:
            self.current_user_id = user_id
            self.current_username = username
            
            # Gestionar recordar cuenta
            if self.remember_var.get():
                self.save_remember_credentials(username, password)
            else:
                if os.path.exists("remember.json"):
                    try:
                        os.remove("remember.json")
                    except Exception:
                        pass
                        
            self.switch_screen_with_fade(self.show_dashboard)
        else:
            messagebox.showerror("Error de acceso", "Usuario o contraseña incorrectos.")

    def handle_register(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Los campos no pueden estar vacíos.")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
            
        success, message = database.register_user(username, password)
        if success:
            messagebox.showinfo("Éxito", message)
            self.switch_screen_with_fade(self.show_login)
        else:
            messagebox.showerror("Error", message)

    # --- DASHBOARD (GESTOR DE BOTS) ---

    def show_dashboard(self):
        self.clear_container()
        
        # Grid layout: Sidebar (220px) y Contenido principal
        self.container.grid_columnconfigure(0, weight=0, minsize=220)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # --- SIDEBAR ---
        sidebar = ctk.CTkFrame(self.container, corner_radius=0, width=220, fg_color="#0f172a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        
        title_lbl = ctk.CTkLabel(sidebar, text="ScriptBot Studio", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="#5850ec")
        title_lbl.grid(row=0, column=0, pady=(30, 5), padx=20, sticky="w")
        
        user_lbl = ctk.CTkLabel(sidebar, text=f"👤 Sesión: {self.current_username}", font=FONT_SUBTITLE, text_color="#94a3b8")
        user_lbl.grid(row=1, column=0, pady=(0, 30), padx=20, sticky="w")
        
        # Boton Cerrar Sesion
        logout_btn = ctk.CTkButton(sidebar, text="Cerrar Sesión", fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), height=32, command=self.handle_logout)
        logout_btn.grid(row=5, column=0, pady=20, padx=20, sticky="ew")
        self.apply_fade_hover(logout_btn, "#ef4444", "#dc2626")
        
        # --- CONTENIDO PRINCIPAL ---
        main_content = ctk.CTkFrame(self.container, corner_radius=0, fg_color="#090d16")
        main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=0, minsize=320) # Formulario a la derecha
        main_content.grid_rowconfigure(0, weight=1)
        
        # --- COLUMNA BOTS REGISTRADOS ---
        bots_list_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        bots_list_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        bots_list_frame.grid_columnconfigure(0, weight=1)
        bots_list_frame.grid_rowconfigure(1, weight=1)
        
        section_title = ctk.CTkLabel(bots_list_frame, text="Mis Bots de Discord", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#f1f5f9")
        section_title.grid(row=0, column=0, pady=(0, 15), sticky="w")
        
        self.scrollable_bots = ctk.CTkScrollableFrame(bots_list_frame, fg_color="#131d30", border_color="#1e293b")
        self.scrollable_bots.grid(row=1, column=0, sticky="nsew")
        self.scrollable_bots.columnconfigure(0, weight=1)
        
        self.load_bots_list()
        
        # --- COLUMNA FORMULARIO CREAR BOT ---
        form_frame = ctk.CTkFrame(main_content, fg_color="#131d30", width=300, corner_radius=12)
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        form_frame.pack_propagate(False)
        
        form_title = ctk.CTkLabel(form_frame, text="Añadir Nuevo Bot", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#5850ec")
        form_title.pack(pady=(20, 15))
        
        self.bot_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Nombre del bot (ej: Música)", width=250, fg_color="#090d16")
        self.bot_name_entry.pack(pady=10)
        
        self.bot_token_entry = ctk.CTkEntry(form_frame, placeholder_text="Token del Bot de Discord", width=250, show="*", fg_color="#090d16")
        self.bot_token_entry.pack(pady=10)
        
        self.bot_prefix_entry = ctk.CTkEntry(form_frame, placeholder_text="Prefijo (ej: !)", width=250, fg_color="#090d16")
        self.bot_prefix_entry.pack(pady=10)
        
        add_btn = ctk.CTkButton(form_frame, text="Registrar Bot", command=self.handle_add_bot, width=250, fg_color="#5850ec", hover_color="#4f46e5", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), height=38)
        add_btn.pack(pady=25)
        self.apply_fade_hover(add_btn, "#5850ec", "#4f46e5")

    def load_bots_list(self):
        for widget in self.scrollable_bots.winfo_children():
            widget.destroy()
            
        bots = database.get_bots(self.current_user_id)
        if not bots:
            no_bots_lbl = ctk.CTkLabel(self.scrollable_bots, text="Aún no tienes bots registrados.\nUsa el panel de la derecha para añadir uno.", font=FONT_SUBTITLE, text_color="gray")
            no_bots_lbl.pack(pady=70)
            return
            
        for idx, bot in enumerate(bots):
            bot_card = ctk.CTkFrame(self.scrollable_bots, fg_color="#1c283d", height=80, corner_radius=8)
            bot_card.pack(fill="x", pady=6, padx=10)
            bot_card.pack_propagate(False)
            
            # Nombre e informacion
            info_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, fill="y", pady=12)
            
            b_name = ctk.CTkLabel(info_frame, text=bot["name"], font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color="#f1f5f9")
            b_name.pack(anchor="w")
            
            b_details = ctk.CTkLabel(info_frame, text=f"Prefijo: '{bot['prefix']}'  •  Token: {bot['token'][:12]}...", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#94a3b8")
            b_details.pack(anchor="w")
            
            # Botones de Accion
            actions_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
            actions_frame.pack(side="right", padx=15)
            
            manage_btn = ctk.CTkButton(actions_frame, text="Gestionar", width=80, height=28, fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), command=lambda b=bot: self.select_bot(b))
            manage_btn.pack(side="left", padx=5)
            self.apply_fade_hover(manage_btn, "#2563eb", "#1d4ed8")
            
            delete_btn = ctk.CTkButton(actions_frame, text="Eliminar", width=60, height=28, fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), command=lambda bid=bot["id"]: self.handle_delete_bot(bid))
            delete_btn.pack(side="left", padx=5)
            self.apply_fade_hover(delete_btn, "#ef4444", "#dc2626")

    def handle_add_bot(self):
        name = self.bot_name_entry.get().strip()
        token = self.bot_token_entry.get().strip()
        prefix = self.bot_prefix_entry.get().strip() or "!"
        
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
        self.switch_screen_with_fade(self.show_bot_controls)

    def handle_logout(self):
        self.on_closing_bot() 
        self.current_user_id = None
        self.current_username = None
        self.active_bot_data = None
        self.switch_screen_with_fade(self.show_login)

    # --- PANEL DE CONTROL DEL BOT (MUSICA & LOGS & LETRAS) ---

    def show_bot_controls(self):
        self.clear_container()
        self.last_song_title = None
        
        # Grid layout: Sidebar y Bucle de Trabajo
        self.container.grid_columnconfigure(0, weight=0, minsize=220)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # --- SIDEBAR DEL BOT ---
        bot_sidebar = ctk.CTkFrame(self.container, corner_radius=0, width=220, fg_color="#0f172a")
        bot_sidebar.grid(row=0, column=0, sticky="nsew")
        bot_sidebar.grid_rowconfigure(6, weight=1)
        
        back_btn = ctk.CTkButton(bot_sidebar, text="◀ Dashboard", fg_color="#6b7280", hover_color="#4b5563", height=28, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), command=self.go_to_dashboard)
        back_btn.grid(row=0, column=0, pady=(20, 20), padx=20, sticky="w")
        self.apply_fade_hover(back_btn, "#6b7280", "#4b5563")
        
        # Nombre del bot activo
        active_bot_title = ctk.CTkLabel(bot_sidebar, text=self.active_bot_data["name"], font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="#5850ec")
        active_bot_title.grid(row=1, column=0, padx=20, sticky="w")
        
        prefix_lbl = ctk.CTkLabel(bot_sidebar, text=f"Prefijo: '{self.active_bot_data['prefix']}'", font=FONT_SUBTITLE, text_color="gray")
        prefix_lbl.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Estado de conexión
        status_frame = ctk.CTkFrame(bot_sidebar, fg_color="transparent")
        status_frame.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.status_dot = ctk.CTkLabel(status_frame, text="●", font=ctk.CTkFont(size=18), text_color="red")
        self.status_dot.pack(side="left")
        
        self.status_txt = ctk.CTkLabel(status_frame, text="Desconectado", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        self.status_txt.pack(side="left", padx=5)
        
        # Canales de Voz y Servidores
        self.guilds_count_lbl = ctk.CTkLabel(bot_sidebar, text="Servidores: 0", font=FONT_SUBTITLE, text_color="#94a3b8")
        self.guilds_count_lbl.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.vc_channel_lbl = ctk.CTkLabel(bot_sidebar, text="Canal de voz: Ninguno", font=FONT_SUBTITLE, text_color="#94a3b8")
        self.vc_channel_lbl.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        # Controles Encendido / Apagado
        power_frame = ctk.CTkFrame(bot_sidebar, fg_color="transparent")
        power_frame.grid(row=7, column=0, pady=20, padx=20, sticky="ew")
        
        self.start_bot_btn = ctk.CTkButton(power_frame, text="Iniciar Bot", fg_color="#10b981", hover_color="#059669", height=38, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), command=self.toggle_bot_power)
        self.start_bot_btn.pack(fill="x", pady=5)
        self.apply_fade_hover(self.start_bot_btn, "#10b981", "#059669")
        
        # --- ZONA DE TRABAJO (MÚSICA & CONSOLA) ---
        bot_workspace = ctk.CTkFrame(self.container, corner_radius=0, fg_color="#090d16")
        bot_workspace.grid(row=0, column=1, sticky="nsew")
        
        # --- CTKTABVIEW (DISEÑO LIMPIO EN PESTAÑAS) ---
        self.tabview = ctk.CTkTabview(
            bot_workspace,
            fg_color="#131d30",
            segmented_button_selected_color="#5850ec",
            segmented_button_selected_hover_color="#4f46e5",
            segmented_button_unselected_color="#0f172a",
            segmented_button_unselected_hover_color="#1e293b",
            text_color="#f1f5f9"
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_player = self.tabview.add("🎵 Reproductor")
        self.tab_lyrics = self.tabview.add("📝 Letra de Canción")
        self.tab_queue = self.tabview.add("📋 Cola de Reproducción")
        self.tab_logs = self.tabview.add("💬 Consola de Logs")
        
        # --- 1. CONFIGURACIÓN PESTAÑA: REPRODUCTOR ---
        player_frame = ctk.CTkFrame(self.tab_player, fg_color="transparent")
        player_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        p_title = ctk.CTkLabel(player_frame, text="Buscar y Reproducir Música", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#5850ec")
        p_title.pack(pady=(10, 5), anchor="w")
        
        # Buscador
        search_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Escribe un título de canción o pega un enlace de YouTube...", height=38, fg_color="#090d16", border_color="#1e293b")
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.gui_action_play())
        
        play_btn = ctk.CTkButton(search_frame, text="Play", width=75, height=38, fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), command=self.gui_action_play)
        play_btn.pack(side="left", padx=(8, 0))
        self.apply_fade_hover(play_btn, "#2563eb", "#1d4ed8")
        
        # Ficha "Ahora sonando"
        self.now_playing_frame = ctk.CTkFrame(player_frame, fg_color="#090d16", height=115, corner_radius=8, border_color="#1e293b", border_width=1)
        self.now_playing_frame.pack(fill="x", pady=20)
        self.now_playing_frame.pack_propagate(False)
        
        self.song_title_lbl = ctk.CTkLabel(self.now_playing_frame, text="Ninguna canción reproduciéndose", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color="#f1f5f9", wraplength=550)
        self.song_title_lbl.pack(pady=(25, 4), padx=15)
        
        self.song_meta_lbl = ctk.CTkLabel(self.now_playing_frame, text="-", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#94a3b8")
        self.song_meta_lbl.pack(pady=0)
        
        # Botones de reproducción
        ctrl_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        ctrl_frame.pack(pady=10)
        
        self.pause_btn = ctk.CTkButton(ctrl_frame, text="⏸ Pausa", width=100, height=36, fg_color="#5850ec", hover_color="#4f46e5", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), command=self.gui_action_pause)
        self.pause_btn.pack(side="left", padx=8)
        self.apply_fade_hover(self.pause_btn, "#5850ec", "#4f46e5")
        
        skip_btn = ctk.CTkButton(ctrl_frame, text="⏭ Saltar", width=100, height=36, fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), command=self.gui_action_skip)
        skip_btn.pack(side="left", padx=8)
        self.apply_fade_hover(skip_btn, "#2563eb", "#1d4ed8")
        
        stop_btn = ctk.CTkButton(ctrl_frame, text="⏹ Detener", width=100, height=36, fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), command=self.gui_action_stop)
        stop_btn.pack(side="left", padx=8)
        self.apply_fade_hover(stop_btn, "#ef4444", "#dc2626")
        
        dc_btn = ctk.CTkButton(ctrl_frame, text="👋 Salir de Voz", width=110, height=36, fg_color="#6b7280", hover_color="#4b5563", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), command=self.gui_action_disconnect)
        dc_btn.pack(side="left", padx=8)
        self.apply_fade_hover(dc_btn, "#6b7280", "#4b5563")
        
        # Slider de Volumen
        vol_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        vol_frame.pack(fill="x", padx=40, pady=20)
        
        vol_lbl = ctk.CTkLabel(vol_frame, text="🔊 Volumen:", font=FONT_SUBTITLE, text_color="#94a3b8")
        vol_lbl.pack(side="left", padx=10)
        
        self.vol_slider = ctk.CTkSlider(vol_frame, from_=0, to=100, number_of_steps=100, fg_color="#090d16", progress_color="#2563eb", button_color="#2563eb", command=self.gui_action_volume)
        self.vol_slider.set(50)
        self.vol_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        # --- 2. CONFIGURACIÓN PESTAÑA: LETRAS ---
        self.show_full_lyrics = False
        
        self.lyrics_container = ctk.CTkFrame(self.tab_lyrics, fg_color="transparent")
        self.lyrics_container.pack(fill="both", expand=True)
        
        # Vista de Enfoque (Apple Music Style) - El Protagonista
        self.lyrics_focus_frame = ctk.CTkFrame(self.lyrics_container, fg_color="transparent")
        self.lyrics_focus_frame.pack(fill="both", expand=True, pady=40)
        
        # Línea anterior (atenuada)
        self.lyr_prev_lbl = ctk.CTkLabel(
            self.lyrics_focus_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#475569",
            wraplength=650
        )
        self.lyr_prev_lbl.pack(pady=10)
        
        # Línea activa (Protagonista en grande y color violeta/blanco)
        self.lyr_curr_lbl = ctk.CTkLabel(
            self.lyrics_focus_frame,
            text="Ninguna canción reproduciéndose",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#a5b4fc",
            wraplength=750
        )
        self.lyr_curr_lbl.pack(pady=15)

        # Visualizador de espectro/ritmo reactivo (línea neon)
        self.vis_bar_container = ctk.CTkFrame(self.lyrics_focus_frame, fg_color="transparent", height=8, width=400)
        self.vis_bar_container.pack(pady=(0, 15))
        self.vis_bar_container.pack_propagate(False)
        
        self.vis_bar = ctk.CTkFrame(self.vis_bar_container, fg_color="#a5b4fc", height=4, corner_radius=2)
        self.vis_bar.place(relx=0.5, rely=0.5, anchor="center")
        
        # Línea siguiente (atenuada)
        self.lyr_next_lbl = ctk.CTkLabel(
            self.lyrics_focus_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#475569",
            wraplength=650
        )
        self.lyr_next_lbl.pack(pady=10)
        
        # Caja de texto para la letra completa (oculta al inicio)
        self.lyrics_textbox = ctk.CTkTextbox(
            self.lyrics_container,
            fg_color="#090d16",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#e2e8f0",
            border_color="#1e293b",
            border_width=1
        )
        self.lyrics_textbox.insert("1.0", "No se está reproduciendo ninguna canción.")
        self.lyrics_textbox.configure(state="disabled")
        
        # Botón para cambiar de modo
        self.toggle_lyrics_btn = ctk.CTkButton(
            self.lyrics_container,
            text="👁 Ver Letra Completa",
            width=140,
            height=28,
            fg_color="#1c283d",
            hover_color="#24344f",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.toggle_lyrics_view
        )
        self.toggle_lyrics_btn.pack(side="bottom", pady=10)
        self.apply_fade_hover(self.toggle_lyrics_btn, "#1c283d", "#24344f")

        # Controles de Sincronización Manual (desfase)
        self.sync_frame = ctk.CTkFrame(self.lyrics_container, fg_color="transparent")
        self.sync_frame.pack(side="bottom", fill="x", pady=(5, 5))
        
        sync_title = ctk.CTkLabel(self.sync_frame, text="⏱️ Sincronizar:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#94a3b8")
        sync_title.pack(side="left", padx=(15, 8))
        
        btn_opts = {"width": 50, "height": 24, "fg_color": "#1e293b", "hover_color": "#334155", "font": ctk.CTkFont(family="Segoe UI", size=11, weight="bold")}
        
        self.btn_sub2 = ctk.CTkButton(self.sync_frame, text="-2.0s", command=lambda: self.adjust_lyrics_offset(-2.0), **btn_opts)
        self.btn_sub2.pack(side="left", padx=3)
        self.apply_fade_hover(self.btn_sub2, "#1e293b", "#334155")
        
        self.btn_sub05 = ctk.CTkButton(self.sync_frame, text="-0.5s", command=lambda: self.adjust_lyrics_offset(-0.5), **btn_opts)
        self.btn_sub05.pack(side="left", padx=3)
        self.apply_fade_hover(self.btn_sub05, "#1e293b", "#334155")
        
        self.lbl_offset = ctk.CTkLabel(self.sync_frame, text="Desfase: +0.0s", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#5850ec", width=100)
        self.lbl_offset.pack(side="left", padx=10)
        
        self.btn_add05 = ctk.CTkButton(self.sync_frame, text="+0.5s", command=lambda: self.adjust_lyrics_offset(0.5), **btn_opts)
        self.btn_add05.pack(side="left", padx=3)
        self.apply_fade_hover(self.btn_add05, "#1e293b", "#334155")
        
        self.btn_add2 = ctk.CTkButton(self.sync_frame, text="+2.0s", command=lambda: self.adjust_lyrics_offset(2.0), **btn_opts)
        self.btn_add2.pack(side="left", padx=3)
        self.apply_fade_hover(self.btn_add2, "#1e293b", "#334155")
        
        self.btn_reset = ctk.CTkButton(self.sync_frame, text="Reset", fg_color="#ef4444", hover_color="#dc2626", text_color="white", command=self.reset_lyrics_offset, width=50, height=24, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.btn_reset.pack(side="left", padx=(10, 15))
        self.apply_fade_hover(self.btn_reset, "#ef4444", "#dc2626")
        
        # --- 3. CONFIGURACIÓN PESTAÑA: COLA ---
        self.scrollable_queue = ctk.CTkScrollableFrame(self.tab_queue, fg_color="#090d16", border_color="#1e293b")
        self.scrollable_queue.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_queue_ui([])
        
        # --- 4. CONFIGURACIÓN PESTAÑA: LOGS ---
        self.log_textbox = ctk.CTkTextbox(
            self.tab_logs,
            fg_color="#090d16",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#86efac",
            border_color="#1e293b",
            border_width=1
        )
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_textbox.configure(state="disabled")
        
        # Sincronizar inmediatamente la interfaz con el estado actual del bot al abrir el panel
        self.update_bot_ui_state()

    def go_to_dashboard(self):
        if self.bridge.status in ["online", "connecting"]:
            if not messagebox.askyesno("Confirmar", "El bot sigue ejecutándose en segundo plano. ¿Volver al Dashboard?"):
                return
        self.switch_screen_with_fade(self.show_dashboard)

    def toggle_bot_power(self):
        if self.bridge.status == "offline":
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
            self.on_closing_bot()

    def on_closing_bot(self):
        if self.bridge.status in ["online", "connecting"] and self.bridge.bot and self.bridge.loop:
            self.bridge.add_log("🔌 Apagando bot de Discord de forma segura...")
            asyncio.run_coroutine_threadsafe(self.bridge.bot.close(), self.bridge.loop)
        
        if hasattr(self, "start_bot_btn") and self.start_bot_btn and self.start_bot_btn.winfo_exists():
            self.start_bot_btn.configure(text="Iniciar Bot", fg_color="#10b981", hover_color="#059669")

    # --- BÚSQUEDA DE LETRAS EN SEGUNDO PLANO ---

    def get_lyrics_from_lrclib(self, song_title, duration=0, progress_callback=None):
        import re
        
        # Generar variaciones de búsqueda para mayor probabilidad de éxito
        queries = []
        
        # Limpieza A: quitar paréntesis y corchetes con su contenido (ej. (Prod. Sceno), [Official Video])
        clean_a = re.sub(r'\(.*?\)|\[.*?\]', '', song_title).strip()
        clean_a = " ".join(clean_a.split())
        if clean_a:
            queries.append(clean_a)
            
        # Limpieza B: si hay un guion, probar solo con la parte derecha (usualmente el título de la canción)
        if "-" in clean_a:
            parts = clean_a.split("-", 1)
            artist = parts[0].strip()
            track = parts[1].strip()
            if track:
                queries.append(track)
            if artist and track:
                queries.append(f"{artist} {track}")
                
        # Limpieza C: eliminar palabras comunes si aún no están cubiertas
        clean_c = song_title
        for remove_word in ["(Official Video)", "(Video Oficial)", "(Official Audio)", "(Audio)", "Lyric Video", "official video", "Lyrics", "lyrics", "feat.", "ft.", "(Lyrics)"]:
            clean_c = clean_c.replace(remove_word, "")
        clean_c = " ".join(clean_c.split())
        if clean_c not in queries:
            queries.append(clean_c)
            
        # Añadir el título original como última opción
        if song_title not in queries:
            queries.append(song_title)
            
        # Intentar cada variación secuencialmente en LRCLIB
        for idx, q_str in enumerate(queries, 1):
            try:
                if progress_callback:
                    progress_callback(idx, q_str)
                query = urllib.parse.quote(q_str)
                url = f"https://lrclib.net/api/search?q={query}"
                req = urllib.request.Request(url, headers={'User-Agent': 'ScriptBotStudio/1.0'})
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data and isinstance(data, list):
                        # Puntuación por coincidencia de duración y presencia de syncedLyrics
                        candidates = []
                        for item in data:
                            if item.get('lyrics') or item.get('syncedLyrics'):
                                has_synced = 1 if item.get('syncedLyrics') else 0
                                item_dur = item.get('duration', 0)
                                dur_diff = abs(item_dur - duration) if duration > 0 and item_dur > 0 else 99999
                                candidates.append((has_synced, dur_diff, item))
                                
                        if candidates:
                            # Ordenar por tiene letra sincronizada desc, luego dur_diff asc
                            candidates.sort(key=lambda x: (-x[0], x[1]))
                            best_item = candidates[0][2]
                            return {
                                'lyrics': best_item.get('lyrics', ''),
                                'synced': best_item.get('syncedLyrics', '')
                            }
            except Exception:
                # Silenciar errores de lectura/conexión en terminal
                pass
                
        return None

    def async_fetch_lyrics(self, title, duration=0):
        def progress_cb(idx, q_str):
            self.after(0, lambda: self.safe_show_search_progress(idx, q_str))
        lyrics_data = self.get_lyrics_from_lrclib(title, duration, progress_callback=progress_cb)
        self.after(0, lambda: self.safe_update_lyrics(lyrics_data))

    def parse_lrc(self, lrc_text):
        import re
        lines = lrc_text.split("\n")
        parsed = []
        for line in lines:
            match = re.match(r'\[(\d+):(\d+)(?:\.(\d+))?\](.*)', line)
            if match:
                m = int(match.group(1))
                s = int(match.group(2))
                ms_str = match.group(3)
                ms = int(ms_str) / 100.0 if ms_str else 0.0
                timestamp = m * 60 + s + ms
                text = match.group(4).strip()
                if text:
                    parsed.append((timestamp, text))
        parsed.sort(key=lambda x: x[0])
        return parsed

    def safe_update_lyrics(self, lyrics_data):
        if not hasattr(self, "lyrics_textbox") or not self.lyrics_textbox.winfo_exists():
            return
            
        self.lyrics_textbox.configure(state="normal")
        self.lyrics_textbox.delete("1.0", "end")
        self.current_song_lrc = []
        
        # Resetear etiquetas de la vista de enfoque
        if hasattr(self, "lyr_prev_lbl") and self.lyr_prev_lbl.winfo_exists():
            self.lyr_prev_lbl.configure(text="")
        if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
            self.lyr_curr_lbl.configure(text="No se encontraron letras para esta canción.")
        if hasattr(self, "lyr_next_lbl") and self.lyr_next_lbl.winfo_exists():
            self.lyr_next_lbl.configure(text="")
            
        if lyrics_data:
            plain = lyrics_data.get('lyrics', '')
            synced = lyrics_data.get('synced', '')
            
            if plain:
                self.lyrics_textbox.insert("end", plain)
                if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
                    self.lyr_curr_lbl.configure(text="(Letra plana disponible. Usa 'Ver Letra Completa')")
            elif synced:
                import re
                clean_plain = re.sub(r'\[\d+:\d+(?:\.\d+)?\]', '', synced).strip()
                self.lyrics_textbox.insert("end", clean_plain)
                
            if synced:
                self.current_song_lrc = self.parse_lrc(synced)
                if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
                    self.lyr_curr_lbl.configure(text="🎶 (Instrumental / Intro)")
        else:
            self.lyrics_textbox.insert("end", "No se encontraron letras para esta canción.")
            
        self.lyrics_textbox.configure(state="disabled")

    def toggle_lyrics_view(self):
        """Alterna entre la vista de letra de enfoque (Karaoke) y la letra completa."""
        if not hasattr(self, "lyrics_focus_frame") or not self.lyrics_focus_frame.winfo_exists():
            return
            
        self.show_full_lyrics = not self.show_full_lyrics
        if self.show_full_lyrics:
            self.lyrics_focus_frame.pack_forget()
            self.lyrics_textbox.pack(fill="both", expand=True, padx=10, pady=(10, 5))
            self.toggle_lyrics_btn.configure(text="✨ Ver Modo Enfoque")
            if hasattr(self, "sync_frame") and self.sync_frame.winfo_exists():
                self.sync_frame.pack_forget()
        else:
            self.lyrics_textbox.pack_forget()
            self.lyrics_focus_frame.pack(fill="both", expand=True, pady=40)
            self.toggle_lyrics_btn.configure(text="👁 Ver Letra Completa")
            if hasattr(self, "sync_frame") and self.sync_frame.winfo_exists():
                # Volver a empaquetar en la posición correcta (encima del botón de alternado)
                self.toggle_lyrics_btn.pack_forget()
                self.toggle_lyrics_btn.pack(side="bottom", pady=10)
                self.sync_frame.pack(side="bottom", fill="x", pady=(5, 5))

    def adjust_lyrics_offset(self, val):
        self.lyrics_offset += val
        sign = "+" if self.lyrics_offset >= 0 else ""
        if hasattr(self, "lbl_offset") and self.lbl_offset.winfo_exists():
            self.lbl_offset.configure(text=f"Desfase: {sign}{self.lyrics_offset:.1f}s")
            
    def reset_lyrics_offset(self):
        self.lyrics_offset = 0.0
        if hasattr(self, "lbl_offset") and self.lbl_offset.winfo_exists():
            self.lbl_offset.configure(text="Desfase: +0.0s")

    def interpolate_color(self, color1, color2, factor):
        c1 = color1.lstrip('#')
        c2 = color2.lstrip('#')
        try:
            r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
            r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color1

    def apply_fade_hover(self, btn, normal_color, hover_color):
        """Aplica un efecto de transición de color suave (fade) de 100ms en el estado hover del botón."""
        btn.custom_normal_color = normal_color
        btn.custom_hover_color = hover_color
        btn.current_transition = None
        
        btn.configure(hover=False, fg_color=normal_color)
        
        def fade(step, reverse=False):
            if not btn.winfo_exists():
                return
            steps = 5
            delay = 20  # 100ms en total (5 pasos x 20ms)
            factor = step / steps
            if reverse:
                factor = 1.0 - factor
            color = self.interpolate_color(btn.custom_normal_color, btn.custom_hover_color, factor)
            btn.configure(fg_color=color)
            if step < steps:
                btn.current_transition = btn.after(delay, lambda: fade(step + 1, reverse))
            else:
                btn.configure(fg_color=btn.custom_hover_color if not reverse else btn.custom_normal_color)
                btn.current_transition = None

        def on_enter(e):
            if hasattr(btn, "current_transition") and btn.current_transition:
                btn.after_cancel(btn.current_transition)
            fade(1, reverse=False)

        def on_leave(e):
            if hasattr(btn, "current_transition") and btn.current_transition:
                btn.after_cancel(btn.current_transition)
            fade(1, reverse=True)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def get_song_feeling_colors(self, title):
        """Determina el esquema de colores de la canción según palabras clave en su título."""
        title_lower = title.lower()
        # Sad / Melancholic songs (e.g. Amorfoda) -> Tonos azul cielo a azul profundo
        if any(w in title_lower for w in ["amorfoda", "sad", "triste", "llorar", "acoustic", "acustico", "piano", "broken"]):
            return "#60a5fa", "#2563eb"
        # Energetic / Aggressive / Trap -> Tonos rosa neón a rojo brillante
        elif any(w in title_lower for w in ["trap", "phonk", "bass", "metal", "rock", "rap", "speed", "remix"]):
            return "#f43f5e", "#e11d48"
        # Chill / Lo-Fi / Summer -> Tonos turquesa a verde esmeralda
        elif any(w in title_lower for w in ["lofi", "chill", "relax", "calm", "happy", "summer", "relaxing"]):
            return "#2dd4bf", "#059669"
        # Por defecto -> Se calcula dinámicamente con rotación HSL lenta
        return None, None

    def hsl_to_hex(self, h, s, l):
        """Convierte coordenadas HSL (H: 0-360, S: 0-100, L: 0-100) a color hexadecimal."""
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def trigger_lyric_transition(self, new_text, target_color):
        """Ejecuta una transición de color de desvanecimiento (fade-out/fade-in) para el verso activo."""
        if not hasattr(self, "lyr_curr_lbl") or not self.lyr_curr_lbl.winfo_exists():
            return
            
        self.in_lyric_transition = True
        bg_color = "#131d30"  # Color de fondo del panel de pestañas
        steps = 4
        delay = 40  # 160ms para fade-out, 160ms para fade-in
        
        def fade_out(step):
            if not self.lyr_curr_lbl.winfo_exists():
                self.in_lyric_transition = False
                return
            if step <= steps:
                factor = 1.0 - (step / steps)
                color = self.interpolate_color(bg_color, target_color, factor)
                self.lyr_curr_lbl.configure(text_color=color)
                self.after(delay, lambda: fade_out(step + 1))
            else:
                self.lyr_curr_lbl.configure(text=new_text)
                fade_in(1)
                
        def fade_in(step):
            if not self.lyr_curr_lbl.winfo_exists():
                self.in_lyric_transition = False
                return
            if step <= steps:
                factor = step / steps
                color = self.interpolate_color(bg_color, target_color, factor)
                self.lyr_curr_lbl.configure(text_color=color)
                self.after(delay, lambda: fade_in(step + 1))
            else:
                self.in_lyric_transition = False
                
        fade_out(1)

    def safe_show_search_progress(self, idx, q_str):
        """Actualiza la interfaz con el estado actual de la búsqueda en segundo plano de forma limpia."""
        # Limpieza estética del query para el usuario
        clean_q = q_str.split(" (Video")[0].split(" (Official")[0]
        msg = f"🔍 Buscando letras... (Opción {idx}: '{clean_q}')"
        if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
            self.lyr_curr_lbl.configure(text=msg, text_color="#94a3b8")
        if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
            self.lyrics_textbox.configure(state="normal")
            self.lyrics_textbox.delete("1.0", "end")
            self.lyrics_textbox.insert("1.0", f"🔍 Buscando letras en LRCLIB...\n\nOpción {idx}: {q_str}")
            self.lyrics_textbox.configure(state="disabled")

    def switch_screen_with_fade(self, show_screen_callback):
        """Cambia de pantalla realizando un desvanecimiento (fade-out/fade-in) de la opacidad de la ventana."""
        steps = 5
        delay = 15  # 75ms fade-out + 75ms fade-in = 150ms de transición rápida y fluida
        
        def fade_out(step):
            if step <= steps:
                alpha = 1.0 - (step / steps) * 0.9  # baja hasta 0.1 de opacidad
                self.attributes("-alpha", alpha)
                self.after(delay, lambda: fade_out(step + 1))
            else:
                # Cambiar de pantalla y reconstruir los widgets
                show_screen_callback()
                fade_in(1)
                
        def fade_in(step):
            if step <= steps:
                alpha = 0.1 + (step / steps) * 0.9  # sube hasta 1.0
                self.attributes("-alpha", alpha)
                self.after(delay, lambda: fade_in(step + 1))
            else:
                self.attributes("-alpha", 1.0)
                
        fade_out(1)

    # --- ACCIONES DE MUSICA DESDE LA GUI ---

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
            
        if self.bridge.state_updated:
            self.bridge.state_updated = False
            self.update_bot_ui_state()
            
        # Incrementar ángulo de rotación de color HSL lenta
        self.lyrics_hue = (self.lyrics_hue + 0.4) % 360
        
        # Calcular visualización de espectro reactiva ("punch")
        is_playing = (self.bridge.status == "online" and self.bridge.bot and not self.bridge.is_paused)
        amp = self.bridge.amplitude if is_playing else 0.0
        # Suavizado exponencial para transiciones suaves de pulso
        self.visual_amplitude = self.visual_amplitude * 0.7 + amp * 0.3
        
        # Determinar colores base y de golpe (ánimo o HSL dinámico)
        if self.song_color_base is not None:
            color_base = self.song_color_base
            color_punch = self.song_color_punch
        else:
            # Rotación de color suave por defecto para ambiente
            color_base = self.hsl_to_hex(self.lyrics_hue, 80, 75)
            color_punch = self.hsl_to_hex((self.lyrics_hue + 45) % 360, 100, 60)
            
        # Color reactivo de la letra activa e indicador inferior
        reactive_color = self.interpolate_color(color_base, color_punch, self.visual_amplitude)
        
        if hasattr(self, "vis_bar") and self.vis_bar.winfo_exists():
            # El ancho de la barra neon se contrae/expande según la amplitud (punch)
            w = int(20 + self.visual_amplitude * 360)
            self.vis_bar.configure(width=w, fg_color=reactive_color)
            
        # Actualizar las líneas de Karaoke (previo, activo, siguiente) en la vista de enfoque
        if self.bridge.status == "online" and self.bridge.bot and self.current_song_lrc:
            # Aplicar desfase manual configurado por el usuario
            elapsed = self.bridge.bot.get_elapsed_time() + self.lyrics_offset
            
            active_idx = -1
            for idx, (ts, text) in enumerate(self.current_song_lrc):
                if ts <= elapsed:
                    active_idx = idx
                else:
                    break
                    
            prev_line = ""
            curr_line = "🎶 (Instrumental / Intro)"
            next_line = ""
            
            if active_idx != -1:
                curr_line = self.current_song_lrc[active_idx][1]
                if active_idx > 0:
                    prev_line = self.current_song_lrc[active_idx - 1][1]
                if active_idx < len(self.current_song_lrc) - 1:
                    next_line = self.current_song_lrc[active_idx + 1][1]
            else:
                if self.current_song_lrc:
                    next_line = self.current_song_lrc[0][1]
                    
            if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
                self.lyr_prev_lbl.configure(text=prev_line)
                
                # Ejecutar transición de fundido si cambia la línea de texto
                if curr_line != self.last_curr_line:
                    self.last_curr_line = curr_line
                    self.trigger_lyric_transition(curr_line, reactive_color)
                elif not self.in_lyric_transition:
                    # Modificar tamaño de la fuente dinámicamente según la amplitud actual (punch)
                    dynamic_font_size = int(24 + self.visual_amplitude * 14)
                    self.lyr_curr_lbl.configure(
                        text=curr_line,
                        text_color=reactive_color,
                        font=ctk.CTkFont(family="Segoe UI", size=dynamic_font_size, weight="bold")
                    )
                
                self.lyr_next_lbl.configure(text=next_line)
            
        self.after(50, self.poll_bot_updates)

    def update_bot_ui_state(self):
        if not hasattr(self, "status_dot") or not self.status_dot.winfo_exists():
            return
            
        # Estado de conexión
        status = self.bridge.status
        if status == "online":
            self.status_dot.configure(text_color="#10b981")
            self.status_txt.configure(text="Conectado")
            if hasattr(self, "start_bot_btn") and self.start_bot_btn.winfo_exists():
                self.start_bot_btn.configure(text="Apagar Bot", fg_color="#ef4444", state="normal")
                self.start_bot_btn.custom_normal_color = "#ef4444"
                self.start_bot_btn.custom_hover_color = "#dc2626"
        elif status == "connecting":
            self.status_dot.configure(text_color="#fbbf24")
            self.status_txt.configure(text="Conectando...")
            if hasattr(self, "start_bot_btn") and self.start_bot_btn.winfo_exists():
                self.start_bot_btn.configure(text="Iniciando...", state="disabled")
        else: # offline
            self.status_dot.configure(text_color="#ef4444")
            self.status_txt.configure(text="Desconectado")
            if hasattr(self, "start_bot_btn") and self.start_bot_btn.winfo_exists():
                self.start_bot_btn.configure(text="Iniciar Bot", fg_color="#10b981", state="normal")
                self.start_bot_btn.custom_normal_color = "#10b981"
                self.start_bot_btn.custom_hover_color = "#059669"
            self.guilds_count_lbl.configure(text="Servidores: 0")
            self.vc_channel_lbl.configure(text="Canal de voz: Ninguno")
            self.update_queue_ui([])
            self.song_title_lbl.configure(text="Ninguna canción reproduciéndose")
            self.song_meta_lbl.configure(text="-")
            
            # Limpiar letra
            if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
                self.lyrics_textbox.configure(state="normal")
                self.lyrics_textbox.delete("1.0", "end")
                self.lyrics_textbox.insert("1.0", "No se está reproduciendo ninguna canción.")
                self.lyrics_textbox.configure(state="disabled")
            if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
                self.lyr_prev_lbl.configure(text="")
                self.lyr_curr_lbl.configure(text="Ninguna canción reproduciéndose")
                self.lyr_next_lbl.configure(text="")
            self.current_song_lrc = []
            self.last_song_title = None
            self.last_curr_line = ""
            self.song_color_base = "#a5b4fc"
            self.song_color_punch = "#f43f5e"
            return
            
        self.guilds_count_lbl.configure(text=f"Servidores: {len(self.bridge.guilds)}")
        
        vc = self.bridge.voice_channel
        self.vc_channel_lbl.configure(text=f"Canal de voz: {vc or 'Ninguno'}")
        
        # Canción actual sonando y buscador de letras
        song = self.bridge.current_song
        if song:
            title = song["title"]
            self.song_title_lbl.configure(text=title)
            duration_str = f"{song['duration'] // 60}:{song['duration'] % 60:02d}" if song['duration'] else "Directo"
            req = song.get("requester", "Desconocido")
            self.song_meta_lbl.configure(text=f"Duración: {duration_str}  •  Pedido por: {req}")
            
            # Buscar letra en segundo plano si cambió de canción
            if self.last_song_title != title:
                self.last_song_title = title
                # Resetear desfase de letras y animaciones para la nueva canción
                self.lyrics_offset = 0.0
                self.last_curr_line = ""
                self.song_color_base, self.song_color_punch = self.get_song_feeling_colors(title)
                
                if hasattr(self, "lbl_offset") and self.lbl_offset.winfo_exists():
                    self.lbl_offset.configure(text="Desfase: +0.0s")
                    
                if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
                    self.lyrics_textbox.configure(state="normal")
                    self.lyrics_textbox.delete("1.0", "end")
                    self.lyrics_textbox.insert("1.0", f"🔍 Buscando letra de: {title}...")
                    self.lyrics_textbox.configure(state="disabled")
                    duration = song.get("duration", 0)
                    threading.Thread(target=self.async_fetch_lyrics, args=(title, duration), daemon=True).start()
        else:
            self.song_title_lbl.configure(text="Ninguna canción reproduciéndose")
            self.song_meta_lbl.configure(text="-")
            if hasattr(self, "lyrics_textbox") and self.lyrics_textbox.winfo_exists():
                self.lyrics_textbox.configure(state="normal")
                self.lyrics_textbox.delete("1.0", "end")
                self.lyrics_textbox.insert("1.0", "No se está reproduciendo ninguna canción.")
                self.lyrics_textbox.configure(state="disabled")
            if hasattr(self, "lyr_curr_lbl") and self.lyr_curr_lbl.winfo_exists():
                self.lyr_prev_lbl.configure(text="")
                self.lyr_curr_lbl.configure(text="Ninguna canción reproduciéndose")
                self.lyr_next_lbl.configure(text="")
            self.current_song_lrc = []
            self.last_song_title = None
            self.last_curr_line = ""
            self.song_color_base = "#a5b4fc"
            self.song_color_punch = "#f43f5e"
            
        # Boton de Pausa / Reanudar
        if self.bridge.is_paused:
            self.pause_btn.configure(text="▶ Reanudar", fg_color="#fbbf24")
            self.pause_btn.custom_normal_color = "#fbbf24"
            self.pause_btn.custom_hover_color = "#d97706"
        else:
            self.pause_btn.configure(text="⏸ Pausa", fg_color="#5850ec")
            self.pause_btn.custom_normal_color = "#5850ec"
            self.pause_btn.custom_hover_color = "#4f46e5"
            
        self.vol_slider.set(self.bridge.volume * 100)
        self.update_queue_ui(self.bridge.queue)

    def update_queue_ui(self, queue_list):
        for widget in self.scrollable_queue.winfo_children():
            widget.destroy()
            
        if not queue_list:
            empty_lbl = ctk.CTkLabel(self.scrollable_queue, text="Cola de reproducción vacía.", text_color="gray", font=FONT_SUBTITLE)
            empty_lbl.pack(pady=40)
            return
            
        for idx, title in enumerate(queue_list, 1):
            q_item = ctk.CTkFrame(self.scrollable_queue, fg_color="#090d16", height=38, corner_radius=6, border_color="#1e293b", border_width=1)
            q_item.pack(fill="x", pady=4, padx=10)
            q_item.pack_propagate(False)
            
            lbl = ctk.CTkLabel(q_item, text=f"{idx}. {title}", font=FONT_BODY, anchor="w", text_color="#f1f5f9")
            lbl.pack(side="left", padx=12, fill="both", expand=True)

    # --- CIERRE SEGURO ---

    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres cerrar ScriptBot Studio?"):
            self.on_closing_bot()
            self.destroy()
