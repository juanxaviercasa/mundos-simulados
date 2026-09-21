"""
Script de prueba: Crear 3 pines de un mismo artículo usando sus 3 imágenes.

Este es un script de prueba específico para verificar que Pinterest funciona bien.
Crea 3 pines del artículo "apagon-global-internet-7-dias" usando:
- Imagen destacada
- Imagen interna 1
- Imagen interna 2

Lee las URLs del media_map.json para asegurar que las imágenes existen en WordPress.

Uso:
    python3 03_test_pinterest_3pines.py
"""

import os
import json
import requests
from dotenv import load_dotenv
import frontmatter
import time

load_dotenv()

PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")
WP_URL = os.environ.get("WP_URL", "https://mundossimulados.online")

CREATE_PIN_ENDPOINT = "https://api.pinterest.com/v1/pins/?access_token={token}"

# Artículo de prueba
SLUG_PRUEBA = "apagon-global-internet-7-dias"


def cargar_media_map():
    """Carga el media_map.json con las URLs de todas las imágenes."""
    if not os.path.exists("media_map.json"):
        print("❌ ERROR: media_map.json no encontrado. Ejecuta 00_mapa_imagenes.py primero.")
        return None
    
    try:
        with open("media_map.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo media_map.json: {e}")
        return None


def obtener_url_imagen(nombre_imagen, media_map):
    """Obtiene la URL completa de una imagen desde el media_map."""
    if not media_map or nombre_imagen not in media_map:
        return None
    
    img_data = media_map[nombre_imagen]
    
    # El media_map devuelve {'id': ..., 'url': ...}
    if isinstance(img_data, dict):
        return img_data.get('url')
    
    # Si es string (backward compatibility)
    return img_data


def crear_pin(titulo, descripcion, enlace, imagen_url, alt_text, hashtags, board_id, token):
    """Crea un pin en Pinterest."""
    
    nota = f"{titulo}\n\n"
    nota += f"{descripcion}\n\n"
    nota += f"Alt: {alt_text}\n\n"
    if hashtags:
        nota += " ".join(hashtags) + "\n\n"
    nota += enlace
    
    payload = {
        "board": board_id,
        "note": nota[:2000],
        "image_url": imagen_url,
        "link": enlace,
    }
    
    headers = {"Content-Type": "application/json"}
    url = CREATE_PIN_ENDPOINT.format(token=token)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 201:
            data = response.json()
            return {'ok': True, 'pin_id': data.get('id', ''), 'error': ''}
        else:
            return {'ok': False, 'pin_id': '', 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'ok': False, 'pin_id': '', 'error': str(e)}


def main():
    """Crea 3 pines de prueba del artículo."""
    
    print(f"📂 Cargando media_map.json...")
    media_map = cargar_media_map()
    if not media_map:
        return
    
    print(f"✓ Media map cargado con {len(media_map)} imágenes\n")
    
    print(f"🔍 Leyendo artículo: {SLUG_PRUEBA}.md")
    
    # Leer artículo
    filepath = os.path.join("articulos", f"{SLUG_PRUEBA}.md")
    
    if not os.path.exists(filepath):
        print(f"❌ ERROR: {filepath} no encontrado")
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
    except Exception as e:
        print(f"❌ Error leyendo artículo: {e}")
        return
    
    # Extraer datos
    titulo_base = post.metadata.get('title', 'Sin título')
    descripcion = post.metadata.get('meta_description', '')[:300]
    tags = post.metadata.get('tags', [])
    
    # Generar hashtags
    hashtags = [f"#{tag.lower().replace(' ', '').replace('-', '')}" for tag in tags[:3]]
    hashtags.extend(["#FuturoSimulado", "#MundosSimulados"])
    
    # URL del artículo
    enlace = f"{WP_URL}/{SLUG_PRUEBA}/"
    
    # Imágenes desde metadatos
    imagen_destacada = post.metadata.get('imagen_destacada', '')
    imagen_interna_1 = post.metadata.get('imagen_interna_1', '')
    imagen_interna_2 = post.metadata.get('imagen_interna_2', '')
    
    alt_destacada = post.metadata.get('alt_destacada', 'Imagen destacada')
    alt_interna_1 = post.metadata.get('alt_interna_1', 'Imagen 1')
    alt_interna_2 = post.metadata.get('alt_interna_2', 'Imagen 2')
    
    # Definir 3 pines
    pines = [
        {
            'titulo': f"{titulo_base} 📌 Parte 1",
            'descripcion': descripcion,
            'imagen': imagen_destacada,
            'alt': alt_destacada,
            'numero': 1
        },
        {
            'titulo': f"{titulo_base} 📌 Parte 2",
            'descripcion': descripcion,
            'imagen': imagen_interna_1,
            'alt': alt_interna_1,
            'numero': 2
        },
        {
            'titulo': f"{titulo_base} 📌 Parte 3",
            'descripcion': descripcion,
            'imagen': imagen_interna_2,
            'alt': alt_interna_2,
            'numero': 3
        }
    ]
    
    print(f"\n📍 Creando 3 pines de: {titulo_base}")
    print(f"🔗 Link: {enlace}")
    print(f"#️⃣ Hashtags: {' '.join(hashtags)}\n")
    
    creados = 0
    
    for pin_info in pines:
        
        if not pin_info['imagen']:
            print(f"⚠️  PIN {pin_info['numero']}: Imagen no especificada, saltando...")
            continue
        
        # Obtener URL del media_map
        imagen_url = obtener_url_imagen(pin_info['imagen'], media_map)
        
        if not imagen_url:
            print(f"⚠️  PIN {pin_info['numero']}: '{pin_info['imagen']}' no encontrada en media_map, saltando...")
            continue
        
        print(f"📌 Creando PIN {pin_info['numero']}/3...")
        print(f"   Título: {pin_info['titulo'][:60]}...")
        print(f"   Imagen: {pin_info['imagen']}")
        
        resultado = crear_pin(
            titulo=pin_info['titulo'],
            descripcion=pin_info['descripcion'],
            enlace=enlace,
            imagen_url=imagen_url,
            alt_text=pin_info['alt'],
            hashtags=hashtags,
            board_id=PINTEREST_BOARD_ID,
            token=PINTEREST_ACCESS_TOKEN
        )
        
        if resultado['ok']:
            print(f"   ✅ PIN CREADO: {resultado['pin_id']}\n")
            creados += 1
        else:
            print(f"   ❌ ERROR: {resultado['error']}\n")
        
        # Esperar entre pines
        time.sleep(2)
    
    print(f"\n✅ RESUMEN: {creados}/3 pines creados exitosamente")
    print(f"🔗 Ver en Pinterest: https://www.pinterest.com/{PINTEREST_BOARD_ID}/")


if __name__ == "__main__":
    main()

