-- ============================================================================
-- TarjetasNFC · Checkout con Stripe
-- Ejecutar completo en Supabase → SQL Editor. Es idempotente: se puede correr
-- varias veces sin duplicar datos ni romper tablas existentes.
--
-- Tablas:
--   ecommerce_products         catálogo (1 fila por tarjeta, con su prod_… de Stripe)
--   ecommerce_product_prices   precios por paquete (1, 2, 5, 10) con su price_… de Stripe
--   orders                     pedidos
--   order_items                partidas del pedido (con la configuración capturada)
--   order_item_links           enlaces / datos que el cliente pidió programar en la tarjeta
--   order_checkout_events      bitácora de eventos de Stripe (webhook)
-- Vista:
--   vista_pedidos_tarjetasnfc  pedidos con sus partidas y enlaces, para consultar rápido
--
-- Seguridad: RLS activado sin políticas públicas. Solo las Edge Functions
-- (service_role) leen y escriben; la clave anon del sitio no puede ver pedidos.
-- ============================================================================

create extension if not exists citext;
create extension if not exists pgcrypto;

-- ----------------------------------------------------------------------------
-- Catálogo
-- ----------------------------------------------------------------------------
create table if not exists public.ecommerce_products (
  id uuid not null default gen_random_uuid(),
  constraint ecommerce_products_pkey primary key (id)
);

alter table public.ecommerce_products
  add column if not exists slug text,
  add column if not exists name text,
  add column if not exists platform text,
  add column if not exists category text,
  add column if not exists link_label text,
  add column if not exists stripe_product_id text,
  add column if not exists site text not null default 'tarjetasnfc.com.mx',
  add column if not exists active boolean not null default true,
  add column if not exists metadata jsonb not null default '{}'::jsonb,
  add column if not exists created_at timestamp with time zone not null default now(),
  add column if not exists updated_at timestamp with time zone not null default now();

create unique index if not exists ux_ecommerce_products_slug
  on public.ecommerce_products using btree (slug) where (slug is not null);
create unique index if not exists ux_ecommerce_products_stripe_product_id
  on public.ecommerce_products using btree (stripe_product_id) where (stripe_product_id is not null);

create table if not exists public.ecommerce_product_prices (
  id uuid not null default gen_random_uuid(),
  ecommerce_product_id uuid not null,
  package_cards integer not null,
  unit_amount numeric(12, 2) not null,
  compare_at_amount numeric(12, 2) null,
  currency text not null default 'MXN'::text,
  stripe_price_id text null,
  active boolean not null default true,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint ecommerce_product_prices_pkey primary key (id),
  constraint ecommerce_product_prices_product_fkey foreign key (ecommerce_product_id)
    references public.ecommerce_products (id) on delete cascade,
  constraint ecommerce_product_prices_package_check check (package_cards > 0),
  constraint ecommerce_product_prices_amount_check check (unit_amount >= (0)::numeric),
  constraint ecommerce_product_prices_product_package_key unique (ecommerce_product_id, package_cards)
);

-- Un price_… de Stripe solo puede pertenecer a un paquete (evita cobrar un paquete con el precio de otro).
create unique index if not exists ux_ecommerce_product_prices_stripe_price_id
  on public.ecommerce_product_prices using btree (stripe_price_id) where (stripe_price_id is not null);

