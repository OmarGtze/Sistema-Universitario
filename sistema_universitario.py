# Sistema Universitario - prototipo
# Ingenieria de Software 2026B
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import random

ventana = tk.Tk()
ventana.title("Sistema Universitario")
ventana.geometry("380x260")

usuario_actual = None


def crear_bd():
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS carreras(id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT, nombre TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nombre TEXT, correo TEXT, contrasena TEXT, rol TEXT, carrera_id INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS materias(id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE, nombre TEXT, creditos INTEGER, cupo INTEGER, docente_id INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS inscripciones(id INTEGER PRIMARY KEY AUTOINCREMENT, estudiante_id INTEGER, materia_id INTEGER, ciclo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS calificaciones(id INTEGER PRIMARY KEY AUTOINCREMENT, inscripcion_id INTEGER, valor REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS solicitudes(id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, estudiante_id INTEGER, tipo TEXT, fecha TEXT, estado TEXT)")
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO carreras(clave, nombre) VALUES ('INNI', 'Ingenieria Informatica')")
        c.execute("INSERT INTO carreras(clave, nombre) VALUES ('INCO', 'Ingenieria en Computacion')")
        c.execute("INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('A0001', 'Laura Rios Vega', 'laura.rios@udg.mx', 'admin123', 'administrador', NULL)")
        c.execute("INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('D1001', 'Carlos Mendez Soto', 'carlos.mendez@udg.mx', 'docente123', 'docente', NULL)")
        c.execute("INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('D1002', 'Mariana Torres Gil', 'mariana.torres@udg.mx', 'docente123', 'docente', NULL)")
        c.execute("INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('218001234', 'Ana Lopez Ruiz', 'ana.lopez@alumnos.udg.mx', 'ana123', 'estudiante', 1)")
        c.execute("INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('218005678', 'Luis Perez Nava', 'luis.perez@alumnos.udg.mx', 'luis123', 'estudiante', 1)")
        c.execute("INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES ('IS101', 'Ingenieria de Software', 8, 40, 2)")
        c.execute("INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES ('BD201', 'Bases de Datos', 8, 2, 3)")
        c.execute("INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES ('PR102', 'Programacion', 8, 35, 2)")
        c.execute("INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES (4, 1, '2026B')")
        c.execute("INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES (4, 2, '2026B')")
        c.execute("INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES (5, 1, '2026B')")
        c.execute("INSERT INTO calificaciones(inscripcion_id, valor) VALUES (1, 92)")
    con.commit()
    con.close()


def login():
    global usuario_actual
    x = e1.get()
    y = e2.get()
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute(f"SELECT * FROM usuarios WHERE codigo = '{x}' AND contrasena = '{y}'")
    d = c.fetchone()
    con.close()
    if d:
        usuario_actual = d
        if d[5] == "estudiante":
            ventana_estudiante()
        elif d[5] == "docente":
            ventana_docente()
        else:
            ventana_admin()
    else:
        messagebox.showerror("Error", "Error")


def ventana_estudiante():
    v = tk.Toplevel(ventana)
    v.title("Estudiante - " + usuario_actual[2])
    v.geometry("620x520")
    tk.Label(v, text="Mis materias y calificaciones", font=("Arial", 12, "bold")).pack(pady=5)
    t = ttk.Treeview(v, columns=("a", "b", "c", "d"), show="headings", height=6)
    t.heading("a", text="Clave")
    t.heading("b", text="Materia")
    t.heading("c", text="Ciclo")
    t.heading("d", text="Calificacion")
    t.column("a", width=80)
    t.column("b", width=250)
    t.column("c", width=80)
    t.column("d", width=100)
    t.pack(padx=10)
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute(f"SELECT m.clave, m.nombre, i.ciclo, (SELECT valor FROM calificaciones WHERE inscripcion_id = i.id) FROM inscripciones i JOIN materias m ON m.id = i.materia_id WHERE i.estudiante_id = {usuario_actual[0]}")
    datos = c.fetchall()
    con.close()
    s = 0
    n = 0
    for f in datos:
        t.insert("", "end", values=(f[0], f[1], f[2], f[3] if f[3] is not None else "-"))
        if f[3] is not None:
            s = s + f[3]
            n = n + 1
    if n > 0:
        tk.Label(v, text="Promedio: " + str(s / n)).pack()
    else:
        tk.Label(v, text="Promedio: -").pack()

    tk.Label(v, text="Solicitar constancia", font=("Arial", 12, "bold")).pack(pady=5)
    cb = ttk.Combobox(v, values=["Constancia de estudios", "Constancia de calificaciones"], state="readonly")
    cb.pack()

    t2 = ttk.Treeview(v, columns=("a", "b", "c", "d"), show="headings", height=5)
    t2.heading("a", text="Folio")
    t2.heading("b", text="Tipo")
    t2.heading("c", text="Fecha")
    t2.heading("d", text="Estado")
    t2.column("a", width=90)
    t2.column("b", width=220)
    t2.column("c", width=100)
    t2.column("d", width=120)

    def solicitar():
        folio = "SOL-" + str(random.randint(1, 9999))
        fecha = str(datetime.date.today())
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"INSERT INTO solicitudes(folio, estudiante_id, tipo, fecha, estado) VALUES ('{folio}', {usuario_actual[0]}, '{cb.get()}', '{fecha}', 'Pendiente')")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")
        for i in t2.get_children():
            t2.delete(i)
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"SELECT folio, tipo, fecha, estado FROM solicitudes WHERE estudiante_id = {usuario_actual[0]}")
        for f in c.fetchall():
            t2.insert("", "end", values=f)
        con.close()

    tk.Button(v, text="Solicitar", command=solicitar).pack(pady=5)
    t2.pack(padx=10)
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute(f"SELECT folio, tipo, fecha, estado FROM solicitudes WHERE estudiante_id = {usuario_actual[0]}")
    for f in c.fetchall():
        t2.insert("", "end", values=f)
    con.close()


def ventana_docente():
    v = tk.Toplevel(ventana)
    v.title("Docente - " + usuario_actual[2])
    v.geometry("620x420")
    tk.Label(v, text="Mis grupos", font=("Arial", 12, "bold")).pack(pady=5)
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute(f"SELECT id, clave, nombre FROM materias WHERE docente_id = {usuario_actual[0]}")
    mats = c.fetchall()
    con.close()
    cb = ttk.Combobox(v, values=[m[1] + " - " + m[2] for m in mats], state="readonly", width=40)
    cb.pack()
    t = ttk.Treeview(v, columns=("a", "b", "c", "d"), show="headings", height=8)
    t.heading("a", text="Inscripcion")
    t.heading("b", text="Codigo")
    t.heading("c", text="Nombre")
    t.heading("d", text="Calificacion")
    t.column("a", width=80)
    t.column("b", width=100)
    t.column("c", width=250)
    t.column("d", width=100)
    t.pack(padx=10, pady=5)

    def cargar(event=None):
        for i in t.get_children():
            t.delete(i)
        m = mats[cb.current()]
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"SELECT i.id, u.codigo, u.nombre, (SELECT valor FROM calificaciones WHERE inscripcion_id = i.id) FROM inscripciones i JOIN usuarios u ON u.id = i.estudiante_id WHERE i.materia_id = {m[0]}")
        for f in c.fetchall():
            t.insert("", "end", values=(f[0], f[1], f[2], f[3] if f[3] is not None else "-"))
        con.close()

    cb.bind("<<ComboboxSelected>>", cargar)
    tk.Label(v, text="Calificacion:").pack()
    e = tk.Entry(v)
    e.pack()

    def guardar():
        sel = t.focus()
        i = t.item(sel)["values"][0]
        val = float(e.get())
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"INSERT INTO calificaciones(inscripcion_id, valor) VALUES ({i}, {val})")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")
        cargar()

    tk.Button(v, text="Guardar", command=guardar).pack(pady=5)


