// Crea el pedido en la base de datos y una sesión de Stripe Checkout.
// POST { items: [{ slug, paquete, cantidad, dato }] }  →  { url, pedido }
// Los precios y los price_… salen de la base de datos, nunca del navegador.
import { admin, cabecerasCors, json, origenPermitido, SITE_URL, SITIO, stripe } from "../_shared/comun.ts";

const MAX_PARTIDAS = 20;
const MAX_CANTIDAD = 50;
const MAX_DATO = 500;

type Partida = { slug: string; paquete: number; cantidad: number; dato: string };

function validar(items: unknown): Partida[] | string {
  if (!Array.isArray(items) || items.length === 0) return "Tu carrito está vacío.";
  if (items.length > MAX_PARTIDAS) return `Máximo ${MAX_PARTIDAS} productos distintos por pedido.`;
  const partidas: Partida[] = [];
  for (const it of items) {
    const slug = typeof it?.slug === "string" ? it.slug.trim() : "";
    const paquete = Number(it?.paquete);
    const cantidad = Number(it?.cantidad);
    const dato = typeof it?.dato === "string" ? it.dato.trim() : "";
    if (!/^[a-z0-9-]{3,80}$/.test(slug)) return "Producto no válido.";
    if (!Number.isInteger(paquete) || paquete <= 0) return "Paquete no válido.";
    if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > MAX_CANTIDAD) return `La cantidad debe ser de 1 a ${MAX_CANTIDAD}.`;
    if (!dato) return "Falta el enlace o dato que programaremos en tu tarjeta.";
    if (dato.length > MAX_DATO) return "El enlace es demasiado largo.";
    partidas.push({ slug, paquete, cantidad, dato });
  }
  return partidas;
}

// "url1, url2" → ["url1", "url2"]
function separarEnlaces(dato: string): string[] {
  return dato.split(",").map((s) => s.trim()).filter(Boolean);
}

function numeroPedido(): string {
  const hoy = new Date().toISOString().slice(2, 10).replace(/-/g, "");
  const letras = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const azar = crypto.getRandomValues(new Uint8Array(5));
  return `TNFC-${hoy}-${Array.from(azar, (b) => letras[b % letras.length]).join("")}`;
}

