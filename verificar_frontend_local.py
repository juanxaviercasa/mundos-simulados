"""Verify the exported catalog and related-reading destinations before publishing."""
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from bs4 import BeautifulSoup
from editorial_site import BASE, SITE


def verify():
    entries = json.loads((BASE / 'search-index.json').read_text(encoding='utf-8'))
    slugs = {entry['slug'] for entry in entries}
    assert len(slugs) == len(entries)
    related_count = 0
    missing_images = []
    for entry in entries:
        slug = entry['slug']
        text = (BASE / slug / 'index.html').read_text(encoding='utf-8')
        soup = BeautifulSoup(text, 'html.parser')
        assert soup.select_one('h1.entry-title'), slug
        assert not soup.select_one('.post-navigation'), slug
        assert not soup.select_one('#respond form'), slug
        assert not soup.title.get_text().startswith('429'), slug
        assert soup.select_one('link[rel=canonical]')['href'] == SITE + '/' + slug + '/', slug
        assert soup.select_one('script[src*="theme.js"]'), slug
        assert soup.select_one('#secondary .ms-editorial-sidebar'), slug
        nav = soup.select_one('.ms-related-articles')
        assert nav, slug
        targets = [a['href'].strip('/') for a in nav.select('li a[href]')]
        assert len(targets) <= 3 and len(targets) == len(set(targets)), slug
        assert slug not in targets and set(targets) <= slugs, slug
        related_count += len(targets)
        for anchor in soup.select('#secondary a[href^="#"]'):
            assert soup.find(id=anchor['href'][1:]), (slug, anchor['href'])
        for image in soup.select('img[src]'):
            parsed = urlsplit(urljoin(SITE + '/' + slug + '/', image['src']))
            if parsed.hostname == 'mundossimulados.online' and not (BASE / unquote(parsed.path).lstrip('/')).is_file():
                missing_images.append({'slug': slug, 'src': image['src']})
    blog = BeautifulSoup((BASE / 'blog/index.html').read_text(encoding='utf-8'), 'html.parser')
    assert len(blog.select('.ms-editorial-card')) == len(entries)
    assert blog.select_one('.ms-editorial-card img')['loading'] == 'eager'
    assert blog.select_one('.ms-editorial-card img')['fetchpriority'] == 'high'
    result = {'articles': len(entries), 'related_links': related_count, 'missing_images': missing_images, 'canonical_sidebar_anchors_theme_and_static_comment_checks': 'passed'}
    (BASE / 'editorial/frontend_validacion_2026-10-11.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    assert not missing_images, 'Hay imágenes locales faltantes'


if __name__ == '__main__':
    verify()
