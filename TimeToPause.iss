; TimeToPause Inno Setup Script
; Compiles to: TimeToPauseSetup.exe

#define AppName      "Time to Pause"
#define AppVersion   "1.4.0"
#define AppPublisher "Aleksandr Suprunov"
#define AppExeName   "TimeToPause.exe"
#define AppURL       "https://github.com/alexagnestor-wq/timetopause"

[Setup]
; ---- Identity ----
AppId={{A9F2B3C1-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ---- Install location ----
DefaultDirName={autopf}\TimeToPause
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ---- Output ----
OutputDir=installer
OutputBaseFilename=TimeToPauseSetup
SetupIconFile=assets\app_icon2.ico

; ---- Compression ----
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ---- UI ----
WizardStyle=modern
WizardResizable=no
DisableWelcomePage=no
DisableReadyPage=no
ShowLanguageDialog=no

; ---- Privileges ----
; Request admin only if needed; use "lowest" so per-user install also works
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ---- Other ----
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "launchapp";   Description: "Launch {#AppName} after install"; GroupDescription: "After install:"; Flags: checkedonce

[Files]
; Main executable
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Default sounds — copied to AppData only if the file doesn't already exist
; (preserves custom sounds the user may have added)
Source: "assets\sounds\alert.wav";              DestDir: "{userappdata}\BreakReminder\assets\sounds"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "assets\sounds\beep.wav";               DestDir: "{userappdata}\BreakReminder\assets\sounds"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "assets\sounds\taste-the-rainbow-mf.wav"; DestDir: "{userappdata}\BreakReminder\assets\sounds"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "assets\sounds\it-is-wednesday.wav";    DestDir: "{userappdata}\BreakReminder\assets\sounds"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "assets\sounds\rick-roll-bass-boosted.wav"; DestDir: "{userappdata}\BreakReminder\assets\sounds"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
; Start Menu
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional task)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Launch after install (optional task)
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent; Tasks: launchapp

[UninstallDelete]
; Clean up the AppData config folder on uninstall
Type: filesandordirs; Name: "{userappdata}\BreakReminder"

[Code]
// Show a friendly message if sounds AppData dir was just created
procedure CurStepChanged(CurStep: TSetupStep);
var
  SoundsDir: String;
begin
  if CurStep = ssPostInstall then begin
    SoundsDir := ExpandConstant('{userappdata}\BreakReminder\assets\sounds');
    if not DirExists(SoundsDir) then
      CreateDir(SoundsDir);
  end;
end;