-- ----------------------------------------------------------------------------
-- Pedidos
-- ----------------------------------------------------------------------------
create table if not exists public.orders (
  id uuid not null default gen_random_uuid(),
  org_id uuid null,
  user_id uuid null,
  order_number text null,
  customer_name text not null,
  customer_email public.citext null,
  customer_phone text null,
  company_name text null,
  status text not null default 'draft'::text,
  payment_status text not null default 'pending'::text,
  currency text not null default 'MXN'::text,
  subtotal_amount numeric(12, 2) not null default 0,
  tax_amount numeric(12, 2) not null default 0,
  shipping_amount numeric(12, 2) not null default 0,
  total_amount numeric(12, 2) not null default 0,
  notes text null,
  updated_at timestamp with time zone null,
  created_at timestamp with time zone not null default now(),
  stripe_checkout_session_id text null,
  stripe_payment_intent_id text null,
  checkout_client_reference_id text null,
  ecommerce_source text not null default 'web_cart'::text,
  market text null,
  locale text null,
  metadata jsonb not null default '{}'::jsonb,
  constraint orders_pkey primary key (id),
  constraint orders_order_number_key unique (order_number),
  constraint orders_shipping_amount_check check ((shipping_amount >= (0)::numeric)),
  constraint orders_status_check check (
    status = any (array['draft', 'quoted', 'paid', 'in_production', 'shipped', 'completed', 'cancelled']::text[])
  ),
  constraint orders_subtotal_amount_check check ((subtotal_amount >= (0)::numeric)),
  constraint orders_tax_amount_check check ((tax_amount >= (0)::numeric)),
  constraint orders_total_amount_check check ((total_amount >= (0)::numeric)),
  constraint orders_payment_status_check check (
    payment_status = any (array['pending', 'partial', 'paid', 'refunded', 'cancelled']::text[])
  )
);

-- Columnas de e-commerce por si la tabla ya existía con una versión anterior.
alter table public.orders
  add column if not exists stripe_checkout_session_id text null,
  add column if not exists stripe_payment_intent_id text null,
  add column if not exists checkout_client_reference_id text null,
  add column if not exists ecommerce_source text not null default 'web_cart'::text,
  add column if not exists market text null,
  add column if not exists locale text null,
  add column if not exists metadata jsonb not null default '{}'::jsonb;

create index if not exists idx_orders_user_id on public.orders using btree (user_id);
create index if not exists idx_orders_org_id on public.orders using btree (org_id);
create index if not exists idx_orders_status on public.orders using btree (status);
create index if not exists idx_orders_stripe_checkout_session_id on public.orders using btree (stripe_checkout_session_id);
create index if not exists idx_orders_market on public.orders using btree (market);
create index if not exists idx_orders_stripe_payment_intent_id on public.orders using btree (stripe_payment_intent_id);
create index if not exists idx_orders_created_at on public.orders using btree (created_at desc);
create unique index if not exists ux_orders_stripe_checkout_session_id
  on public.orders using btree (stripe_checkout_session_id) where (stripe_checkout_session_id is not null);
create unique index if not exists ux_orders_checkout_client_reference_id
  on public.orders using btree (checkout_client_reference_id) where (checkout_client_reference_id is not null);

create table if not exists public.order_items (
  id uuid not null default gen_random_uuid(),
  order_id uuid not null,
  product_type_id uuid null,
  description text not null,
  quantity integer not null,
  unit_price numeric(12, 2) not null default 0,
  total_price numeric(12, 2) not null default 0,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  ecommerce_product_id uuid null,
  stripe_product_id text null,
  stripe_price_id text null,
  cart_item_id text null,
  configuration jsonb not null default '{}'::jsonb,
  constraint order_items_pkey primary key (id),
  constraint order_items_order_id_fkey foreign key (order_id) references public.orders (id) on delete cascade,
  constraint order_items_ecommerce_product_id_fkey foreign key (ecommerce_product_id)
    references public.ecommerce_products (id) on delete set null,
  constraint order_items_quantity_check check ((quantity > 0)),
  constraint order_items_total_price_check check ((total_price >= (0)::numeric)),
  constraint order_items_unit_price_check check ((unit_price >= (0)::numeric))
);

alter table public.order_items
  add column if not exists ecommerce_product_id uuid null,
  add column if not exists stripe_product_id text null,
  add column if not exists stripe_price_id text null,
  add column if not exists cart_item_id text null,
  add column if not exists configuration jsonb not null default '{}'::jsonb;

create index if not exists idx_order_items_order_id on public.order_items using btree (order_id);
create index if not exists idx_order_items_ecommerce_product_id on public.order_items using btree (ecommerce_product_id);
create index if not exists idx_order_items_cart_item_id on public.order_items using btree (cart_item_id);
create index if not exists idx_order_items_stripe_price_id on public.order_items using btree (stripe_price_id);

