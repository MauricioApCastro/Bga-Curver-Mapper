#define MyAppName "BGA Mapper"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "contato.mactecnology@gmail.com"
#define MyAppExeName "BGA Mapper.exe"
#define MyAppUserModelID "mactecnology.bgamapper.app"

[Setup]
AppId={{F9F44D54-3B51-4D57-9F51-33C38339E264}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=BGA_Mapper_Setup_{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Dirs]
Name: "{userdocs}\BGA Mapper\data"
Name: "{userdocs}\BGA Mapper\excels"

[Files]
Source: "..\dist\BGA Mapper\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\GUIA_USUARIO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\TERMOS_USO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\PRIVACIDADE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "{#MyAppUserModelID}"
Name: "{group}\Pasta de arquivos do BGA Mapper"; Filename: "{userdocs}\BGA Mapper"
Name: "{group}\Guia de uso"; Filename: "{app}\GUIA_USUARIO.txt"
Name: "{group}\Termos de uso"; Filename: "{app}\TERMOS_USO.txt"
Name: "{group}\Privacidade"; Filename: "{app}\PRIVACIDADE.txt"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "{#MyAppUserModelID}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent


