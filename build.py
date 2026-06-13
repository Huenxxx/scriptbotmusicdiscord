import os
import sys
import shutil
import subprocess
import zipfile

def run_cmd(cmd, shell=True):
    print(f"Ejecutando: {cmd}")
    res = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        print(f"Error al ejecutar comando: {res.stderr}")
        sys.exit(1)
    print(res.stdout)

def main():
    # 1. Limpiar carpetas de compilación anteriores
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            print(f"Limpiando {folder}...")
            shutil.rmtree(folder)

    # 2. Ejecutar PyInstaller
    print("Iniciando PyInstaller...")
    # --windowed para ocultar la ventana de consola ya que es una aplicación CTk
    # --noconfirm para sobrescribir sin preguntar
    # --name para especificar el nombre del ejecutable
    run_cmd('pyinstaller --name="ScriptBot Studio" --windowed --noconfirm main.py')

    # 3. Verificar que el ejecutable existe
    exe_dir = os.path.join("dist", "ScriptBot Studio")
    exe_path = os.path.join(exe_dir, "ScriptBot Studio.exe")
    if not os.path.exists(exe_path):
        print(f"Error: No se encontró el ejecutable en {exe_path}")
        sys.exit(1)

    # 4. Copiar ffmpeg.exe al directorio dist
    ffmpeg_src = "ffmpeg.exe"
    ffmpeg_dst = os.path.join(exe_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_src):
        print("Copiando ffmpeg.exe al directorio dist...")
        shutil.copy2(ffmpeg_src, ffmpeg_dst)
    else:
        print("Advertencia: No se encontró ffmpeg.exe en el directorio raíz. No se incluirá en el portable.")

    # 5. Crear ZIP Portable
    zip_path = os.path.join("dist", "ScriptBot_Studio_Portable.zip")
    print(f"Creando ZIP portable en {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(exe_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, "dist")
                zipf.write(filepath, arcname)
    print("ZIP Portable creado con éxito.")

    # 6. Generar Script de Inno Setup
    iss_content = """[Setup]
AppName=ScriptBot Studio
AppVersion=1.0.0
DefaultDirName={userappdata}\\Programs\\ScriptBot Studio
DefaultGroupName=ScriptBot Studio
UninstallDisplayIcon={app}\\ScriptBot Studio.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=ScriptBot_Studio_Setup
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\\ScriptBot Studio\\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\ScriptBot Studio"; Filename: "{app}\\ScriptBot Studio.exe"
Name: "{userdesktop}\\ScriptBot Studio"; Filename: "{app}\\ScriptBot Studio.exe"
"""
    iss_path = "setup.iss"
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(iss_content)
    print(f"Script de Inno Setup escrito en {iss_path}")

    # 7. Compilar instalador con Inno Setup
    iscc_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Users\huenx\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "ISCC.exe"
    ]
    iscc_compiled = False
    for path in iscc_paths:
        if path == "ISCC.exe" or os.path.exists(path):
            try:
                print(f"Compilando setup.exe usando: {path}...")
                run_cmd(f'"{path}" setup.iss')
                iscc_compiled = True
                break
            except Exception as e:
                print(f"Fallo al compilar con {path}: {e}")

    if iscc_compiled:
        print("Setup.exe creado con éxito.")
    else:
        print("Error: No se pudo localizar ISCC.exe para compilar el instalador.")
        sys.exit(1)

if __name__ == "__main__":
    main()
