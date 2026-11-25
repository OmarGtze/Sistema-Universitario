"""Punto de entrada del Sistema Universitario."""
from siu import bd, interfaz


def main():
    con = bd.conectar()
    try:
        interfaz.iniciar(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
