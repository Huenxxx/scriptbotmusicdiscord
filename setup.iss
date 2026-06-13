[Setup]
AppName=ScriptBot Studio
AppVersion=1.0.0
DefaultDirName={userappdata}\Programs\ScriptBot Studio
DefaultGroupName=ScriptBot Studio
UninstallDisplayIcon={app}\ScriptBot Studio.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=ScriptBot_Studio_Setup
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\ScriptBot Studio\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ScriptBot Studio"; Filename: "{app}\ScriptBot Studio.exe"
Name: "{userdesktop}\ScriptBot Studio"; Filename: "{app}\ScriptBot Studio.exe"
