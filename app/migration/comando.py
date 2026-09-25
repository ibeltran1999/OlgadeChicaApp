import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Iterator

from alembic import command
from alembic.config import Config

from app.configuracion import (
    carpeta_datos,
    carpeta_recursos,
    ruta_base_datos,
    url_base_datos,
)

BASELINE_REVISION = "20260924_0001"


class MigrationError(RuntimeError):
    pass


@contextmanager
def _migration_lock(data_dir: Path) -> Iterator[None]:
    lock_path = data_dir / ".migration.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise MigrationError("Ya hay otra migracion en curso") from error

    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as lock_file:
            lock_file.write(str(os.getpid()))
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def _create_backup(data_dir: Path, database_path: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = data_dir / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=False)

    if database_path.exists():
        shutil.copy2(database_path, backup_dir / database_path.name)

    storage_dir = data_dir / "storage"
    if storage_dir.exists():
        shutil.copytree(storage_dir, backup_dir / "storage")

    return backup_dir


def _check_integrity(database_path: Path) -> None:
    if not database_path.exists():
        return

    with closing(sqlite3.connect(database_path)) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()

    if result != ("ok",):
        raise MigrationError(f"La base no paso integrity_check: {result}")


def _table_names(database_path: Path) -> set[str]:
    if not database_path.exists():
        return set()

    with closing(sqlite3.connect(database_path)) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

    return {row[0] for row in rows}


def _has_alembic_version(database_path: Path) -> bool:
    return "alembic_version" in _table_names(database_path)


def _run_alembic(database_path: Path) -> None:
    config = Config(str(carpeta_recursos() / "alembic.ini"))
    config.attributes["database_url"] = url_base_datos(database_path.parent)
    command.upgrade(config, "head")


def migrate(data_dir: Path | None = None) -> Path:
    data_dir = carpeta_datos(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    database_path = ruta_base_datos(data_dir)

    with _migration_lock(data_dir):
        backup_dir = _create_backup(data_dir, database_path)
        _check_integrity(database_path)

        # Un archivo de cero bytes aún no tiene esquema ni datos que preservar.
        if (
            database_path.exists()
            and database_path.stat().st_size > 0
            and not _has_alembic_version(database_path)
        ):
            raise MigrationError(
                "La base existe pero no tiene version de Alembic; "
                "debe ser versionada antes de ejecutar esta herramienta."
            )

        _run_alembic(database_path)
        _check_integrity(database_path)

    return backup_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Instala o actualiza los datos de Olga de Chica"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Carpeta estable que contiene olga.db y storage",
    )
    args = parser.parse_args(argv)

    try:
        backup_dir = migrate(args.data_dir)
    except Exception as error:
        print(f"Migracion fallida: {error}", file=sys.stderr)
        return 1

    print(f"Migracion completada. Respaldo: {backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
