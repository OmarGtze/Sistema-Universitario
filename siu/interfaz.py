"""Capa de presentación: ventanas del sistema hechas con Tkinter.

La interfaz no ejecuta consultas SQL; todo lo pide a la capa de servicios.
"""
import tkinter as tk
from tkinter import ttk

from siu import servicios
from siu.servicios import ErrorSistema

FUENTE_TITULO = ("Arial", 15, "bold")
FUENTE_SUBTITULO = ("Arial", 11, "bold")
COLOR_ERROR = "#B71C1C"
COLOR_EXITO = "#1B5E20"


# ---------- utilidades reutilizables (antes se repetían en cada ventana) ----------
def crear_tabla(padre, columnas, alto=6):
    """columnas: lista de (identificador, título, ancho)."""
    tabla = ttk.Treeview(padre, columns=[c[0] for c in columnas], show="headings", height=alto)
    for identificador, titulo, ancho in columnas:
        tabla.heading(identificador, text=titulo)
        tabla.column(identificador, width=ancho, anchor="w")
    return tabla


def llenar_tabla(tabla, filas):
    tabla.delete(*tabla.get_children())
    for fila in filas:
        tabla.insert("", "end", values=[("-" if v is None else v) for v in fila])


def valor_seleccionado(tabla):
    """Regresa el primer valor de la fila seleccionada o None si no hay selección."""
    seleccion = tabla.selection()
    if not seleccion:
        return None
    return tabla.item(seleccion[0])["values"][0]


def crear_campo(padre, etiqueta, fila, columna, ancho=22, **opciones):
    ttk.Label(padre, text=etiqueta).grid(row=fila, column=columna, sticky="e", padx=5, pady=4)
    entrada = ttk.Entry(padre, width=ancho, **opciones)
    entrada.grid(row=fila, column=columna + 1, sticky="w", padx=5, pady=4)
    return entrada


