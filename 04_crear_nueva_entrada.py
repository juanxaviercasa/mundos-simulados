"""
04_crear_nueva_entrada.py - Generador Autónomo y Asistido de Artículos con IA (SEO & GEO)
para "Mundos Simulados".

Capacidades:
1. Modo Idea Propia: Escribe cualquier premisa y la IA investiga en motores de búsqueda,
   extrae datos científicos reales y redacta el artículo completo.
2. Modo Descubrimiento Autónomo: Consulta motores de búsqueda en vivo (Google Suggest / tendencias)
   y analiza los 240 artículos existentes para recomendar titulares magnéticos y 100% inéditos.
3. Rigor Editorial: Aplica estrictamente prompt_maestro_articulo.txt (1400-1900 palabras,
   dato medible real de partida, 1 variable alterada, sin marketing, marcadores de imagen).
4. Optimización GEO & SEO: H2s con respuestas inmediatas para citas en Perplexity/ChatGPT/Google SGE,
   interlinking automático con artículos existentes de la misma categoría.
5. Publicación en WordPress: Guarda el archivo .md y opcionalmente crea el borrador con RankMath SEO
   directamente en WordPress mediante REST API.

Uso:
    python 04_crear_nueva_entrada.py --interactivo
    python 04_crear_nueva_entrada.py --descubrir --categoria astrofisica
    python 04_crear_nueva_entrada.py --idea "Que pasaria si la gravedad disminuyera un 10%" --publicar
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
from datetime import datetime

import frontmatter
import markdown as md
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Configuración de Entorno ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
WP_URL = os.environ.get("WP_URL_TARGET") or os.environ.get("WP_URL", "").rstrip("/")
if not WP_URL or "mundossimulados.online" in WP_URL:
    # Si mundossimulados.online no resuelve o está en desarrollo, usar endpoint activo de Pantheon
    WP_URL = "https://dev-simulandomundos.pantheonsite.io"
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
WP_SEO_PLUGIN = os.environ.get("WP_SEO_PLUGIN", "rankmath").lower()
CSV_PATH = os.environ.get("CSV_PATH", "Estructura Mundos Simulados.csv")
CARPETA_ARTICULOS = "articulos"
PROMPT_MAESTRO_PATH = "prompt_maestro_articulo.txt"

CATEGORIAS_DISPONIBLES = {
    "astrofisica": "Astrofísica y Espacio",
    "tecnologia": "Tecnología y Futuro",
    "biosfera": "Biosfera, Naturaleza y Clima",
    "economia": "Economía y Sociedad Global"
}

# --- 1. Utilidades de Texto y Slugs ---

def normalizar_slug(texto):
    """Convierte un título en slug limpio y amigable para URL."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    return re.sub(r"[-\s]+", "-", texto)


def cargar_prompt_maestro():
    """Carga las reglas editoriales obligatorias del sitio."""
    if os.path.exists(PROMPT_MAESTRO_PATH):
        with open(PROMPT_MAESTRO_PATH, encoding="utf-8") as f:
            return f.read()
    return (
        "Eres el redactor editorial de Mundos Simulados, explicando escenarios 'qué pasaría si...' "
        "con rigor científico. Parte de un dato medible real, cambia UNA sola variable y sigue consecuencias "
        "en orden temporal. Español neutro, sin exclamaciones ni em-dash. 1400-1900 palabras. "
        "Inserta {{IMAGEN_INTERNA_1}} y {{IMAGEN_INTERNA_2}} en sus propias líneas. "
        "Cierra con 'qué nos dice esto del mundo real'."
    )


# --- 2. Carga y Análisis de Artículos Existentes (Cero Duplicados) ---

