"""Capa de lógica de negocio: reglas y validaciones del sistema universitario.

Cada función valida los datos recibidos y, si algo es incorrecto, lanza ErrorSistema
con un mensaje claro que la interfaz muestra al usuario.
"""
import datetime
import re

from siu import datos
from siu.seguridad import generar_hash, verificar_contrasena

TIPOS_CONSTANCIA = ["Constancia de estudios", "Constancia de calificaciones"]
ESTADOS_SOLICITUD = ["Pendiente", "En proceso", "Lista para entrega", "Entregada", "Rechazada"]
ESTADOS_FINALES = ["Entregada", "Rechazada"]
ROLES = ["estudiante", "docente", "administrador"]
CALIFICACION_APROBATORIA = 60
CALIFICACION_MINIMA = 0
CALIFICACION_MAXIMA = 100

PATRON_CODIGO = re.compile(r"^[A-Za-z0-9]{4,15}$")
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PATRON_CICLO = re.compile(r"^\d{4}[AB]$")
PATRON_CLAVE_MATERIA = re.compile(r"^[A-Z]{2,4}\d{3}$")


class ErrorSistema(Exception):
    """Error de validación o de negocio que se muestra al usuario."""


# ---------- utilidades de validación ----------
def _obligatorios(**campos):
    vacios = [nombre for nombre, valor in campos.items() if not str(valor).strip()]
    if vacios:
        raise ErrorSistema("Completa los campos obligatorios: " + ", ".join(vacios) + ".")


def _entero_positivo(texto, nombre):
    try:
        numero = int(str(texto).strip())
    except ValueError:
        raise ErrorSistema(f"El campo {nombre} debe ser un número entero.")
    if numero <= 0:
        raise ErrorSistema(f"El campo {nombre} debe ser mayor que cero.")
    return numero


# ---------- autenticación ----------
def iniciar_sesion(con, codigo, contrasena):
    if not codigo.strip() or not contrasena:
        raise ErrorSistema("Ingresa tu código y tu contraseña.")
    usuario = datos.buscar_usuario_por_codigo(con, codigo)
    if usuario is None or not verificar_contrasena(contrasena, usuario["contrasena"]):
        raise ErrorSistema("Código o contraseña incorrectos.")
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
    if tipo not in TIPOS_CONSTANCIA:
        raise ErrorSistema("Selecciona el tipo de constancia que deseas solicitar.")
    for solicitud in datos.solicitudes_de_estudiante(con, estudiante_id):
        if solicitud["tipo"] == tipo and solicitud["estado"] not in ESTADOS_FINALES:
            raise ErrorSistema(f"Ya tienes una solicitud de este tipo en trámite (folio {solicitud['folio']}).")
    folio = f"SOL-{datos.siguiente_numero_solicitud(con):04d}"
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
    if not inscripcion_id:
        raise ErrorSistema("Selecciona un alumno de la lista.")
    if not str(valor).strip():
        raise ErrorSistema("Escribe la calificación.")
    try:
        numero = float(str(valor).strip())
    except ValueError:
        raise ErrorSistema("La calificación debe ser un número.")
    if not CALIFICACION_MINIMA <= numero <= CALIFICACION_MAXIMA:
        raise ErrorSistema(f"La calificación debe estar entre {CALIFICACION_MINIMA} y {CALIFICACION_MAXIMA}.")
    datos.guardar_calificacion(con, inscripcion_id, numero)
    return numero


