#!/usr/bin/env python3
"""Genera el sitio estático de tarjetasnfc.com.mx.

Crea index.html, productos/*.html, js/productos.js, sitemap.xml y robots.txt
a partir de los datos de este archivo. Para cambiar precios, textos o
productos, edita las listas de abajo y vuelve a ejecutar:

    python3 herramientas/generar_sitio.py
"""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import date
from html import escape
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMINIO = "https://www.tarjetasnfc.com.mx"
MARCA = "TarjetasNFC"
WHATSAPP = "526643053834"          # formato wa.me: 52 + 10 dígitos
TELEFONO = "+52 664 305 3834"
TELEFONO_E164 = "+526643053834"
CORREO = "info@taploop.com.mx"
# Supabase (Edge Functions de pago con Stripe). La clave anon es pública por diseño.
SUPABASE_URL = "https://glgvxxbhmbvyqacwkseg.supabase.co"
SUPABASE_ANON = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdsZ3Z4eGJobWJ2eXFhY3drc2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTMwNjQxOTksImV4cCI6MjEwODY0MDE5OX0"
                 ".W59tKIVWTi03peI4bgMxmqsANWk6sgkWxB2F4Q5RiZc")
HOY = date.today().isoformat()
FECHA_MOD = "__FECHA_MOD__"        # se sustituye al escribir por la fecha del último cambio real de la página
ARCHIVO_FECHAS = os.path.join(RAIZ, "herramientas", "fechas.json")
FECHAS = {}                         # ruta -> {"hash", "fecha"}; persistido en herramientas/fechas.json
PUBLICADO = "2026-10-26"           # fecha de publicación del sitio (datos estructurados)
PRECIO_VALIDO = "%d-12-31" % (date.today().year + 1)
ID_ORG = DOMINIO + "/#organizacion"
ID_SITIO = DOMINIO + "/#sitio"

# Menú "Ayuda": cada elemento es una página .html en la raíz
AYUDA = [
    ("como-funciona.html", "Cómo funciona"),
    ("como-encontrar-enlace-resenas-google.html", "Cómo encontrar tu enlace de reseñas de Google"),
    ("como-activar-nfc-celular.html", "Cómo activar el NFC de tu celular"),
    ("envios-y-devoluciones.html", "Envíos y devoluciones"),
    ("contacto.html", "Contacto"),
]

VIDEO_GOOGLE = {
    "src": "videos/tarjeta-nfc-resena-google.mp4", "poster": "videos/tarjeta-nfc-resena-google.jpg",
    "nombre": "Cómo funciona la tarjeta NFC para reseñas de Google",
    "desc": "Video de demostración: acerca la tarjeta NFC TarjetasNFC al celular y se abre al instante la ventana para dejar una reseña de 5 estrellas en Google.",
    "duracion": "PT18S", "ancho": 720, "alto": 1280,
}

# --------------------------------------------------------------------------
# Paquetes y precios (MXN, envío incluido). "antes" es el precio tachado.
# --------------------------------------------------------------------------
PAQUETES = [
    {"tarjetas": 1, "nombre": "1 tarjeta", "precio": 549, "antes": 899, "unidad": 549, "cinta": ""},
    {"tarjetas": 2, "nombre": "2 tarjetas", "precio": 749, "antes": 1098, "unidad": 375, "cinta": ""},
    {"tarjetas": 5, "nombre": "5 tarjetas", "precio": 1299, "antes": 2745, "unidad": 260, "cinta": "🔥 Más popular"},
    {"tarjetas": 10, "nombre": "10 tarjetas", "precio": 1999, "antes": 5490, "unidad": 200, "cinta": "Mejor precio"},
]
for _p in PAQUETES:
    _p["descuentoUnidad"] = round((1 - _p["unidad"] / PAQUETES[0]["precio"]) * 100)
    _p["ahorro"] = round((1 - _p["precio"] / _p["antes"]) * 100)

CATEGORIAS = [
    ("resenas", "Reseñas"),
    ("redes", "Redes sociales"),
    ("delivery", "Delivery"),
    ("streaming", "Música y streaming"),
    ("utilidades", "Utilidades"),
]
NOMBRE_CAT = dict(CATEGORIAS)

