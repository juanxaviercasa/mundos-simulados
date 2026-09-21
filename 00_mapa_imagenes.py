"""
Recorre la biblioteca de medios de WordPress y arma un mapa
  nombre_de_archivo.webp -> {"id": 123, "url": "https://.../archivo.webp"}
guardado en media_map.json.

También compara ese mapa contra las 720 rutas de imagen que pide el CSV
(destacada + interna 1 + interna 2 por cada uno de los 240 artículos) y te
dice cuántas encontró y cuáles faltan, para que lo corrijas antes de generar
o publicar nada.

Uso:
    python3 00_mapa_imagenes.py
"""

import json
import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
CSV_PATH = os.environ.get("CSV_PATH", "Estructura_Mundos_Simulados_-_contenido.csv")

if not (WP_URL and WP_USER and WP_APP_PASSWORD):
    sys.exit("Faltan WP_URL, WP_USER o WP_APP_PASSWORD en tu .env")

AUTH = (WP_USER, WP_APP_PASSWORD)


def descargar_biblioteca_medios():
    """Pagina /wp/v2/media hasta traer todo. Devuelve una lista de items."""
    items = []
    pagina = 1
    while True:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/media",
            params={"per_page": 100, "page": pagina},
            auth=AUTH,
            timeout=30,
        )
        if resp.status_code == 400 and pagina > 1:
            # WordPress devuelve 400 "rest_post_invalid_page_number"
            # cuando ya no hay más páginas.
            break
        resp.raise_for_status()
        lote = resp.json()
        if not lote:
            break
        items.extend(lote)
        print(f"  página {pagina}: {len(lote)} elementos")
        pagina += 1
    return items


def main():
    print("Descargando biblioteca de medios de WordPress...")
    items = descargar_biblioteca_medios()
    print(f"Total en la biblioteca: {len(items)} elementos\n")

    mapa = {}
    for item in items:
        url = item.get("source_url", "")
        nombre = os.path.basename(url.split("?")[0])
        mapa[nombre] = {"id": item["id"], "url": url}

    with open("media_map.json", "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=2)
    print(f"media_map.json escrito con {len(mapa)} archivos.\n")

    # --- Cruce contra lo que pide el CSV ---
    if not os.path.exists(CSV_PATH):
        print(f"Aviso: no encontré {CSV_PATH} en esta carpeta, salto la verificación.")
        return

    df = pd.read_csv(CSV_PATH)
    esperadas = set()
    for col in ["Archivo Destacada", "Archivo Interna 1", "Archivo Interna 2"]:
        esperadas.update(df[col].dropna().astype(str).str.strip())

    faltantes = sorted(n for n in esperadas if n not in mapa)
    encontradas = len(esperadas) - len(faltantes)

    print(f"El CSV pide {len(esperadas)} archivos de imagen distintos.")
    print(f"  Encontrados en la biblioteca: {encontradas}")
    print(f"  Faltantes: {len(faltantes)}")
    if faltantes:
        print("\nPrimeros 20 faltantes:")
        for n in faltantes[:20]:
            print(f"  - {n}")
        with open("imagenes_faltantes.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(faltantes))
        print(f"\nLista completa en imagenes_faltantes.txt ({len(faltantes)} archivos).")
        print("Súbelas a la biblioteca de medios antes de publicar esos artículos.")


if __name__ == "__main__":
    main()
