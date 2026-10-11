"""Remove export-only overhead and prepare stable, cache-versioned assets."""
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from editorial_site import BASE, card_image, write_html
from corregir_lectura import normalize_reading

VERSION = '20261011-8'


def clean_script(match):
    script = match.group(0)
    # These are expired scripts copied from the source response, not live security config.
    if '__CF$cv$params' in script or 'wpemojisettings' in script.lower() or 'wp-emoji-settings' in script or 'wp-emoji-loader' in script or 'animateCounter(hudEl' in script:
        return ''
    if 'src=' in script and 'theme.js' not in script and not re.search(r'\bdefer\b', script.split('>')[0]):
        return script.replace('<script', '<script defer', 1)
    return script


def optimize_exports():
    count = 0
    for folder, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in {'.git', 'editorial', 'artifacts', 'node_modules', 'wp-content', 'wp-includes', 'backups_posts', '__pycache__'}]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = Path(folder) / name
            text = path.read_text(encoding='utf-8')
            text = normalize_reading(text)
            value = re.sub(r'<script\b[^>]*>.*?</script>', clean_script, text, flags=re.S | re.I)
            value = value.replace('mundossimulados.onine', 'mundossimulados.online')
            value = value.replace('Portal de divulgación científica, astrofísica extrema y modelos matemáticos de realidades alternas.', 'Escenarios hipotéticos para explorar ciencia, tecnología y sociedad.')
            value = re.sub(r'(/wp-static-arquitect-assets/(?:theme\.css|theme\.js|editorial\.css|blog-filters\.js))(?:\?v=[^"\s<>]+)?', r'\1?v=' + VERSION, value)
            if value != text:
                write_html(path, value)
                count += 1
    path = BASE / 'index.html'
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    for image in soup.select('.ms-universe img'):
        src = image.get('src', '')
        source = BASE / src.removeprefix('./').lstrip('/')
        if source.is_file() and 'thumbs/' not in src:
            image['src'] = card_image(source)
            image['loading'] = 'lazy'
            image['decoding'] = 'async'
            with Image.open(source) as original:
                image['width'], image['height'] = original.size
            image.attrs.pop('srcset', None)
    hero = '/wp-content/uploads/2026/09/hero-4d-dimension-1.webp'
    if not soup.select_one('link[data-ms-hero-preload]'):
        soup.head.append(soup.new_tag('link', attrs={'rel': 'preload', 'as': 'image', 'href': hero, 'fetchpriority': 'high', 'data-ms-hero-preload': 'true'}))
    write_html(path, str(soup))
    print(f'Exportaciones optimizadas: {count}; portada sin descarga ni animación del contador.')


if __name__ == '__main__':
    optimize_exports()
