$ErrorActionPreference = "Stop"

pyinstaller --noconfirm --clean --onedir --name OlgaDeChica `
    --add-data "app/presentation/templates;app/presentation/templates" `
    --add-data "app/static;app/static" `
    run.py

pyinstaller --noconfirm --clean --onedir --name OlgaMigracion `
    --add-data "alembic.ini;." `
    --add-data "alembic;alembic" `
    app/migration/comando.py

Write-Host "Build completado en dist/"
