# Revisión de requisitos de la primera entrega

| Criterio | Peso | Evidencia | Estado |
|---|---:|---|---|
| Alineación con ODS | 4% | README e informe: ODS 3.6 y 11.2 | Implementado |
| Repositorio organizado e historial | 6% | Carpetas de datos, código, SQL, notebook, documentación y pruebas | Archivos preparados; integración remota pendiente |
| README y .gitignore | 10% | Instrucciones Windows/macOS/Linux, justificación del stack y exclusiones | Implementado |
| Migración relacional | 10% | src/etl.py, sql/modelo.sql y auditoría | Ejecutada y verificada |
| EDA profundo y tamaño | 20% | Notebook, calidad, patrones temporales y perfiles | EDA implementado; mínimo analítico de 10.000 pendiente |
| Extracción desde BD | 10% | SQL, vista y conexiones de solo lectura | Implementado |
| Visualizaciones | 20% | Diez gráficos y tablas derivados de SQL | Implementado |
| Informe técnico | 20% | reports/informe_tecnico.md y versión HTML | Implementado |

## Condiciones que el equipo debe resolver

1. **Tamaño analítico:** 12.386 filas de origen, pero 6.193 filas después de retirar el nivel distrital replicado. No declarar 12.386 observaciones independientes. Consultar al profesor la interpretación del mínimo; si exige 10.000 filas analíticas, ampliar con fuentes compatibles sin solapamiento o cambiar de conjunto. No duplicar filas, desagregar artificialmente `casos` ni añadir variables para aparentar el cumplimiento.
2. **Integrantes:** registrar nombres reales de entre 2 y 4 personas, según la consigna. No se proporcionó la lista completa.
3. **Repositorio:** revisar los archivos e incorporarlos al GitHub del equipo con commits informativos. No atribuir cambios a compañeros que no los realizaron.
4. **Fecha y alcance:** el PDF corresponde a la primera entrega y fija el 31/08/2026 a las 23:59. Confirmar cualquier prórroga o documento posterior. Esta revisión no cubre requisitos de entregas no adjuntadas.

La documentación y las pruebas respaldan lo implementado; no equivalen a una garantía de nota ni resuelven la condición del tamaño.
