import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Iterator

from alembic import command
from alembic.config import Config

BASELINE_REVISION = "20260924_0001"
EXPECTED_TABLES = {"archivos", "filminas", "filmina_tags", "tags"}
PROJECT_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


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


def _database_url(database_path: Path) -> str:
    return f"sqlite:///{database_path.as_posix()}"


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

    with sqlite3.connect(database_path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()

    if result != ("ok",):
        raise MigrationError(f"La base no paso integrity_check: {result}")


def _table_names(database_path: Path) -> set[str]:
    if not database_path.exists():
        return set()

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    return {row[0] for row in rows}


def _has_alembic_version(database_path: Path) -> bool:
    return "alembic_version" in _table_names(database_path)


def _run_alembic(database_path: Path, operation: str) -> None:
    database_url = _database_url(database_path)
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

    previous_url = os.environ.get("ALEMBIC_DATABASE_URL")
    os.environ["ALEMBIC_DATABASE_URL"] = database_url
    try:
        if operation == "stamp":
            command.stamp(config, BASELINE_REVISION)
        else:
            command.upgrade(config, "head")
    finally:
        if previous_url is None:
            os.environ.pop("ALEMBIC_DATABASE_URL", None)
        else:
            os.environ["ALEMBIC_DATABASE_URL"] = previous_url


def migrate(data_dir: Path, adopt_existing: bool = False) -> Path:
    data_dir = data_dir.expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    database_path = data_dir / "olga.db"

    with _migration_lock(data_dir):
        backup_dir = _create_backup(data_dir, database_path)
        _check_integrity(database_path)

        if database_path.exists() and not _has_alembic_version(database_path):
            if not adopt_existing:
                raise MigrationError(
                    "La base existe pero no tiene version de Alembic. "
                    "Ejecute nuevamente con --adopt-existing despues de verificarla."
                )

            missing_tables = EXPECTED_TABLES - _table_names(database_path)
            if missing_tables:
                raise MigrationError(
                    "No se puede adoptar la base; faltan tablas: "
                    + ", ".join(sorted(missing_tables))
                )
            _run_alembic(database_path, "stamp")

        _run_alembic(database_path, "upgrade")
        _check_integrity(database_path)

    return backup_dir


def _default_data_dir() -> Path:
    return Path(os.environ.get("OLGA_DATA_DIR", PROJECT_ROOT / "instance"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Instala o actualiza los datos de Olga de Chica"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=_default_data_dir(),
        help="Carpeta estable que contiene olga.db y storage",
    )
    parser.add_argument(
        "--adopt-existing",
        action="store_true",
        help="Marca como baseline una base existente sin version de Alembic",
    )
    args = parser.parse_args(argv)

    try:
        backup_dir = migrate(args.data_dir, args.adopt_existing)
    except Exception as error:
        print(f"Migracion fallida: {error}", file=sys.stderr)
        return 1

    print(f"Migracion completada. Respaldo: {backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
