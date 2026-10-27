// Utilidades compartidas por las Edge Functions de TarjetasNFC.
import Stripe from "npm:stripe@17.7.0";
import { createClient } from "npm:@supabase/supabase-js@2.49.4";

export const SITIO = "tarjetasnfc.com.mx";
export const SITE_URL = (Deno.env.get("SITE_URL") ?? "https://www.tarjetasnfc.com.mx").replace(/\/+$/, "");

const ORIGENES = (Deno.env.get("ALLOWED_ORIGINS") ?? "https://www.tarjetasnfc.com.mx,https://tarjetasnfc.com.mx")
  .split(",").map((o) => o.trim()).filter(Boolean);
const ORIGEN_LOCAL = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;

export function origenPermitido(req: Request): boolean {
  const origen = req.headers.get("origin");
  return !origen || ORIGENES.includes(origen) || ORIGEN_LOCAL.test(origen);
}

export function cabecerasCors(req: Request): Record<string, string> {
  const origen = req.headers.get("origin") ?? "";
  const cabeceras: Record<string, string> = {
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
  if (origen && (ORIGENES.includes(origen) || ORIGEN_LOCAL.test(origen))) cabeceras["Access-Control-Allow-Origin"] = origen;
  return cabeceras;
}

export function json(cuerpo: unknown, estado = 200, cabeceras: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(cuerpo), {
    status: estado,
    headers: { ...cabeceras, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function requerida(nombre: string): string {
  const valor = Deno.env.get(nombre);
  if (!valor) throw new Error(`Falta la variable de entorno ${nombre}`);
  return valor;
}

// SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY las inyecta Supabase automáticamente.
export const admin = createClient(requerida("SUPABASE_URL"), requerida("SUPABASE_SERVICE_ROLE_KEY"), {
  auth: { persistSession: false, autoRefreshToken: false },
});

export const stripe = new Stripe(requerida("STRIPE_SECRET_KEY"), {
  httpClient: Stripe.createFetchHttpClient(),
  appInfo: { name: "tarjetasnfc-checkout" },
});

export const centavosAPesos = (c: number | null | undefined) => Math.round(c ?? 0) / 100;
