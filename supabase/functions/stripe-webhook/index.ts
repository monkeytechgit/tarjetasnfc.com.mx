// Webhook de Stripe: actualiza el pedido y guarda cada evento en order_checkout_events.
// URL: https://glgvxxbhmbvyqacwkseg.supabase.co/functions/v1/stripe-webhook
// Eventos: checkout.session.completed, checkout.session.async_payment_succeeded,
//          checkout.session.async_payment_failed, checkout.session.expired, charge.refunded
import Stripe from "npm:stripe@17.7.0";
import { admin, centavosAPesos, stripe } from "../_shared/comun.ts";

const SECRETO = Deno.env.get("STRIPE_WEBHOOK_SECRET") ?? "";
const cripto = Stripe.createSubtleCryptoProvider();

type Pedido = { id: string; payment_status: string; status: string; customer_name: string; metadata: Record<string, unknown> };
const CAMPOS = "id, payment_status, status, customer_name, metadata";

async function buscarPorSesion(s: Stripe.Checkout.Session): Promise<Pedido | null> {
  const id = s.metadata?.order_id || s.client_reference_id;
  if (id && /^[0-9a-f-]{36}$/i.test(id)) {
    const { data } = await admin.from("orders").select(CAMPOS).eq("id", id).maybeSingle();
    if (data) return data as Pedido;
  }
  const { data } = await admin.from("orders").select(CAMPOS).eq("stripe_checkout_session_id", s.id).maybeSingle();
  return (data as Pedido) ?? null;
}

async function actualizar(id: string, cambios: Record<string, unknown>) {
  const { error } = await admin.from("orders").update({ ...cambios, updated_at: new Date().toISOString() }).eq("id", id);
  if (error) throw new Error(`orders.update: ${error.message}`);
}

async function sesionCompletada(s: Stripe.Checkout.Session, pedido: Pedido) {
  // Según la versión de API del webhook, el envío llega en uno u otro campo.
  // deno-lint-ignore no-explicit-any
  const sx = s as any;
  const envio = sx.collected_information?.shipping_details ?? sx.shipping_details ?? null;
  const cliente = s.customer_details;
  const pagado = s.payment_status === "paid" || s.payment_status === "no_payment_required";
  const yaPagado = pedido.payment_status === "paid";
  await actualizar(pedido.id, {
    customer_name: envio?.name || cliente?.name || pedido.customer_name,
    customer_email: cliente?.email ?? null,
    customer_phone: cliente?.phone ?? null,
    company_name: sx.customer_details?.business_name ?? null,
    stripe_checkout_session_id: s.id,
    stripe_payment_intent_id: typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id ?? null,
    subtotal_amount: centavosAPesos(s.amount_subtotal),
    shipping_amount: centavosAPesos(s.total_details?.amount_shipping),
    tax_amount: centavosAPesos(s.total_details?.amount_tax),
    total_amount: centavosAPesos(s.amount_total),
    currency: (s.currency ?? "mxn").toUpperCase(),
    payment_status: pagado || yaPagado ? "paid" : "pending",
    status: pagado || yaPagado ? (pedido.status === "draft" ? "paid" : pedido.status) : pedido.status,
    metadata: {
      ...pedido.metadata,
      shipping_address: envio?.address ?? null,
      shipping_name: envio?.name ?? null,
      billing_address: cliente?.address ?? null,
      stripe_customer_id: typeof s.customer === "string" ? s.customer : s.customer?.id ?? null,
      payment_method_types: s.payment_method_types,
      checkout_completed_at: new Date().toISOString(),
      ...(pagado ? { paid_at: new Date().toISOString() } : {}),
    },
  });
}

