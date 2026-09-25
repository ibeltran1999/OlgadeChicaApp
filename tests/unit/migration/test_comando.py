import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from sqlalchemy import create_engine

from app.migration.comando import (
    BASELINE_REVISION,
    MigrationError,
    migrate,
)
from app.persistence.modelos import Base


class ComandoMigracionTestCase(unittest.TestCase):

    def setUp(self):
        self.directorio_temporal = tempfile.TemporaryDirectory()
        self.carpeta_datos = Path(self.directorio_temporal.name)
        self.ruta_base_datos = self.carpeta_datos / "olga.db"

    def tearDown(self):
        self.directorio_temporal.cleanup()

    def nombres_de_tablas(self):
        with closing(sqlite3.connect(self.ruta_base_datos)) as conexion:
            filas = conexion.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()

        return {fila[0] for fila in filas}

    def version_de_alembic(self):
        with closing(sqlite3.connect(self.ruta_base_datos)) as conexion:
            return conexion.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()[0]

    def crear_base_legacy(self):
        engine = create_engine(f"sqlite:///{self.ruta_base_datos}")
        Base.metadata.create_all(engine)
        engine.dispose()

    def test_crea_base_nueva_y_registra_baseline(self):
        respaldo = migrate(self.carpeta_datos)

        self.assertEqual(
            self.nombres_de_tablas(),
            {
                "alembic_version",
                "archivos",
                "filminas",
                "filmina_tags",
                "tags",
            },
        )
        self.assertEqual(self.version_de_alembic(), BASELINE_REVISION)
        self.assertTrue(respaldo.is_dir())

    def test_inicializa_archivo_vacio_y_conserva_respaldo(self):
        self.ruta_base_datos.touch()

        respaldo = migrate(self.carpeta_datos)

        self.assertEqual((respaldo / "olga.db").read_bytes(), b"")
        self.assertIn("tags", self.nombres_de_tablas())
        self.assertIn("filminas", self.nombres_de_tablas())
        self.assertEqual(self.version_de_alembic(), BASELINE_REVISION)
        migrate(self.carpeta_datos)
        self.assertEqual(self.version_de_alembic(), BASELINE_REVISION)

    def test_rechaza_base_existente_sin_version_de_alembic(self):
        self.crear_base_legacy()

        with self.assertRaisesRegex(MigrationError, "no tiene version de Alembic"):
            migrate(self.carpeta_datos)

    def test_ejecuciones_repetidas_son_idempotentes(self):
        primer_respaldo = migrate(self.carpeta_datos)
        segundo_respaldo = migrate(self.carpeta_datos)

        self.assertNotEqual(primer_respaldo, segundo_respaldo)
        self.assertEqual(self.version_de_alembic(), BASELINE_REVISION)

    def test_rechaza_migracion_si_existe_bloqueo(self):
        ruta_bloqueo = self.carpeta_datos / ".migration.lock"
        ruta_bloqueo.write_text("otro proceso", encoding="ascii")

        with self.assertRaises(MigrationError):
            migrate(self.carpeta_datos)

        self.assertTrue(ruta_bloqueo.exists())


if __name__ == "__main__":
    unittest.main()
