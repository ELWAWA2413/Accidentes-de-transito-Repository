"""Carga el CSV y prepara el modelo estrella."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data/raw/osb_evento_transporte.csv'
DB_PATH = ROOT / 'data/processed/accidentes.sqlite'

COLUMNAS = {
    'CODIGO_LOCALIDAD': 'codigo_localidad', 'ANO': 'anio', 'casos': 'casos',
    'Sexo': 'sexo', 'MES_DEL_HECHO': 'mes', 'DIA_DEL_HECHO': 'dia',
    'RANGO_DE_HORA_DEL_HECHO_XXX3_HORAS_': 'franja_hora',
    'PERTENENCIA_GRUPAL': 'pertenencia_grupal',
    'PAIS_DE_NACIMIENTO': 'pais_nacimiento',
    'CLASE_O_TIPO_DE_ACCIDENTE_DE_TRANSPORTE': 'tipo_accidente',
    'CIRCUNSTANCIA_DEL_HECHO_DETALLADA': 'circunstancia',
    'CONDICION_DE_LA_VICTIMA_AT_': 'condicion_victima',
    'MEDIO_DE_DESPLAZAMIENTO_O_TRANSPORTE': 'medio_transporte',
    'OBJETO_DE_COLISION': 'objeto_colision', 'LOCALIDAD': 'localidad',
    'ANCESTRO_RACIAL': 'ancestro_racial', 'PERTENENCIA_ETNICA': 'pertenencia_etnica',
    'CICLO_VITAL': 'ciclo_vital',
}
MESES = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split()
DIAS = 'lunes martes miércoles jueves viernes sábado domingo'.split()
DIMENSIONES = {
    'dim_tiempo': ['anio', 'mes', 'mes_numero', 'dia', 'dia_numero', 'franja_hora', 'hora_inicio'],
    'dim_localidad': ['codigo_localidad', 'localidad', 'ubicacion_conocida'],
    'dim_victima': ['sexo', 'ciclo_vital', 'condicion_victima', 'pais_nacimiento',
                    'pertenencia_grupal', 'ancestro_racial', 'pertenencia_etnica'],
    'dim_transporte': ['medio_transporte', 'objeto_colision'],
    'dim_hecho': ['tipo_accidente', 'circunstancia'],
}


def limpiar_texto(valor):
    texto = ' '.join(unicodedata.normalize('NFC', valor).split())
    if not texto or texto.casefold() in ('sin información', 'sin informacion', 'sin dato'):
        return 'Sin información'
    if texto.casefold() == 'no aplica':
        return 'No aplica'
    return texto


def transformar(original, fila):
    r = {nuevo: limpiar_texto(original[viejo]) for viejo, nuevo in COLUMNAS.items()}
    for campo in ['codigo_localidad', 'anio', 'casos']:
        r[campo] = int(r[campo])
    if r['casos'] <= 0 or not 0 <= r['codigo_localidad'] <= 21:
        raise ValueError(f'Valor inválido en la fila {fila}')
    for campo, orden in [('mes', MESES), ('dia', DIAS)]:
        valor = r[campo].lower()
        if valor not in orden and r[campo] != 'Sin información':
            raise ValueError(f'{campo} no reconocido en la fila {fila}: {valor}')
        r[campo] = valor if valor in orden else 'Sin información'
        r[campo + '_numero'] = orden.index(valor) + 1 if valor in orden else None
    r['franja_hora'] = r['franja_hora'].strip('()')
    franjas = {f'{h:02d}:00 a {h+2:02d}:59': h for h in range(0, 24, 3)}
    if r['franja_hora'] not in franjas and r['franja_hora'] != 'Sin información':
        raise ValueError(f'Franja no reconocida en la fila {fila}')
    r['hora_inicio'] = franjas.get(r['franja_hora'])
    # Solo unificamos variantes de escritura claras.
    for campo in ['medio_transporte', 'objeto_colision']:
        r[campo] = {'Microbus': 'Microbús', 'Tracto – camión': 'Tractocamión',
                    'Avión – avioneta': 'Avión, Avioneta'}.get(r[campo], r[campo])
    r['ancestro_racial'] = {'Indigena': 'Indígena'}.get(r['ancestro_racial'], r['ancestro_racial'])
    r['nivel_geografico'] = 'distrital' if r['codigo_localidad'] == 0 else 'local'
    r['ubicacion_conocida'] = int(1 <= r['codigo_localidad'] <= 20)
    r['fila_fuente'] = fila
    return r


def cargar(csv_path=CSV_PATH, db_path=DB_PATH):
    csv_path, db_path = Path(csv_path), Path(db_path)
    with csv_path.open(encoding='cp1252', newline='') as archivo:
        lector = csv.DictReader(archivo, delimiter=';')
        if lector.fieldnames != list(COLUMNAS):
            raise ValueError('Las columnas del CSV cambiaron. Revisar antes de cargar.')
        originales = list(lector)
    if not originales:
        raise ValueError('El archivo está vacío.')

    # Bogotá y las localidades repiten los mismos casos.
    campos = [c for c in COLUMNAS if c not in ('CODIGO_LOCALIDAD', 'LOCALIDAD')]
    distrital = Counter(tuple(r[c] for c in campos) for r in originales if r['CODIGO_LOCALIDAD'] == '0')
    local = Counter(tuple(r[c] for c in campos) for r in originales if r['CODIGO_LOCALIDAD'] != '0')
    if not distrital or distrital != local:
        raise ValueError('Los niveles geográficos ya no coinciden. Revisar la fuente; no se cargó.')
    limpios = [transformar(r, i) for i, r in enumerate(originales, start=2)]
    detalle = [r for r in limpios if r['nivel_geografico'] == 'local']
    auditoria = {
        'sha256_csv': hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        'filas_originales': len(originales), 'columnas_originales': len(COLUMNAS),
        'suma_bruta_no_utilizar': sum(r['casos'] for r in limpios),
        'filas_distritales_excluidas_del_hecho': len(limpios) - len(detalle),
        'replica_geografica_exacta': True,
        'filas_analiticas': len(detalle), 'casos_analiticos': sum(r['casos'] for r in detalle),
        'duplicados_exactos_fuente_excedentes': len(originales) - len(set(tuple(r.values()) for r in originales)),
        'duplicados_exactos_detalle_excedentes': len(detalle) - len(set(tuple(r[c] for c in COLUMNAS) for r in originales if r['CODIGO_LOCALIDAD'] != '0')),
        'minimo_10000_fuente': len(originales) >= 10000,
        'minimo_10000_analitico': len(detalle) >= 10000,
    }
    db_path.parent.mkdir(parents=True, exist_ok=True)
    temporal = db_path.with_suffix('.tmp')
    temporal.unlink(missing_ok=True)
    con = sqlite3.connect(temporal)
    try:
        con.executescript((ROOT / 'sql/modelo.sql').read_text(encoding='utf-8'))
        with con:
            definicion = ', '.join(f'"{c}" TEXT' for c in COLUMNAS)
            con.execute(f'CREATE TABLE fuente_original (fila_fuente INTEGER PRIMARY KEY, {definicion})')
            marcas = ','.join('?' for _ in range(len(COLUMNAS) + 1))
            con.executemany(f'INSERT INTO fuente_original VALUES ({marcas})',
                            [(i, *r.values()) for i, r in enumerate(originales, start=2)])
            columnas = list(limpios[0])
            numericos = {'codigo_localidad', 'anio', 'casos', 'mes_numero', 'dia_numero',
                         'hora_inicio', 'ubicacion_conocida', 'fila_fuente'}
            definicion = ','.join(f'{c} {"INTEGER" if c in numericos else "TEXT"}' for c in columnas)
            con.execute(f'CREATE TABLE stg_mortalidad ({definicion})')
            marcas = ','.join('?' for _ in columnas)
            con.executemany(f'INSERT INTO stg_mortalidad VALUES ({marcas})',
                            [tuple(r[c] for c in columnas) for r in limpios])
            mapas = {}
            for tabla, campos_dim in DIMENSIONES.items():
                claves = list(dict.fromkeys(tuple(r[c] for c in campos_dim) for r in detalle))
                mapas[tabla] = {clave: i for i, clave in enumerate(claves, start=1)}
                marcas = ','.join('?' for _ in range(len(campos_dim) + 1))
                con.executemany(f'INSERT INTO {tabla} VALUES ({marcas})',
                                [(i, *clave) for clave, i in mapas[tabla].items()])
            for i, r in enumerate(detalle, start=1):
                ids = [mapas[t][tuple(r[c] for c in cols)] for t, cols in DIMENSIONES.items()]
                con.execute('INSERT INTO hecho_mortalidad VALUES (?,?,?,?,?,?,?,?)',
                            (i, r['fila_fuente'], *ids, r['casos']))
            con.execute('CREATE TABLE auditoria (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)')
            con.executemany('INSERT INTO auditoria VALUES (?,?)',
                            [(k, json.dumps(v, ensure_ascii=False)) for k, v in auditoria.items()])
        if con.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Se encontraron claves sin relación.')
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('La base no pasó la validación de integridad.')
        total = con.execute('SELECT COUNT(*), SUM(casos) FROM vw_mortalidad').fetchone()
        if total != (len(detalle), auditoria['casos_analiticos']):
            raise ValueError('El total no coincide después de la carga.')
    except Exception:
        con.close()
        temporal.unlink(missing_ok=True)
        raise
    con.close()
    temporal.replace(db_path)
    return auditoria


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=CSV_PATH)
    parser.add_argument('--db', type=Path, default=DB_PATH)
    args = parser.parse_args()
    print(json.dumps(cargar(args.csv, args.db), indent=2, ensure_ascii=False))
