"""Casos de prueba del Sistema Universitario (Tarea 11).

Cada prueba usa una base de datos nueva con los datos de prueba de siu/bd.py:
- Ana López (218001234): inscrita en IS101 (calificación 92) y BD201 (sin calificación), ciclo 2026B.
- Luis Pérez (218005678): inscrito en IS101 (sin calificación).
- BD201 tiene cupo de 2 alumnos y ya tiene 1 inscrito (Ana).
La primera línea del docstring de cada prueba es su identificador y nombre.
"""
import os
import tempfile
import unittest

from siu import bd, servicios
from siu.servicios import ErrorSistema

INSC_ANA_IS101, INSC_ANA_BD201, INSC_LUIS_IS101 = 1, 2, 3
ID_ANA = 4


class BaseDePruebas(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.con = bd.conectar(os.path.join(self.carpeta.name, "pruebas.db"))

    def tearDown(self):
        self.con.close()
        self.carpeta.cleanup()

    def assertError(self, mensaje_esperado, funcion, *args):
        with self.assertRaises(ErrorSistema) as contexto:
            funcion(*args)
        self.assertIn(mensaje_esperado, str(contexto.exception))

    def calificacion_de(self, inscripcion_id):
        filas = self.con.execute("SELECT valor FROM calificaciones WHERE inscripcion_id = ?",
                                 (inscripcion_id,)).fetchall()
        return [f["valor"] for f in filas]


# ---------------- F1. Inicio de sesión (RF-01) ----------------
class PruebasInicioSesion(BaseDePruebas):
    def test_cp01_login_valido(self):
        """CP-01 Inicio de sesión con credenciales válidas"""
        usuario = servicios.iniciar_sesion(self.con, "218001234", "ana123")
        self.assertEqual(usuario["nombre"], "Ana López Ruiz")
        self.assertEqual(usuario["rol"], "estudiante")

    def test_cp02_contrasena_incorrecta(self):
        """CP-02 Inicio de sesión con contraseña incorrecta"""
        self.assertError("Código o contraseña incorrectos.", servicios.iniciar_sesion, self.con, "218001234", "ana999")

    def test_cp03_campos_vacios(self):
        """CP-03 Inicio de sesión con campos vacíos"""
        self.assertError("Ingresa tu código y tu contraseña.", servicios.iniciar_sesion, self.con, "", "")

    def test_cp04_inyeccion_sql(self):
        """CP-04 Inicio de sesión con inyección SQL"""
        self.assertError("Código o contraseña incorrectos.", servicios.iniciar_sesion,
                         self.con, "' OR '1'='1' --", "x")


# ---------------- F2. Consulta de calificaciones (RF-04) ----------------
class PruebasConsultaCalificaciones(BaseDePruebas):
    def test_cp05_consulta_y_promedio(self):
        """CP-05 Consulta de calificaciones y promedio del estudiante"""
        filas = servicios.calificaciones_de_estudiante(self.con, ID_ANA)
        self.assertEqual([f["clave"] for f in filas], ["BD201", "IS101"])
        self.assertEqual(servicios.calcular_promedio(filas), 92.0)

    def test_cp06_limite_aprobatoria(self):
        """CP-06 Límite de calificación aprobatoria (60 y 59.9)"""
        servicios.registrar_calificacion(self.con, INSC_ANA_BD201, "60")
        servicios.registrar_calificacion(self.con, INSC_ANA_IS101, "59.9")
        estados = {f["clave"]: f["estado"] for f in servicios.calificaciones_de_estudiante(self.con, ID_ANA)}
        self.assertEqual(estados, {"BD201": "Aprobada", "IS101": "Reprobada"})


# ---------------- F3. Solicitud de constancias (RF-05, RF-06) ----------------
class PruebasSolicitudes(BaseDePruebas):
    def test_cp07_solicitud_valida(self):
        """CP-07 Solicitud de constancia válida"""
        folio = servicios.solicitar_constancia(self.con, ID_ANA, "Constancia de estudios")
        self.assertEqual(folio, "SOL-0001")
        solicitud = servicios.solicitudes_de_estudiante(self.con, ID_ANA)[0]
        self.assertEqual(solicitud["estado"], "Pendiente")

    def test_cp08_solicitud_duplicada(self):
        """CP-08 Solicitud duplicada mientras otra está en trámite"""
        servicios.solicitar_constancia(self.con, ID_ANA, "Constancia de estudios")
        self.assertError("Ya tienes una solicitud de este tipo en trámite", servicios.solicitar_constancia,
                         self.con, ID_ANA, "Constancia de estudios")

    def test_cp09_tipo_no_seleccionado(self):
        """CP-09 Solicitud sin seleccionar el tipo de constancia"""
        self.assertError("Selecciona el tipo de constancia", servicios.solicitar_constancia, self.con, ID_ANA, "")

    def test_cp10_seguimiento_de_estado(self):
        """CP-10 Integración: el administrador cambia el estado y el estudiante lo consulta"""
        folio = servicios.solicitar_constancia(self.con, ID_ANA, "Constancia de calificaciones")
        servicios.atender_solicitud(self.con, folio, "Lista para entrega")
        self.assertEqual(servicios.solicitudes_de_estudiante(self.con, ID_ANA)[0]["estado"], "Lista para entrega")


# ---------------- F4. Registro de calificaciones (RF-09) ----------------
class PruebasRegistroCalificaciones(BaseDePruebas):
    def test_cp11_calificacion_valida_sin_duplicar(self):
        """CP-11 Registro y modificación de una calificación válida"""
        servicios.registrar_calificacion(self.con, INSC_LUIS_IS101, "85")
        servicios.registrar_calificacion(self.con, INSC_LUIS_IS101, "88")
        self.assertEqual(self.calificacion_de(INSC_LUIS_IS101), [88.0])

    def test_cp12_limites_validos(self):
        """CP-12 Calificaciones en los límites válidos (0 y 100)"""
        servicios.registrar_calificacion(self.con, INSC_LUIS_IS101, "0")
        servicios.registrar_calificacion(self.con, INSC_ANA_BD201, "100")
        self.assertEqual(self.calificacion_de(INSC_LUIS_IS101) + self.calificacion_de(INSC_ANA_BD201), [0.0, 100.0])

    def test_cp13_mayor_a_100(self):
        """CP-13 Calificación mayor a 100 (101)"""
        self.assertError("entre 0 y 100", servicios.registrar_calificacion, self.con, INSC_LUIS_IS101, "101")
        self.assertEqual(self.calificacion_de(INSC_LUIS_IS101), [])

    def test_cp14_negativa(self):
        """CP-14 Calificación negativa (-5)"""
        self.assertError("entre 0 y 100", servicios.registrar_calificacion, self.con, INSC_LUIS_IS101, "-5")
        self.assertEqual(self.calificacion_de(INSC_LUIS_IS101), [])

    def test_cp15_no_numerica(self):
        """CP-15 Calificación con texto ("abc")"""
        self.assertError("La calificación debe ser un número.", servicios.registrar_calificacion,
                         self.con, INSC_LUIS_IS101, "abc")


# ---------------- F5. Registro de usuarios (RF-11) ----------------
class PruebasRegistroUsuarios(BaseDePruebas):
    def test_cp16_usuario_valido_puede_entrar(self):
        """CP-16 Integración: registrar un usuario e iniciar sesión con él"""
        servicios.registrar_usuario(self.con, "218009999", "Sofía Ramos Díaz", "sofia.ramos@alumnos.udg.mx",
                                    "sofia123", "estudiante")
        self.assertEqual(servicios.iniciar_sesion(self.con, "218009999", "sofia123")["nombre"], "Sofía Ramos Díaz")

    def test_cp17_correo_invalido(self):
        """CP-17 Registro de usuario con correo inválido"""
        self.assertError("El correo no tiene un formato válido", servicios.registrar_usuario, self.con,
                         "218009999", "Sofía Ramos Díaz", "sofia.ramos@", "sofia123", "estudiante")

    def test_cp18_correo_duplicado(self):
        """CP-18 Registro de usuario con un correo ya registrado"""
        self.assertError("correo", servicios.registrar_usuario, self.con, "218009999", "Otra Persona",
                         "ana.lopez@alumnos.udg.mx", "otra123", "estudiante")


# ---------------- F6. Inscripción de alumnos (RF-13) ----------------
class PruebasInscripciones(BaseDePruebas):
    def test_cp19_inscripcion_integrada(self):
        """CP-19 Integración: la inscripción aparece para el estudiante y para el docente"""
        servicios.inscribir_alumno(self.con, "218005678", "PR102", "2026B")
        claves = [f["clave"] for f in servicios.calificaciones_de_estudiante(self.con, 5)]
        self.assertIn("PR102", claves)
        materia = self.con.execute("SELECT id FROM materias WHERE clave = 'PR102'").fetchone()["id"]
        self.assertIn("218005678", [a["codigo"] for a in servicios.alumnos_de_materia(self.con, materia)])

    def test_cp20_inscripcion_duplicada(self):
        """CP-20 Inscripción duplicada en la misma materia y ciclo"""
        self.assertError("ya está inscrito", servicios.inscribir_alumno, self.con, "218001234", "IS101", "2026B")

    def test_cp21_cupo_lleno(self):
        """CP-21 Inscripción cuando la materia llega a su cupo (BD201, cupo 2)"""
        servicios.inscribir_alumno(self.con, "218005678", "BD201", "2026B")  # ocupa el lugar 2 de 2
        servicios.registrar_usuario(self.con, "218009999", "Sofía Ramos Díaz", "sofia.ramos@alumnos.udg.mx",
                                    "sofia123", "estudiante")
        self.assertError("cupo", servicios.inscribir_alumno, self.con, "218009999", "BD201", "2026B")


if __name__ == "__main__":
    unittest.main()
