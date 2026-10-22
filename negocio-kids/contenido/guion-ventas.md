# Guion de ventas por WhatsApp

Base del agente `vendedor`. Ajusta nombre de la tienda, ciudad y métodos de pago.

## Flujo

1. **Saludo** (responde en menos de 10 minutos en horario de tienda)
   > ¡Hola! Gracias por escribir a Nido Kids 😊 ¿Para niño o niña, y cuántos meses o años tiene?
2. **Talla**
   > ¿Sabes cuánto mide de estatura? Si no, con la edad te oriento. Nuestras prendas vienen por estatura en cm, así es más fácil acertar.
3. **Propuesta** (máximo 3 opciones, con foto real y precio)
   > Para 2 años (unos 90 cm) te recomiendo la talla 100 para que le dure. Tengo estas 3 opciones: …
4. **Cierre**
   > ¿Te la separo? Puedes pagar por transferencia o DeUna, o en efectivo al recibir. ¿A qué dirección te la envío?
5. **Confirmación**
   > ¡Listo! Pedido: [prenda], talla [x], $[precio]. Entrega [día] entre [hora]. Te escribo cuando el motorizado salga.
6. **Después de la entrega** (al día siguiente)
   > ¿Le quedó bien? Si nos mandas una foto con la prenda, te regalamos un set de lazos en tu próxima compra.

## Objeciones

| Si te dicen | Responde |
|---|---|
| “En Temu está más barato” | Sí, pero allá esperas de 3 a 5 semanas, pagas $20 de aduana por paquete y si no le queda no la puedes cambiar. Aquí la ves, la recibes hoy y puedes cambiar la talla. |
| “¿Y si no le queda?” | Tienes 3 días para cambiar la talla si está sin usar y con la etiqueta. |
| “¿La tela es buena?” | Te mando un video de cerca y la foto de la etiqueta: es [composición]. |
| “Está caro” | Te ofrezco el combo [prenda + accesorio] por $[x]: sale más a cuenta y queda listo para regalar. |
| “Lo pienso” | ¡Claro! Solo te cuento que de esa talla me queda [n]. Si quieres te la separo hasta mañana sin compromiso. |

## Seguimiento

- A las 24 h, a quien preguntó y no compró: “Hola, ¿pudiste ver lo de la pijama? Todavía tengo tu talla.”
- Cuando quede 1 unidad: aviso a quienes preguntaron por esa prenda.
- Cada venta va a `datos/ventas.csv`.
