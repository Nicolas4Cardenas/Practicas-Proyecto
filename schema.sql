-- Esquema de base de datos - Sistema Web Control de Plagas en Plátano
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuario (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('campesino', 'profesional')),
    creado_en     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reporte (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id    INTEGER NOT NULL REFERENCES usuario(id),
    descripcion   TEXT NOT NULL,
    ubicacion     TEXT NOT NULL,
    tipo_plaga    TEXT,
    zona          TEXT,
    estado        TEXT NOT NULL DEFAULT 'Reportado'
                  CHECK (estado IN ('Reportado', 'En revisión', 'Diagnosticado', 'Resuelto')),
    creado_en     TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS foto (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id     INTEGER NOT NULL REFERENCES reporte(id) ON DELETE CASCADE,
    nombre_archivo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnostico (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    reporte_id     INTEGER NOT NULL UNIQUE REFERENCES reporte(id),
    profesional_id INTEGER NOT NULL REFERENCES usuario(id),
    texto          TEXT NOT NULL,
    recomendacion  TEXT NOT NULL,
    creado_en      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notificacion (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL REFERENCES usuario(id),
    reporte_id  INTEGER NOT NULL REFERENCES reporte(id),
    mensaje     TEXT NOT NULL,
    leida       INTEGER NOT NULL DEFAULT 0,
    creado_en   TEXT NOT NULL
);
