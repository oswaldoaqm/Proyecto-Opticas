/*
 * Trazado vectorial de rayos en una lente gruesa: version JavaScript del paquete
 * Python `lentes`, para la pagina web. Misma fisica y mismas convenciones
 * (docs/decisiones): eje optico = eje y, la luz viaja en +y, cara g abajo y cara f
 * arriba, normal orientada hacia el medio de incidencia, Snell vectorial con
 * reflexion total. tests/test_web.py compara sus resultados con los de Python.
 */
(function (raiz) {
  "use strict";

  const EPS = 1e-9;

  // ------------------------------------------------------------- vectores 2D
  const punto = (a, b) => a[0] * b[0] + a[1] * b[1];
  const acotar = (v) => Math.min(1, Math.max(-1, v));

  function unitario(v) {
    const m = Math.hypot(v[0], v[1]);
    if (m === 0) throw new Error("vector nulo");
    return [v[0] / m, v[1] / m];
  }

  function biseccion(f, a, b) {
    let fa = f(a);
    for (let i = 0; i < 300; i++) {
      const m = 0.5 * (a + b);
      if (m === a || m === b) break;
      const fm = f(m);
      if (fm === 0) return m;
      if ((fa < 0) === (fm < 0)) {
        a = m;
        fa = fm;
      } else {
        b = m;
      }
    }
    return 0.5 * (a + b);
  }

  // ------------------------------------------------------------- superficies
  function conica(yv, R, k, nombre) {
    const c = Number.isFinite(R) ? 1 / R : 0;
    return {
      s: (x) => yv + (c * x * x) / (1 + Math.sqrt(1 - (1 + k) * c * c * x * x)),
      ds: (x) => (c * x) / Math.sqrt(1 - (1 + k) * c * c * x * x),
      yv,
      R: Number.isFinite(R) ? R : Infinity,
      k,
      nombre,
    };
  }

  // Formulas en x: numeros, x, pi, e, + - * / ^ (o **), parentesis y funciones.
  const FUNCIONES = Object.assign(Object.create(null), {
    sqrt: Math.sqrt, sin: Math.sin, cos: Math.cos, tan: Math.tan, exp: Math.exp,
    log: Math.log, abs: Math.abs, sinh: Math.sinh, cosh: Math.cosh,
  });
  const CONSTANTES = Object.assign(Object.create(null), { pi: Math.PI, e: Math.E });

  function tokenizar(t) {
    const tokens = [];
    let i = 0;
    while (i < t.length) {
      const c = t[i];
      if (/\s/.test(c)) {
        i++;
      } else if (/[0-9.]/.test(c)) {
        const m = /^(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/.exec(t.slice(i));
        if (!m) throw new Error(`número mal escrito cerca de "${t.slice(i, i + 6)}"`);
        tokens.push({ tipo: "num", valor: parseFloat(m[0]) });
        i += m[0].length;
      } else if (/[A-Za-z_]/.test(c)) {
        const m = /^[A-Za-z_]\w*/.exec(t.slice(i));
        tokens.push({ tipo: "id", valor: m[0] });
        i += m[0].length;
      } else if (t.startsWith("**", i)) {
        tokens.push({ tipo: "op", valor: "^" });
        i += 2;
      } else if ("+-*/^()".includes(c)) {
        tokens.push({ tipo: "op", valor: c });
        i++;
      } else {
        throw new Error(`símbolo no permitido: "${c}"`);
      }
    }
    return tokens;
  }

  // Escritura comoda en el celular: x², 0,05, 2·x, el signo menos tipografico.
  function normalizar(texto) {
    return String(texto)
      .replace(/²/g, "^2").replace(/³/g, "^3")
      .replace(/[·×]/g, "*")
      .replace(/[\u2212\u2013]/g, "-")
      .replace(/(\d),(\d)/g, "$1.$2");
  }

  function compilar(texto) {
    const tk = tokenizar(normalizar(texto));
    let p = 0;
    const es = (v) => p < tk.length && tk[p].tipo === "op" && tk[p].valor === v;

    function expresion() {
      let a = termino();
      while (es("+") || es("-")) {
        const op = tk[p++].valor;
        const izq = a;
        const der = termino();
        a = op === "+" ? (x) => izq(x) + der(x) : (x) => izq(x) - der(x);
      }
      return a;
    }
    // Multiplicacion implicita: 0.05x^2, 2(x + 1) o 2pi valen como 0.05*x^2, 2*(x + 1), 2*pi.
    const empiezaFactor = () => p < tk.length && (tk[p].tipo !== "op" || tk[p].valor === "(");
    function termino() {
      let a = unario();
      while (es("*") || es("/") || empiezaFactor()) {
        const op = es("/") ? "/" : "*";
        if (es("*") || es("/")) p++;
        const izq = a;
        const der = op === "/" ? unario() : potencia();
        a = op === "*" ? (x) => izq(x) * der(x) : (x) => izq(x) / der(x);
      }
      return a;
    }
    function unario() {
      if (es("-")) {
        p++;
        const a = unario();
        return (x) => -a(x);
      }
      if (es("+")) {
        p++;
        return unario();
      }
      return potencia();
    }
    function potencia() {
      const base = atomo();
      if (es("^")) {
        p++;
        const exponente = unario();
        return (x) => Math.pow(base(x), exponente(x));
      }
      return base;
    }
    function atomo() {
      if (p >= tk.length) throw new Error("la fórmula termina antes de tiempo");
      const t = tk[p++];
      if (t.tipo === "num") {
        const v = t.valor;
        return () => v;
      }
      if (t.tipo === "id") {
        if (t.valor === "x") return (x) => x;
        if (t.valor in CONSTANTES) {
          const v = CONSTANTES[t.valor];
          return () => v;
        }
        if (t.valor in FUNCIONES) {
          if (!es("(")) throw new Error(`falta "(" después de ${t.valor}`);
          p++;
          const a = expresion();
          if (!es(")")) throw new Error('falta ")"');
          p++;
          const f = FUNCIONES[t.valor];
          return (x) => f(a(x));
        }
        throw new Error(`no conozco "${t.valor}": usa x, números, pi y funciones como sqrt`);
      }
      if (t.valor === "(") {
        const a = expresion();
        if (!es(")")) throw new Error('falta ")"');
        p++;
        return a;
      }
      throw new Error(`no esperaba "${t.valor}"`);
    }

    const f = expresion();
    if (p < tk.length) {
      const v = tk[p].valor;
      throw new Error(v === ")" ? 'sobra un ")"' : `revisa la fórmula cerca de "${v}" (¿falta un * ?)`);
    }
    return f;
  }

  function desdeExpresion(texto, nombre) {
    const s = compilar(texto);
    const ds = (x) => {
      const h = 1e-6 * Math.max(1, Math.abs(x));
      return (s(x + h) - s(x - h)) / (2 * h);
    };
    const yv = s(0);
    if (!Number.isFinite(yv)) throw new Error("la cara no está definida en x = 0");
    const h2 = 1e-4;
    const curvatura = (s(h2) - 2 * yv + s(-h2)) / (h2 * h2);
    const R = Math.abs(curvatura) < 1e-12 ? Infinity : 1 / curvatura;
    return { s, ds, yv, R, k: null, nombre: nombre || String(texto) };
  }

  // ------------------------------------------------------------------ lente
  function bordeNatural(abajo, arriba, espesor) {
    const h = (x) => arriba.s(x) - abajo.s(x);
    let x0 = 0;
    let paso = 1e-3 * Math.max(espesor, 1e-6);
    while (x0 < 1e6) {
      const x1 = x0 + paso;
      const v = h(x1);
      if (Number.isNaN(v)) {
        let xa = x0;
        let va = h(x0);
        for (let i = 1; i <= 2000; i++) {
          const x = x0 + ((x1 - x0) * i) / 2000;
          const vx = h(x);
          if (Number.isNaN(vx)) break;
          if (va > 0 && vx <= 0) return vx < 0 ? biseccion(h, xa, x) : x;
          xa = x;
          va = vx;
        }
        throw new Error("las caras no se juntan: indica la semiapertura");
      }
      if (v <= 0) return v < 0 ? biseccion(h, x0, x1) : x1;
      x0 = x1;
      paso *= 1.25;
    }
    throw new Error("no se encontró el borde de la lente");
  }

  function crearLente(abajo, arriba, n, semiapertura) {
    if (!(n > 0)) throw new Error("el índice debe ser positivo");
    if (!(arriba.yv > abajo.yv)) throw new Error("en x = 0 la cara f debe estar por encima de la g");
    const espesor = arriba.yv - abajo.yv;
    const a = semiapertura == null ? bordeNatural(abajo, arriba, espesor) : semiapertura;
    let ymin = Infinity;
    let ymax = -Infinity;
    for (let i = 0; i <= 1000; i++) {
      const x = -a + (2 * a * i) / 1000;
      const yb = abajo.s(x);
      const yt = arriba.s(x);
      if (Number.isFinite(yb)) ymin = Math.min(ymin, yb);
      if (Number.isFinite(yt)) ymax = Math.max(ymax, yt);
    }
    return { abajo, arriba, n, espesor, semiapertura: a, ymin, ymax };
  }

  function lenteBiconvexa(R1, R2, espesor, n = 1.5, k1 = 0, k2 = 0, semiapertura) {
    const g = conica(-espesor / 2, +R1, k1, "g");
    const f = conica(+espesor / 2, -R2, k2, "f");
    return crearLente(g, f, n, semiapertura);
  }

  function contiene(lente, P) {
    const [x, y] = P;
    if (Math.abs(x) >= lente.semiapertura) return false;
    return lente.abajo.s(x) < y && y < lente.arriba.s(x);
  }

  // -------------------------------------------------------------- refraccion
  function refractar(u, normal, n1, n2) {
    u = unitario(u);
    let nh = unitario(normal);
    if (punto(nh, u) > 0) nh = [-nh[0], -nh[1]];
    const cosI = -punto(nh, u);
    const eta = n1 / n2;
    const k = 1 - eta * eta * (1 - cosI * cosI);
    const thetaI = Math.acos(acotar(cosI));
    if (k < 0) {
      const dir = unitario([u[0] + 2 * cosI * nh[0], u[1] + 2 * cosI * nh[1]]);
      return { dir, total: true, normal: nh, thetaI, thetaT: null };
    }
    const c = eta * cosI - Math.sqrt(k);
    const dir = unitario([eta * u[0] + c * nh[0], eta * u[1] + c * nh[1]]);
    return { dir, total: false, normal: nh, thetaI, thetaT: Math.acos(acotar(-punto(nh, dir))) };
  }

  // ------------------------------------------------------------ interseccion
  function rangoEnCaja(P, u, xmin, xmax, ymin, ymax) {
    let lo = -Infinity;
    let hi = Infinity;
    for (const [p, d, a, b] of [[P[0], u[0], xmin, xmax], [P[1], u[1], ymin, ymax]]) {
      if (Math.abs(d) < 1e-15) {
        if (p < a || p > b) return null;
      } else {
        const t1 = (a - p) / d;
        const t2 = (b - p) / d;
        lo = Math.max(lo, Math.min(t1, t2));
        hi = Math.min(hi, Math.max(t1, t2));
      }
    }
    lo = Math.max(lo, EPS);
    return hi <= lo ? null : [lo, hi];
  }

  function interseccion(P, u, sup, semiapertura, lamMin, lamMax, muestras = 2001) {
    const H = (L) => P[1] + L * u[1] - sup.s(P[0] + L * u[0]);
    let Lprev = null;
    let hprev = NaN;
    for (let i = 0; i < muestras; i++) {
      const L = lamMin + ((lamMax - lamMin) * i) / (muestras - 1);
      const x = P[0] + L * u[0];
      const h = Math.abs(x) <= semiapertura ? H(L) : NaN;
      if (Number.isFinite(h) && Number.isFinite(hprev) && hprev * h <= 0) {
        if (hprev === 0) {
          if (i - 1 > 0) return Lprev;
        } else if (h === 0) {
          return L;
        } else {
          return biseccion(H, Lprev, L);
        }
      }
      Lprev = L;
      hprev = h;
    }
    return null;
  }

  function primerImpacto(lente, P, u, muestras = 2001) {
    const pad = 1e-9 + 1e-6 * (lente.ymax - lente.ymin);
    const rango = rangoEnCaja(P, u, -lente.semiapertura - pad, lente.semiapertura + pad,
                              lente.ymin - pad, lente.ymax + pad);
    if (!rango) return null;
    let mejor = null;
    for (const sup of [lente.abajo, lente.arriba]) {
      const lam = interseccion(P, u, sup, lente.semiapertura, rango[0], rango[1], muestras);
      if (lam !== null && (mejor === null || lam < mejor[0])) mejor = [lam, sup];
    }
    return mejor;
  }

  // ------------------------------------------------------- trazado completo
  // `muestras`: puntos con los que se busca el cruce en cada cara antes de refinar con
  // biseccion (2001, como en Python; la pagina usa menos para ir mas rapido).
  function trazar(lente, P, u, nMedio = 1, maxEventos = 12, muestras = 2001) {
    let d = unitario(u);
    let pos = [P[0], P[1]];
    const tr = { puntos: [pos], direcciones: [d], detalles: [], caras: [], estado: "ok" };
    let dentro = contiene(lente, pos);
    for (let e = 0; e < maxEventos; e++) {
      const impacto = primerImpacto(lente, pos, d, muestras);
      if (!impacto) {
        tr.estado = dentro ? "sale_por_el_borde" : tr.detalles.length ? "ok" : "no_toca_lente";
        return tr;
      }
      const [lam, sup] = impacto;
      const Q = [pos[0] + lam * d[0], pos[1] + lam * d[1]];
      const [n1, n2] = dentro ? [lente.n, nMedio] : [nMedio, lente.n];
      const det = refractar(d, [-sup.ds(Q[0]), 1], n1, n2);
      tr.puntos.push(Q);
      tr.direcciones.push(det.dir);
      tr.detalles.push(det);
      tr.caras.push(sup.nombre);
      if (!det.total) dentro = !dentro;
      pos = Q;
      d = det.dir;
    }
    tr.estado = "demasiados_eventos";
    return tr;
  }

  function rayoHacia(lente, P, h) {
    return unitario([h - P[0], lente.abajo.s(h) - P[1]]);
  }

  // ----------------------------------------------------------------- imagen
  function interseccionRectas(P1, u1, P2, u2) {
    const det = -u1[0] * u2[1] + u2[0] * u1[1];
    if (Math.abs(det) < 1e-14) return null;
    const bx = P2[0] - P1[0];
    const by = P2[1] - P1[1];
    const s = (-bx * u2[1] + u2[0] * by) / det;
    const t = (u1[0] * by - u1[1] * bx) / det;
    return { punto: [P1[0] + s * u1[0], P1[1] + s * u1[1]], s, t };
  }

  function salida(tr) {
    return [tr.puntos[tr.puntos.length - 1], tr.direcciones[tr.direcciones.length - 1]];
  }

  function imagenDeDosRayos(t1, t2) {
    const [Q1, e1] = salida(t1);
    const [Q2, e2] = salida(t2);
    const r = interseccionRectas(Q1, e1, Q2, e2);
    return r ? { punto: r.punto, virtual: r.s < 0 && r.t < 0 } : null;
  }

  // ---------------------------------------------------------------- paraxial
  const mult = (A, B) => [
    [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
    [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
  ];

  function matrizSistema(lente) {
    const refr = (n1, n2, R) => {
      const potencia = Number.isFinite(R) ? (n2 - n1) / R : 0;
      return [[1, 0], [-potencia / n2, n1 / n2]];
    };
    const tras = (d) => [[1, d], [0, 1]];
    return mult(refr(lente.n, 1, lente.arriba.R), mult(tras(lente.espesor), refr(1, lente.n, lente.abajo.R)));
  }

  function imagenParaxial(lente, P) {
    const [[A, B], [C, D]] = matrizSistema(lente);
    const s0 = lente.abajo.yv - P[1];
    const den = C * s0 + D;
    if (den === 0) return { y: Infinity, x: Infinity, aumento: Infinity, virtual: false };
    const si = -(A * s0 + B) / den;
    const m = A + si * C;
    return { y: lente.arriba.yv + si, x: m * P[0], aumento: m, virtual: si < 0 };
  }

  function focalEfectiva(lente) {
    const C = matrizSistema(lente)[1][0];
    return C === 0 ? Infinity : -1 / C;
  }

  const Lentes = {
    conica, compilar, desdeExpresion, crearLente, lenteBiconvexa, contiene, refractar,
    interseccion, trazar, rayoHacia, interseccionRectas, salida, imagenDeDosRayos, matrizSistema,
    imagenParaxial, focalEfectiva,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = Lentes;
  else raiz.Lentes = Lentes;
})(typeof globalThis !== "undefined" ? globalThis : this);
