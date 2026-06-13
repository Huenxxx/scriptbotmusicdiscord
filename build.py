import os
import sys
import shutil
import subprocess

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

    # 2. Ejecutar PyInstaller en modo --onefile (un solo ejecutable)
    print("Iniciando PyInstaller...")
    # --windowed para ocultar la ventana de consola ya que es una aplicación CTk
    # --noconfirm para sobrescribir sin preguntar
    # --onefile para empaquetar todo en un único .exe
    # --add-data para incrustar ffmpeg.exe si está presente
    if os.path.exists("ffmpeg.exe"):
        print("Incrustando ffmpeg.exe dentro del ejecutable portable...")
        run_cmd('pyinstaller --name="ScriptBot Studio" --onefile --windowed --add-data "ffmpeg.exe;." --noconfirm main.py')
    else:
        print("Advertencia: No se encontró ffmpeg.exe. Compilando sin incrustar ffmpeg...")
        run_cmd('pyinstaller --name="ScriptBot Studio" --onefile --windowed --noconfirm main.py')

    # 3. Verificar que el ejecutable existe
    exe_path = os.path.join("dist", "ScriptBot Studio.exe")
    if not os.path.exists(exe_path):
        print(f"Error: No se encontró el ejecutable en {exe_path}")
        sys.exit(1)

    # 4. Crear el archivo Portable duplicando y renombrando el .exe
    portable_path = os.path.join("dist", "ScriptBot_Studio_Windows_Portable.exe")
    print(f"Creando ejecutable portable renombrado en {portable_path}...")
    shutil.copy2(exe_path, portable_path)

    # 5. Generar Script de Inno Setup para instalar el único .exe
    iss_content = """[Setup]
AppName=ScriptBot Studio
AppVersion=1.0.0
DefaultDirName={userappdata}\\Programs\\ScriptBot Studio
DefaultGroupName=ScriptBot Studio
UninstallDisplayIcon={app}\\ScriptBot Studio.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=ScriptBot_Studio_Windows_Setup
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\\ScriptBot Studio.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\ScriptBot Studio"; Filename: "{app}\\ScriptBot Studio.exe"
Name: "{userdesktop}\\ScriptBot Studio"; Filename: "{app}\\ScriptBot Studio.exe"
"""
    iss_path = "setup.iss"
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(iss_content)
    print(f"Script de Inno Setup escrito en {iss_path}")

    # 6. Compilar instalador con Inno Setup
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
