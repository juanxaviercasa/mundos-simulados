"""Build crawlable blog navigation and keep exported article metadata in sync."""
import json
import re
import time
from html import escape
from pathlib import Path
from urllib.parse import urljoin
from urllib.parse import urlencode

import frontmatter
import markdown
from PIL import Image
from bs4 import BeautifulSoup
from related_articles import build_related

BASE = Path(__file__).resolve().parent
SITE = "https://mundossimulados.online"
CATEGORIES = {"astrofisica": "Astrofísica", "biosfera": "Biosfera", "tecnologia": "Tecnología", "economia": "Economía"}
PRACTICAL_LINKS = {
    'semana-laboral-dos-dias': ('finanzas/calculadora-sobrecostos-laborales', 'Explorar costos laborales', 'Si administras una pyme, distingue el escenario hipotético de tus costos actuales. Puedes explorar componentes del costo laboral con una herramienta de Nube para Pymes.'),
    'redes-neuronales-planetarias': ('operaciones/simulador-tco-fisico-nube', 'Comparar costos de infraestructura', 'Una red planetaria es un escenario hipotético. Para una decisión empresarial concreta, Nube para Pymes ofrece un simulador de costos de infraestructura física y en la nube.'),
    'apagon-global-internet-7-dias': ('operaciones/simulador-tco-fisico-nube', 'Explorar costos de infraestructura', 'Para una pyme, la continuidad operativa requiere decisiones concretas. Explora los costos de infraestructura con Nube para Pymes; un cálculo no sustituye un plan de contingencia.'),
}


def fragment(html):
    return BeautifulSoup(html, "html.parser")


def write_html(path, html):
    """Replace whole pages atomically, retrying transient Windows file locks."""
    temporary = path.with_name(path.name + '.ms-edit.tmp')
    try:
        temporary.write_text(html, encoding='utf-8')
        for attempt in range(5):
            try:
                temporary.replace(path)
                return
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(.2)
    finally:
        temporary.unlink(missing_ok=True)


def asset(soup):
    if not soup.select_one('link[data-ms-editorial]'):
        soup.head.append(fragment('<link data-ms-editorial="true" rel="stylesheet" href="/wp-static-arquitect-assets/editorial.css"/>'))
    if not soup.select_one('link[data-ms-theme-assets]'):
        soup.head.append(fragment('<link data-ms-theme-assets="true" rel="stylesheet" href="/wp-static-arquitect-assets/theme.css"/><script src="/wp-static-arquitect-assets/theme.js"></script>'))
    # Keep the tiny preference script synchronous to avoid a theme flash.
    for script in soup.select('script[src]'):
        if 'theme.js' not in script['src']:
            script['defer'] = ''


def card_image(source):
    """Create a small derivative for listing cards, preserving the original."""
    target = BASE / 'wp-static-arquitect-assets/thumbs' / source.name
    target = target.with_suffix('.webp')
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
        with Image.open(source) as image:
            image.thumbnail((640, 360))
            image.convert('RGB').save(target, 'WEBP', quality=74, method=6)
    return '/wp-static-arquitect-assets/thumbs/' + target.name


def metadata(entry):
    path = BASE / "articulos" / f"{entry['slug']}.md"
    return frontmatter.load(path).metadata if path.exists() else {}