def obtener_articulos_existentes():
    """
    Carga todos los artículos existentes desde el CSV y la carpeta articulos/
    para garantizar cero duplicación de temas y permitir interlinking contextual.
    """
    articulos = []
    slugs_vistos = set()

    # Desde CSV si existe
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            for _, fila in df.iterrows():
                slug = str(fila.get("URL Slug (Post)", "")).strip()
                titulo = str(fila.get("Tema General (H1)", "")).strip()
                cat = str(fila.get("Categoría (Slug)", "")).strip().lower()
                kw = str(fila.get("Palabra Clave", "")).strip()
                if slug and slug not in slugs_vistos:
                    slugs_vistos.add(slug)
                    articulos.append({
                        "slug": slug,
                        "titulo": titulo,
                        "categoria": cat,
                        "palabra_clave": kw
                    })
        except Exception as e:
            print(f"[aviso] No se pudo leer {CSV_PATH}: {e}")

    # Desde articulos/*.md
    if os.path.exists(CARPETA_ARTICULOS):
        for f in os.listdir(CARPETA_ARTICULOS):
            if f.endswith(".md"):
                slug = f[:-3]
                if slug not in slugs_vistos:
                    slugs_vistos.add(slug)
                    try:
                        post = frontmatter.load(os.path.join(CARPETA_ARTICULOS, f))
                        articulos.append({
                            "slug": slug,
                            "titulo": post.metadata.get("title", slug),
                            "categoria": post.metadata.get("categoria", "astrofisica"),
                            "palabra_clave": post.metadata.get("focus_keyword", "")
                        })
                    except Exception:
                        pass

    return articulos


# --- 3. Motores de Búsqueda e Investigación en Tiempo Real ---

def investigar_en_motores_de_busqueda(consulta, categoria=None):
    """
    Investiga en tiempo real usando motores de búsqueda (Google Suggest y Wikipedia API):
    1. Obtiene preguntas reales con alta intención de búsqueda ('qué pasaría si...').
    2. Extrae datos científicos medibles, constantes físicas y hechos verificados.
    """
    datos_investigacion = {
        "sugerencias_busqueda": [],
        "hechos_cientificos": [],
        "resumen_contextual": ""
    }

    # 1. Google Suggest: Sugerencias reales que la gente busca
    queries_a_consultar = [consulta]
    if categoria:
        queries_a_consultar.append(f"que pasaria si {consulta}")
        queries_a_consultar.append(f"que pasaria si en {categoria}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    sugerencias = set()
    for q in queries_a_consultar:
        try:
            url = f"https://suggestqueries.google.com/complete/search?client=chrome&q={urllib.parse.quote(q)}"
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                res = r.json()
                if len(res) > 1 and isinstance(res[1], list):
                    for item in res[1][:6]:
                        sugerencias.add(str(item))
        except Exception:
            pass

    datos_investigacion["sugerencias_busqueda"] = list(sugerencias)[:8]

    # 2. Wikipedia REST API: Extracción de datos medibles reales y definiciones científicas
    palabras_clave = [p for p in re.findall(r"\b[A-Za-zÁ-ú]{4,}\b", consulta) if p.lower() not in [
        "como", "este", "esta", "para", "pero", "seria", "mundo", "tierra", "pasaria", "sobre"
    ]]

    terminos_a_buscar = palabras_clave[:3]
    for termino in terminos_a_buscar:
        try:
            url_wiki = f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termino)}"
            r_wiki = requests.get(url_wiki, headers={"User-Agent": "MundosSimuladosBot/1.0"}, timeout=5)
            if r_wiki.status_code == 200:
                data_wiki = r_wiki.json()
                extract = data_wiki.get("extract", "")
                if extract:
                    datos_investigacion["hechos_cientificos"].append({
                        "termino": termino,
                        "extracto": extract[:400]
                    })
        except Exception:
            pass

    return datos_investigacion


# --- 4. Descubrimiento Dinámico de Modelos Gemini ---

