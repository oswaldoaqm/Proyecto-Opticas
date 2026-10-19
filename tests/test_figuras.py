"""Las figuras se guardan igual cada vez y en cualquier sistema (decision 0005)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lentes.estilo import aplicar_estilo, guardar_figura  # noqa: E402


def _figura():
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.plot([0, 1, 2], [0, 1, 4], label="prueba")
    ax.set_title("Aberración - prueba")
    ax.legend()
    return fig


def test_svg_con_saltos_lf_y_sin_fecha(tmp_path):
    fig = _figura()
    png, svg = guardar_figura(fig, tmp_path / "prueba")
    plt.close(fig)
    datos = svg.read_bytes()
    assert png.suffix == ".png" and svg.suffix == ".svg"
    assert b"\r\n" not in datos            # en Windows, guardado directo a archivo saldria con CRLF
    assert b"<dc:date>" not in datos        # sin fecha: regenerar no cambia el archivo
    assert datos.startswith(b"<?xml")


def test_regenerar_da_los_mismos_bytes(tmp_path):
    rutas = []
    for carpeta in ("a", "b"):
        fig = _figura()
        rutas.append(guardar_figura(fig, tmp_path / carpeta / "prueba"))
        plt.close(fig)
    for primera, segunda in zip(*rutas):
        assert primera.read_bytes() == segunda.read_bytes()
