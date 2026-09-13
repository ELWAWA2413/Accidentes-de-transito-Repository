"""Tablas y gráficos consultados desde SQLite."""

import argparse
import json
from pathlib import Path
import re
import sqlite3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from src.etl import DB_PATH, ROOT, COLUMNAS, DIAS


def conectar(db_path=DB_PATH):
    # Solo lectura: no creamos una base vacía por error.
    return sqlite3.connect(Path(db_path).resolve().as_uri() + '?mode=ro', uri=True)


def consultas():
    texto = (ROOT / 'sql/consultas.sql').read_text(encoding='utf-8')
    partes = re.split(r'-- consulta: (\w+)\n', texto)
    return {partes[i]: partes[i + 1].strip() for i in range(1, len(partes), 2)}


def perfil(con):
    filas = []
    for campo in COLUMNAS.values():
        # Los nombres de columnas vienen de nuestra lista fija.
        sql = f'''SELECT COUNT(*) AS registros, COUNT(DISTINCT "{campo}") AS categorias,
            SUM("{campo}" IS NULL) AS nulos,
            SUM(CASE WHEN "{campo}" = 'Sin información' THEN 1 ELSE 0 END) AS sin_informacion,
            SUM(CASE WHEN "{campo}" = 'No aplica' THEN 1 ELSE 0 END) AS no_aplica
            FROM stg_mortalidad WHERE nivel_geografico = 'local' '''
        r = pd.read_sql_query(sql, con).iloc[0].to_dict()
        r['campo'] = campo
        r['pct_sin_informacion'] = round(100 * r['sin_informacion'] / r['registros'], 2)
        filas.append(r)
    return pd.DataFrame(filas)[['campo', 'registros', 'categorias', 'nulos', 'sin_informacion', 'pct_sin_informacion', 'no_aplica']]


