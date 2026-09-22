#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sincronizar_metricas.py
Módulo centralizado para calcular y sincronizar automáticamente todas las métricas,
contadores y catálogos de Mundos Simulados:
- sobre-mi/index.html: Contador de escenarios modelados
- escenarios/index.html: Contador 'Todos (N)', buscador y tarjetas faltantes
- index.html: Hero badge, botón de exploración, HUD panel y badges de categorías
- author/jxaviercabellosgmail-com/index.html: Twitter metadata count
- sitemap.xml: URLs de todos los posts publicados
- Fix de featured images heredadas en posts publicados
"""

import os
import re
import json
import glob
import frontmatter
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_INDEX_PATH = os.path.join(BASE_DIR, "search-index.json")
ARTICULOS_DIR = os.path.join(BASE_DIR, "articulos")

CAT_NAME_DISPLAY = {
    "astrofisica": "Astrofísica",
    "biosfera": "Biosfera",
    "tecnologia": "Tecnología",
    "economia": "Economía"
}

def cargar_articulos_metadata():
    """Lee todos los archivos de articulos/*.md para obtener categoria e imagen destacada."""
    metadata = {}
    for md_path in glob.glob(os.path.join(ARTICULOS_DIR, "*.md")):
        try:
            post = frontmatter.load(md_path)
            slug = post.get("slug")
            if slug:
                metadata[slug] = {
                    "slug": slug,
                    "title": post.get("title", slug),
                    "categoria": post.get("categoria", "astrofisica"),
                    "imagen": post.get("imagen_destacada"),
                    "alt": post.get("alt_destacada", post.get("title", "")),
                    "description": post.get("meta_description", "")
                }
        except Exception as e:
            print(f"Advertencia al leer {md_path}: {e}")
    return metadata

def obtener_metricas(search_db, articulos_meta):
    """Calcula totales y desglose por categoría."""
    total = len(search_db)
    counts = {"astrofisica": 0, "biosfera": 0, "tecnologia": 0, "economia": 0}
    for entry in search_db:
        slug = entry.get("slug")
        meta = articulos_meta.get(slug)
        cat = meta.get("categoria", "astrofisica") if meta else "astrofisica"
        if cat in counts:
            counts[cat] += 1
        else:
            counts["astrofisica"] += 1
    return total, counts

def sincronizar_sobre_mi(total):
    """Actualiza el contador en sobre-mi/index.html."""
    path = os.path.join(BASE_DIR, "sobre-mi", "index.html")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar contador de Orbitron
    pattern = r'(<strong[^>]*font-family:\s*\'Orbitron\'[^>]*>)\s*\d+\+?\s*(</strong>\s*<span[^>]*>Escenarios Modelados</span>)'
    replacement = rf'\g<1>{total}+\g<2>'
    new_content, n = re.subn(pattern, replacement, content)
    
    if n == 0:
        pattern2 = r'>\d+\+<(/strong>\s*<span[^>]*>Escenarios Modelados)'
        new_content, n = re.subn(pattern2, f'>{total}+<\\1', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] sobre-mi/index.html actualizado a {total}+ escenarios ({n} cambios)")

def sincronizar_escenarios(total, search_db, articulos_meta):
    """Actualiza contadores e inyecta tarjetas faltantes en escenarios/index.html."""
    path = os.path.join(BASE_DIR, "escenarios", "index.html")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Actualizar botón Todos (N)
    content = re.sub(r'data-cat="all">Todos\s*\(\d+\)</button>', f'data-cat="all">Todos ({total})</button>', content)

    # 2. Actualizar placeholder del buscador
    content = re.sub(r'placeholder="Buscar entre los \d+ escenarios\.\.\."', f'placeholder="Buscar entre los {total} escenarios..."', content)

    # 3. Detectar artículos faltantes en el grid
    soup = BeautifulSoup(content, "html.parser")
    grid = soup.find("div", id="ms-scenarios-grid")
    
    if grid:
        existing_slugs = set()
        for art in grid.find_all("article", class_="ms-scenario-item"):
            link = art.find("a")
            if link and link.get("href"):
                s = link.get("href").replace("../", "").strip("/")
                existing_slugs.add(s)

        missing_entries = [entry for entry in search_db if entry.get("slug") not in existing_slugs]
        
        if missing_entries:
            print(f"[INFO] Inyectando {len(missing_entries)} tarjetas nuevas en escenarios/index.html...")
            for entry in reversed(missing_entries):
                slug = entry.get("slug")
                meta = articulos_meta.get(slug, {})
                title = entry.get("title", meta.get("title", slug))
                cat = meta.get("categoria", "astrofisica")
                cat_display = CAT_NAME_DISPLAY.get(cat, "Astrofísica")
                snippet = entry.get("snippet", meta.get("description", ""))
                
                img_file = meta.get("imagen") or f"{slug}.webp"
                img_src = f"../wp-content/uploads/2026/08/{img_file}"
                
                card_html = f'''<article class="ms-scenario-item" data-category="{cat}" data-excerpt="{snippet.lower()}" data-title="{title.lower()}" style="background: rgba(13, 20, 36, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
<div>
<div style="aspect-ratio: 16/9; overflow: hidden; background: #080C16;">
<img alt="{title}" loading="lazy" src="{img_src}" style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease;"/>
</div>
<div style="padding: 22px;">
<span class="ms-pill-cat" style="font-size: 0.68rem; margin-bottom: 10px;">{cat_display}</span>
<h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.18rem; font-weight: 700; line-height: 1.35; margin: 8px 0 12px;">
<a href="../{slug}/" style="color: #FFFFFF; text-decoration: none;">{title}</a>
</h3>
<p style="font-size: 0.88rem; color: #94A3B8; line-height: 1.55; margin-bottom: 16px;">
  {snippet}
</p>
</div>
</div>
<div style="padding: 0 22px 22px;">
<a href="../{slug}/" style="display: inline-flex; align-items: center; gap: 6px; color: #00F0FF; font-weight: 600; font-size: 0.9rem; text-decoration: none;">
  Explorar Simulación ➔
</a>
</div>
</article>'''
                new_card_soup = BeautifulSoup(card_html, "html.parser").find("article")
                grid.insert(0, new_card_soup)
            
            content = str(soup)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] escenarios/index.html sincronizado (Total: {total} escenarios)")

def sincronizar_home(total, counts):
    """Actualiza cifras del Hero, HUD y badges de categorías en index.html."""
    path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Hero radar badge
    content = re.sub(
        r'<span>Simulador Cuántico Activo · [^<]+</span>',
        f'<span>Simulador Cuántico Activo · {total} Escenarios Publicados</span>',
        content
    )

    # 2. Botón Hero Explorar Escenarios
    content = re.sub(
        r'<span>🧭 Explorar los \d+\+? Escenarios</span>',
        f'<span>🧭 Explorar los {total} Escenarios</span>',
        content
    )

    # 3. HUD panel: Escenarios Publicados
    content = re.sub(
        r'(<strong id="ms-hud-published">)\d+(</strong>)',
        rf'\g<1>{total}\g<2>',
        content
    )

    # 4. Badges de Dimensiones
    content = re.sub(
        r'(<article class="ms-dim-card ms-dim-astro">[\s\S]*?<span class="ms-dim-badge">)\d+ Simulaciones(</span>)',
        rf'\g<1>{counts["astrofisica"]} Simulaciones\g<2>',
        content
    )
    content = re.sub(
        r'(<article class="ms-dim-card ms-dim-bio">[\s\S]*?<span class="ms-dim-badge">)\d+ Simulaciones(</span>)',
        rf'\g<1>{counts["biosfera"]} Simulaciones\g<2>',
        content
    )
    content = re.sub(
        r'(<article class="ms-dim-card ms-dim-tech">[\s\S]*?<span class="ms-dim-badge">)\d+ Simulaciones(</span>)',
        rf'\g<1>{counts["tecnologia"]} Simulaciones\g<2>',
        content
    )
    content = re.sub(
        r'(<article class="ms-dim-card ms-dim-eco">[\s\S]*?<span class="ms-dim-badge">)\d+ Simulaciones(</span>)',
        rf'\g<1>{counts["economia"]} Simulaciones\g<2>',
        content
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] index.html actualizado con {total} escenarios y desglose {counts}")

def sincronizar_author(total):
    """Actualiza twitter:data2 en author."""
    path = os.path.join(BASE_DIR, "author", "jxaviercabellosgmail-com", "index.html")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(r'<meta content="\d+" name="twitter:data2"/>', f'<meta content="{total}" name="twitter:data2"/>', content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] author metadata actualizado a {total}")

def sincronizar_sitemap(search_db):
    """Asegura que todos los posts publicados estén en sitemap.xml."""
    path = os.path.join(BASE_DIR, "sitemap.xml")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    agregados = 0
    for entry in search_db:
        slug = entry.get("slug")
        url = f"https://mundossimulados.online/{slug}/"
        if url not in content and f"/{slug}/" not in content:
            date_str = entry.get("date", "2026-09-22")
            url_block = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{date_str}T00:00:00+00:00</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
            content = content.replace("</urlset>", url_block)
            agregados += 1

    if agregados > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] sitemap.xml actualizado ({agregados} URLs agregadas)")
    else:
        print("[OK] sitemap.xml ya está al día.")

def corregir_featured_images_posts(search_db, articulos_meta):
    """Corrige imágenes destacadas en posts publicados que tengan la imagen de la plantilla."""
    corregidos = 0
    for entry in search_db:
        slug = entry.get("slug")
        post_html_path = os.path.join(BASE_DIR, slug, "index.html")
        if not os.path.exists(post_html_path):
            continue
        
        meta = articulos_meta.get(slug)
        if not meta or not meta.get("imagen"):
            continue
            
        real_img = meta.get("imagen")
        real_alt = meta.get("alt", entry.get("title", ""))
        
        with open(post_html_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if slug != "piel-camaleonica-camuflaje" and "piel-camaleonica-camuflaje" in content:
            soup = BeautifulSoup(content, "html.parser")
            
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if "piel-camaleonica-camuflaje" in src:
                    img["src"] = f"../wp-content/uploads/2026/08/{real_img}"
                    img["alt"] = real_alt
                    
            for og in soup.find_all("meta", property=["og:image", "twitter:image"]):
                content_val = og.get("content", "")
                if "piel-camaleonica-camuflaje" in content_val:
                    og["content"] = f"../wp-content/uploads/2026/08/{real_img}"
                    
            with open(post_html_path, "w", encoding="utf-8") as f:
                f.write(str(soup))
            corregidos += 1
            
    if corregidos > 0:
        print(f"[OK] Se corrigió la imagen destacada en {corregidos} artículos publicados.")

def sincronizar_todo():
    """Ejecuta todas las tareas de sincronización."""
    print("--- Iniciando Sincronización Global de Métricas y Catálogo ---")
    if not os.path.exists(SEARCH_INDEX_PATH):
        print(f"Error: No se encontró {SEARCH_INDEX_PATH}")
        return
        
    with open(SEARCH_INDEX_PATH, "r", encoding="utf-8") as f:
        search_db = json.load(f)
        
    articulos_meta = cargar_articulos_metadata()
    total, counts = obtener_metricas(search_db, articulos_meta)
    
    print(f"Total Publicados: {total}")
    print(f"Desglose: {counts}")
    
    sincronizar_sobre_mi(total)
    sincronizar_escenarios(total, search_db, articulos_meta)
    sincronizar_home(total, counts)
    sincronizar_author(total)
    sincronizar_sitemap(search_db)
    corregir_featured_images_posts(search_db, articulos_meta)
    
    print("--- Sincronización Global Completada con Éxito ---")

if __name__ == "__main__":
    sincronizar_todo()
