# Caso_Accidentes
# Taller Grupo 6 : ETL-Project: First Delivery

## Integrantes
Laura Torres
Juliana Serrano
Juan Hernandez
Juan Lopéz

# 📋 Asignación de Actividades y Roles del Proyecto

Este documento detalla la distribución de tareas, responsabilidades y entregables asignados a cada integrante del equipo para el desarrollo del proyecto.

---

## 👥 Equipo de Trabajo y Responsabilidades

### 👩‍💻 Laura Torres
* **Rol / Área:** *Ej. Lógica de Datos / Documentación General*
* **Actividades Asignadas:**
  * [ ] Definición del pipeline de datos y estructura general del proyecto.
  * [ ] Redacción y estandarización del archivo `README.md` y documentación técnica.
  * [ ] Integración de módulos principales.

---

### 👩‍💻 Juliana Serrano
* **Rol / Área:** *Ej. Diseño de Pruebas / Análisis*
* **Actividades Asignadas:**
  * [ ] Análisis exploratorio de datos y verificación de calidad.
  * [ ] Pruebas unitarias y validación del código.
  * [ ] Elaboración de informes de progreso.

---

### 👨‍💻 Juan Hernández
* **Rol / Área:** *Ej. Desarrollo Back-end / Arquitectura*
* **Actividades Asignadas:**
  * [ ] Configuración del entorno de desarrollo y gestión de dependencias.
  * [ ] Implementación de funciones core y lógica del sistema.
  * [ ] Mantenimiento y control de versiones en el repositorio Git.

---

### 👨‍💻 Juan López
* **Rol / Área:** *Ej. Visualización / Despliegue*
* **Actividades Asignadas:**
  * [ ] Diseño de paneles de control y gráficos interactivos.
  * [ ] Optimización del rendimiento de las consultas y scripts.
  * [ ] Preparación del paquete final para la entrega.

---

## 📅 Matriz de Seguimiento de Tareas

| Actividad / Tarea | Responsable | Estado | Fecha Límite |
| :--- | :--- | :---: | :---: |
| Configuración de repositorio y estructura base | **Juan Hernández** | 🟢 Completado | DD/MM/AAAA |
| Redacción de documentación y requerimientos | **Laura Torres** | 🟡 En progreso | DD/MM/AAAA |
| Limpieza y procesamiento de datos | **Juliana Serrano** | 🟡 En progreso | DD/MM/AAAA |
| Desarrollo de visualizaciones e interfaz | **Juan López** | 🔴 Pendiente | DD/MM/AAAA |


---


Primera entrega de ETL: análisis de mortalidad por accidentes de tránsito en Bogotá, con el CSV aportado de SDS / SALUDATA para 2015-2025.

## Hallazgo que afecta la entrega

El CSV contiene **12.386 filas y 18 variables**, pero repite los casos en los niveles distrital (código 0, Bogotá) y local (códigos 1-21). Ambos bloques coinciden exactamente al comparar las otras 16 columnas, incluyendo sus multiplicidades.

El análisis correcto usa **6.193 filas y 6.200 casos**, conservando el detalle local y los casos sin localidad (código 21). La suma bruta de 12.400 cuenta cada caso dos veces. No se fabrican filas ni se eliminan registros solo por parecer iguales.

**El mínimo de 10.000 registros analíticos no está cumplido con esta fuente.** El archivo bruto sí supera ese tamaño. Antes de entregar, se debe confirmar con el profesor si evalúa las filas de origen o las filas analíticas. Si exige las últimas, hay que ampliar la cobertura con datos oficiales compatibles y sin solapamiento, o cambiar la fuente. El código detiene la carga si cambia el patrón geográfico, para exigir una revisión.

## Objetivo y ODS

Describir la evolución temporal, la distribución territorial y los perfiles de las víctimas para orientar preguntas de prevención vial. Se relaciona con el ODS 3, meta 3.6 (muertes y lesiones por tránsito), y el ODS 11, meta 11.2 (transporte seguro). Son conteos y proporciones; no se calculan tasas por población ni se prueban causas.

## Ejecutar en Windows / Visual Studio Code

Se recomienda Python 3.11 o 3.12. Abre la carpeta completa del proyecto en VS Code y abre una terminal. Los comandos siguientes usan PowerShell y no requieren activar el entorno.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.etl
.\.venv\Scripts\python.exe -m src.analisis
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m jupyterlab
```

En Jupyter abre `notebooks/01_eda.ipynb` y ejecuta las celdas de arriba abajo. En VS Code también puedes abrirlo con las extensiones Python y Jupyter, seleccionando el intérprete de `.venv`. El notebook ya incluye resultados; para recalcularlos debes crear primero la base con el ETL.

Verificación realizada: cuatro pruebas del ETL aprobadas y 27 celdas de código ejecutadas con IPython en proceso, con diez imágenes y sin errores. No se abrió un servidor Jupyter en el entorno de preparación porque no permitía conexiones locales. Para repetir esa verificación sin servidor: `python -m src.verificar_notebook` (usa el ejecutable de `.venv` correspondiente).

En macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.etl
.venv/bin/python -m src.analisis
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m jupyterlab
```

