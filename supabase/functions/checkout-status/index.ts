// Estado del pedido para la página gracias.html.
// GET ?session_id=cs_…  →  { pedido, estado_pago, correo, total, moneda }
// Solo devuelve datos mínimos; el correo va enmascarado.
import { admin, cabecerasCors, centavosAPesos, json, stripe } from "../_shared/comun.ts";

function enmascarar(correo: string | null): string | null {
  if (!correo) return null;
  const [usuario, dominio] = correo.split("@");
  if (!dominio) return null;
  return `${usuario.slice(0, 2)}${"•".repeat(Math.max(1, usuario.length - 2))}@${dominio}`;
}

Deno.serve(async (req) => {
  const cors = cabecerasCors(req);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (req.method !== "GET") return json({ error: "Método no permitido." }, 405, cors);

  const sesionId = new URL(req.url).searchParams.get("session_id") ?? "";
  if (!/^cs_(test|live)_[A-Za-z0-9]{10,200}$/.test(sesionId)) return json({ error: "Sesión no válida." }, 400, cors);

  const { data: pedido, error } = await admin.from("orders")
    .select("order_number, payment_status, status, customer_email, total_amount, currency")
    .eq("stripe_checkout_session_id", sesionId).maybeSingle();
  if (error) { console.error("orders.select", error); return json({ error: "No pudimos consultar tu pedido." }, 500, cors); }
  if (!pedido) return json({ error: "Pedido no encontrado." }, 404, cors);

  let estado = pedido.payment_status;
  let correo = pedido.customer_email as string | null;
  let total = Number(pedido.total_amount);

  // Si el webhook todavía no llega, preguntamos directo a Stripe (solo lectura).
  if (estado === "pending") {
    try {
      const s = await stripe.checkout.sessions.retrieve(sesionId);
      if (s.payment_status === "paid") estado = "paid";
      correo = correo ?? s.customer_details?.email ?? null;
      if (s.amount_total != null) total = centavosAPesos(s.amount_total);
    } catch (e) {
      console.error("checkout.sessions.retrieve", e);
    }
  }

  return json({ pedido: pedido.order_number, estado_pago: estado, correo: enmascarar(correo), total, moneda: pedido.currency }, 200, cors);
});
