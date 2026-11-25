"""Ejecuta los casos de prueba y muestra un resumen de una línea por caso.

Uso (desde la carpeta del proyecto):  python -m pruebas.ejecutar_pruebas
"""
import sys
import unittest

from pruebas import test_sistema


class ResultadoResumido(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.lineas = []

    def _nombre(self, prueba):
        return prueba.shortDescription() or str(prueba)

    def addSuccess(self, prueba):
        super().addSuccess(prueba)
        self.lineas.append(f"APROBADA     {self._nombre(prueba)}")

    def addFailure(self, prueba, error):
        super().addFailure(prueba, error)
        motivo = str(error[1]).splitlines()[0]
        if motivo.endswith("not raised"):
            motivo = "Se esperaba un mensaje de error, pero el sistema aceptó la operación."
        self.lineas.append(f"NO APROBADA  {self._nombre(prueba)}\n             -> {motivo}")

    def addError(self, prueba, error):
        super().addError(prueba, error)
        self.lineas.append(f"ERROR        {self._nombre(prueba)}\n             -> {error[0].__name__}: {error[1]}")


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_sistema)
    resultado = ResultadoResumido()
    suite.run(resultado)
    for linea in sorted(resultado.lineas, key=lambda l: l.split("CP-")[1][:2]):
        print(linea)
    fallidas = len(resultado.failures) + len(resultado.errors)
    print("-" * 78)
    print(f"Total: {resultado.testsRun}   Aprobadas: {resultado.testsRun - fallidas}   No aprobadas: {fallidas}")
    return 1 if fallidas else 0


if __name__ == "__main__":
    sys.exit(main())
