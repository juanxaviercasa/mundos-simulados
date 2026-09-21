#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exportador Estático de Alta Fidelidad - Mundos Simulados
Descarga la totalidad de páginas (Home, Páginas, Categorías, 170 Posts)
y todos sus assets estáticos (CSS, JS, WebP/Imágenes, Fuentes)
desde Pantheon hacia mundossimuladosexport para despliegue en GitHub Pages y Cloudflare Pages.
"""

import os
import sys
import re
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote

WP_HOST = "https://dev-simulandomundos.pantheonsite.io"
EXPORT_DIR = os.path.abspath("mundossimuladosexport")

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def run_curl(url, output_path=None, binary=False):
    """Ejecuta curl.exe de forma segura para evitar bloqueos por TLS/Cloudflare."""
    cmd = ["curl.exe", "-s", "-L", "--compressed", "--retry", "2", "--connect-timeout", "15"]
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cmd.extend(["-o", output_path])
        res = subprocess.run(cmd + [url], capture_output=True)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0
    else:
        res = subprocess.run(cmd + [url], capture_output=True)
        if res.returncode != 0:
            return None
        if binary:
            return res.stdout
        try:
            return res.stdout.decode('utf-8', errors='replace')
        except Exception:
            return res.stdout.decode('latin1', errors='replace')

def obtener_urls():
    """Descubre todas las URLs a exportar usando WP REST API."""
    print("Descubriendo URLs desde WordPress REST API...")
    urls_to_crawl = []
    
    # 1. Portada
    urls_to_crawl.append({"url": f"{WP_HOST}/", "slug": "", "type": "home"})
    
    # 2. Páginas
    print("  -> Consultando paginas...")
    raw = run_curl(f"{WP_HOST}/wp-json/wp/v2/pages?per_page=100")
    if raw:
        pages = json.loads(raw)
        for p in pages:
            slug = p.get("slug", "").strip()
            if slug and slug != "inicio":
                urls_to_crawl.append({
                    "url": f"{WP_HOST}/{slug}/",
                    "slug": slug,
                    "type": "page",
                    "title": p.get("title", {}).get("rendered", slug)
                })
    
    # 3. Categorías
    print("  -> Consultando categorias...")
    raw = run_curl(f"{WP_HOST}/wp-json/wp/v2/categories?per_page=100")
    if raw:
        cats = json.loads(raw)
        for c in cats:
            slug = c.get("slug", "").strip()
            if slug:
                urls_to_crawl.append({
                    "url": f"{WP_HOST}/category/{slug}/",
                    "slug": f"category/{slug}",
                    "type": "category",
                    "title": c.get("name", slug)
                })
                
    # 4. Autor
    urls_to_crawl.append({
        "url": f"{WP_HOST}/author/jxaviercabellosgmail-com/",
        "slug": "author/jxaviercabellosgmail-com",
        "type": "author",
        "title": "Xavier Cabello"
    })
    
    # 5. Artículos (posts)
    print("  -> Consultando articulos...")
    page = 1
    total_posts = 0
    search_index = []
    
    while True:
        raw = run_curl(f"{WP_HOST}/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,slug,title,excerpt,date")
        if not raw:
            break
        try:
            posts = json.loads(raw)
        except Exception:
            break
        if not posts or not isinstance(posts, list) or len(posts) == 0:
            break
            
        for post in posts:
            slug = post.get("slug", "").strip()
            title = post.get("title", {}).get("rendered", "")
            excerpt_raw = post.get("excerpt", {}).get("rendered", "")
            # Limpiar etiquetas HTML de excerpt
            excerpt_clean = re.sub(r'<[^>]+>', '', excerpt_raw).strip()
            
            urls_to_crawl.append({
                "url": f"{WP_HOST}/{slug}/",
                "slug": slug,
                "type": "post",
                "title": title
            })
            
            search_index.append({
                "title": title,
                "slug": slug,
                "url": f"/{slug}/",
                "snippet": excerpt_clean[:180] + ("..." if len(excerpt_clean) > 180 else ""),
                "date": post.get("date", "")[:10]
            })
            total_posts += 1
            
        print(f"     Pagina {page}: {len(posts)} articulos obtenidos.")
        if len(posts) < 100:
            break
        page += 1
        
    print(f"Total de URLs a rastrear: {len(urls_to_crawl)} (incluye {total_posts} articulos)")
    return urls_to_crawl, search_index

def descargar_pagina(item):
    """Descarga el HTML de una página."""
    url = item["url"]
    slug = item["slug"]
    
    if not slug:
        out_path = os.path.join(EXPORT_DIR, "index.html")
    else:
        out_path = os.path.join(EXPORT_DIR, slug, "index.html")
        
    fetch_url = url + ("?v=14" if "?" not in url else "&v=14")
    html = run_curl(fetch_url)
    if not html or len(html) < 200:
        return item, False, "Descarga vacia o fallida"
        
    # Verificar que no sea un 403 de protección
    if "Directory access forbidden" in html and len(html) < 300:
        return item, False, "Devolvio 403 Forbidden"
        
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return item, True, out_path

def extraer_assets(html_content):
    """Extrae todas las referencias a assets de wp-content y wp-includes."""
    assets = set()
    patterns = [
        r'src=[\'"]([^\'"]+)[\'"]',
        r'href=[\'"]([^\'"]+)[\'"]',
        r'srcset=[\'"]([^\'"]+)[\'"]',
        r'url\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)'
    ]
    
    for pat in patterns:
        for match in re.findall(pat, html_content, re.IGNORECASE):
            # En caso de srcset con múltiples URLs
            for part in match.split(','):
                candidate = part.strip().split(' ')[0].strip()
                if not candidate:
                    continue
                # Limpiar query params (?ver=1.0)
                clean = candidate.split('?')[0].split('#')[0]
                if '/wp-content/' in clean or '/wp-includes/' in clean:
                    assets.add(clean)
                    
    return assets

def descargar_asset(asset_url):
    """Descarga un activo estático y lo guarda en su ruta relativa exacta."""
    # Normalizar URL
    if asset_url.startswith('//'):
        full_url = "https:" + asset_url
    elif asset_url.startswith('http://') or asset_url.startswith('https://'):
        full_url = asset_url
    elif asset_url.startswith('/'):
        full_url = WP_HOST + asset_url
    else:
        full_url = WP_HOST + '/' + asset_url
        
    # Reemplazar mundossimulados.online con WP_HOST
    full_url = full_url.replace("https://mundossimulados.online", WP_HOST)
    full_url = full_url.replace("http://mundossimulados.online", WP_HOST)
    
    parsed = urlparse(full_url)
    rel_path = unquote(parsed.path.lstrip('/'))
    
    if not (rel_path.startswith('wp-content/') or rel_path.startswith('wp-includes/')):
        return False
        
    local_file = os.path.join(EXPORT_DIR, rel_path.replace('/', os.sep))
    
    if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
        return True
        
    return run_curl(full_url, local_file, binary=True)

def reescribir_html(file_path, rel_path, known_slugs):
    """Reescribe URLs a rutas RELATIVAS exactas según la profundidad del archivo."""
    dirname = os.path.dirname(rel_path)
    if not dirname or dirname == '.':
        prefix = "./"
    else:
        parts = dirname.replace('\\', '/').split('/')
        prefix = "../" * len(parts)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return

    # 1. Assets
    content = re.sub(r'([\'"])/wp-content/', r'\1' + prefix + 'wp-content/', content)
    content = re.sub(r'([\'"])/wp-includes/', r'\1' + prefix + 'wp-includes/', content)
    content = re.sub(r'([\'"])/wp-static-arquitect-assets/', r'\1' + prefix + 'wp-static-arquitect-assets/', content)

    # 2. Categorías y autor
    content = re.sub(r'href=[\'"]/category/([^\'"]+)/?[\'"]', r'href="' + prefix + r'category/\1/"', content)
    content = re.sub(r'href=[\'"]/author/([^\'"]+)/?[\'"]', r'href="' + prefix + r'author/\1/"', content)

    # 3. Páginas fijas
    for fp in ['sobre-mi', 'escenarios', 'blog', 'politica-de-privacidad']:
        content = re.sub(r'href=[\'"]/' + fp + r'/?[\'"]', r'href="' + prefix + fp + r'/"', content)

    # 4. Portada
    home_link = prefix if prefix != "./" else "./"
    content = re.sub(r'href=[\'"]/(?:index\.html)?[\'"]', r'href="' + home_link + r'"', content)

    # 5. Artículos
    for slug in known_slugs:
        pattern = r'href=[\'"]/' + re.escape(slug) + r'/?[\'"]'
        content = re.sub(pattern, r'href="' + prefix + slug + r'/"', content)

    # 6. data-wpsa-root para buscador Spotlight
    root_val = prefix.rstrip('/') if prefix != "./" else "."
    if 'data-wpsa-root=' not in content:
        content = re.sub(r'<body([^>]*)>', r'<body\1 data-wpsa-root="' + root_val + r'">', content, count=1)
    else:
        content = re.sub(r'data-wpsa-root=[\'"][^\'"]*[\'"]', r'data-wpsa-root="' + root_val + r'"', content)

    # 7. Limpieza de artefactos dinámicos
    content = re.sub(r'<link[^>]+dns-prefetch[^>]+dev-simulandomundos[^>]*>', '', content, flags=re.I)
    content = re.sub(r'<link[^>]+alternate[^>]+oembed[^>]*>', '', content, flags=re.I)
    content = re.sub(r'<link[^>]+rel=["\']https://api\.w\.org/["\'][^>]*>', '', content, flags=re.I)
    content = re.sub(r'<link[^>]+rel=["\']EditURI["\'][^>]*>', '', content, flags=re.I)
    content = re.sub(r'<link[^>]+rel=["\']wlwmanifest["\'][^>]*>', '', content, flags=re.I)

    # 8. Limpiar dominios absolutos
    content = content.replace("https://dev-simulandomundos.pantheonsite.io/", prefix)
    content = content.replace("http://dev-simulandomundos.pantheonsite.io/", prefix)
    content = content.replace("https://dev-simulandomundos.pantheonsite.io", "")
    content = content.replace("http://dev-simulandomundos.pantheonsite.io", "")

    content = content.replace("https://mundossimulados.online/", prefix)
    content = content.replace("http://mundossimulados.online/", prefix)
    content = content.replace("https://mundossimulados.online", "")
    content = content.replace("http://mundossimulados.online", "")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("=" * 70)
    print("🚀 INICIANDO EXPORTACIÓN ESTÁTICA COMPLETA DE MUNDOS SIMULADOS")
    print("=" * 70)
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    urls, search_index = obtener_urls()
    
    # 1. Descargar páginas HTML en paralelo
    print(f"\nDescargando {len(urls)} páginas HTML con 8 hilos...")
    downloaded_html_files = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(descargar_pagina, item): item for item in urls}
        done_count = 0
        for f in as_completed(futures):
            item, success, detail = f.result()
            done_count += 1
            if success:
                downloaded_html_files.append(detail)
                if done_count % 25 == 0 or done_count == len(urls):
                    print(f"  [{done_count}/{len(urls)}] Descargadas ({item['slug'] or 'HOME'})")
            else:
                print(f"  ❌ Error en {item['url']}: {detail}")
                
    # 2. Extraer todos los assets
    print("\nEscaneando assets (CSS, JS, WebP, SVG, fuentes)...")
    all_assets = set()
    for html_file in downloaded_html_files:
        try:
            with open(html_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            all_assets.update(extraer_assets(content))
        except Exception:
            pass
            
    # Añadir imágenes del media_map.json si existe
    if os.path.exists("media_map.json"):
        try:
            with open("media_map.json", "r", encoding="utf-8") as f:
                media_data = json.load(f)
            for m in media_data:
                u = m.get("url", "")
                if u:
                    all_assets.add(u)
            print(f"  -> Integradas {len(media_data)} imagenes desde media_map.json")
        except Exception as e:
            print("  Aviso al leer media_map.json:", e)
            
    print(f"Total de assets unicos a descargar: {len(all_assets)}")
    
    # 3. Descargar assets en paralelo
    print(f"\nDescargando {len(all_assets)} assets con 12 hilos...")
    success_assets = 0
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(descargar_asset, a): a for a in all_assets}
        done_assets = 0
        for f in as_completed(futures):
            ok = f.result()
            done_assets += 1
            if ok:
                success_assets += 1
            if done_assets % 100 == 0 or done_assets == len(all_assets):
                print(f"  [{done_assets}/{len(all_assets)}] Assets procesados (Exitosos: {success_assets})")
                
    # 4. Reescribir URLs en todos los HTML descargados
    print("\nReescribiendo enlaces internos a rutas RELATIVAS...")
    known_slugs = [item['slug'] for item in urls if item.get('slug')]
    for html_file in downloaded_html_files:
        rel = os.path.relpath(html_file, EXPORT_DIR)
        reescribir_html(html_file, rel, known_slugs)
        
    # 5. Generar search-index.json actualizado
    search_file = os.path.join(EXPORT_DIR, "search-index.json")
    with open(search_file, "w", encoding="utf-8") as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print(f"✅ search-index.json generado con {len(search_index)} articulos.")
    
    # 6. Generar .nojekyll (CRÍTICO para GitHub Pages)
    nojekyll_file = os.path.join(EXPORT_DIR, ".nojekyll")
    with open(nojekyll_file, "w", encoding="utf-8") as f:
        f.write("")
    print("✅ .nojekyll generado para GitHub Pages.")
    
    # 7. Generar _routes.json para Cloudflare Pages
    routes_file = os.path.join(EXPORT_DIR, "_routes.json")
    routes_content = {
        "version": 1,
        "include": ["/*"],
        "exclude": [
            "/wp-static-arquitect-assets/*",
            "/wp-content/*",
            "/wp-includes/*",
            "/search-index.json",
            "/sitemap.xml",
            "/robots.txt",
            "/llms.txt"
        ]
    }
    with open(routes_file, "w", encoding="utf-8") as f:
        json.dump(routes_content, f, indent=2)
    print("✅ _routes.json generado para Cloudflare Pages.")
    
    # 8. Validar archivo index.html principal
    main_index = os.path.join(EXPORT_DIR, "index.html")
    if os.path.exists(main_index):
        size = os.path.getsize(main_index)
        with open(main_index, "r", encoding="utf-8", errors="replace") as f:
            first_few = f.read(500)
        print(f"\nVerificación de Portada principal (index.html):")
        print(f"  Tamaño: {size:,} bytes")
        if "Directory access forbidden" in first_few or size < 1000:
            print("  ❌ ALERTA: index.html sigue conteniendo un error o tamaño insuficiente!")
        else:
            print("  ✅ PORTADA CORRECTA Y COMPLETA (Libre de 403 Forbidden).")
            
    print("\n" + "=" * 70)
    print("🎉 EXPORTACIÓN ESTÁTICA CONCLUIDA CON ÉXITO")
    print("=" * 70)

if __name__ == "__main__":
    main()
