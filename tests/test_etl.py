import csv
import hashlib
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.etl import cargar, CSV_PATH, COLUMNAS


class PruebasETL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / 'prueba.sqlite'
        cls.auditoria = cargar(CSV_PATH, cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_totales_sin_doble_conteo(self):
        with closing(sqlite3.connect(self.db)) as con:
            resultado = con.execute(
                'SELECT COUNT(*), SUM(casos) FROM hecho_mortalidad'
            ).fetchone()
            self.assertEqual(resultado, (6193, 6200))

            total_fuente = con.execute(
                'SELECT COUNT(*) FROM fuente_original'
            ).fetchone()[0]
            self.assertEqual(total_fuente, 12386)

            registros_bogota = con.execute(
                'SELECT COUNT(*) FROM vw_mortalidad WHERE codigo_localidad = 0'
            ).fetchone()[0]
            self.assertEqual(registros_bogota, 0)

    def test_relaciones_y_reconstruccion(self):
        with closing(sqlite3.connect(self.db)) as con:
            relaciones = con.execute(
                'PRAGMA foreign_key_check'
            ).fetchall()
            self.assertEqual(relaciones, [])

            campos = ','.join(['fila_fuente', *COLUMNAS.values()])

            fuente = con.execute(
                f"""
                SELECT {campos}
                FROM stg_mortalidad
                WHERE nivel_geografico = 'local'
                ORDER BY fila_fuente
                """
            ).fetchall()

            reconstruido = con.execute(
                f"""
                SELECT {campos}
                FROM vw_mortalidad
                ORDER BY fila_fuente
                """
            ).fetchall()

            self.assertEqual(fuente, reconstruido)

    def test_repetir_carga_no_duplica(self):
        resultado = cargar(CSV_PATH, self.db)
        self.assertEqual(resultado, self.auditoria)

        with closing(sqlite3.connect(self.db)) as con:
            total = con.execute(
                'SELECT SUM(casos) FROM hecho_mortalidad'
            ).fetchone()[0]
            self.assertEqual(total, 6200)

    def test_fuente_distinta_no_reemplaza_base(self):
        alterado = Path(self.tmp.name) / 'alterado.csv'

        with CSV_PATH.open(encoding='cp1252', newline='') as archivo:
            filas = list(csv.reader(archivo, delimiter=';'))

        filas[1][2] = '99'

        with alterado.open('w', encoding='cp1252', newline='') as archivo:
            csv.writer(archivo, delimiter=';').writerows(filas)

        antes = hashlib.sha256(self.db.read_bytes()).hexdigest()

        with self.assertRaisesRegex(ValueError, 'niveles geográficos'):
            cargar(alterado, self.db)

        despues = hashlib.sha256(self.db.read_bytes()).hexdigest()
        self.assertEqual(antes, despues)


if __name__ == '__main__':
    unittest.main()