-- Enlaces o datos que se programan en cada tarjeta (uno por fila, en el orden que los escribió el cliente).
create table if not exists public.order_item_links (
  id uuid not null default gen_random_uuid(),
  order_id uuid not null,
  order_item_id uuid not null,
  platform text null,
  field_label text null,
  value text not null,
  is_url boolean not null default false,
  position integer not null default 1,
  created_at timestamp with time zone not null default now(),
  constraint order_item_links_pkey primary key (id),
  constraint order_item_links_order_id_fkey foreign key (order_id) references public.orders (id) on delete cascade,
  constraint order_item_links_order_item_id_fkey foreign key (order_item_id) references public.order_items (id) on delete cascade,
  constraint order_item_links_position_check check (position > 0)
);

create index if not exists idx_order_item_links_order_id on public.order_item_links using btree (order_id);
create index if not exists idx_order_item_links_order_item_id on public.order_item_links using btree (order_item_id);

create table if not exists public.order_checkout_events (
  id uuid not null default gen_random_uuid(),
  order_id uuid null,
  stripe_checkout_session_id text null,
  event_type text not null,
  payment_status text null,
  amount_total numeric null,
  currency text null default 'MXN'::text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone not null default now(),
  constraint order_checkout_events_pkey primary key (id),
  constraint order_checkout_events_order_id_fkey foreign key (order_id) references public.orders (id) on delete set null
);

-- Id del evento de Stripe (evt_…) para no procesar dos veces el mismo reintento del webhook.
alter table public.order_checkout_events add column if not exists stripe_event_id text null;

create index if not exists idx_order_checkout_events_order_id on public.order_checkout_events using btree (order_id);
create index if not exists idx_order_checkout_events_session_id on public.order_checkout_events using btree (stripe_checkout_session_id);
create unique index if not exists ux_order_checkout_events_stripe_event_id
  on public.order_checkout_events using btree (stripe_event_id) where (stripe_event_id is not null);

-- Llaves foráneas hacia tablas que pueden existir en tu proyecto (app_users, organizations,
-- product_types). Solo se crean si esas tablas existen, para que el script no falle.
do $$
begin
  if to_regclass('public.app_users') is not null
     and not exists (select 1 from pg_constraint where conname = 'orders_user_id_fkey') then
    alter table public.orders add constraint orders_user_id_fkey
      foreign key (user_id) references public.app_users (id) on delete set null;
  end if;
  if to_regclass('public.organizations') is not null
     and not exists (select 1 from pg_constraint where conname = 'orders_org_id_fkey') then
    alter table public.orders add constraint orders_org_id_fkey
      foreign key (org_id) references public.organizations (id) on delete set null;
  end if;
  if to_regclass('public.product_types') is not null
     and not exists (select 1 from pg_constraint where conname = 'order_items_product_type_id_fkey') then
    alter table public.order_items add constraint order_items_product_type_id_fkey
      foreign key (product_type_id) references public.product_types (id) on delete set null;
  end if;
end $$;

-- updated_at automático en el catálogo
create or replace function public.tnfc_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trg_ecommerce_products_updated_at on public.ecommerce_products;
create trigger trg_ecommerce_products_updated_at before update on public.ecommerce_products
  for each row execute function public.tnfc_set_updated_at();

drop trigger if exists trg_ecommerce_product_prices_updated_at on public.ecommerce_product_prices;
create trigger trg_ecommerce_product_prices_updated_at before update on public.ecommerce_product_prices
  for each row execute function public.tnfc_set_updated_at();

-- ----------------------------------------------------------------------------
-- Seguridad: nadie con la clave anon/authenticated puede leer ni escribir.
-- ----------------------------------------------------------------------------
alter table public.ecommerce_products enable row level security;
alter table public.ecommerce_product_prices enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;
alter table public.order_item_links enable row level security;
alter table public.order_checkout_events enable row level security;