def generar(db_path=DB_PATH, output=ROOT / 'reports'):
    output = Path(output)
    figuras, tablas = output / 'figures', output / 'tables'
    figuras.mkdir(parents=True, exist_ok=True)
    tablas.mkdir(parents=True, exist_ok=True)
    with conectar(db_path) as con:
        datos = {nombre: pd.read_sql_query(sql, con) for nombre, sql in consultas().items()}
        datos['calidad_campos'] = perfil(con)
        auditoria = {k: json.loads(v) for k, v in con.execute('SELECT clave, valor FROM auditoria')}
        resumen = pd.read_sql_query('''SELECT COUNT(*) AS registros, SUM(casos) AS casos,
            SUM(CASE WHEN ubicacion_conocida = 0 THEN casos ELSE 0 END) AS sin_localidad,
            SUM(CASE WHEN dia_numero IS NULL OR hora_inicio IS NULL THEN casos ELSE 0 END) AS sin_dia_hora,
            SUM(CASE WHEN mes_numero IS NULL THEN casos ELSE 0 END) AS sin_mes
            FROM vw_mortalidad''', con).iloc[0].to_dict()
        datos['descripcion_casos'] = pd.read_sql_query('SELECT casos FROM hecho_mortalidad', con).describe().reset_index()
    anual = datos['anual']
    anual['variacion_pct'] = (anual.casos.pct_change() * 100).round(2)
    for nombre, tabla in datos.items():
        tabla.to_csv(tablas / f'{nombre}.csv', index=False, encoding='utf-8-sig')
    resumen = {k: int(v) for k, v in resumen.items()}
    resumen['auditoria'] = auditoria
    (output / 'resumen.json').write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.titleweight': 'bold', 'figure.facecolor': 'white'})

    def guardar(fig, nombre, nota='Fuente: CSV aportado de SDS / SALUDATA. Consulta SQL sobre el detalle local; 2015-2025.'):
        fig.text(.02, .015, nota, fontsize=8, color='#555555')
        fig.tight_layout(rect=(0, .045, 1, 1))
        fig.savefig(figuras / f'{nombre}.png', dpi=150, bbox_inches='tight')
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(anual.anio, anual.casos, marker='o', color='#126a80', linewidth=2)
    for _, r in anual.iterrows():
        ax.annotate(str(int(r.casos)), (r.anio, r.casos), xytext=(0, 9), textcoords='offset points', ha='center')
    ax.set(xticks=anual.anio, xlabel='Año del hecho', ylabel='Casos registrados',
           title='Evolución anual de la mortalidad registrada')
    ax.set_ylim(0, anual.casos.max() * 1.2)
    ax.grid(axis='y', alpha=.2)
    guardar(fig, '01_evolucion_anual')

    for nombre, campo, titulo, archivo in [
        ('localidades', 'localidad', 'Casos por localidad conocida', '02_localidades'),
        ('victimas', 'condicion_victima', 'Condición de la víctima', '03_victimas'),
        ('transporte', 'medio_transporte', 'Diez medios de transporte con más casos', '04_transporte'),
        ('ciclo_vital', 'ciclo_vital', 'Casos por ciclo vital', '05_ciclo_vital'),
        ('sexo', 'sexo', 'Casos por sexo registrado', '06_sexo')]:
        d = datos[nombre].head(10) if nombre == 'transporte' else datos[nombre]
        d = d.iloc[::-1]
        fig, ax = plt.subplots(figsize=(10, max(3.4, len(d) * .30 + 1.4)))
        ax.barh(d[campo], d.casos, color='#126a80')
        ax.bar_label(ax.containers[0], padding=3, fontsize=9)
        ax.set(title=titulo, xlabel='Casos registrados', xlim=(0, d.casos.max() * 1.18))
        nota = f'Excluye {resumen["sin_localidad"]} casos sin localidad identificada. Los totales no son tasas de riesgo.' if nombre == 'localidades' else 'Fuente: consulta SQL sobre el detalle local. Se suma casos; no se cuentan filas.'
        guardar(fig, archivo, nota)

    d = datos['dia_hora'].pivot(index='dia_numero', columns='hora_inicio', values='casos').reindex(index=range(1, 8), columns=range(0, 24, 3)).fillna(0)
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(d, cmap='YlGnBu', aspect='auto')
    ax.set(xticks=range(8), xticklabels=[f'{h:02d}-{h+2:02d} h' for h in range(0, 24, 3)],
           yticks=range(7), yticklabels=DIAS, title='Casos por día de la semana y franja horaria')
    for i in range(7):
        for j in range(8):
            ax.text(j, i, int(d.iloc[i, j]), ha='center', va='center', fontsize=9,
                    color='white' if d.iloc[i, j] > d.to_numpy().max() * .6 else '#222222')
    fig.colorbar(im, ax=ax, label='Casos')
    guardar(fig, '07_dia_hora', f'Excluye {resumen["sin_dia_hora"]} casos sin día o sin hora. Son conteos acumulados, no tasas por exposición.')

    fig, ax = plt.subplots(figsize=(10, 4.3))
    d = datos['calidad_campos'].sort_values('pct_sin_informacion').tail(8)
    ax.barh(d.campo, d.pct_sin_informacion, color='#c87b35')
    ax.bar_label(ax.containers[0], fmt='%.1f%%', padding=3)
    ax.set(title='Campos con mayor falta de información', xlabel='% de registros analíticos', xlim=(0, 112))
    guardar(fig, '08_calidad', '“Sin información” es un faltante semántico. “No aplica” se conserva como categoría diferente.')

    fig, ax = plt.subplots(figsize=(10, 4.5))
    d = datos['calidad_anual']
    for campo, etiqueta in [('pct_sin_circunstancia', 'Sin circunstancia'), ('pct_sin_hora', 'Sin hora'), ('pct_sin_localidad', 'Sin localidad')]:
        ax.plot(d.anio, d[campo], marker='o', label=etiqueta)
    ax.set(title='Calidad del registro a través del tiempo', ylabel='% de casos', xticks=d.anio, ylim=(0, 105))
    ax.legend()
    guardar(fig, '09_calidad_anual')

    fig, ax = plt.subplots(figsize=(10, 4.5))
    d = datos['meses']
    ax.bar(d.mes.str[:3], d.casos, color='#126a80')
    ax.set(title='Distribución mensual acumulada', ylabel='Casos registrados', xlabel='Mes del hecho')
    guardar(fig, '10_meses', f'Excluye {resumen["sin_mes"]} casos sin mes. La cobertura de cada año se revisa en cobertura_mensual.csv.')
    return datos, resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DB_PATH)
    parser.add_argument('--output', type=Path, default=ROOT / 'reports')
    args = parser.parse_args()
    _, resumen = generar(args.db, args.output)
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
