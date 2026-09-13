PRAGMA foreign_keys = ON;

CREATE TABLE dim_tiempo (
    id INTEGER PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes TEXT NOT NULL,
    mes_numero INTEGER CHECK (mes_numero BETWEEN 1 AND 12),
    dia TEXT NOT NULL,
    dia_numero INTEGER CHECK (dia_numero BETWEEN 1 AND 7),
    franja_hora TEXT NOT NULL,
    hora_inicio INTEGER CHECK (hora_inicio BETWEEN 0 AND 23)
);
CREATE TABLE dim_localidad (
    id INTEGER PRIMARY KEY,
    codigo_localidad INTEGER NOT NULL,
    localidad TEXT NOT NULL,
    ubicacion_conocida INTEGER NOT NULL CHECK (ubicacion_conocida IN (0,1))
);
CREATE TABLE dim_victima (
    id INTEGER PRIMARY KEY,
    sexo TEXT NOT NULL,
    ciclo_vital TEXT NOT NULL,
    condicion_victima TEXT NOT NULL,
    pais_nacimiento TEXT NOT NULL,
    pertenencia_grupal TEXT NOT NULL,
    ancestro_racial TEXT NOT NULL,
    pertenencia_etnica TEXT NOT NULL
);
CREATE TABLE dim_transporte (
    id INTEGER PRIMARY KEY,
    medio_transporte TEXT NOT NULL,
    objeto_colision TEXT NOT NULL
);
CREATE TABLE dim_hecho (
    id INTEGER PRIMARY KEY,
    tipo_accidente TEXT NOT NULL,
    circunstancia TEXT NOT NULL
);
CREATE TABLE hecho_mortalidad (
    id INTEGER PRIMARY KEY,
    fila_fuente INTEGER NOT NULL UNIQUE,
    tiempo_id INTEGER NOT NULL REFERENCES dim_tiempo(id),
    localidad_id INTEGER NOT NULL REFERENCES dim_localidad(id),
    victima_id INTEGER NOT NULL REFERENCES dim_victima(id),
    transporte_id INTEGER NOT NULL REFERENCES dim_transporte(id),
    hecho_id INTEGER NOT NULL REFERENCES dim_hecho(id),
    casos INTEGER NOT NULL CHECK (casos > 0)
);
CREATE INDEX idx_hecho_tiempo ON hecho_mortalidad(tiempo_id);
CREATE INDEX idx_hecho_localidad ON hecho_mortalidad(localidad_id);
CREATE INDEX idx_hecho_victima ON hecho_mortalidad(victima_id);

CREATE VIEW vw_mortalidad AS
SELECT f.fila_fuente, f.casos,
       t.anio, t.mes, t.mes_numero, t.dia, t.dia_numero,
       t.franja_hora, t.hora_inicio,
       l.codigo_localidad, l.localidad, l.ubicacion_conocida,
       v.sexo, v.ciclo_vital, v.condicion_victima, v.pais_nacimiento,
       v.pertenencia_grupal, v.ancestro_racial, v.pertenencia_etnica,
       tr.medio_transporte, tr.objeto_colision,
       h.tipo_accidente, h.circunstancia
FROM hecho_mortalidad f
JOIN dim_tiempo t ON t.id = f.tiempo_id
JOIN dim_localidad l ON l.id = f.localidad_id
JOIN dim_victima v ON v.id = f.victima_id
JOIN dim_transporte tr ON tr.id = f.transporte_id
JOIN dim_hecho h ON h.id = f.hecho_id;
