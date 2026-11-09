"""Contenido único de cada página de producto (guía, pasos, colocación, consejos y FAQ).

Cada entrada se muestra debajo de la ficha de compra en productos/<slug>.html y alimenta
los datos estructurados (FAQPage y HowTo). Los textos admiten HTML en línea sencillo
(<strong>, <em>, <a>); los enlaces son relativos a la carpeta productos/.

Claves:
  titulo_seo / desc_seo  -> <title> y meta description propios (máx. ~60 y ~155 caracteres)
  h2                      -> título de la guía
  intro                   -> párrafos de introducción
  beneficios              -> [(título, texto)]
  enlace                  -> {"titulo", "lead", "pasos": [(título, texto)], "nota"}
  donde                   -> [(lugar, por qué)]
  consejos                -> [texto]
  faq                     -> [(pregunta, respuesta)]  (respuestas en texto plano)
  blog                    -> slugs de artículos relacionados (opcional)
"""

GUIAS = {
    # ------------------------------------------------------------------ GOOGLE
    "tarjeta-nfc-resenas-google": {
        "titulo_seo": "Tarjeta NFC para Reseñas de Google con QR | México",
        "desc_seo": "Tarjeta NFC con código QR que abre la ventana de reseñas de Google de tu negocio en un toque. Más estrellas en Google Maps. Pago único y envío gratis.",
        "h2": "Tarjeta NFC para reseñas de Google: la forma más rápida de juntar estrellas",
        "intro": [
            "Casi todos tus clientes nuevos te van a buscar en Google antes de visitarte. Según la <a href=\"https://www.brightlocal.com/research/local-consumer-review-survey/\" target=\"_blank\" rel=\"noopener\">encuesta 2026 de BrightLocal</a>, el <strong>97%</strong> de los consumidores lee reseñas de negocios locales, el <strong>47%</strong> no usaría un negocio con menos de 20 reseñas y el <strong>74%</strong> busca opiniones de los últimos tres meses. Es decir: no basta con tener buenas reseñas, necesitas reseñas <em>constantes</em>.",
            "El problema casi nunca es que el cliente no quiera opinar: es que le da flojera buscar tu negocio, encontrar el botón y escribir. La tarjeta NFC para reseñas de Google elimina esos pasos. El cliente acerca su celular y se abre directo la ventana para calificarte con estrellas. Si su teléfono no tiene NFC, escanea el código QR impreso y llega al mismo lugar.",
        ],
        "beneficios": [
            ("Mejor posición en Google Maps", "Google indica en su <a href=\"https://support.google.com/business/answer/7091?hl=es\" target=\"_blank\" rel=\"noopener\">ayuda oficial</a> que la cantidad de reseñas y las valoraciones positivas influyen en la prominencia, uno de los tres factores del ranking local."),
            ("Reseñas recientes todo el año", "Al estar siempre a la vista en tu mostrador, la invitación se repite con cada cliente, no solo cuando te acuerdas de pedirla."),
            ("Cumple las reglas de Google", "La tarjeta abre el enlace oficial de reseñas. No filtra clientes ni ofrece incentivos: el cliente decide cuántas estrellas da y qué escribe."),
            ("Un enlace por sucursal", "Si tienes varias ubicaciones, programamos cada tarjeta con el enlace de su sucursal para que las reseñas lleguen al perfil correcto."),
        ],
        "enlace": {
            "titulo": "Cómo obtener el enlace de reseñas de tu Perfil de Empresa",
            "lead": "Lo necesitas al hacer tu pedido. Es gratis y toma un par de minutos:",
            "pasos": [
                ("Abre tu Perfil de Empresa", "Busca el nombre de tu negocio en Google con la cuenta que lo administra. Verás el panel de edición del perfil."),
                ("Elige «Pedir reseñas»", "En el panel toca «Pedir reseñas» (puede aparecer como «Obtener más reseñas»). Google genera un enlace corto."),
                ("Copia el enlace", "Normalmente empieza con https://g.page/r/. Cópialo completo."),
                ("Pégalo al comprar", "Pégalo en el campo «Enlace de reseñas de Google» de esta página. Si no lo encuentras, escríbenos y te ayudamos con el nombre y la dirección de tu negocio."),
            ],
            "nota": "¿Prefieres una guía con más detalle? Lee <a href=\"../como-encontrar-enlace-resenas-google.html\">cómo encontrar tu enlace de reseñas de Google</a>.",
        },
        "donde": [
            ("En la caja o mostrador", "Es el último punto de contacto: el cliente ya pagó y tiene el celular en la mano."),
            ("En la carpeta de la cuenta", "En restaurantes, es el momento de mayor satisfacción después de comer."),
            ("En la mesa o la recepción", "Con un portatarjetas a la vista, la invitación trabaja sola mientras el cliente espera."),
            ("En manos de tu equipo", "Meseros, estilistas o técnicos pueden mostrarla al terminar el servicio con una frase amable."),
        ],
        "consejos": [
            "Acompaña la tarjeta con una frase corta: «¿Te gustó? Acerca tu celular y califícanos».",
            "Pide la reseña a <strong>todos</strong> tus clientes, no solo a los que se ven contentos: elegir a quién pedírsela va contra las políticas de Google.",
            "Responde cada reseña, buena o mala. El 89% de los consumidores espera que el dueño responda (BrightLocal 2026).",
            "Cuenta tus reseñas cada lunes. En pocas semanas vas a ver la diferencia entre antes y después de colocar la tarjeta.",
            "Nunca ofrezcas descuentos o regalos a cambio de reseñas: Google lo considera participación falsa.",
        ],
        "faq": [
            ("¿La tarjeta deja la reseña de forma automática?", "No. La tarjeta solo abre la ventana oficial para calificar tu negocio en Google. El cliente elige las estrellas y escribe su comentario, por eso las reseñas son reales y cumplen las políticas de Google."),
            ("¿Mi cliente necesita cuenta de Google para dejar la reseña?", "Sí, Google pide iniciar sesión para publicar. La mayoría de los usuarios de Android y Gmail ya tienen una cuenta, así que en la práctica casi nadie tiene que registrarse."),
            ("¿Cuántas reseñas puedo conseguir con la tarjeta?", "Depende del flujo de clientes y de qué tan visible esté. Lo que sí cambia es la constancia: en lugar de depender de que el cliente se acuerde, la invitación está ahí en cada visita."),
            ("¿Funciona si tengo varias sucursales?", "Sí. Cada sucursal tiene su propio Perfil de Empresa y su enlace. Al comprar, escribe los enlaces separados por coma y configuramos cada tarjeta con el correcto."),
            ("¿Esto viola las políticas de Google?", "No. Google permite y recomienda pedir reseñas a tus clientes. Lo que prohíbe es ofrecer incentivos, pedirlas solo a clientes satisfechos o publicar reseñas falsas. La tarjeta solo facilita el acceso al enlace oficial."),
        ],
        "blog": ["como-conseguir-mas-resenas-en-google", "como-aparecer-en-google-maps", "estadisticas-de-resenas-en-linea-2026"],
    },

    # --------------------------------------------------------------- INSTAGRAM
    "tarjeta-nfc-instagram": {
        "titulo_seo": "Tarjeta NFC para Instagram con QR | Gana Seguidores",
        "desc_seo": "Tarjeta NFC con código QR que abre tu perfil de Instagram en un toque para que tus clientes te sigan al instante. Pago único y envío gratis a todo México.",
        "h2": "Tarjeta NFC para Instagram: convierte clientes en seguidores",
        "intro": [
            "Tus mejores seguidores potenciales no están en un anuncio: ya están en tu local. Probaron tu producto, conocieron tu servicio y les gustó. El reto es que te sigan antes de irse, y para eso hay que quitar los obstáculos: deletrear tu usuario, buscarlo entre cuentas parecidas, encontrar el botón correcto.",
            "La tarjeta NFC para Instagram hace todo eso en un segundo. El cliente acerca su celular y se abre tu perfil en la app de Instagram, listo para tocar «Seguir». Si su teléfono no tiene NFC, el código QR impreso lleva al mismo perfil.",
        ],
        "beneficios": [
            ("Seguidores reales y locales", "Quien te sigue desde tu mostrador vive cerca y ya te compró: es la audiencia que más vale para un negocio local."),
            ("Sin errores de usuario", "Nada de «¿es con guion bajo o con punto?». La tarjeta abre exactamente tu cuenta."),
            ("Más alcance para tus publicaciones", "Más seguidores que interactúan hacen que tu contenido llegue a más personas de tu zona."),
            ("Funciona para cuentas personales y de empresa", "Sirve para tu negocio, tu marca personal o tu portafolio como creador."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu perfil de Instagram",
            "lead": "Tu enlace siempre tiene la forma https://www.instagram.com/tuusuario. Para copiarlo desde la app:",
            "pasos": [
                ("Abre tu perfil", "Entra a Instagram y toca tu foto en la esquina inferior derecha."),
                ("Toca «Compartir perfil»", "Aparece debajo de tu biografía, junto a «Editar perfil»."),
                ("Elige «Copiar enlace»", "El enlace de tu perfil queda copiado en el portapapeles."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página. También puedes escribir solo tu usuario y nosotros armamos el enlace."),
            ],
            "nota": "Si cambias tu nombre de usuario, el enlace anterior deja de funcionar. Elige un usuario definitivo antes de pedir tus tarjetas.",
        },
        "donde": [
            ("Junto a la caja", "El cliente espera su cambio o su ticket: el momento perfecto para seguirte."),
            ("En el probador o el espejo", "En boutiques y barberías, justo cuando el cliente se ve bien y quiere compartirlo."),
            ("En tu stand de expo o bazar", "Los visitantes te siguen en un toque y te recuerdan después del evento."),
            ("En empaques y pedidos", "Dentro de la bolsa o caja, para que te sigan al abrir su compra."),
        ],
        "consejos": [
            "Dales un motivo para seguirte: «Síguenos para ver los nuevos modelos antes que nadie».",
            "Antes de colocar la tarjeta, revisa tu perfil: foto clara, biografía con tu ciudad y un enlace a tu acción principal (WhatsApp, menú o tienda).",
            "Publica contenido que solo tú puedes mostrar: el proceso, tu equipo y clientes reales (con su permiso).",
            "No compres seguidores: no compran ni interactúan y bajan el alcance de tu cuenta.",
        ],
        "faq": [
            ("¿Se abre la app de Instagram o el navegador?", "Si el cliente tiene la app instalada, el celular normalmente abre el perfil directamente en Instagram. Si no la tiene, se abre la versión web, donde también puede seguirte."),
            ("¿Sirve para una cuenta privada?", "Sí, la tarjeta abre tu perfil. En una cuenta privada el cliente enviará una solicitud de seguimiento que tú apruebas, como siempre."),
            ("¿Puedo poner mi Instagram y mi TikTok en la misma tarjeta?", "Cada tarjeta abre un solo enlace para que el mensaje sea claro. Si quieres ambas redes, te conviene una tarjeta para cada una; puedes combinarlas en el mismo pedido."),
            ("¿Qué pasa si cambio mi usuario de Instagram?", "El enlace configurado apuntará al usuario anterior y dejará de funcionar. Escríbenos antes de cambiarlo para revisar tu caso."),
        ],
        "blog": ["como-conseguir-seguidores-instagram-negocio-local", "tarjetas-nfc-para-esteticas-barberias-consultorios"],
    },

    # ---------------------------------------------------------------- FACEBOOK
    "tarjeta-nfc-facebook": {
        "titulo_seo": "Tarjeta NFC para Facebook con QR | Seguidores y Likes",
        "desc_seo": "Tarjeta NFC con código QR que abre la página de Facebook de tu negocio para ganar seguidores y recomendaciones en un toque. Envío gratis en México.",
        "h2": "Tarjeta NFC para Facebook: más seguidores y recomendaciones para tu página",
        "intro": [
            "En México, Facebook sigue siendo uno de los lugares donde más personas buscan y recomiendan negocios locales: la fonda de confianza, el taller del barrio, el gimnasio de la colonia. En la encuesta 2026 de BrightLocal, Facebook y Google aparecen como las fuentes más comunes de recomendaciones locales.",
            "La tarjeta NFC para Facebook lleva a tus clientes directo a tu página para que te sigan, le den me gusta y, si quieren, te dejen una recomendación. Un toque con el celular o un escaneo del QR y listo.",
        ],
        "beneficios": [
            ("Recomendaciones visibles", "Las recomendaciones de tus clientes aparecen en tu página y ayudan a que otros confíen en ti."),
            ("Una comunidad para avisar novedades", "Promociones, horarios especiales o nuevos productos llegan a quienes ya te conocen."),
            ("Ideal para negocios de barrio", "Para muchos clientes, Facebook es la red que más usan: la tarjeta les facilita encontrarte."),
            ("Funciona con Messenger", "Desde tu página, el cliente también puede escribirte por Messenger para pedir o cotizar."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu página de Facebook",
            "lead": "El enlace de una página suele verse así: https://www.facebook.com/tunegocio.",
            "pasos": [
                ("Abre tu página", "En la app de Facebook entra a la página de tu negocio (no a tu perfil personal)."),
                ("Toca «Compartir»", "Busca el botón «Compartir» o el menú «⋯» de la página."),
                ("Elige «Copiar enlace»", "El enlace queda copiado. También puedes copiarlo de la barra de direcciones en la computadora."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página para que configuremos tu tarjeta."),
            ],
            "nota": "Si tu página tiene un nombre de usuario personalizado, el enlace es más corto y fácil de reconocer. Puedes configurarlo en los ajustes de la página.",
        },
        "donde": [
            ("En la caja", "El cliente te sigue mientras le cobras."),
            ("En la mesa o la barra", "En fondas, cafeterías y bares, mientras espera su orden."),
            ("En la recepción", "En gimnasios, escuelas y consultorios, para enterarse de avisos y horarios."),
            ("En entregas a domicilio", "Dentro del pedido, para que te recomienden y te vuelvan a llamar."),
        ],
        "consejos": [
            "Mantén tu página activa: publica al menos una vez por semana para que quien te siga vea movimiento.",
            "Completa la información: horario, teléfono, WhatsApp, dirección y menú o catálogo.",
            "Contesta los mensajes rápido; muchos clientes escriben a la página antes de visitarte.",
            "Agradece públicamente las recomendaciones: a quien la dejó le gusta y a los demás les da confianza.",
        ],
        "faq": [
            ("¿Abre mi perfil personal o la página del negocio?", "Abre exactamente el enlace que nos envíes. Te recomendamos usar la página del negocio, que es la que permite seguidores y recomendaciones."),
            ("¿El cliente necesita tener la app de Facebook?", "No es obligatorio. Si la tiene, normalmente se abre la página en la app; si no, se abre en el navegador."),
            ("¿Puedo usar la tarjeta para un grupo de Facebook?", "Sí. Envíanos el enlace del grupo y la tarjeta lo abrirá para que el cliente solicite unirse."),
            ("¿Sirve para recibir reseñas?", "Facebook usa «recomendaciones» en lugar de estrellas. La tarjeta lleva a tu página, donde el cliente puede recomendarte si esa opción está activa."),
        ],
        "blog": ["como-conseguir-seguidores-instagram-negocio-local"],
    },

    # ------------------------------------------------------------------ TIKTOK
    "tarjeta-nfc-tiktok": {
        "titulo_seo": "Tarjeta NFC para TikTok con QR | Más Seguidores",
        "desc_seo": "Tarjeta NFC con código QR que abre tu perfil de TikTok en un toque para que te sigan y vean tus videos. Para negocios y creadores. Envío gratis.",
        "h2": "Tarjeta NFC para TikTok: que te sigan antes de salir por la puerta",
        "intro": [
            "TikTok se volvió el escaparate de muchos negocios mexicanos: taquerías que se hacen virales, tiendas que venden por live y creadores que construyen comunidad con videos cortos. Pero cuando un cliente te conoce en persona, buscarte en la app con el usuario exacto es un paso que casi nadie da.",
            "La tarjeta NFC para TikTok resuelve eso: el cliente acerca su celular y se abre tu perfil listo para seguirte y ver tus videos. Con el código QR impreso funciona también en celulares sin NFC.",
        ],
        "beneficios": [
            ("Seguidores que ya te conocen", "Un seguidor que probó tu producto interactúa más con tu contenido."),
            ("Ideal para eventos y activaciones", "En bazares, ferias y conciertos, compartir tu perfil en un toque es más rápido que dictar tu usuario."),
            ("Impulsa tus lives", "Más seguidores reales significa más personas avisadas cuando entras en vivo."),
            ("Para negocios y creadores", "Funciona igual para la cuenta de tu marca o para tu perfil personal."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu perfil de TikTok",
            "lead": "Tu enlace tiene la forma https://www.tiktok.com/@tuusuario.",
            "pasos": [
                ("Abre tu perfil", "En la app de TikTok toca «Perfil» en la esquina inferior derecha."),
                ("Abre el menú de compartir", "Toca el ícono de compartir o el menú de tu perfil."),
                ("Elige «Copiar enlace»", "El enlace de tu perfil queda copiado."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página o escribe tu @usuario y lo armamos por ti."),
            ],
            "nota": "Si cambias tu @usuario, el enlace anterior deja de funcionar. Avísanos antes de hacerlo.",
        },
        "donde": [
            ("En tu stand o mesa de venta", "En bazares y expos, donde llegan muchas personas nuevas."),
            ("En la caja", "Para que el cliente te siga mientras le entregas su pedido."),
            ("En tu food truck o barra", "Mientras esperan, ven tus videos y te siguen."),
            ("En colaboraciones", "Para intercambiar perfiles con otros creadores en un toque."),
        ],
        "consejos": [
            "Pon tu mejor video fijado al inicio del perfil: es lo primero que verá quien llegue con la tarjeta.",
            "Menciona la tarjeta en tus videos: «¿Nos visitas? Acerca tu celular a la tarjeta y síguenos».",
            "Usa una biografía clara con tu ciudad y qué vendes.",
            "Combina con la tarjeta de reseñas de Google: TikTok te da alcance y Google te da confianza.",
        ],
        "faq": [
            ("¿Se abre la app de TikTok?", "Si el cliente tiene TikTok instalado, normalmente el perfil se abre en la app. Si no, se abre la versión web."),
            ("¿Puedo poner el enlace de un video en lugar del perfil?", "Sí. La tarjeta abre el enlace que nos envíes: puede ser tu perfil, un video específico o tu tienda."),
            ("¿Funciona con cuentas de empresa?", "Sí, funciona con cuentas personales, de creador y de empresa."),
            ("¿Cuántas tarjetas necesito para un evento?", "Para un stand pequeño basta con una o dos a la vista. Si tu equipo se mueve entre el público, conviene una por persona; el paquete de 5 suele ser el más práctico."),
        ],
        "blog": ["como-conseguir-seguidores-instagram-negocio-local"],
    },

    # ---------------------------------------------------------------- WHATSAPP
    "tarjeta-nfc-whatsapp": {
        "titulo_seo": "Tarjeta NFC para WhatsApp con QR | Chats al Instante",
        "desc_seo": "Tarjeta NFC con código QR que abre un chat de WhatsApp con tu negocio sin guardar el número. Para pedidos, citas y cotizaciones. Envío gratis.",
        "h2": "Tarjeta NFC para WhatsApp: tus clientes te escriben sin guardar tu número",
        "intro": [
            "En México, WhatsApp es el canal de ventas de miles de negocios: pedidos, cotizaciones, citas y atención a clientes pasan por ahí. Pero para escribirte, el cliente tiene que guardar tu número, abrir la app, buscarte y empezar la conversación. Muchos se quedan a la mitad.",
            "La tarjeta NFC para WhatsApp abre directamente un chat con tu negocio, sin guardar contactos. Usa el enlace oficial de «clic para chatear» de WhatsApp y, si quieres, puede incluir un mensaje de inicio ya escrito, como «Hola, quiero hacer un pedido».",
        ],
        "beneficios": [
            ("Más conversaciones, más ventas", "Cada paso que quitas convierte a más curiosos en clientes que te escriben."),
            ("Mensaje inicial listo", "El chat puede abrirse con un texto predefinido para que sepas de dónde viene el cliente."),
            ("Funciona con WhatsApp Business", "Combínala con tu catálogo, respuestas rápidas y mensaje de bienvenida."),
            ("Sin errores al marcar", "Nada de números mal anotados en una servilleta."),
        ],
        "enlace": {
            "titulo": "Qué datos necesitamos para tu tarjeta de WhatsApp",
            "lead": "No necesitas buscar ningún enlace: con tu número armamos el enlace oficial de WhatsApp (wa.me).",
            "pasos": [
                ("Tu número a 10 dígitos", "El número de WhatsApp de tu negocio, por ejemplo 55 1234 5678. Nosotros agregamos la clave de México (52)."),
                ("Un mensaje de inicio (opcional)", "Si quieres que el chat se abra con un texto, mándanoslo por WhatsApp después de tu compra."),
                ("Verificamos el enlace", "Antes de programar la tarjeta comprobamos que abra el chat correcto."),
                ("Recibes tu tarjeta lista", "Con NFC y código QR, configurada con tu número."),
            ],
            "nota": "El formato wa.me es el método oficial documentado por WhatsApp para iniciar un chat sin guardar el número.",
        },
        "donde": [
            ("En la caja o mostrador", "Para pedidos a domicilio y para que el cliente te vuelva a pedir."),
            ("En la recepción de tu consultorio o estética", "Para agendar la siguiente cita en el momento."),
            ("En tu vehículo o taller", "Para plomeros, electricistas y técnicos que trabajan a domicilio."),
            ("En la entrega del pedido", "Para que el cliente guarde el contacto y repita su compra."),
        ],
        "consejos": [
            "Activa WhatsApp Business: puedes configurar horario, mensaje de bienvenida, respuestas rápidas y catálogo.",
            "Usa un mensaje de inicio que identifique la tarjeta, por ejemplo «Hola, vengo de la tarjeta del mostrador».",
            "Responde rápido: un cliente que escribe y no recibe respuesta se va con la competencia.",
            "Combínala con la tarjeta de reseñas: primero atiendes por WhatsApp y al final pides la reseña.",
        ],
        "faq": [
            ("¿El cliente necesita guardar mi número?", "No. La tarjeta abre el chat directamente. Si el cliente quiere, puede guardar tu contacto después desde la conversación."),
            ("¿Funciona con WhatsApp Business?", "Sí, funciona igual con WhatsApp y con WhatsApp Business."),
            ("¿Puedo usar un número fijo?", "Sí, siempre que ese número tenga una cuenta de WhatsApp activa (WhatsApp Business permite registrar números fijos)."),
            ("¿Puedo tener varias tarjetas con números distintos?", "Sí. Escribe los números separados por coma al comprar y configuramos cada tarjeta con el suyo, por ejemplo uno por sucursal o por vendedor."),
        ],
        "blog": ["tarjetas-nfc-para-esteticas-barberias-consultorios", "tarjeta-de-presentacion-nfc-digital"],
    },

    # -------------------------------------------------------------------- WIFI
    "tarjeta-nfc-wifi": {
        "titulo_seo": "Tarjeta NFC y QR para Wi‑Fi | Sin Dictar la Contraseña",
        "desc_seo": "Tarjeta con NFC y código QR para que tus clientes se conecten a tu Wi‑Fi sin escribir la contraseña. Ideal para cafeterías, hoteles y oficinas. Envío gratis.",
        "h2": "Tarjeta NFC para Wi‑Fi: conecta a tus clientes sin dictar contraseñas",
        "intro": [
            "«¿Cuál es la clave del Wi‑Fi?» es probablemente la pregunta que más repite tu equipo. Dictar una contraseña larga, con mayúsculas y símbolos, quita tiempo y casi siempre termina en un «no me deja».",
            "La tarjeta para Wi‑Fi guarda los datos de tu red en un formato estándar. En iPhone, la cámara reconoce el código QR y ofrece «Unirse a la red»; en la mayoría de los Android, la cámara o el lector de QR del sistema hacen lo mismo, y muchos equipos Android también pueden conectarse con el toque NFC. Así nadie tiene que escribir nada.",
        ],
        "beneficios": [
            ("Menos interrupciones para tu equipo", "El cliente se conecta solo, sin preguntar."),
            ("Contraseñas seguras sin sufrir", "Puedes usar una clave larga y compleja porque nadie tiene que teclearla."),
            ("Mejor experiencia", "En cafeterías y coworkings, el Wi‑Fi es parte del servicio que el cliente califica."),
            ("Combínala con reseñas", "Un cliente conectado tiene más facilidad para dejarte una reseña en Google."),
        ],
        "enlace": {
            "titulo": "Qué datos necesitamos para tu tarjeta de Wi‑Fi",
            "lead": "No compartas tu contraseña en el formulario público: te la pedimos por WhatsApp de forma privada.",
            "pasos": [
                ("Nombre de la red (SSID)", "Escríbelo exactamente igual, respetando mayúsculas, espacios y guiones."),
                ("Tipo de seguridad", "Casi siempre es WPA2 o WPA3. Lo ves en la configuración de tu módem o router."),
                ("Contraseña por WhatsApp", "Después de tu compra te escribimos para pedirla de forma privada."),
                ("Probamos antes de enviar", "Verificamos que el código conecte a la red con los datos que nos diste."),
            ],
            "nota": "Recomendación de seguridad: crea una red de invitados separada de la red donde están tu caja, tu terminal y tus computadoras, y programa la tarjeta con esa red.",
        },
        "donde": [
            ("En cada mesa", "En cafeterías y restaurantes, en un portatarjetas junto al menú."),
            ("En la habitación", "En hoteles y rentas vacacionales, junto a la TV o el escritorio."),
            ("En la sala de espera", "En consultorios, talleres y oficinas."),
            ("En la recepción del coworking", "Para visitantes y miembros nuevos."),
        ],
        "consejos": [
            "Usa una red de invitados y una contraseña distinta a la de tu operación.",
            "Si cambias la contraseña, la tarjeta deja de conectar: planea los cambios y pide tarjetas nuevas cuando lo hagas.",
            "Pon el nombre de la red visible en la tarjeta o junto a ella, por si alguien prefiere conectarse a mano.",
            "Coloca la tarjeta de reseñas de Google junto a la del Wi‑Fi: es el combo más usado en cafeterías.",
        ],
        "faq": [
            ("¿Funciona en iPhone?", "Sí. La cámara del iPhone reconoce el código QR de Wi‑Fi y muestra la opción para unirse a la red. Es la forma más directa en iPhone."),
            ("¿Funciona en Android?", "Sí. Desde Android 10 la cámara o el lector de QR del sistema reconocen el código de Wi‑Fi, y en muchos equipos basta con acercar el celular a la tarjeta (NFC)."),
            ("¿Qué pasa si cambio la contraseña?", "La tarjeta guarda la contraseña que tenía la red al configurarla. Si la cambias, deja de conectar y necesitas una tarjeta nueva."),
            ("¿Es seguro?", "Es tan seguro como dar la contraseña, pero más cómodo. La clave de la seguridad es que los clientes usen una red de invitados separada de la de tu negocio."),
        ],
        "blog": ["como-compartir-wifi-con-clientes", "tarjetas-nfc-para-restaurantes", "tarjetas-nfc-para-hoteles-y-airbnb"],
    },

    # ------------------------------------------------------------- TRIPADVISOR
    "tarjeta-nfc-resenas-tripadvisor": {
        "titulo_seo": "Tarjeta NFC para Reseñas de TripAdvisor con QR | MX",
        "desc_seo": "Tarjeta NFC con código QR que lleva a tus huéspedes y comensales a tu ficha de TripAdvisor para dejar su opinión. Ideal para turismo. Envío gratis a México.",
        "h2": "Tarjeta NFC para TripAdvisor: más opiniones de viajeros",
        "intro": [
            "En destinos turísticos como Cancún, Tulum, Oaxaca, San Miguel de Allende o Los Cabos, muchos viajeros eligen dónde comer, dormir y qué tour tomar consultando TripAdvisor. Tu posición en el listado de tu destino depende en buena parte de la cantidad, la calidad y lo recientes que sean tus opiniones.",
            "El reto con los turistas es el tiempo: se van en unos días y, de regreso en casa, olvidan opinar. La tarjeta NFC para TripAdvisor lleva al viajero a tu ficha justo al final de la experiencia, cuando todavía está emocionado.",
        ],
        "beneficios": [
            ("Opiniones en el momento justo", "Al terminar la cena, el tour o la estancia, antes de que el viajero se vaya."),
            ("Funciona con viajeros extranjeros", "NFC y QR son universales: no importa de qué país sea el celular."),
            ("Mejor posición en tu destino", "Más opiniones recientes te ayudan a destacar frente a la competencia de la zona."),
            ("Una tarjeta por punto de contacto", "Recepción, restaurante, bar o punto de salida del tour."),
        ],
        "enlace": {
            "titulo": "Cómo obtener el enlace de tu negocio en TripAdvisor",
            "lead": "Necesitamos la dirección de tu ficha o el enlace para escribir una opinión:",
            "pasos": [
                ("Busca tu negocio", "Entra a tripadvisor.com.mx y busca tu hotel, restaurante o actividad."),
                ("Copia el enlace de la ficha", "Copia la dirección completa de la página de tu negocio."),
                ("O usa tu cuenta de propietario", "Si administras la ficha, en Tripadvisor para empresas encontrarás herramientas para pedir opiniones con un enlace directo."),
                ("Pégalo al comprar", "Pega el enlace en el campo de esta página. Si tienes dudas, mándanos el nombre de tu negocio."),
            ],
            "nota": "Tripadvisor, igual que Google, prohíbe ofrecer incentivos a cambio de opiniones. Invita a todos tus clientes por igual.",
        },
        "donde": [
            ("En la recepción del hotel", "Al hacer el check‑out, el huésped tiene el celular en la mano."),
            ("En la cuenta del restaurante", "Después de una buena comida, el viajero quiere recomendarte."),
            ("Al final del tour", "Tu guía puede mostrar la tarjeta al despedirse del grupo."),
            ("En la habitación", "Junto a la tarjeta del Wi‑Fi, para opinar con calma."),
        ],
        "consejos": [
            "Usa una frase bilingüe: «¿Te gustó? / Did you enjoy it? Acerca tu celular / Tap your phone».",
            "Responde las opiniones en el idioma en que las escribieron.",
            "Combínala con la tarjeta de Google: muchos viajeros consultan ambos sitios.",
            "Capacita a tu equipo para invitar a opinar sin presionar.",
        ],
        "faq": [
            ("¿El viajero necesita la app de TripAdvisor?", "No. El enlace se abre en el navegador o en la app si la tiene instalada. Para publicar una opinión, TripAdvisor le pedirá iniciar sesión."),
            ("¿Funciona con celulares extranjeros?", "Sí. El NFC y el código QR funcionan igual con celulares de cualquier país."),
            ("¿Puedo tener una tarjeta para el hotel y otra para el restaurante?", "Sí. Si tienen fichas distintas en TripAdvisor, envíanos los enlaces separados por coma y configuramos cada tarjeta."),
            ("¿Está permitido pedir opiniones en TripAdvisor?", "Sí, pedir opiniones a tus clientes está permitido. Lo que no se permite es ofrecer incentivos o publicar opiniones falsas."),
        ],
        "blog": ["tarjetas-nfc-para-hoteles-y-airbnb", "como-responder-resenas-negativas"],
    },

    # ------------------------------------------------------------------ AIRBNB
    "tarjeta-nfc-resenas-airbnb": {
        "titulo_seo": "Tarjeta NFC para Airbnb con QR | Reseñas de Huéspedes",
        "desc_seo": "Tarjeta NFC con código QR que abre tu anuncio de Airbnb para recordar a tus huéspedes calificar su estancia y volver a reservar. Envío gratis.",
        "h2": "Tarjeta NFC para Airbnb: mejores calificaciones y huéspedes que regresan",
        "intro": [
            "En Airbnb, las calificaciones lo son todo: influyen en cuántas personas reservan tu espacio y en la confianza que generas frente a otros anuncios de la zona. Pero muchos huéspedes se van sin calificar, o lo dejan para después y se les olvida.",
            "La tarjeta NFC para Airbnb abre tu anuncio con un toque. Colocada en un lugar visible de tu propiedad, recuerda al huésped que su opinión importa y le permite guardar tu anuncio como favorito para volver a reservar.",
        ],
        "beneficios": [
            ("Recordatorio elegante", "Una tarjeta bien diseñada se ve profesional, no insistente."),
            ("Más huéspedes que regresan", "Al abrir tu anuncio, el huésped puede guardarlo y reservar de nuevo en su próximo viaje."),
            ("Sirve para varias propiedades", "Una tarjeta por propiedad, cada una con el enlace de su anuncio."),
            ("Combínala con el Wi‑Fi", "La tarjeta de Wi‑Fi junto a la de Airbnb resuelve las dos preguntas más comunes de tus huéspedes."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu anuncio de Airbnb",
            "lead": "El enlace de un anuncio suele verse así: https://www.airbnb.mx/rooms/123456789.",
            "pasos": [
                ("Abre tu anuncio", "En la app o la web de Airbnb, entra a tu anuncio como lo vería un huésped."),
                ("Toca «Compartir»", "El botón está en la parte superior del anuncio."),
                ("Elige «Copiar enlace»", "El enlace de tu anuncio queda copiado."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página. Si tienes varias propiedades, sepáralos con coma."),
            ],
            "nota": "Airbnb abre el periodo de reseñas cuando termina la estancia, y la reseña se escribe desde la app del huésped. La tarjeta funciona como recordatorio y como acceso directo a tu anuncio.",
        },
        "donde": [
            ("Junto a la puerta de salida", "Lo último que ve el huésped antes de irse."),
            ("En el libro o carpeta de bienvenida", "Junto a las reglas de la casa y recomendaciones de la zona."),
            ("En la mesa de entrada o la cocina", "Lugares donde el huésped deja llaves y celular."),
            ("Junto a la tarjeta del Wi‑Fi", "El huésped la va a usar desde el primer día."),
        ],
        "consejos": [
            "Envía un mensaje amable por la app al terminar la estancia y menciona que te encantaría conocer su opinión.",
            "Nunca ofrezcas descuentos a cambio de una buena calificación: las políticas de Airbnb lo prohíben.",
            "Revisa los comentarios y responde públicamente con cortesía, sobre todo los críticos.",
            "Cuida los detalles que más se califican: limpieza, comunicación y exactitud del anuncio.",
        ],
        "faq": [
            ("¿El huésped puede dejar la reseña desde la tarjeta?", "La tarjeta abre tu anuncio. Airbnb habilita la reseña al terminar la estancia y el huésped la escribe desde su app en la sección de viajes. La tarjeta funciona como recordatorio y acceso directo."),
            ("¿Sirve para varias propiedades?", "Sí. Envíanos el enlace de cada anuncio separado por coma y programamos cada tarjeta con el suyo."),
            ("¿Puedo usarla para Booking u otra plataforma?", "Sí. La tarjeta abre el enlace que nos envíes, así que puede apuntar a tu anuncio en otra plataforma o a tu propia página de reservas."),
            ("¿Qué pasa si cambio el anuncio?", "Si el anuncio conserva su enlace, la tarjeta sigue funcionando. Si creas un anuncio nuevo, escríbenos para revisar tu caso."),
        ],
        "blog": ["tarjetas-nfc-para-hoteles-y-airbnb", "como-compartir-wifi-con-clientes"],
    },

    # --------------------------------------------------------------- UBER EATS
    "tarjeta-nfc-uber-eats": {
        "titulo_seo": "Tarjeta NFC para Uber Eats con QR | Más Pedidos",
        "desc_seo": "Tarjeta NFC con código QR que abre tu restaurante en Uber Eats para que tus clientes vuelvan a pedir a domicilio en segundos. Envío gratis en México.",
        "h2": "Tarjeta NFC para Uber Eats: convierte visitas en pedidos a domicilio",
        "intro": [
            "El cliente que comió en tu restaurante y le gustó es el que más probabilidades tiene de pedirte a domicilio. El problema es que, cuando abre la app de delivery en su casa, ve cientos de opciones y no siempre se acuerda de tu nombre.",
            "La tarjeta NFC para Uber Eats abre directamente tu tienda en la app para que el cliente la guarde como favorita o haga su pedido en ese momento. Funciona con un toque o escaneando el código QR.",
        ],
        "beneficios": [
            ("Pedidos de clientes que ya te conocen", "El cliente que te visitó confía en tu comida y repite."),
            ("Directo a tu tienda", "Sin buscar entre la competencia dentro de la app."),
            ("Ideal para dark kitchens", "Si no tienes comedor, la tarjeta en tus bolsas de entrega trae al cliente de vuelta."),
            ("Más calificaciones en la app", "Clientes frecuentes suelen calificar y eso mejora tu presencia dentro de la plataforma."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu tienda en Uber Eats",
            "lead": "El enlace de una tienda suele empezar con https://www.ubereats.com/mx/store/.",
            "pasos": [
                ("Busca tu restaurante", "En ubereats.com o en la app, busca tu negocio como lo haría un cliente."),
                ("Abre tu tienda", "Entra a la página de tu restaurante en la plataforma."),
                ("Copia el enlace", "En la app usa «Compartir» y «Copiar enlace»; en la computadora, copia la barra de direcciones."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página. Si tienes varias sucursales, sepáralos con coma."),
            ],
            "nota": "Si tienes acceso al administrador de tu restaurante en Uber Eats, ahí también puedes encontrar el enlace para compartir tu tienda.",
        },
        "donde": [
            ("En las bolsas de entrega", "Engrapada o dentro del pedido, para el siguiente antojo."),
            ("En la caja", "Para el cliente que pide para llevar y otro día prefiere a domicilio."),
            ("En las mesas", "Para quienes descubren tu comida en el local."),
            ("En el mostrador de recolección", "Para repartidores y clientes que recogen."),
        ],
        "consejos": [
            "Acompaña la tarjeta con un mensaje claro: «¿Antojo en casa? Acerca tu celular y pídenos por Uber Eats».",
            "Mantén actualizado tu menú, horario y fotos en la app para que el cliente no se decepcione.",
            "Combínala con la tarjeta de Rappi si estás en ambas plataformas: cada cliente tiene su favorita.",
            "Pide también reseñas en Google: la reputación fuera de la app atrae clientes nuevos al local.",
        ],
        "faq": [
            ("¿Se abre la app de Uber Eats?", "Si el cliente tiene la app instalada, normalmente el enlace abre tu tienda en la app. Si no, se abre en el navegador, donde también puede pedir."),
            ("¿Funciona fuera de la zona de entrega?", "La tarjeta abre tu tienda, pero la plataforma solo permite pedir si la dirección del cliente está dentro de tu zona de cobertura."),
            ("¿Puedo usar la misma tarjeta para varias sucursales?", "Cada tarjeta abre un enlace. Si cada sucursal tiene su tienda en Uber Eats, pide una tarjeta por sucursal."),
            ("¿Necesito permiso de Uber Eats para usar la tarjeta?", "La tarjeta solo abre el enlace público de tu tienda, el mismo que podrías compartir en redes sociales. Es una tarjeta independiente; Uber Eats es marca de su respectivo dueño."),
        ],
        "blog": ["tarjetas-nfc-para-restaurantes"],
    },

    # ------------------------------------------------------------------- RAPPI
    "tarjeta-nfc-rappi": {
        "titulo_seo": "Tarjeta NFC para Rappi con QR | Pedidos Recurrentes",
        "desc_seo": "Tarjeta NFC con código QR que abre tu tienda o restaurante en Rappi para que tus clientes vuelvan a pedir a domicilio en un toque. Envío gratis.",
        "h2": "Tarjeta NFC para Rappi: clientes que vuelven a pedir",
        "intro": [
            "Rappi no es solo comida: farmacias, florerías, tiendas de conveniencia y supermercados de barrio venden a domicilio con la plataforma. En todos los casos, el cliente que ya te compró en persona es el más fácil de convertir en cliente recurrente.",
            "La tarjeta NFC para Rappi abre tu tienda directamente en la app. Un toque o un escaneo del QR y el cliente puede guardar tu tienda o pedir en ese momento.",
        ],
        "beneficios": [
            ("Para cualquier giro en Rappi", "Restaurantes, farmacias, florerías, minisúper y más."),
            ("Directo a tu tienda", "Sin buscar entre la competencia dentro de la app."),
            ("Pedidos recurrentes", "El cliente que guarda tu tienda vuelve a pedir con más facilidad."),
            ("Funciona en bolsas y empaques", "La tarjeta viaja con cada pedido."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu tienda en Rappi",
            "lead": "El enlace de una tienda suele empezar con https://www.rappi.com.mx/.",
            "pasos": [
                ("Busca tu tienda", "En rappi.com.mx o en la app, busca tu negocio como lo haría un cliente."),
                ("Abre la página de tu tienda", "Entra a tu tienda o restaurante dentro de la plataforma."),
                ("Copia el enlace", "Usa la opción de compartir de la app o copia la barra de direcciones en la computadora."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página. Si tienes varias sucursales, sepáralos con coma."),
            ],
            "nota": "Si no encuentras el enlace, mándanos el nombre de tu negocio y la ciudad y te ayudamos.",
        },
        "donde": [
            ("En la caja", "Para que el cliente te pida desde casa la próxima vez."),
            ("Dentro de cada pedido", "En bolsas, cajas o junto al ticket."),
            ("En el mostrador de farmacia o tienda", "Para compras urgentes a domicilio."),
            ("En arreglos y regalos", "En florerías, para el próximo detalle."),
        ],
        "consejos": [
            "Usa una frase directa: «¿Te lo llevamos? Acerca tu celular y pide por Rappi».",
            "Mantén tu catálogo, precios y fotos al día dentro de la plataforma.",
            "Si también estás en Uber Eats, ofrece ambas tarjetas: cada cliente tiene su app favorita.",
            "Pide reseñas en Google a los clientes que visitan tu local para atraer gente nueva.",
        ],
        "faq": [
            ("¿Se abre la app de Rappi?", "Si el cliente tiene Rappi instalado, normalmente el enlace abre tu tienda en la app. Si no, se abre en el navegador."),
            ("¿Sirve para farmacias y tiendas, no solo restaurantes?", "Sí. La tarjeta abre cualquier tienda que tengas en Rappi."),
            ("¿Qué pasa si el cliente está fuera de mi zona?", "La tarjeta abre tu tienda, pero la plataforma solo permite pedir dentro de tu zona de cobertura."),
            ("¿Puedo combinar tarjetas de Rappi y Uber Eats?", "Sí. Puedes agregar ambas al carrito, cada una con su paquete."),
        ],
        "blog": ["tarjetas-nfc-para-restaurantes"],
    },

    # ---------------------------------------------------------------- LINKEDIN
    "tarjeta-nfc-linkedin": {
        "titulo_seo": "Tarjeta NFC para LinkedIn con QR | Tarjeta de Presentación",
        "desc_seo": "Tarjeta de presentación NFC con QR que abre tu perfil de LinkedIn con un toque. Networking en juntas, congresos y entrevistas. Envío gratis en México.",
        "h2": "Tarjeta NFC para LinkedIn: tu tarjeta de presentación digital",
        "intro": [
            "Las tarjetas de presentación de papel terminan en un cajón: se pierden, se desactualizan y obligan a la otra persona a capturar tus datos a mano. En un congreso o una junta, lo que de verdad quieres es que te agreguen en LinkedIn antes de despedirse.",
            "La tarjeta NFC para LinkedIn es una tarjeta de presentación digital: la otra persona acerca su celular y se abre tu perfil, listo para conectar. Si su teléfono no tiene NFC, escanea el código QR. Tu perfil siempre está actualizado, aunque cambies de puesto.",
        ],
        "beneficios": [
            ("Nunca pierdes un contacto", "La conexión queda guardada en LinkedIn, no en una tarjeta de papel."),
            ("Siempre actualizada", "Si cambias de puesto o empresa, actualizas tu perfil y la tarjeta sigue sirviendo."),
            ("Impresión profesional", "Compartir tu perfil con un toque deja una imagen moderna y memorable."),
            ("Para equipos completos", "Ventas, reclutamiento y dirección: una tarjeta por persona."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu perfil de LinkedIn",
            "lead": "Tu enlace público tiene la forma https://www.linkedin.com/in/tunombre.",
            "pasos": [
                ("Abre tu perfil", "En LinkedIn toca tu foto y entra a «Ver perfil»."),
                ("Busca tu URL pública", "En la computadora aparece como «Perfil público y URL» en la parte derecha de tu perfil."),
                ("Personaliza tu URL (opcional)", "Puedes cambiarla por algo como /in/nombre-apellido para que sea más limpia."),
                ("Pégala al comprar", "Pega el enlace en el campo de esta página. Para una página de empresa, usa el enlace de la página."),
            ],
            "nota": "Personaliza tu URL antes de pedir la tarjeta: si la cambias después, el enlace anterior deja de funcionar.",
        },
        "donde": [
            ("En tu cartera", "Como cualquier tarjeta de presentación, siempre a la mano."),
            ("En congresos y expos", "Para conectar en segundos entre conferencias."),
            ("En entrevistas", "Reclutadores y candidatos comparten perfil al terminar."),
            ("En tu escritorio o stand", "Para visitantes y clientes."),
        ],
        "consejos": [
            "Antes de usar la tarjeta, completa tu perfil: foto profesional, titular claro y experiencia actualizada.",
            "Después de conectar, envía un mensaje breve recordando dónde se conocieron.",
            "Para equipos de ventas, pide una tarjeta por vendedor con su propio perfil.",
            "Si prefieres que te escriban directo, combínala con una tarjeta de WhatsApp.",
        ],
        "faq": [
            ("¿Sirve como tarjeta de presentación?", "Sí. Es una tarjeta de presentación digital del tamaño de una tarjeta de crédito: en lugar de leer tus datos, la otra persona abre tu perfil de LinkedIn en un toque."),
            ("¿Puedo usar la página de mi empresa?", "Sí. La tarjeta abre el enlace que nos envíes: tu perfil personal o la página de tu empresa."),
            ("¿La otra persona necesita la app de LinkedIn?", "No es obligatorio. Si tiene la app, normalmente se abre ahí; si no, se abre la versión web."),
            ("¿Hacen tarjetas para todo un equipo?", "Sí. Escribe los enlaces separados por coma al comprar o escríbenos por WhatsApp para pedidos de mayoreo."),
        ],
        "blog": ["tarjeta-de-presentacion-nfc-digital", "que-es-una-tarjeta-nfc"],
    },

    # ----------------------------------------------------------------- YOUTUBE
    "tarjeta-nfc-youtube": {
        "titulo_seo": "Tarjeta NFC para YouTube con QR | Más Suscriptores",
        "desc_seo": "Tarjeta NFC con código QR que abre tu canal de YouTube para que se suscriban en un toque. Para creadores, escuelas y marcas. Envío gratis en México.",
        "h2": "Tarjeta NFC para YouTube: suscriptores en un toque",
        "intro": [
            "Si haces tutoriales, clases, música, reseñas o contenido de tu negocio en YouTube, cada persona que te conoce en persona es un suscriptor potencial. Pero «búscame en YouTube» casi nunca funciona: hay canales con nombres parecidos y el interés se enfría en minutos.",
            "La tarjeta NFC para YouTube abre tu canal al instante. Incluso podemos configurarla para que muestre directamente la ventana de confirmación de suscripción, de modo que suscribirse sea un solo toque más.",
        ],
        "beneficios": [
            ("Suscripción directa", "Con el enlace adecuado, YouTube muestra de inmediato la confirmación para suscribirse."),
            ("Para escuelas y academias", "Alumnos y padres llegan a tus clases y tutoriales sin buscar."),
            ("Para negocios con tutoriales", "Ferreterías, tiendas de belleza o talleres que enseñan a usar sus productos."),
            ("Para eventos", "Conferencias, presentaciones y meetups donde conoces a tu audiencia."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu canal de YouTube",
            "lead": "Tu enlace tiene la forma https://www.youtube.com/@tucanal.",
            "pasos": [
                ("Abre tu canal", "En YouTube toca tu foto y entra a «Tu canal»."),
                ("Copia el enlace", "Usa «Compartir» → «Copiar enlace», o copia la dirección en la computadora."),
                ("Elige si quieres suscripción directa", "Podemos agregar al enlace la opción que muestra la ventana de suscripción al abrirlo."),
                ("Pégalo al comprar", "Pega el enlace en el campo de esta página. También puede ser un video o una playlist específica."),
            ],
            "nota": "Para la suscripción directa se agrega ?sub_confirmation=1 al final del enlace de tu canal. Si lo prefieres, lo hacemos nosotros.",
        },
        "donde": [
            ("En tu escuela o academia", "En recepción y en cada salón."),
            ("En tu mostrador", "Junto a los productos que explicas en tus videos."),
            ("En presentaciones y eventos", "Para que el público se suscriba al terminar."),
            ("En tu merch o empaques", "Para quien te compra y quiere ver más."),
        ],
        "consejos": [
            "Usa la suscripción directa: reduce un paso y aumenta las suscripciones.",
            "Si quieres promocionar un video específico (un tutorial o un lanzamiento), configura la tarjeta con ese video.",
            "Cuida la portada y el tráiler de tu canal: es lo primero que verá quien llegue con la tarjeta.",
            "Combínala con Instagram o TikTok si publicas videos cortos.",
        ],
        "faq": [
            ("¿Puede abrir un video en lugar del canal?", "Sí. La tarjeta abre el enlace que nos envíes: tu canal, un video, una playlist o un short."),
            ("¿Qué es la suscripción directa?", "Es un parámetro que se agrega al enlace del canal para que YouTube muestre de inmediato la ventana de confirmación de suscripción."),
            ("¿Se abre la app de YouTube?", "Si el usuario tiene la app instalada, normalmente el enlace se abre ahí. Si no, en el navegador."),
            ("¿Sirve para canales de iglesias o comunidades?", "Sí, para cualquier canal: transmisiones en vivo, mensajes y avisos llegan a más personas."),
        ],
        "blog": ["como-conseguir-seguidores-instagram-negocio-local"],
    },

    # ----------------------------------------------------------------- SPOTIFY
    "tarjeta-nfc-spotify": {
        "titulo_seo": "Tarjeta NFC para Spotify con QR | Música y Podcast",
        "desc_seo": "Tarjeta NFC con QR que abre tu perfil de artista, canción, playlist o podcast en Spotify con un toque. Para músicos, DJs y negocios. Envío gratis.",
        "h2": "Tarjeta NFC para Spotify: que tu música suene en más celulares",
        "intro": [
            "Si eres músico, DJ o podcaster, cada presentación en vivo es una oportunidad para ganar oyentes. Pero entre el ruido del lugar y los nombres parecidos, pocas personas logran encontrarte en Spotify después del show.",
            "La tarjeta NFC para Spotify abre tu perfil de artista, tu último sencillo, una playlist o tu podcast con un toque. Y no es solo para artistas: bares y cafeterías la usan para compartir su playlist, y los novios para compartir la música de su boda.",
        ],
        "beneficios": [
            ("Nuevos oyentes en cada show", "El público te sigue en Spotify antes de salir del lugar."),
            ("Promociona un lanzamiento", "Configura la tarjeta con tu nuevo sencillo para impulsar las reproducciones."),
            ("Playlist de tu negocio", "Tus clientes guardan la música que suena en tu café o bar."),
            ("Regalos y eventos", "Bodas, XV años y aniversarios con su playlist en una tarjeta."),
        ],
        "enlace": {
            "titulo": "Cómo copiar un enlace de Spotify",
            "lead": "Los enlaces de Spotify empiezan con https://open.spotify.com/.",
            "pasos": [
                ("Abre lo que quieres compartir", "Tu perfil de artista, una canción, un álbum, una playlist o un episodio de podcast."),
                ("Toca el menú «⋯»", "Aparece junto al título o en la parte superior."),
                ("Elige «Compartir» → «Copiar enlace»", "El enlace queda copiado en tu celular."),
                ("Pégalo al comprar", "Pégalo en el campo de esta página. Puedes pedir varias tarjetas con enlaces distintos."),
            ],
            "nota": "Para lanzamientos, puedes configurar una tarjeta con tu perfil de artista (que siempre muestra lo más nuevo) en lugar de una canción específica.",
        },
        "donde": [
            ("En tu merch y mesa de ventas", "Después del show, el público pasa a comprar y te sigue."),
            ("En la barra del bar o la cafetería", "Para compartir la playlist del lugar."),
            ("En invitaciones y recuerdos", "Para bodas, XV años y eventos."),
            ("En tu estudio o escuela de música", "Para alumnos y visitantes."),
        ],
        "consejos": [
            "Usa el perfil de artista si lanzas música seguido: siempre muestra lo más reciente.",
            "Menciona la tarjeta desde el escenario: «Acerquen su celular a la tarjeta en la mesa de merch».",
            "Para podcasts, enlaza el programa completo para que la gente lo siga.",
            "Combínala con Instagram o TikTok para que el público vea tus próximas fechas.",
        ],
        "faq": [
            ("¿Qué puedo poner en la tarjeta?", "Cualquier enlace de Spotify: perfil de artista, canción, álbum, playlist, podcast o episodio."),
            ("¿Se abre la app de Spotify?", "Si el usuario tiene Spotify instalado, normalmente el enlace se abre en la app. Si no, se abre la versión web."),
            ("¿Funciona con Apple Music o YouTube Music?", "Sí. La tarjeta abre el enlace que nos envíes, de cualquier plataforma."),
            ("¿Sirve como regalo?", "Sí. Una tarjeta con una playlist especial es un regalo original para parejas, bodas o cumpleaños."),
        ],
        "blog": ["que-es-una-tarjeta-nfc"],
    },

    # ------------------------------------------------------------------ TWITCH
    "tarjeta-nfc-twitch": {
        "titulo_seo": "Tarjeta NFC para Twitch con QR | Streamers y Esports",
        "desc_seo": "Tarjeta NFC con código QR que abre tu canal de Twitch en un toque para ganar seguidores en torneos, convenciones y eventos gamer. Envío gratis.",
        "h2": "Tarjeta NFC para Twitch: haz crecer tu comunidad fuera de línea",
        "intro": [
            "La comunidad de un streamer también se construye en persona: torneos, convenciones, cafés gamer y meetups. Ahí conoces a personas que comparten tus gustos y que podrían convertirse en espectadores fieles, pero dictar el nombre de tu canal entre el ruido no funciona.",
            "La tarjeta NFC para Twitch abre tu canal con un toque para que te sigan en el momento y reciban la notificación cuando entres en vivo.",
        ],
        "beneficios": [
            ("Seguidores en eventos", "Torneos, convenciones y meetups se vuelven fuente de nuevos espectadores."),
            ("Notificaciones de tus directos", "Quien te sigue recibe el aviso cuando empiezas a transmitir."),
            ("Para equipos de esports", "Una tarjeta por jugador o una para el canal del equipo."),
            ("Para cafés y tiendas gamer", "Promociona el canal de tu local o de tus torneos."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu canal de Twitch",
            "lead": "Tu enlace tiene la forma https://www.twitch.tv/tucanal.",
            "pasos": [
                ("Abre tu canal", "En Twitch entra a tu perfil o canal."),
                ("Copia el enlace", "Usa la opción de compartir o copia la dirección en la computadora."),
                ("Revisa tu usuario", "El enlace usa tu nombre de usuario; si planeas cambiarlo, hazlo antes de pedir la tarjeta."),
                ("Pégalo al comprar", "Pega el enlace en el campo de esta página."),
            ],
            "nota": "Si transmites en varias plataformas, puedes pedir una tarjeta para cada una (Twitch, Kick, YouTube o TikTok).",
        },
        "donde": [
            ("En tu stand o mesa en convenciones", "Para fans y curiosos."),
            ("En torneos", "Junto a tu equipo o en tu credencial."),
            ("En cafés y tiendas gamer", "En el mostrador o en las estaciones de juego."),
            ("En tu setup", "Para colaboraciones y visitas."),
        ],
        "consejos": [
            "Comparte tu horario de transmisiones en tu perfil para que los nuevos seguidores sepan cuándo verte.",
            "Menciona la tarjeta en tus directos cuando vayas a un evento.",
            "Lleva varias tarjetas: en convenciones se mueven rápido.",
            "Combínala con TikTok o YouTube para tus clips.",
        ],
        "faq": [
            ("¿Se abre la app de Twitch?", "Si el usuario tiene la app instalada, normalmente el canal se abre ahí. Si no, en el navegador."),
            ("¿Puedo cambiar a Kick o YouTube después?", "La tarjeta queda configurada con el enlace que nos envíes. Si cambias de plataforma, te conviene una tarjeta nueva para esa plataforma."),
            ("¿Hacen tarjetas para equipos de esports?", "Sí. Escribe los enlaces de cada jugador separados por coma o escríbenos por WhatsApp para pedidos grandes."),
            ("¿Funciona en eventos con mucha gente?", "Sí. El NFC solo se activa a pocos centímetros, así que cada persona abre el canal desde su propio celular sin interferencias."),
        ],
        "blog": ["nfc-vs-codigo-qr"],
    },

    # -------------------------------------------------------------------- KICK
    "tarjeta-nfc-kick": {
        "titulo_seo": "Tarjeta NFC para Kick con QR | Para Streamers",
        "desc_seo": "Tarjeta NFC con código QR que abre tu canal de Kick en un toque para ganar seguidores en eventos, meetups y colaboraciones. Envío gratis en México.",
        "h2": "Tarjeta NFC para Kick: nuevos espectadores para tus streams",
        "intro": [
            "Kick ganó popularidad entre streamers de habla hispana y muchas comunidades se mueven entre transmisiones en vivo y eventos presenciales. Cada meetup o colaboración es una oportunidad para sumar seguidores, siempre que encontrarte sea fácil.",
            "La tarjeta NFC para Kick abre tu canal con un toque. Si el celular no tiene NFC, el código QR impreso lleva al mismo lugar.",
        ],
        "beneficios": [
            ("Seguidores en persona", "Convierte los encuentros con tu comunidad en seguidores del canal."),
            ("Para colaboraciones", "Intercambia canales con otros creadores en segundos."),
            ("Para comunidades y equipos", "Una tarjeta por miembro o una para el canal principal."),
            ("Sin escribir tu usuario", "Nada de deletrear nombres con números o guiones."),
        ],
        "enlace": {
            "titulo": "Cómo copiar el enlace de tu canal de Kick",
            "lead": "Tu enlace tiene la forma https://kick.com/tucanal.",
            "pasos": [
                ("Abre tu canal", "En Kick entra a tu canal."),
                ("Copia el enlace", "Usa la opción de compartir o copia la dirección en la computadora."),
                ("Confirma tu usuario", "Si planeas cambiar tu nombre de usuario, hazlo antes de pedir la tarjeta."),
                ("Pégalo al comprar", "Pega el enlace en el campo de esta página."),
            ],
            "nota": "Si también transmites en Twitch o YouTube, puedes combinar tarjetas de cada plataforma en el mismo pedido.",
        },
        "donde": [
            ("En meetups y eventos", "Para la comunidad que te conoce en persona."),
            ("En tu setup", "Para colaboraciones y visitas."),
            ("En convenciones", "En tu stand o credencial."),
            ("En merch", "Dentro de tus pedidos de playeras o accesorios."),
        ],
        "consejos": [
            "Comparte tus horarios en el perfil del canal.",
            "Lleva varias tarjetas a los eventos y repártelas entre tu equipo.",
            "Menciona en tus streams a qué eventos vas a ir.",
            "Combínala con TikTok para tus clips y mejores momentos.",
        ],
        "faq": [
            ("¿Se abre la app de Kick?", "Si el usuario tiene la app instalada, normalmente el canal se abre ahí. Si no, en el navegador."),
            ("¿Funciona con cualquier celular?", "Sí. El NFC funciona en iPhone XS o posterior y en la mayoría de los Android con NFC; para cualquier otro, el código QR."),
            ("¿Puedo usar la tarjeta para otra plataforma después?", "La tarjeta queda configurada con el enlace que nos envíes. Para otra plataforma te recomendamos una tarjeta nueva."),
            ("¿Hacen pedidos para comunidades grandes?", "Sí. Para más de 10 tarjetas escríbenos por WhatsApp y cotizamos mayoreo."),
        ],
        "blog": ["nfc-vs-codigo-qr"],
    },
}