def recover_error_pages(entries):
    """Recover failed exports from existing Markdown, without consuming drafts."""
    broken = []
    for entry in entries:
        path = BASE / entry['slug'] / 'index.html'
        if path.exists() and re.search(r'<title[^>]*>\s*429\b', path.read_text(encoding='utf-8'), re.I):
            source = BASE / 'articulos' / f"{entry['slug']}.md"
            if not source.exists():
                raise ValueError(f'No hay fuente Markdown para recuperar {entry["slug"]}')
            post = frontmatter.load(source)
            if post.get('slug') != entry['slug'] or not post.content.strip():
                raise ValueError(f'Fuente de recuperación inválida: {source}')
            broken.append((entry, post, path))
    if not broken:
        return 0
    template = (BASE / 'piel-camaleonica-camuflaje/index.html').read_text(encoding='utf-8')
    for entry, post, path in broken:
        soup = fragment(template)
        if soup.title is None:
            soup.head.append(soup.new_tag('title'))
        soup.title.string = entry['title'] + ' - Mundos Simulados'
        soup.select_one('h1.entry-title').string = entry['title']
        description = post.get('meta_description', '')
        set_meta(soup, 'description', description)
        body = post.content
        for number in (1, 2):
            image = post.get(f'imagen_interna_{number}')
            markup = ''
            if image and (BASE / 'wp-content/uploads/2026/08' / image).exists():
                markup = f'<figure><img src="/wp-content/uploads/2026/08/{escape(image)}" alt="{escape(post.get(f"alt_interna_{number}", ""), quote=True)}" loading="lazy"/></figure>'
            body = body.replace('{{IMAGEN_INTERNA_' + str(number) + '}}', markup)
        content = soup.select_one('.entry-content')
        content.clear()
        content.append(fragment(markdown.markdown(body, extensions=['extra'])))
        image = soup.select_one('.post-thumb img')
        featured = post.get('imagen_destacada')
        if image and featured and (BASE / 'wp-content/uploads/2026/08' / featured).exists():
            image['src'] = '/wp-content/uploads/2026/08/' + featured
            image['alt'] = post.get('alt_destacada', entry['title'])
            for attr in ('srcset', 'sizes'):
                image.attrs.pop(attr, None)
        for tag in soup.select('.post-navigation, link[rel="shortlink"], link[rel="EditURI"]'):
            tag.decompose()
        for article in soup.select('article[id]'):
            article['id'] = 'article-' + entry['slug']
        write_html(path, str(soup))
    print(f'Exportaciones 429 recuperadas desde Markdown existente: {len(broken)}')
    return len(broken)


def recover_existing_exports():
    """Repair catalogued error exports without publishing or consuming drafts."""
    entries = json.loads((BASE / 'search-index.json').read_text(encoding='utf-8'))
    broken = [entry for entry in entries if re.search(
        r'<title[^>]*>\s*429\b',
        (BASE / entry['slug'] / 'index.html').read_text(encoding='utf-8'), re.I)]
    recover_error_pages(entries)
    for entry in broken:
        update_article(entry, entries)
    return len(broken)


def sidebar(entries, current=None, headings=()):
    toc = "".join(f'<li><a href="#{escape(h[0], quote=True)}">{escape(h[1])}</a></li>' for h in headings)
    latest = ""
    for e in [e for e in entries if e['slug'] != current][:5]:
        latest += f'<li><a href="/{escape(e["slug"])}/">{escape(e["title"])}</a><small>{escape(e["date"][:10])}</small></li>'
    cats = "".join(f'<li><a href="/blog/?category={key}">{name}</a></li>' for key, name in CATEGORIES.items())
    return f'''<div class="ms-editorial-sidebar">
      <section><h2>Explora el blog</h2><form action="/blog/" role="search"><label for="ms-sidebar-search">Buscar artículos</label><input id="ms-sidebar-search" name="q" type="search" placeholder="Tema o palabra clave"/><button type="submit">Buscar</button></form></section>
      {f'<nav aria-label="En este artículo"><h2>En este artículo</h2><ol>{toc}</ol></nav>' if toc else ''}
      <section><h2>Últimas entradas</h2><ul>{latest}</ul><a href="/blog/">Ver todas las entradas →</a></section>
      <nav aria-label="Categorías"><h2>Por temática</h2><ul>{cats}</ul></nav>
      <section><h2>Sobre el proyecto</h2><p>Escenarios hipotéticos para explorar ciencia, tecnología y sociedad.</p><a href="/sobre-mi/">Conoce al autor y el proyecto →</a></section>
    </div>'''


def set_meta(soup, key, value, property=False):
    attr = "property" if property else "name"
    tag = soup.find("meta", attrs={attr: key})
    if tag is None:
        tag = soup.new_tag("meta", attrs={attr: key})
        soup.head.append(tag)
    tag["content"] = value


