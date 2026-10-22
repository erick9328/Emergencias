# Negocio de ropa infantil Temu → Ecuador (Navidad 2026)

Sistema de agentes y herramientas para elegir ropa de 3 meses a 5 años en Temu, calcular su costo puesto en Ecuador, fijar precios y venderla en redes sociales antes de Navidad.

## Qué hay aquí

| Parte | Archivo | Qué hace |
|---|---|---|
| Agente investigador | `.claude/agents/investigador-temu.md` | Busca en Temu los más vendidos, mejor calificados, con reseñas con fotos, buena tela y tallas en cm |
| Extractor de Temu | `herramientas/temu_scraper.py` | Corre un scraper de Apify (o lee un JSON exportado), filtra por edad y calificación, y ordena por puntaje |
| Agente de costos | `.claude/agents/analista-costos.md` | Costo en Ecuador con la tasa de $20 por paquete, precio de venta, ganancia y punto de equilibrio |
| Dashboard | `dashboard/index.html` | Calculadora del negocio: se regenera con `herramientas/construir_dashboard.py` |
| Agente estratega | `.claude/agents/estratega-contenido.md` | Calendario de contenido y lista de fotos y videos |
| Agente copywriter | `.claude/agents/copywriter.md` | Captions, guiones de reels, Estados de WhatsApp |
| Agente publicador | `.claude/agents/publicador.md` | CSV para Meta Business Suite o publicación por la Graph API |
| Agente vendedor | `.claude/agents/vendedor.md` | Guiones de WhatsApp, objeciones, seguimiento, landing y registro de ventas |
| Landing page | `landing/index.html` | Catálogo con botón de WhatsApp por producto y guía de tallas |
| Plan de contenido | `contenido/plan-contenido.md`, `contenido/guion-ventas.md` | Punto de partida para los agentes de contenido y ventas |

## Cómo usarlo

1. **Datos reales de Temu.** Opción A, Apify: crea una cuenta en apify.com, copia tu token y corre
   ```bash
   export APIFY_TOKEN=...
   python negocio-kids/herramientas/temu_scraper.py --apify
   ```
   Opción B: abre Claude Code en tu computadora con Claude in Chrome y pide “usa el agente investigador-temu”. Navega Temu con tu cuenta de Ecuador, así que ve los precios reales que vas a pagar.
2. **Costos y dashboard.**
   ```bash
   python negocio-kids/herramientas/construir_dashboard.py
   ```
   Abre `negocio-kids/dashboard/index.html` en el navegador, ajusta cantidades y precios, y compra.
3. **Cuando llegue la ropa**, pide en Claude Code: “estratega-contenido, planea la semana”, luego “copywriter, escribe los textos”, luego “publicador, prepara la programación”.
4. **Ventas:** cambia el número de WhatsApp en `landing/index.html` (constante `TIENDA`) y publícala gratis en Vercel, Netlify o GitHub Pages.

Requisitos: Python 3.9 o superior. Los scripts no usan librerías externas.

## ¿Es viable?

Con los valores de referencia del dashboard (62 prendas en 3 paquetes):

- Inversión total: unos **$540** (pedido $382, tasas $60, empaque y $75 de publicidad y gastos).
- Si vendes el 85% del stock: **unos $220 de ganancia neta**, un retorno del 41% en 5 o 6 semanas.
- Punto de equilibrio: **35 prendas de 62** (56%).
- Cada prenda paga cerca de **$1 de tasa** cuando el paquete va lleno (unas 20 prendas por paquete de 3,6 kg). Un paquete con 5 prendas paga $4 por prenda: la clave del margen es llenar los paquetes.

El margen por prenda es bueno (45–55%) porque en Ecuador la ropa infantil de tienda cuesta entre 2 y 3 veces más. Tu ventaja es el tiempo: desde la primera semana de diciembre un pedido nuevo a Temu ya no llega para Navidad, y tú tienes la ropa en la mano.

El negocio es rentable a escala pequeña. Con el 4x4 no crece mucho más, por dos razones:

1. **El régimen 4x4 es para compras sin fines comerciales.** SENAE ha advertido que traer mercadería por courier para revenderla es ilegal y tiene sanciones, y la tasa de $20 se creó en junio de 2025 justamente para frenar ese uso. Un primer lote pequeño sirve para probar si se vende. Si funciona, saca RUC (régimen RIMPE emprendedor) e importa por régimen formal o compra a un importador mayorista. Confirma con un agente de aduanas antes de invertir más.
2. **Cupo de $1.600 al año por persona.** Lo que ya compraste este año en Temu, Amazon o Shein cuenta.

Riesgos de calendario: Temu tarda normalmente de 10 a 25 días hábiles a Ecuador y en temporada alta puede tardar el doble. Para vender desde finales de noviembre hay que comprar **esta semana** (antes del 27 de octubre).

## Lo que no se pudo hacer desde la sesión en la nube

- Temu y Apify están bloqueados por la red de la sesión en la nube donde se armó esto. Por eso los precios y pesos de `datos/productos.json` son **estimaciones de referencia**, no datos sacados de Temu. Reemplázalos con el paso 1 antes de comprar.
- `temu_scraper.py` se probó con un archivo de muestra, no contra Apify en vivo. Cada actor de Apify usa su propio formato de entrada; si el primero falla, revisa su pestaña Input y usa `--entrada`.
- La publicación automática necesita una app de Meta con tokens tuyos. Sin eso, el publicador deja un CSV para subir a Meta Business Suite.

## Fuentes

- [Tasa de $20 a paquetes 4x4 desde el 16 de junio de 2025 (Primicias)](https://www.primicias.ec/economia/tasa-pedidos-4x4-temu-amazon-couriers-compras-98506/)
- [Tarifa de $20 para evitar uso comercial informal del 4x4 (El Universo)](https://www.eluniverso.com/noticias/economia/tarifa-fija-para-envio-paquetes-sistema-4x4-ecuador-efecto-temu-nota/)
- [Envíos Courier o Postal (SENAE)](https://www.aduana.gob.ec/servicio-al-ciudadano/envios-courier-postal/)
- [Arancel de $20 y límites del 4x4 (Importaciones Ecuador)](https://www.importacionesecuador.com.ec/articulos/arancel-de-usd-20-para-importaciones-a-traves-de-courier-4-x-4)
- [Aduana sobre ingreso de prendas para venta (Extra)](https://www.extra.ec/noticia/servicios-y-tramites/aduana-aclara-articulos-que-puedes-ingresar-sin-tributos-ecuador-142951.html)
- [Tiempos de entrega de Temu a Ecuador (Extra)](https://www.extra.ec/noticia/servicios-y-tramites/que-hacer-si-tu-pedido-de-temu-no-llega-tras-el-black-friday-140643.html)
- [Precios de referencia: pijamas de bebé en Zara Ecuador](https://www.zara.com/ec/es/ninos-bebe-pijamas-l7221.html)
- [Scraper de Temu en Apify (apivault_labs)](https://apify.com/apivault_labs/temu-product-scraper)
