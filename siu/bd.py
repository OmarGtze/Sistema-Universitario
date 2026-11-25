"""Conexión a la base de datos, creación de tablas y datos de prueba."""
import os
import sqlite3

from siu.seguridad import generar_hash

RUTA_BD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "universidad.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS carreras(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    correo TEXT,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL,
    carrera_id INTEGER REFERENCES carreras(id)
);
CREATE TABLE IF NOT EXISTS materias(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    creditos INTEGER,
    cupo INTEGER,
    docente_id INTEGER REFERENCES usuarios(id)
);
CREATE TABLE IF NOT EXISTS inscripciones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL REFERENCES usuarios(id),
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    ciclo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS calificaciones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inscripcion_id INTEGER NOT NULL REFERENCES inscripciones(id),
    valor REAL
);
CREATE TABLE IF NOT EXISTS solicitudes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT,
    estudiante_id INTEGER NOT NULL REFERENCES usuarios(id),
    tipo TEXT,
    fecha TEXT,
    estado TEXT
);
"""

CARRERAS = [("INNI", "Ingeniería Informática"), ("INCO", "Ingeniería en Computación")]

# (codigo, nombre, correo, contraseña, rol, carrera)
USUARIOS = [
    ("A0001", "Laura Ríos Vega", "laura.rios@udg.mx", "admin123", "administrador", None),
    ("D1001", "Carlos Méndez Soto", "carlos.mendez@udg.mx", "docente123", "docente", None),
    ("D1002", "Mariana Torres Gil", "mariana.torres@udg.mx", "docente123", "docente", None),
    ("218001234", "Ana López Ruiz", "ana.lopez@alumnos.udg.mx", "ana123", "estudiante", "INNI"),
    ("218005678", "Luis Pérez Nava", "luis.perez@alumnos.udg.mx", "luis123", "estudiante", "INNI"),
]

# (clave, nombre, créditos, cupo, código del docente)
MATERIAS = [
    ("IS101", "Ingeniería de Software", 8, 40, "D1001"),
    ("BD201", "Bases de Datos", 8, 2, "D1002"),
    ("PR102", "Programación", 8, 35, "D1001"),
]

# (código del estudiante, clave de la materia, ciclo, calificación o None)
INSCRIPCIONES = [
    ("218001234", "IS101", "2026B", 92),
    ("218001234", "BD201", "2026B", None),
    ("218005678", "IS101", "2026B", None),
]


def conectar(ruta=RUTA_BD):
    """Abre una conexión con la base de datos y la deja lista para usarse."""
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    inicializar(con)
    return con


def inicializar(con):
    con.executescript(ESQUEMA)
    if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        cargar_datos_iniciales(con)
    con.commit()


def _id(con, tabla, columna, valor):
    fila = con.execute(f"SELECT id FROM {tabla} WHERE {columna} = ?", (valor,)).fetchone()
    return fila["id"] if fila else None


def cargar_datos_iniciales(con):
    con.executemany("INSERT INTO carreras(clave, nombre) VALUES (?, ?)", CARRERAS)
    for codigo, nombre, correo, contrasena, rol, carrera in USUARIOS:
        con.execute(
            "INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES (?, ?, ?, ?, ?, ?)",
            (codigo, nombre, correo, generar_hash(contrasena), rol, _id(con, "carreras", "clave", carrera)),
        )
    for clave, nombre, creditos, cupo, docente in MATERIAS:
        con.execute(
            "INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES (?, ?, ?, ?, ?)",
            (clave, nombre, creditos, cupo, _id(con, "usuarios", "codigo", docente)),
        )
    for alumno, materia, ciclo, calificacion in INSCRIPCIONES:
        cur = con.execute(
            "INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES (?, ?, ?)",
            (_id(con, "usuarios", "codigo", alumno), _id(con, "materias", "clave", materia), ciclo),
        )
        if calificacion is not None:
            con.execute("INSERT INTO calificaciones(inscripcion_id, valor) VALUES (?, ?)",
                        (cur.lastrowid, calificacion))
