"""Genera dashboard/index.html con los datos de datos/productos.json.

Uso:
    python negocio-kids/herramientas/construir_dashboard.py
    python negocio-kids/herramientas/construir_dashboard.py --datos otra_ruta.json --fragmento salida.html
"""
import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MARCA = "__PRODUCTOS_JSON__"


def construir(ruta_datos: Path) -> str:
    datos = json.loads(ruta_datos.read_text(encoding="utf-8"))
    if isinstance(datos, list):
        datos = {"productos": datos}
    plantilla = (BASE / "dashboard" / "plantilla.html").read_text(encoding="utf-8")
    # Evita que un texto con "</script>" cierre el bloque del dashboard
    incrustado = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    return plantilla.replace(MARCA, incrustado)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", type=Path, default=BASE / "datos" / "productos.json")
    ap.add_argument("--salida", type=Path, default=BASE / "dashboard" / "index.html")
    ap.add_argument("--fragmento", type=Path, help="Además guarda el HTML sin <html>/<head> (para publicarlo como Artifact)")
    args = ap.parse_args()

    fragmento = construir(args.datos)
    pagina = (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "</head>\n<body>\n" + fragmento + "\n</body>\n</html>\n"
    )
    args.salida.write_text(pagina, encoding="utf-8")
    print(f"Dashboard generado: {args.salida}")
    if args.fragmento:
        args.fragmento.write_text(fragmento, encoding="utf-8")
        print(f"Fragmento generado: {args.fragmento}")


if __name__ == "__main__":
    main()