def update_article(entry, entries, recommendations=None):
    path = BASE / entry['slug'] / 'index.html'
    if not path.exists():
        return
    soup = fragment(path.read_text(encoding='utf-8'))
    content = soup.select_one('.entry-content')
    if not content or not soup.select_one('h1.entry-title'):
        return
    asset(soup)
    meta = metadata(entry)
    for title in soup.select('#ez-toc-container .ez-toc-title'):
        title.string = 'Tabla de contenidos'
    for image in soup.select('.ast-single-post-featured-section img'):
        image['loading'] = 'eager'
        image['fetchpriority'] = 'high'
        image['decoding'] = 'async'
    respond = soup.select_one('#respond')
    if respond:
        respond.replace_with(fragment('<section class="ms-reader-note"><h2>Correcciones y comentarios</h2><p>Los comentarios públicos no están habilitados en esta versión. Puedes enviar una observación editorial a <a href="mailto:contacto@mundossimulados.online">contacto@mundossimulados.online</a>, indicando el artículo y la afirmación que deseas revisar.</p></section>'))
    for bridge in soup.select('.ms-todolima-bridge'):
        target = bridge.select_one('a[href*="todolima.com"]')
        if not target:
            bridge.decompose()
            continue
        href = target['href']
        label = target.get_text(' ', strip=True).replace('verificados', '').replace('colegiados', '').rstrip(' →').strip()
        bridge.clear()
        bridge.append(fragment(f'<h2>Servicios locales relacionados</h2><p>Para una necesidad real en Lima, puedes consultar información del directorio de Todo Lima y contactar directamente con el proveedor para confirmar disponibilidad, condiciones y credenciales.</p><p><a href="{escape(href, quote=True)}">{escape(label)} →</a></p><small>Proyecto del mismo autor. El directorio no valida las hipótesis del escenario ni garantiza la calidad de cada proveedor.</small>'))
        bridge.attrs = {'class': ['ms-todolima-bridge', 'ms-practical-bridge']}
    for old in soup.select('.post-navigation, .ast-related-posts-wrap, .ms-related-articles'):
        old.decompose()
    if recommendations is None:
        recommendations = build_related(entries, {e['slug']: metadata(e).get('categoria', '') for e in entries})
    by_slug = {e['slug']: e for e in entries}
    related = recommendations.get(entry['slug'], [])
    links = ''.join(f'<li><a href="/{escape(slug)}/">{escape(by_slug[slug]["title"])}</a></li>' for slug in related if slug in by_slug)
    category = meta.get('categoria', '')
    hub = f'<p><a href="/blog/?category={escape(category, quote=True)}">Explorar todos los escenarios de {escape(CATEGORIES[category])} →</a></p>' if category in CATEGORIES else '<p><a href="/blog/">Explorar el catálogo de escenarios →</a></p>'
    content.insert_after(fragment(f'<nav class="ms-related-articles" aria-label="Lecturas relacionadas"><h2>Continúa explorando</h2><p>Otros escenarios hipotéticos relacionados; estas lecturas no son fuentes científicas del artículo.</p><ul>{links}</ul>{hub}</nav>'))
    for old in content.select('.ms-practical-bridge:not(.ms-todolima-bridge)'):
        old.decompose()
    if entry['slug'] in PRACTICAL_LINKS:
        route, label, description = PRACTICAL_LINKS[entry['slug']]
        query = urlencode({'utm_source': 'mundossimulados', 'utm_medium': 'referral', 'utm_campaign': 'ecosistema', 'utm_content': entry['slug']})
        target = 'https://nubeparapymes.online/herramientas/' + route + '/?' + query
        owner = 'https://todolima.com/auditoria?' + query
        content.append(fragment(f'<aside class="ms-practical-bridge"><h2>Del escenario a una decisión práctica</h2><p>{escape(description)}</p><p><a href="{escape(target, quote=True)}">{escape(label)} en Nube para Pymes →</a></p><p>Si tu negocio está en Lima y buscas apoyo para su presencia digital, puedes <a href="{escape(owner, quote=True)}">consultar la auditoría de Todo Lima</a>.</p><small>Proyectos del mismo autor. Esta recomendación no respalda las hipótesis científicas del artículo.</small></aside>'))
    cat = meta.get('categoria', '')
    headings = []
    for n, h in enumerate(content.select('h2, h3'), 1):
        if h.find_parent(id='ez-toc-container'):
            continue
        h['id'] = h.get('id') or f'section-{n}'
        headings.append((h['id'], h.get_text(' ', strip=True)))
    for a in content.select('a[href]'):
        if 'pantheonsite.io' in a['href'] and '#' in a['href']:
            target = a['href'].split('#', 1)[1]
            if soup.find(id=target):
                a['href'] = '#' + target
    secondary = soup.select_one('#secondary')
    if secondary:
        secondary.clear()
        secondary.append(fragment(sidebar(entries, entry['slug'], headings)))
    url = f"{SITE}/{entry['slug']}/"
    canonical = soup.find('link', rel='canonical')
    if canonical:
        canonical['href'] = url
    date = entry['date']
    set_meta(soup, 'og:url', url, True)
    # Rebuild copied schema only when it points at a different article.
    schemas = soup.find_all('script', type='application/ld+json')
    copied = any('piel-camaleonica-camuflaje' in s.get_text() for s in schemas) and entry['slug'] != 'piel-camaleonica-camuflaje'
    if copied or meta.get('editorial_status') == 'reviewed_draft':
        modified = meta.get('editorial_review_date', date)
        if meta.get('editorial_status') == 'reviewed_draft':
            if soup.title is None:
                soup.head.append(soup.new_tag('title'))
            soup.title.string = entry['title'] + ' - Mundos Simulados'
            soup.select_one('h1.entry-title').string = entry['title']
            set_meta(soup, 'description', meta.get('meta_description', ''))
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '') if desc_tag else meta.get('meta_description', '')
        image = soup.select_one('.post-thumb img')
        image_url = urljoin(url, image['src']) if image and image.get('src') else None
        for key in ['og:title', 'twitter:title']:
            set_meta(soup, key, entry['title'], key.startswith('og:'))
        for key in ['og:description', 'twitter:description']:
            set_meta(soup, key, description, key.startswith('og:'))
        if image_url:
            for key in ['og:image', 'og:image:secure_url', 'twitter:image']:
                set_meta(soup, key, image_url, key.startswith('og:'))
            set_meta(soup, 'og:image:alt', image.get('alt', entry['title']), True)
        set_meta(soup, 'article:published_time', date, True)
        set_meta(soup, 'article:modified_time', modified, True)
        set_meta(soup, 'article:section', CATEGORIES.get(cat, cat), True)
        for t in soup.select('.entry-meta .published'):
            t.clear()
            t.append(fragment(f'<time datetime="{escape(date)}">{escape(date[:10])}</time>'))
        for s in schemas:
            s.decompose()
        schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', '@id': url + '#article', 'url': url, 'headline': entry['title'], 'description': description, 'datePublished': date, 'dateModified': date, 'mainEntityOfPage': url, 'inLanguage': 'es', 'author': {'@type': 'Person', 'name': 'Xavier Cabello', 'url': SITE + '/sobre-mi/'}, 'publisher': {'@type': 'Organization', 'name': 'Mundos Simulados', 'url': SITE}, 'articleSection': CATEGORIES.get(cat, cat)}
        if image_url:
            schema['image'] = image_url
        schema['dateModified'] = modified
        script = soup.new_tag('script', type='application/ld+json')
        script.string = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
        soup.head.append(script)
    write_html(path, str(soup))


