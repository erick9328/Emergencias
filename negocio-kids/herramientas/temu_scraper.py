"""Busca en Temu los productos infantiles (3 meses a 5 años) más vendidos y mejor calificados.

Dos formas de usarlo:

1) Con Apify (scraper en la nube, cuesta unos centavos por cada 1.000 productos):
       export APIFY_TOKEN=tu_token
       python negocio-kids/herramientas/temu_scraper.py --apify

   Por defecto usa el actor "apivault_labs~temu-product-scraper". Cada actor de Apify
   tiene su propio formato de entrada: revisa la pestaña "Input" del actor y, si hace
   falta, pasa la tuya con --entrada entrada.json.

2) Con un archivo ya descargado (exportado desde Apify, o JSON guardado a mano):
       python negocio-kids/herramientas/temu_scraper.py --desde-archivo resultados.json

El resultado se guarda en datos/productos.json con el formato que lee el dashboard.
Después corre construir_dashboard.py para verlo.
"""
import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from urllib import request

BASE = Path(__file__).resolve().parent.parent

BUSQUEDAS = [
    "toddler christmas pajamas cotton",
    "baby my first christmas outfit",
    "toddler girl party dress",
    "toddler boy gentleman outfit",
    "baby bodysuit cotton pack",
    "baby first walker shoes",
    "toddler summer cotton set",
    "baby headbands bows set",
    "toddler knit cardigan",
    "baby gift set newborn cotton",
]

# Palabras que indican la edad buscada (3 meses a 5 años)
EDAD_SI = re.compile(r"\b(baby|infant|toddler|kids?|bebe|bebé|niñ[oa]s?|0-3|3-6|6-12|12-18|18-24|[1-5]\s?t\b|[1-5]\s?(y|years?|años))\b", re.I)
EDAD_NO = re.compile(r"\b(women|men|adult|teen|mujer|hombre|adulto|8-12|10-14|12-16)\b", re.I)
TELA_BUENA = re.compile(r"(cotton|algod[oó]n|bamboo|bamb[uú]|modal)", re.I)

# Alias de campos: cada actor de Apify nombra distinto los mismos datos
CAMPOS = {
    "titulo": ["title", "name", "goodsName", "productName", "nombre"],
    "precio": ["price", "salePrice", "currentPrice", "priceValue", "minPrice", "precio_temu"],
    "vendidos": ["soldCount", "sold", "sales", "salesCount", "salesVolume", "ventas"],
    "rating": ["rating", "stars", "score", "averageRating"],
    "resenas": ["reviewCount", "reviews", "reviewsCount", "commentCount", "resenas"],
    "resenas_foto": ["photoReviewCount", "reviewsWithPhotos", "imageReviewCount", "resenas_con_foto"],
    "url": ["url", "productUrl", "link", "goodsUrl"],
    "imagen": ["image", "imageUrl", "thumbnail", "mainImage"],
    "tela": ["material", "fabric", "composition"],
}


def campo(item, clave):
    for k in CAMPOS[clave]:
        v = item.get(k)
        if v not in (None, "", []):
            return v
    return None


def numero(v):
    """'1.2K+ sold' -> 1200, '$6.49' -> 6.49, {'value': 3} -> 3."""
    if v is None:
        return None
    if isinstance(v, dict):
        v = v.get("value") or v.get("amount") or v.get("price")
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([km])?", s)
    if not m:
        return None
    n = float(m.group(1))
    return n * {"k": 1_000, "m": 1_000_000}.get(m.group(2), 1)


def normalizar(item):
    titulo = str(campo(item, "titulo") or "").strip()
    return {
        "titulo": titulo,
        "precio": numero(campo(item, "precio")),
        "vendidos": numero(campo(item, "vendidos")) or 0,
        "rating": numero(campo(item, "rating")) or 0,
        "resenas": numero(campo(item, "resenas")) or 0,
        "resenas_foto": numero(campo(item, "resenas_foto")),
        "url": campo(item, "url") or "",
        "imagen": campo(item, "imagen") or "",
        "tela": str(campo(item, "tela") or ""),
    }


def es_de_la_edad(p):
    texto = p["titulo"]
    return bool(EDAD_SI.search(texto)) and not EDAD_NO.search(texto)


