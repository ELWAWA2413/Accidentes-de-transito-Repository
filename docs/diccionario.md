# Diccionario y reglas

| Campo de origen | Nombre en staging / vista | Uso |
|---|---|---|
| CODIGO_LOCALIDAD | codigo_localidad | Código geográfico: 0 distrital; 1-20 localidades; 21 sin dato. |
| ANO | anio | Año del hecho; entero. |
| casos | casos | Número de casos; entero positivo y medida que se suma. |
| Sexo | sexo | Sexo registrado. |
| MES_DEL_HECHO | mes | Mes; normalizado a minúsculas y ordenado 1-12. |
| DIA_DEL_HECHO | dia | Día de semana, no día del mes; orden lunes a domingo. |
| RANGO_DE_HORA_DEL_HECHO_XXX3_HORAS_ | franja_hora | Intervalo de tres horas; se quitan paréntesis externos. |
| PERTENENCIA_GRUPAL | pertenencia_grupal | Pertenencia grupal reportada. |
| PAIS_DE_NACIMIENTO | pais_nacimiento | País de nacimiento reportado. |
| CLASE_O_TIPO_DE_ACCIDENTE_DE_TRANSPORTE | tipo_accidente | Clasificación del accidente; no se fusionan categorías dudosas. |
| CIRCUNSTANCIA_DEL_HECHO_DETALLADA | circunstancia | Circunstancia registrada; no demuestra causalidad. |
| CONDICION_DE_LA_VICTIMA_AT_ | condicion_victima | Conductor, pasajero, peatón o sin información. |
| MEDIO_DE_DESPLAZAMIENTO_O_TRANSPORTE | medio_transporte | Medio utilizado; No aplica no se cambia automáticamente por peatón. |
| OBJETO_DE_COLISION | objeto_colision | Objeto con el que se registra la colisión. |
| LOCALIDAD | localidad | Nombre del lugar; se conserva sin ubicación como faltante. |
| ANCESTRO_RACIAL | ancestro_racial | Categoría publicada; se corrige Indigena a Indígena. |
| PERTENENCIA_ETNICA | pertenencia_etnica | Pertenencia reportada; No aplica se diferencia de ausencia. |
| CICLO_VITAL | ciclo_vital | Grupo de edad publicado; no permite calcular edad exacta. |

El CSV original usa separador punto y coma y se interpreta como Windows-1252. El SHA-256 se guarda en la tabla `auditoria` y en `reports/resumen.json`. No se cambia el archivo original.

Se normalizan espacios y Unicode, las variantes de “Sin información” y “Sin dato”, y la escritura de “No aplica”. En transporte se unifican Microbus/Microbús, Tracto – camión/Tractocamión y Avión – avioneta/Avión, Avioneta. No se unen Choque y Choque con otro vehículo, ni Otra y Otro, sin un diccionario que justifique equivalencias.

Los faltantes numéricos derivados (mes_numero, dia_numero, hora_inicio) se guardan como NULL. Los faltantes categóricos se conservan explícitos y se cuantifican en calidad_campos.csv. “Ninguno” no se trata como vacío.

El metadato define un indicador de tasa por 100.000 habitantes, pero este CSV no contiene el denominador poblacional. El proyecto analiza casos y proporciones, no reproduce esa tasa. El campo ciclo_vital contiene un registro “Fetos”; se conserva y se señala para revisión del publicador, sin recodificarlo ni inventar su edad.
