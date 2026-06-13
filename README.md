# 🎨 ScriptBot Studio

**ScriptBot Studio** es un gestor de escritorio interactivo y moderno desarrollado en Python para administrar múltiples bots de música de Discord. Todo esto sin dependencias externas como Java o servidores Lavalink.

<p align="center">
  <img src="https://raw.githubusercontent.com/Huenxxx/scriptbotmusicdiscord/main/.gemini/antigravity/brain/802d8151-10d3-40a9-bf8e-66a76a3b4892/scriptbot_logo_1781316130725.png" alt="ScriptBot Studio Logo" width="200"/>
</p>

---

## ✨ Características Principales

*   **Autenticación Local (Login/Registro)**: Las credenciales y configuraciones de tus bots se almacenan cifradas en una base de datos local SQLite (`data.db`).
*   **Gestor de Múltiples Bots (Dashboard)**: Añade, organiza y elimina múltiples bots indicando su Token de Discord, Prefijo y un Nombre personalizado.
*   **Panel de Control de Música**:
    *   **Búsqueda Rápida**: Escribe un nombre o pega un enlace de YouTube directamente en la GUI.
    *   **Controles en Vivo**: Reproducir, Pausar/Reanudar, Saltar canción (Skip), Regular volumen y Detener la música (Stop).
    *   **Cola de Reproducción**: Visualiza las canciones que están por reproducirse en tiempo real.
    *   **Estado de Conexión**: Indicadores visuales en vivo del estado de conexión del bot (Online/Offline) y del canal de voz al que está conectado.
*   **Consola de Logs Integrada**: Mira exactamente qué está haciendo tu bot en tiempo real a través del terminal incorporado.
*   **Comandos de Chat de Discord**: El bot sigue respondiendo a comandos del chat de Discord (`!play`, `!skip`, `!pause`, `!resume`, `!volume`, `!queue`, `!stop`, `!leave`).

---

## 🛠️ Instalación y Requisitos

### Requisitos Previos

1.  **Python 3.8+**: Asegúrate de tener Python instalado y añadido al PATH de tu sistema.
2.  **FFmpeg**: El programa requiere el binario de FFmpeg (`ffmpeg.exe`) para el procesamiento de audio. Por defecto, busca en la raíz del proyecto.
3.  **Habilitar Message Content Intent**: Ve al [Discord Developer Portal](https://discord.com/developers/applications), selecciona tu aplicación, entra en **Bot** y en la sección **Privileged Gateway Intents** activa **Message Content Intent**, **Server Members Intent** y **Presence Intent**.

### Instalación de Librerías

Ejecuta el siguiente comando en tu terminal para instalar las dependencias:

```bash
pip install -r requirements.txt
```

*(O de forma manual)*:

```bash
pip install discord.py[voice] yt-dlp PyNaCl customtkinter darkdetect
```

---

## 🚀 Cómo Iniciar el Programa

Para abrir la interfaz gráfica de **ScriptBot Studio**, simplemente ejecuta el archivo `main.py`:

```bash
python main.py
```

1.  **Registra una cuenta local** en la pantalla inicial.
2.  **Inicia sesión** con las credenciales que creaste.
3.  Registra un nuevo bot ingresando su **Token de Discord** y un **Nombre**.
4.  Haz clic en **Gestionar** en el bot que desees y luego pulsa **Iniciar Bot**.
5.  ¡Listo! Ya puedes poner música escribiendo en el buscador de la GUI o mediante los comandos en Discord.

---

## 🛡️ Seguridad

Tus credenciales de usuario locales se cifran usando PBKDF2 con salting (HMAC-SHA256). La base de datos local `data.db` está configurada en `.gitignore` para asegurar que tus tokens de Discord nunca se suban a un repositorio público de GitHub por accidente.