async function procesar(evento: Stripe.Event): Promise<{ orderId: string | null; sesionId: string | null; estadoPago: string | null; monto: number | null; moneda: string | null }> {
  if (evento.type === "charge.refunded") {
    const cargo = evento.data.object as Stripe.Charge;
    const pi = typeof cargo.payment_intent === "string" ? cargo.payment_intent : cargo.payment_intent?.id;
    const { data } = pi ? await admin.from("orders").select(CAMPOS).eq("stripe_payment_intent_id", pi).maybeSingle() : { data: null };
    const pedido = data as Pedido | null;
    if (pedido) {
      await actualizar(pedido.id, {
        ...(cargo.refunded ? { payment_status: "refunded", status: "cancelled" } : {}),
        metadata: { ...pedido.metadata, refunded_amount: centavosAPesos(cargo.amount_refunded), refunded_at: new Date().toISOString() },
      });
    }
    return { orderId: pedido?.id ?? null, sesionId: null, estadoPago: cargo.refunded ? "refunded" : "partial_refund", monto: centavosAPesos(cargo.amount_refunded), moneda: cargo.currency };
  }

  const s = evento.data.object as Stripe.Checkout.Session;
  const pedido = await buscarPorSesion(s);
  const resultado = { orderId: pedido?.id ?? null, sesionId: s.id, estadoPago: s.payment_status, monto: centavosAPesos(s.amount_total), moneda: s.currency };
  if (!pedido) return resultado; // sesión de otro sitio o pago que no salió de este checkout

  switch (evento.type) {
    case "checkout.session.completed":
    case "checkout.session.async_payment_succeeded": // OXXO / transferencia: aquí llega con payment_status "paid"
      await sesionCompletada(s, pedido);
      break;
    case "checkout.session.async_payment_failed":
      if (pedido.payment_status !== "paid") await actualizar(pedido.id, { payment_status: "cancelled", status: "cancelled", notes: "El pago (OXXO/transferencia) no se completó." });
      break;
    case "checkout.session.expired":
      if (pedido.payment_status !== "paid") await actualizar(pedido.id, { payment_status: "cancelled", status: "cancelled", notes: "La sesión de pago expiró sin completarse." });
      break;
  }
  return resultado;
}

const EVENTOS = new Set([
  "checkout.session.completed",
  "checkout.session.async_payment_succeeded",
  "checkout.session.async_payment_failed",
  "checkout.session.expired",
  "charge.refunded",
]);

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Método no permitido", { status: 405 });
  if (!SECRETO) return new Response("Falta STRIPE_WEBHOOK_SECRET", { status: 500 });

  const firma = req.headers.get("stripe-signature");
  if (!firma) return new Response("Falta la firma de Stripe", { status: 400 });
  const cuerpo = await req.text();
  let evento: Stripe.Event;
  try {
    evento = await stripe.webhooks.constructEventAsync(cuerpo, firma, SECRETO, undefined, cripto);
  } catch (e) {
    console.error("firma inválida", e);
    return new Response("Firma inválida", { status: 400 });
  }

  if (!EVENTOS.has(evento.type)) return new Response(JSON.stringify({ recibido: true, ignorado: evento.type }), { status: 200 });

  // Stripe reintenta los webhooks: si ya procesamos este evento, no hacemos nada.
  const { data: repetido } = await admin.from("order_checkout_events").select("id").eq("stripe_event_id", evento.id).maybeSingle();
  if (repetido) return new Response(JSON.stringify({ recibido: true, repetido: true }), { status: 200 });

  try {
    const r = await procesar(evento);
    const { error } = await admin.from("order_checkout_events").insert({
      order_id: r.orderId,
      stripe_checkout_session_id: r.sesionId,
      stripe_event_id: evento.id,
      event_type: evento.type,
      payment_status: r.estadoPago,
      amount_total: r.monto,
      currency: (r.moneda ?? "mxn").toUpperCase(),
      payload: evento as unknown as Record<string, unknown>,
    });
    if (error && error.code !== "23505") console.error("order_checkout_events.insert", error);
  } catch (e) {
    console.error("procesar", evento.type, evento.id, e);
    return new Response("Error al procesar", { status: 500 }); // Stripe lo reintentará
  }
  return new Response(JSON.stringify({ recibido: true }), { status: 200, headers: { "Content-Type": "application/json" } });
});
