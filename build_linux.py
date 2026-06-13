import os
import sys
import subprocess

def main():
    print("=== Compilacion de Linux usando Docker ===")
    
    # 1. Comprobar si docker esta ejecutandose
    try:
        res = subprocess.run(["docker", "info"], capture_output=True)
        if res.returncode != 0:
            print("Error: Docker esta instalado pero no parece estar ejecutandose. Abre Docker Desktop e intentalo de nuevo.")
            sys.exit(1)
    except Exception:
        print("Error: No se pudo verificar el estado de Docker.")
        sys.exit(1)

    # 2. Comandos que se ejecutaran dentro del contenedor Linux
    # Descargar ffmpeg para Linux si no esta, instalar dependencias y compilar
    container_commands = [
        "apt-get update && apt-get install -y python3-tk wget xz-utils binutils",
        "if [ ! -f ffmpeg ]; then wget -qO ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && tar -xf ffmpeg.tar.xz && find . -name ffmpeg -type f -executable -exec cp {} . \\; && rm -f ffmpeg.tar.xz && rm -rf ffmpeg-*-static; fi",
        "pip install --upgrade pip",
        "pip install -r requirements.txt pyinstaller",
        "pyinstaller --name=\"ScriptBot Studio\" --onefile --windowed --add-data \"ffmpeg:.\" --noconfirm main.py",
        "cp \"dist/ScriptBot Studio\" \"dist/ScriptBot_Studio_Linux_Portable\"",
        # Crear script install.sh
        """cat << 'EOF' > dist/install.sh
#!/bin/bash
set -e
INSTALL_DIR="$HOME/.local/share/scriptbot-studio"
echo "Instalando ScriptBot Studio en $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp "ScriptBot Studio" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/ScriptBot Studio"

LAUNCHER_DIR="$HOME/.local/share/applications"
mkdir -p "$LAUNCHER_DIR"
cat << EOL > "$LAUNCHER_DIR/scriptbot-studio.desktop"
[Desktop Entry]
Name=ScriptBot Studio
Comment=Discord Music Bot Manager
Exec="$INSTALL_DIR/ScriptBot Studio"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOL

chmod +x "$LAUNCHER_DIR/scriptbot-studio.desktop"
echo "¡Instalacion completada con exito! Puedes ejecutarlo desde el menu de aplicaciones."
EOF
chmod +x dist/install.sh""",
        "cd dist && tar -czf ScriptBot_Studio_Linux_Installer.tar.gz install.sh \"ScriptBot Studio\""
    ]

    joined_commands = " && ".join(container_commands)
    
    # 3. Argumentos de docker como lista para evitar problemas de escape de comillas
    cwd = os.getcwd()
    docker_args = [
        "docker", "run", "--rm",
        "-v", f"{cwd}:/app",
        "-w", "/app",
        "python:3.11-slim-bookworm",
        "/bin/bash", "-c", joined_commands
    ]
    
    print("Iniciando contenedor Docker (python:3.11-slim-bookworm)...")
    print("Esto descargara ffmpeg para Linux y compilara el portable y el instalador.")
    print("Ejecutando proceso...")
    
    res = subprocess.run(docker_args, capture_output=False)
    
    if res.returncode == 0:
        print("\n=== Compilacion de Linux Finalizada con Exito ===")
        print("Archivos creados en dist/:")
        print(" - dist/ScriptBot_Studio_Linux_Portable (Binario ejecutable unico)")
        print(" - dist/ScriptBot_Studio_Linux_Installer.tar.gz (Instalador tarball)")
    else:
        print(f"\nOcurrio un error al compilar con Docker (Codigo de salida: {res.returncode}).")

if __name__ == "__main__":
    main()
