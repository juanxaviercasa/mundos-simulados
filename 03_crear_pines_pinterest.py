"""
Crea pines automáticamente en Pinterest desde los artículos generados.

Cada pin:
- Usa la imagen destacada del artículo
- Tiene un título descriptivo optimizado para Pinterest
- Linkea al artículo en WordPress
- Se publica automáticamente en el tablero configurado

Uso:
    python3 03_crear_pines_pinterest.py --limite 5      # Crear 5 pines de prueba
    python3 03_crear_pines_pinterest.py                 # Crear pines de todos los articulos
    python3 03_crear_pines_pinterest.py --tablero "Otro Tablero"  # Usar otro tablero
"""

import argparse
import csv
import os
import sys
import time
import json
from datetime import datetime, timedelta

import frontmatter
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuración de Pinterest API
PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")
CSV_PATH = os.environ.get("CSV_PATH", "Estructura Mundos Simulados.csv")
WP_URL = os.environ.get("WP_URL", "https://mundossimulados.online")
ARTICULOS_FOLDER = "articulos"
LOG_PATH = "pinterest_log.csv"

# API endpoints
PINTEREST_API_BASE = "https://api.pinterest.com/v1"
CREATE_PIN_ENDPOINT = f"{PINTEREST_API_BASE}/pins/?access_token={{token}}"