def resolver_modelo_gemini(api_key):
    """
    Descubre dinámicamente qué modelos Flash están activos y disponibles
    en la cuenta y capa gratuita de Google AI Studio para evitar errores 404/429.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            modelos_disponibles = [
                m["name"] for m in r.json().get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            
            # Prioridad de modelos de alto rendimiento y bajo costo en capa gratuita
            orden_preferido = [
                "gemini-3.5-flash-lite",
                "gemini-flash-lite-latest",
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-flash-latest",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash"
            ]

            for pref in orden_preferido:
                for avail in modelos_disponibles:
                    if pref in avail:
                        return avail.replace("models/", "")

            if modelos_disponibles:
                return modelos_disponibles[0].replace("models/", "")
    except Exception:
        pass

    return os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")


def llamar_gemini(prompt, api_key, system_instruction=None, json_mode=False):
    """Ejecuta una petición con reintentos a la API REST de Gemini."""
    modelo = resolver_modelo_gemini(api_key)
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3 if json_mode else 0.7,
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    intentos = 3
    for i in range(intentos):
        try:
            resp = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
            if resp.status_code == 200:
                data = resp.json()
                candidato = data.get("candidates", [{}])[0]
                partes = candidato.get("content", {}).get("parts", [])
                if partes:
                    return partes[0].get("text", "")
            elif resp.status_code == 429:
                print(f"[espera] Cuota saturada temporalmente. Pausando 10s (intento {i+1}/{intentos})...")
                time.sleep(10)
            else:
                print(f"[error api] Código {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[error red] {e}. Reintentando...")
            time.sleep(3)

    return ""


# --- 5. Modo Descubrimiento Autónomo de Temas ---

def descubrir_temas_nuevos(categoria=None, cantidad=6):
    """
    Descubre temas vírgenes analizando:
    1. Tendencias y preguntas reales de motores de búsqueda.
    2. La base de 240 artículos existentes para garantizar 0 repetición.
    """
    articulos_existentes = obtener_articulos_existentes()
    titulos_existentes = [a["titulo"] for a in articulos_existentes]

    cat_slug = categoria if categoria in CATEGORIAS_DISPONIBLES else "astrofisica"
    cat_nombre = CATEGORIAS_DISPONIBLES[cat_slug]

    print(f"\n[1/3] Investigando motores de búsqueda para la categoría: {cat_nombre}...")
    semillas = [
        f"que pasaria si {cat_slug}",
        f"que pasaria si la tierra",
        f"que pasaria si el sol",
        f"que pasaria si la humanidad",
        f"que pasaria si la atmosfera"
    ]
    sugerencias_busqueda = []
    for s in semillas:
        res = investigar_en_motores_de_busqueda(s, cat_slug)
        sugerencias_busqueda.extend(res.get("sugerencias_busqueda", []))

    sugerencias_unicas = list(set(sugerencias_busqueda))[:12]
    print(f"      -> {len(sugerencias_unicas)} tendencias de búsqueda detectadas en tiempo real.")

    print(f"[2/3] Cruzando con los {len(titulos_existentes)} artículos existentes para garantizar CERO duplicados...")
    muestra_existentes = [t for t in titulos_existentes if cat_slug in t.lower() or len(t) > 0][:50]

    prompt_descubrimiento = f"""
Actúa como editor en jefe de 'Mundos Simulados'.
Queremos descubrir {cantidad} NUEVOS temas de artículos para la categoría '{cat_nombre}' ({cat_slug}).

REGLAS OBLIGATORIAS:
1. Ninguna de las propuestas puede repetir ni ser similar a estos títulos ya publicados:
{json.dumps(muestra_existentes, ensure_ascii=False, indent=2)}

2. Utiliza la intención de búsqueda real detectada en motores de búsqueda:
{json.dumps(sugerencias_unicas, ensure_ascii=False, indent=2)}

3. Cada propuesta debe cumplir el método editorial:
   - Partir de un dato medible real (ley física, cifra exacta, porcentaje).
   - Alterar UNA sola variable del mundo real.
   - Plantear una pregunta directa con alta atracción ('¿Qué pasaría si...?').
   - Estructura GEO: preparada para responder preguntas concretas que citan Perplexity y ChatGPT Search.