def ventana_admin():
    v = tk.Toplevel(ventana)
    v.title("Administrador - " + usuario_actual[2])
    v.geometry("700x620")
    # registrar usuario
    tk.Label(v, text="Registrar usuario", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=5)
    tk.Label(v, text="Codigo").grid(row=1, column=0)
    a1 = tk.Entry(v)
    a1.grid(row=1, column=1)
    tk.Label(v, text="Nombre").grid(row=1, column=2)
    a2 = tk.Entry(v)
    a2.grid(row=1, column=3)
    tk.Label(v, text="Correo").grid(row=2, column=0)
    a3 = tk.Entry(v)
    a3.grid(row=2, column=1)
    tk.Label(v, text="Contrasena").grid(row=2, column=2)
    a4 = tk.Entry(v)
    a4.grid(row=2, column=3)
    tk.Label(v, text="Rol").grid(row=3, column=0)
    a5 = ttk.Combobox(v, values=["estudiante", "docente", "administrador"])
    a5.grid(row=3, column=1)

    def reg_usuario():
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"INSERT INTO usuarios(codigo, nombre, correo, contrasena, rol, carrera_id) VALUES ('{a1.get()}', '{a2.get()}', '{a3.get()}', '{a4.get()}', '{a5.get()}', 1)")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")

    tk.Button(v, text="Registrar", command=reg_usuario).grid(row=3, column=3)

    # registrar materia
    tk.Label(v, text="Registrar materia", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=4, pady=5)
    tk.Label(v, text="Clave").grid(row=5, column=0)
    b1 = tk.Entry(v)
    b1.grid(row=5, column=1)
    tk.Label(v, text="Nombre").grid(row=5, column=2)
    b2 = tk.Entry(v)
    b2.grid(row=5, column=3)
    tk.Label(v, text="Creditos").grid(row=6, column=0)
    b3 = tk.Entry(v)
    b3.grid(row=6, column=1)
    tk.Label(v, text="Cupo").grid(row=6, column=2)
    b4 = tk.Entry(v)
    b4.grid(row=6, column=3)
    tk.Label(v, text="Codigo docente").grid(row=7, column=0)
    b5 = tk.Entry(v)
    b5.grid(row=7, column=1)

    def reg_materia():
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"SELECT id FROM usuarios WHERE codigo = '{b5.get()}'")
        d = c.fetchone()
        c.execute(f"INSERT INTO materias(clave, nombre, creditos, cupo, docente_id) VALUES ('{b1.get()}', '{b2.get()}', {b3.get()}, {b4.get()}, {d[0]})")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")

    tk.Button(v, text="Registrar", command=reg_materia).grid(row=7, column=3)

    # inscribir
    tk.Label(v, text="Inscribir alumno", font=("Arial", 12, "bold")).grid(row=8, column=0, columnspan=4, pady=5)
    tk.Label(v, text="Codigo alumno").grid(row=9, column=0)
    c1 = tk.Entry(v)
    c1.grid(row=9, column=1)
    tk.Label(v, text="Clave materia").grid(row=9, column=2)
    c2 = tk.Entry(v)
    c2.grid(row=9, column=3)
    tk.Label(v, text="Ciclo").grid(row=10, column=0)
    c3 = tk.Entry(v)
    c3.grid(row=10, column=1)

    def inscribir():
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"SELECT id FROM usuarios WHERE codigo = '{c1.get()}'")
        x = c.fetchone()
        c.execute(f"SELECT id FROM materias WHERE clave = '{c2.get()}'")
        y = c.fetchone()
        c.execute(f"INSERT INTO inscripciones(estudiante_id, materia_id, ciclo) VALUES ({x[0]}, {y[0]}, '{c3.get()}')")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")

    tk.Button(v, text="Inscribir", command=inscribir).grid(row=10, column=3)

    # solicitudes
    tk.Label(v, text="Solicitudes", font=("Arial", 12, "bold")).grid(row=11, column=0, columnspan=4, pady=5)
    t = ttk.Treeview(v, columns=("a", "b", "c", "d"), show="headings", height=6)
    t.heading("a", text="Folio")
    t.heading("b", text="Tipo")
    t.heading("c", text="Fecha")
    t.heading("d", text="Estado")
    t.column("a", width=90)
    t.column("b", width=220)
    t.column("c", width=100)
    t.column("d", width=120)
    t.grid(row=12, column=0, columnspan=4, padx=10)
    con = sqlite3.connect("universidad.db")
    c = con.cursor()
    c.execute("SELECT folio, tipo, fecha, estado FROM solicitudes")
    for f in c.fetchall():
        t.insert("", "end", values=f)
    con.close()
    est = ttk.Combobox(v, values=["Pendiente", "En proceso", "Lista para entrega", "Entregada", "Rechazada"])
    est.grid(row=13, column=1, pady=5)

    def cambiar():
        sel = t.focus()
        folio = t.item(sel)["values"][0]
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute(f"UPDATE solicitudes SET estado = '{est.get()}' WHERE folio = '{folio}'")
        con.commit()
        con.close()
        messagebox.showinfo("OK", "Listo")
        for i in t.get_children():
            t.delete(i)
        con = sqlite3.connect("universidad.db")
        c = con.cursor()
        c.execute("SELECT folio, tipo, fecha, estado FROM solicitudes")
        for f in c.fetchall():
            t.insert("", "end", values=f)
        con.close()

    tk.Button(v, text="Cambiar estado", command=cambiar).grid(row=13, column=3)


crear_bd()
tk.Label(ventana, text="SISTEMA UNIVERSITARIO", font=("Arial", 14, "bold")).pack(pady=15)
tk.Label(ventana, text="Codigo").pack()
e1 = tk.Entry(ventana)
e1.pack()
tk.Label(ventana, text="Contrasena").pack()
e2 = tk.Entry(ventana, show="*")
e2.pack()
tk.Button(ventana, text="Entrar", command=login).pack(pady=15)
ventana.mainloop()
