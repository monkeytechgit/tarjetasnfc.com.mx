/* tarjetasnfc.com.mx — interacción del sitio
   Depende de js/productos.js (window.PRODUCTOS, window.PAQUETES, window.SITIO). */
(function () {
  "use strict";

  var BASE = document.body.getAttribute("data-base") || "";
  var PRODUCTOS = window.PRODUCTOS || [];
  var PAQUETES = window.PAQUETES || [];
  var SITIO = window.SITIO || {};
  var CLAVE_CARRITO = "tnfc_carrito";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  function dinero(n) { return "$" + Number(n).toLocaleString("es-MX") + " MXN"; }
  function paquete(id) { return PAQUETES.filter(function (p) { return p.tarjetas === Number(id); })[0] || PAQUETES[0]; }
  function producto(slug) { return PRODUCTOS.filter(function (p) { return p.slug === slug; })[0]; }
  function escapar(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var avisoTimer;
  function aviso(texto) {
    var el = $("#aviso");
    if (!el) return;
    el.textContent = texto;
    el.classList.add("visible");
    clearTimeout(avisoTimer);
    avisoTimer = setTimeout(function () { el.classList.remove("visible"); }, 2600);
  }

  /* ---------- Paneles laterales (menú y carrito) ---------- */
  var fondo = $("#drawer-fondo");
  function abrirPanel(panel) {
    cerrarPaneles();
    panel.classList.add("abierto");
    panel.setAttribute("aria-hidden", "false");
    fondo.classList.add("abierto");
    document.body.classList.add("bloqueado");
    var foco = panel.querySelector("button, a, input");
    if (foco) foco.focus();
  }
  function cerrarPaneles() {
    $$(".drawer.abierto, .buscador.abierto").forEach(function (p) {
      p.classList.remove("abierto");
      p.setAttribute("aria-hidden", "true");
    });
    if (fondo) fondo.classList.remove("abierto");
    document.body.classList.remove("bloqueado");
  }
  $$("[data-abrir]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("data-abrir"));
      if (panel) abrirPanel(panel);
    });
  });
  $$("[data-cerrar]").forEach(function (btn) { btn.addEventListener("click", cerrarPaneles); });
  if (fondo) fondo.addEventListener("click", cerrarPaneles);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { cerrarPaneles(); salirPantallaCompleta(); }
  });
  $$(".menu-movil a").forEach(function (a) { a.addEventListener("click", cerrarPaneles); });

  /* ---------- Header con sombra y volver arriba ---------- */
  var header = $(".header");
  var volver = $(".volver-arriba");
  var barraCompra = $(".barra-compra");
  var ctaCompra = $("#btn-agregar");
  function alDesplazar() {
    var y = window.scrollY;
    if (header) header.classList.toggle("con-sombra", y > 10);
    if (volver) volver.classList.toggle("visible", y > 600);
    if (barraCompra && ctaCompra) {
      var r = ctaCompra.getBoundingClientRect();
      barraCompra.classList.toggle("visible", r.bottom < 0);
    }
  }
  window.addEventListener("scroll", alDesplazar, { passive: true });
  alDesplazar();
  if (volver) volver.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  /* ---------- Buscador ---------- */
  var buscador = $("#buscador");
  var inputBusqueda = $("#buscador-input");
  var resultados = $("#buscador-resultados");
  function normalizar(t) { return t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9 ]/g, ""); }
  function pintarResultados(q) {
    if (!resultados) return;
    var n = normalizar(q.trim());
    var lista = PRODUCTOS.filter(function (p) {
      return !n || normalizar(p.nombre + " " + p.plataforma + " " + p.categoriaNombre).indexOf(n) > -1;
    });
    resultados.innerHTML = lista.length ? lista.map(function (p) {
      return '<a href="' + BASE + p.url + '"><img src="' + BASE + p.imagen + '" alt="" width="52" height="52" loading="lazy">' + escapar(p.nombre) + "</a>";
    }).join("") : '<p class="sin-resultados">No encontramos productos con “' + escapar(q) + '”.</p>';
  }
  function abrirBuscador() {
    cerrarPaneles();
    buscador.classList.add("abierto");
    buscador.setAttribute("aria-hidden", "false");
    fondo.classList.add("abierto");
    pintarResultados(inputBusqueda.value);
    setTimeout(function () { inputBusqueda.focus(); }, 50);
  }
  if (buscador) {
    $$("[data-buscar]").forEach(function (btn) { btn.addEventListener("click", abrirBuscador); });
    inputBusqueda.addEventListener("input", function () { pintarResultados(inputBusqueda.value); });
    // Búsqueda desde Google (SearchAction): /?q=termino
    var consulta = new URLSearchParams(location.search).get("q");
    if (consulta) { inputBusqueda.value = consulta; abrirBuscador(); }
  }

  /* ---------- Carrito ---------- */
  function leerCarrito() {
    try { return JSON.parse(localStorage.getItem(CLAVE_CARRITO)) || []; } catch (e) { return []; }
  }
  function guardarCarrito(items) {
    try { localStorage.setItem(CLAVE_CARRITO, JSON.stringify(items)); } catch (e) { /* sin almacenamiento */ }
    pintarCarrito(items);
  }
  var carrito = leerCarrito();

  function totalCarrito(items) {
    return items.reduce(function (s, it) { return s + paquete(it.paquete).precio * it.cantidad; }, 0);
  }

  function pintarCarrito(items) {
    carrito = items;
    var unidades = items.reduce(function (s, it) { return s + it.cantidad; }, 0);
    $$(".contador-carrito").forEach(function (c) { c.textContent = unidades; });
    var cuerpo = $("#carrito-items");
    var pie = $("#carrito-pie");
    if (!cuerpo) return;
    if (!items.length) {
      cuerpo.innerHTML = '<div class="carrito__vacio"><svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h3l2.6 12.2a1 1 0 0 0 1 .8h9.8a1 1 0 0 0 1-.8L21 7H6"/></svg><p>Tu carrito está vacío.</p><a class="btn btn--primario" href="' + BASE + 'index.html#catalogo">Ver tarjetas</a></div>';
      pie.hidden = true;
      return;
    }
    pie.hidden = false;
    cuerpo.innerHTML = items.map(function (it, i) {
      var p = producto(it.slug);
      var pq = paquete(it.paquete);
      if (!p) return "";
      return '<div class="item-carrito">' +
        '<img src="' + BASE + p.imagen + '" alt="" width="76" height="76">' +
        "<div><h3>" + escapar(p.nombre) + "</h3>" +
        '<p class="item-carrito__meta">' + escapar(pq.nombre) + (it.dato ? " · " + escapar(it.dato) : "") + "</p>" +
        '<div class="item-carrito__fila"><div class="cantidad" data-item="' + i + '">' +
        '<button type="button" data-accion="menos" aria-label="Quitar uno">−</button>' +
        '<input type="number" value="' + it.cantidad + '" min="1" aria-label="Cantidad" readonly>' +
        '<button type="button" data-accion="mas" aria-label="Agregar uno">+</button></div>' +
        '<span class="item-carrito__precio">' + dinero(pq.precio * it.cantidad) + "</span></div>" +
        '<button type="button" class="btn-texto" data-eliminar="' + i + '">Eliminar</button></div></div>';
    }).join("");
    $("#carrito-total").textContent = dinero(totalCarrito(items));
  }

  var contCarrito = $("#carrito-items");
  if (contCarrito) {
    contCarrito.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      var items = carrito.slice();
      if (btn.hasAttribute("data-eliminar")) {
        items.splice(Number(btn.getAttribute("data-eliminar")), 1);
      } else if (btn.hasAttribute("data-accion")) {
        var i = Number(btn.parentNode.getAttribute("data-item"));
        items[i].cantidad = Math.max(1, items[i].cantidad + (btn.getAttribute("data-accion") === "mas" ? 1 : -1));
      }
      guardarCarrito(items);
    });
  }

  function mensajePedido(items) {
    var lineas = ["¡Hola! Quiero hacer este pedido en tarjetasnfc.com.mx:", ""];
    items.forEach(function (it) {
      var p = producto(it.slug);
      var pq = paquete(it.paquete);
      if (!p) return;
      lineas.push("• " + p.nombre + " — " + pq.nombre + " x" + it.cantidad + " = " + dinero(pq.precio * it.cantidad));
      if (it.dato) lineas.push("   " + p.campo.etiqueta + ": " + it.dato);
    });
    lineas.push("", "Total: " + dinero(totalCarrito(items)) + " (envío incluido)");
    return lineas.join("\n");
  }
  function irAWhatsApp(texto) {
    window.open("https://wa.me/" + SITIO.whatsapp + "?text=" + encodeURIComponent(texto), "_blank", "noopener");
  }
  var btnFinalizar = $("#btn-finalizar");
  if (btnFinalizar) btnFinalizar.addEventListener("click", function () { if (carrito.length) irAWhatsApp(mensajePedido(carrito)); });

  /* ---------- Pago con Stripe (Supabase Edge Functions) ---------- */
  function llamarFuncion(ruta, opciones) {
    opciones = opciones || {};
    opciones.headers = Object.assign({ apikey: SITIO.anon, Authorization: "Bearer " + SITIO.anon }, opciones.headers || {});
    return fetch(SITIO.funciones + "/" + ruta, opciones).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) throw new Error(d.error || "Ocurrió un error. Intenta de nuevo.");
        return d;
      });
    });
  }
  var botonesPago = [];
  function irAPagar(items, boton) {
    if (!items.length || boton.disabled) return;
    if (!boton.dataset.html) boton.dataset.html = boton.innerHTML;
    if (botonesPago.indexOf(boton) < 0) botonesPago.push(boton);
    boton.disabled = true;
    boton.textContent = "Abriendo pago seguro…";
    llamarFuncion("create-checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: items.map(function (it) { return { slug: it.slug, paquete: it.paquete, cantidad: it.cantidad, dato: it.dato }; }) })
    }).then(function (d) {
      if (!d.url) throw new Error("No pudimos abrir el pago seguro.");
      location.href = d.url;
    }).catch(function (e) {
      restaurarBoton(boton);
      aviso(e.message === "Failed to fetch" ? "Sin conexión. Revisa tu internet e intenta de nuevo." : e.message);
    });
  }
  function restaurarBoton(boton) {
    boton.disabled = false;
    if (boton.dataset.html) boton.innerHTML = boton.dataset.html;
  }
  // Al volver desde Stripe con el botón «atrás» la página puede salir de caché con el botón bloqueado.
  window.addEventListener("pageshow", function () { botonesPago.forEach(restaurarBoton); });

  var btnPagar = $("#btn-pagar");
  if (btnPagar) btnPagar.addEventListener("click", function () { irAPagar(carrito, btnPagar); });

  if (new URLSearchParams(location.search).get("pago") === "cancelado") {
    history.replaceState(null, "", location.pathname + location.hash);
    if (carrito.length) abrirPanel($("#carrito"));
    setTimeout(function () { aviso("El pago se canceló. Tu carrito sigue guardado."); }, 300);
  }

  /* ---------- Página de gracias (regreso de Stripe) ---------- */
  var gracias = $("#pagina-gracias");
  if (gracias) {
    var sesion = new URLSearchParams(location.search).get("session_id");
    var titulo = $("#gracias-titulo");
    var texto = $("#gracias-texto");
    var mostrar = function (estado, t, p) { gracias.setAttribute("data-estado", estado); titulo.textContent = t; texto.textContent = p; };
    if (!sesion) {
      mostrar("ok", "¡Gracias por tu compra!", "Si completaste tu pago, te contactaremos por correo electrónico para preparar tu pedido.");
    } else {
      guardarCarrito([]); // Stripe solo regresa aquí cuando el pago se completó o quedó en proceso
      llamarFuncion("checkout-status?session_id=" + encodeURIComponent(sesion)).then(function (d) {
        $("#gracias-pedido").textContent = d.pedido;
        $("#gracias-total").textContent = dinero(d.total);
        $("#gracias-correo").textContent = d.correo || "el correo que registraste";
        $("#gracias-datos").hidden = false;
        if (d.estado_pago === "paid") {
          mostrar("ok", "¡Compra realizada con éxito!", "Recibimos tu pago. Nos pondremos en contacto contigo por correo electrónico para confirmar los detalles y enviarte tu pedido.");
        } else {
          mostrar("pendiente", "¡Pedido registrado!", "Tu pago está en proceso (por ejemplo, OXXO o transferencia). En cuanto se confirme, te contactaremos por correo electrónico.");
        }
      }).catch(function () {
        mostrar("ok", "¡Compra realizada con éxito!", "Recibimos tu pedido. Nos pondremos en contacto contigo por correo electrónico para confirmar los detalles y enviarte tu pedido.");
      });
    }
  }

  pintarCarrito(carrito);

  /* ---------- Catálogo: filtros y orden ---------- */
  var rejilla = $("#rejilla-catalogo");
  if (rejilla) {
    var chips = $$(".chip[data-categoria]");
    var orden = $("#orden");
    var conteo = $("#conteo");
    var tarjetas = $$(".tarjeta-producto", rejilla);
    var categoria = new URLSearchParams(location.search).get("categoria") || "todas";

    function aplicar() {
      var visibles = 0;
      tarjetas.forEach(function (t) {
        var ok = categoria === "todas" || t.getAttribute("data-categoria") === categoria;
        t.hidden = !ok;
        if (ok) visibles++;
      });
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.getAttribute("data-categoria") === categoria)); });
      conteo.textContent = visibles + (visibles === 1 ? " producto" : " productos");
    }
    function ordenar() {
      var criterio = orden.value;
      var lista = tarjetas.slice().sort(function (a, b) {
        if (criterio === "az") return a.getAttribute("data-nombre").localeCompare(b.getAttribute("data-nombre"), "es");
        if (criterio === "za") return b.getAttribute("data-nombre").localeCompare(a.getAttribute("data-nombre"), "es");
        return Number(a.getAttribute("data-orden")) - Number(b.getAttribute("data-orden"));
      });
      lista.forEach(function (t) { rejilla.appendChild(t); });
    }
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        categoria = c.getAttribute("data-categoria");
        var url = new URL(location.href);
        if (categoria === "todas") url.searchParams.delete("categoria"); else url.searchParams.set("categoria", categoria);
        history.replaceState(null, "", url);
        aplicar();
      });
    });
    orden.addEventListener("change", ordenar);
    // enlaces del menú hacia categorías estando en el index
    $$('a[href*="categoria="]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        var u = new URL(a.href, location.href);
        if (u.pathname !== location.pathname) return;
        e.preventDefault();
        categoria = u.searchParams.get("categoria") || "todas";
        history.replaceState(null, "", u);
        aplicar();
        cerrarPaneles();
        document.getElementById("catalogo").scrollIntoView({ behavior: "smooth" });
      });
    });
    aplicar();
  }

  /* ---------- Galería de producto ---------- */
  var galeria = $(".galeria");
  function salirPantallaCompleta() {
    if (galeria && galeria.classList.contains("pantalla-completa")) {
      galeria.classList.remove("pantalla-completa");
      document.body.classList.remove("bloqueado");
    }
  }
  if (galeria) {
    var pista = $(".galeria__pista", galeria);
    var slides = $$(".galeria__slide", galeria);
    var minis = $$(".miniatura", galeria);
    var actual = 0;
    function ir(i) {
      actual = (i + slides.length) % slides.length;
      pista.style.transform = "translateX(" + (-100 * actual) + "%)";
      minis.forEach(function (m, j) { m.setAttribute("aria-current", String(j === actual)); });
      slides.forEach(function (s, j) { s.setAttribute("aria-hidden", String(j !== actual)); });
      slides.forEach(function (s, j) {
        var v = s.querySelector("video");
        if (!v) return;
        if (j === actual) {
          var reproduccion = v.play();
          if (reproduccion && reproduccion.catch) reproduccion.catch(function () { /* autoplay bloqueado */ });
        } else {
          v.pause();
        }
      });
      var tira = minis[actual] && minis[actual].parentNode;
      if (tira) {
        var m = minis[actual];
        if (m.offsetLeft < tira.scrollLeft) tira.scrollLeft = m.offsetLeft;
        else if (m.offsetLeft + m.offsetWidth > tira.scrollLeft + tira.clientWidth) tira.scrollLeft = m.offsetLeft + m.offsetWidth - tira.clientWidth;
      }
    }
    $(".galeria__flecha--prev", galeria).addEventListener("click", function () { ir(actual - 1); });
    $(".galeria__flecha--next", galeria).addEventListener("click", function () { ir(actual + 1); });
    minis.forEach(function (m, j) { m.addEventListener("click", function () { ir(j); }); });
    $(".galeria__expandir", galeria).addEventListener("click", function () {
      var activa = galeria.classList.toggle("pantalla-completa");
      document.body.classList.toggle("bloqueado", activa);
    });
    var x0 = null;
    var visor = $(".galeria__visor", galeria);
    visor.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    visor.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) ir(actual + (dx < 0 ? 1 : -1));
      x0 = null;
    });
    ir(0);
  }

  /* ---------- Formulario de contacto ---------- */
  var formContacto = $("#form-contacto");
  if (formContacto) {
    var validarContacto = function () {
      var primero = null;
      $$("[required]", formContacto).forEach(function (c) {
        var mal = !c.value.trim() || (c.type === "email" && !c.checkValidity());
        c.classList.toggle("error", mal);
        if (mal && !primero) primero = c;
      });
      if (primero) { primero.focus(); aviso("Revisa los campos marcados."); }
      return !primero;
    };
    var mensajeContacto = function () {
      var el = formContacto.elements;
      var lineas = ["¡Hola! Les escribo desde tarjetasnfc.com.mx:", "", "Nombre: " + el.nombre.value.trim(), "Email: " + el.email.value.trim()];
      if (el.telefono.value.trim()) lineas.push("Teléfono: " + el.telefono.value.trim());
      lineas.push("", el.comentario.value.trim());
      return lineas.join("\n");
    };
    $$(".input", formContacto).forEach(function (c) { c.addEventListener("input", function () { c.classList.remove("error"); }); });
    formContacto.addEventListener("submit", function (e) {
      e.preventDefault();
      if (validarContacto()) irAWhatsApp(mensajeContacto());
    });
    $("#btn-correo").addEventListener("click", function () {
      if (validarContacto()) {
        location.href = "mailto:" + SITIO.correo + "?subject=" + encodeURIComponent("Contacto desde tarjetasnfc.com.mx") + "&body=" + encodeURIComponent(mensajeContacto());
      }
    });
  }

  /* ---------- Compra: paquetes, cantidad y agregar ---------- */
  var form = $("#form-compra");
  if (form) {
    var slug = form.getAttribute("data-slug");
    var p = producto(slug);
    var inputCantidad = $("#cantidad");
    var inputDato = $("#dato-negocio");

    function paqueteElegido() { return paquete($('input[name="paquete"]:checked', form).value); }
    function actualizarPrecio() {
      var pq = paqueteElegido();
      var cant = Math.max(1, parseInt(inputCantidad.value, 10) || 1);
      $("#precio-actual").textContent = dinero(pq.precio);
      $("#precio-antes").textContent = dinero(pq.antes);
      $("#precio-ahorro").textContent = "Ahorra " + Math.round((1 - pq.precio / pq.antes) * 100) + "%";
      $("#precio-nota").textContent = pq.tarjetas > 1 ? dinero(pq.unidad) + " por tarjeta · envío gratis incluido" : "Envío gratis incluido a todo México";
      $("#btn-agregar-precio").textContent = dinero(pq.precio * cant);
      $$(".barra-compra__precio").forEach(function (el) { el.textContent = dinero(pq.precio * cant); });
      $$(".barra-compra__paquete").forEach(function (el) { el.textContent = pq.nombre; });
    }
    $$('input[name="paquete"]', form).forEach(function (r) { r.addEventListener("change", actualizarPrecio); });
    $$("[data-cantidad]", form).forEach(function (b) {
      b.addEventListener("click", function () {
        var v = (parseInt(inputCantidad.value, 10) || 1) + Number(b.getAttribute("data-cantidad"));
        inputCantidad.value = Math.min(99, Math.max(1, v));
        actualizarPrecio();
      });
    });
    inputCantidad.addEventListener("input", actualizarPrecio);

    function validar() {
      var v = inputDato.value.trim();
      inputDato.classList.toggle("error", !v);
      if (!v) {
        inputDato.focus({ preventScroll: true });
        inputDato.scrollIntoView({ behavior: "smooth", block: "center" });
        aviso("Completa «" + p.campo.etiqueta + "» para configurar tu tarjeta.");
      }
      return v;
    }
    function itemActual(dato) {
      return { slug: slug, paquete: paqueteElegido().tarjetas, cantidad: Math.max(1, parseInt(inputCantidad.value, 10) || 1), dato: dato };
    }
    inputDato.addEventListener("input", function () { inputDato.classList.remove("error"); });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var dato = validar();
      if (!dato) return;
      var nuevo = itemActual(dato);
      var items = carrito.slice();
      var igual = items.filter(function (it) { return it.slug === nuevo.slug && it.paquete === nuevo.paquete && it.dato === nuevo.dato; })[0];
      if (igual) igual.cantidad += nuevo.cantidad; else items.push(nuevo);
      guardarCarrito(items);
      abrirPanel($("#carrito"));
    });
    $("#btn-comprar").addEventListener("click", function () {
      var dato = validar();
      if (dato) irAPagar([itemActual(dato)], $("#btn-comprar"));
    });
    $$(".barra-compra .btn").forEach(function (b) {
      b.addEventListener("click", function () { $("#btn-agregar").click(); });
    });
    actualizarPrecio();
  }
})();
