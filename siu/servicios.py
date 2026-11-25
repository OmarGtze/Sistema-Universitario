"""Capa de lógica de negocio: reglas del sistema universitario."""
import datetime
import random

from siu import datos

TIPOS_CONSTANCIA = ["Constancia de estudios", "Constancia de calificaciones"]
ESTADOS_SOLICITUD = ["Pendiente", "En proceso", "Lista para entrega", "Entregada", "Rechazada"]
ROLES = ["estudiante", "docente", "administrador"]
CALIFICACION_APROBATORIA = 60


class ErrorSistema(Exception):
    """Error que se muestra al usuario."""


# ---------- autenticación ----------
def iniciar_sesion(con, codigo, contrasena):
    usuario = datos.buscar_usuario_por_credenciales(con, codigo, contrasena)
    if usuario is None:
        raise ErrorSistema("Error")
    return usuario


# ---------- estudiante ----------
def calificaciones_de_estudiante(con, estudiante_id):
    filas = []
    for fila in datos.materias_de_estudiante(con, estudiante_id):
        valor = fila["valor"]
        if valor is None:
            estado = "Sin calificación"
        elif valor >= CALIFICACION_APROBATORIA:
            estado = "Aprobada"
        else:
            estado = "Reprobada"
        filas.append({"clave": fila["clave"], "materia": fila["nombre"], "ciclo": fila["ciclo"],
                      "calificacion": valor, "estado": estado})
    return filas


def calcular_promedio(filas):
    valores = [f["calificacion"] for f in filas if f["calificacion"] is not None]
    if not valores:
        return None
    return round(sum(valores) / len(valores), 2)


def solicitar_constancia(con, estudiante_id, tipo):
    folio = "SOL-" + str(random.randint(1, 9999))
    datos.insertar_solicitud(con, folio, estudiante_id, tipo, str(datetime.date.today()))
    return folio


def solicitudes_de_estudiante(con, estudiante_id):
    return datos.solicitudes_de_estudiante(con, estudiante_id)


# ---------- docente ----------
def grupos_de_docente(con, docente_id):
    return datos.materias_de_docente(con, docente_id)


def alumnos_de_materia(con, materia_id):
    return datos.alumnos_de_materia(con, materia_id)


def registrar_calificacion(con, inscripcion_id, valor):
    datos.insertar_calificacion(con, inscripcion_id, float(valor))


# ---------- administrador ----------
def registrar_usuario(con, codigo, nombre, correo, contrasena, rol):
    carrera_id = 1 if rol == "estudiante" else "NULL"
    datos.insertar_usuario(con, codigo, nombre, correo, contrasena, rol, carrera_id)


def registrar_materia(con, clave, nombre, creditos, cupo, codigo_docente):
    docente = datos.buscar_usuario_por_codigo(con, codigo_docente)
    datos.insertar_materia(con, clave, nombre, creditos, cupo, docente["id"])


def inscribir_alumno(con, codigo_alumno, clave_materia, ciclo):
    alumno = datos.buscar_usuario_por_codigo(con, codigo_alumno)
    materia = datos.buscar_materia_por_clave(con, clave_materia)
    datos.insertar_inscripcion(con, alumno["id"], materia["id"], ciclo)


def todas_las_solicitudes(con):
    return datos.todas_las_solicitudes(con)


def atender_solicitud(con, folio, estado):
    datos.actualizar_estado_solicitud(con, folio, estado)