Deno.serve(async (req) => {
  const cors = cabecerasCors(req);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (req.method !== "POST") return json({ error: "Método no permitido." }, 405, cors);
  if (!origenPermitido(req)) return json({ error: "Origen no permitido." }, 403, cors);

  let cuerpo: { items?: unknown };
  try { cuerpo = await req.json(); } catch { return json({ error: "Solicitud no válida." }, 400, cors); }
  const partidas = validar(cuerpo?.items);
  if (typeof partidas === "string") return json({ error: partidas }, 400, cors);

  // Catálogo desde la base de datos
  const slugs = [...new Set(partidas.map((p) => p.slug))];
  const { data: productos, error: errProd } = await admin
    .from("ecommerce_products")
    .select("id, slug, name, platform, link_label, stripe_product_id")
    .in("slug", slugs).eq("active", true).eq("site", SITIO);
  if (errProd) { console.error("catálogo", errProd); return json({ error: "No pudimos cargar el catálogo." }, 500, cors); }
  const { data: precios, error: errPrecio } = await admin
    .from("ecommerce_product_prices")
    .select("id, ecommerce_product_id, package_cards, unit_amount, currency, stripe_price_id")
    .in("ecommerce_product_id", (productos ?? []).map((p) => p.id)).eq("active", true);
  if (errPrecio) { console.error("precios", errPrecio); return json({ error: "No pudimos cargar los precios." }, 500, cors); }

  const lineas = [];
  for (const [i, p] of partidas.entries()) {
    const prod = productos?.find((x) => x.slug === p.slug);
    const precio = prod && precios?.find((x) => x.ecommerce_product_id === prod.id && x.package_cards === p.paquete);
    if (!prod || !precio) return json({ error: "Uno de los productos ya no está disponible. Actualiza la página." }, 409, cors);
    if (!precio.stripe_price_id) {
      return json({ error: `El paquete de ${p.paquete} tarjetas de ${prod.platform} aún no está disponible para pago en línea. Escríbenos por WhatsApp.` }, 409, cors);
    }
    const unitario = Number(precio.unit_amount);
    lineas.push({ i, p, prod, precio, unitario, total: unitario * p.cantidad });
  }

  // Doble verificación contra Stripe: el price_… debe existir, estar activo, ser MXN,
  // costar lo mismo que en la base de datos y pertenecer al producto correcto.
  try {
    const unicos = [...new Map(lineas.map((l) => [l.precio.stripe_price_id, l])).values()];
    const enStripe = await Promise.all(unicos.map((l) => stripe.prices.retrieve(l.precio.stripe_price_id!)));
    for (const [k, sp] of enStripe.entries()) {
      const l = unicos[k];
      const producto = typeof sp.product === "string" ? sp.product : sp.product.id;
      if (!sp.active || sp.currency !== "mxn" || sp.unit_amount !== Math.round(l.unitario * 100) ||
          (l.prod.stripe_product_id && producto !== l.prod.stripe_product_id)) {
        console.error("precio inconsistente", sp.id, { activo: sp.active, moneda: sp.currency, monto: sp.unit_amount, producto, esperado: l });
        return json({ error: `El precio de ${l.prod.platform} (${l.p.paquete} tarjetas) no coincide. Escríbenos por WhatsApp para completar tu compra.` }, 409, cors);
      }
    }
  } catch (e) {
    console.error("stripe.prices.retrieve", e);
    return json({ error: "No pudimos conectar con el sistema de pagos. Intenta de nuevo." }, 502, cors);
  }

  const subtotal = lineas.reduce((s, l) => s + l.total, 0);
  const idPedido = crypto.randomUUID();
  let numero = "";

  // Pedido (reintenta si el número de pedido llegara a repetirse)
  for (let intento = 0; intento < 3; intento++) {
    numero = numeroPedido();
    const { error } = await admin.from("orders").insert({
      id: idPedido,
      order_number: numero,
      customer_name: "Pendiente de pago",
      status: "draft",
      payment_status: "pending",
      currency: "MXN",
      subtotal_amount: subtotal,
      tax_amount: 0,
      shipping_amount: 0,
      total_amount: subtotal,
      checkout_client_reference_id: idPedido,
      ecommerce_source: "web_cart",
      market: "MX",
      locale: "es-MX",
      updated_at: new Date().toISOString(),
      metadata: {
        site: SITIO,
        prices_include_tax: true,
        user_agent: req.headers.get("user-agent")?.slice(0, 300) ?? null,
        origin: req.headers.get("origin"),
      },
    });
    if (!error) break;
    if (error.code !== "23505" || intento === 2) {
      console.error("orders.insert", error);
      return json({ error: "No pudimos registrar tu pedido. Intenta de nuevo." }, 500, cors);
    }
  }

  // Partidas y enlaces
  const { data: filas, error: errItems } = await admin.from("order_items").insert(lineas.map((l) => ({
    order_id: idPedido,
    description: `${l.prod.name} · ${l.p.paquete} ${l.p.paquete === 1 ? "tarjeta" : "tarjetas"}`,
    quantity: l.p.cantidad,
    unit_price: l.unitario,
    total_price: l.total,
    ecommerce_product_id: l.prod.id,
    stripe_product_id: l.prod.stripe_product_id,
    stripe_price_id: l.precio.stripe_price_id,
    cart_item_id: String(l.i + 1),
    metadata: { slug: l.p.slug, platform: l.prod.platform, package_cards: l.p.paquete, cards_total: l.p.paquete * l.p.cantidad },
    configuration: { field_label: l.prod.link_label, value: l.p.dato, links: separarEnlaces(l.p.dato) },
  }))).select("id, cart_item_id");
  if (errItems || !filas) {
    console.error("order_items.insert", errItems);
    await admin.from("orders").delete().eq("id", idPedido);
    return json({ error: "No pudimos registrar tu pedido. Intenta de nuevo." }, 500, cors);
  }

  const enlaces = lineas.flatMap((l) => {
    const fila = filas.find((f) => f.cart_item_id === String(l.i + 1))!;
    return separarEnlaces(l.p.dato).map((valor, k) => ({
      order_id: idPedido,
      order_item_id: fila.id,
      platform: l.prod.platform,
      field_label: l.prod.link_label,
      value: valor,
      is_url: /^https?:\/\//i.test(valor) || /^[\w-]+(\.[\w-]+)+(\/|$)/.test(valor),
      position: k + 1,
    }));
  });
  if (enlaces.length) {
    const { error } = await admin.from("order_item_links").insert(enlaces);
    if (error) console.error("order_item_links.insert", error); // los enlaces también quedan en order_items.configuration
  }

  // Sesión de Stripe Checkout
  const meta = { order_id: idPedido, order_number: numero, site: SITIO, ecommerce_source: "web_cart" };
  let sesion;
  try {
    sesion = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: lineas.map((l) => ({ price: l.precio.stripe_price_id!, quantity: l.p.cantidad })),
      client_reference_id: idPedido,
      metadata: meta,
      payment_intent_data: { metadata: meta, description: `Pedido ${numero} · TarjetasNFC` },
      locale: "es-419",
      billing_address_collection: "auto",
      shipping_address_collection: { allowed_countries: ["MX"] },
      shipping_options: [{
        shipping_rate_data: {
          type: "fixed_amount",
          fixed_amount: { amount: 0, currency: "mxn" },
          display_name: "Envío gratis a todo México",
          delivery_estimate: { minimum: { unit: "business_day", value: 3 }, maximum: { unit: "business_day", value: 5 } },
        },
      }],
      phone_number_collection: { enabled: true },
      custom_text: {
        submit: { message: "Programamos tu tarjeta con el enlace que nos diste y te contactamos por correo electrónico." },
      },
      success_url: `${SITE_URL}/gracias.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${SITE_URL}/?pago=cancelado`,
    }, { idempotencyKey: `checkout-${idPedido}` });
  } catch (e) {
    console.error("checkout.sessions.create", e);
    await admin.from("orders").update({
      status: "cancelled", payment_status: "cancelled", notes: "No se pudo crear la sesión de Stripe.", updated_at: new Date().toISOString(),
    }).eq("id", idPedido);
    return json({ error: "No pudimos abrir el pago seguro. Intenta de nuevo en un momento." }, 502, cors);
  }

  await admin.from("orders").update({ stripe_checkout_session_id: sesion.id, updated_at: new Date().toISOString() }).eq("id", idPedido);
  await admin.from("order_checkout_events").insert({
    order_id: idPedido,
    stripe_checkout_session_id: sesion.id,
    event_type: "checkout.session.created",
    payment_status: sesion.payment_status,
    amount_total: (sesion.amount_total ?? 0) / 100,
    currency: (sesion.currency ?? "mxn").toUpperCase(),
    payload: { id: sesion.id, expires_at: sesion.expires_at, items: partidas.length },
  });

  return json({ url: sesion.url, pedido: numero }, 200, cors);
});
