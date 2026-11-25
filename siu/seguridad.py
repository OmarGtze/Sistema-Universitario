"""Funciones para guardar y verificar contraseñas de forma segura (PBKDF2 con sal)."""
import hashlib
import hmac
import os

ITERACIONES = 120_000


def generar_hash(contrasena):
    sal = os.urandom(16)
    clave = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${sal.hex()}${clave.hex()}"


def verificar_contrasena(contrasena, hash_guardado):
    try:
        _, iteraciones, sal_hex, clave_hex = hash_guardado.split("$")
    except (AttributeError, ValueError):
        return False
    clave = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), bytes.fromhex(sal_hex), int(iteraciones))
    return hmac.compare_digest(clave.hex(), clave_hex)
