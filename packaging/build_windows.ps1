$ErrorActionPreference = "Stop"

$argumentosAplicacion = @(
    "--noconfirm"
    "--clean"
    "--onedir"
    "--windowed"
    "--name", "OlgaDeChica"
    "--icon", "packaging/assets/olgadechicaIcon.ico"
    "--add-data", "app/presentation/templates;app/presentation/templates"
    "--add-data", "app/static;app/static"
    "run.py"
)
pyinstaller @argumentosAplicacion
if ($LASTEXITCODE -ne 0) { throw "Fallo al construir OlgaDeChica" }

$argumentosMigracion = @(
    "--noconfirm"
    "--clean"
    "--onedir"
    "--name", "OlgaMigracion"
    "--hidden-import", "logging.config"
    "--add-data", "alembic.ini;."
    "--add-data", "alembic;alembic"
    "app/migration/comando.py"
)
pyinstaller @argumentosMigracion
if ($LASTEXITCODE -ne 0) { throw "Fallo al construir OlgaMigracion" }

Write-Host "Build completado en dist/"