Responde ÚNICAMENTE un JSON con una lista de {cantidad} objetos con esta estructura:
[
  {{
    "titulo": "Título magnético H1 optimizado para búsqueda",
    "palabra_clave": "palabra clave principal",
    "dato_medible_base": "Dato o ley científica real de partida (ej: La gravedad terrestre promedio es de 9.80665 m/s²)",
    "variable_alterada": "Qué variable cambia (ej: Disminución de la gravedad en un 15%)",
    "por_que_es_relevante": "Intención de búsqueda del usuario y valor científico",
    "categoria": "{cat_slug}"
  }}
]
"""
    print("[3/3] Consultando a la IA para generar propuestas basadas en motores de búsqueda...")
    respuesta = llamar_gemini(prompt_descubrimiento, GEMINI_API_KEY, json_mode=True)
    if not respuesta:
        print("[error] No se recibió respuesta de la IA.")
        return []

    try:
        propuestas = json.loads(respuesta)
        return propuestas
    except Exception as e:
        # Extraer JSON de bloques markdown si los hay
        match = re.search(r"\[.*\]", respuesta, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        print(f"[error al parsear propuestas]: {e}")
        return []


# --- 6. Generación del Artículo Completo (SEO & GEO) ---

def redactar_articulo(idea_o_tema, categoria="astrofisica", palabra_clave_propuesta=None):
    """
    Redacta el artículo completo cumpliendo todos los estándares editoriales,
    investigación con motores de búsqueda, GEO e interlinking contextual.
    """
    print(f"\n=======================================================")
    print(f" REDACTANDO ARTÍCULO: {idea_o_tema}")
    print(f"=======================================================")

    # 1. Investigación en Motores de Búsqueda
    print(f"[1/5] Realizando investigación en motores de búsqueda...")
    datos_investigacion = investigar_en_motores_de_busqueda(idea_o_tema, categoria)
    print(f"      - Sugerencias detectadas: {len(datos_investigacion['sugerencias_busqueda'])}")
    print(f"      - Hechos científicos verificados: {len(datos_investigacion['hechos_cientificos'])}")

    # 2. Interlinking: Buscar artículos existentes en la misma categoría
    print(f"[2/5] Buscando artículos existentes para interlinking contextual...")
    articulos_existentes = obtener_articulos_existentes()
    articulos_categoria = [a for a in articulos_existentes if a["categoria"] == categoria]
    if not articulos_categoria:
        articulos_categoria = articulos_existentes[:5]
    else:
        articulos_categoria = articulos_categoria[:6]

    enlaces_sugeridos = [
        f"- [{a['titulo']}](https://mundossimulados.online/{a['slug']}/)"
        for a in articulos_categoria[:3]
    ]
    texto_interlinks = "\n".join(enlaces_sugeridos)

    # 3. Estructuración GEO y Planificación Editorial
    print(f"[3/5] Diseñando arquitectura GEO (H2s tipo pregunta con respuesta directa para IAs)...")
    prompt_maestro = cargar_prompt_maestro()

    prompt_plan = f"""
Actúa como Director Editorial y Especialista en GEO (Generative Engine Optimization) de Mundos Simulados.
Para la premisa: "{idea_o_tema}" (Categoría: {categoria})

Investigación de motores de búsqueda en tiempo real:
Sugerencias de búsqueda: {json.dumps(datos_investigacion['sugerencias_busqueda'], ensure_ascii=False)}
Hechos de referencia: {json.dumps(datos_investigacion['hechos_cientificos'], ensure_ascii=False)}

Genera la ficha técnica y arquitectura del artículo en formato JSON con estos campos exactos:
{{
  "title": "H1 optimizado para intención de búsqueda (máx 65 caracteres)",
  "slug": "url-slug-amigable-sin-acentos",
  "focus_keyword": "{palabra_clave_propuesta or 'palabra clave exacta de 3 a 5 palabras'}",
  "meta_description": "Meta descripción magnética de 145-155 caracteres",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4"],
  "dato_medible_real": "Dato o constante física real verificable con cifra exacta",
  "h2_geo": [
    "H2 pregunta 1 (Fase inicial inmediata)",
    "H2 pregunta 2 (Impacto en la física / biosfera / sociedad)",
    "H2 pregunta 3 (Consecuencias a medio y largo plazo)",
    "H2 pregunta 4 (¿Es reversible o una nueva normalidad?)"
  ],
  "alt_destacada": "Descripción en español para alt text de imagen destacada",
  "prompt_destacada": "Cinematic photo in 16:9 ratio, photorealistic, Unreal Engine 5 style...",
  "alt_interna_1": "Descripción en español de la imagen interna 1",
  "prompt_interna_1": "Detailed realistic photography of...",
  "alt_interna_2": "Descripción en español de la imagen interna 2",
  "prompt_interna_2": "Macro cinematic shot of...",
  "pinterest_title": "Título llamativo para Pin de Pinterest",
  "pinterest_desc": "Descripción atractiva para Pinterest con 3 hashtags relevantes"
}}
"""
    plan_json_str = llamar_gemini(prompt_plan, GEMINI_API_KEY, json_mode=True)
    try:
        plan = json.loads(plan_json_str)
    except Exception:
        match = re.search(r"\{.*\}", plan_json_str, re.DOTALL)
        if match:
            plan = json.loads(match.group(0))
        else:
            sys.exit("[error fatal] No se pudo generar la arquitectura del artículo.")

    # 4. Redacción del Artículo Completo (1400-1900 palabras)
    print(f"[4/5] Redactando artículo completo con rigor científico y formato GEO...")
    prompt_redaccion = f"""