La base se crea en `data/processed/accidentes.sqlite`. SQLite es una base relacional real, integrada con Python: admite SQL, claves primarias, claves foráneas y transacciones. La consigna permite elegir la base; PostgreSQL y MySQL aparecen como ejemplos. La base se regenera y está excluida de Git.

## Organización

| Ruta | Contenido |
|---|---|
| `data/raw/` | CSV original sin modificar y metadatos oficiales |
| `src/etl.py` | Validación, limpieza, separación de niveles y carga |
| `sql/modelo.sql` | Cinco dimensiones, tabla de hechos, índices y vista |
| `sql/consultas.sql` | Consultas utilizadas para tablas y gráficos |
| `src/analisis.py` | EDA y diez gráficos consultados desde SQLite |
| `notebooks/01_eda.ipynb` | Notebook con SQL, resultados e interpretaciones |
| `reports/informe_tecnico.md` | Informe técnico editable |
| `reports/informe_tecnico.html` | Informe con gráficos para abrir en el navegador |
| `reports/figures/` | Diez gráficos PNG |
| `reports/tables/` | Tablas de resultados exportadas desde SQL |
| `docs/arquitectura.md` | Arquitectura, grano del hecho y relaciones |
| `docs/diccionario.md` | Mapeo de las 18 variables y reglas |
| `docs/requisitos.md` | Revisión de la rúbrica y pendientes |
| `tests/` | Integridad, totales, recarga y protección ante cambios |

## Herramientas y decisiones

Python permite ejecutar el ETL; `csv` preserva el archivo original y `sqlite3` controla la carga. Pandas facilita el EDA **después de consultar SQL**. Matplotlib genera gráficos reproducibles. Jupyter reúne código, resultados y explicación. Git/GitHub permiten revisar cambios y trabajar en equipo. No hacen falta servicios pagados, contraseñas ni Docker.

Flujo: CSV -> fuente original en SQLite -> staging limpio -> modelo estrella -> consultas SQL -> notebook, tablas y gráficos. El almacén dimensional está en la misma base, apropiado para el tamaño y alcance académico. No hay lectura del CSV en el código de visualización.

## Calidad y límites

- Se conserva `casos` como medida; siete registros del detalle representan dos casos cada uno.
- Se unifican mayúsculas de meses/días, paréntesis de horas y variantes claras de escritura.
- `Sin información` se reporta como ausencia; `No aplica` tiene significado diferente.
- El CSV no permite inferir día del mes, coordenadas, edades exactas ni identificadores personales.
- 250 casos no tienen localidad identificada y 2.051 no tienen día u hora suficientes para el mapa de calor.
- Las categorías de circunstancias y transporte cambian con los años. No se fuerzan equivalencias dudosas.
- Los conteos de años recientes corresponden a esta copia. Tener los 12 meses no certifica un cierre definitivo.
- El metadato menciona cobertura hasta 2026 preliminar; el archivo aportado solo incluye 2015-2025.

## GitHub y entrega

Se partió del commit `9abb753`, cuyo contenido era únicamente el título del README. Los archivos nuevos están preparados para revisar en una rama de desarrollo. No se necesita subir `.venv`, cachés ni la base generada.

Para incorporar la carpeta al repositorio local del equipo, copia el contenido del proyecto (sin reemplazar su carpeta `.git`), revisa `git status`, crea una rama, añade los archivos y haz un commit que describa los cambios. No subas el ZIP como sustituto del código. El equipo debe registrar sus integrantes reales (de 2 a 4) y revisar los resultados antes de entregar.

## Fuentes

- [Datos Abiertos Bogotá: Mortalidad por accidentes de tránsito](https://datosabiertos.bogota.gov.co/dataset/mortalidad-por-accidentes-de-transito).
- Entidad publicadora: Secretaría Distrital de Salud. Fuente indicada en el metadato: Instituto Nacional de Medicina Legal y Ciencias Forenses.
- Licencia del conjunto: Creative Commons Attribution 4.0. Se conserva el CSV aportado sin modificación. Metadatos del portal consultados el 13 de septiembre de 2026.
- [ODS 3](https://sdgs.un.org/goals/goal3) y [ODS 11](https://sdgs.un.org/goals/goal11).
- Documento del curso: `Project - First delivery.pdf`, ETL G51, primera entrega. Indica fecha límite 31 de agosto de 2026, 23:59; confirmar si existe una nueva fecha o consigna.
