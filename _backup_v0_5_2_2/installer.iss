; Rob's Code Wizard - Inno Setup script (v0.3.9.5.1.1)
; ISPP #if FileExists guards keep this resilient to missing optional files.

#define MyAppName "Rob's Code Wizard"
#define MyAppVersion "0.3.9.5.1.1"
#define MyAppPublisher "Robert Slater"
#define MyAppExeName "RobsCodeWizard.exe"
#define MyExePath "..\dist\RobsCodeWizard.exe"
#define MyIconPath "..\resources\icon.ico"

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
CloseApplications=yes
RestartApplications=yes
CloseApplicationsFilter=*.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "{#MyExePath}"; DestDir: "{app}"; Flags: ignoreversion
#if FileExists(MyIconPath)
Source: "{#MyIconPath}"; DestDir: "{app}"; Flags: ignoreversion
#endif

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
; v0.4.8 silent-install relaunch (auto-relaunch after updater installs)
Filename: "{app}\{#MyAppExeName}"; Flags: nowait runasoriginaluser; Check: WizardSilent
