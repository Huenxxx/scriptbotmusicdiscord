import os
import sys
import json
import requests

# Ruta del archivo de configuración de Firebase en el directorio de la aplicación
def get_app_dir():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            app_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'ScriptBot Studio')
        else:
            app_dir = os.path.expanduser('~/.config/scriptbot-studio')
        try:
            os.makedirs(app_dir, exist_ok=True)
        except Exception:
            pass
        return app_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(get_app_dir(), "firebase_config.json")
FIREBASE_CONFIG = None
CURRENT_ID_TOKEN = None

# Configuración por defecto (Firebase de ScriptBot Studio)
DEFAULT_CONFIG = {
    "apiKey": "AIzaSyDtr1hsDmD8nfD18nLmZuF7TUDQDqn_KOs",
    "projectId": "scriptbotstudio-9156c",
    "databaseUrl": "https://scriptbotstudio-9156c-default-rtdb.europe-west1.firebasedatabase.app"
}

def is_config_placeholder(config):
    if not config:
        return True
    return (config.get("apiKey") == "TU_FIREBASE_API_KEY" or 
            config.get("projectId") == "TU_PROJECT_ID")

def load_firebase_config():
    global FIREBASE_CONFIG
    if FIREBASE_CONFIG is not None:
        return FIREBASE_CONFIG
        
    if not os.path.exists(CONFIG_FILE):
        # Crear plantilla de configuración por defecto para que el usuario sepa que puede personalizarla
        template = {
            "apiKey": "TU_FIREBASE_API_KEY",
            "projectId": "TU_PROJECT_ID",
            "databaseUrl": "https://TU_PROJECT_ID-default-rtdb.firebaseio.com"
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al crear plantilla de Firebase: {e}")
        # Retornar la configuración por defecto incrustada
        FIREBASE_CONFIG = DEFAULT_CONFIG
        return FIREBASE_CONFIG
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
            if is_config_placeholder(loaded_config):
                FIREBASE_CONFIG = DEFAULT_CONFIG
            else:
                FIREBASE_CONFIG = loaded_config
            return FIREBASE_CONFIG
    except Exception as e:
        print(f"Error al cargar firebase_config.json: {e}")
        FIREBASE_CONFIG = DEFAULT_CONFIG
        return FIREBASE_CONFIG

def init_db():
    """Inicializa Firebase cargando o creando la plantilla de configuración."""
    load_firebase_config()

def register_user(username, password):
    """Registra un nuevo usuario en Firebase Auth. Retorna (exito, mensaje)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "El usuario y la contraseña no pueden estar vacíos."
        
    config = load_firebase_config()
    if is_config_placeholder(config):
        return False, "Firebase no está configurado. Edita 'firebase_config.json' con tus credenciales."
        
    api_key = config.get("apiKey")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    
    # Firebase Auth requiere un email válido, por lo que creamos uno sintáctico
    email = f"{username}@scriptbot.local"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res_data = res.json()
        if res.status_code == 200:
            return True, "Registro completado con éxito."
        else:
            error_msg = res_data.get("error", {}).get("message", "Error desconocido")
            if error_msg == "EMAIL_EXISTS":
                return False, "El nombre de usuario ya está registrado."
            elif "WEAK_PASSWORD" in error_msg:
                return False, "La contraseña debe tener al menos 6 caracteres."
            elif "INVALID_EMAIL" in error_msg:
                return False, "El nombre de usuario contiene caracteres no válidos para Firebase."
            return False, f"Error de Firebase: {error_msg}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def login_user(username, password):
    """Autentica al usuario en Firebase Auth. Retorna el UID del usuario si es correcto, None si no."""
    global CURRENT_ID_TOKEN
    username = username.strip().lower()
    if not username or not password:
        return None
        
    config = load_firebase_config()
    if is_config_placeholder(config):
        return None
        
    api_key = config.get("apiKey")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    email = f"{username}@scriptbot.local"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res_data = res.json()
        if res.status_code == 200:
            CURRENT_ID_TOKEN = res_data.get("idToken")
            return res_data.get("localId") # Retorna el UID único de Firebase
        else:
            return None
    except Exception:
        return None

def add_bot(user_id, name, token, prefix="!"):
    """Añade un bot asociado al UID del usuario en Firebase Realtime Database. Retorna (exito, mensaje)."""
    name = name.strip()
    token = token.strip()
    prefix = prefix.strip() or "!"
    
    if not name or not token:
        return False, "El nombre y el token del bot son obligatorios."
        
    config = load_firebase_config()
    if is_config_placeholder(config):
        return False, "Firebase no está configurado de manera válida."
        
    db_url = config.get("databaseUrl").rstrip("/")
    url = f"{db_url}/users/{user_id}/bots.json"
    
    params = {}
    if CURRENT_ID_TOKEN:
        params["auth"] = CURRENT_ID_TOKEN
        
    payload = {
        "name": name,
        "token": token,
        "prefix": prefix
    }
    
    try:
        res = requests.post(url, json=payload, params=params, timeout=10)
        if res.status_code == 200:
            return True, "Bot añadido correctamente."
        else:
            return False, f"Error de Firebase: {res.text}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def get_bots(user_id):
    """Obtiene todos los bots asociados al UID del usuario desde Firebase Realtime Database."""
    config = load_firebase_config()
    if is_config_placeholder(config):
        return []
        
    db_url = config.get("databaseUrl").rstrip("/")
    url = f"{db_url}/users/{user_id}/bots.json"
    
    params = {}
    if CURRENT_ID_TOKEN:
        params["auth"] = CURRENT_ID_TOKEN
        
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if not data:
                return []
                
            bots = []
            for bot_key, bot_data in data.items():
                bots.append({
                    "id": bot_key, # El push ID generado por Firebase sirve como ID de bot
                    "name": bot_data.get("name"),
                    "token": bot_data.get("token"),
                    "prefix": bot_data.get("prefix", "!")
                })
            return bots
        else:
            return []
    except Exception:
        return []

def delete_bot(bot_id, user_id):
    """Elimina un bot específico del usuario de Firebase Realtime Database."""
    config = load_firebase_config()
    if is_config_placeholder(config):
        return False
        
    db_url = config.get("databaseUrl").rstrip("/")
    url = f"{db_url}/users/{user_id}/bots/{bot_id}.json"
    
    params = {}
    if CURRENT_ID_TOKEN:
        params["auth"] = CURRENT_ID_TOKEN
        
    try:
        res = requests.delete(url, params=params, timeout=10)
        return res.status_code == 200
    except Exception:
        return False
