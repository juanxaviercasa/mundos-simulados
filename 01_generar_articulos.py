"""
Lee el CSV de Mundos Simulados y genera un artículo por fila con la API de
Gemini, usando un modelo Flash de la capa GRATUITA (sin tarjeta, sin costo).
Guarda cada uno como .md con front matter (todo el SEO) en articulos/.

Esto NO usa tu suscripción Gemini Pro del chat: usa una llave de API propia,
gratuita, de Google AI Studio. Son dos medidores separados, así que esto no
te consume nada de tus 100 prompts/día de Pro.

Si un .md ya existe para ese slug, la fila se salta: correr este script dos
veces no duplica trabajo. Usa --forzar para regenerar de todos modos.

Antes de correrlo:
  1. Entra a https://aistudio.google.com, crea una API key (no pide tarjeta).
  2. Revisa en la misma consola qué modelos Flash están en capa gratuita
     para tu cuenta/región ahora mismo, y cuál es tu límite de peticiones
     por minuto y por día. Estos números y estos nombres de modelo han
     cambiado varias veces en 2026, así que confía en lo que veas en tu
     propia consola, no en el valor por defecto de este script.
  3. Pon esa API key y ese nombre de modelo en tu .env.

Uso:
    python3 01_generar_articulos.py --limite 5 --categoria tecnologia
    python3 01_generar_articulos.py                     # las 240
    python3 01_generar_articulos.py --forzar --limite 3  # regenerar 3
"""

import argparse
import csv
import os
import sys
import time

import frontmatter
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    sys.exit("Falta la librería: pip install google-generativeai --break-system-packages")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Candidato de modelo Flash gratuito al momento de escribir esto (agosto 2026).
# CONFIRMA en aistudio.google.com cuál te aparece a ti en capa gratuita.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
CSV_PATH = os.environ.get("CSV_PATH", "Estructura_Mundos_Simulados_-_contenido.csv")
CARPETA_ARTICULOS = "articulos"
LOG_PATH = "generacion_log.csv"

if not GEMINI_API_KEY:
    sys.exit(
        "Falta GEMINI_API_KEY en tu .env\n"
        "Sácala gratis en https://aistudio.google.com (no pide tarjeta)."
    )

with open("prompt_maestro_articulo.txt", encoding="utf-8") as f:
    PROMPT_MAESTRO = f.read()

genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel(GEMINI_MODEL, system_instruction=PROMPT_MAESTRO)


def parsear_lista(celda, prefijo):
    """'H2: A; H2: B' -> ['A', 'B']. Sirve tanto para H2 como para viñetas."""
    if not isinstance(celda, str) or not celda.strip():
        return []
    partes = [p.strip() for p in celda.split(";")]
    limpias = []
    for p in partes:
        if p.startswith(prefijo):
            p = p[len(prefijo):].strip()
        limpias.append(p)
    return [p for p in limpias if p]


def construir_prompt_usuario(fila):
    h2s = parsear_lista(fila["Estructura H2 Magnéticos"], "H2:")
    vinetas = parsear_lista(fila["Viñetas de Resumen"], "-")

    partes = [
        f"H1 del artículo (no lo repitas en el cuerpo): {fila['Tema General (H1)']}",
        f"Palabra clave objetivo: {fila['Palabra Clave']}",
        "",
        "Estructura de H2 obligatoria, en este orden:",
    ]
    partes += [f"- {h}" for h in h2s]
    partes.append("")
    partes.append("Ideas clave que el artículo debe cubrir (no las copies literal, desarróllalas):")
    partes += [f"- {v}" for v in vinetas]
    partes.append("")
    partes.append(f"Contexto de la imagen interna 1 (para ubicarla con sentido): {fila['Alt Text Interna 1']}")
    partes.append(f"Contexto de la imagen interna 2 (para ubicarla con sentido): {fila['Alt Text Interna 2']}")
    return "\n".join(partes)


def es_error_de_cuota(e):
    texto = str(e).lower()
    return any(s in texto for s in ["429", "quota", "rate limit", "resource_exhausted"])


def generar_cuerpo(prompt_usuario, reintentos=4):
    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            respuesta = modelo.generate_content(prompt_usuario)
            texto = (respuesta.text or "").strip()
            if not texto:
                raise ValueError("Gemini devolvió una respuesta vacía")
            return texto
        except Exception as e:  # noqa: BLE001 — capturamos cualquier fallo de red/API/cuota
            ultimo_error = e
            if es_error_de_cuota(e):
                # la capa gratuita es la que tiene el límite estricto de
                # peticiones por minuto; una espera corta casi nunca alcanza
                espera = 60 * intento
                print(f"    límite de la capa gratuita alcanzado, espero {espera}s (intento {intento})")
            else:
                espera = 5 * intento
                print(f"    intento {intento} falló ({e}); reintento en {espera}s")
            time.sleep(espera)
    raise RuntimeError(f"Sin éxito tras {reintentos} intentos: {ultimo_error}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=None, help="máximo de artículos a generar en esta corrida")
    ap.add_argument("--categoria", type=str, default=None, help="filtrar por Categoría (Slug)")
    ap.add_argument("--forzar", action="store_true", help="regenerar aunque el .md ya exista")
    ap.add_argument(
        "--pausa", type=float, default=4.0,
        help="segundos de espera entre llamadas (la capa gratuita tiene RPM más bajo que la de pago)",
    )
    args = ap.parse_args()

    os.makedirs(CARPETA_ARTICULOS, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    if args.categoria:
        df = df[df["Categoría (Slug)"] == args.categoria]

    log_nuevo = not os.path.exists(LOG_PATH)
    log_f = open(LOG_PATH, "a", newline="", encoding="utf-8")
    log_w = csv.writer(log_f)
    if log_nuevo:
        log_w.writerow(["slug", "estado", "detalle"])

    generados = 0
    for _, fila in df.iterrows():
        if args.limite is not None and generados >= args.limite:
            break

        slug = str(fila["URL Slug (Post)"]).strip()
        ruta_md = os.path.join(CARPETA_ARTICULOS, f"{slug}.md")

        if os.path.exists(ruta_md) and not args.forzar:
            print(f"[salto] {slug} (ya existe)")
            continue

        print(f"[generando] {slug}")
        try:
            prompt_usuario = construir_prompt_usuario(fila)
            cuerpo = generar_cuerpo(prompt_usuario)

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

            log_w.writerow([slug, "ok", ""])
            log_f.flush()
            generados += 1
        except Exception as e:  # noqa: BLE001
            print(f"    ERROR: {e}")
            log_w.writerow([slug, "error", str(e)])
            log_f.flush()

        time.sleep(args.pausa)

    log_f.close()
    print(f"\nGenerados en esta corrida: {generados}")
    print(f"Revisa {LOG_PATH} si algo falló.")


if __name__ == "__main__":
    main()