def build_blog(entries):
    path = BASE / 'blog/index.html'
    soup = fragment(path.read_text(encoding='utf-8'))
    asset(soup)
    primary = soup.select_one('#primary')
    primary['class'] = ['content-area', 'primary', 'ms-blog-primary']
    primary.clear()
    cards = []
    for number, e in enumerate(entries):
        meta = metadata(e)
        cat = meta.get('categoria', '')
        img = meta.get('imagen_destacada')
        img_path = BASE / 'wp-content/uploads/2026/08' / img if img else None
        source = card_image(img_path) if img_path and img_path.exists() else None
        loading = 'eager' if number == 0 else 'lazy'
        priority = ' fetchpriority="high"' if number == 0 else ''
        image = f'<img src="{escape(source)}" alt="{escape(meta.get("alt_destacada", e["title"]), quote=True)}" loading="{loading}"{priority} width="640" height="360"/>' if source else '<div class="ms-card-placeholder" aria-hidden="true">MS</div>'
        snippet = re.sub(r'\[&hellip;\]', '…', e.get('snippet', ''))
        cards.append(f'''<article class="ms-editorial-card" data-category="{escape(cat)}" data-date="{escape(e['date'][:10])}"><a class="ms-card-image" href="/{escape(e['slug'])}/" aria-label="{escape(e['title'], quote=True)}">{image}</a><div class="ms-card-copy"><span class="ms-card-category">{escape(CATEGORIES.get(cat, 'Escenarios'))}</span><h2><a href="/{escape(e['slug'])}/">{escape(e['title'])}</a></h2><p>{escape(snippet)}</p><time datetime="{escape(e['date'])}">{escape(e['date'][:10])}</time></div></article>''')
    options = ''.join(f'<option value="{key}">{value}</option>' for key, value in CATEGORIES.items())
    primary.append(fragment(f'''<main id="main" class="site-main ms-editorial-blog"><header class="ms-blog-intro"><span class="ms-card-category">La bitácora de Mundos Simulados</span><h1>Ciencia para imaginar otros mundos</h1><p>Explora escenarios hipotéticos de astrofísica, biosfera, tecnología y economía. Las publicaciones más recientes aparecen primero.</p></header><form id="ms-blog-filters" class="ms-blog-filters" role="search"><div><label for="ms-blog-search">Buscar en el blog</label><input id="ms-blog-search" type="search" name="q" placeholder="¿Qué te gustaría explorar?"/></div><div><label for="ms-blog-category">Temática</label><select id="ms-blog-category" name="category"><option value="">Todas las temáticas</option>{options}</select></div><div><label for="ms-blog-order">Ordenar</label><select id="ms-blog-order"><option value="newest">Más recientes</option><option value="oldest">Más antiguas</option></select></div><div><label for="ms-blog-since">Publicadas desde</label><input id="ms-blog-since" type="date" name="since"/></div><button type="reset">Limpiar filtros</button></form><p id="ms-blog-results" role="status" aria-live="polite">{len(entries)} artículos</p><div id="ms-blog-grid" class="ms-editorial-grid">{''.join(cards)}</div><p id="ms-blog-empty" hidden>No encontramos artículos con esos filtros. Prueba otra búsqueda.</p><button id="ms-blog-more" type="button" hidden>Mostrar más artículos</button><noscript><p>Todos los artículos se muestran por fecha. Activa JavaScript para usar los filtros.</p></noscript></main>'''))
    # The listing does not use the exported TOC plugin.
    for tag in soup.select('link[href*="easy-table-of-contents"], script[src*="easy-table-of-contents"], script[id^="ez-toc"], style[id^="ez-toc"]'):
        tag.decompose()
    script = soup.select_one('script[data-ms-blog]')
    filters = soup.select_one('#ms-blog-filters')
    disclosure = soup.new_tag('details', attrs={'class': 'ms-filter-details', 'open': True})
    filters.wrap(disclosure)
    summary = soup.new_tag('summary')
    summary.string = 'Filtrar y ordenar artículos'
    disclosure.insert(0, summary)
    if not script:
        soup.body.append(fragment('<script data-ms-blog="true" src="/wp-static-arquitect-assets/blog-filters.js?v=20261011-2" defer></script>'))
    else:
        script['src'] = '/wp-static-arquitect-assets/blog-filters.js?v=20261011-2'
    for tag in soup.find_all('link', rel=['next', 'prev']):
        tag.decompose()
    canonical = soup.find('link', rel='canonical')
    if canonical:
        canonical['href'] = SITE + '/blog/'
    set_meta(soup, 'og:url', SITE + '/blog/', True)
    for old in soup.find_all('script', type='application/ld+json'):
        old.decompose()
    schema = soup.new_tag('script', type='application/ld+json')
    schema.string = json.dumps({'@context': 'https://schema.org', '@type': 'CollectionPage', '@id': SITE + '/blog/#webpage', 'url': SITE + '/blog/', 'name': 'Blog de Mundos Simulados', 'inLanguage': 'es', 'isPartOf': {'@type': 'WebSite', 'url': SITE, 'name': 'Mundos Simulados'}}, ensure_ascii=False)
    soup.head.append(schema)
    write_html(path, str(soup))


def sync_editorial():
    entries = json.loads((BASE / 'search-index.json').read_text(encoding='utf-8'))
    entries = sorted({e['slug']: e for e in entries}.values(), key=lambda e: e['date'], reverse=True)
    recover_error_pages(entries)
    build_blog(entries)
    recommendations = build_related(entries, {e['slug']: metadata(e).get('categoria', '') for e in entries})
    for e in entries:
        update_article(e, entries, recommendations)
    print(f'Blog, barras laterales y metadatos sincronizados: {len(entries)} artículos')


if __name__ == '__main__':
    sync_editorial()