class Aplicacion(tk.Tk):
    def __init__(self, con):
        super().__init__()
        self.con = con
        self.usuario = None
        self.title("Sistema Universitario")
        self.geometry("820x560")
        self.barra_estado = tk.Label(self, anchor="w", padx=10, pady=6, font=("Arial", 10, "bold"))
        self.barra_estado.pack(side="bottom", fill="x")
        self.contenedor = ttk.Frame(self, padding=12)
        self.contenedor.pack(fill="both", expand=True)
        self.mostrar_login()

    # ---------- mensajes ----------
    def mostrar_mensaje(self, texto, error=False):
        """Muestra el mensaje en la barra inferior: rojo para errores y verde para confirmaciones."""
        color = COLOR_ERROR if error else COLOR_EXITO
        fondo = "#FDECEA" if error else "#E8F5E9"
        self.barra_estado.config(text=("✖ " if error else "✔ ") + texto, fg=color, bg=fondo)

    def ejecutar(self, accion, mensaje_exito):
        """Ejecuta una acción de la interfaz y muestra el resultado; regresa True si tuvo éxito."""
        try:
            resultado = accion()
        except ErrorSistema as error:
            self.mostrar_mensaje(str(error), error=True)
            return False
        except Exception:
            self.mostrar_mensaje("Ocurrió un error inesperado. Intenta de nuevo o avisa al administrador.", error=True)
            return False
        self.mostrar_mensaje(mensaje_exito.format(resultado=resultado))
        return True

    def limpiar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    # ---------- inicio de sesión ----------
    def mostrar_login(self):
        self.limpiar()
        self.usuario = None
        self.barra_estado.config(text="", bg=self.cget("bg"))
        marco = ttk.Frame(self.contenedor, padding=30)
        marco.place(relx=0.5, rely=0.4, anchor="center")
        ttk.Label(marco, text="SISTEMA UNIVERSITARIO", font=FUENTE_TITULO).grid(row=0, column=0, columnspan=2, pady=15)
        self.entrada_codigo = crear_campo(marco, "Código:", 1, 0)
        self.entrada_contrasena = crear_campo(marco, "Contraseña:", 2, 0, show="*")
        ttk.Button(marco, text="Entrar", command=self.entrar).grid(row=3, column=0, columnspan=2, pady=15)
        self.entrada_codigo.focus()

    def entrar(self):
        try:
            self.usuario = servicios.iniciar_sesion(
                self.con, self.entrada_codigo.get(), self.entrada_contrasena.get())
        except ErrorSistema as error:
            self.mostrar_mensaje(str(error), error=True)
            return
        self.mostrar_panel()

    # ---------- panel principal ----------
    def mostrar_panel(self):
        self.limpiar()
        self.mostrar_mensaje(f"Sesión iniciada correctamente como {self.usuario['rol']}.")
        encabezado = ttk.Frame(self.contenedor)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text=f"Bienvenido(a), {self.usuario['nombre']}  ({self.usuario['rol']})",
                  font=FUENTE_SUBTITULO).pack(side="left")
        ttk.Button(encabezado, text="Cerrar sesión", command=self.mostrar_login).pack(side="right")
        self.pestanas = ttk.Notebook(self.contenedor)
        self.pestanas.pack(fill="both", expand=True, pady=8)
        rol = self.usuario["rol"]
        if rol == "estudiante":
            self.pestana_calificaciones()
            self.pestana_tramites()
        elif rol == "docente":
            self.pestana_grupos()
        else:
            self.pestana_usuarios()
            self.pestana_materias()
            self.pestana_inscripciones()
            self.pestana_solicitudes()

    def nueva_pestana(self, titulo):
        marco = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(marco, text=titulo)
        return marco

    # ---------- estudiante ----------
    def pestana_calificaciones(self):
        marco = self.nueva_pestana("Mis materias y calificaciones")
        self.tabla_calificaciones = crear_tabla(marco, [
            ("clave", "Clave", 80), ("materia", "Materia", 260), ("ciclo", "Ciclo", 70),
            ("calificacion", "Calificación", 100), ("estado", "Estado", 130)], alto=10)
        self.tabla_calificaciones.pack(fill="x")
        self.etiqueta_promedio = ttk.Label(marco, font=FUENTE_SUBTITULO)
        self.etiqueta_promedio.pack(anchor="e", pady=8)
        self.cargar_calificaciones()

    def cargar_calificaciones(self):
        filas = servicios.calificaciones_de_estudiante(self.con, self.usuario["id"])
        llenar_tabla(self.tabla_calificaciones,
                     [(f["clave"], f["materia"], f["ciclo"], f["calificacion"], f["estado"]) for f in filas])
        promedio = servicios.calcular_promedio(filas)
        self.etiqueta_promedio.config(text=f"Promedio: {promedio if promedio is not None else '-'}")

    def pestana_tramites(self):
        marco = self.nueva_pestana("Trámites")
        ttk.Label(marco, text="Tipo de constancia:").grid(row=0, column=0, sticky="w")
        self.combo_tipo = ttk.Combobox(marco, values=servicios.TIPOS_CONSTANCIA, state="readonly", width=32)
        self.combo_tipo.grid(row=0, column=1, padx=5)
        ttk.Button(marco, text="Solicitar", command=self.solicitar_constancia).grid(row=0, column=2)
        self.tabla_solicitudes = crear_tabla(marco, [
            ("folio", "Folio", 100), ("tipo", "Tipo", 260), ("fecha", "Fecha", 110), ("estado", "Estado", 150)], alto=9)
        self.tabla_solicitudes.grid(row=1, column=0, columnspan=3, pady=10, sticky="we")
        self.cargar_solicitudes()

    def cargar_solicitudes(self):
        llenar_tabla(self.tabla_solicitudes,
                     [tuple(f) for f in servicios.solicitudes_de_estudiante(self.con, self.usuario["id"])])

    def solicitar_constancia(self):
        if self.ejecutar(lambda: servicios.solicitar_constancia(self.con, self.usuario["id"], self.combo_tipo.get()),
                         "Solicitud registrada con el folio {resultado}. Puedes consultar su estado en esta pestaña."):
            self.cargar_solicitudes()

    # ---------- docente ----------
    def pestana_grupos(self):
        marco = self.nueva_pestana("Mis grupos")
        self.grupos = servicios.grupos_de_docente(self.con, self.usuario["id"])
        ttk.Label(marco, text="Materia:").grid(row=0, column=0, sticky="w")
        self.combo_grupo = ttk.Combobox(marco, state="readonly", width=40,
                                        values=[f"{g['clave']} - {g['nombre']}" for g in self.grupos])
        self.combo_grupo.grid(row=0, column=1, padx=5, sticky="w")
        self.combo_grupo.bind("<<ComboboxSelected>>", lambda evento: self.cargar_alumnos())
        self.tabla_alumnos = crear_tabla(marco, [
            ("inscripcion", "Inscripción", 90), ("codigo", "Código", 110), ("nombre", "Nombre", 280),
            ("calificacion", "Calificación", 100)], alto=9)
        self.tabla_alumnos.grid(row=1, column=0, columnspan=4, pady=10, sticky="we")
        ttk.Label(marco, text="Calificación:").grid(row=2, column=0, sticky="w")
        self.entrada_calificacion = ttk.Entry(marco, width=10)
        self.entrada_calificacion.grid(row=2, column=1, sticky="w", padx=5)
        ttk.Button(marco, text="Guardar calificación", command=self.guardar_calificacion).grid(row=2, column=2)

    def cargar_alumnos(self):
        if self.combo_grupo.current() < 0:
            return
        grupo = self.grupos[self.combo_grupo.current()]
        llenar_tabla(self.tabla_alumnos, [tuple(f) for f in servicios.alumnos_de_materia(self.con, grupo["id"])])

    def guardar_calificacion(self):
        inscripcion_id = valor_seleccionado(self.tabla_alumnos)
        if self.ejecutar(lambda: servicios.registrar_calificacion(self.con, inscripcion_id,
                                                                  self.entrada_calificacion.get()),
                         "Calificación de {resultado} guardada correctamente."):
            self.entrada_calificacion.delete(0, "end")
            self.cargar_alumnos()

    # ---------- administrador ----------
    def pestana_usuarios(self):
        marco = self.nueva_pestana("Usuarios")
        self.usuario_codigo = crear_campo(marco, "Código:", 0, 0)
        self.usuario_nombre = crear_campo(marco, "Nombre:", 0, 2, ancho=30)
        self.usuario_correo = crear_campo(marco, "Correo:", 1, 0)
        self.usuario_contrasena = crear_campo(marco, "Contraseña:", 1, 2, show="*")
        ttk.Label(marco, text="Rol:").grid(row=2, column=0, sticky="e", padx=5)
        self.usuario_rol = ttk.Combobox(marco, values=servicios.ROLES, state="readonly", width=20)
        self.usuario_rol.grid(row=2, column=1, sticky="w", padx=5)
        ttk.Button(marco, text="Registrar usuario", command=self.registrar_usuario).grid(row=3, column=3, pady=10, sticky="e")

    def registrar_usuario(self):
        codigo = self.usuario_codigo.get().strip()
        if self.ejecutar(lambda: servicios.registrar_usuario(
                self.con, codigo, self.usuario_nombre.get(), self.usuario_correo.get(),
                self.usuario_contrasena.get(), self.usuario_rol.get()),
                f"Usuario {codigo} registrado correctamente."):
            for campo in (self.usuario_codigo, self.usuario_nombre, self.usuario_correo, self.usuario_contrasena):
                campo.delete(0, "end")

    def pestana_materias(self):
        marco = self.nueva_pestana("Materias")
        self.materia_clave = crear_campo(marco, "Clave:", 0, 0)
        self.materia_nombre = crear_campo(marco, "Nombre:", 0, 2, ancho=30)
        self.materia_creditos = crear_campo(marco, "Créditos:", 1, 0)
        self.materia_cupo = crear_campo(marco, "Cupo:", 1, 2)
        self.materia_docente = crear_campo(marco, "Código docente:", 2, 0)
        ttk.Button(marco, text="Registrar materia", command=self.registrar_materia).grid(row=3, column=3, pady=10, sticky="e")

    def registrar_materia(self):
        clave = self.materia_clave.get().strip().upper()
        self.ejecutar(lambda: servicios.registrar_materia(
            self.con, clave, self.materia_nombre.get(), self.materia_creditos.get(),
            self.materia_cupo.get(), self.materia_docente.get()),
            f"Materia {clave} registrada correctamente.")

    def pestana_inscripciones(self):
        marco = self.nueva_pestana("Inscripciones")
        self.inscripcion_alumno = crear_campo(marco, "Código del alumno:", 0, 0)
        self.inscripcion_materia = crear_campo(marco, "Clave de la materia:", 1, 0)
        self.inscripcion_ciclo = crear_campo(marco, "Ciclo:", 2, 0)
        ttk.Button(marco, text="Inscribir", command=self.inscribir_alumno).grid(row=3, column=1, pady=10, sticky="e")

    def inscribir_alumno(self):
        alumno = self.inscripcion_alumno.get().strip()
        materia = self.inscripcion_materia.get().strip().upper()
        self.ejecutar(lambda: servicios.inscribir_alumno(self.con, alumno, materia, self.inscripcion_ciclo.get()),
                      f"Alumno {alumno} inscrito en {materia}.")

    def pestana_solicitudes(self):
        marco = self.nueva_pestana("Solicitudes")
        self.tabla_todas = crear_tabla(marco, [
            ("folio", "Folio", 90), ("alumno", "Alumno", 100), ("tipo", "Tipo", 230), ("fecha", "Fecha", 100),
            ("estado", "Estado", 140)], alto=10)
        self.tabla_todas.grid(row=0, column=0, columnspan=3, sticky="we")
        ttk.Label(marco, text="Nuevo estado:").grid(row=1, column=0, sticky="e", pady=10)
        self.combo_estado = ttk.Combobox(marco, values=servicios.ESTADOS_SOLICITUD, state="readonly")
        self.combo_estado.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Button(marco, text="Cambiar estado", command=self.cambiar_estado).grid(row=1, column=2, sticky="w")
        self.cargar_todas_las_solicitudes()

    def cargar_todas_las_solicitudes(self):
        llenar_tabla(self.tabla_todas, [tuple(f) for f in servicios.todas_las_solicitudes(self.con)])

    def cambiar_estado(self):
        folio = valor_seleccionado(self.tabla_todas)
        estado = self.combo_estado.get()
        if self.ejecutar(lambda: servicios.atender_solicitud(self.con, folio, estado),
                         f"La solicitud {folio} cambió a «{estado}»."):
            self.cargar_todas_las_solicitudes()


def iniciar(con):
    Aplicacion(con).mainloop()
