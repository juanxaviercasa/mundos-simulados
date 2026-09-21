"""
Lee los .md de articulos/, resuelve categoría y etiquetas contra tu
WordPress, reemplaza los dos marcadores de imagen interna por bloques de
imagen reales usando media_map.json, y envía el post como borrador.

Si el slug ya existe en WordPress, se salta (usa --actualizar para
sobrescribirlo en vez de saltarlo). Si a un artículo le falta cualquiera de
sus tres imágenes en media_map.json, se salta y queda registrado: nunca se
publica un post con una imagen rota.

Uso:
    python3 02_publicar_wordpress.py --limite 5 --seco   # revisar sin enviar
    python3 02_publicar_wordpress.py --limite 5           # publicar 5 de verdad
    python3 02_publicar_wordpress.py                      # las que falten, todas
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

import frontmatter
import markdown as md
import requests
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
WP_SEO_PLUGIN = os.environ.get("WP_SEO_PLUGIN", "rankmath").lower()
CARPETA_ARTICULOS = "articulos"
LOG_PATH = "publicacion_log.csv"

if not (WP_URL and WP_USER and WP_APP_PASSWORD):
    sys.exit("Faltan WP_URL, WP_USER o WP_APP_PASSWORD en tu .env")

AUTH = (WP_USER, WP_APP_PASSWORD)

if not os.path.exists("media_map.json"):
    sys.exit("No existe media_map.json. Corre primero 00_mapa_imagenes.py")
with open("media_map.json", encoding="utf-8") as f:
    MEDIA_MAP = json.load(f)

_cache_categorias = {}
_cache_tags = {}


def id_categoria(slug):
    if slug in _cache_categorias:
        return _cache_categorias[slug]
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories", params={"slug": slug}, auth=AUTH, timeout=30)
    r.raise_for_status()
    datos = r.json()
    if not datos:
        raise ValueError(f"La categoría '{slug}' no existe en WordPress. Créala primero.")
    _cache_categorias[slug] = datos[0]["id"]
    return _cache_categorias[slug]


def id_tag(nombre):
    if nombre in _cache_tags:
        return _cache_tags[nombre]
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/tags", params={"search": nombre}, auth=AUTH, timeout=30)
    r.raise_for_status()
    for t in r.json():
        if t["name"].lower() == nombre.lower():
            _cache_tags[nombre] = t["id"]
            return t["id"]
    # no existe todavía, se crea
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/tags", json={"name": nombre}, auth=AUTH, timeout=30)
    r.raise_for_status()
    tid = r.json()["id"]
    _cache_tags[nombre] = tid
    return tid


def post_existente(slug):
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts", params={"slug": slug, "status": "any"}, auth=AUTH, timeout=30)
    r.raise_for_status()
    datos = r.json()
    return datos[0]["id"] if datos else None


def bloque_imagen(info, alt):
    return (
        '<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
        '<figure class="wp-block-image size-large">'
        '<img src="%s" alt="%s" class="wp-image-%d" loading="lazy"/>'
        "</figure>\n"
        "<!-- /wp:image -->"
    ) % (info["id"], info["url"], alt.replace('"', "&quot;"), info["id"])


def construir_html(cuerpo_md, meta):
    html = md.markdown(cuerpo_md, extensions=["extra"])

    for marcador, archivo_key, alt_key in [
        ("IMAGEN_INTERNA_1", "imagen_interna_1", "alt_interna_1"),
        ("IMAGEN_INTERNA_2", "imagen_interna_2", "alt_interna_2"),
    ]:
        archivo = meta[archivo_key]
        info = MEDIA_MAP.get(archivo)
        bloque = bloque_imagen(info, meta[alt_key])
        patron_con_parrafo = re.compile(r"<p>\s*\{\{" + marcador + r"\}\}\s*</p>")
        if patron_con_parrafo.search(html):
            html = patron_con_parrafo.sub(bloque, html)
        else:
            html = html.replace("{{" + marcador + "}}", bloque)

    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=None)
    ap.add_argument("--categoria", type=str, default=None, help="filtra por categoria del front matter")
    ap.add_argument("--seco", action="store_true", help="arma el post y lo imprime, no lo envía")
    ap.add_argument("--actualizar", action="store_true", help="si el slug ya existe, sobrescribirlo")
    args = ap.parse_args()

    rutas = sorted(glob.glob(os.path.join(CARPETA_ARTICULOS, "*.md")))
    log_nuevo = not os.path.exists(LOG_PATH)
    log_f = open(LOG_PATH, "a", newline="", encoding="utf-8")
    log_w = csv.writer(log_f)
    if log_nuevo:
        log_w.writerow(["slug", "estado", "detalle"])

    publicados = 0
    for ruta in rutas:
        if args.limite is not None and publicados >= args.limite:
            break

        post = frontmatter.load(ruta)
        meta = post.metadata
        slug = meta["slug"]

        if args.categoria and meta.get("categoria") != args.categoria:
            continue

        # --- verificar que las tres imágenes existan en el mapa ---
        faltan = [
            meta[k] for k in ("imagen_destacada", "imagen_interna_1", "imagen_interna_2")
            if meta[k] not in MEDIA_MAP
        ]
        if faltan:
            print(f"[salto] {slug}: faltan en media_map.json -> {faltan}")
            log_w.writerow([slug, "salto_imagenes", ";".join(faltan)])
            continue

        existente = post_existente(slug)
        if existente and not args.actualizar:
            print(f"[salto] {slug} (ya publicado, id {existente})")
            continue

        try:
            cat_id = id_categoria(meta["categoria"])
            tag_ids = [id_tag(t) for t in meta.get("tags", [])]
            html = construir_html(post.content, meta)
            destacada_id = MEDIA_MAP[meta["imagen_destacada"]]["id"]

            payload = {
                "title": meta["title"],
                "slug": slug,
                "status": "draft",
                "content": html,
                "categories": [cat_id],
                "tags": tag_ids,
                "featured_media": destacada_id,
            }

            if WP_SEO_PLUGIN == "rankmath":
                payload["meta"] = {
                    "rank_math_title": meta["title"],
                    "rank_math_description": meta["meta_description"],
                    "rank_math_focus_keyword": meta["focus_keyword"],
                }
            elif WP_SEO_PLUGIN == "yoast":
                payload["meta"] = {
                    "_yoast_wpseo_title": meta["title"],
                    "_yoast_wpseo_metadesc": meta["meta_description"],
                    "_yoast_wpseo_focuskw": meta["focus_keyword"],
                }

            if args.seco:
                print(f"\n[seco] {slug}")
                print(json.dumps({**payload, "content": html[:300] + "..."}, ensure_ascii=False, indent=2))
                publicados += 1
                continue

            if existente:
                r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{existente}", json=payload, auth=AUTH, timeout=60)
            else:
                r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", json=payload, auth=AUTH, timeout=60)
            r.raise_for_status()
            nuevo_id = r.json()["id"]
            print(f"[ok] {slug} -> post id {nuevo_id} ({WP_URL}/wp-admin/post.php?post={nuevo_id}&action=edit)")
            log_w.writerow([slug, "ok", str(nuevo_id)])
            log_f.flush()
            publicados += 1

        except Exception as e:  # noqa: BLE001
            print(f"[error] {slug}: {e}")
            log_w.writerow([slug, "error", str(e)])
            log_f.flush()

    log_f.close()
    print(f"\n{'Simulados' if args.seco else 'Publicados'} en esta corrida: {publicados}")
    print(f"Revisa {LOG_PATH} si algo falló o se saltó.")


if __name__ == "__main__":
    main()
