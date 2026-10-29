// Recibe casos en JSON por la entrada estandar, los traza con trazado.js y devuelve
// los resultados en JSON. Lo usa tests/test_web.py para comparar con Python.
const L = require("../web/trazado.js");

function construir(d) {
  if (d.tipo === "conica") return L.lenteBiconvexa(d.R1, d.R2, d.espesor, d.n, d.k1, d.k2);
  return L.crearLente(L.desdeExpresion(d.g, "g"), L.desdeExpresion(d.f, "f"), d.n, d.semiapertura ?? undefined);
}

let entrada = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (parte) => (entrada += parte));
process.stdin.on("end", () => {
  const resultados = JSON.parse(entrada).map((caso) => {
    const lente = construir(caso.lente);
    const tr = L.trazar(lente, caso.P, caso.u, 1, 12, 601); // las mismas muestras que la pagina (app.js)
    return {
      estado: tr.estado,
      caras: tr.caras,
      puntos: tr.puntos,
      direcciones: tr.direcciones,
      semiapertura: lente.semiapertura,
      paraxial: L.imagenParaxial(lente, caso.P),
    };
  });
  process.stdout.write(JSON.stringify(resultados));
});
