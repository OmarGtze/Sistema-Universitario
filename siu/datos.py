"""Capa de acceso a datos: todas las consultas SQL del sistema están en este módulo."""


# ---------- usuarios ----------
def buscar_usuario_por_credenciales(con, codigo, contrasena):
    return con.execute(
        f"SELECT * FROM usuarios WHERE codigo = '{codigo}' AND contrasena = '{contrasena}'"
    ).fetchone()


def buscar_usuario_por_codigo(con, codigo):
    return con.execute(f"SELECT * FROM usuarios WHERE codigo = '{codigo}'").fetchone()


def insertar_usuario(con, codigo, nombre, correo, contrasena, rol, carrera_id):
    con.execute(
        f"INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) "
        f"VALUES ('{codigo}', '{nombre}', '{correo}', '{contrasena}', '{rol}', {carrera_id})"
    )
    con.commit()


# ---------- materias e inscripciones ----------
def buscar_materia_por_clave(con, clave):
    return con.execute(f"SELECT * FROM materias WHERE clave = '{clave}'").fetchone()


def insertar_materia(con, clave, nombre, creditos, cupo, docente_id):
    con.execute(
        f"INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) "
        f"VALUES ('{clave}', '{nombre}', {creditos}, {cupo}, {docente_id})"
    )
    con.commit()


def materias_de_docente(con, docente_id):
    return con.execute(f"SELECT * FROM materias WHERE docente_id = {docente_id} ORDER BY clave").fetchall()


def insertar_inscripcion(con, estudiante_id, materia_id, ciclo):
    con.execute(
        f"INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES ({estudiante_id}, {materia_id}, '{ciclo}')"
    )
    con.commit()


def materias_de_estudiante(con, estudiante_id):
    return con.execute(
        "SELECT m.clave, m.nombre, i.ciclo, c.valor FROM inscripciones i "
        "JOIN materias m ON m.id = i.materia_id "
        "LEFT JOIN calificaciones c ON c.inscripcion_id = i.id "
        f"WHERE i.estudiante_id = {estudiante_id} ORDER BY i.ciclo, m.clave"
    ).fetchall()


def alumnos_de_materia(con, materia_id):
    return con.execute(
        "SELECT i.id AS inscripcion_id, u.codigo, u.nombre, c.valor FROM inscripciones i "
        "JOIN usuarios u ON u.id = i.estudiante_id "
        "LEFT JOIN calificaciones c ON c.inscripcion_id = i.id "
        f"WHERE i.materia_id = {materia_id} ORDER BY u.nombre"
    ).fetchall()


# ---------- calificaciones ----------
def insertar_calificacion(con, inscripcion_id, valor):
    con.execute(f"INSERT INTO calificaciones(inscripcion_id, valor) VALUES ({inscripcion_id}, {valor})")
    con.commit()


# ---------- solicitudes ----------
def insertar_solicitud(con, folio, estudiante_id, tipo, fecha):
    con.execute(
        f"INSERT INTO solicitudes(folio, estudiante_id, tipo, fecha, estado) "
        f"VALUES ('{folio}', {estudiante_id}, '{tipo}', '{fecha}', 'Pendiente')"
    )
    con.commit()


def solicitudes_de_estudiante(con, estudiante_id):
    return con.execute(
        f"SELECT folio, tipo, fecha, estado FROM solicitudes WHERE estudiante_id = {estudiante_id} ORDER BY id"
    ).fetchall()


def todas_las_solicitudes(con):
    return con.execute(
        "SELECT s.folio, u.codigo, s.tipo, s.fecha, s.estado FROM solicitudes s "
        "JOIN usuarios u ON u.id = s.estudiante_id ORDER BY s.id"
    ).fetchall()


def actualizar_estado_solicitud(con, folio, estado):
    con.execute(f"UPDATE solicitudes SET estado = '{estado}' WHERE folio = '{folio}'")
    con.commit()
