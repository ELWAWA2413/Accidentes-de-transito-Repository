-- consulta: anual
SELECT anio, COUNT(*) AS registros, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY anio ORDER BY anio;

-- consulta: localidades
SELECT codigo_localidad, localidad, SUM(casos) AS casos
FROM vw_mortalidad WHERE ubicacion_conocida = 1
GROUP BY codigo_localidad, localidad ORDER BY casos DESC;

-- consulta: sexo
SELECT sexo, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY sexo ORDER BY casos DESC;

-- consulta: victimas
SELECT condicion_victima, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY condicion_victima ORDER BY casos DESC;

-- consulta: transporte
SELECT medio_transporte, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY medio_transporte ORDER BY casos DESC;

-- consulta: ciclo_vital
SELECT ciclo_vital, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY ciclo_vital ORDER BY casos DESC;

-- consulta: dia_hora
SELECT dia, dia_numero, franja_hora, hora_inicio, SUM(casos) AS casos
FROM vw_mortalidad WHERE dia_numero IS NOT NULL AND hora_inicio IS NOT NULL
GROUP BY dia, dia_numero, franja_hora, hora_inicio ORDER BY dia_numero, hora_inicio;

-- consulta: meses
SELECT mes, mes_numero, SUM(casos) AS casos
FROM vw_mortalidad WHERE mes_numero IS NOT NULL
GROUP BY mes, mes_numero ORDER BY mes_numero;

-- consulta: calidad_anual
SELECT anio, SUM(casos) AS casos,
 ROUND(100.0 * SUM(CASE WHEN circunstancia = 'Sin información' THEN casos ELSE 0 END) / SUM(casos), 2) AS pct_sin_circunstancia,
 ROUND(100.0 * SUM(CASE WHEN hora_inicio IS NULL THEN casos ELSE 0 END) / SUM(casos), 2) AS pct_sin_hora,
 ROUND(100.0 * SUM(CASE WHEN ubicacion_conocida = 0 THEN casos ELSE 0 END) / SUM(casos), 2) AS pct_sin_localidad
FROM vw_mortalidad GROUP BY anio ORDER BY anio;

-- consulta: tipos_por_anio
SELECT anio, tipo_accidente, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY anio, tipo_accidente ORDER BY anio, casos DESC;

-- consulta: circunstancias
SELECT circunstancia, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY circunstancia ORDER BY casos DESC;

-- consulta: sexo_ciclo
SELECT sexo, ciclo_vital, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY sexo, ciclo_vital ORDER BY ciclo_vital, sexo;

-- consulta: cobertura_mensual
SELECT anio, mes_numero, SUM(casos) AS casos
FROM vw_mortalidad GROUP BY anio, mes_numero ORDER BY anio, mes_numero;
