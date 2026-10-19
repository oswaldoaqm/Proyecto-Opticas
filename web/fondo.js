/*
 * Fondo de la pagina, en dos capas:
 * - #luz, arriba de la pagina (se va con la cabecera al desplazar): la caustica de la lente de
 *   trabajo con caras esfericas (R = 10, d = 2, n = 1.5) iluminada por un haz paralelo,
 *   calculada con el mismo trazador de la simulacion.
 * - #fondo, fijo detras de todo: charcos suaves de los colores de la luz que tiñen el vidrio
 *   de los paneles.
 * Se dibuja una vez y se repite solo si cambia el tamano o el tema. Es decorativo: si algo
 * falla, la pagina funciona igual.
 */
(function () {
  "use strict";

  const L = window.Lentes;
  const capaLuz = document.getElementById("luz");
  const capaFondo = document.getElementById("fondo");
  if (!L || !capaLuz || !capaFondo || !capaLuz.getContext) return;
  const raiz = document.documentElement;

  // ------------------------------------------------------------- los rayos
  const lente = L.lenteBiconvexa(10, 10, 2, 1.5, 0, 0);
  const [[A], [C]] = L.matrizSistema(lente);
  const foco = lente.arriba.yv - A / C; // foco imagen paraxial para un haz paralelo
  const rayos = [];
  const N = 241;
  for (let i = 0; i < N; i++) {
    const x = lente.semiapertura * (-0.97 + (1.94 * i) / (N - 1));
    const tr = L.trazar(lente, [x, lente.ymin - 1], [0, 1], 1, 4, 241);
    if (tr.estado === "ok" && tr.puntos.length === 3 && !tr.detalles.some((d) => d.total)) rayos.push(tr);
  }

  // ------------------------------------------------------------- utilidades
  function rgba(hex, a) {
    const h = hex.trim().replace("#", "");
    const v = parseInt(h.length === 3 ? h.replace(/./g, "$&$&") : h, 16);
    return `rgba(${(v >> 16) & 255}, ${(v >> 8) & 255}, ${v & 255}, ${a})`;
  }

  function preparar(lienzo) {
    const W = lienzo.clientWidth;
    const H = lienzo.clientHeight;
    if (W < 2 || H < 2) return null;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    lienzo.width = Math.round(W * dpr);
    lienzo.height = Math.round(H * dpr);
    const ctx = lienzo.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    return { ctx, W, H };
  }

  function charco(ctx, x, y, r, color, a) {
    if (!(r > 0)) return;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(color, a));
    g.addColorStop(0.45, rgba(color, a * 0.45));
    g.addColorStop(1, rgba(color, 0));
    ctx.fillStyle = g;
    ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
  }

  // ---------------------------------------------------------------- dibujo
  function dibujar() {
    const estilo = getComputedStyle(raiz);
    const color = (nombre) => estilo.getPropertyValue(nombre).trim() || "#888888";
    const oscuro = estilo.getPropertyValue("--modo").trim() === "oscuro";
    const f = oscuro ? 1.3 : 1;

    // Charcos fijos detras de los paneles: la luz que llega, abajo a la izquierda, y la que
    // sale, a la derecha.
    const fondo = preparar(capaFondo);
    if (fondo) {
      const { ctx, W, H } = fondo;
      const m = Math.max(W, H);
      charco(ctx, 0.12 * W, 0.86 * H, 0.6 * m, color("--incidente"), 0.15 * f);
      charco(ctx, 0.9 * W, 0.42 * H, 0.46 * m, color("--emergente"), 0.14 * f);
      charco(ctx, 0.62 * W, 0.08 * H, 0.3 * m, color("--imagen"), 0.1 * f);
    }

    const luz = preparar(capaLuz);
    if (!luz) return;
    const { ctx, W, H } = luz;
    const a = lente.semiapertura;

    // La luz va de izquierda a derecha: en pantallas anchas la lente queda a la derecha del
    // titulo; en el celular, en una franja sobre el titulo (estilo.css le deja ese espacio).
    const angosta = W < 700;
    const alto = window.innerHeight || 800;
    const y0 = angosta ? 48 : Math.min(Math.max(0.14 * alto, 112), 160);
    const cx = (angosta ? 0.5 : 0.66) * W;
    const k = Math.min((angosta ? 32 : Math.min(0.115 * alto, 105)) / a, (0.93 * W - cx) / foco);
    const aP = (p) => [cx + p[1] * k, y0 - p[0] * k];
    const fx = cx + foco * k;
    const lejos = (W + H) / k;

    // El brillo del foco y del vidrio, sin pasar del borde de abajo de la capa.
    const m = Math.max(W, alto);
    charco(ctx, fx, y0, Math.min(0.17 * m, H - y0 - 2), color("--imagen"), 0.28 * f);
    charco(ctx, cx, y0, Math.min(0.08 * m, H - y0 - 2), color("--transmitido"), 0.12 * f);

    // Los rayos, uno por uno, para que la luz se sume donde se juntan (la caustica). El haz
    // aparece de a poco desde la izquierda y con los bordes suaves.
    ctx.globalCompositeOperation = oscuro ? "lighter" : "source-over";
    ctx.lineWidth = 1;
    const alfa = oscuro ? 0.09 : 0.08;
    const entrada = ctx.createLinearGradient(angosta ? 0 : 0.36 * W, 0, cx, 0);
    entrada.addColorStop(0, rgba(color("--incidente"), 0));
    entrada.addColorStop(1, rgba(color("--incidente"), alfa));
    const salidaLuz = ctx.createLinearGradient(fx, 0, W, 0);
    salidaLuz.addColorStop(0, rgba(color("--emergente"), alfa));
    salidaLuz.addColorStop(1, rgba(color("--emergente"), alfa * 0.45));
    const vidrio = rgba(color("--transmitido"), alfa * 0.9);
    const tramo = (p, q, estiloTrazo) => {
      const s = aP(p);
      const t = aP(q);
      ctx.strokeStyle = estiloTrazo;
      ctx.beginPath();
      ctx.moveTo(s[0], s[1]);
      ctx.lineTo(t[0], t[1]);
      ctx.stroke();
    };
    for (const tr of rayos) {
      const [P, Q1, Q2] = tr.puntos;
      const e = tr.direcciones[2];
      const borde = Math.min(1, (1 - Math.abs(P[0]) / a) / 0.3);
      ctx.globalAlpha = borde * borde * (3 - 2 * borde);
      tramo([P[0], P[1] - lejos], Q1, entrada);
      ctx.globalAlpha = 1;
      tramo(Q1, Q2, vidrio);
      tramo(Q2, [Q2[0] + lejos * e[0], Q2[1] + lejos * e[1]], salidaLuz);
    }

    // El contorno de la lente.
    ctx.globalCompositeOperation = "source-over";
    ctx.beginPath();
    const n = 90;
    for (let i = 0; i <= n; i++) {
      const x = -a + (2 * a * i) / n;
      const s = aP([x, lente.abajo.s(x)]);
      if (i) ctx.lineTo(s[0], s[1]);
      else ctx.moveTo(s[0], s[1]);
    }
    for (let i = n; i >= 0; i--) {
      const x = -a + (2 * a * i) / n;
      const s = aP([x, lente.arriba.s(x)]);
      ctx.lineTo(s[0], s[1]);
    }
    ctx.closePath();
    ctx.fillStyle = rgba(color("--lente-relleno"), oscuro ? 0.12 : 0.3);
    ctx.fill();
    ctx.strokeStyle = rgba(color("--tinta-2"), oscuro ? 0.35 : 0.3);
    ctx.stroke();
  }

  let pedido = false;
  function programar() {
    if (pedido) return;
    pedido = true;
    requestAnimationFrame(() => {
      pedido = false;
      try {
        dibujar();
      } catch (e) {
        capaLuz.hidden = true;
        capaFondo.hidden = true;
      }
    });
  }

  if (window.ResizeObserver) {
    const ro = new ResizeObserver(programar);
    ro.observe(capaLuz);
    ro.observe(capaFondo);
  } else {
    window.addEventListener("resize", programar);
  }
  if (window.matchMedia) {
    const oscuro = window.matchMedia("(prefers-color-scheme: dark)");
    if (oscuro.addEventListener) oscuro.addEventListener("change", programar);
  }
  if (window.MutationObserver) {
    new MutationObserver(programar).observe(raiz, { attributes: true, attributeFilter: ["data-theme", "class", "style"] });
  }
  programar();
})();
