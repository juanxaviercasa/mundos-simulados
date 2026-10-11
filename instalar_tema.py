"""Install shared theme assets in exported pages, without publishing."""
import os
from pathlib import Path
from editorial_site import BASE, write_html


def install():
    count = 0
    for folder, dirs, files in os.walk(BASE):
        dirs[:] = [name for name in dirs if name not in {'.git', 'editorial', 'node_modules', 'wp-content', 'wp-includes', 'backups_posts', '__pycache__'}]
        for name in files:
            if not name.endswith('.html'):
                continue
            path = Path(folder) / name
            text = path.read_text(encoding='utf-8')
            if '</head>' not in text or 'data-ms-theme-assets' in text:
                continue
            assets = '<link data-ms-theme-assets="true" rel="stylesheet" href="/wp-static-arquitect-assets/theme.css"/><script src="/wp-static-arquitect-assets/theme.js"></script>'
            write_html(path, text.replace('</head>', assets + '\n</head>', 1))
            count += 1
    print(f'Tema claro/oscuro instalado en {count} páginas locales.', flush=True)


if __name__ == '__main__':
    install()