def crear_pin(titulo, descripcion, enlace_articulo, imagen_url, alt_text, hashtags, board_id, token):
    """
    Crea un pin en Pinterest con descripción mejorada, hashtags y alt text.
    
    Args:
        titulo: Título del pin (optimizado para Pinterest)
        descripcion: Descripción del pin
        enlace_articulo: URL del artículo WordPress
        imagen_url: URL de la imagen destacada
        alt_text: Descripción alternativa de la imagen
        hashtags: Lista de hashtags relevantes
        board_id: ID del tablero Pinterest
        token: Access token de Pinterest API
    
    Returns:
        dict con resultado: {'ok': bool, 'pin_id': str, 'error': str}
    """
    
    # Construir nota con descripción mejorada
    nota = f"{titulo}\n\n"
    nota += f"{descripcion}\n\n"
    nota += f"Alt: {alt_text}\n\n"
    
    # Agregar hashtags
    if hashtags:
        nota += " ".join(hashtags) + "\n\n"
    
    nota += enlace_articulo
    
    payload = {
        "board": board_id,
        "note": nota[:2000],  # Pinterest limita a 2000 caracteres
        "image_url": imagen_url,
        "link": enlace_articulo,
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    url = CREATE_PIN_ENDPOINT.format(token=token)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 201:
            data = response.json()
            return {
                'ok': True,
                'pin_id': data.get('id', ''),
                'error': ''
            }
        else:
            return {
                'ok': False,
                'pin_id': '',
                'error': f"HTTP {response.status_code}: {response.text}"
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'ok': False,
            'pin_id': '',
            'error': str(e)
        }


def obtener_pines_existentes():
    """Retorna conjunto de slugs ya publicados como pins."""
    if not os.path.exists(LOG_PATH):
        return set()
    
    try:
        df = pd.read_csv(LOG_PATH)
        return set(df['slug'].unique())
    except:
        return set()


def leer_articulo(slug):
    """Lee un artículo .md y retorna metadatos con alt text."""
    filepath = os.path.join(ARTICULOS_FOLDER, f"{slug}.md")
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        return {
            'titulo': post.metadata.get('title', ''),
            'descripcion': post.metadata.get('meta_description', ''),
            'imagen': post.metadata.get('imagen_destacada', ''),
            'alt_destacada': post.metadata.get('alt_destacada', ''),
            'tags': post.metadata.get('tags', []),
            'slug': post.metadata.get('slug', slug),
        }
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return None


def optimizar_titulo_pinterest(titulo_original):
    """Convierte un título largo en uno optimizado para Pinterest (140-200 caracteres)."""
    # Pinterest favorece títulos cortos, descriptivos
    if len(titulo_original) <= 140:
        return titulo_original
    
    # Truncar a las primeras palabras clave
    partes = titulo_original.split(':')
    if len(partes) > 1:
        return partes[0].strip()[:140]
    
    return titulo_original[:140]


def generar_hashtags(tags_articulo, palabra_clave):
    """
    Genera hashtags relevantes para Pinterest basados en tags del artículo.
    
    Args:
        tags_articulo: Lista de tags del artículo
        palabra_clave: Palabra clave principal del artículo
    
    Returns:
        Lista de hashtags formateados para Pinterest
    """
    hashtags = []
    
    # Agregar palabra clave como hashtag principal
    if palabra_clave:
        keyword_clean = palabra_clave.lower().replace(" ", "")
        hashtags.append(f"#{keyword_clean}")
    
    # Agregar tags del artículo como hashtags (max 3-4)
    if tags_articulo:
        for tag in tags_articulo[:4]:
            tag_clean = str(tag).lower().replace(" ", "").replace("-", "")
            if len(tag_clean) > 2:  # Evitar hashtags muy cortos
                hashtags.append(f"#{tag_clean}")
    
    # Agregar hashtags genéricos útiles para Pinterest
    hashtags.extend([
        "#FuturoSimulado",
        "#CienciaFicción",
        "#MundosSimulados"
    ])
    
    return hashtags[:8]  # Pinterest recomienda máx 8 hashtags


def mejorar_descripcion(descripcion_original, titulo):
    """Mejora la descripción para Pinterest agregando contexto."""
    # Limitar a 300 caracteres para Pinterest
    desc_clean = descripcion_original.strip()
    
    if len(desc_clean) > 300:
        desc_clean = desc_clean[:297] + "..."
    
    return desc_clean


def main():
    ap = argparse.ArgumentParser(
        description="Crea pines automáticamente en Pinterest desde artículos generados.",
    )
    ap.add_argument(
        "--limite", type=int, default=None,
        help="Limitar a N pines (ej: 5 para pruebas)"
    )
    ap.add_argument(
        "--tablero", type=str, default=None,
        help="Nombre del tablero (si no está en .env)"
    )
    ap.add_argument(
        "--pausa", type=float, default=2.0,
        help="Segundos de espera entre pines (por rate limiting de Pinterest)"
    )
    args = ap.parse_args()
    
    # Validar credenciales
    if not PINTEREST_ACCESS_TOKEN:
        sys.exit("ERROR: PINTEREST_ACCESS_TOKEN no está en .env")
    
    if not PINTEREST_BOARD_ID and not args.tablero:
        sys.exit("ERROR: PINTEREST_BOARD_ID no está en .env ni se pasó --tablero")
    
    board_id = args.tablero or PINTEREST_BOARD_ID
    
    # Leer CSV
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        sys.exit(f"Error leyendo CSV: {e}")
    
    # Inicializar log
    log_nuevo = not os.path.exists(LOG_PATH)
    log_f = open(LOG_PATH, "a", newline="", encoding="utf-8")
    log_w = csv.writer(log_f)
    if log_nuevo:
        log_w.writerow(["slug", "titulo", "estado", "pin_id", "detalle"])
    
    pines_existentes = obtener_pines_existentes()
    creados = 0
    saltados = 0
    
    for idx, fila in df.iterrows():
        slug = fila.get('URL Slug (Post)', '')
        
        if not slug:
            continue
        
        # Saltar si ya existe pin
        if slug in pines_existentes:
            print(f"[saltado] {slug} (ya tiene pin)")
            saltados += 1
            continue
        
        # Leer artículo
        articulo = leer_articulo(slug)
        if not articulo:
            print(f"[error] {slug} - No existe .md")
            log_w.writerow([slug, "", "error", "", "Archivo .md no encontrado"])
            log_f.flush()
            continue
        
        # URL del artículo
        enlace = f"{WP_URL}/{slug}/"
        
        # Imagen destacada URL
        imagen_url = f"{WP_URL}/wp-content/uploads/{articulo['imagen']}"
        
        # Optimizar título para Pinterest
        titulo_pin = optimizar_titulo_pinterest(articulo['titulo'])
        
        # Mejorar descripción
        descripcion_mejorada = mejorar_descripcion(articulo['descripcion'], titulo_pin)
        
        # Generar hashtags automáticamente
        palabra_clave = fila.get('Palabra Clave', '')
        hashtags = generar_hashtags(articulo['tags'], palabra_clave)
        
        # Alt text
        alt_text = articulo['alt_destacada']
        
        print(f"[creando] {slug}")
        print(f"  Título: {titulo_pin[:80]}...")
        print(f"  Hashtags: {' '.join(hashtags)}")
        print(f"  Link: {enlace}")
        
        # Crear pin
        resultado = crear_pin(
            titulo=titulo_pin,
            descripcion=descripcion_mejorada,
            enlace_articulo=enlace,
            imagen_url=imagen_url,
            alt_text=alt_text,
            hashtags=hashtags,
            board_id=board_id,
            token=PINTEREST_ACCESS_TOKEN
        )
        
        if resultado['ok']:
            print(f"  ✓ Pin creado: {resultado['pin_id']}")
            log_w.writerow([slug, titulo_pin, "ok", resultado['pin_id'], ""])
            creados += 1
        else:
            print(f"  ✗ Error: {resultado['error'][:100]}")
            log_w.writerow([slug, titulo_pin, "error", "", resultado['error'][:500]])
        
        log_f.flush()
        
        # Respetar rate limiting
        time.sleep(args.pausa)
        
        # Respetar límite si se pasó
        if args.limite and creados >= args.limite:
            break
    
    log_f.close()
    
    print(f"\n✓ Resumen:")
    print(f"  Pines creados: {creados}")
    print(f"  Pines saltados (ya existen): {saltados}")
    print(f"  Log guardado en: {LOG_PATH}")


if __name__ == "__main__":
    main()
