"""Capa de acceso a datos: todas las consultas SQL del sistema están en este módulo.

Todas las consultas son parametrizadas (usan ?), por lo que los datos escritos por el
usuario nunca se mezclan con el texto de la consulta.
"""


# ---------- usuarios ----------
def buscar_usuario_por_codigo(con, codigo):
    return con.execute("SELECT * FROM usuarios WHERE codigo = ?", (codigo,)).fetchone()


def buscar_usuario_por_correo(con, correo):
    return con.execute("SELECT * FROM usuarios WHERE LOWER(correo) = LOWER(?)", (correo,)).fetchone()


def insertar_usuario(con, codigo, nombre, correo, contrasena_hash, rol, carrera_id):
    con.execute(
        "INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES (?, ?, ?, ?, ?, ?)",
        (codigo, nombre, correo, contrasena_hash, rol, carrera_id),
    )
    con.commit()


# ---------- materias e inscripciones ----------
def buscar_materia_por_clave(con, clave):
    return con.execute("SELECT * FROM materias WHERE clave = ?", (clave,)).fetchone()


def insertar_materia(con, clave, nombre, creditos, cupo, docente_id):
    con.execute(
        "INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES (?, ?, ?, ?, ?)",
        (clave, nombre, creditos, cupo, docente_id),
    )
    con.commit()


def materias_de_docente(con, docente_id):
    return con.execute("SELECT * FROM materias WHERE docente_id = ? ORDER BY clave", (docente_id,)).fetchall()


def insertar_inscripcion(con, estudiante_id, materia_id, ciclo):
    con.execute(
        "INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES (?, ?, ?)",
        (estudiante_id, materia_id, ciclo),
    )
    con.commit()


def contar_inscritos(con, materia_id, ciclo):
    return con.execute(
        "SELECT COUNT(*) FROM inscripciones WHERE materia_id = ? AND ciclo = ?", (materia_id, ciclo)
    ).fetchone()[0]


def materias_de_estudiante(con, estudiante_id):
    return con.execute(
        "SELECT m.clave, m.nombre, i.ciclo, c.valor FROM inscripciones i "
        "JOIN materias m ON m.id = i.materia_id "
        "LEFT JOIN calificaciones c ON c.inscripcion_id = i.id "
        "WHERE i.estudiante_id = ? ORDER BY i.ciclo, m.clave",
        (estudiante_id,),
    ).fetchall()


def alumnos_de_materia(con, materia_id):
    return con.execute(
        "SELECT i.id AS inscripcion_id, u.codigo, u.nombre, c.valor FROM inscripciones i "
        "JOIN usuarios u ON u.id = i.estudiante_id "
        "LEFT JOIN calificaciones c ON c.inscripcion_id = i.id "
        "WHERE i.materia_id = ? ORDER BY u.nombre",
        (materia_id,),
    ).fetchall()


# ---------- calificaciones ----------
def guardar_calificacion(con, inscripcion_id, valor):
    """Registra la calificación de una inscripción o la actualiza si ya existía (nunca la duplica)."""
    existente = con.execute("SELECT id FROM calificaciones WHERE inscripcion_id = ?", (inscripcion_id,)).fetchone()
    if existente:
        con.execute("UPDATE calificaciones SET valor = ? WHERE id = ?", (valor, existente["id"]))
    else:
        con.execute("INSERT INTO calificaciones(inscripcion_id, valor) VALUES (?, ?)", (inscripcion_id, valor))
    con.commit()


# ---------- solicitudes ----------
def siguiente_numero_solicitud(con):
    return con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM solicitudes").fetchone()[0]


def insertar_solicitud(con, folio, estudiante_id, tipo, fecha):
    con.execute(
        "INSERT INTO solicitudes(folio, estudiante_id, tipo, fecha, estado) VALUES (?, ?, ?, ?, 'Pendiente')",
        (folio, estudiante_id, tipo, fecha),
    )
    con.commit()


def solicitudes_de_estudiante(con, estudiante_id):
    return con.execute(
        "SELECT folio, tipo, fecha, estado FROM solicitudes WHERE estudiante_id = ? ORDER BY id",
        (estudiante_id,),
    ).fetchall()


def todas_las_solicitudes(con):
    return con.execute(
        "SELECT s.folio, u.codigo, s.tipo, s.fecha, s.estado FROM solicitudes s "
        "JOIN usuarios u ON u.id = s.estudiante_id ORDER BY s.id"
    ).fetchall()


def actualizar_estado_solicitud(con, folio, estado):
    con.execute("UPDATE solicitudes SET estado = ? WHERE folio = ?", (estado, folio))
    con.commit()
