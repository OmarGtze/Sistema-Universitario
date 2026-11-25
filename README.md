# Sistema Universitario

Prototipo de un sistema universitario para la materia de Ingeniería de Software (CUCEI, ciclo 2026B).

Permite que los estudiantes consulten sus materias y calificaciones y soliciten constancias, que los docentes
registren calificaciones y que los administradores registren usuarios y materias, inscriban alumnos y atiendan
solicitudes.

## Requisitos

- Python 3.10 o superior (incluye Tkinter y SQLite).

## Ejecución

```
python main.py
```

## Estructura

```
main.py            punto de entrada
siu/bd.py          conexión, tablas y datos de prueba
siu/datos.py       capa de acceso a datos (SQL)
siu/servicios.py   capa de lógica de negocio
siu/interfaz.py    capa de presentación (Tkinter)
```

La base de datos `universidad.db` se crea automáticamente con datos de prueba.

## Usuarios de prueba

| Rol | Código | Contraseña |
|---|---|---|
| Administrador | A0001 | admin123 |
| Docente | D1001 | docente123 |
| Estudiante | 218001234 | ana123 |
