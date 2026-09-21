#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte todas las rutas absolutas (/wp-content, /wp-includes, enlaces internos)
a rutas RELATIVAS exactas según la profundidad de cada archivo HTML.
Esto garantiza que el sitio funcione al 100% de forma idéntica en:
1. GitHub Pages (https://usuario.github.io/mundos-simulados/)
2. Cloudflare Pages (https://mundos-simulados.pages.dev/)
3. Dominio personalizado (https://mundossimulados.online/)
4. Navegador local sin servidor (file:///)
"""

import os
import sys
import re
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

EXPORT_DIR = os.path.abspath("mundossimuladosexport")

def get_all_html_files(base_dir):
    """Encuentra todos los archivos HTML en el directorio de exportación."""
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        if '.git' in root:
            continue
        for f in files:
            if f.endswith('.html'):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                html_files.append((full_path, rel_path))
    return html_files

def get_depth_prefix(rel_path):
    """Calcula el prefijo relativo según la profundidad de la carpeta."""
    dirname = os.path.dirname(rel_path)
    if not dirname or dirname == '.':
        return "./"
    parts = dirname.replace('\\', '/').split('/')
    depth = len(parts)
    return "../" * depth

def process_html_file(full_path, rel_path, known_slugs):
    prefix = get_depth_prefix(rel_path)
    
    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # 1. Assets con leading slash
    # /wp-content/ -> {prefix}wp-content/
    content = re.sub(r'([\'"])/wp-content/', r'\1' + prefix + 'wp-content/', content)
    # /wp-includes/ -> {prefix}wp-includes/
    content = re.sub(r'([\'"])/wp-includes/', r'\1' + prefix + 'wp-includes/', content)
    # /wp-static-arquitect-assets/ -> {prefix}wp-static-arquitect-assets/
    content = re.sub(r'([\'"])/wp-static-arquitect-assets/', r'\1' + prefix + 'wp-static-arquitect-assets/', content)

    # 2. Enlaces a categorías
    content = re.sub(r'href=[\'"]/category/([^\'"]+)/?[\'"]', r'href="' + prefix + r'category/\1/"', content)
    
    # 3. Enlaces a autor
    content = re.sub(r'href=[\'"]/author/([^\'"]+)/?[\'"]', r'href="' + prefix + r'author/\1/"', content)

    # 4. Enlaces a páginas fijas conocidas
    fixed_pages = ['sobre-mi', 'escenarios', 'blog', 'politica-de-privacidad']
    for fp in fixed_pages:
        content = re.sub(r'href=[\'"]/' + fp + r'/?[\'"]', r'href="' + prefix + fp + r'/"', content)

    # 5. Enlaces a la portada (home)
    # Reemplazar href="/" por href="{prefix}"
    home_link = prefix if prefix != "./" else "./"
    content = re.sub(r'href=[\'"]/(?:index\.html)?[\'"]', r'href="' + home_link + r'"', content)

    # 6. Enlaces a los 170 artículos conocidos
    for slug in known_slugs:
        # href="/slug/" o href="/slug"
        pattern = r'href=[\'"]/' + re.escape(slug) + r'/?[\'"]'
        replacement = r'href="' + prefix + slug + r'/"'
        content = re.sub(pattern, replacement, content)

    # 7. Inyectar data-wpsa-root en el body para el buscador Spotlight
    root_val = prefix.rstrip('/') if prefix != "./" else "."
    if 'data-wpsa-root=' not in content:
        content = re.sub(r'<body([^>]*)>', r'<body\1 data-wpsa-root="' + root_val + r'">', content, count=1)
    else:
        content = re.sub(r'data-wpsa-root=[\'"][^\'"]*[\'"]', r'data-wpsa-root="' + root_val + r'"', content)

    # 8. Limpiar dns-prefetch y oembed de Pantheon
    content = re.sub(r'<link[^>]+dns-prefetch[^>]+dev-simulandomundos[^>]*>', '', content, flags=re.I)
    content = re.sub(r'<link[^>]+alternate[^>]+oembed[^>]*>', '', content, flags=re.I)

    # 9. Limpiar cualquier remanente de Pantheon o mundossimulados.online
    content = content.replace("https://dev-simulandomundos.pantheonsite.io/", prefix)
    content = content.replace("http://dev-simulandomundos.pantheonsite.io/", prefix)
    content = content.replace("https://dev-simulandomundos.pantheonsite.io", "")
    content = content.replace("http://dev-simulandomundos.pantheonsite.io", "")

    content = content.replace("https://mundossimulados.online/", prefix)
    content = content.replace("http://mundossimulados.online/", prefix)
    content = content.replace("https://mundossimulados.online", "")
    content = content.replace("http://mundossimulados.online", "")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_search_client_js():
    """Actualiza search-client.js para que use rutas relativas según data-wpsa-root."""
    js_path = os.path.join(EXPORT_DIR, "wp-static-arquitect-assets", "search-client.js")
    if not os.path.exists(js_path):
        return
    with open(js_path, "r", encoding="utf-8", errors="replace") as f:
        js = f.read()

    # Asegurar que getIndexUrl use la ruta relativa del data-wpsa-root
    old_fn = """    function getIndexUrl() {
        // Soporte para URLs relativas o root-relative
        const rootAttr = document.body.getAttribute('data-wpsa-root');
        if (rootAttr) {
            return rootAttr.replace(/\/+$/, '') + '/search-index.json';
        }
        return '/search-index.json';
    }"""
    
    new_fn = """    function getIndexUrl() {
        const rootAttr = document.body.getAttribute('data-wpsa-root');
        const prefix = (rootAttr && rootAttr !== '.') ? (rootAttr.replace(/\/+$/, '') + '/') : './';
        return prefix + 'search-index.json';
    }"""

    if old_fn in js:
        js = js.replace(old_fn, new_fn)
    else:
        # Regex replacement if whitespace differs
        js = re.sub(
            r'function getIndexUrl\(\)\s*\{[^}]+\}',
            """function getIndexUrl() {
        const rootAttr = document.body.getAttribute('data-wpsa-root');
        const prefix = (rootAttr && rootAttr !== '.') ? (rootAttr.replace(/\/+$/, '') + '/') : './';
        return prefix + 'search-index.json';
    }""",
            js
        )

    # Actualizar renderResults para que anteponga el rootPrefix a item.url
    js = js.replace(
        "'<a href=\"' + escapeHtml(item.url) + '\" class=\"wpsa-search-item-link\">'",
        """'<a href=\"' + (document.body.getAttribute('data-wpsa-root') ? document.body.getAttribute('data-wpsa-root').replace(/\\/+$/, '') + '/' : './') + item.slug + '/\" class=\"wpsa-search-item-link\">'"""
    )

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("✅ search-client.js actualizado para enlaces de búsqueda 100% relativos.")

def main():
    print("Obteniendo lista de slugs exportados...")
    known_slugs = [d for d in os.listdir(EXPORT_DIR) if os.path.isdir(os.path.join(EXPORT_DIR, d)) and not d.startswith('.') and d not in ['wp-content', 'wp-includes', 'wp-static-arquitect-assets', 'category', 'author']]
    print(f"Total de slugs detectados: {len(known_slugs)}")

    html_files = get_all_html_files(EXPORT_DIR)
    print(f"Procesando {len(html_files)} archivos HTML...")

    count = 0
    for full_path, rel_path in html_files:
        process_html_file(full_path, rel_path, known_slugs)
        count += 1
        if count % 25 == 0 or count == len(html_files):
            print(f"  [{count}/{len(html_files)}] Procesado: {rel_path}")

    update_search_client_js()
    print("\n🎉 Todas las rutas han sido convertidas exitosamente a formato RELATIVO.")

if __name__ == "__main__":
    main()
