import unittest
from corregir_lectura import normalize_reading


class ReadingExportTests(unittest.TestCase):
    def test_contact_navigation_is_added_once_to_both_menus(self):
        item = '<li class="menu-item"><a class="menu-link" href="../sobre-mi/">Sobre mí</a></li>'
        source = '<ul id="ast-hf-menu-1">' + item + '</ul><ul id="ast-hf-mobile-menu">' + item + '</ul>'
        result = normalize_reading(source)
        self.assertEqual(result.count('ms-contact-nav'), 2)
        self.assertEqual(result, normalize_reading(result))

    def test_translation_and_featured_image_are_idempotent(self):
        source = '<body class="single-post"><p class="ez-toc-title" style="cursor:inherit">Table of Contents</p><img class="wp-post-image" loading="lazy" src="moon.webp"/><img src="body.webp"/></body>'
        result = normalize_reading(source)
        self.assertIn('Tabla de contenidos', result)
        self.assertIn('loading="eager"', result)
        self.assertIn('fetchpriority="high"', result)
        self.assertIn('<img src="body.webp"/>', result)
        self.assertEqual(result, normalize_reading(result))

    def test_unrelated_asset_and_content_are_preserved(self):
        source = '<a href="/contacto/">Formulario de contacto</a><link href="/wp-static-arquitect-assets/theme.css?v=20261011-3"><script src="other.js?v=20261011-3"></script>'
        result = normalize_reading(source)
        self.assertIn('theme.css?v=20261011-7', result)
        self.assertIn('other.js?v=20261011-3', result)
        self.assertIn('Formulario de contacto', result)


if __name__ == '__main__':
    unittest.main()
