"""
Arma UN solo bloque de texto con N artículos del CSV (10, 20, los que
quieras) para que lo pegues directo en un chat nuevo de Gemini. No llama a
ninguna API, no gasta nada: solo prepara el texto.

También escribe un manifiesto (lote_XX_manifest.json) con la lista exacta de
slugs que deberían venir en la respuesta, para que 01b_importar_lote.py
pueda avisarte si Gemini se saltó alguno.

Uso:
    python3 01a_generar_prompt_lote.py --cantidad 10
    python3 01a_generar_prompt_lote.py --cantidad 20 --categoria biosfera
    python3 01a_generar_prompt_lote.py --cantidad 10 --lote 3   # numerarlo tú mismo
"""

import argparse
import glob
import json
import os

import pandas as pd

CSV_PATH = os.environ.get("CSV_PATH", "Estructura_Mundos_Simulados_-_contenido.csv")
CARPETA_ARTICULOS = "articulos"
CARPETA_LOTES = "lotes"

with open("prompt_maestro_articulo.txt", encoding="utf-8") as f:
    PROMPT_MAESTRO = f.read()


def parsear_lista(celda, prefijo):
    if not isinstance(celda, str) or not celda.strip():
        return []
    partes = [p.strip() for p in celda.split(";")]
    limpias = []
    for p in partes:
        if p.startswith(prefijo):
            p = p[len(prefijo):].strip()
        limpias.append(p)
    return [p for p in limpias if p]


def bloque_para_fila(fila):
    h2s = parsear_lista(fila["Estructura H2 Magnéticos"], "H2:")
    vinetas = parsear_lista(fila["Viñetas de Resumen"], "-")
    partes = [
        f"SLUG: {fila['URL Slug (Post)']}",
        f"H1 (no lo repitas en el cuerpo): {fila['Tema General (H1)']}",
        f"Palabra clave objetivo: {fila['Palabra Clave']}",
        "Estructura de H2 obligatoria, en este orden:",
    ]
    partes += [f"  - {h}" for h in h2s]
    partes.append("Ideas clave a desarrollar (no las copies literal):")
    partes += [f"  - {v}" for v in vinetas]
    partes.append(f"Contexto imagen interna 1: {fila['Alt Text Interna 1']}")
    partes.append(f"Contexto imagen interna 2: {fila['Alt Text Interna 2']}")
    return "\n".join(partes)


def siguiente_numero_lote():
    existentes = glob.glob(os.path.join(CARPETA_LOTES, "lote_*.txt"))
    numeros = []
    for e in existentes:
        base = os.path.basename(e).replace("lote_", "").replace(".txt", "")
        if base.isdigit():
            numeros.append(int(base))
    return max(numeros, default=0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cantidad", type=int, default=10, help="cuántos artículos incluir en este lote")
    ap.add_argument("--categoria", type=str, default=None, help="filtrar por Categoría (Slug)")
    ap.add_argument("--lote", type=int, default=None, help="número de lote (si no lo pones, se autoincrementa)")
    args = ap.parse_args()

    os.makedirs(CARPETA_LOTES, exist_ok=True)
    os.makedirs(CARPETA_ARTICULOS, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    if args.categoria:
        df = df[df["Categoría (Slug)"] == args.categoria]

    ya_generados = {
        os.path.basename(p)[:-3] for p in glob.glob(os.path.join(CARPETA_ARTICULOS, "*.md"))
    }
    pendientes = df[~df["URL Slug (Post)"].isin(ya_generados)]

    if pendientes.empty:
        print("No quedan filas pendientes con ese filtro. Todo ya tiene su .md en articulos/.")
        return

    seleccion = pendientes.head(args.cantidad)
    numero = args.lote if args.lote is not None else siguiente_numero_lote()
    nombre_lote = f"lote_{numero:02d}"

    bloques = [bloque_para_fila(fila) for _, fila in seleccion.iterrows()]

    instrucciones_formato = f"""
Vas a escribir {len(bloques)} artículos. Para CADA UNO, sin excepción, envuelve
el resultado exactamente así, con el slug real en la marca de inicio y fin:

===INICIO SLUG: <slug-del-articulo>===
(aquí el cuerpo completo del artículo en Markdown)
===FIN SLUG: <slug-del-articulo>===

No agregues nada entre un bloque y el siguiente aparte de esas marcas. No
uses bloques de código con triple acento grave alrededor de toda la
respuesta. Genera los {len(bloques)} artículos completos, uno tras otro, sin
resumir ninguno ni saltarte ninguno.
""".strip()

    prompt_final = (
        PROMPT_MAESTRO
        + "\n\n---\n\n"
        + instrucciones_formato
        + "\n\n---\n\nARTÍCULOS A ESCRIBIR EN ESTE LOTE:\n\n"
        + "\n\n---\n\n".join(bloques)
    )

    ruta_prompt = os.path.join(CARPETA_LOTES, f"{nombre_lote}.txt")
    with open(ruta_prompt, "w", encoding="utf-8") as f:
        f.write(prompt_final)

    manifiesto = {
        "lote": nombre_lote,
        "slugs": seleccion["URL Slug (Post)"].tolist(),
    }
    ruta_manifiesto = os.path.join(CARPETA_LOTES, f"{nombre_lote}_manifest.json")
    with open(ruta_manifiesto, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=2)

    print(f"Listo: {ruta_prompt}")
    print(f"Incluye {len(bloques)} artículos: {', '.join(manifiesto['slugs'])}")
    print("\nSiguiente paso:")
    print(f"  1. Abre {ruta_prompt}, copia TODO el contenido.")
    print("  2. Pégalo en un chat NUEVO de Gemini.")
    print("  3. Copia TODA la respuesta de Gemini (no hace falta que la limpies).")
    print(f"  4. Guárdala en: respuestas/{nombre_lote}_respuesta.txt")
    print(f"  5. Corre: python3 01b_importar_lote.py --lote {numero}")


if __name__ == "__main__":
    main()