-- ----------------------------------------------------------------------------
-- Vista de consulta (respeta RLS de quien la consulta)
-- ----------------------------------------------------------------------------
create or replace view public.vista_pedidos_tarjetasnfc
with (security_invoker = true) as
select
  o.order_number,
  o.created_at,
  o.status,
  o.payment_status,
  o.customer_name,
  o.customer_email,
  o.customer_phone,
  o.total_amount,
  o.currency,
  o.metadata -> 'shipping_address' as shipping_address,
  i.description,
  i.quantity,
  i.metadata ->> 'package_cards' as package_cards,
  i.configuration ->> 'field_label' as field_label,
  (select string_agg(l.value, ', ' order by l.position)
     from public.order_item_links l where l.order_item_id = i.id) as links,
  o.stripe_checkout_session_id,
  o.stripe_payment_intent_id,
  o.id as order_id,
  i.id as order_item_id
from public.orders o
join public.order_items i on i.order_id = o.id
where o.ecommerce_source = 'web_cart' and o.metadata ->> 'site' = 'tarjetasnfc.com.mx';

revoke all on public.vista_pedidos_tarjetasnfc from anon, authenticated;

-- ----------------------------------------------------------------------------
-- Datos: catálogo y precios de Stripe
-- ----------------------------------------------------------------------------
insert into public.ecommerce_products (slug, name, platform, category, link_label, stripe_product_id) values
  ('tarjeta-nfc-resenas-google',      'Tarjeta NFC para reseñas de Google',      'Google',      'resenas',    'Enlace de reseñas de Google',            'prod_VVxvWEtJRkNxJs'),
  ('tarjeta-nfc-instagram',           'Tarjeta NFC para Instagram',              'Instagram',   'redes',      'Enlace de tu perfil de Instagram',       'prod_VVxybTulUbjN7i'),
  ('tarjeta-nfc-facebook',            'Tarjeta NFC para Facebook',               'Facebook',    'redes',      'Enlace de tu página de Facebook',        'prod_VVxvBcFM88jBTj'),
  ('tarjeta-nfc-tiktok',              'Tarjeta NFC para TikTok',                 'TikTok',      'redes',      'Enlace de tu perfil de TikTok',          'prod_VVy0jmpG12cZaE'),
  ('tarjeta-nfc-whatsapp',            'Tarjeta NFC para WhatsApp',               'WhatsApp',    'redes',      'Número de WhatsApp de tu negocio',       'prod_VVy3Rp0P3DActe'),
  ('tarjeta-nfc-wifi',                'Tarjeta NFC para Wi‑Fi',                  'Wi‑Fi',       'utilidades', 'Nombre de tu red Wi‑Fi (SSID)',          'prod_VVy3OgjqeLpXNe'),
  ('tarjeta-nfc-resenas-tripadvisor', 'Tarjeta NFC para reseñas de TripAdvisor', 'TripAdvisor', 'resenas',    'Enlace de tu negocio en TripAdvisor',    'prod_VVy1ntdFmAGvy4'),
  ('tarjeta-nfc-resenas-airbnb',      'Tarjeta NFC para reseñas de Airbnb',      'Airbnb',      'resenas',    'Enlace de tu anuncio de Airbnb',         'prod_VVxuAXFBOgOWOF'),
  ('tarjeta-nfc-uber-eats',           'Tarjeta NFC para Uber Eats',              'Uber Eats',   'delivery',   'Enlace de tu restaurante en Uber Eats',  'prod_VVy2bHcE8Ivffq'),
  ('tarjeta-nfc-rappi',               'Tarjeta NFC para Rappi',                  'Rappi',       'delivery',   'Enlace de tu tienda en Rappi',           'prod_VVxzI9l5kKQSwq'),
  ('tarjeta-nfc-linkedin',            'Tarjeta NFC para LinkedIn',               'LinkedIn',    'redes',      'Enlace de tu perfil de LinkedIn',        'prod_VVxzXs0c0rPxag'),
  ('tarjeta-nfc-youtube',             'Tarjeta NFC para YouTube',                'YouTube',     'redes',      'Enlace de tu canal de YouTube',          'prod_VVy4i7NwA01WB3'),
  ('tarjeta-nfc-spotify',             'Tarjeta NFC para Spotify',                'Spotify',     'redes',      'Enlace de Spotify',                      'prod_VVy0mITT5PmXT3'),
  ('tarjeta-nfc-twitch',              'Tarjeta NFC para Twitch',                 'Twitch',      'redes',      'Enlace de tu canal de Twitch',           'prod_VVy2KHZ143Nq7O'),
  ('tarjeta-nfc-kick',                'Tarjeta NFC para Kick',                   'Kick',        'redes',      'Enlace de tu canal de Kick',             'prod_VVxyoyFWRi9Bkn')