def puntaje(p, max_vendidos, max_resenas):
    """0 a 100: ventas 40%, calificación 30%, número de reseñas 20%, fotos de clientes y tela 10%."""
    ventas = math.log1p(p["vendidos"]) / math.log1p(max_vendidos or 1)
    rating = max(0.0, (p["rating"] - 4.0) / 1.0) if p["rating"] else 0
    resenas = math.log1p(p["resenas"]) / math.log1p(max_resenas or 1)
    extra = 0.5 if (p["resenas_foto"] or 0) >= 20 else 0
    extra += 0.5 if TELA_BUENA.search(p["tela"] + " " + p["titulo"]) else 0
    return round(100 * (0.4 * ventas + 0.3 * min(rating, 1) + 0.2 * resenas + 0.1 * extra), 1)


def a_formato_dashboard(p, i):
    precio = p["precio"] or 0
    return {
        "id": f"temu-{i}",
        "nombre": p["titulo"][:70],
        "categoria": "Temu",
        "edad": "",
        "precio_temu": round(precio, 2),
        "peso_g": 180,  # Temu casi nunca publica el peso: ajústalo en el dashboard
        "cantidad": 0,
        "precio_venta": round(max(1, math.ceil(precio * 2.5)) - 0.01, 2),
        "referencia_local": "",
        "demanda": 3,
        "tela": p["tela"] or "Revisar composición en la ficha",
        "tallas": "Revisar tabla en cm",
        "buscar_en_temu": "",
        "url": p["url"],
        "ventas": int(p["vendidos"]),
        "rating": p["rating"] or None,
        "resenas": int(p["resenas"]),
        "resenas_con_foto": int(p["resenas_foto"]) if p["resenas_foto"] is not None else None,
        "puntaje": p["puntaje"],
    }


def correr_apify(actor, entrada, token):
    url = f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?token={token}&timeout=300"
    req = request.Request(url, data=json.dumps(entrada).encode(), headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=330) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    fuente = ap.add_mutually_exclusive_group(required=True)
    fuente.add_argument("--apify", action="store_true", help="Correr un actor de Apify (requiere APIFY_TOKEN)")
    fuente.add_argument("--desde-archivo", type=Path, help="Procesar un JSON ya descargado")
    ap.add_argument("--actor", default="apivault_labs~temu-product-scraper")
    ap.add_argument("--entrada", type=Path, help="JSON de entrada para el actor (si el formato por defecto no sirve)")
    ap.add_argument("--max", type=int, default=40, help="Productos por búsqueda")
    ap.add_argument("--top", type=int, default=20, help="Cuántos productos guardar")
    ap.add_argument("--min-rating", type=float, default=4.5)
    ap.add_argument("--min-vendidos", type=int, default=500)
    ap.add_argument("--salida", type=Path, default=BASE / "datos" / "productos.json")
    args = ap.parse_args()

    if args.apify:
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            sys.exit("Falta APIFY_TOKEN. Créalo en https://console.apify.com/account/integrations")
        entrada = (json.loads(args.entrada.read_text(encoding="utf-8")) if args.entrada
                   else {"searchQueries": BUSQUEDAS, "maxItems": args.max, "country": "EC"})
        crudos = correr_apify(args.actor, entrada, token)
    else:
        crudos = json.loads(args.desde_archivo.read_text(encoding="utf-8"))
        if isinstance(crudos, dict):
            crudos = crudos.get("items") or crudos.get("productos") or []

    vistos, productos = set(), []
    for item in crudos:
        p = normalizar(item)
        clave = p["url"] or p["titulo"].lower()
        if not p["titulo"] or clave in vistos or not es_de_la_edad(p):
            continue
        vistos.add(clave)
        if p["rating"] and p["rating"] < args.min_rating:
            continue
        if p["vendidos"] < args.min_vendidos:
            continue
        productos.append(p)

    if not productos:
        sys.exit("Ningún producto pasó los filtros. Baja --min-vendidos o --min-rating, o revisa el formato del archivo.")

    max_v = max(p["vendidos"] for p in productos)
    max_r = max(p["resenas"] for p in productos)
    for p in productos:
        p["puntaje"] = puntaje(p, max_v, max_r)
    productos.sort(key=lambda p: p["puntaje"], reverse=True)

    salida = {
        "fuente": "apify" if args.apify else str(args.desde_archivo),
        "nota": "Pesos en 180 g por defecto y precio de venta a 2,5x: ajústalos en el dashboard.",
        "productos": [a_formato_dashboard(p, i) for i, p in enumerate(productos[: args.top])],
    }
    args.salida.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(productos)} productos pasaron los filtros; guardé los {min(args.top, len(productos))} mejores en {args.salida}")
    for p in productos[:10]:
        print(f"  {p['puntaje']:5.1f}  ${p['precio'] or 0:6.2f}  {int(p['vendidos']):>7} vendidos  ★{p['rating'] or '-'}  {p['titulo'][:60]}")


if __name__ == "__main__":
    main()
