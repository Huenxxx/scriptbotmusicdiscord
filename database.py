import sqlite3
import hashlib
import os

DB_FILE = "data.db"

def get_connection():
    """Retorna una conexion a la base de datos local con soporte de claves foraneas."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Inicializa la base de datos creando las tablas necesarias si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    );
    """)
    
    # Crear tabla de bots asociados a usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        token TEXT NOT NULL,
        prefix TEXT NOT NULL DEFAULT '!',
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Genera un hash seguro para la contrasena usando PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(16)
    else:
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
            
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000 # Numero de iteraciones
    )
    return key.hex(), salt.hex()

def register_user(username, password):
    """Registra un nuevo usuario con contrasena cifrada. Retorna (exito, mensaje)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "El usuario y la contraseña no pueden estar vacíos."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        password_hash, salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True, "Registro completado con éxito."
    except sqlite3.IntegrityError:
        return False, "El nombre de usuario ya está registrado."
    except Exception as e:
        return False, f"Error al registrar: {str(e)}"
    finally:
        conn.close()

def login_user(username, password):
    """Verifica las credenciales del usuario. Retorna el ID del usuario si es correcto, None si no."""
    username = username.strip().lower()
    if not username or not password:
        return None
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_id, stored_hash, salt = row
        test_hash, _ = hash_password(password, salt)
        if test_hash == stored_hash:
            return user_id
            
    return None

def add_bot(user_id, name, token, prefix="!"):
    """Anade un bot para un usuario. Retorna (exito, mensaje)."""
    name = name.strip()
    token = token.strip()
    prefix = prefix.strip()
    
    if not name or not token:
        return False, "El nombre y el token del bot son obligatorios."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO bots (user_id, name, token, prefix) VALUES (?, ?, ?, ?)",
            (user_id, name, token, prefix)
        )
        conn.commit()
        return True, "Bot añadido correctamente."
    except Exception as e:
        return False, f"Error al guardar el bot: {str(e)}"
    finally:
        conn.close()

def get_bots(user_id):
    """Retorna una lista de diccionarios con los bots asociados al usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, token, prefix FROM bots WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    bots = []
    for row in rows:
        bots.append({
            "id": row[0],
            "name": row[1],
            "token": row[2],
            "prefix": row[3]
        })
    return bots

def delete_bot(bot_id, user_id):
    """Elimina un bot si pertenece al usuario especificado."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM bots WHERE id = ? AND user_id = ?", (bot_id, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()