# ---------- administrador ----------
def registrar_usuario(con, codigo, nombre, correo, contrasena, rol):
    codigo, nombre, correo = codigo.strip(), nombre.strip(), correo.strip()
    _obligatorios(código=codigo, nombre=nombre, correo=correo, contraseña=contrasena, rol=rol)
    if not PATRON_CODIGO.match(codigo):
        raise ErrorSistema("El código debe tener de 4 a 15 letras o números, sin espacios.")
    if not PATRON_CORREO.match(correo):
        raise ErrorSistema("El correo no tiene un formato válido (ejemplo: nombre@udg.mx).")
    if len(contrasena) < 6:
        raise ErrorSistema("La contraseña debe tener al menos 6 caracteres.")
    if rol not in ROLES:
        raise ErrorSistema("Selecciona un rol válido.")
    if datos.buscar_usuario_por_codigo(con, codigo) is not None:
        raise ErrorSistema(f"El código {codigo} ya está registrado.")
    if datos.buscar_usuario_por_correo(con, correo) is not None:
        raise ErrorSistema(f"El correo {correo} ya está registrado con otro usuario.")
    carrera_id = 1 if rol == "estudiante" else None
    datos.insertar_usuario(con, codigo, nombre, correo, generar_hash(contrasena), rol, carrera_id)


def registrar_materia(con, clave, nombre, creditos, cupo, codigo_docente):
    clave, nombre, codigo_docente = clave.strip().upper(), nombre.strip(), codigo_docente.strip()
    _obligatorios(clave=clave, nombre=nombre, créditos=creditos, cupo=cupo, docente=codigo_docente)
    if not PATRON_CLAVE_MATERIA.match(clave):
        raise ErrorSistema("La clave de la materia debe tener de 2 a 4 letras y 3 números (ejemplo: IS101).")
    creditos = _entero_positivo(creditos, "créditos")
    cupo = _entero_positivo(cupo, "cupo")
    docente = datos.buscar_usuario_por_codigo(con, codigo_docente)
    if docente is None or docente["rol"] != "docente":
        raise ErrorSistema(f"No existe un docente con el código {codigo_docente}.")
    if datos.buscar_materia_por_clave(con, clave) is not None:
        raise ErrorSistema(f"La materia {clave} ya está registrada.")
    datos.insertar_materia(con, clave, nombre, creditos, cupo, docente["id"])


def inscribir_alumno(con, codigo_alumno, clave_materia, ciclo):
    codigo_alumno, clave_materia, ciclo = codigo_alumno.strip(), clave_materia.strip().upper(), ciclo.strip().upper()
    _obligatorios(alumno=codigo_alumno, materia=clave_materia, ciclo=ciclo)
    if not PATRON_CICLO.match(ciclo):
        raise ErrorSistema("El ciclo debe tener el formato 2026A o 2026B.")
    alumno = datos.buscar_usuario_por_codigo(con, codigo_alumno)
    if alumno is None or alumno["rol"] != "estudiante":
        raise ErrorSistema(f"No existe un estudiante con el código {codigo_alumno}.")
    materia = datos.buscar_materia_por_clave(con, clave_materia)
    if materia is None:
        raise ErrorSistema(f"No existe la materia {clave_materia}.")
    for inscrita in datos.materias_de_estudiante(con, alumno["id"]):
        if inscrita["clave"] == clave_materia and inscrita["ciclo"] == ciclo:
            raise ErrorSistema(f"El alumno ya está inscrito en {clave_materia} en el ciclo {ciclo}.")
    inscritos = datos.contar_inscritos(con, materia["id"], ciclo)
    if inscritos >= materia["cupo"]:
        raise ErrorSistema(f"La materia {clave_materia} ya no tiene cupo en el ciclo {ciclo} "
                           f"({inscritos} de {materia['cupo']} lugares ocupados).")
    datos.insertar_inscripcion(con, alumno["id"], materia["id"], ciclo)


def todas_las_solicitudes(con):
    return datos.todas_las_solicitudes(con)


def atender_solicitud(con, folio, estado):
    if not folio:
        raise ErrorSistema("Selecciona una solicitud de la lista.")
    if estado not in ESTADOS_SOLICITUD:
        raise ErrorSistema("Selecciona el nuevo estado de la solicitud.")
    datos.actualizar_estado_solicitud(con, folio, estado)