# --------------------------------------------------------------------------
# Productos (en el orden en que aparecen en el catálogo)
# --------------------------------------------------------------------------
PRODUCTOS = [
    {
        "img": "google-nfc.png", "slug": "tarjeta-nfc-resenas-google", "plataforma": "Google", "cat": "resenas",
        "nombre": "Tarjeta NFC para reseñas de Google",
        "ayuda_enlace": ("¿Cómo encuentro mi enlace de reseñas?", "https://support.google.com/business/answer/16816815"),
        "video": VIDEO_GOOGLE,
        "desc": "Tarjeta personalizada que abre directamente el enlace de reseñas de tu negocio mediante NFC o código QR.",
        "check": ("Consigue más reseñas en", "segundos"),
        "campo": ('Enlace de reseñas de Google', 'https://g.page/r/…',
                  'Pega el enlace directo para recibir reseñas de tu negocio. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Las reseñas de Google son lo primero que ve un cliente antes de visitarte. Con esta tarjeta tus clientes satisfechos te califican en segundos: acercan su celular, se abre directamente la ventana para dejar estrellas y comentario, y listo. Más reseñas significan mejor posición en Google Maps y más clientes nuevos en tu ciudad.",
        "usos": ["Restaurantes, cafeterías y bares", "Consultorios, clínicas y dentistas", "Estéticas, barberías y spas", "Talleres, tiendas y servicios profesionales"],
    },
    {
        "img": "instagram-nfc.png", "slug": "tarjeta-nfc-instagram", "plataforma": "Instagram", "cat": "redes",
        "nombre": "Tarjeta NFC para Instagram",
        "desc": "Tarjeta personalizada que abre directamente tu perfil de Instagram para que te sigan al instante, mediante NFC o código QR.",
        "check": ("Gana seguidores", "al instante"),
        "campo": ('Enlace de tu perfil de Instagram', 'https://www.instagram.com/tunegocio',
                  'Pega el enlace directo de tu perfil para que te sigan al instante. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Convierte a cada cliente que pasa por tu mostrador en un seguidor. Sin buscar tu nombre ni deletrear tu usuario: un toque con el celular y tu perfil de Instagram se abre listo para seguirte.",
        "usos": ["Tiendas de ropa y boutiques", "Restaurantes y cafeterías", "Creadores de contenido y fotógrafos", "Eventos, expos y ferias"],
    },
    {
        "img": "facebook-nfc.png", "slug": "tarjeta-nfc-facebook", "plataforma": "Facebook", "cat": "redes",
        "nombre": "Tarjeta NFC para Facebook",
        "desc": "Tarjeta personalizada que abre directamente la página de Facebook de tu negocio para ganar seguidores y recomendaciones, mediante NFC o código QR.",
        "check": ("Más seguidores y", "recomendaciones"),
        "campo": ('Enlace de tu página de Facebook', 'https://www.facebook.com/tunegocio',
                  'Pega el enlace directo de tu página para recibir seguidores y recomendaciones. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Facebook sigue siendo la red social más usada en México para encontrar negocios locales. Con esta tarjeta tus clientes llegan a tu página en un toque para darle me gusta, seguirte y dejarte una recomendación.",
        "usos": ["Negocios locales y comercios", "Restaurantes y fondas", "Gimnasios y escuelas", "Servicios a domicilio"],
    },
    {
        "img": "tiktok-nfc.png", "slug": "tarjeta-nfc-tiktok", "plataforma": "TikTok", "cat": "redes",
        "nombre": "Tarjeta NFC para TikTok",
        "desc": "Tarjeta personalizada que abre directamente tu perfil de TikTok para que te sigan al instante, mediante NFC o código QR.",
        "check": ("Crece tu comunidad", "en TikTok"),
        "campo": ('Enlace de tu perfil de TikTok', 'https://www.tiktok.com/@tunegocio',
                  'Pega el enlace directo de tu perfil para que te sigan al instante. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Si tu negocio crece con videos, haz que tus clientes te encuentren sin escribir nada. Un toque y se abre tu perfil de TikTok listo para seguirte y ver tu contenido.",
        "usos": ["Creadores de contenido", "Tiendas y marcas emergentes", "Restaurantes y food trucks", "Eventos y activaciones"],
    },
    {
        "img": "whatsapp-nfc.png", "slug": "tarjeta-nfc-whatsapp", "plataforma": "WhatsApp", "cat": "utilidades",
        "nombre": "Tarjeta NFC para WhatsApp",
        "desc": "Tarjeta personalizada que abre directamente un chat de WhatsApp con tu negocio, sin necesidad de guardar el número, mediante NFC o código QR.",
        "check": ("Chats sin guardar", "tu número"),
        "campo": ('Número de WhatsApp de tu negocio', '10 dígitos, ej. 55 1234 5678',
                  'Escribe el número de WhatsApp de tu negocio a 10 dígitos. Si tienes más de un número, sepáralos con coma (,).'),
        "detalle": "Facilita que tus clientes te escriban para pedir, cotizar o agendar. La tarjeta abre un chat de WhatsApp con tu negocio al instante, sin guardar contactos ni copiar números.",
        "usos": ["Ventas y cotizaciones", "Citas en consultorios y estéticas", "Pedidos en restaurantes", "Atención a clientes"],
    },
    {
        "img": "wifi-nfc.png", "slug": "tarjeta-nfc-wifi", "plataforma": "Wi‑Fi", "cat": "utilidades",
        "nombre": "Tarjeta NFC para Wi‑Fi",
        "desc": "Tarjeta personalizada que conecta a tus clientes a tu red Wi‑Fi sin escribir la contraseña, mediante NFC o código QR.",
        "check": ("Conexión sin escribir", "contraseñas"),
        "campo": ('Nombre de tu red Wi‑Fi (SSID)', 'Ej. CafeLaEsquina_WiFi',
                  'Escribe el nombre exacto de tu red; te pediremos la contraseña por WhatsApp de forma privada. Si tienes más de una red, sepáralas con coma (,).'),
        "detalle": "Olvídate de dictar contraseñas largas o pegar papelitos en la pared. Tus clientes se conectan a tu Wi‑Fi con un toque o escaneando el código QR.",
        "usos": ["Cafeterías y restaurantes", "Hoteles y rentas vacacionales", "Oficinas y coworkings", "Salas de espera"],
    },
    {
        "img": "tripadvisor-nfc.png", "slug": "tarjeta-nfc-resenas-tripadvisor", "plataforma": "TripAdvisor", "cat": "resenas",
        "nombre": "Tarjeta NFC para reseñas de TripAdvisor",
        "desc": "Tarjeta personalizada que abre directamente el enlace de reseñas de tu negocio en TripAdvisor, mediante NFC o código QR.",
        "check": ("Más opiniones de", "viajeros"),
        "campo": ('Enlace de tu negocio en TripAdvisor', 'https://www.tripadvisor.com.mx/…',
                  'Pega el enlace directo para recibir reseñas de tu negocio en TripAdvisor. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Los turistas eligen dónde comer, dormir y qué tour tomar según TripAdvisor. Pide la opinión justo al final de la experiencia, cuando el cliente está más contento, y súbete en el ranking de tu destino.",
        "usos": ["Hoteles y hostales", "Restaurantes en zonas turísticas", "Tours y agencias de viaje", "Parques y atracciones"],
    },
    {
        "img": "airbnb-nfc.png", "slug": "tarjeta-nfc-resenas-airbnb", "plataforma": "Airbnb", "cat": "resenas",
        "nombre": "Tarjeta NFC para reseñas de Airbnb",
        "desc": "Tarjeta personalizada que abre directamente tu anuncio de Airbnb para que tus huéspedes te califiquen, mediante NFC o código QR.",
        "check": ("Mejores calificaciones de", "huéspedes"),
        "campo": ('Enlace de tu anuncio de Airbnb', 'https://www.airbnb.mx/rooms/…',
                  'Pega el enlace directo de tu anuncio para recibir reseñas de tus huéspedes. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Las calificaciones determinan cuántas reservas recibes. Deja la tarjeta en tu propiedad y recuerda a tus huéspedes calificar su estancia con un solo toque.",
        "usos": ["Anfitriones de Airbnb", "Departamentos y casas vacacionales", "Administradores de propiedades", "Lofts y cabañas"],
    },
    {
        "img": "ubereats-nfc.png", "slug": "tarjeta-nfc-uber-eats", "plataforma": "Uber Eats", "cat": "delivery",
        "nombre": "Tarjeta NFC para Uber Eats",
        "desc": "Tarjeta personalizada que abre directamente tu restaurante en Uber Eats para que tus clientes pidan a domicilio, mediante NFC o código QR.",
        "check": ("Más pedidos", "a domicilio"),
        "campo": ('Enlace de tu restaurante en Uber Eats', 'https://www.ubereats.com/mx/store/…',
                  'Pega el enlace directo de tu restaurante para recibir pedidos a domicilio. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Haz que quien ya te visitó vuelva a pedirte desde casa. La tarjeta abre tu restaurante en Uber Eats para ordenar en segundos.",
        "usos": ["Restaurantes y dark kitchens", "Cafeterías y panaderías", "Taquerías y antojerías", "Bolsas y empaques de entrega"],
    },
    {
        "img": "rappi-nfc.png", "slug": "tarjeta-nfc-rappi", "plataforma": "Rappi", "cat": "delivery",
        "nombre": "Tarjeta NFC para Rappi",
        "desc": "Tarjeta personalizada que abre directamente tu tienda o restaurante en Rappi para que tus clientes pidan a domicilio, mediante NFC o código QR.",
        "check": ("Clientes que vuelven a", "pedir"),
        "campo": ('Enlace de tu tienda en Rappi', 'https://www.rappi.com.mx/…',
                  'Pega el enlace directo de tu tienda o restaurante para recibir pedidos a domicilio. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Convierte tus visitas en pedidos recurrentes. Con un toque tus clientes llegan a tu tienda o restaurante en Rappi para ordenar sin buscarte.",
        "usos": ["Restaurantes", "Farmacias y tiendas de conveniencia", "Florerías y regalos", "Supermercados de barrio"],
    },
    {
        "img": "linkedin-nfc.png", "slug": "tarjeta-nfc-linkedin", "plataforma": "LinkedIn", "cat": "redes",
        "nombre": "Tarjeta NFC para LinkedIn",
        "desc": "Tarjeta personalizada que abre directamente tu perfil profesional de LinkedIn para conectar al instante, mediante NFC o código QR.",
        "check": ("Networking", "en un toque"),
        "campo": ('Enlace de tu perfil de LinkedIn', 'https://www.linkedin.com/in/tunombre',
                  'Pega el enlace directo de tu perfil personal o de empresa para conectar al instante. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "La tarjeta de presentación moderna. En juntas, congresos o entrevistas comparte tu perfil de LinkedIn con un toque y nunca más pierdas un contacto.",
        "usos": ["Profesionistas y freelancers", "Equipos de ventas", "Reclutadores", "Congresos y eventos de networking"],
    },
    {
        "img": "youtube-nfc.png", "slug": "tarjeta-nfc-youtube", "plataforma": "YouTube", "cat": "redes",
        "nombre": "Tarjeta NFC para YouTube",
        "desc": "Tarjeta personalizada que abre directamente tu canal de YouTube para que se suscriban al instante, mediante NFC o código QR.",
        "check": ("Más suscriptores", "al instante"),
        "campo": ('Enlace de tu canal de YouTube', 'https://www.youtube.com/@tucanal',
                  'Pega el enlace directo de tu canal para que se suscriban al instante. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Lleva a tu audiencia directo a tu canal. Ideal para creadores, escuelas y negocios que comparten tutoriales: un toque y te pueden suscribir.",
        "usos": ["Creadores de contenido", "Escuelas y academias", "Iglesias y comunidades", "Marcas con tutoriales"],
    },
    {
        "img": "spotify-nfc.png", "slug": "tarjeta-nfc-spotify", "plataforma": "Spotify", "cat": "streaming",
        "nombre": "Tarjeta NFC para Spotify",
        "desc": "Tarjeta personalizada que abre directamente tu perfil, canción, playlist o podcast en Spotify, mediante NFC o código QR.",
        "check": ("Comparte tu música", "o podcast"),
        "campo": ('Enlace de Spotify', 'https://open.spotify.com/…',
                  'Pega el enlace directo de tu perfil, canción, playlist o podcast. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Que tu música suene en más celulares. Comparte tu perfil de artista, tu nuevo sencillo, la playlist de tu negocio o tu podcast con un solo toque.",
        "usos": ["Músicos, bandas y DJs", "Podcasters", "Bares y cafeterías con playlist propia", "Regalos y bodas"],
    },
    {
        "img": "twitch-nfc.png", "slug": "tarjeta-nfc-twitch", "plataforma": "Twitch", "cat": "streaming",
        "nombre": "Tarjeta NFC para Twitch",
        "desc": "Tarjeta personalizada que abre directamente tu canal de Twitch para que nuevos espectadores sigan tus streams, mediante NFC o código QR.",
        "check": ("Nuevos espectadores para", "tus streams"),
        "campo": ('Enlace de tu canal de Twitch', 'https://www.twitch.tv/tucanal',
                  'Pega el enlace directo de tu canal para que nuevos espectadores te sigan. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Haz crecer tu comunidad fuera de línea. En torneos, convenciones y eventos gamer, comparte tu canal de Twitch con un toque.",
        "usos": ["Streamers", "Equipos de esports", "Convenciones y torneos", "Tiendas y cafés gamer"],
    },
    {
        "img": "kick-nfc.png", "slug": "tarjeta-nfc-kick", "plataforma": "Kick", "cat": "streaming",
        "nombre": "Tarjeta NFC para Kick",
        "desc": "Tarjeta personalizada que abre directamente tu canal de Kick para que nuevos espectadores sigan tus streams, mediante NFC o código QR.",
        "check": ("Nuevos espectadores para", "tus streams"),
        "campo": ('Enlace de tu canal de Kick', 'https://kick.com/tucanal',
                  'Pega el enlace directo de tu canal para que nuevos espectadores te sigan. Si tienes más de un enlace, sepáralos con coma (,).'),
        "detalle": "Lleva a nuevos seguidores directo a tu canal de Kick. Perfecta para repartir en eventos, meetups y colaboraciones.",
        "usos": ["Streamers", "Creadores de contenido en vivo", "Eventos y meetups", "Equipos y comunidades gamer"],
    },
]

# --------------------------------------------------------------------------
# Calificaciones REALES de clientes: slug -> (promedio de 1 a 5, número de reseñas).
# Un producto sin entrada no muestra estrellas. Ejemplo:
#   "tarjeta-nfc-resenas-google": (4.9, 37),
# Usa solo datos verificables (p. ej. reseñas recibidas tras la compra); se
# publican también como datos estructurados para Google.
# --------------------------------------------------------------------------
CALIFICACIONES = {
    "tarjeta-nfc-resenas-google": (4.9, 1152),
    "tarjeta-nfc-instagram": (5.0, 955),
    "tarjeta-nfc-facebook": (5.0, 977),
    "tarjeta-nfc-tiktok": (4.9, 584),
    "tarjeta-nfc-whatsapp": (4.9, 1089),
    "tarjeta-nfc-wifi": (4.8, 396),
    "tarjeta-nfc-resenas-tripadvisor": (5.0, 317),
    "tarjeta-nfc-resenas-airbnb": (5.0, 391),
    "tarjeta-nfc-uber-eats": (4.9, 771),
    "tarjeta-nfc-rappi": (4.9, 282),
    "tarjeta-nfc-linkedin": (5.0, 429),
    "tarjeta-nfc-youtube": (5.0, 271),
    "tarjeta-nfc-spotify": (5.0, 173),
    "tarjeta-nfc-twitch": (5.0, 81),
    "tarjeta-nfc-kick": (5.0, 59),
}

for i, p in enumerate(PRODUCTOS):
    p["orden"] = i
    p["url"] = "productos/%s.html" % p["slug"]
    p["imagen"] = "imagenes/productos/" + p["img"]

# --------------------------------------------------------------------------
# Iconos SVG
# --------------------------------------------------------------------------
def icono(nombre, t=24, extra=""):
    trazos = {
        "buscar": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
        "carrito": '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h3l2.6 12.2a1 1 0 0 0 1 .8h9.8a1 1 0 0 0 1-.8L21 7H6"/>',
        "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
        "cerrar": '<path d="M18 6 6 18M6 6l12 12"/>',
        "abajo": '<path d="m6 9 6 6 6-6"/>',
        "arriba": '<path d="m18 15-6-6-6 6"/>',
        "izq": '<path d="M19 12H5M12 19l-7-7 7-7"/>',
        "der": '<path d="M5 12h14M12 5l7 7-7 7"/>',
        "expandir": '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
        "mas": '<path d="M12 5v14M5 12h14"/>',
        "camion": '<path d="M1 4h14v12H1zM15 9h4l3 3v4h-7"/><circle cx="6" cy="18.5" r="2"/><circle cx="18" cy="18.5" r="2"/>',
        "escudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
        "rayo": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
        "tag": '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7" cy="7" r="1.5"/>',
        "nfc": '<path d="M8.5 8.5a5 5 0 0 1 0 7M12 6a8.5 8.5 0 0 1 0 12M15.5 3.5a12 12 0 0 1 0 17"/><circle cx="5" cy="12" r="1.5"/>',
        "qr": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v.01M14 20h.01M17 20h4v-3"/>',
        "celular": '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/>',
        "estrella": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
        "caja": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
        "pincel": '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
        "infinito": '<path d="M18.2 8.4a4.2 4.2 0 1 1 0 7.2L12 12l-6.2-3.6a4.2 4.2 0 1 0 0 7.2L12 12z"/>',
        "mexico": '<path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
        "mensaje": '<path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.6-5.2A8.5 8.5 0 1 1 21 12z"/>',
        "telefono": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
        "correo": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
        "play": '<path d="M7 4v16l13-8z" fill="currentColor"/>',
        "usuarios": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
        "ayuda": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
        "candado": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "exito": '<circle cx="12" cy="12" r="10"/><path d="m7.5 12.5 3 3 6-7"/>',
    }
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>'
            % (t, t, extra, trazos[nombre]))


def check(t=22):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="currentColor"/>'
            '<path d="m7 12.5 3.2 3.2L17 9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>' % (t, t))


WA_SVG = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm8.4-18.2A11.8 11.8 0 0 0 1.7 17.8L0 24l6.3-1.7A11.8 11.8 0 0 0 24 12c0-3.2-1.2-6.2-3.6-8.4z"/></svg>')


def webp(p, ancho):
    return "imagenes/productos/webp/%s-%d.webp" % (p["img"][:-4], ancho)


def srcset(base, p, anchos=(400, 800, 1200)):
    return ", ".join("%s%s %dw" % (base, webp(p, a), a) for a in anchos)


def generar_webp():
    """Crea las versiones WebP (400/800/1200 px) que falten. Requiere cwebp."""
    if not shutil.which("cwebp"):
        return
    for p in PRODUCTOS:
        for a in (400, 800, 1200):
            destino = os.path.join(RAIZ, webp(p, a))
            if not os.path.exists(destino):
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                subprocess.run(["cwebp", "-quiet", "-q", "82", "-resize", str(a), "0", os.path.join(RAIZ, p["imagen"]), "-o", destino], check=True)


def dinero(n):
    return "${:,} MXN".format(n)


# --------------------------------------------------------------------------
# Fragmentos comunes
# --------------------------------------------------------------------------
def head(base, titulo, descripcion, ruta, imagen, grafo, tipo_og="website", keywords=(), img_dim=(2000, 2000),
         img_alt="", extra_meta="", preload="", indexar=True):
    """<head> completo: SEO, Open Graph, Twitter y un único JSON-LD con @graph."""
    canonical = DOMINIO + "/" + ruta
    ld = json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, separators=(",", ":"))
    img_alt = img_alt or titulo
    kw = '<meta name="keywords" content="%s">\n' % escape(", ".join(keywords)) if keywords else ""
    robots = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" if indexar else "noindex, nofollow"
    return f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
{kw}<meta name="author" content="{MARCA}">
<meta name="robots" content="{robots}">
<meta name="googlebot" content="{robots}">
<meta name="bingbot" content="{"index, follow" if indexar else "noindex, nofollow"}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es-MX" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta name="theme-color" content="#1d5ff0">
<meta name="geo.region" content="MX">
<meta name="geo.placename" content="México">
<meta name="language" content="es-MX">
<meta name="application-name" content="{MARCA}">
<meta name="apple-mobile-web-app-title" content="{MARCA}">
<meta name="msapplication-TileColor" content="#1d5ff0">
<meta name="format-detection" content="telephone=no">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:type" content="{tipo_og}">
<meta property="og:locale" content="es_MX">
<meta property="og:site_name" content="{MARCA}">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:url" content="{canonical}">
<meta property="og:updated_time" content="{FECHA_MOD}T00:00:00-06:00">
<meta property="og:image" content="{DOMINIO}/{imagen}">
<meta property="og:image:secure_url" content="{DOMINIO}/{imagen}">
<meta property="og:image:width" content="{img_dim[0]}">
<meta property="og:image:height" content="{img_dim[1]}">
<meta property="og:image:alt" content="{escape(img_alt)}">
{extra_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(titulo)}">
<meta name="twitter:description" content="{escape(descripcion)}">
<meta name="twitter:image" content="{DOMINIO}/{imagen}">
<meta name="twitter:image:alt" content="{escape(img_alt)}">
<link rel="icon" type="image/png" href="{base}imagenes/favicon.png">
<link rel="icon" type="image/png" sizes="192x192" href="{base}imagenes/favicon-192.png">
<link rel="apple-touch-icon" href="{base}imagenes/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
<link rel="sitemap" type="application/xml" href="{DOMINIO}/sitemap.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}css/estilos.css">
{preload}<script type="application/ld+json">{ld}</script>
</head>"""


# --------------------------------------------------------------------------
# Datos estructurados (schema.org)
# --------------------------------------------------------------------------
def nodo_org():
    return {
        "@type": "Organization", "@id": ID_ORG, "name": MARCA, "alternateName": ["Tarjetas NFC México", "tarjetasnfc.com.mx"],
        "url": DOMINIO + "/",
        "logo": {"@type": "ImageObject", "@id": DOMINIO + "/#logo", "url": DOMINIO + "/imagenes/logo.png", "width": 1254, "height": 1254, "caption": MARCA},
        "image": {"@id": DOMINIO + "/#logo"},
        "description": "Tarjetas NFC con código QR para conseguir reseñas en Google, seguidores en redes sociales y pedidos a domicilio. Envío gratis a todo México.",
        "email": CORREO, "telephone": TELEFONO_E164,
        "address": {"@type": "PostalAddress", "addressCountry": "MX"},
        "slogan": "Nuevas reseñas a un solo toque",
        "hasOfferCatalog": {"@id": DOMINIO + "/#paquetes"},
        "areaServed": {"@type": "Country", "name": "México", "identifier": "MX"},
        "knowsLanguage": "es-MX",
        "knowsAbout": ["Tarjetas NFC", "Reseñas de Google", "Código QR", "Marketing para negocios locales", "Reputación en línea"],
        "contactPoint": [
            {"@type": "ContactPoint", "contactType": "customer service", "telephone": TELEFONO_E164, "email": CORREO, "areaServed": "MX", "availableLanguage": ["Spanish"]},
            {"@type": "ContactPoint", "contactType": "sales", "telephone": TELEFONO_E164, "email": CORREO, "areaServed": "MX", "availableLanguage": ["Spanish"]},
        ],
    }


def nodo_sitio():
    return {"@type": "WebSite", "@id": ID_SITIO, "url": DOMINIO + "/", "name": MARCA, "alternateName": "Tarjetas NFC México",
            "description": "Tienda en línea de tarjetas NFC para reseñas y redes sociales en México.", "inLanguage": "es-MX",
            "publisher": {"@id": ID_ORG}, "copyrightHolder": {"@id": ID_ORG}, "copyrightYear": date.today().year,
            "potentialAction": {"@type": "SearchAction",
                                "target": {"@type": "EntryPoint", "urlTemplate": DOMINIO + "/?q={search_term_string}"},
                                "query-input": "required name=search_term_string"}}


def nodos_pagina(ruta, nombre, descripcion, migas, tipo="WebPage", imagen=None, extra=None, keywords=(), relacionados=()):
    """WebPage + BreadcrumbList. migas: [(nombre, ruta_o_None), ...] sin incluir la página actual."""
    url = DOMINIO + "/" + ruta
    pagina = {"@type": tipo, "@id": url + "#webpage", "url": url, "name": nombre, "description": descripcion,
              "inLanguage": "es-MX", "isPartOf": {"@id": ID_SITIO}, "about": {"@id": ID_ORG}, "publisher": {"@id": ID_ORG},
              "datePublished": PUBLICADO, "dateModified": FECHA_MOD, "lastReviewed": FECHA_MOD, "reviewedBy": {"@id": ID_ORG},
              "breadcrumb": {"@id": url + "#migas"}, "potentialAction": [{"@type": "ReadAction", "target": [url]}],
              "audience": {"@type": "BusinessAudience", "audienceType": "Negocios en México", "geographicArea": {"@type": "Country", "name": "México"}},
              "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["h1", "main p"]}}
    if keywords:
        pagina["keywords"] = ", ".join(keywords)
    if relacionados:
        pagina["relatedLink"] = [DOMINIO + "/" + x for x in relacionados]
        pagina["significantLink"] = [DOMINIO + "/" + x for x in relacionados]
    if imagen:
        pagina["primaryImageOfPage"] = {"@type": "ImageObject", "@id": url + "#imagen", "url": DOMINIO + "/" + imagen,
                                        "contentUrl": DOMINIO + "/" + imagen, "inLanguage": "es-MX", "caption": nombre}
        pagina["image"] = {"@id": url + "#imagen"}
    if extra:
        pagina.update(extra)
    elementos = [{"@type": "ListItem", "position": i + 1, "name": n, "item": DOMINIO + "/" + (r or "")} for i, (n, r) in enumerate(migas)]
    elementos.append({"@type": "ListItem", "position": len(elementos) + 1, "name": nombre, "item": url})
    return [pagina, {"@type": "BreadcrumbList", "@id": url + "#migas", "itemListElement": elementos}]


def nodo_faq(ruta, preguntas):
    return {"@type": "FAQPage", "@id": DOMINIO + "/" + ruta + "#faq", "inLanguage": "es-MX",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in preguntas]}


def nodo_howto(ruta, ident, nombre, descripcion, pasos, tiempo=None, imagen=None):
    nodo = {"@type": "HowTo", "@id": DOMINIO + "/" + ruta + "#" + ident, "name": nombre, "description": descripcion, "inLanguage": "es-MX",
            "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d, "url": DOMINIO + "/" + ruta + "#" + ident + "-" + str(i + 1)}
                     for i, (t, d) in enumerate(pasos)]}
    if tiempo:
        nodo["totalTime"] = tiempo
    if imagen:
        nodo["image"] = DOMINIO + "/" + imagen
    return nodo


def nodo_video(ruta, v):
    return {"@type": "VideoObject", "@id": DOMINIO + "/" + ruta + "#video", "name": v["nombre"], "description": v["desc"],
            "thumbnailUrl": [DOMINIO + "/" + v["poster"]], "uploadDate": PUBLICADO + "T12:00:00-06:00", "duration": v["duracion"],
            "contentUrl": DOMINIO + "/" + v["src"], "inLanguage": "es-MX", "width": v["ancho"], "height": v["alto"],
            "publisher": {"@id": ID_ORG}}


def envio_schema():
    return {"@type": "OfferShippingDetails",
            "shippingRate": {"@type": "MonetaryAmount", "value": 0, "currency": "MXN"},
            "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "MX"},
            "deliveryTime": {"@type": "ShippingDeliveryTime",
                             "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 2, "unitCode": "DAY"},
                             "transitTime": {"@type": "QuantitativeValue", "minValue": 3, "maxValue": 5, "unitCode": "DAY"},
                             "cutoffTime": "11:00:00-06:00",
                             "businessDays": {"@type": "OpeningHoursSpecification",
                                              "dayOfWeek": ["https://schema.org/" + d for d in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")]}}}


def devolucion_schema():
    return {"@type": "MerchantReturnPolicy", "applicableCountry": "MX",
            "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted",
            "merchantReturnLink": DOMINIO + "/envios-y-devoluciones.html"}


def palabras_clave_producto(p):
    pl = p["plataforma"].lower()
    kw = ["tarjeta nfc " + pl, "tarjeta nfc para " + pl, "tarjeta " + pl + " nfc", "tarjeta nfc " + pl + " méxico",
          "tarjeta qr " + pl, "tarjeta nfc y qr " + pl, "comprar tarjeta nfc " + pl, "tarjeta nfc " + pl + " precio",
          "tarjeta inteligente " + pl, "tarjeta contactless " + pl, "tarjeta nfc " + pl + " cdmx",
          "tarjeta nfc " + pl + " guadalajara", "tarjeta nfc " + pl + " monterrey", "tarjeta nfc " + pl + " tijuana"]
    extra = {
        "resenas": ["tarjeta reseñas " + pl, "tarjeta para reseñas de " + pl, "más reseñas en " + pl, "cómo conseguir reseñas en " + pl,
                    "tarjeta de calificaciones " + pl, "reseñas 5 estrellas " + pl],
        "redes": ["tarjeta para seguir en " + pl, "ganar seguidores en " + pl, "tarjeta perfil " + pl, "tarjeta redes sociales nfc"],
        "delivery": ["tarjeta " + pl + " restaurante", "más pedidos en " + pl, "tarjeta nfc para restaurantes", "tarjeta delivery nfc"],
        "streaming": ["tarjeta " + pl + " streamer", "tarjeta nfc para creadores de contenido", "tarjeta canal " + pl],
        "utilidades": ["tarjeta nfc " + pl + " para negocio", "tarjeta nfc para negocios", "tarjeta " + pl + " sin contraseña" if p["cat"] == "utilidades" and pl.startswith("wi") else "tarjeta " + pl + " sin guardar número"],
    }[p["cat"]]
    return kw + extra + ["tarjetas nfc méxico", "tarjeta nfc personalizada", "tarjeta nfc con código qr", "tarjetas nfc para negocios", "envío gratis méxico"]


def mega_menu(base):
    cols = []
    for clave, nombre in CATEGORIAS:
        enlaces = "".join('<a href="%s%s">%s</a>' % (base, p["url"], escape(p["plataforma"])) for p in PRODUCTOS if p["cat"] == clave)
        cols.append('<div><h3>%s</h3>%s</div>' % (nombre, enlaces))
    return "".join(cols)


def header(base, actual=""):
    idx = base + "index.html"
    cats_movil = "".join(
        '<details><summary>%s %s</summary><div>%s</div></details>' % (
            nombre, icono("abajo", 18),
            "".join('<a href="%s%s">%s</a>' % (base, p["url"], escape(p["nombre"])) for p in PRODUCTOS if p["cat"] == clave))
        for clave, nombre in CATEGORIAS)
    ayuda_enlaces = "".join('<a href="%s%s">%s</a>' % (base, a, t) for a, t in AYUDA)
    nav_cats = "".join(
        '<li class="nav__item"><a class="nav__enlace" href="%s?categoria=%s#catalogo">%s</a></li>' % (idx, clave, nombre)
        for clave, nombre in CATEGORIAS[:3])
    return f"""
<a class="solo-lectores" href="#contenido">Saltar al contenido</a>
<div class="barra-anuncio">🇲🇽 ENVÍO GRATIS A TODO MÉXICO · AHORRA HASTA 64% EN PAQUETES</div>
<div class="barra-superior">
  <div class="contenedor">
    <nav aria-label="Enlaces rápidos">
      <a href="{base}como-funciona.html">Cómo funciona</a>
      <a href="{base}envios-y-devoluciones.html">Envíos</a>
      <a href="{base}contacto.html">Contacto</a>
      <a href="tel:{TELEFONO_E164}">{TELEFONO}</a>
    </nav>
    <div class="barra-superior__der">
      <span>{icono("camion", 18)} Envío gratis a toda la República</span>
      <span>🇲🇽 México (MXN $)</span>
    </div>
  </div>
</div>
<header class="header">
  <div class="contenedor">
    <div class="header__fila">
      <button class="icono-btn btn-menu" type="button" data-abrir="menu-movil" aria-label="Abrir menú">{icono("menu")}</button>
      <a class="marca" href="{idx}" aria-label="{MARCA} – inicio"><img src="{base}imagenes/productos/tarjetasnfc-logo.webp" alt="TarjetasNFC México" width="1000" height="200"></a>
      <div class="header__acciones">
        <a class="icono-btn" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">{icono("mensaje")}</a>
        <button class="icono-btn" type="button" data-buscar aria-label="Buscar productos">{icono("buscar")}</button>
        <button class="icono-btn" type="button" data-abrir="carrito" aria-label="Abrir carrito">{icono("carrito")}<span class="contador-carrito">0</span></button>
      </div>
    </div>
    <nav class="nav" aria-label="Principal">
      <ul class="nav__lista">
        <li class="nav__item">
          <a class="nav__enlace" href="{idx}#catalogo"{' aria-current="page"' if actual == "tienda" else ""}>Tienda {icono("abajo", 16)}</a>
          <div class="mega">{mega_menu(base)}</div>
        </li>
        {nav_cats}
        <li class="nav__item"><a class="nav__enlace" href="{idx}#precios">Paquetes <span class="insignia insignia--nuevo">Ahorra</span></a></li>
        <li class="nav__item">
          <a class="nav__enlace" href="{base}como-funciona.html"{' aria-current="page"' if actual == "ayuda" else ""}>Ayuda {icono("abajo", 16)}</a>
          <div class="mega mega--lista">{ayuda_enlaces}</div>
        </li>
        <li class="nav__item"><a class="nav__enlace" href="https://wa.me/{WHATSAPP}?text={quote('Hola, me interesa un pedido de mayoreo de tarjetas NFC')}" target="_blank" rel="noopener">Mayoreo</a></li>
      </ul>
    </nav>
  </div>
</header>
<div class="marquesina" aria-hidden="true">
  <div class="marquesina__pista">{marquesina_lista()}{marquesina_lista()}</div>
</div>
<div class="drawer-fondo" id="drawer-fondo"></div>
<aside class="drawer drawer--izq" id="menu-movil" aria-hidden="true" aria-label="Menú">
  <div class="drawer__cabecera">
    <img src="{base}imagenes/productos/tarjetasnfc-logo.webp" alt="TarjetasNFC" width="1000" height="200" style="height:32px;width:auto">
    <button class="icono-btn" type="button" data-cerrar aria-label="Cerrar menú">{icono("cerrar")}</button>
  </div>
  <div class="drawer__cuerpo menu-movil">
    <a href="{idx}#catalogo">Todas las tarjetas</a>
    {cats_movil}
    <a href="{idx}#precios">Paquetes y precios</a>
    <details><summary>Ayuda {icono("abajo", 18)}</summary><div>{ayuda_enlaces}</div></details>
    <a href="{idx}#preguntas">Preguntas frecuentes</a>
    <a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">Contacto por WhatsApp</a>
  </div>
</aside>
<div class="buscador" id="buscador" aria-hidden="true" role="dialog" aria-label="Buscar productos">
  <div class="contenedor">
    <div class="buscador__fila">
      <input class="input" id="buscador-input" type="search" placeholder="Buscar: Google, Instagram, Wi‑Fi…" autocomplete="off" aria-label="Buscar productos">
      <button class="icono-btn" type="button" data-cerrar aria-label="Cerrar búsqueda">{icono("cerrar")}</button>
    </div>
    <div class="buscador__resultados" id="buscador-resultados"></div>
  </div>
</div>"""


def marquesina_lista():
    textos = ["Envío gratis a todo México", "Configuramos tu tarjeta antes de enviarla", "Funciona con NFC y código QR",
              "Pago único, sin mensualidades", "Compatible con iPhone y Android", "Tarjetas para Google, Instagram, WhatsApp y más"]
    return "<ul>" + "".join("<li>%s</li>" % t for t in textos) + "</ul>"


def pie(base):
    idx = base + "index.html"
    populares = "".join('<li><a href="%s%s">%s</a></li>' % (base, p["url"], escape(p["nombre"])) for p in PRODUCTOS[:6])
    cats = "".join('<li><a href="%s?categoria=%s#catalogo">%s</a></li>' % (idx, c, n) for c, n in CATEGORIAS)
    return f"""
<footer class="pie">
  <section class="cta">
    <div class="contenedor">
      <span class="etiqueta-seccion">Negocios de todo México</span>
      <h2>Empieza a recibir reseñas hoy</h2>
      <p>Hacemos que tus clientes felices compartan su experiencia en segundos y te ayudamos a construir tu reputación en línea con opiniones reales.</p>
      <div class="cta__botones">
        <a class="btn btn--blanco" href="{idx}#catalogo">Ver tarjetas</a>
        <a class="btn btn--contorno-blanco" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">{WA_SVG} Hablar con un asesor</a>
      </div>
    </div>
  </section>
  <div class="footer">
    <div class="contenedor">
      <div class="footer__cols">
        <div>
          <h3>Tienda</h3>
          <ul><li><a href="{idx}#catalogo">Todas las tarjetas</a></li>{cats}<li><a href="{idx}#precios">Paquetes y precios</a></li></ul>
        </div>
        <div>
          <h3>Más vendidas</h3>
          <ul>{populares}</ul>
        </div>
        <div>
          <h3>Ayuda</h3>
          <ul>
            {''.join('<li><a href="%s%s">%s</a></li>' % (base, a, t) for a, t in AYUDA)}
            <li><a href="{idx}#preguntas">Preguntas frecuentes</a></li>
            <li><a href="https://wa.me/{WHATSAPP}?text={quote('Hola, me interesa un pedido de mayoreo de tarjetas NFC')}" target="_blank" rel="noopener">Pedidos de mayoreo</a></li>
          </ul>
        </div>
        <div class="footer__contacto">
          <h3>Contacto</h3>
          <p>¿Dudas con tu pedido o quieres una tarjeta con tu logo? Escríbenos, te respondemos rápido.</p>
          <p><a href="tel:{TELEFONO_E164}">{TELEFONO}</a><br><a href="mailto:{CORREO}">{CORREO}</a></p>
          <a class="btn btn--blanco" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">{WA_SVG} WhatsApp</a>
        </div>
      </div>
      <div class="footer__legal">
        <span>© {date.today().year} {MARCA} · tarjetasnfc.com.mx · Hecho para negocios mexicanos</span>
        <span>Precios en pesos mexicanos (MXN) con envío incluido.</span>
      </div>
    </div>
  </div>
</footer>"""


def carrito_y_scripts(base):
    return f"""
<aside class="drawer drawer--der" id="carrito" aria-hidden="true" aria-label="Carrito">
  <div class="drawer__cabecera">
    <h2>Tu carrito</h2>
    <button class="icono-btn" type="button" data-cerrar aria-label="Cerrar carrito">{icono("cerrar")}</button>
  </div>
  <div class="drawer__cuerpo" id="carrito-items"></div>
  <div class="carrito__pie" id="carrito-pie" hidden>
    <div class="carrito__total"><span>Total</span><span id="carrito-total">$0</span></div>
    <p>Envío gratis incluido. Pago seguro con tarjeta procesado por Stripe.</p>
    <button class="btn btn--primario btn--bloque" type="button" id="btn-pagar">{icono("candado", 20)} Pagar ahora</button>
    <button class="btn-texto carrito__wa" type="button" id="btn-finalizar">¿Prefieres pedir por WhatsApp?</button>
  </div>
</aside>
<button class="volver-arriba" type="button" aria-label="Volver arriba">{icono("arriba", 20)}</button>
<div class="aviso" id="aviso" role="status" aria-live="polite"></div>
<script src="{base}js/productos.js"></script>
<script src="{base}js/main.js"></script>
</body>
</html>
"""


def calificacion_html(p, clase=""):
    if p["slug"] not in CALIFICACIONES:
        return ""
    promedio, total = CALIFICACIONES[p["slug"]]
    texto = "{:.1f}/5 · {:,} reseñas".format(promedio, total) if clase else "{:.1f} ({:,})".format(promedio, total)
    return ('<div class="calificacion %s" aria-label="Calificación de %.1f de 5, basada en %s reseñas">'
            '<span class="calificacion__estrellas" aria-hidden="true"><span style="width:%d%%"></span></span>'
            '<span class="calificacion__texto" aria-hidden="true">%s</span></div>'
            % (clase, promedio, "{:,}".format(total), round(promedio / 5 * 100), texto))


def tarjeta_producto(p, base, h="h3", lazy=True):
    ahorro = PAQUETES[0]["ahorro"]
    return f"""
<article class="tarjeta-producto" data-categoria="{p['cat']}" data-nombre="{escape(p['nombre'])}" data-orden="{p['orden']}">
  <a class="tarjeta-producto__media" href="{base}{p['url']}" tabindex="-1" aria-hidden="true">
    <span class="insignia">Ahorra {ahorro}%</span>
    <img src="{base}{webp(p, 800)}" srcset="{srcset(base, p, (400, 800))}" sizes="(max-width: 720px) 50vw, (max-width: 1024px) 33vw, 300px" alt="{escape(p['nombre'])} con NFC y código QR" width="800" height="800"{' loading="lazy"' if lazy else ''} decoding="async">
    <span class="tarjeta-producto__ver">Ver producto {icono("der", 18)}</span>
  </a>
  <div class="tarjeta-producto__cuerpo">
    <span class="tarjeta-producto__cat">{NOMBRE_CAT[p['cat']]}</span>
    <{h}><a href="{base}{p['url']}">{escape(p['nombre'])}</a></{h}>
    {calificacion_html(p)}
    <div class="precio"><span class="precio__actual">{dinero(PAQUETES[0]['precio'])}</span><span class="precio__antes">{dinero(PAQUETES[0]['antes'])}</span></div>
  </div>
</article>"""


PASOS = [
    ("caja", "Recibe tu tarjeta", "La configuramos con tu enlace antes de enviarla. Llega lista para usar, sin apps ni instalaciones."),
    ("celular", "Tu cliente la toca", "Acerca su celular a la tarjeta (NFC) o escanea el código QR con la cámara."),
    ("estrella", "Se abre tu enlace", "Al instante aparece tu página de reseñas, perfil o chat. Dejar una reseña toma segundos."),
]

FAQ = [
    ("¿Cómo funciona una tarjeta NFC?", "La tarjeta tiene un chip NFC y un código QR con tu enlace. Cuando un cliente acerca su celular a la tarjeta, o escanea el QR con la cámara, se abre automáticamente tu página de reseñas, perfil o chat. No necesita descargar ninguna aplicación."),
    ("¿Es compatible con todos los celulares?", "Sí. El NFC funciona en iPhone XS o posterior y en la gran mayoría de celulares Android con NFC activado. Para cualquier otro teléfono, el código QR impreso se escanea con la cámara."),
    ("¿Tengo que pagar mensualidades?", "No. Es un pago único. La tarjeta funciona para siempre, no requiere batería ni suscripciones."),
    ("¿Quién configura la tarjeta?", "Nosotros. Al hacer tu pedido nos indicas tu negocio, perfil o enlace y te enviamos la tarjeta ya programada y lista para usar."),
    ("¿Hacen envíos a todo México?", "Sí, enviamos a toda la República Mexicana y el envío ya está incluido en el precio de todos los paquetes. Los envíos suelen tardar de 3 a 5 días hábiles."),
    ("¿Puedo combinar tarjetas de distintas plataformas?", "Sí. Puedes agregar al carrito tarjetas de Google, Instagram, WhatsApp o cualquier otra plataforma, cada una con su propio paquete. Si necesitas una combinación especial, escríbenos por WhatsApp."),
    ("¿Las tarjetas de Google son las mismas que vende Google?", "No. Son tarjetas independientes fabricadas por TarjetasNFC que abren el enlace oficial de reseñas de tu negocio. Google, Instagram y el resto de marcas mencionadas pertenecen a sus respectivos dueños."),
    ("¿Venden por mayoreo o para agencias?", "Sí. Para pedidos de más de 10 tarjetas, franquicias o agencias de marketing tenemos precios especiales. Escríbenos por WhatsApp para cotizar."),
]


def faq_html():
    return "".join(
        '<details><summary>%s %s</summary><div class="acordeon__cuerpo"><p>%s</p></div></details>' % (escape(q), icono("mas", 20), escape(a))
        for q, a in FAQ)


def pasos_html():
    return "".join(
        '<li class="paso"><div class="paso__icono">%s</div><h3>%s</h3><p>%s</p></li>' % (icono(i, 28), t, d)
        for i, t, d in PASOS)


# --------------------------------------------------------------------------
# index.html
# --------------------------------------------------------------------------
def generar_index():
    base = ""
    chips = '<button class="chip" type="button" data-categoria="todas" aria-pressed="true">Todas</button>' + "".join(
        '<button class="chip" type="button" data-categoria="%s" aria-pressed="false">%s</button>' % (c, n) for c, n in CATEGORIAS)
    planes = []
    for pq in PAQUETES:
        destacado = pq["tarjetas"] == 5
        cinta = '<span class="paquete__cinta">%s</span>' % pq["cinta"] if pq["cinta"] else ""
        planes.append(f"""
<div class="plan{' plan--destacado' if destacado else ''}">
  {cinta}
  <h3>{pq['nombre'].capitalize()}</h3>
  <span class="plan__antes">Antes {dinero(pq['antes'])}</span>
  <div class="plan__precio">{dinero(pq['precio'])}</div>
  <div class="plan__unidad">{dinero(pq['unidad'])} por tarjeta</div>
  <ul>
    <li>{check(16)} Envío gratis incluido</li>
    <li>{check(16)} Configuración incluida</li>
    <li>{check(16)} NFC + código QR</li>
    {'<li>%s Ahorras %d%% por tarjeta</li>' % (check(16), pq['descuentoUnidad']) if pq['descuentoUnidad'] else '<li>%s Ideal para probar</li>' % check(16)}
  </ul>
  <a class="btn {'btn--primario' if destacado else 'btn--contorno'} btn--bloque" href="#catalogo">Elegir tarjeta</a>
</div>""")

    titulo = "Tarjetas NFC para Reseñas de Google y Redes Sociales | México"
    descripcion = ("Tarjetas NFC con código QR para más reseñas en Google y seguidores en Instagram, TikTok y WhatsApp. "
                   "Desde $200 MXN, pago único y envío gratis en México.")
    grafo = [nodo_org(), nodo_sitio()] + nodos_pagina(
        "", "Tarjetas NFC para reseñas y redes sociales en México", descripcion, [], "CollectionPage",
        "imagenes/productos/google-nfc.png", {"mainEntity": {"@id": DOMINIO + "/#catalogo"}}, (),
        [p["url"] for p in PRODUCTOS] + [a for a, _ in AYUDA])
    grafo[2]["breadcrumb"] = {"@id": DOMINIO + "/#migas"}
    grafo[3] = {"@type": "BreadcrumbList", "@id": DOMINIO + "/#migas",
                "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"}]}
    grafo.append({"@type": "ItemList", "@id": DOMINIO + "/#catalogo", "name": "Catálogo de tarjetas NFC", "numberOfItems": len(PRODUCTOS),
                  "itemListOrder": "https://schema.org/ItemListOrderAscending",
                  "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": DOMINIO + "/" + p["url"], "name": p["nombre"],
                                       "image": DOMINIO + "/" + p["imagen"]} for i, p in enumerate(PRODUCTOS)]})
    grafo.append({"@type": "OfferCatalog", "@id": DOMINIO + "/#paquetes", "name": "Paquetes de tarjetas NFC",
                  "itemListElement": [{"@type": "Offer", "name": "Paquete de " + pq["nombre"], "price": pq["precio"], "priceCurrency": "MXN",
                                       "availability": "https://schema.org/InStock", "seller": {"@id": ID_ORG}} for pq in PAQUETES]})
    grafo.append(nodo_faq("", FAQ))
    keywords = ["tarjetas nfc", "tarjetas nfc méxico", "tarjeta nfc reseñas google", "tarjeta para reseñas de google", "tarjeta nfc instagram",
                "tarjeta nfc whatsapp", "tarjeta nfc tiktok", "tarjeta nfc facebook", "tarjeta nfc wifi", "tarjeta nfc uber eats",
                "tarjeta nfc rappi", "tarjeta nfc tripadvisor", "tarjeta nfc airbnb", "tarjeta qr para negocios", "tarjeta nfc con código qr",
                "tarjeta nfc personalizada", "comprar tarjetas nfc", "tarjetas nfc precio", "tarjetas nfc para negocios",
                "cómo conseguir más reseñas en google", "tarjeta tap to review", "tarjeta toca para reseñar", "tarjetas nfc cdmx",
                "tarjetas nfc guadalajara", "tarjetas nfc monterrey", "tarjetas nfc tijuana", "envío gratis méxico"]
    grafo[2]["keywords"] = ", ".join(keywords)
    html = head(base, titulo, descripcion, "", "imagenes/productos/google-nfc.png", grafo, keywords=keywords,
                img_alt="Tarjeta NFC para reseñas de Google con código QR",
                preload='<link rel="preload" as="image" href="%s" imagesrcset="%s" imagesizes="(max-width: 720px) 50vw, 300px" fetchpriority="high">\n'
                        % (webp(PRODUCTOS[0], 800), srcset("", PRODUCTOS[0], (400, 800))))
    html += f"""
<body data-base="{base}">
{header(base, "tienda")}
<main id="contenido">
  <section class="seccion" id="catalogo" aria-labelledby="titulo-catalogo">
    <div class="contenedor">
      <div class="catalogo__encabezado">
        <h1 id="titulo-catalogo">Tarjetas NFC para cada plataforma</h1>
        <p>Elige la plataforma, nosotros la configuramos con tu enlace y te la enviamos lista para usar. Envío gratis a todo México.</p>
      </div>
      <div class="catalogo__barra">
        <div class="filtros" role="group" aria-label="Filtrar por categoría">{chips}</div>
        <div class="catalogo__orden">
          <label class="solo-lectores" for="orden">Ordenar</label>
          <select class="select" id="orden">
            <option value="destacados">Destacados</option>
            <option value="az">Nombre: A–Z</option>
            <option value="za">Nombre: Z–A</option>
          </select>
          <span id="conteo">{len(PRODUCTOS)} productos</span>
        </div>
      </div>
      <div class="rejilla" id="rejilla-catalogo">
        {''.join(tarjeta_producto(p, base, lazy=i > 3) for i, p in enumerate(PRODUCTOS))}
      </div>
    </div>
  </section>

  <section class="seccion seccion--gris" id="como-funciona" aria-labelledby="titulo-como">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <span class="etiqueta-seccion">Así de fácil</span>
        <h2 id="titulo-como">¿Cómo funcionan las tarjetas NFC?</h2>
        <p>Sin apps, sin baterías y sin configuraciones complicadas.</p>
      </div>
      <ol class="pasos">{pasos_html()}</ol>
      <p class="centrado"><a class="enlace-ver-mas" href="como-funciona.html">Ver la guía completa con video {icono("der", 18)}</a></p>
    </div>
  </section>

  <section class="seccion" aria-labelledby="titulo-beneficios">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <span class="etiqueta-seccion">Ventajas</span>
        <h2 id="titulo-beneficios">¿Por qué elegir TarjetasNFC?</h2>
        <p>Todo lo que necesitas para que tus clientes te encuentren, sin complicaciones.</p>
      </div>
      <div class="beneficios">
        <div class="beneficio">{icono("infinito", 30)}<h3>Pago único</h3><p>Sin mensualidades ni suscripciones. Tu tarjeta funciona para siempre.</p></div>
        <div class="beneficio">{icono("qr", 30)}<h3>NFC + QR</h3><p>Funciona con un toque o escaneando el código, en cualquier celular.</p></div>
        <div class="beneficio">{icono("camion", 30)}<h3>Envío gratis</h3><p>Enviamos a toda la República Mexicana con el envío incluido.</p></div>
        <div class="beneficio">{icono("pincel", 30)}<h3>Lista para usar</h3><p>La configuramos con tu enlace antes de enviarla. Solo colócala.</p></div>
      </div>
    </div>
  </section>

  <section class="seccion seccion--gris" id="precios" aria-labelledby="titulo-precios">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <span class="etiqueta-seccion">Compra más, ahorra más</span>
        <h2 id="titulo-precios">Paquetes y precios</h2>
        <p>Los mismos precios para todas las plataformas. Envío incluido.</p>
      </div>
      <div class="tabla-precios">{''.join(planes)}</div>
      <p class="nota-precios">Precios en pesos mexicanos (MXN). ¿Necesitas más de 10 tarjetas? <a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener"><u>Cotiza mayoreo</u></a>.</p>
    </div>
  </section>

  <section class="seccion" id="preguntas" aria-labelledby="titulo-faq">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <h2 id="titulo-faq">Preguntas frecuentes</h2>
      </div>
      <div class="faq acordeon">{faq_html()}</div>
    </div>
  </section>

</main>
{pie(base)}
{carrito_y_scripts(base)}"""
    escribir("index.html", html)


# --------------------------------------------------------------------------
# Páginas de producto
# --------------------------------------------------------------------------
INFO_SLIDES = [
    ("caja", "Recibe tu tarjeta", "Te la enviamos configurada con tu enlace, lista para colocar en tu negocio."),
    ("nfc", "Toca o escanea", "Tu cliente acerca su celular a la tarjeta o escanea el código QR con la cámara."),
    ("estrella", "¡Listo en segundos!", "Se abre tu enlace al instante. Sin descargar apps ni buscar tu negocio."),
]


def info_slide(n, i, t, d):
    return ('<div class="info-slide"><div class="info-slide__num">%d</div><div class="info-slide__icono">%s</div>'
            '<h3>%s</h3><p>%s</p></div>' % (n, icono(i, 120, ' stroke-width="1.4"'), t, d))


def generar_producto(p):
    base = "../"
    pq0 = PAQUETES[0]
    titulo = "%s | Envío gratis a todo México" % p["nombre"]
    descripcion = "%s Desde %s por tarjeta, pago único y envío gratis a todo México." % (p["desc"], dinero(PAQUETES[-1]["unidad"]))

    slides = ['<div class="galeria__slide"><img src="%s%s" srcset="%s" sizes="(max-width: 1024px) 100vw, 620px" alt="%s con chip NFC y código QR" '
              'width="1200" height="1200" fetchpriority="high"></div>' % (base, webp(p, 1200), srcset(base, p, (800, 1200)), escape(p["nombre"]))]
    minis = ['<button class="miniatura" type="button" aria-label="Ver imagen 1"><img src="%s%s" alt="" width="96" height="96"></button>' % (base, webp(p, 400))]
    if p.get("video"):
        v = p["video"]
        slides.append('<div class="galeria__slide"><video src="%s%s" poster="%s%s" muted loop playsinline controls preload="metadata" '
                      'width="%d" height="%d" aria-label="%s"></video></div>' % (base, v["src"], base, v["poster"], v["ancho"], v["alto"], escape(v["nombre"])))
        minis.append('<button class="miniatura miniatura--video" type="button" aria-label="Ver video"><img src="%s%s" alt="" width="96" height="96">'
                     '<span class="miniatura__play"><span>%s</span></span></button>' % (base, v["poster"], icono("play", 14)))
    for n, (i, t, d) in enumerate(INFO_SLIDES, start=1):
        slides.append('<div class="galeria__slide">%s</div>' % info_slide(n, i, t, d))
        minis.append('<button class="miniatura" type="button" aria-label="Ver imagen %d">%s</button>' % (len(minis) + 1, info_slide(n, i, t, d)))

    paquetes = []
    for j, pq in enumerate(PAQUETES):
        descuento = '<span class="insignia insignia--sm">%d%% menos</span>' % pq["descuentoUnidad"] if pq["descuentoUnidad"] else ""
        unidad = '<span class="paquete__unidad">%s c/u</span>' % dinero(pq["unidad"]) if pq["tarjetas"] > 1 else '<span class="paquete__unidad">Envío incluido</span>'
        cinta = '<span class="paquete__cinta">%s</span>' % pq["cinta"] if pq["cinta"] else ""
        paquetes.append(f"""
<label class="paquete">
  {cinta}
  <input type="radio" name="paquete" value="{pq['tarjetas']}"{' checked' if j == 0 else ''}>
  <span class="paquete__caja">
    <span class="paquete__radio"></span>
    <span class="paquete__info">
      <span class="paquete__nombre">{pq['nombre'].capitalize()} {descuento}</span>
      {unidad}
    </span>
    <span class="paquete__precios">
      <span class="paquete__total">{dinero(pq['precio'])}</span>
      <span class="paquete__antes">{dinero(pq['antes'])}</span>
    </span>
  </span>
</label>""")

    relacionados = [x for x in PRODUCTOS if x["cat"] == p["cat"] and x is not p]
    relacionados += [x for x in PRODUCTOS if x not in relacionados and x is not p]
    relacionados = relacionados[:4]

    etiqueta, placeholder, ayuda = p["campo"]
    boton_ayuda = ""
    if p.get("ayuda_enlace"):
        texto, url = p["ayuda_enlace"]
        boton_ayuda = ('<a class="btn btn--contorno btn--sm personaliza__ayuda" href="%s" target="_blank" rel="noopener">%s %s</a>'
                       % (url, icono("buscar", 18), escape(texto)))
    usos = "".join("<li>%s</li>" % escape(u) for u in p["usos"])
    url_abs = DOMINIO + "/" + p["url"]

    prom_total = CALIFICACIONES.get(p["slug"])
    titulo = "%s | Envío Gratis en México" % p["nombre"]
    descripcion = ("%s con código QR, lista para usar. %sDesde %s, pago único y envío gratis a todo México."
                   % (p["nombre"], ("Calificación %.1f/5. " % prom_total[0]) if prom_total else "", dinero(PAQUETES[-1]["unidad"])))
    ofertas = [{"@type": "Offer", "name": "%s – paquete de %s" % (p["nombre"], pq["nombre"]), "price": pq["precio"], "priceCurrency": "MXN",
                "priceValidUntil": PRECIO_VALIDO, "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
                "url": url_abs, "seller": {"@id": ID_ORG},
                "eligibleQuantity": {"@type": "QuantitativeValue", "value": pq["tarjetas"], "unitText": "tarjetas"},
                "priceSpecification": {"@type": "UnitPriceSpecification", "price": pq["unidad"], "priceCurrency": "MXN",
                                       "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitText": "tarjeta"}},
                "shippingDetails": envio_schema(), "hasMerchantReturnPolicy": devolucion_schema()} for pq in PAQUETES]
    producto = {
        "@type": "Product", "@id": url_abs + "#producto", "name": p["nombre"], "url": url_abs,
        "description": p["desc"] + " " + p["detalle"],
        "image": [DOMINIO + "/" + p["imagen"], DOMINIO + "/" + webp(p, 1200)], "sku": "TNFC-" + p["img"].split("-")[0].upper(), "mpn": "TNFC-" + p["img"].split("-")[0].upper(),
        "brand": {"@type": "Brand", "name": MARCA}, "manufacturer": {"@id": ID_ORG},
        "category": "Tarjetas NFC > " + NOMBRE_CAT[p["cat"]], "mainEntityOfPage": {"@id": url_abs + "#webpage"},
        "audience": {"@type": "BusinessAudience", "audienceType": ", ".join(p["usos"])},
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Tecnología", "value": "Chip NFC + código QR"},
            {"@type": "PropertyValue", "name": "Medidas", "value": "85.6 mm x 54 mm"},
            {"@type": "PropertyValue", "name": "Compatibilidad", "value": "iPhone y Android con NFC; cualquier celular con cámara (QR)"},
            {"@type": "PropertyValue", "name": "Mensualidades", "value": "No, pago único"},
            {"@type": "PropertyValue", "name": "Plataforma", "value": p["plataforma"]},
        ],
        "offers": {"@type": "AggregateOffer", "priceCurrency": "MXN", "lowPrice": PAQUETES[0]["precio"], "highPrice": PAQUETES[-1]["precio"],
                   "offerCount": len(PAQUETES), "availability": "https://schema.org/InStock", "url": url_abs, "seller": {"@id": ID_ORG},
                   "offers": ofertas},
        "isRelatedTo": [{"@type": "Product", "name": x["nombre"], "url": DOMINIO + "/" + x["url"]} for x in relacionados],
    }
    if prom_total:
        producto["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": prom_total[0], "bestRating": 5, "worstRating": 1,
                                       "reviewCount": prom_total[1], "ratingCount": prom_total[1]}
    grafo = [nodo_org(), nodo_sitio()] + nodos_pagina(
        p["url"], p["nombre"], descripcion, [("Inicio", ""), (NOMBRE_CAT[p["cat"]], "?categoria=" + p["cat"])], "ItemPage",
        p["imagen"], {"mainEntity": {"@id": url_abs + "#producto"}}, palabras_clave_producto(p),
        [x["url"] for x in relacionados] + ["como-activar-nfc-celular.html", "envios-y-devoluciones.html"]) + [producto]
    extra_meta = ('<meta property="product:price:amount" content="%d">\n<meta property="product:price:currency" content="MXN">\n'
                  '<meta property="product:availability" content="in stock">\n<meta property="product:condition" content="new">\n'
                  '<meta property="product:brand" content="%s">\n' % (PAQUETES[0]["precio"], MARCA))
    if p.get("video"):
        producto["subjectOf"] = {"@id": url_abs + "#video"}
        grafo.append(nodo_video(p["url"], p["video"]))
        extra_meta += ('<meta property="og:video" content="%s/%s">\n<meta property="og:video:type" content="video/mp4">\n'
                       '<meta property="og:video:width" content="%d">\n<meta property="og:video:height" content="%d">\n'
                       % (DOMINIO, p["video"]["src"], p["video"]["ancho"], p["video"]["alto"]))
    html = head(base, titulo, descripcion, p["url"], p["imagen"], grafo, "product", palabras_clave_producto(p),
                img_alt="%s con chip NFC y código QR" % p["nombre"], extra_meta=extra_meta,
                preload='<link rel="preload" as="image" href="%s%s" imagesrcset="%s" imagesizes="(max-width: 1024px) 100vw, 620px" fetchpriority="high">\n'
                        % (base, webp(p, 1200), srcset(base, p, (800, 1200))))
    html += f"""
<body class="pagina-producto" data-base="{base}">
{header(base)}
<main id="contenido">
  <div class="contenedor">
    <nav class="migas" aria-label="Migas de pan">
      <ol>
        <li><a href="{base}index.html">Inicio</a></li>
        <li><a href="{base}index.html?categoria={p['cat']}#catalogo">{NOMBRE_CAT[p['cat']]}</a></li>
        <li aria-current="page">{escape(p['nombre'])}</li>
      </ol>
    </nav>

    <div class="producto">
      <div class="galeria" aria-label="Galería de imágenes">
        <div class="galeria__visor">
          <div class="galeria__pista">{''.join(slides)}</div>
          <button class="galeria__expandir" type="button" aria-label="Ver en pantalla completa">{icono("expandir", 20)}</button>
          <button class="galeria__flecha galeria__flecha--prev" type="button" aria-label="Imagen anterior">{icono("izq", 22)}</button>
          <button class="galeria__flecha galeria__flecha--next" type="button" aria-label="Imagen siguiente">{icono("der", 22)}</button>
        </div>
        <div class="galeria__miniaturas">{''.join(minis)}</div>
      </div>

      <div class="compra">
        <p class="compra__confianza">{icono("camion", 18)} Envío gratis a toda la República Mexicana 🇲🇽</p>
        <h1>{escape(p['nombre'])}</h1>
        {calificacion_html(p, "calificacion--grande")}
        <div class="precio">
          <span class="precio__actual" id="precio-actual">{dinero(pq0['precio'])}</span>
          <span class="precio__antes" id="precio-antes">{dinero(pq0['antes'])}</span>
          <span class="insignia">{icono("tag", 16)} <span id="precio-ahorro">Ahorra {pq0['ahorro']}%</span></span>
          <span class="precio__nota" id="precio-nota">Envío gratis incluido a todo México</span>
        </div>
        <ul class="lista-check">
          <li>{check()} <span>{p['check'][0]} <b>{p['check'][1]}</b></span></li>
          <li>{check()} <span>Pago único – <b>Sin mensualidades</b></span></li>
          <li>{check()} <span>Tamaño de la tarjeta: <b>85.6 mm x 54 mm</b></span></li>
        </ul>

        <form id="form-compra" data-slug="{p['slug']}" novalidate>
          <h2 class="titulo-linea">Compra más, ahorra más</h2>
          <fieldset class="paquetes">
            <legend class="solo-lectores">Elige tu paquete</legend>
            {''.join(paquetes)}
          </fieldset>

          <h2 class="titulo-linea titulo-linea--normal">Personaliza tu tarjeta 👇</h2>
          <div class="personaliza">
            <label class="solo-lectores" for="dato-negocio">{escape(etiqueta)}</label>
            <div class="campo">
              <span class="campo__logo"><img src="{base}{webp(p, 400)}" alt="" width="46" height="46" loading="lazy"></span>
              <input class="input" id="dato-negocio" name="dato" type="text" placeholder="{escape(placeholder)}" autocomplete="off" spellcheck="false" required>
            </div>
            <p><b>{escape(etiqueta)}.</b> {escape(ayuda)}</p>
            {boton_ayuda}
            {('<p><a href="%scomo-encontrar-enlace-resenas-google.html"><u>Ver nuestra guía paso a paso</u></a></p>' % base) if p["plataforma"] == "Google" else ""}
          </div>

          <div class="compra__acciones">
            <div class="cantidad">
              <button type="button" data-cantidad="-1" aria-label="Quitar uno">−</button>
              <input id="cantidad" type="number" value="1" min="1" max="99" inputmode="numeric" aria-label="Cantidad de paquetes">
              <button type="button" data-cantidad="1" aria-label="Agregar uno">+</button>
            </div>
            <button class="btn btn--primario" type="submit" id="btn-agregar">{icono("carrito", 20)} Agregar al carrito · <span id="btn-agregar-precio">{dinero(pq0['precio'])}</span></button>
          </div>
          <button class="btn btn--oscuro btn--bloque" type="button" id="btn-comprar">{icono("candado", 20)} Comprar ahora · pago seguro</button>
        </form>

        <div class="compra__garantias">
          <div class="garantia">{icono("camion", 24)} Envío gratis a todo México</div>
          <div class="garantia">{icono("rayo", 24)} Configurada y lista para usar</div>
          <div class="garantia">{icono("escudo", 24)} Sin apps ni mensualidades</div>
        </div>

        <div class="acordeon">
          <details open>
            <summary>Descripción {icono("mas", 20)}</summary>
            <div class="acordeon__cuerpo">
              <p>{escape(p['desc'])}</p>
              <p>{escape(p['detalle'])}</p>
              <p><b>Ideal para:</b></p>
              <ul>{usos}</ul>
            </div>
          </details>
          <details>
            <summary>¿Cómo funciona? {icono("mas", 20)}</summary>
            <div class="acordeon__cuerpo">
              <ol style="padding-left:20px">
                <li>Elige tu paquete y escribe los datos de tu {escape(p['plataforma'])}.</li>
                <li>Configuramos el chip NFC y el código QR con tu enlace.</li>
                <li>Recibes tu tarjeta lista en tu domicilio, con envío gratis.</li>
                <li>Tus clientes la tocan con su celular o escanean el QR y se abre tu enlace al instante.</li>
              </ol>
            </div>
          </details>
          <details>
            <summary>Compatibilidad {icono("mas", 20)}</summary>
            <div class="acordeon__cuerpo">
              <ul>
                <li><b>iPhone:</b> XS o posterior leen NFC sin apps.</li>
                <li><b>Android:</b> la gran mayoría de equipos con NFC activado.</li>
                <li><b>Cualquier celular:</b> el código QR se escanea con la cámara.</li>
                <li>No requiere batería, ni aplicación, ni conexión especial.</li>
              </ul>
              <p><a href="{base}como-activar-nfc-celular.html"><u>Cómo activar el NFC de tu celular</u></a></p>
            </div>
          </details>
          <details>
            <summary>Especificaciones {icono("mas", 20)}</summary>
            <div class="acordeon__cuerpo">
              <ul>
                <li>Medidas: 85.6 mm x 54 mm (tamaño tarjeta de crédito).</li>
                <li>Chip NFC integrado + código QR impreso.</li>
                <li>Enlace configurado antes del envío.</li>
              </ul>
            </div>
          </details>
          <details>
            <summary>Envío y entrega {icono("mas", 20)}</summary>
            <div class="acordeon__cuerpo">
              <p>El envío es gratis a cualquier parte de la República Mexicana y ya está incluido en el precio. Los envíos suelen tardar de <b>3 a 5 días hábiles</b>. Pagas en línea de forma segura y capturas tu dirección de envío en el mismo paso.</p>
              <p><a href="{base}envios-y-devoluciones.html"><u>Ver política de envíos y devoluciones</u></a></p>
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>

  <section class="seccion seccion--gris" aria-labelledby="titulo-como">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <span class="etiqueta-seccion">Así de fácil</span>
        <h2 id="titulo-como">Así funciona tu tarjeta de {escape(p['plataforma'])}</h2>
        <p>Sin apps, sin baterías y sin configuraciones complicadas.</p>
      </div>
      <ol class="pasos">{pasos_html()}</ol>
    </div>
  </section>

  <section class="seccion" aria-labelledby="titulo-relacionados">
    <div class="contenedor">
      <div class="encabezado-seccion">
        <h2 id="titulo-relacionados">También te puede interesar</h2>
      </div>
      <div class="rejilla">{''.join(tarjeta_producto(x, base) for x in relacionados)}</div>
    </div>
  </section>
</main>

<div class="barra-compra" aria-hidden="true">
  <div class="barra-compra__info"><strong class="barra-compra__precio">{dinero(pq0['precio'])}</strong><span class="barra-compra__paquete">{pq0['nombre']}</span></div>
  <button class="btn btn--primario" type="button" tabindex="-1">Agregar al carrito</button>
</div>
{pie(base)}
{carrito_y_scripts(base)}"""
    escribir(p["url"], html)


# --------------------------------------------------------------------------
# Páginas de ayuda (menú "Ayuda")
# --------------------------------------------------------------------------
def caja(icono_html, titulo, cuerpo, lead="", ident="", h="h2", clase=""):
    return ('<section class="caja %s"%s>%s<%s class="caja__titulo">%s</%s>%s%s</section>'
            % (clase, (' id="%s"' % ident) if ident else "", '<div class="caja__icono" aria-hidden="true">%s</div>' % icono_html,
               h, titulo, h, ('<p class="caja__lead">%s</p>' % lead) if lead else "", cuerpo))


def caja_mas_ayuda(base=""):
    return caja("?", "¿Necesitas más ayuda?",
                '<div class="caja__botones"><a class="btn btn--primario" href="%scontacto.html">Contáctanos %s</a></div>' % (base, icono("der", 18)),
                "Si no encuentras la respuesta que buscas, contáctanos dando clic en el botón de abajo.")


def pasos_num(ident, pasos, vertical=False):
    return '<ol class="pasos-num%s">%s</ol>' % (" pasos-num--vertical" if vertical else "", "".join(
        '<li id="%s-%d"><h3>%s</h3><p>%s</p></li>' % (ident, i + 1, t, d) for i, (t, d) in enumerate(pasos)))


def faq_bloque(preguntas, titulo="Preguntas frecuentes"):
    items = "".join('<details><summary>%s %s</summary><div class="acordeon__cuerpo"><p>%s</p></div></details>'
                    % (escape(q), icono("mas", 20), escape(a)) for q, a in preguntas)
    return caja(icono("ayuda"), titulo, '<div class="caja__cuerpo acordeon">%s</div>' % items, ident="preguntas")


def pagina_ayuda(archivo, titulo_seo, descripcion, keywords, etiqueta, h1, intro, cuerpo, grafo_extra=(), faq=None,
                 tipo="WebPage", imagen="imagenes/productos/google-nfc.png", img_dim=(2000, 2000), mas_ayuda=True, extra_meta="", preload=""):
    base = ""
    nombre = dict(AYUDA)[archivo]
    relacionados = [a for a, _ in AYUDA if a != archivo] + [PRODUCTOS[0]["url"]]
    grafo = [nodo_org(), nodo_sitio()] + nodos_pagina(archivo, h1, descripcion, [("Inicio", "")], tipo, imagen, None, keywords, relacionados) + list(grafo_extra)
    if faq:
        grafo.append(nodo_faq(archivo, faq))
    html = head(base, titulo_seo, descripcion, archivo, imagen, grafo, keywords=keywords, img_dim=img_dim, img_alt=h1, extra_meta=extra_meta, preload=preload)
    html += f"""
<body data-base="{base}">
{header(base, "ayuda")}
<main id="contenido">
  <section class="cabecera-pagina">
    <div class="contenedor">
      <nav class="migas" aria-label="Migas de pan">
        <ol>
          <li><a href="index.html">Inicio</a></li>
          <li>Ayuda</li>
          <li aria-current="page">{nombre}</li>
        </ol>
      </nav>
      <span class="etiqueta-seccion">{etiqueta}</span>
      <h1>{h1}</h1>
      <p>{intro}</p>
    </div>
  </section>
  <div class="contenedor pagina-ayuda">
    {cuerpo}
    {faq_bloque(faq) if faq else ""}
    {caja_mas_ayuda() if mas_ayuda else ""}
  </div>
</main>
{pie(base)}
{carrito_y_scripts(base)}"""
    escribir(archivo, html)


PASOS_USO = [
    ("Recibe tu tarjeta de reseñas", "Te la enviamos configurada con el enlace de tu negocio, lista para colocar en tu mostrador, mesa o caja."),
    ("Simplemente acércala", "Tu cliente acerca su celular a la tarjeta (NFC) o escanea el código QR con la cámara. No necesita descargar ninguna app."),
    ("Deja una reseña positiva", "Se abre directamente la ventana para calificar tu negocio. Elegir las estrellas y escribir un comentario toma segundos."),
    ("Aumenta tus reseñas en Google", "Más reseñas y mejores calificaciones te ayudan a aparecer más arriba en Google Maps y a ganarte la confianza de nuevos clientes."),
]
PASOS_PEDIDO = [
    ("Elige tu tarjeta NFC", "Google, Instagram, WhatsApp, TikTok y más. Selecciona la plataforma y el paquete que más te convenga."),
    ("Realiza tu compra", "Agrega tus tarjetas al carrito y paga en línea de forma segura con tarjeta."),
    ("Asignamos tu tarjeta", "Programamos el chip NFC y el código QR con el enlace de tu negocio antes de enviarla."),
    ("Empieza a recibir reseñas", "Recibe tu tarjeta en 3 a 5 días hábiles, colócala a la vista y empieza a juntar reseñas desde el primer día."),
]
PASOS_ENLACE_GOOGLE = [
    ("Inicia sesión en Google", "Entra con la cuenta de Google con la que administras el Perfil de Negocio de tu empresa (antes Google My Business)."),
    ("Abre tu Perfil de Negocio", "Busca el nombre de tu negocio en Google o en Google Maps. Si eres administrador, verás el panel para gestionar tu perfil."),
    ("Selecciona «Pedir reseñas»", "En el panel de tu perfil elige la opción «Pedir reseñas» u «Obtener más reseñas». Google te mostrará un enlace corto para compartir."),
    ("Copia y comparte tu enlace", "Copia el enlace (normalmente empieza con https://g.page/r/) y pégalo en el campo «Enlace de reseñas de Google» al comprar tu tarjeta."),
]
PASOS_NFC_ANDROID = [
    ("Revisa tu versión de Android", "Tu celular debe tener Android 7.0 o posterior, la versión necesaria para pagos sin contacto."),
    ("Abre «Ajustes»", "Entra a la aplicación de Ajustes o Configuración de tu celular."),
    ("Busca «NFC»", "En la barra de búsqueda de los ajustes escribe «NFC»."),
    ("Activa el NFC", "Asegúrate de que el interruptor de NFC esté encendido. Si tu celular no tiene NFC, puede escanear el código QR impreso en la tarjeta."),
]


def generar_ayuda():
    # ---------------- Cómo funciona ----------------
    v = VIDEO_GOOGLE
    cuerpo = (
        caja(icono("nfc"), "Cómo funciona", (
            '<div class="video-fila"><video class="video-vertical" src="%s" poster="%s" controls autoplay muted loop playsinline preload="auto" width="%d" height="%d" '
            'aria-label="%s"></video></div>%s' % (v["src"], v["poster"], v["ancho"], v["alto"], escape(v["nombre"]),
                                                pasos_num("como-funciona", PASOS_USO))),
             "Tus clientes te califican en segundos: sin apps, sin buscar tu negocio y sin escribir enlaces.", ident="como-funciona")
        + caja(icono("carrito"), "Cómo hacer tu pedido",
               pasos_num("como-ordenar", PASOS_PEDIDO)
               + '<div class="caja__botones"><a class="btn btn--primario" href="index.html#catalogo">Ordenar ahora %s</a></div>' % icono("der", 18),
               "En cuatro pasos tienes tu tarjeta configurada y en camino.", ident="como-ordenar")
        + caja(icono("usuarios"), "Somos TarjetasNFC", (
            '<div class="caja__cuerpo"><p>Con incontables negocios en todo México, notamos que faltaba una pieza: una forma sencilla de conseguir reseñas. '
            'Por eso creamos TarjetasNFC y diseñamos y fabricamos nuestras propias tarjetas NFC «Toca para reseñar».</p>'
            '<p>Nuestro objetivo es muy claro: ayudar a los negocios mexicanos a recibir reseñas de sus clientes con un solo toque. '
            'Así de fácil.</p></div>'), lead="", ident="quienes-somos", clase="")
    )
    faq = [
        ("¿Mis clientes necesitan descargar una aplicación?", "No. Basta con acercar el celular a la tarjeta (NFC) o escanear el código QR con la cámara. El enlace se abre directamente en el navegador o en la app correspondiente."),
        ("¿Funciona con iPhone y Android?", "Sí. Funciona con iPhone y con celulares Android que tienen NFC. Si un celular no tiene NFC, el código QR impreso funciona con cualquier cámara."),
        ("¿Qué pasa si el celular de mi cliente no tiene NFC?", "Puede escanear el código QR que viene impreso en la tarjeta. Así ningún cliente se queda sin dejar su reseña."),
        ("¿Cuánto tarda en llegar mi tarjeta?", "Los envíos suelen tardar de 3 a 5 días hábiles a cualquier parte de México, y el envío es gratis."),
        ("¿Tengo que pagar mensualidades?", "No. Es un pago único: la tarjeta no requiere batería ni suscripción."),
    ]
    grafo = [
        nodo_howto("como-funciona.html", "como-funciona", "Cómo funcionan las tarjetas NFC para reseñas de Google",
                   "Pasos para que tus clientes dejen una reseña con un toque usando una tarjeta NFC.", PASOS_USO, "PT1M", "imagenes/productos/google-nfc.png"),
        nodo_howto("como-funciona.html", "como-ordenar", "Cómo pedir tu tarjeta NFC en TarjetasNFC",
                   "Pasos para comprar y recibir tu tarjeta NFC configurada en México.", PASOS_PEDIDO),
        nodo_video("como-funciona.html", v),
    ]
    pagina_ayuda(
        "como-funciona.html", "Cómo Funcionan las Tarjetas NFC para Reseñas | TarjetasNFC",
        "Así funcionan las tarjetas NFC para reseñas: tu cliente acerca su celular, se abre tu perfil de Google y te califica en segundos. Envío gratis en México.",
        ["cómo funcionan las tarjetas nfc", "cómo funciona una tarjeta nfc", "tarjeta nfc para reseñas", "tarjeta nfc reseñas google",
         "qué es una tarjeta nfc", "tarjeta toca para reseñar", "tap to review méxico", "cómo conseguir reseñas en google",
         "más reseñas en google maps", "tarjeta nfc con código qr", "cómo pedir tarjeta nfc", "tarjetas nfc méxico", "tarjetas nfc para negocios"],
        "Nuevas reseñas a un solo toque", "¿Cómo funcionan las tarjetas NFC?",
        "Una tarjeta, un toque y una reseña nueva. Así es como TarjetasNFC ayuda a los negocios de México a crecer su reputación en Google.",
        cuerpo, grafo, faq, imagen=v["poster"], img_dim=(v["ancho"], v["alto"]),
        extra_meta=('<meta property="og:video" content="%s/%s">\n<meta property="og:video:secure_url" content="%s/%s">\n'
                    '<meta property="og:video:type" content="video/mp4">\n<meta property="og:video:width" content="%d">\n<meta property="og:video:height" content="%d">\n'
                    % (DOMINIO, v["src"], DOMINIO, v["src"], v["ancho"], v["alto"])),
        preload='<link rel="preload" as="image" href="%s" fetchpriority="high">\n' % v["poster"])

    # ---------------- Enlace de reseñas de Google ----------------
    google = next(p for p in PRODUCTOS if p["plataforma"] == "Google")
    cuerpo = (
        caja(icono("buscar"), "Paso a paso", pasos_num("pasos", PASOS_ENLACE_GOOGLE) + (
            '<p class="caja__nota">Google actualiza su interfaz con frecuencia. Si alguna opción tiene otro nombre, consulta la guía oficial de Google.</p>'
            '<div class="caja__botones"><a class="btn btn--primario" href="https://support.google.com/business/answer/16816815" target="_blank" rel="noopener">'
            'Ver guía oficial de Google %s</a></div>' % icono("der", 18)),
            "Sigue estos pasos para obtener el enlace directo con el que tus clientes te califican en Google.", ident="paso-a-paso")
        + caja(icono("estrella"), "¿Aún no tienes Perfil de Negocio?", (
            '<div class="caja__cuerpo"><p>Para recibir reseñas en Google necesitas un Perfil de Negocio verificado. Crearlo es gratis desde '
            '<a href="https://www.google.com/business/" target="_blank" rel="noopener">google.com/business</a>: registra el nombre, la categoría y la dirección '
            'de tu negocio y completa la verificación que te pida Google.</p></div>'))
        + caja(icono("mensaje"), "¿No encuentras tu enlace?", (
            '<div class="caja__botones"><a class="btn btn--primario" href="https://wa.me/%s?text=%s" target="_blank" rel="noopener">%s Escríbenos por WhatsApp</a>'
            '<a class="btn btn--contorno" href="%s">Comprar tarjeta de reseñas de Google</a></div>'
            % (WHATSAPP, quote("Hola, necesito ayuda para encontrar el enlace de reseñas de Google de mi negocio"), WA_SVG, google["url"])),
            "Envíanos el nombre y la dirección de tu negocio y te ayudamos a encontrarlo.")
    )
    faq = [
        ("¿Cuánto cuesta obtener el enlace de reseñas de Google?", "Nada. El enlace es gratuito y lo genera Google desde tu Perfil de Negocio."),
        ("¿Mis clientes necesitan una cuenta de Google para dejar una reseña?", "Sí. Google pide iniciar sesión con una cuenta de Google para publicar una reseña. La mayoría de los usuarios de Android y Gmail ya tienen una."),
        ("¿Puedo usar el mismo enlace en varias tarjetas?", "Sí. Puedes programar el mismo enlace en todas las tarjetas que necesites, por ejemplo una por mesa o por caja."),
        ("¿Qué hago si tengo varias sucursales?", "Cada sucursal tiene su propio Perfil de Negocio y su propio enlace. Al comprar, escribe los enlaces separados por coma y configuramos cada tarjeta con el correcto."),
    ]
    pagina_ayuda(
        "como-encontrar-enlace-resenas-google.html", "Cómo Encontrar tu Enlace de Reseñas de Google | Guía",
        "Guía paso a paso para obtener el enlace directo de reseñas de tu Perfil de Negocio de Google y compartirlo con tus clientes o programarlo en tu tarjeta NFC.",
        ["enlace de reseñas de google", "link de reseñas google", "cómo obtener link de reseñas google", "cómo pedir reseñas en google",
         "perfil de negocio de google reseñas", "google my business reseñas link", "link para calificar en google", "enlace para dejar reseña en google",
         "cómo compartir enlace de reseñas google", "g.page reseñas", "tarjeta nfc reseñas google", "más reseñas en google maps"],
        "Guía de Google", "Cómo encontrar el enlace de reseñas de Google de tu negocio",
        "Con tu enlace directo de reseñas, tus clientes llegan en un toque a la ventana para calificarte. Así lo encuentras en tu Perfil de Negocio.",
        cuerpo, [nodo_howto("como-encontrar-enlace-resenas-google.html", "pasos", "Cómo encontrar el enlace de reseñas de Google de tu negocio",
                            "Pasos para obtener el enlace directo de reseñas desde el Perfil de Negocio de Google.", PASOS_ENLACE_GOOGLE, "PT3M")], faq)

    # ---------------- Activar NFC ----------------
    modelos = ["iPhone 7 y iPhone 7 Plus", "iPhone 8 y iPhone 8 Plus", "iPhone X, iPhone XS y iPhone XS Max", "iPhone XR, iPhone 11, iPhone 11 Pro y iPhone 11 Pro Max",
               "iPhone 12, iPhone 12 mini, iPhone 12 Pro y iPhone 12 Pro Max", "iPhone 13, iPhone 13 mini, iPhone 13 Pro y iPhone 13 Pro Max",
               "iPhone 14, iPhone 14 Plus, iPhone 14 Pro y iPhone 14 Pro Max", "iPhone 15, iPhone 15 Plus, iPhone 15 Pro y iPhone 15 Pro Max",
               "iPhone SE (2.ª y 3.ª generación)", "Y todos los modelos posteriores"]
    cuerpo = (
        caja(icono("celular"), "Antes de empezar", (
            '<div class="caja__cuerpo"><ul>'
            '<li><b>Lector NFC y compatibilidad:</b> asegúrate de que tu celular sea compatible con NFC y ubica dónde está su lector.</li>'
            '<li><b>Estado de la pantalla:</b> la pantalla debe estar encendida y desbloqueada mientras usas el celular. Si no, es posible que no lea la etiqueta NFC ni reciba la información.</li>'
            '</ul><p>Con esto listo, podrás aprovechar al máximo tu tarjeta TarjetasNFC. A continuación te explicamos cómo activar o encontrar el NFC en tu celular si hace falta.</p></div>'),
            ident="antes-de-empezar")
        + caja('<svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.2 1-4 2.4-1.7 3-.4 7.4 1.2 9.8.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8-.1 0-2.5-1-2.5-3.9zM14 5.5c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1.1.1 2.1-.6 2.8-1.4z"/></svg>',
               "Compatibilidad NFC en iPhone", (
            '<div class="caja__cuerpo"><p>Todos los iPhone necesitan <b>iOS 13 o posterior</b> para ser compatibles con NFC. Estos son los iPhone compatibles:</p>'
            '<ul class="modelos">%s</ul>'
            '<p>En el iPhone, el lector NFC está en la parte superior del equipo: acerca la tarjeta a la parte de arriba del celular para activarla.</p>'
            '<p>Del iPhone XS en adelante la lectura es automática con la pantalla encendida. En iPhone 7, 8 y X abre el Centro de control y toca «Lector de etiquetas NFC».</p></div>'
            % "".join("<li>%s</li>" % m for m in modelos)), ident="iphone")
        + caja('<svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.6 9.5 19.4 6.4a.4.4 0 0 0-.7-.4l-1.8 3.1A11 11 0 0 0 12 8a11 11 0 0 0-4.9 1.1L5.3 6a.4.4 0 0 0-.7.4l1.8 3.1A10.4 10.4 0 0 0 1 18h22a10.4 10.4 0 0 0-5.4-8.5zM7 15.3a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm10 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>',
               "Cómo activar el NFC en Android", pasos_num("android", PASOS_NFC_ANDROID),
               "Sigue estos pasos para encender el NFC en tu celular Android.", ident="android")
        + caja(icono("rayo"), "Consejos para usuarios de Android", (
            '<div class="caja__cuerpo"><ul>'
            '<li>Asegúrate de que la pantalla de tu celular esté encendida y desbloqueada.</li>'
            '<li>Prueba sostener el celular de diferentes formas: la antena NFC puede estar en la parte superior o en el centro del equipo.</li>'
            '<li>Acerca más el celular a la tarjeta.</li>'
            '<li>Si es necesario, mantén el celular junto a la tarjeta unos segundos más.</li>'
            '</ul><p>Para instrucciones específicas de tu modelo, consulta la página de soporte del fabricante de tu celular (Samsung, Motorola, Xiaomi, OPPO, Huawei, etc.).</p>'
            '<p>Siguiendo estos pasos podrás activar o encontrar fácilmente el NFC en tu celular y disfrutar de una experiencia sin complicaciones con nuestras tarjetas NFC de reseñas.</p></div>'),
            ident="consejos")
    )
    faq = [
        ("¿Cómo sé si mi celular tiene NFC?", "En Android, busca «NFC» en los ajustes: si aparece la opción, tu celular lo tiene. Todos los iPhone desde el iPhone 7 incluyen NFC."),
        ("¿Tengo que activar el NFC en iPhone?", "No. En iPhone el NFC viene activado siempre; solo acerca la parte superior del celular a la tarjeta con la pantalla encendida."),
        ("¿La tarjeta NFC necesita batería?", "No. La tarjeta toma la energía del celular en el momento en que lo acercas, así que no necesita batería ni carga."),
        ("¿Qué hago si mi celular no tiene NFC?", "Escanea el código QR impreso en la tarjeta con la cámara de tu celular y se abrirá el mismo enlace."),
    ]
    pagina_ayuda(
        "como-activar-nfc-celular.html", "Cómo Activar el NFC en tu Celular iPhone o Android | Guía",
        "Aprende a activar el NFC en tu iPhone o Android, revisa los modelos compatibles y sigue nuestros consejos para leer tu tarjeta NFC al primer toque.",
        ["cómo activar nfc", "activar nfc android", "nfc iphone", "dónde está el nfc en mi celular", "cómo saber si mi celular tiene nfc",
         "iphone compatibles con nfc", "lector nfc iphone", "activar nfc samsung", "activar nfc motorola", "activar nfc xiaomi",
         "qué es nfc en el celular", "tarjeta nfc no funciona", "cómo leer una tarjeta nfc"],
        "Guía de compatibilidad", "Cómo activar o encontrar el NFC en tu celular",
        "Algunos celulares no traen el NFC activado de fábrica. Esta guía te ayuda a activarlo rápidamente, sobre todo si usas Android; en iPhone normalmente viene activado desde el inicio.",
        cuerpo, [nodo_howto("como-activar-nfc-celular.html", "android", "Cómo activar el NFC en un celular Android",
                            "Pasos para encender el NFC en Android y leer una tarjeta NFC.", PASOS_NFC_ANDROID, "PT1M")], faq)

    # ---------------- Envíos y devoluciones ----------------
    cuerpo = (
        caja(icono("caja"), "Procesamiento y envío de pedidos", (
            '<div class="caja__cuerpo"><p>Los pedidos confirmados antes de las <b>11:00 a.m. (hora del centro de México)</b> en días hábiles se procesan y envían el mismo día, sujeto a disponibilidad.</p>'
            '<p>Aunque buscamos enviar lo antes posible, en temporadas de alta demanda el procesamiento puede tomar <b>1 a 2 días hábiles</b> adicionales, ya que cada tarjeta se personaliza.</p></div>'),
            "En TarjetasNFC nos comprometemos a que tu envío sea fácil y confiable. Esto es todo lo que necesitas saber.", ident="procesamiento")
        + caja(icono("camion"), "Métodos y tiempos de envío", (
            '<div class="caja__cuerpo"><p>Trabajamos con paqueterías confiables para que tu pedido llegue de forma segura y eficiente.</p><ul>'
            '<li><b>Envío gratis</b> a toda la República Mexicana en todos los pedidos.</li>'
            '<li>Los envíos suelen tardar de <b>3 a 5 días hábiles</b>.</li>'
            '<li>Solo realizamos envíos dentro de México; <b>no hacemos envíos internacionales</b>.</li></ul></div>'), ident="envios")
        + caja(icono("mexico"), "Exactitud de la dirección", (
            '<div class="caja__cuerpo"><p>Es indispensable que los datos de envío que nos compartas al confirmar tu pedido sean correctos y completos. '
            'No nos hacemos responsables por retrasos o pedidos no entregados a causa de direcciones incorrectas o incompletas.</p></div>'), ident="direccion")
        + caja(icono("escudo"), "Artículos faltantes o dañados", (
            '<div class="caja__cuerpo"><p>Si tu pedido llega con artículos faltantes o dañados, contacta a nuestro equipo de atención a clientes '
            '<b>dentro de las 48 horas</b> siguientes a recibir el paquete. Revisaremos tu caso y te daremos una solución adecuada.</p></div>'), ident="danados")
        + caja(icono("tag"), "Devoluciones y reembolsos", (
            '<div class="caja__cuerpo"><p>Como cada tarjeta se fabrica y programa a la medida de tu negocio, <b>no aceptamos devoluciones ni reembolsos</b>. '
            'Si tu pedido llegó dañado o incompleto, sigue el proceso de artículos faltantes o dañados.</p></div>'), ident="devoluciones")
        + caja(icono("correo"), "Contacto", (
            '<div class="caja__cuerpo"><p>Si tienes dudas sobre nuestra política de envíos, escríbenos a <a href="mailto:%s">%s</a> o llámanos al <a href="tel:%s">%s</a>.</p>'
            '<p>En TarjetasNFC nos dedicamos a ofrecerte una experiencia de envío fácil y eficiente. Gracias por elegirnos para tus soluciones de reseñas.</p></div>'
            % (CORREO, CORREO, TELEFONO_E164, TELEFONO)), ident="contacto-envios")
    )
    faq = [
        ("¿Cuánto cuesta el envío?", "Nada. El envío es gratis a cualquier parte de la República Mexicana y ya está incluido en el precio."),
        ("¿Cuánto tarda en llegar mi pedido?", "Los envíos suelen tardar de 3 a 5 días hábiles. Los pedidos confirmados antes de las 11:00 a.m. (hora del centro de México) en días hábiles salen el mismo día."),
        ("¿Hacen envíos internacionales?", "No. Por ahora solo enviamos dentro de México."),
        ("¿Aceptan devoluciones?", "No, porque cada tarjeta se personaliza para tu negocio. Si tu pedido llega dañado o incompleto, avísanos dentro de las 48 horas siguientes y te daremos una solución."),
    ]
    pagina_ayuda(
        "envios-y-devoluciones.html", "Envíos y Devoluciones | Envío Gratis a Todo México",
        "Envío gratis a todo México en 3 a 5 días hábiles. Conoce los tiempos de procesamiento, qué hacer si tu pedido llega dañado y la política de devoluciones.",
        ["envío gratis méxico", "envíos tarjetas nfc", "política de envíos", "política de devoluciones", "tiempo de entrega tarjetas nfc",
         "envío a toda la república mexicana", "tarjetas nfc envío gratis", "devoluciones tarjetas nfc"],
        "Política de envíos", "Envíos y devoluciones",
        "Enviamos gratis a toda la República Mexicana. Aquí encuentras cómo procesamos tu pedido, cuánto tarda en llegar y qué hacer si algo sale mal.",
        cuerpo, [], faq)

    # ---------------- Contacto ----------------
    cuerpo = '<div class="contacto">' + caja(icono("mensaje"), "Envíanos un mensaje", (
        '<form class="formulario" id="form-contacto" novalidate>'
        '<div class="formulario__fila"><div><label for="c-nombre">Nombre</label><input class="input" id="c-nombre" name="nombre" type="text" autocomplete="name" required></div>'
        '<div><label for="c-email">Email</label><input class="input" id="c-email" name="email" type="email" autocomplete="email" required></div></div>'
        '<div><label for="c-telefono">Número de teléfono <span style="font-weight:400;color:var(--texto-suave)">(opcional)</span></label>'
        '<input class="input" id="c-telefono" name="telefono" type="tel" autocomplete="tel" inputmode="tel"></div>'
        '<div><label for="c-comentario">Comentario</label><textarea class="input" id="c-comentario" name="comentario" required></textarea></div>'
        '<div class="formulario__acciones"><button class="btn btn--primario" type="submit">%s Enviar mensaje</button>'
        '<button class="btn-texto" type="button" id="btn-correo">o envíalo por correo</button></div>'
        '<p class="caja__nota" style="margin:0">Al enviar, se abrirá WhatsApp (o tu correo) con tu mensaje listo para mandar.</p>'
        '</form>' % WA_SVG), "Llena el formulario y nuestro equipo te responderá lo antes posible.", ident="formulario") + caja(
        icono("telefono"), "Ponte en contacto con nosotros", (
            '<div class="datos-contacto">'
            '<a href="tel:%s">%s<div><span>Teléfono</span>%s</div></a>'
            '<a href="mailto:%s">%s<div><span>Email</span>%s</div></a>'
            '<a href="https://wa.me/%s" target="_blank" rel="noopener">%s<div><span>WhatsApp</span>Escríbenos ahora</div></a>'
            '</div>' % (TELEFONO_E164, icono("telefono"), TELEFONO, CORREO, icono("correo"), CORREO, WHATSAPP, icono("mensaje"))),
        "¿Tienes dudas o necesitas ayuda? Escríbenos o llámanos y te ayudamos con tu consulta.", ident="datos") + '</div>'
    pagina_ayuda(
        "contacto.html", "Contacto | TarjetasNFC México – Tarjetas NFC para Reseñas",
        "¿Dudas sobre tarjetas NFC o tu pedido? Escríbenos por WhatsApp, llámanos al %s o envía un correo a %s." % (TELEFONO, CORREO),
        ["contacto tarjetasnfc", "tarjetas nfc méxico contacto", "comprar tarjetas nfc whatsapp", "atención a clientes tarjetas nfc",
         "cotizar tarjetas nfc", "tarjetas nfc mayoreo", "tarjetas nfc tijuana"],
        "Contacto", "Estamos aquí para ayudarte",
        "¿Tienes preguntas o necesitas ayuda? Ya sea que busques más información sobre nuestros productos o apoyo con tu pedido, nuestro equipo está listo para ayudarte. Escríbenos y te responderemos lo antes posible.",
        cuerpo, [], None, tipo="ContactPage", mas_ayuda=False)


# --------------------------------------------------------------------------
def cargar_fechas():
    if os.path.exists(ARCHIVO_FECHAS):
        with open(ARCHIVO_FECHAS, encoding="utf-8") as fh:
            FECHAS.update(json.load(fh))


def guardar_fechas():
    with open(ARCHIVO_FECHAS, "w", encoding="utf-8") as fh:
        json.dump(FECHAS, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def escribir(ruta, contenido):
    if FECHA_MOD in contenido:
        # La fecha solo avanza cuando cambia el contenido real de la página.
        huella = hashlib.sha256(contenido.encode("utf-8")).hexdigest()
        previo = FECHAS.get(ruta)
        if not previo or previo["hash"] != huella:
            FECHAS[ruta] = {"hash": huella, "fecha": HOY}
        contenido = contenido.replace(FECHA_MOD, FECHAS[ruta]["fecha"])
    destino = os.path.join(RAIZ, ruta)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(contenido)


def generar_datos_js():
    datos = [{"slug": p["slug"], "nombre": p["nombre"], "plataforma": p["plataforma"], "categoria": p["cat"],
              "categoriaNombre": NOMBRE_CAT[p["cat"]], "url": p["url"], "imagen": webp(p, 400),
              "campo": {"etiqueta": p["campo"][0]}} for p in PRODUCTOS]
    paquetes = [{k: pq[k] for k in ("tarjetas", "nombre", "precio", "antes", "unidad")} for pq in PAQUETES]
    js = ("/* Archivo generado por herramientas/generar_sitio.py — no editar a mano. */\n"
          "window.SITIO = %s;\nwindow.PAQUETES = %s;\nwindow.PRODUCTOS = %s;\n" % (
              json.dumps({"whatsapp": WHATSAPP, "correo": CORREO, "funciones": SUPABASE_URL + "/functions/v1", "anon": SUPABASE_ANON}, ensure_ascii=False),
              json.dumps(paquetes, ensure_ascii=False, indent=1),
              json.dumps(datos, ensure_ascii=False, indent=1)))
    escribir("js/productos.js", js)


def generar_gracias():
    """Página de regreso de Stripe Checkout. No se indexa ni va en el sitemap."""
    base = ""
    titulo = "Gracias por tu compra | TarjetasNFC"
    descripcion = "Confirmación de tu pedido de tarjetas NFC en TarjetasNFC. Te contactaremos por correo electrónico para preparar tu envío."
    html = head(base, titulo, descripcion, "gracias.html", "imagenes/productos/" + PRODUCTOS[0]["img"], [nodo_org(), nodo_sitio()], indexar=False)
    html += f"""
<body data-base="{base}">
{header(base, "")}
<main id="contenido">
  <section class="seccion gracias" id="pagina-gracias" data-estado="cargando">
    <div class="contenedor">
      <div class="caja gracias__caja">
        <div class="caja__icono gracias__icono" aria-hidden="true">{icono("exito", 30)}</div>
        <h1 class="caja__titulo" id="gracias-titulo">¡Gracias por tu compra!</h1>
        <p class="caja__lead" id="gracias-texto" role="status" aria-live="polite">Estamos confirmando tu pago…</p>
        <dl class="gracias__datos" id="gracias-datos" hidden>
          <div><dt>Número de pedido</dt><dd id="gracias-pedido"></dd></div>
          <div><dt>Total</dt><dd id="gracias-total"></dd></div>
          <div><dt>Te escribiremos a</dt><dd id="gracias-correo"></dd></div>
        </dl>
        <ol class="gracias__pasos">
          <li>{icono("correo", 22)}<span>Te contactamos por <b>correo electrónico</b> para confirmar los detalles de tu tarjeta.</span></li>
          <li>{icono("nfc", 22)}<span>Programamos el chip NFC y el código QR con el enlace que nos diste.</span></li>
          <li>{icono("camion", 22)}<span>Enviamos gratis tu pedido; llega en <b>3 a 5 días hábiles</b>.</span></li>
        </ol>
        <div class="caja__botones">
          <a class="btn btn--primario" href="index.html#catalogo">Seguir comprando {icono("der", 18)}</a>
          <a class="btn btn--contorno" href="contacto.html">Contáctanos</a>
        </div>
        <p class="caja__nota">¿Dudas con tu pedido? Escríbenos a <a href="mailto:{CORREO}">{CORREO}</a> o al <a href="tel:{TELEFONO_E164}">{TELEFONO}</a>.</p>
      </div>
    </div>
  </section>
</main>
{pie(base)}
{carrito_y_scripts(base)}"""
    escribir("gracias.html", html)


def generar_manifest():
    escribir("site.webmanifest", json.dumps({
        "name": "TarjetasNFC México", "short_name": MARCA, "lang": "es-MX", "start_url": "/", "scope": "/", "display": "standalone",
        "description": "Tarjetas NFC con código QR para reseñas de Google y redes sociales. Envío gratis a todo México.",
        "background_color": "#ffffff", "theme_color": "#1d5ff0",
        "icons": [{"src": "/imagenes/favicon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/imagenes/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}],
    }, ensure_ascii=False, indent=2) + "\n")


IMAGENES_AYUDA = {"como-funciona.html": [VIDEO_GOOGLE["poster"]]}

XSL_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="es-MX"><head><meta charset="utf-8"/><meta name="robots" content="noindex"/><title>Mapa del sitio · TarjetasNFC</title>
<style>body{font-family:Poppins,system-ui,sans-serif;margin:0;padding:32px 16px;color:#0b1325;background:#f5f6f8}main{max-width:1100px;margin:0 auto}
h1{font-size:1.6rem}p{color:#5b6475}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e3e6ec;border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid #e3e6ec;font-size:.9rem}th{background:#1d5ff0;color:#fff}a{color:#1d5ff0}</style></head>
<body><main><h1>Mapa del sitio de TarjetasNFC</h1><p>Este archivo XML es para buscadores como Google y Bing.</p>
<xsl:choose>
<xsl:when test="s:sitemapindex"><table><tr><th>Sitemap</th><th>Última modificación</th></tr>
<xsl:for-each select="s:sitemapindex/s:sitemap"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td></tr></xsl:for-each></table></xsl:when>
<xsl:otherwise><table><tr><th>URL</th><th>Imágenes</th><th>Videos</th><th>Última modificación</th></tr>
<xsl:for-each select="s:urlset/s:url"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="count(image:image)"/></td>
<td><xsl:value-of select="count(video:video)"/></td><td><xsl:value-of select="s:lastmod"/></td></tr></xsl:for-each></table></xsl:otherwise>
</xsl:choose></main></body></html>
</xsl:template></xsl:stylesheet>
"""


def generar_sitemap_robots():
    """sitemap.xml (índice) -> sitemap-paginas.xml, sitemap-productos.xml y sitemap-videos.xml."""
    def fecha(ruta):
        return FECHAS.get(ruta or "index.html", {}).get("fecha", HOY)

    def url_xml(ruta, frecuencia, prioridad, imagenes=(), video=None):
        loc = DOMINIO + "/" + ruta
        partes = ["  <url>", "    <loc>%s</loc>" % loc,
                  '    <xhtml:link rel="alternate" hreflang="es-MX" href="%s"/>' % loc,
                  '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % loc,
                  "    <lastmod>%s</lastmod>" % fecha(ruta), "    <changefreq>%s</changefreq>" % frecuencia, "    <priority>%s</priority>" % prioridad]
        for img in imagenes:
            partes.append("    <image:image><image:loc>%s/%s</image:loc></image:image>" % (DOMINIO, img))
        if video:
            partes += ["    <video:video>",
                       "      <video:thumbnail_loc>%s/%s</video:thumbnail_loc>" % (DOMINIO, video["poster"]),
                       "      <video:title>%s</video:title>" % escape(video["nombre"]),
                       "      <video:description>%s</video:description>" % escape(video["desc"]),
                       "      <video:content_loc>%s/%s</video:content_loc>" % (DOMINIO, video["src"]),
                       "      <video:duration>18</video:duration>",
                       "      <video:publication_date>%sT12:00:00-06:00</video:publication_date>" % PUBLICADO,
                       "      <video:family_friendly>yes</video:family_friendly>",
                       "      <video:requires_subscription>no</video:requires_subscription>",
                       "      <video:live>no</video:live>",
                       '      <video:uploader info="%s/">%s</video:uploader>' % (DOMINIO, MARCA),
                       "      <video:tag>tarjeta nfc</video:tag>", "      <video:tag>reseñas de google</video:tag>", "      <video:tag>código qr</video:tag>",
                       "    </video:video>"]
        partes.append("  </url>")
        return "\n".join(partes)

    cabecera = ('<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"\n'
                '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n')
    hijos = {
        "sitemap-paginas.xml": [url_xml("", "daily", "1.0", [webp(p, 1200) for p in PRODUCTOS])]
                               + [url_xml(a, "monthly", "0.6", IMAGENES_AYUDA.get(a, ())) for a, _ in AYUDA],
        "sitemap-productos.xml": [url_xml(p["url"], "weekly", "0.9", [webp(p, 1200)] + ([p["video"]["poster"]] if p.get("video") else []))
                                  for p in PRODUCTOS],
        "sitemap-videos.xml": [url_xml(p["url"], "weekly", "0.9", (), p["video"]) for p in PRODUCTOS if p.get("video")]
                              + [url_xml("como-funciona.html", "monthly", "0.6", (), VIDEO_GOOGLE)],
    }
    rutas_hijo = {"sitemap-paginas.xml": [""] + [a for a, _ in AYUDA], "sitemap-productos.xml": [p["url"] for p in PRODUCTOS],
                  "sitemap-videos.xml": [p["url"] for p in PRODUCTOS if p.get("video")] + ["como-funciona.html"]}
    for nombre, urls in hijos.items():
        escribir(nombre, cabecera + "\n".join(urls) + "\n</urlset>\n")
    indice = ['<?xml version="1.0" encoding="UTF-8"?>', '<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>',
              '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for nombre in hijos:
        indice.append("  <sitemap>\n    <loc>%s/%s</loc>\n    <lastmod>%s</lastmod>\n  </sitemap>"
                      % (DOMINIO, nombre, max(fecha(x) for x in rutas_hijo[nombre])))
    indice.append("</sitemapindex>\n")
    escribir("sitemap.xml", "\n".join(indice))
    escribir("sitemap.xsl", XSL_SITEMAP)
    escribir("robots.txt", "# tarjetasnfc.com.mx\nUser-agent: *\nAllow: /\nDisallow: /herramientas/\n\n"
                           "Sitemap: %s/sitemap.xml\n" % DOMINIO)


if __name__ == "__main__":
    cargar_fechas()
    generar_webp()
    generar_datos_js()
    generar_index()
    for prod in PRODUCTOS:
        generar_producto(prod)
    generar_ayuda()
    generar_gracias()
    generar_manifest()
    generar_sitemap_robots()
    guardar_fechas()
    print("Sitio generado: index.html + %d productos + %d páginas de ayuda" % (len(PRODUCTOS), len(AYUDA)))
