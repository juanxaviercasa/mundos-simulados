"""
Lee lo que pegaste de la respuesta de Gemini para un lote, separa cada
artículo por sus marcas ===INICIO SLUG:...=== / ===FIN SLUG:...===, y
escribe un .md por artículo en articulos/ con el mismo front matter que
antes (título, meta descripción, tags, imágenes...). A partir de aquí
02_publicar_wordpress.py funciona exactamente igual que si el texto hubiera
salido de la API.

Cruza el resultado contra el manifiesto del lote para avisarte si Gemini se
saltó algún artículo o si aparece uno que no pediste.

Uso:
    python3 01b_importar_lote.py --lote 1
    python3 01b_importar_lote.py --lote 1 --forzar   # sobrescribir si ya existían
"""

import argparse
import json
import os
import re
import sys

import frontmatter
import pandas as pd

CSV_PATH = os.environ.get("CSV_PATH", "Estructura_Mundos_Simulados_-_contenido.csv")
CARPETA_ARTICULOS = "articulos"
CARPETA_LOTES = "lotes"
CARPETA_RESPUESTAS = "respuestas"

PATRON_BLOQUE = re.compile(
    r"===\s*INICIO\s*SLUG:\s*(?P<slug>[a-z0-9\-]+)\s*===(?P<cuerpo>.*?)===\s*FIN\s*SLUG:\s*(?P=slug)\s*===",
    re.DOTALL | re.IGNORECASE,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", type=int, required=True)
    ap.add_argument("--forzar", action="store_true", help="sobrescribir .md que ya existan")
    args = ap.parse_args()

    nombre_lote = f"lote_{args.lote:02d}"
    ruta_manifiesto = os.path.join(CARPETA_LOTES, f"{nombre_lote}_manifest.json")
    ruta_respuesta = os.path.join(CARPETA_RESPUESTAS, f"{nombre_lote}_respuesta.txt")

    if not os.path.exists(ruta_manifiesto):
        sys.exit(f"No encuentro {ruta_manifiesto}. Corre primero 01a_generar_prompt_lote.py")
    if not os.path.exists(ruta_respuesta):
        sys.exit(
            f"No encuentro {ruta_respuesta}.\n"
            f"Crea la carpeta 'respuestas' si no existe y guarda ahí el texto que "
            f"copiaste de Gemini con ese nombre exacto."
        )

    with open(ruta_manifiesto, encoding="utf-8") as f:
        manifiesto = json.load(f)
    esperados = set(manifiesto["slugs"])

    with open(ruta_respuesta, encoding="utf-8") as f:
        texto = f.read()

    encontrados = {}
    for m in PATRON_BLOQUE.finditer(texto):
        slug = m.group("slug").strip()
        cuerpo = m.group("cuerpo").strip()
        encontrados[slug] = cuerpo

    faltantes = esperados - encontrados.keys()
    sobrantes = encontrados.keys() - esperados

    print(f"Esperados en el lote: {len(esperados)}")
    print(f"Encontrados en la respuesta: {len(encontrados)}")
    if faltantes:
        print(f"FALTAN (Gemini no los escribió o cambió el slug): {sorted(faltantes)}")
    if sobrantes:
        print(f"De más (no estaban en el manifiesto, se importan igual): {sorted(sobrantes)}")

    if not encontrados:
        sys.exit(
            "\nNo se reconoció ningún bloque ===INICIO SLUG:...=== / ===FIN SLUG:...===\n"
            "Revisa que hayas pegado la respuesta completa de Gemini, incluidas esas marcas."
        )

    df = pd.read_csv(CSV_PATH).set_index("URL Slug (Post)")
    os.makedirs(CARPETA_ARTICULOS, exist_ok=True)

    escritos = 0
    for slug, cuerpo in encontrados.items():
        if slug not in df.index:
            print(f"  [salto] {slug}: ese slug no existe en el CSV, no sé qué SEO ponerle")
            continue

        ruta_md = os.path.join(CARPETA_ARTICULOS, f"{slug}.md")
        if os.path.exists(ruta_md) and not args.forzar:
            print(f"  [salto] {slug} (ya existe, usa --forzar para sobrescribir)")
            continue

        fila = df.loc[slug]
        tags = [t.strip() for t in str(fila["Etiquetas (Tags)"]).split(",") if t.strip()]

        post = frontmatter.Post(cuerpo)
        post["slug"] = slug
        post["categoria"] = fila["Categoría (Slug)"]
        post["title"] = fila["Tema General (H1)"]
        post["focus_keyword"] = fila["Palabra Clave"]
        post["meta_description"] = fila["Meta Descripción"]
        post["tags"] = tags
        post["imagen_destacada"] = fila["Archivo Destacada"]
        post["alt_destacada"] = fila["Alt Text Destacada"]
        post["imagen_interna_1"] = fila["Archivo Interna 1"]
        post["alt_interna_1"] = fila["Alt Text Interna 1"]
        post["imagen_interna_2"] = fila["Archivo Interna 2"]
        post["alt_interna_2"] = fila["Alt Text Interna 2"]

        with open(ruta_md, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        escritos += 1

    print(f"\n.md escritos en articulos/: {escritos}")
    if faltantes:
        print(
            f"\nPara completar los que faltaron, pídeselos a Gemini en el mismo chat "
            f"(\"continúa con los que falten: {', '.join(sorted(faltantes))}\"), "
            f"pega la respuesta agregándola AL FINAL de {ruta_respuesta}, y vuelve a "
            f"correr este mismo comando."
        )


if __name__ == "__main__":
    main()
