"""Normalize legacy article labels and cache versions without reformatting pages."""
import re


def normalize_reading(html):
    html = re.sub(r'(wp-static-arquitect-assets/(?:theme\.(?:css|js)|editorial\.css|blog-filters\.js)\?v=)20261011-[34]', r'\g<1>20261011-5', html)
    html = re.sub(r'(<p\b[^>]*class="ez-toc-title"[^>]*>)Table of Contents(</p>)', r'\1Tabla de contenidos\2', html)
    html = html.replace('>Toggle</span>', '>Mostrar u ocultar índice</span>')
    def prioritize(match):
        tag = match.group(0)
        if 'wp-post-image' not in tag:
            return tag
        for attr, value in [('loading', 'eager'), ('fetchpriority', 'high'), ('decoding', 'async')]:
            if re.search(r'\b' + attr + r'=', tag):
                tag = re.sub(r'\b' + attr + r'="[^"]*"', attr + '="' + value + '"', tag)
            else:
                tag = tag.replace('<img ', '<img ' + attr + '="' + value + '" ', 1)
        return tag
    if 'single-post' in html:
        html = re.sub(r'<img\b[^>]*>', prioritize, html)
    return html
