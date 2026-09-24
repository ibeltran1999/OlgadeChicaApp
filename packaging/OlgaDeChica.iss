[Setup]
AppId={{B8EECF1E-0F83-4D92-A7C5-01DADEC1CA11}
AppName=Olga de Chica
AppVersion=0.1.0
DefaultDirName={autopf}\OlgaDeChica
DefaultGroupName=Olga de Chica
OutputDir=..\release
OutputBaseFilename=OlgaDeChica-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\dist\OlgaDeChica\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "..\dist\OlgaMigracion\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Dirs]
Name: "{localappdata}\OlgaDeChica"
Name: "{localappdata}\OlgaDeChica\storage"

[Icons]
Name: "{group}\Olga de Chica"; Filename: "{app}\OlgaDeChica.exe"
Name: "{commondesktop}\Olga de Chica"; Filename: "{app}\OlgaDeChica.exe"

[Run]
Filename: "{app}\OlgaDeChica.exe"; Description: "Iniciar Olga de Chica"; Flags: nowait postinstall skipifsilent; Check: CanLaunchApplication

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
	MigrationSuccessful: Boolean;

function CanLaunchApplication(): Boolean;
begin
	Result := MigrationSuccessful;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
	ResultCode: Integer;
begin
	if CurStep = ssPostInstall then begin
		if not Exec(
			ExpandConstant('{app}\OlgaMigracion.exe'),
			'--data-dir "' + ExpandConstant('{localappdata}\OlgaDeChica') + '"',
			'', SW_HIDE, ewWaitUntilTerminated, ResultCode) then begin
			MsgBox('No fue posible ejecutar la migracion de la base de datos.', mbError, MB_OK);
			Abort;
		end;

		if ResultCode <> 0 then begin
			MsgBox('La migracion fallo. La aplicacion no se iniciara.', mbError, MB_OK);
			Abort;
		end;

		MigrationSuccessful := True;
	end;
end;
