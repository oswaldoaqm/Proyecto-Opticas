/*
 * Simulador de la pagina web: estado, controles, dibujo y lecturas.
 * La fisica esta en trazado.js, la misma que la del paquete Python (tests/test_web.py
 * lo comprueba). Convenciones del proyecto (docs/decisiones/0001): eje optico = eje y,
 * la luz avanza en +y, g es la cara de entrada y f la de salida.
 */
(function () {
  "use strict";

  const L = window.Lentes;
  const MUESTRAS = 601; // puntos por cara al buscar cada cruce (Python usa 2001; el cruce se afina igual)
  const $ = (id) => document.getElementById(id);
  const limitar = (v, a, b) => Math.min(b, Math.max(a, v));
  const grados = (r) => (r * 180) / Math.PI;
  const radianes = (g) => (g * Math.PI) / 180;
  const reducido = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };

  // ---------------------------------------------------------------- formato
  function num(v, d = 3) {
    if (v === Infinity) return "∞";
    if (v === -Infinity) return "-∞";
    if (!Number.isFinite(v)) return "-";
    const s = v.toFixed(d);
    return Number(s) === 0 ? (0).toFixed(d) : s;
  }
  const corto = (v) => String(Number(v.toPrecision(6)));
  const f1 = (v) => (Math.round(v * 10) / 10).toString();
  const mayuscula = (t) => t.charAt(0).toUpperCase() + t.slice(1);
  const escapar = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  function pasoBonito(bruto) {
    const p = Math.pow(10, Math.floor(Math.log10(bruto)));
    const r = bruto / p;
    return (r < 1.5 ? 1 : r < 3.5 ? 2 : r < 7.5 ? 5 : 10) * p;
  }
  const decimalesDe = (paso) => Math.max(0, -Math.floor(Math.log10(paso) + 1e-9));

  // ------------------------------------------------------------------ casos
  const BASE = { R1: 10, R2: 10, d: 2 };
  const CASOS = {
    parabolica: {
      nombre: "Caras parabólicas (ejemplo)",
      nota: "La lente del notebook 01: n = 1.5, R = 10, d = 2 y rayos a +2° y -2° desde P = (0, -30).",
      n: 1.5, P: [0, -30], conica: { ...BASE, k1: -1, k2: -1 }, alfas: [2, -2],
    },
    esferica: {
      nombre: "Caras esféricas",
      nota: "Los mismos radios de vértice: la misma imagen paraxial, pero más aberración.",
      n: 1.5, P: [0, -30], conica: { ...BASE, k1: 0, k2: 0 }, alfas: [7, -7],
    },
    asferica: {
      nombre: "Asféricas, k = -2.33",
      nota: "La constante cónica que anula la aberración de tercer orden para este objeto (notebook 02).",
      n: 1.5, P: [0, -30], conica: { ...BASE, k1: -2.33, k2: -2.33 }, alfas: [7, -7],
    },
    fuera: {
      nombre: "Objeto fuera del eje",
      nota: "El segundo punto objeto del notebook 01, P = (-1, -30), con rayos a 0° y 4°.",
      n: 1.5, P: [-1, -30], conica: { ...BASE, k1: -1, k2: -1 }, alfas: [0, 4],
    },
    virtual: {
      nombre: "Objeto dentro del foco",
      nota: "P está más cerca que el foco F: los rayos salen separándose y sus prolongaciones se cruzan detrás del objeto.",
      n: 1.5, P: [0, -7], conica: { ...BASE, k1: -1, k2: -1 }, alfas: [8, -8],
    },
    total: {
      nombre: "Índice alto: reflexión total",
      nota: "Con n = 2.4, como el diamante, los rayos muy inclinados no salen por la cara f: se reflejan dentro del vidrio.",
      n: 2.4, P: [0, -8], conica: { R1: 6, R2: 6, d: 2, k1: 0, k2: 0 }, alfas: [19, -8],
    },
    formula: {
      nombre: "Fórmula libre (polinómica)",
      nota: "Así se especifican las asféricas: una parábola más términos en x^4. Con x^4/6000 se anula la aberración de tercer orden; en el borde queda un resto pequeño de orden superior.",
      n: 1.5, P: [0, -30], formula: { g: "-1 + x^2/20 - x^4/6000", f: "1 - x^2/20 + x^4/6000", a: "" }, alfas: [7, -7],
    },
  };

  // ------------------------------------------------------------------ estado
  const estado = {
    caso: "parabolica",
    n: 1.5,
    P: [0, -30],
    modo: "conica",
    conica: { ...BASE, k1: -1, k2: -1 },
    formula: { g: "", f: "", a: "" },
    formulaPropia: false,
    fr: [0.2, -0.2], // rayos 1 y 2: posicion entre los bordes de la lente vistos desde P (-1 a 1)
    abanico: 13,
    vista: "todo",
  };

  // ------------------------------------------------------------------- lente
  let lente = null; // ultima lente valida
  let errorLente = null;
  let claveLente = "";

  function conCampo(mensaje, campo) {
    const e = new Error(mayuscula(mensaje));
    e.campo = campo;
    return e;
  }

  function caraDeFormula(texto, nombre) {
    if (!String(texto).trim()) throw conCampo(`escribe ${nombre}(x)`, nombre);
    try {
      return L.desdeExpresion(texto, nombre);
    } catch (e) {
      throw conCampo(e.message, nombre);
    }
  }

  function construirLente() {
    if (estado.modo === "conica") {
      const c = estado.conica;
      try {
        return L.lenteBiconvexa(c.R1, c.R2, c.d, estado.n, c.k1, c.k2);
      } catch (e) {
        throw conCampo("con estos radios y este espesor las caras no se juntan: baja el espesor o aumenta los radios.", null);
      }
    }
    const g = caraDeFormula(estado.formula.g, "g");
    const f = caraDeFormula(estado.formula.f, "f");
    const textoA = estado.formula.a.trim().replace(",", ".");
    let a;
    if (textoA !== "") {
      a = Number(textoA);
      if (!(a > 0)) throw conCampo("la semiapertura debe ser un número mayor que 0.", "a");
    }
    let nueva;
    try {
      nueva = L.crearLente(g, f, estado.n, a);
    } catch (e) {
      const juntan = /juntan|borde/.test(e.message);
      throw conCampo(juntan ? "las caras no se juntan: escribe una semiapertura." : e.message + ".", null);
    }
    for (let i = 0; i <= 200; i++) {
      const x = -nueva.semiapertura + (2 * nueva.semiapertura * i) / 200;
      const yg = g.s(x);
      const yf = f.s(x);
      if (!Number.isFinite(yg)) throw conCampo("g(x) no está definida en todo el ancho de la lente.", "g");
      if (!Number.isFinite(yf)) throw conCampo("f(x) no está definida en todo el ancho de la lente.", "f");
      if (yf < yg - 1e-9) throw conCampo("las caras se cruzan antes del borde: f(x) debe quedar por encima de g(x).", null);
    }
    return nueva;
  }

  function actualizarLente() {
    const clave = JSON.stringify([estado.modo, estado.n, estado.modo === "conica" ? estado.conica : estado.formula]);
    if (clave === claveLente) return;
    claveLente = clave;
    try {
      lente = construirLente();
      errorLente = null;
    } catch (e) {
      errorLente = { mensaje: e.message, campo: e.campo || null };
    }
  }

  function rangoAngular(len, P) {
    const a = 0.995 * len.semiapertura;
    const angulo = (x) => Math.atan2(x - P[0], len.abajo.s(x) - P[1]);
    return [angulo(-a), angulo(a)];
  }

  // ------------------------------------------------------------------ escena
  let escena = null;

  function limpio(tr) {
    return tr.estado === "ok" && tr.detalles.length === 2 && !tr.detalles[0].total && !tr.detalles[1].total &&
      tr.direcciones[2][1] > 0;
  }

  function problema(tr) {
    if (tr.estado === "no_toca_lente") return "no toca la lente";
    if (tr.detalles.some((d) => d.total)) return "tiene reflexión total interna";
    if (tr.estado === "sale_por_el_borde") return "sale por el borde de la lente";
    if (tr.estado === "demasiados_eventos") return "queda atrapado en la lente";
    return "no sale hacia adelante";
  }

  function trazarRayo(P, alfa) {
    return { alfa, tr: L.trazar(lente, P, [Math.sin(alfa), Math.cos(alfa)], 1, 12, MUESTRAS) };
  }

  function imagenDe(principales) {
    const [r1, r2] = principales;
    for (const [i, r] of [[1, r1], [2, r2]]) {
      if (!limpio(r.tr)) return { tipo: "sin", motivo: `el rayo ${i} ${problema(r.tr)}` };
    }
    if (Math.abs(r1.alfa - r2.alfa) < 1e-9) return { tipo: "sin", motivo: "los rayos 1 y 2 son el mismo rayo" };
    const [Q1, e1] = L.salida(r1.tr);
    const [Q2, e2] = L.salida(r2.tr);
    const c = L.interseccionRectas(Q1, e1, Q2, e2);
    if (!c || Math.abs(c.punto[1]) > 1e5) return { tipo: "infinito" };
    if (c.s > 0 && c.t > 0) return { tipo: "real", punto: c.punto };
    if (c.s < 0 && c.t < 0) return { tipo: "virtual", punto: c.punto };
    return { tipo: "sin", motivo: "los rayos emergentes no se cruzan de un mismo lado de la lente" };
  }

  // Donde cruza cada rayo al rayo central (el que llega al centro de la cara g).
  // Con P en el eje, el rayo central es el eje y esto es la aberracion esferica longitudinal.
  function curvaAberracion(esc) {
    const { central, paraxial } = esc;
    if (!limpio(central.tr) || !Number.isFinite(paraxial.y)) return null;
    const [Qc, ec] = L.salida(central.tr);
    const hc = central.tr.puntos[1][0];
    const tope = Math.max(5, 0.5 * Math.abs(paraxial.y - esc.lente.ymax));
    const puntos = [];
    const agregar = (r, cual) => {
      if (!limpio(r.tr)) return;
      const h = r.tr.puntos[1][0] - hc;
      if (Math.abs(h) < 2e-3 * esc.lente.semiapertura) return;
      const [Q, e] = L.salida(r.tr);
      const c = L.interseccionRectas(Q, e, Qc, ec);
      if (!c) return;
      const dy = c.punto[1] - paraxial.y;
      if (Math.abs(dy) <= tope) puntos.push({ h, dy, cual });
    };
    esc.abanico.forEach((r) => agregar(r, 0));
    esc.principales.forEach((r, i) => agregar(r, i + 1));
    return puntos;
  }

  function calcularEscena() {
    const P = estado.P.slice();
    const [amin, amax] = rangoAngular(lente, P);
    const alfaDe = (t) => amin + ((t + 1) / 2) * (amax - amin);
    const principales = estado.fr.map((t) => trazarRayo(P, alfaDe(t)));
    const abanico = [];
    const N = estado.abanico;
    for (let i = 0; i < N; i++) abanico.push(trazarRayo(P, alfaDe(N === 1 ? 0 : -0.97 + (1.94 * i) / (N - 1))));
    const central = trazarRayo(P, Math.atan2(-P[0], lente.abajo.yv - P[1]));
    const [[A], [C, D]] = L.matrizSistema(lente);
    const esc = {
      lente, P, amin, amax, principales, abanico, central,
      paraxial: L.imagenParaxial(lente, P),
      focal: L.focalEfectiva(lente),
      F: C === 0 ? NaN : lente.abajo.yv + D / C,
      Fp: C === 0 ? NaN : lente.arriba.yv - A / C,
    };
    esc.imagen = imagenDe(principales);
    esc.curva = curvaAberracion(esc);
    return esc;
  }

  // ------------------------------------------------------------------ vistas
  function rectTodo(esc) {
    const { lente: len, P } = esc;
    const a = len.semiapertura;
    const dObj = Math.max(len.ymin - P[1], 0.5);
    const alcance = Math.max(3 * dObj, 12);
    let y0 = P[1];
    let y1 = len.ymax;
    let x0 = Math.min(-a, P[0]);
    let x1 = Math.max(a, P[0]);
    let despues = false;
    const candidatos = [];
    if (esc.imagen.punto) candidatos.push(esc.imagen.punto);
    if (Number.isFinite(esc.paraxial.y)) candidatos.push([esc.paraxial.x, esc.paraxial.y]);
    for (const [x, y] of candidatos) {
      if (y > len.ymax && y - len.ymax <= alcance) {
        y1 = Math.max(y1, y);
        despues = true;
      } else if (y < len.ymin && len.ymin - y <= alcance + dObj) {
        y0 = Math.min(y0, y);
      } else {
        continue;
      }
      x0 = Math.min(x0, x);
      x1 = Math.max(x1, x);
    }
    const largo = y1 - y0;
    y1 = despues ? y1 + Math.max(0.15 * largo, 1.5) : Math.max(y1 + 0.3 * largo, len.ymax + 0.6 * dObj);
    y0 -= 0.05 * largo + 0.8;
    const ancho = x1 - x0;
    return { x0: x0 - 0.2 * ancho - 0.4, x1: x1 + 0.2 * ancho + 0.4, y0, y1 };
  }

  function rectImagen(esc) {
    const par = Number.isFinite(esc.paraxial.y) ? [esc.paraxial.x, esc.paraxial.y] : null;
    const centro = esc.imagen.punto || par;
    if (!centro) return rectTodo(esc);
    const ys = [centro[1]];
    if (par) ys.push(par[1]);
    if (esc.curva && par) for (const p of esc.curva) ys.push(par[1] + p.dy);
    let y0 = Math.min(...ys);
    let y1 = Math.max(...ys);
    const escala = Math.max(y1 - y0, 0.04 * Math.abs(centro[1] - esc.lente.ymax), 0.3);
    y0 -= 0.7 * escala;
    y1 += 0.7 * escala;
    const mitad = 0.25 * (y1 - y0);
    return { x0: centro[0] - mitad, x1: centro[0] + mitad, y0, y1 };
  }

  const CAMPOS = ["x0", "x1", "y0", "y1"];
  function mezclar(a, b, f) {
    const r = {};
    for (const k of CAMPOS) r[k] = a[k] + (b[k] - a[k]) * f;
    return r;
  }
  function distinta(a, b) {
    const tol = 1e-3 * Math.max(b.y1 - b.y0, b.x1 - b.x0);
    return CAMPOS.some((k) => Math.abs(a[k] - b[k]) > tol);
  }

  // ----------------------------------------------------------------- lienzo
  const lienzo = $("lienzo");
  let W = 600;
  let H = 400;
  let vertical = false;

  function medir() {
    const r = lienzo.getBoundingClientRect();
    W = Math.max(1, r.width);
    H = Math.max(1, r.height);
    vertical = H > 1.05 * W;
    lienzo.setAttribute("viewBox", `0 0 ${f1(W)} ${f1(H)}`);
  }

  // Mundo (x, y) -> pantalla. En horizontal la luz va de izquierda a derecha (pantalla x = y del
  // mundo, +x del mundo hacia arriba); en vertical se ve como en el enunciado (y hacia arriba).
  function transformacion(rect) {
    const m = vertical ? { l: 46, r: 12, t: 50, b: 12 } : { l: 12, r: 12, t: 44, b: 32 };
    const iw = Math.max(W - m.l - m.r, 10);
    const ih = Math.max(H - m.t - m.b, 10);
    const sa = rect.y1 - rect.y0;
    const sc = rect.x1 - rect.x0;
    const k = vertical ? Math.min(iw / sc, ih / sa) : Math.min(iw / sa, ih / sc);
    const cx = m.l + iw / 2;
    const cy = m.t + ih / 2;
    const xc = (rect.x0 + rect.x1) / 2;
    const yc = (rect.y0 + rect.y1) / 2;
    const aP = vertical
      ? (p) => [cx + (p[0] - xc) * k, cy - (p[1] - yc) * k]
      : (p) => [cx + (p[1] - yc) * k, cy - (p[0] - xc) * k];
    const aM = vertical
      ? (s) => [xc + (s[0] - cx) / k, yc - (s[1] - cy) / k]
      : (s) => [xc - (s[1] - cy) / k, yc + (s[0] - cx) / k];
    const e1 = aM([0, 0]);
    const e2 = aM([W, H]);
    const vis = {
      x0: Math.min(e1[0], e2[0]), x1: Math.max(e1[0], e2[0]),
      y0: Math.min(e1[1], e2[1]), y1: Math.max(e1[1], e2[1]),
    };
    return { k, aP, aM, vis };
  }

  function expandir(c, f) {
    const dx = f * (c.x1 - c.x0);
    const dy = f * (c.y1 - c.y0);
    return { x0: c.x0 - dx, x1: c.x1 + dx, y0: c.y0 - dy, y1: c.y1 + dy };
  }

  // Recorte de un segmento a una caja (Liang-Barsky), en coordenadas del mundo.
  function recortar(p, q, c) {
    let t0 = 0;
    let t1 = 1;
    const dx = q[0] - p[0];
    const dy = q[1] - p[1];
    const lados = [[-dx, p[0] - c.x0], [dx, c.x1 - p[0]], [-dy, p[1] - c.y0], [dy, c.y1 - p[1]]];
    for (const [pp, qq] of lados) {
      if (pp === 0) {
        if (qq < 0) return null;
      } else {
        const r = qq / pp;
        if (pp < 0) {
          if (r > t1) return null;
          if (r > t0) t0 = r;
        } else {
          if (r < t0) return null;
          if (r < t1) t1 = r;
        }
      }
    }
    return [[p[0] + t0 * dx, p[1] + t0 * dy], [p[0] + t1 * dx, p[1] + t1 * dy]];
  }

  const linea = (p, q) => `M${f1(p[0])} ${f1(p[1])}L${f1(q[0])} ${f1(q[1])}`;

  function lejos(Q, e, vis) {
    const t = 2 * (Math.hypot(vis.x1 - vis.x0, vis.y1 - vis.y0) +
      Math.hypot(Q[0] - (vis.x0 + vis.x1) / 2, Q[1] - (vis.y0 + vis.y1) / 2));
    return [Q[0] + t * e[0], Q[1] + t * e[1]];
  }

  // Tramos de un rayo: incidente, dentro del vidrio y emergente (despues de una reflexion
  // total el rayo sigue dentro del vidrio).
  function tramos(tr, vis) {
    const out = [];
    let dentro = false;
    for (let i = 0; i < tr.puntos.length; i++) {
      const p = tr.puntos[i];
      const q = i + 1 < tr.puntos.length ? tr.puntos[i + 1] : lejos(p, tr.direcciones[i], vis);
      out.push({ tipo: i === 0 ? "inc" : dentro ? "tra" : "eme", p, q });
      if (i < tr.detalles.length && !tr.detalles[i].total) dentro = !dentro;
    }
    return out;
  }

  function grupoRayos(clase, trazos, T, caja) {
    const d = { inc: "", tra: "", eme: "" };
    for (const tr of trazos) {
      for (const s of tramos(tr, T.vis)) {
        const c = recortar(s.p, s.q, caja);
        if (c) d[s.tipo] += linea(T.aP(c[0]), T.aP(c[1]));
      }
    }
    return `<g class="${clase}"><path class="r-inc" d="${d.inc}"/><path class="r-tra" d="${d.tra}"/>` +
      `<path class="r-eme" d="${d.eme}"/></g>`;
  }

  function contorno(len, T) {
    const a = len.semiapertura;
    const n = 140;
    let d = "";
    for (let i = 0; i <= n; i++) {
      const x = -a + (2 * a * i) / n;
      const s = T.aP([x, len.abajo.s(x)]);
      d += (i ? "L" : "M") + f1(s[0]) + " " + f1(s[1]);
    }
    for (let i = n; i >= 0; i--) {
      const x = -a + (2 * a * i) / n;
      const s = T.aP([x, len.arriba.s(x)]);
      d += "L" + f1(s[0]) + " " + f1(s[1]);
    }
    return d + "Z";
  }

  function texto(t, x, y, clase, ancla = "middle") {
    return `<text class="${clase}" x="${f1(x)}" y="${f1(y)}" text-anchor="${ancla}" dominant-baseline="central">${t}</text>`;
  }

  // Etiqueta a un lado de un punto: lado +1 hacia +x del mundo (arriba en horizontal,
  // a la derecha en vertical), -1 hacia el otro lado.
  function etiqueta(t, q, lado, clase, dist = 15) {
    if (vertical) return texto(t, q[0] + lado * dist, q[1], clase, lado > 0 ? "start" : "end");
    return texto(t, q[0], q[1] - lado * dist, clase);
  }

  function rotulosCaras(len, T) {
    const a = len.semiapertura;
    if (a * T.k < 45) return "";
    const x = 0.62 * a;
    const pg = T.aP([x, len.abajo.s(x)]);
    const pf = T.aP([x, len.arriba.s(x)]);
    if (vertical) return texto("g(x)", pg[0], pg[1] + 12, "etiqueta suave") + texto("f(x)", pf[0], pf[1] - 12, "etiqueta suave");
    return texto("g(x)", pg[0] - 8, pg[1], "etiqueta suave", "end") + texto("f(x)", pf[0] + 8, pf[1], "etiqueta suave", "start");
  }

  function rotulosRayos(esc, T) {
    let s = "";
    esc.principales.forEach((r, i) => {
      const tr = r.tr;
      const base = tr.puntos.length > 1 ? tr.puntos[1] : [esc.P[0] + 8 * Math.sin(r.alfa), esc.P[1] + 8 * Math.cos(r.alfa)];
      const q = T.aP(base);
      const lado = base[0] >= 0 ? 1 : -1;
      const pos = vertical ? [q[0] + 13 * lado, q[1] + 15] : [q[0] - 15, q[1] - 13 * lado];
      s += texto(String(i + 1), pos[0], pos[1], "etiqueta rayo");
    });
    return s;
  }

  function regla(T, esc) {
    const paso = pasoBonito(64 / T.k);
    const dec = decimalesDe(paso);
    const sub = (paso / 5) * T.k >= 8 ? paso / 5 : (paso / 2) * T.k >= 8 ? paso / 2 : 0;
    const { y0, y1 } = T.vis;
    const en = (y) => (vertical ? T.aP([0, y])[1] : T.aP([0, y])[0]);
    let s = '<g class="regla">';
    if (!vertical) {
      const b = H - 25;
      s += `<line x1="0" x2="${f1(W)}" y1="${b}" y2="${b}"/>`;
      if (sub) for (let i = Math.ceil(y0 / sub); i <= Math.floor(y1 / sub); i++) {
        const x = f1(en(i * sub));
        s += `<line x1="${x}" x2="${x}" y1="${b}" y2="${b + 3}"/>`;
      }
      for (let i = Math.ceil(y0 / paso); i <= Math.floor(y1 / paso); i++) {
        const xn = en(i * paso);
        const x = f1(xn);
        s += `<line x1="${x}" x2="${x}" y1="${b}" y2="${b + 6}"/>`;
        if (xn > 16 && xn < W - 16) s += `<text x="${x}" y="${b + 17}" text-anchor="middle">${num(i * paso, dec)}</text>`;
      }
      s += `<text x="${f1(W - 6)}" y="${b - 6}" text-anchor="end">y</text>`;
    } else {
      const b = 36;
      s += `<line x1="${b}" x2="${b}" y1="0" y2="${f1(H)}"/>`;
      if (sub) for (let i = Math.ceil(y0 / sub); i <= Math.floor(y1 / sub); i++) {
        const y = f1(en(i * sub));
        s += `<line x1="${b - 3}" x2="${b}" y1="${y}" y2="${y}"/>`;
      }
      for (let i = Math.ceil(y0 / paso); i <= Math.floor(y1 / paso); i++) {
        const yn = en(i * paso);
        const y = f1(yn);
        s += `<line x1="${b - 6}" x2="${b}" y1="${y}" y2="${y}"/>`;
        if (yn > 8 && yn < H - 8) s += `<text x="${b - 9}" y="${y}" text-anchor="end" dominant-baseline="central">${num(i * paso, dec)}</text>`;
      }
      s += `<text x="${b + 6}" y="12" dominant-baseline="central">y</text>`;
    }
    for (const [y, nombre] of [[esc.F, "F"], [esc.Fp, "F′"]]) {
      if (!Number.isFinite(y) || y < y0 || y > y1) continue;
      const p = en(y);
      if (!vertical) {
        const b = H - 25;
        s += `<polygon class="foco" points="${f1(p - 4)},${b} ${f1(p + 4)},${b} ${f1(p)},${b - 6}"/>` +
          `<text class="foco" x="${f1(p)}" y="${b - 13}" text-anchor="middle">${nombre}</text>`;
      } else {
        const b = 36;
        s += `<polygon class="foco" points="${b},${f1(p - 4)} ${b},${f1(p + 4)} ${b + 6},${f1(p)}"/>` +
          `<text class="foco" x="${b + 9}" y="${f1(p)}" dominant-baseline="central">${nombre}</text>`;
      }
    }
    return s + "</g>";
  }

  function indicador(p, T, nombre) {
    const despues = p[1] > T.vis.y1;
    const valor = `${nombre} en y = ${num(p[1], 1)}`;
    if (!vertical) {
      const yEje = T.aP([0, 0])[1] - 14;
      return despues
        ? texto(`${valor} →`, W - 10, yEje, "etiqueta suave", "end")
        : texto(`← ${valor}`, 10, yEje, "etiqueta suave", "start");
    }
    const xEje = T.aP([0, 0])[0];
    return despues
      ? texto(`↑ ${valor}`, xEje, 58, "etiqueta suave")
      : texto(`↓ ${valor}`, xEje, H - 18, "etiqueta suave");
  }

  function marcas(esc, T) {
    let s = "";
    const visible = (p) => p && Number.isFinite(p[0]) && Number.isFinite(p[1]) &&
      p[0] >= T.vis.x0 && p[0] <= T.vis.x1 && p[1] >= T.vis.y0 && p[1] <= T.vis.y1;
    const par = Number.isFinite(esc.paraxial.y) ? [esc.paraxial.x, esc.paraxial.y] : null;
    const im = esc.imagen;
    const nombreImagen = im.tipo === "virtual" ? "imagen virtual" : "imagen";
    if (visible(par)) {
      const q = T.aP(par);
      s += `<circle class="marca-paraxial" cx="${f1(q[0])}" cy="${f1(q[1])}" r="6"/>` + etiqueta("paraxial", q, -1, "etiqueta suave");
    }
    if (visible(im.punto)) {
      const q = T.aP(im.punto);
      s += `<circle class="marca-imagen" cx="${f1(q[0])}" cy="${f1(q[1])}" r="5.5"/>` + etiqueta(nombreImagen, q, 1, "etiqueta");
    }
    if (im.punto && !visible(im.punto)) s += indicador(im.punto, T, nombreImagen);
    else if (!im.punto && par && !visible(par)) s += indicador(par, T, "imagen paraxial");
    const p = T.aP(esc.P);
    s += `<circle class="asa-p" cx="${f1(p[0])}" cy="${f1(p[1])}" r="13"/>` +
      `<circle class="marca-p" cx="${f1(p[0])}" cy="${f1(p[1])}" r="5.5"/>` + etiqueta("P", p, -1, "etiqueta", 21);
    return s;
  }

  function leyenda(conProlongacion) {
    const items = [["r-inc", "incidente"], ["r-tra", "en el vidrio"], ["r-eme", "emergente"]];
    if (conProlongacion) items.push(["prolongacion", "prolongación"]);
    const w = 116;
    const h = 10 + 17 * items.length;
    const x = vertical ? W - 10 - w : 10;
    const y = vertical ? H - 10 - h : 10;
    let s = `<g class="leyenda-svg" transform="translate(${f1(x)} ${f1(y)})"><rect width="${w}" height="${h}" rx="6"/>`;
    items.forEach(([c, t], i) => {
      const yy = 14 + 17 * i;
      s += `<line class="${c}" x1="10" x2="30" y1="${yy}" y2="${yy}"/><text x="37" y="${yy}" dominant-baseline="central">${t}</text>`;
    });
    return s + "</g>";
  }

  function dibujar() {
    const esc = escena;
    if (!esc || !vistaActual) return;
    const T = transformacion(vistaActual);
    const caja = expandir(T.vis, 0.08);
    const out = [];
    const eje = recortar([0, caja.y0], [0, caja.y1], caja);
    if (eje) out.push(`<path class="eje-optico" d="${linea(T.aP(eje[0]), T.aP(eje[1]))}"/>`);
    out.push(regla(T, esc));
    out.push(`<path class="vidrio" d="${contorno(esc.lente, T)}"/>`);
    out.push(rotulosCaras(esc.lente, T));
    if (esc.abanico.length) out.push(grupoRayos("abanico", esc.abanico.map((r) => r.tr), T, caja));
    if (esc.imagen.tipo === "virtual") {
      let d = "";
      for (const r of esc.principales) {
        const c = recortar(L.salida(r.tr)[0], esc.imagen.punto, caja);
        if (c) d += linea(T.aP(c[0]), T.aP(c[1]));
      }
      out.push(`<path class="prolongacion" d="${d}"/>`);
    }
    out.push(grupoRayos("principal", esc.principales.map((r) => r.tr), T, caja));
    out.push(rotulosRayos(esc, T));
    out.push(marcas(esc, T));
    out.push(leyenda(esc.imagen.tipo === "virtual"));
    lienzo.innerHTML = out.join("");
  }

  // ---------------------------------------------------------- gráfica y tabla
  function dibujarGrafica(esc) {
    const svg = $("grafica");
    const r = svg.getBoundingClientRect();
    const w = Math.max(r.width, 60);
    const h = Math.max(r.height, 60);
    svg.setAttribute("viewBox", `0 0 ${f1(w)} ${f1(h)}`);
    const pts = esc && esc.curva ? esc.curva : [];
    if (pts.length < 2) {
      svg.innerHTML = texto("Hacen falta al menos dos rayos que atraviesen la lente.", w / 2, h / 2, "grafica-titulo");
      return;
    }
    const m = { l: 52, r: 16, t: 26, b: 42 };
    const dys = pts.map((p) => p.dy);
    const hs = pts.map((p) => p.h);
    let x0 = Math.min(0, ...dys);
    let x1 = Math.max(0, ...dys);
    if (x1 - x0 < 1e-6) {
      x0 -= 1e-3;
      x1 += 1e-3;
    }
    const px = 0.08 * (x1 - x0);
    x0 -= px;
    x1 += px;
    let y0 = Math.min(0, ...hs);
    let y1 = Math.max(0, ...hs);
    const py = 0.1 * (y1 - y0 || 1);
    y0 -= py;
    y1 += py;
    const X = (v) => m.l + ((v - x0) / (x1 - x0)) * (w - m.l - m.r);
    const Y = (v) => h - m.b - ((v - y0) / (y1 - y0)) * (h - m.t - m.b);
    let s = "";
    const pxs = pasoBonito((x1 - x0) / 5);
    for (let i = Math.ceil(x0 / pxs); i <= Math.floor(x1 / pxs); i++) {
      const xx = f1(X(i * pxs));
      s += `<line class="grafica-rejilla" x1="${xx}" x2="${xx}" y1="${m.t}" y2="${f1(h - m.b)}"/>` +
        `<text class="grafica-texto" x="${xx}" y="${f1(h - m.b + 14)}" text-anchor="middle">${num(i * pxs, decimalesDe(pxs))}</text>`;
    }
    const pys = pasoBonito((y1 - y0) / 4);
    for (let i = Math.ceil(y0 / pys); i <= Math.floor(y1 / pys); i++) {
      const yy = f1(Y(i * pys));
      s += `<line class="grafica-rejilla" x1="${m.l}" x2="${f1(w - m.r)}" y1="${yy}" y2="${yy}"/>` +
        `<text class="grafica-texto" x="${m.l - 7}" y="${yy}" text-anchor="end" dominant-baseline="central">${num(i * pys, decimalesDe(pys))}</text>`;
    }
    const x0p = X(0);
    s += `<line class="grafica-cero" x1="${f1(x0p)}" x2="${f1(x0p)}" y1="${m.t}" y2="${f1(h - m.b)}"/>`;
    const ancla = x0p < m.l + 60 ? "start" : x0p > w - m.r - 60 ? "end" : "middle";
    s += `<text class="grafica-titulo" x="${f1(x0p)}" y="${m.t - 10}" text-anchor="${ancla}">imagen paraxial</text>`;
    const abanico = pts.filter((p) => !p.cual).sort((a, b) => a.h - b.h);
    if (abanico.length > 1) {
      s += `<path class="r-eme" fill="none" stroke-width="1.2" opacity="0.6" d="${abanico.map((p, i) => (i ? "L" : "M") + f1(X(p.dy)) + " " + f1(Y(p.h))).join("")}"/>`;
    }
    for (const p of abanico) s += `<circle class="pt-abanico" cx="${f1(X(p.dy))}" cy="${f1(Y(p.h))}" r="2.8"/>`;
    for (const p of pts.filter((q) => q.cual)) {
      s += `<circle class="pt-principal" cx="${f1(X(p.dy))}" cy="${f1(Y(p.h))}" r="4.2"/>` +
        texto(String(p.cual), X(p.dy) + (X(p.dy) > w - m.r - 20 ? -11 : 11), Y(p.h), "etiqueta rayo");
    }
    s += texto("Δy: dónde cruza el rayo, medido desde la imagen paraxial", m.l + (w - m.l - m.r) / 2, h - 9, "grafica-titulo");
    s += `<text class="grafica-titulo" transform="translate(14 ${f1(m.t + (h - m.t - m.b) / 2)}) rotate(-90)" text-anchor="middle" dominant-baseline="central">h, altura en la cara g</text>`;
    svg.innerHTML = s;
  }

  const angulo = (r) => (r === null ? "" : num(grados(r), 2) + "°");
  const vector = (v) => `(${num(v[0], 4)}, ${num(v[1], 4)})`;

  function actualizarTabla(esc) {
    const filas = [];
    esc.principales.forEach((r, i) => {
      const tr = r.tr;
      filas.push(`<tr><td>${i + 1}</td><td>sale de P</td><td></td><td></td><td>${vector(tr.direcciones[0])}</td></tr>`);
      tr.detalles.forEach((d, j) => {
        const paso = `cara ${tr.caras[j]}`;
        filas.push(d.total
          ? `<tr><td>${i + 1}</td><td>${paso}</td><td>${angulo(d.thetaI)}</td><td class="total">reflexión total</td><td>${vector(d.dir)}</td></tr>`
          : `<tr><td>${i + 1}</td><td>${paso}</td><td>${angulo(d.thetaI)}</td><td>${angulo(d.thetaT)}</td><td>${vector(d.dir)}</td></tr>`);
      });
      if (tr.estado === "no_toca_lente") filas.push(`<tr><td>${i + 1}</td><td>no toca la lente</td><td></td><td></td><td></td></tr>`);
    });
    $("tabla").tBodies[0].innerHTML = filas.join("");
  }

  function actualizarLecturas(esc) {
    const im = esc.imagen;
    const par = esc.paraxial;
    const tipo = im.tipo === "real" || im.tipo === "virtual" ? " " + im.tipo : "";
    $("t-imagen").innerHTML = `Imagen${tipo}<span class="largo"> (rayos 1 y 2)</span>`;
    if (im.punto) {
      $("l-imagen").innerHTML = `y = ${num(im.punto[1])}<span class="sub">x = ${num(im.punto[0])}</span>`;
    } else if (im.tipo === "infinito") {
      $("l-imagen").innerHTML = 'muy lejos<span class="sub">rayos casi paralelos</span>';
    } else {
      $("l-imagen").innerHTML = 'sin imagen<span class="sub">ver el aviso</span>';
    }
    if (Number.isFinite(par.y)) {
      $("l-paraxial").innerHTML = `y = ${num(par.y)}<span class="sub">x = ${num(par.x)}</span>` +
        `<span class="sub">aumento ${num(par.aumento)}</span>`;
    } else {
      $("l-paraxial").innerHTML = 'en el infinito<span class="sub">P está en el foco</span>';
    }
    lienzo.setAttribute("aria-label", "Lente, rayos e imagen. " +
      (im.punto ? `Imagen ${im.tipo} en y = ${num(im.punto[1])}. ` : "Los rayos 1 y 2 no forman imagen. ") +
      (Number.isFinite(par.y) ? `Imagen paraxial en y = ${num(par.y)}.` : ""));
    $("l-diferencia").innerHTML = im.punto && Number.isFinite(par.y)
      ? `Δy = ${num(im.punto[1] - par.y)}<span class="sub">Δx = ${num(im.punto[0] - par.x)}</span>`
      : "-";
  }

  function actualizarEstados(esc) {
    const items = [];
    const im = esc.imagen;
    if (im.tipo === "virtual") items.push(["", "Imagen virtual: los rayos salen separándose"]);
    if (im.tipo === "infinito") items.push(["", "Imagen en el infinito"]);
    esc.principales.forEach((r, i) => {
      if (!limpio(r.tr)) items.push(["alerta", `Rayo ${i + 1}: ${problema(r.tr)}`]);
    });
    if (im.tipo === "sin" && esc.principales.every((r) => limpio(r.tr))) items.push(["alerta", mayuscula(im.motivo)]);
    const tot = esc.abanico.filter((r) => r.tr.detalles.some((d) => d.total)).length;
    if (tot) items.push(["alerta", `${tot} ${tot === 1 ? "rayo" : "rayos"} del abanico con reflexión total`]);
    $("estados").innerHTML = items.map(([c, t]) => `<li${c ? ` class="${c}"` : ""}>${escapar(t)}</li>`).join("");
  }

  function mostrarError() {
    const e = errorLente;
    for (const c of ["g", "f", "a"]) {
      const p = $(c + "-error");
      const ver = Boolean(e && e.campo === c);
      p.hidden = !ver;
      if (ver) p.textContent = e.mensaje;
    }
    const aviso = $("aviso-lente");
    aviso.hidden = !e;
    if (e) {
      aviso.textContent = (e.campo ? "Revisa la fórmula marcada." : e.mensaje) +
        (escena ? " La figura muestra la última lente válida." : "");
    }
  }

  function tipoConica(k) {
    if (Math.abs(k) < 1e-9) return "esfera";
    if (Math.abs(k + 1) < 1e-9) return "parábola";
    if (k < -1) return "hipérbola";
    return k < 0 ? "elipse alargada" : "elipse achatada";
  }

  // ---------------------------------------------------------------- controles
  const CONTROLES = {};
  const textoControl = (v, d) => String(Number(v.toFixed(d)));

  function enlazar(id, decimales, alCambiar) {
    const rango = $(id);
    const numero = $(id + "-n");
    CONTROLES[id] = { rango, numero, decimales };
    rango.addEventListener("input", () => {
      const v = Number(rango.value);
      numero.value = textoControl(v, decimales);
      alCambiar(v);
    });
    numero.addEventListener("change", () => {
      let v = Number(String(numero.value).replace(",", "."));
      if (numero.value === "" || !Number.isFinite(v)) {
        numero.value = textoControl(Number(rango.value), decimales);
        return;
      }
      v = limitar(v, Number(rango.min), Number(rango.max));
      numero.value = textoControl(v, decimales);
      rango.value = v;
      alCambiar(v);
    });
  }

  // No pisa la casilla donde se esta escribiendo, salvo al cargar un caso (`forzar`).
  function poner(id, v, forzar = false) {
    const c = CONTROLES[id];
    c.rango.value = v;
    if (forzar || document.activeElement !== c.numero) c.numero.value = textoControl(v, c.decimales);
  }

  function rangoDe(id, min, max) {
    const c = CONTROLES[id];
    c.rango.min = min;
    c.rango.max = max;
  }

  function fraccion(alfa) {
    if (!escena) return 0;
    return limitar((2 * (alfa - escena.amin)) / (escena.amax - escena.amin) - 1, -1, 1);
  }

  function formulaCara(yv, R, k, signo) {
    const s = signo > 0 ? "+" : "-";
    if (Math.abs(k + 1) < 1e-12) return `${corto(yv)} ${s} x^2/${corto(2 * R)}`;
    const b = (1 + k) / (R * R);
    const raiz = b >= 0 ? `sqrt(1 - ${corto(b)}*x^2)` : `sqrt(1 + ${corto(-b)}*x^2)`;
    return `${corto(yv)} ${s} x^2/(${corto(R)}*(1 + ${raiz}))`;
  }

  function mostrarModo() {
    $("grupo-conica").hidden = estado.modo !== "conica";
    $("grupo-formula").hidden = estado.modo !== "formula";
  }

  function ponerVista(v) {
    estado.vista = v;
    $("vista-todo").setAttribute("aria-pressed", String(v === "todo"));
    $("vista-imagen").setAttribute("aria-pressed", String(v === "imagen"));
    programar();
  }

  function escribirControles() {
    $("caso").value = estado.caso;
    poner("n", estado.n, true);
    for (const k of ["R1", "R2", "k1", "k2", "d"]) poner(k, estado.conica[k], true);
    poner("abanico", estado.abanico, true);
    $("modo-" + estado.modo).checked = true;
    for (const c of ["g", "f", "a"]) $(c + "-formula").value = estado.formula[c];
    mostrarModo();
    ponerVista("todo");
  }

  function actualizarPanel() {
    mostrarError();
    $("k1-tipo").textContent = "· " + tipoConica(estado.conica.k1);
    $("k2-tipo").textContent = "· " + tipoConica(estado.conica.k2);
    if (!escena) return;
    const esc = escena;
    const a = esc.lente.semiapertura;
    const xm = Math.max(8, Math.ceil(1.6 * a));
    rangoDe("xP", -xm, xm);
    rangoDe("yP", -90, Math.floor((esc.lente.ymin - 0.25) * 100) / 100);
    poner("xP", esc.P[0]);
    poner("yP", esc.P[1]);
    esc.principales.forEach((r, i) => {
      const id = "a" + (i + 1);
      rangoDe(id, grados(esc.amin), grados(esc.amax));
      poner(id, grados(r.alfa));
      const u = r.tr.direcciones[0];
      const entra = r.tr.puntos.length > 1 ? ` · entra en x = ${num(r.tr.puntos[1][0])}` : " · no toca la lente";
      $(id + "-nota").textContent = `û${i ? "₂" : "₁"} = ${vector(u)}${entra}`;
    });
    let nota = `Focal efectiva ${num(esc.focal)}`;
    if (Number.isFinite(esc.F)) nota += ` · F en y = ${num(esc.F, 2)} · F′ en y = ${num(esc.Fp, 2)}`;
    $("nota-lente").textContent = nota + ` · semiapertura ${num(a, 2)}`;
    actualizarLecturas(esc);
    actualizarEstados(esc);
    actualizarTabla(esc);
    dibujarGrafica(esc);
    $("grafica-nota").textContent = Math.abs(esc.P[0]) < 1e-9
      ? "Cada punto es un rayo: la altura h a la que entra en la lente y dónde cruza el eje, medido desde la imagen paraxial. Sin aberración todos caerían en Δy = 0. Con caras esféricas los rayos que entran lejos del eje enfocan antes."
      : "Con P fuera del eje se mide dónde cruza cada rayo al rayo central, el que llega al centro de la cara g. La curva deja de ser simétrica: es la coma, otra aberración que aparece fuera del eje.";
  }

  function aplicarCaso(clave) {
    const c = CASOS[clave];
    estado.caso = clave;
    estado.n = c.n;
    estado.P = c.P.slice();
    if (c.formula) {
      estado.modo = "formula";
      Object.assign(estado.formula, c.formula);
      estado.formulaPropia = true;
    } else {
      estado.modo = "conica";
      Object.assign(estado.conica, c.conica);
      estado.formulaPropia = false;
    }
    estado.abanico = c.abanico || 13;
    actualizarLente();
    if (lente && !errorLente) {
      const [amin, amax] = rangoAngular(lente, estado.P);
      estado.fr = c.alfas.map((g) => limitar((2 * (radianes(g) - amin)) / (amax - amin) - 1, -1, 1));
    }
    escribirControles();
    $("nota-caso").textContent = c.nota;
    cambio();
  }

  // ------------------------------------------------------------ bucle de dibujo
  let vistaActual = null;
  let vistaObjetivo = null;
  let congelada = false;
  let sucio = true;
  let pedido = false;
  let ultimo = 0;

  function programar() {
    if (!pedido) {
      pedido = true;
      requestAnimationFrame(cuadro);
    }
  }

  function cambio() {
    sucio = true;
    programar();
  }

  function cuadro(t) {
    pedido = false;
    if (sucio) {
      sucio = false;
      actualizarLente();
      if (lente && !errorLente) {
        estado.P[1] = Math.min(estado.P[1], lente.ymin - 0.25);
        escena = calcularEscena();
      }
      actualizarPanel();
    }
    if (!escena) return;
    if (!congelada) vistaObjetivo = estado.vista === "imagen" ? rectImagen(escena) : rectTodo(escena);
    const dt = ultimo ? Math.min(t - ultimo, 80) : 16;
    ultimo = t;
    const f = !vistaActual || reducido.matches ? 1 : 1 - Math.exp(-dt / 110);
    vistaActual = vistaActual ? mezclar(vistaActual, vistaObjetivo, f) : { ...vistaObjetivo };
    dibujar();
    if (distinta(vistaActual, vistaObjetivo)) {
      programar();
    } else {
      vistaActual = { ...vistaObjetivo };
      ultimo = 0;
    }
  }

  // --------------------------------------------------------- arrastrar a P
  let arrastre = null;

  function posicion(cx, cy) {
    const r = lienzo.getBoundingClientRect();
    return [cx - r.left, cy - r.top];
  }

  function cercaDeP(s, tactil) {
    if (!escena || !vistaActual) return false;
    const p = transformacion(vistaActual).aP(estado.P);
    return Math.hypot(s[0] - p[0], s[1] - p[1]) <= (tactil ? 34 : 18);
  }

  lienzo.addEventListener("pointerdown", (e) => {
    if (!cercaDeP(posicion(e.clientX, e.clientY), e.pointerType !== "mouse")) return;
    arrastre = e.pointerId;
    congelada = true;
    vistaObjetivo = { ...vistaActual };
    lienzo.setPointerCapture(e.pointerId);
    lienzo.style.cursor = "grabbing";
    e.preventDefault();
  });

  lienzo.addEventListener("pointermove", (e) => {
    if (arrastre === null) {
      if (e.pointerType === "mouse") lienzo.style.cursor = cercaDeP(posicion(e.clientX, e.clientY), false) ? "grab" : "";
      return;
    }
    if (e.pointerId !== arrastre || !escena) return;
    const T = transformacion(vistaActual);
    const w = T.aM(posicion(e.clientX, e.clientY));
    const margen = 12 / T.k;
    const xm = Number(CONTROLES.xP.rango.max);
    const x = limitar(w[0], Math.max(T.vis.x0 + margen, -xm), Math.min(T.vis.x1 - margen, xm));
    const y = Math.min(limitar(w[1], Math.max(T.vis.y0 + margen, -90), T.vis.y1 - margen), escena.lente.ymin - 0.25);
    estado.P = [Math.round(x * 100) / 100, Math.round(y * 100) / 100];
    cambio();
  });

  function soltar(e) {
    if (e.pointerId !== arrastre) return;
    arrastre = null;
    congelada = false;
    lienzo.style.cursor = "";
    programar();
  }
  lienzo.addEventListener("pointerup", soltar);
  lienzo.addEventListener("pointercancel", soltar);

  // En pantallas tactiles, un toque sobre P no debe desplazar la pagina.
  lienzo.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1 && cercaDeP(posicion(e.touches[0].clientX, e.touches[0].clientY), true)) e.preventDefault();
  }, { passive: false });

  // ------------------------------------------------------------------ inicio
  enlazar("xP", 2, (v) => { estado.P[0] = v; cambio(); });
  enlazar("yP", 2, (v) => { estado.P[1] = v; cambio(); });
  enlazar("n", 4, (v) => { estado.n = v; cambio(); });
  for (const k of ["R1", "R2", "k1", "k2", "d"]) {
    enlazar(k, k[0] === "k" ? 3 : 2, (v) => { estado.conica[k] = v; cambio(); });
  }
  enlazar("a1", 2, (v) => { estado.fr[0] = fraccion(radianes(v)); cambio(); });
  enlazar("a2", 2, (v) => { estado.fr[1] = fraccion(radianes(v)); cambio(); });
  enlazar("abanico", 0, (v) => { estado.abanico = Math.round(v); cambio(); });

  for (const r of document.querySelectorAll('input[name="modo"]')) {
    r.addEventListener("change", () => {
      if (!r.checked) return;
      if (r.value === "formula" && !estado.formulaPropia) {
        const c = estado.conica;
        estado.formula.g = formulaCara(-c.d / 2, c.R1, c.k1, 1);
        estado.formula.f = formulaCara(c.d / 2, c.R2, c.k2, -1);
        estado.formula.a = "";
        for (const k of ["g", "f", "a"]) $(k + "-formula").value = estado.formula[k];
      }
      estado.modo = r.value;
      mostrarModo();
      cambio();
    });
  }
  for (const c of ["g", "f", "a"]) {
    $(c + "-formula").addEventListener("input", (e) => {
      estado.formula[c] = e.target.value;
      estado.formulaPropia = true;
      cambio();
    });
  }

  const selector = $("caso");
  selector.innerHTML = Object.entries(CASOS).map(([k, c]) => `<option value="${k}">${escapar(c.nombre)}</option>`).join("");
  selector.addEventListener("change", () => aplicarCaso(selector.value));
  $("restablecer").addEventListener("click", () => aplicarCaso(selector.value));
  $("vista-todo").addEventListener("click", () => ponerVista("todo"));
  $("vista-imagen").addEventListener("click", () => ponerVista("imagen"));
  $("controles").addEventListener("submit", (e) => e.preventDefault());

  if (window.ResizeObserver) {
    new ResizeObserver(() => { medir(); programar(); }).observe(lienzo);
    new ResizeObserver(() => { if (escena) dibujarGrafica(escena); }).observe($("grafica"));
  }
  medir();
  aplicarCaso("parabolica");
})();
