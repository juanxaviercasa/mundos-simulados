import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup
import editorial_site as site


class EditorialBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.editorial-test-', dir=Path(__file__).resolve().parent)
        self.base = Path(self.temp.name)
        self.override = patch.object(site, 'BASE', self.base)
        self.override.start()
        self.entries = [{'slug': 'nuevo-articulo', 'title': 'Ciencia & <futuro>', 'date': '2026-10-10', 'snippet': 'Una hipótesis.'}]
        (self.base / 'nuevo-articulo').mkdir()
        (self.base / 'blog').mkdir()
        (self.base / 'articulos').mkdir()
        (self.base / 'articulos/nuevo-articulo.md').write_text('---\ncategoria: economia\n---\nTexto', encoding='utf-8')
        self.article = self.base / 'nuevo-articulo/index.html'
        self.article.write_text('''<html><head><link rel="canonical" href="../viejo/"/><meta name="description" content="Descripción correcta"/><script type="application/ld+json">{"headline":"piel-camaleonica-camuflaje"}</script></head><body><h1 class="entry-title">Ciencia</h1><div class="entry-meta"><span class="published">septiembre 19</span></div><div class="post-thumb"><img src="../imagen.webp" alt="Imagen"/></div><div class="entry-content"><h2 id="primero">Pregunta</h2><p>Respuesta</p><h2>Más detalles</h2><a href="https://dev-simulandomundos.pantheonsite.io/?p=2/#primero">Índice</a></div><div id="secondary"></div></body></html>''', encoding='utf-8')
        (self.base / 'blog/index.html').write_text('<html><head><link rel="next" href="page/2/"/><link rel="canonical" href="../blog/"/></head><body><div id="primary"></div></body></html>', encoding='utf-8')

    def tearDown(self):
        self.override.stop()
        self.temp.cleanup()

    def test_copied_article_identity_is_replaced(self):
        site.update_article(self.entries[0], self.entries)
        soup = BeautifulSoup(self.article.read_text(encoding='utf-8'), 'html.parser')
        schema = json.loads(soup.find('script', type='application/ld+json').string)
        self.assertEqual(schema['headline'], self.entries[0]['title'])
        self.assertEqual(schema['datePublished'], '2026-10-10')

    def test_review_updates_schema_without_changing_publication_date(self):
        site.update_article(self.entries[0], self.entries)
        (self.base / 'articulos/nuevo-articulo.md').write_text('---\ncategoria: economia\neditorial_status: reviewed_draft\neditorial_review_date: "2026-10-11"\nmeta_description: Descripción revisada\n---\nTexto', encoding='utf-8')
        self.entries[0]['title'] = 'Título revisado'
        site.update_article(self.entries[0], self.entries)
        soup = BeautifulSoup(self.article.read_text(encoding='utf-8'), 'html.parser')
        schema = json.loads(soup.find('script', type='application/ld+json').string)
        self.assertEqual(schema['headline'], 'Título revisado')
        self.assertEqual(schema['description'], 'Descripción revisada')
        self.assertEqual(schema['dateModified'], '2026-10-11')
        self.assertEqual(schema['datePublished'], '2026-10-10')
        self.assertEqual(schema['articleSection'], 'Economía')
        self.assertEqual(schema['image'], site.SITE + '/imagen.webp')
        self.assertEqual(soup.find('link', rel='canonical')['href'], site.SITE + '/nuevo-articulo/')
        self.assertEqual(soup.select_one('.published time')['datetime'], '2026-10-10')
        self.assertNotIn('piel-camaleonica', str(soup))

    def test_sidebar_has_working_anchors_and_static_search(self):
        site.update_article(self.entries[0], self.entries)
        soup = BeautifulSoup(self.article.read_text(encoding='utf-8'), 'html.parser')
        for a in soup.select('#secondary a[href^="#"]'):
            self.assertIsNotNone(soup.find(id=a['href'][1:]))
        self.assertEqual(soup.select_one('.entry-content a')['href'], '#primero')
        self.assertEqual(soup.select_one('#secondary form')['action'], '/blog/')
        self.assertIsNone(soup.select_one('#secondary a[href="/nuevo-articulo/"]'))

    def test_blog_is_crawlable_and_escapes_titles(self):
        site.build_blog(self.entries)
        soup = BeautifulSoup((self.base / 'blog/index.html').read_text(encoding='utf-8'), 'html.parser')
        self.assertEqual(soup.select_one('.ms-editorial-card h2').get_text(), 'Ciencia & <futuro>')
        self.assertIsNone(soup.find('futuro'))
        self.assertEqual(soup.select_one('.ms-editorial-card')['data-category'], 'economia')
        self.assertIsNone(soup.find('link', rel='next'))
        self.assertIsNone(soup.select_one('.ms-editorial-card').get('hidden'))

    def test_rebuild_is_idempotent(self):
        site.update_article(self.entries[0], self.entries)
        first = self.article.read_bytes()
        site.update_article(self.entries[0], self.entries)
        self.assertEqual(first, self.article.read_bytes())
        site.build_blog(self.entries)
        first = (self.base / 'blog/index.html').read_bytes()
        site.build_blog(self.entries)
        self.assertEqual(first, (self.base / 'blog/index.html').read_bytes())

    def test_error_export_is_recovered_from_existing_source(self):
        template = self.base / 'piel-camaleonica-camuflaje'
        template.mkdir()
        (template / 'index.html').write_bytes(self.article.read_bytes())
        self.article.write_text('<html><head><title>429 - Too Many Requests</title></head><body>Error</body></html>', encoding='utf-8')
        (self.base / 'articulos/nuevo-articulo.md').write_text('---\nslug: nuevo-articulo\ncategoria: economia\nmeta_description: Descripción original\n---\n## Evidencia\nTexto recuperado de la fuente existente.', encoding='utf-8')
        self.assertEqual(site.recover_error_pages(self.entries), 1)
        site.update_article(self.entries[0], self.entries)
        soup = BeautifulSoup(self.article.read_text(encoding='utf-8'), 'html.parser')
        self.assertIn('Texto recuperado', soup.select_one('.entry-content').get_text())
        self.assertNotIn('Too Many Requests', str(soup))
        self.assertEqual(json.loads(soup.find('script', type='application/ld+json').string)['headline'], self.entries[0]['title'])
        self.assertEqual(site.recover_error_pages(self.entries), 0)


if __name__ == '__main__':
    unittest.main()
