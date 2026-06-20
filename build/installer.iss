; Rob's Code Wizard - Inno Setup script (hotfix .8)
; Tolerates missing app\assets\icon.ico via ISPP #if FileExists().

#define MyAppName "Rob's Code Wizard"
#define MyAppVersion "0.3.9.5.0"
#define MyAppPublisher "Robert Slater"
#define MyAppExeName "RobsCodeWizard.exe"
#define MyExePath "..\dist\RobsCodeWizard.exe"
#define MyIconPath "..\app\assets\icon.ico"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\RobsCodeWizard
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=RobsCodeWizard_Setup
#if FileExists(MyIconPath)
SetupIconFile={#MyIconPath}
#endif
Compression=lzma2/ultra
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "{#MyExePath}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