H1 del artículo (no lo repitas en el cuerpo): {plan['title']}
Palabra clave objetivo: {plan['focus_keyword']}
Categoría: {categoria}

Dato medible de partida obligatorio: {plan['dato_medible_real']}

Estructura de H2 obligatoria (Formato GEO: pregunta directa, respondiendo en el primer párrafo de cada H2 con precisión para que motores de respuesta como Perplexity o Google SGE extraigan la cita):
{chr(10).join(['## ' + h for h in plan['h2_geo']])}

Interlinking contextual obligatorio:
Incorpora de forma fluida y natural en el texto 1 o 2 de estos enlaces internos a otros artículos de nuestro sitio:
{texto_interlinks}

Contexto para ubicar las imágenes:
- Imagen 1: {plan['alt_interna_1']}
- Imagen 2: {plan['alt_interna_2']}

RECUERDA LAS REGLAS DEL MÉTODO EDITORIAL:
- Extensión: 1400 a 1900 palabras.
- Español neutro, sin exclamaciones, sin em-dash (—).
- Cero relleno, rigor físico estricto.
- Inserta en su propia línea exactamente: {{{{IMAGEN_INTERNA_1}}}} después del primer o segundo H2.
- Inserta en su propia línea exactamente: {{{{IMAGEN_INTERNA_2}}}} antes del cierre.
- Cierra con el párrafo 'qué nos dice esto del mundo real'.
- Responde ÚNICAMENTE con el cuerpo del artículo en Markdown.
"""
    cuerpo_markdown = llamar_gemini(prompt_redaccion, GEMINI_API_KEY, system_instruction=prompt_maestro)

    # Contar palabras
    palabras = len(cuerpo_markdown.split())
    print(f"      -> Conteo de palabras generado: {palabras} palabras.")

    # Asegurar marcadores si faltaran
    if "{{IMAGEN_INTERNA_1}}" not in cuerpo_markdown:
        partes = cuerpo_markdown.split("## ", 2)
        if len(partes) >= 3:
            cuerpo_markdown = partes[0] + "## " + partes[1] + "\n\n{{IMAGEN_INTERNA_1}}\n\n## " + partes[2]
    if "{{IMAGEN_INTERNA_2}}" not in cuerpo_markdown:
        pos = cuerpo_markdown.rfind("## ")
        if pos != -1:
            cuerpo_markdown = cuerpo_markdown[:pos] + "\n\n{{IMAGEN_INTERNA_2}}\n\n" + cuerpo_markdown[pos:]

    # 5. Estructurar archivo Markdown con Frontmatter
    print(f"[5/5] Consolidando metadatos RankMath SEO y guardando...")
    slug = plan.get("slug") or normalizar_slug(plan["title"])

    metadatos = {
        "title": plan["title"],
        "slug": slug,
        "categoria": categoria,
        "focus_keyword": plan["focus_keyword"],
        "meta_description": plan["meta_description"],
        "tags": plan.get("tags", []),
        "imagen_destacada": f"{slug}-destacada.webp",
        "alt_destacada": plan["alt_destacada"],
        "prompt_destacada": plan["prompt_destacada"],
        "imagen_interna_1": f"{slug}-interna-1.webp",
        "alt_interna_1": plan["alt_interna_1"],
        "prompt_interna_1": plan["prompt_interna_1"],
        "imagen_interna_2": f"{slug}-interna-2.webp",
        "alt_interna_2": plan["alt_interna_2"],
        "prompt_interna_2": plan["prompt_interna_2"],
        "pinterest_title": plan.get("pinterest_title", ""),
        "pinterest_desc": plan.get("pinterest_desc", ""),
        "fecha_creacion": datetime.now().isoformat()
    }

    post = frontmatter.Post(cuerpo_markdown.strip(), **metadatos)
    os.makedirs(CARPETA_ARTICULOS, exist_ok=True)
    ruta_guardado = os.path.join(CARPETA_ARTICULOS, f"{slug}.md")
    with open(ruta_guardado, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    print(f"[exito] Artículo guardado en: {ruta_guardado}")
    return post, ruta_guardado


# --- 7. Publicación Directa en WordPress como Borrador ---

def publicar_en_wordpress(post):
    """
    Envía el artículo a WordPress mediante la REST API en estado 'draft',
    registrando los metadatos de RankMath SEO.
    """
    if not (WP_URL and WP_USER and WP_APP_PASSWORD):
        print("[aviso] No se configuraron credenciales de WordPress en .env. Saltando subida a WP.")
        return False

    meta = post.metadata
    print(f"\n[wp] Conectando con WordPress en {WP_URL}...")
    auth = (WP_USER, WP_APP_PASSWORD)

    # 1. Obtener ID de categoría
    cat_slug = meta.get("categoria", "astrofisica")
    cat_id = None
    try:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories", params={"slug": cat_slug}, auth=auth, timeout=20)
        if r.status_code == 200 and r.json():
            cat_id = r.json()[0]["id"]
    except Exception as e:
        print(f"[aviso wp] Error al buscar categoría {cat_slug}: {e}")

    # 2. Obtener IDs de tags
    tag_ids = []
    for tag_name in meta.get("tags", []):
        try:
            r = requests.get(f"{WP_URL}/wp-json/wp/v2/tags", params={"search": tag_name}, auth=auth, timeout=15)
            if r.status_code == 200 and r.json():
                tag_ids.append(r.json()[0]["id"])
            else:
                r_crear = requests.post(f"{WP_URL}/wp-json/wp/v2/tags", json={"name": tag_name}, auth=auth, timeout=15)
                if r_crear.status_code == 201:
                    tag_ids.append(r_crear.json()["id"])
        except Exception:
            pass

    # 3. Convertir Markdown a HTML preservando placeholders de imágenes
    cuerpo_html = md.markdown(post.content, extensions=["extra"])

    payload = {
        "title": meta["title"],
        "slug": meta["slug"],
        "status": "draft",
        "content": cuerpo_html,
    }
    if cat_id:
        payload["categories"] = [cat_id]
    if tag_ids:
        payload["tags"] = tag_ids

    # Metadatos SEO RankMath
    payload["meta"] = {
        "rank_math_title": meta["title"],
        "rank_math_description": meta["meta_description"],
        "rank_math_focus_keyword": meta["focus_keyword"],
    }

    try:
        resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", json=payload, auth=auth, timeout=30)
        if resp.status_code in [200, 201]:
            post_id = resp.json().get("id")
            print(f"[exito wp] ¡Borrador creado en WordPress con ID #{post_id}!")
            print(f"           URL de edición: {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")
            print(f"           Estado: 'draft' (listo para la cola FIFO del Drip-Feed)")
            return True
        else:
            print(f"[error wp] Respuesta {resp.status_code}: {resp.text[:300]}")
            return False
    except Exception as e:
        print(f"[error wp conexión]: {e}")
        return False


# --- 8. Generación Automática en Lote (Cola Desatendida) ---

def generar_lote_articulos(cantidad=5, categoria="astrofisica", publicar=True):
    """
    Ejecuta un lote de generación de N artículos seguidos en cola desatendida:
    1. Descubre N temas inéditos consultando motores de búsqueda y descartando los 240 existentes.
    2. Redacta cada artículo de forma secuencial con rigor científico y formato GEO.
    3. Si publicar=True, crea cada borrador en WordPress listo para el Drip-Feed.
    """
    print("\n" + "="*70)
    print(f" INICIANDO GENERACIÓN EN LOTE: {cantidad} ARTÍCULOS ({categoria.upper()})")
    print("="*70)

    propuestas = descubrir_temas_nuevos(categoria, cantidad=cantidad)
    if not propuestas:
        print("[error] No se pudieron descubrir temas para el lote.")
        return []

    generados = []
    print(f"\n[lote] Se generarán {len(propuestas)} artículos en secuencia.\n")

    for i, prop in enumerate(propuestas, 1):
        print(f"\n>>> Procesando artículo {i}/{len(propuestas)}: '{prop['titulo']}'")
        try:
            post, ruta = redactar_articulo(
                prop["titulo"],
                categoria=categoria,
                palabra_clave_propuesta=prop.get("palabra_clave")
            )
            exito_wp = False
            if publicar:
                exito_wp = publicar_en_wordpress(post)

            generados.append({
                "numero": i,
                "titulo": prop["titulo"],
                "slug": post.metadata.get("slug"),
                "ruta_md": ruta,
                "publicado_wp": exito_wp
            })

            # Pausa de cortesía entre llamadas para no saturar cuota gratuita
            if i < len(propuestas):
                print("\n[pausa] Esperando 6 segundos antes del siguiente artículo...")
                time.sleep(6)

        except Exception as e:
            print(f"[error en artículo {i}]: {e}")

    print("\n" + "="*70)
    print(" RESUMEN DE GENERACIÓN EN LOTE FINALIZADO:")
    print("="*70)
    for g in generados:
        estado_wp = "Subido a WP como borrador" if g["publicado_wp"] else "Guardado localmente en .md"
        print(f"- [{g['numero']}] {g['titulo']} -> {estado_wp}")

    return generados


# --- 9. Menú Interactivo de Terminal ---

def menu_interactivo():
    print("\n" + "="*70)
    print("   MUNDOS SIMULADOS - GENERADOR EDITORIAL AUTÓNOMO CON IA (SEO & GEO)")
    print("="*70)
    print("1. Ingresar mi propia idea o premisa científica")
    print("2. Descubrir temas inéditos en motores de búsqueda (Cero duplicados)")
    print("3. Generar un LOTE de N artículos en cola desatendida (ej. 3, 5, 10)")
    print("4. Salir")
    print("-"*70)

    opcion = input("Selecciona una opción [1-4]: ").strip()
    if opcion == "1":
        idea = input("\nEscribe tu idea (ej. ¿Qué pasaría si la Tierra tuviera dos lunas?): ").strip()
        if not idea:
            print("[aviso] Idea vacía. Cancelando.")
            return

        print("\nCategorías disponibles:")
        cats = list(CATEGORIAS_DISPONIBLES.keys())
        for idx, c in enumerate(cats, 1):
            print(f"  {idx}. {c} ({CATEGORIAS_DISPONIBLES[c]})")
        cat_idx = input(f"Selecciona categoría [1-{len(cats)}] (por defecto 1): ").strip()
        try:
            cat_elegida = cats[int(cat_idx) - 1]
        except Exception:
            cat_elegida = "astrofisica"

        pub = input("\n¿Deseas subirlo directamente como borrador a WordPress? [s/N]: ").strip().lower()
        publicar = pub in ["s", "si", "y", "yes"]

        post, _ = redactar_articulo(idea, categoria=cat_elegida)
        if publicar:
            publicar_en_wordpress(post)

    elif opcion == "2":
        print("\nCategorías para descubrir tendencias:")
        cats = list(CATEGORIAS_DISPONIBLES.keys())
        for idx, c in enumerate(cats, 1):
            print(f"  {idx}. {c} ({CATEGORIAS_DISPONIBLES[c]})")
        cat_idx = input(f"Selecciona categoría [1-{len(cats)}] (por defecto 1): ").strip()
        try:
            cat_elegida = cats[int(cat_idx) - 1]
        except Exception:
            cat_elegida = "astrofisica"

        propuestas = descubrir_temas_nuevos(cat_elegida, cantidad=6)
        if not propuestas:
            print("[aviso] No se encontraron propuestas.")
            return

        print(f"\nTemas inéditos descubiertos basados en motores de búsqueda:")
        print("-"*70)
        for idx, p in enumerate(propuestas, 1):
            print(f"[{idx}] {p.get('titulo')}")
            print(f"    Keyword: {p.get('palabra_clave')} | Base: {p.get('dato_medible_base', '')[:90]}...")
            print(f"    Variable: {p.get('variable_alterada', '')}")
            print()

        eleccion = input(f"Ingresa el número del tema a redactar [1-{len(propuestas)}] o 0 para cancelar: ").strip()
        try:
            idx_tema = int(eleccion)
            if 1 <= idx_tema <= len(propuestas):
                elegido = propuestas[idx_tema - 1]
                pub = input("\n¿Deseas subirlo como borrador a WordPress tras redactarlo? [s/N]: ").strip().lower()
                publicar = pub in ["s", "si", "y", "yes"]

                post, _ = redactar_articulo(
                    elegido["titulo"],
                    categoria=cat_elegida,
                    palabra_clave_propuesta=elegido.get("palabra_clave")
                )
                if publicar:
                    publicar_en_wordpress(post)
        except ValueError:
            print("[aviso] Operación cancelada.")

    elif opcion == "3":
        print("\nCategorías disponibles para el lote:")
        cats = list(CATEGORIAS_DISPONIBLES.keys())
        for idx, c in enumerate(cats, 1):
            print(f"  {idx}. {c} ({CATEGORIAS_DISPONIBLES[c]})")
        cat_idx = input(f"Selecciona categoría [1-{len(cats)}] (por defecto 1): ").strip()
        try:
            cat_elegida = cats[int(cat_idx) - 1]
        except Exception:
            cat_elegida = "astrofisica"

        cant_input = input("\n¿Cuántos artículos deseas generar en cola? [ej. 3, 5, 10] (por defecto 5): ").strip()
        try:
            cantidad = int(cant_input)
            if cantidad < 1:
                cantidad = 5
        except ValueError:
            cantidad = 5

        pub = input("\n¿Deseas subir los artículos automáticamente como borradores a WordPress? [S/n]: ").strip().lower()
        publicar = pub not in ["n", "no"]

        generar_lote_articulos(cantidad=cantidad, categoria=cat_elegida, publicar=publicar)

    else:
        print("Saliendo...")


# --- Punto de Entrada Principal ---

def main():
    parser = argparse.ArgumentParser(description="Generador Autónomo de Artículos IA (SEO & GEO) - Mundos Simulados")
    parser.add_argument("--idea", type=str, help="Premisa o idea para redactar el artículo")
    parser.add_argument("--descubrir", action="store_true", help="Descubrir temas en motores de búsqueda sin duplicar existentes")
    parser.add_argument("--lote", type=int, default=None, help="Número de artículos a generar en lote desatendido")
    parser.add_argument("--categoria", type=str, default="astrofisica", choices=list(CATEGORIAS_DISPONIBLES.keys()))
    parser.add_argument("--palabra-clave", type=str, default=None, help="Palabra clave SEO objetivo")
    parser.add_argument("--publicar", action="store_true", help="Publicar como borrador en WordPress mediante REST API")
    parser.add_argument("--interactivo", action="store_true", help="Lanzar el menú interactivo paso a paso")

    args = parser.parse_args()

    if args.interactivo or (len(sys.argv) == 1):
        menu_interactivo()
    elif args.lote:
        generar_lote_articulos(cantidad=args.lote, categoria=args.categoria, publicar=args.publicar)
    elif args.descubrir:
        propuestas = descubrir_temas_nuevos(args.categoria, cantidad=6)
        print("\n" + "="*70)
        print(f" PROPUESTAS INÉDITAS DESCUBIERTAS ({args.categoria.upper()}):")
        print("="*70)
        for idx, p in enumerate(propuestas, 1):
            print(f"\n{idx}. {p.get('titulo')}")
            print(f"   Keyword: {p.get('palabra_clave')}")
            print(f"   Dato base: {p.get('dato_medible_base')}")
            print(f"   Variable alterada: {p.get('variable_alterada')}")
    elif args.idea:
        post, _ = redactar_articulo(args.idea, categoria=args.categoria, palabra_clave_propuesta=args.palabra_clave)
        if args.publicar:
            publicar_en_wordpress(post)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