on conflict (slug) where (slug is not null) do update set
  name = excluded.name,
  platform = excluded.platform,
  category = excluded.category,
  link_label = excluded.link_label,
  stripe_product_id = excluded.stripe_product_id,
  active = true;

with precios (slug, package_cards, unit_amount, compare_at_amount, stripe_price_id) as (values
  ('tarjeta-nfc-resenas-google', 1,  549.00,  899.00, 'price_1UUw009JOXLlO77Y9dydwRq5'),
  ('tarjeta-nfc-resenas-google', 2,  749.00, 1098.00, 'price_1UUwWW9JOXLlO77YwAVOuYjH'),
  ('tarjeta-nfc-resenas-google', 5, 1299.00, 2745.00, 'price_1UUwWW9JOXLlO77Yx9SBDbHd'),
  ('tarjeta-nfc-resenas-google', 10, 1999.00, 5490.00, 'price_1UUwWW9JOXLlO77YW88P5BRB'),

  ('tarjeta-nfc-instagram', 1,  549.00,  899.00, 'price_1UUw2A9JOXLlO77YIhkrgNly'),
  ('tarjeta-nfc-instagram', 2,  749.00, 1098.00, 'price_1UUwXP9JOXLlO77YM4UtHl8A'),
  ('tarjeta-nfc-instagram', 5, 1299.00, 2745.00, 'price_1UUwXP9JOXLlO77YIZW4qrDc'),
  ('tarjeta-nfc-instagram', 10, 1999.00, 5490.00, 'price_1UUwXP9JOXLlO77YpLAhaO0L'),

  ('tarjeta-nfc-facebook', 1,  549.00,  899.00, 'price_1UUvzN9JOXLlO77YV15mSH9n'),
  ('tarjeta-nfc-facebook', 2,  749.00, 1098.00, 'price_1UUwV69JOXLlO77Y29X3qfHI'),
  ('tarjeta-nfc-facebook', 5, 1299.00, 2745.00, 'price_1UUwV69JOXLlO77YDcDNyAUP'),
  ('tarjeta-nfc-facebook', 10, 1999.00, 5490.00, 'price_1UUwV69JOXLlO77Yhix2sJFH'),

  -- TikTok 10 tarjetas: el price_… que llegó es el mismo del paquete de 5
  -- (price_1UUwcz9JOXLlO77YuqdKihbI). Queda en NULL hasta tener el correcto; ver UPDATE al final.
  ('tarjeta-nfc-tiktok', 1,  549.00,  899.00, 'price_1UUw4p9JOXLlO77Y859LTXxZ'),
  ('tarjeta-nfc-tiktok', 2,  749.00, 1098.00, 'price_1UUwcz9JOXLlO77Y6b0oeJwj'),
  ('tarjeta-nfc-tiktok', 5, 1299.00, 2745.00, 'price_1UUwcz9JOXLlO77YuqdKihbI'),
  ('tarjeta-nfc-tiktok', 10, 1999.00, 5490.00, null),

  ('tarjeta-nfc-whatsapp', 1,  549.00,  899.00, 'price_1UUw7I9JOXLlO77YKABIqIiu'),
  ('tarjeta-nfc-whatsapp', 2,  749.00, 1098.00, 'price_1UUwjS9JOXLlO77YjkluOkaF'),
  ('tarjeta-nfc-whatsapp', 5, 1299.00, 2745.00, 'price_1UUwjS9JOXLlO77YEFM9u7FN'),
  ('tarjeta-nfc-whatsapp', 10, 1999.00, 5490.00, 'price_1UUwjS9JOXLlO77YDE1nrI3K'),

  ('tarjeta-nfc-wifi', 1,  549.00,  899.00, 'price_1UUw7m9JOXLlO77YkD0uhPMp'),
  ('tarjeta-nfc-wifi', 2,  749.00, 1098.00, 'price_1UUwkj9JOXLlO77YI3QxStqM'),
  ('tarjeta-nfc-wifi', 5, 1299.00, 2745.00, 'price_1UUwkj9JOXLlO77YFReoSSFX'),
  ('tarjeta-nfc-wifi', 10, 1999.00, 5490.00, 'price_1UUwkj9JOXLlO77YOapQ1Quk'),

  ('tarjeta-nfc-resenas-tripadvisor', 1,  549.00,  899.00, 'price_1UUw5a9JOXLlO77YiW9HkuZW'),
  ('tarjeta-nfc-resenas-tripadvisor', 2,  749.00, 1098.00, 'price_1UUweb9JOXLlO77Y1kNV7Jog'),
  ('tarjeta-nfc-resenas-tripadvisor', 5, 1299.00, 2745.00, 'price_1UUweb9JOXLlO77YWC3WZqgS'),
  ('tarjeta-nfc-resenas-tripadvisor', 10, 1999.00, 5490.00, 'price_1UUweb9JOXLlO77YLkEMp9u8'),

  ('tarjeta-nfc-resenas-airbnb', 1,  549.00,  899.00, 'price_1UUvyd9JOXLlO77YqQ15qkz1'),
  ('tarjeta-nfc-resenas-airbnb', 2,  749.00, 1098.00, 'price_1UUwTA9JOXLlO77YNgr0pCFD'),
  ('tarjeta-nfc-resenas-airbnb', 5, 1299.00, 2745.00, 'price_1UUwTA9JOXLlO77YkWq6ig3v'),
  ('tarjeta-nfc-resenas-airbnb', 10, 1999.00, 5490.00, 'price_1UUwTA9JOXLlO77YvOIJW0Pb'),

  ('tarjeta-nfc-uber-eats', 1,  549.00,  899.00, 'price_1UUw6j9JOXLlO77YOJN7STfO'),
  ('tarjeta-nfc-uber-eats', 2,  749.00, 1098.00, 'price_1UUwhy9JOXLlO77YXD4Mt7i9'),
  ('tarjeta-nfc-uber-eats', 5, 1299.00, 2745.00, 'price_1UUwhy9JOXLlO77YPNusOB3f'),
  ('tarjeta-nfc-uber-eats', 10, 1999.00, 5490.00, 'price_1UUwhy9JOXLlO77Y8PdNjAcn'),

  ('tarjeta-nfc-rappi', 1,  549.00,  899.00, 'price_1UUw3n9JOXLlO77Y8w8icvI8'),
  ('tarjeta-nfc-rappi', 2,  749.00, 1098.00, 'price_1UUwb79JOXLlO77Y51LUTZMc'),
  ('tarjeta-nfc-rappi', 5, 1299.00, 2745.00, 'price_1UUwb79JOXLlO77YrfaWWwX5'),
  ('tarjeta-nfc-rappi', 10, 1999.00, 5490.00, 'price_1UUwb79JOXLlO77Y547dRBX0'),

  ('tarjeta-nfc-linkedin', 1,  549.00,  899.00, 'price_1UUw3A9JOXLlO77YBEef7Sic'),
  ('tarjeta-nfc-linkedin', 2,  749.00, 1098.00, 'price_1UUwZx9JOXLlO77YMvASUyJP'),
  ('tarjeta-nfc-linkedin', 5, 1299.00, 2745.00, 'price_1UUwZx9JOXLlO77YRaXtAORM'),
  ('tarjeta-nfc-linkedin', 10, 1999.00, 5490.00, 'price_1UUwZx9JOXLlO77YAhhWHsOt'),

  ('tarjeta-nfc-youtube', 1,  549.00,  899.00, 'price_1UUw8L9JOXLlO77YMuXzcJRM'),
  ('tarjeta-nfc-youtube', 2,  749.00, 1098.00, 'price_1UUwlT9JOXLlO77Yg6bOh37M'),
  ('tarjeta-nfc-youtube', 5, 1299.00, 2745.00, 'price_1UUwlT9JOXLlO77Y6wGeIzua'),
  ('tarjeta-nfc-youtube', 10, 1999.00, 5490.00, 'price_1UUwlT9JOXLlO77Yl45WGUR4'),

  ('tarjeta-nfc-spotify', 1,  549.00,  899.00, 'price_1UUw4P9JOXLlO77YnEUiHElb'),
  ('tarjeta-nfc-spotify', 2,  749.00, 1098.00, 'price_1UUwc89JOXLlO77YPgUmPghm'),
  ('tarjeta-nfc-spotify', 5, 1299.00, 2745.00, 'price_1UUwc89JOXLlO77YV1SnL2mV'),
  ('tarjeta-nfc-spotify', 10, 1999.00, 5490.00, 'price_1UUwc89JOXLlO77YRdlxbIXp'),

  ('tarjeta-nfc-twitch', 1,  549.00,  899.00, 'price_1UUw6B9JOXLlO77Y4Pb8oJXb'),
  ('tarjeta-nfc-twitch', 2,  749.00, 1098.00, 'price_1UUwhF9JOXLlO77YYYyAc6jK'),
  ('tarjeta-nfc-twitch', 5, 1299.00, 2745.00, 'price_1UUwhF9JOXLlO77YykEekWBP'),
  ('tarjeta-nfc-twitch', 10, 1999.00, 5490.00, 'price_1UUwhF9JOXLlO77YIVnIJxxl'),

  ('tarjeta-nfc-kick', 1,  549.00,  899.00, 'price_1UUw2g9JOXLlO77Y4Qu4x72Q'),
  ('tarjeta-nfc-kick', 2,  749.00, 1098.00, 'price_1UUwYo9JOXLlO77YSO7i0zsL'),
  ('tarjeta-nfc-kick', 5, 1299.00, 2745.00, 'price_1UUwYo9JOXLlO77Yd7HqWIZR'),
  ('tarjeta-nfc-kick', 10, 1999.00, 5490.00, 'price_1UUwYo9JOXLlO77Y8Z8AYwgU')
)
insert into public.ecommerce_product_prices (ecommerce_product_id, package_cards, unit_amount, compare_at_amount, currency, stripe_price_id, active)
select p.id, x.package_cards, x.unit_amount, x.compare_at_amount, 'MXN', x.stripe_price_id, true
from precios x
join public.ecommerce_products p on p.slug = x.slug
on conflict (ecommerce_product_id, package_cards) do update set
  unit_amount = excluded.unit_amount,
  compare_at_amount = excluded.compare_at_amount,
  stripe_price_id = coalesce(excluded.stripe_price_id, public.ecommerce_product_prices.stripe_price_id),
  active = true;

-- Cuando tengas el price_… correcto del paquete de 10 tarjetas de TikTok, ejecuta:
-- update public.ecommerce_product_prices set stripe_price_id = 'price_XXXXXXXX'
-- where package_cards = 10
--   and ecommerce_product_id = (select id from public.ecommerce_products where slug = 'tarjeta-nfc-tiktok');

-- Comprobación: deben salir 15 productos y 60 precios (59 con price_… mientras falte el de TikTok 10).
select count(distinct p.id) as productos, count(pr.id) as precios, count(pr.stripe_price_id) as precios_con_stripe
from public.ecommerce_products p
join public.ecommerce_product_prices pr on pr.ecommerce_product_id = p.id
where p.site = 'tarjetasnfc.com.mx';
