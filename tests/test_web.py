"""La pagina web (web/trazado.js) traza los mismos rayos que el paquete Python.

Ejecuta el JavaScript con Node.js (tests/verificar_web.cjs). Si Node no esta
instalado la prueba se omite, salvo en el CI de GitHub, donde debe correr.
"""
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from lentes import Lente, desde_expresion, imagen_paraxial, lente_biconvexa, trazar

RAIZ = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
EN_CI = os.environ.get("CI") == "true"
pytestmark = pytest.mark.skipif(NODE is None and not EN_CI, reason="hace falta Node.js para probar la pagina web")

CONICA = {"tipo": "conica", "R1": 10, "R2": 10, "espesor": 2, "n": 1.5}
CASOS = [
    {"lente": {**CONICA, "k1": -1, "k2": -1}, "P": [0, -30], "grados": 2},
    {"lente": {**CONICA, "k1": -1, "k2": -1}, "P": [-1, -30], "grados": 4},
    {"lente": {**CONICA, "k1": 0, "k2": 0}, "P": [0, -30], "grados": 7},
    {"lente": {**CONICA, "k1": -2.33, "k2": -2.33}, "P": [0.4, -22], "grados": -5},
    {"lente": {"tipo": "conica", "R1": 12, "R2": 6, "espesor": 1.5, "n": 1.62, "k1": -0.5, "k2": 0.3},
     "P": [0.8, -25], "grados": -1},
    {"lente": {**CONICA, "k1": -1, "k2": -1}, "P": [0, -6], "grados": 10},
    {"lente": {**CONICA, "k1": -1, "k2": -1}, "P": [0, -30], "grados": 20},  # no toca la lente
    {"lente": {"tipo": "expresion", "g": "-1 + x**2/20", "f": "1 - x^2/20", "n": 1.5}, "P": [0.5, -25], "grados": 3},
    {"lente": {"tipo": "expresion", "g": "9 - sqrt(100 - x^2)", "f": "-9 + sqrt(100 - x**2)", "n": 1.5},
     "P": [0, -40], "grados": 4},
    {"lente": {"tipo": "expresion", "g": "-1", "f": "1", "n": 1.5, "semiapertura": 50}, "P": [0, 0], "grados": 60},
]


def construir(d):
    if d["tipo"] == "conica":
        return lente_biconvexa(d["R1"], d["R2"], d["espesor"], d["n"], d["k1"], d["k2"])
    return Lente(desde_expresion(d["g"], "g"), desde_expresion(d["f"], "f"), d["n"], d.get("semiapertura"))


@pytest.fixture(scope="module")
def resultados_js():
    if NODE is None:
        pytest.fail("en el CI debe haber Node.js para comparar la pagina web con Python")
    entrada = []
    for caso in CASOS:
        a = math.radians(caso["grados"])
        entrada.append({**caso, "u": [math.sin(a), math.cos(a)]})
    proceso = subprocess.run([NODE, str(RAIZ / "tests" / "verificar_web.cjs")], input=json.dumps(entrada),
                             capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(proceso.stdout)


@pytest.mark.parametrize("i", range(len(CASOS)))
def test_mismo_recorrido_que_python(i, resultados_js):
    caso, js = CASOS[i], resultados_js[i]
    lente = construir(caso["lente"])
    a = math.radians(caso["grados"])
    tr = trazar(lente, caso["P"], [math.sin(a), math.cos(a)])
    tol = 1e-9 if caso["lente"]["tipo"] == "conica" else 1e-7  # la web deriva numericamente las formulas
    assert js["estado"] == tr.estado
    assert js["caras"] == tr.caras
    assert np.isclose(js["semiapertura"], lente.semiapertura, rtol=1e-9)
    assert np.allclose(js["puntos"], np.array(tr.puntos), atol=tol)
    assert np.allclose(js["direcciones"], np.array(tr.direcciones), atol=tol)


@pytest.mark.parametrize("i", [0, 1, 4, 5, 7, 8])
def test_misma_imagen_paraxial(i, resultados_js):
    caso, js = CASOS[i], resultados_js[i]
    par = imagen_paraxial(construir(caso["lente"]), caso["P"])
    rtol = 1e-12 if caso["lente"]["tipo"] == "conica" else 1e-5
    assert np.isclose(js["paraxial"]["y"], par.y, rtol=rtol)
    assert np.isclose(js["paraxial"]["aumento"], par.aumento, rtol=rtol)
