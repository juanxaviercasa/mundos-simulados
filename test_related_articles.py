import unittest
from related_articles import build_related


class RelatedArticlesTests(unittest.TestCase):
    def test_curated_choices_are_valid_unique_and_not_self(self):
        entries = [{'slug': s, 'title': s.replace('-', ' ')} for s in ['semana-laboral-dos-dias', 'desempleo-global-automatizacion', 'salario-universal-obligatorio']]
        result = build_related(entries, {e['slug']: 'economia' for e in entries})
        self.assertEqual(result['semana-laboral-dos-dias'], ['desempleo-global-automatizacion', 'salario-universal-obligatorio'])
        for slug, targets in result.items():
            self.assertNotIn(slug, targets)
            self.assertEqual(len(targets), len(set(targets)))
            self.assertTrue(set(targets) <= {e['slug'] for e in entries})

    def test_fallback_requires_shared_topic_and_category(self):
        entries = [{'slug': 'red-solar', 'title': 'Tormenta solar'}, {'slug': 'viento-solar', 'title': 'Viento solar'}, {'slug': 'otro', 'title': 'Salarios y comercio'}, {'slug': 'energia-solar', 'title': 'Energía solar'}]
        result = build_related(entries, {'red-solar': 'astrofisica', 'viento-solar': 'astrofisica', 'otro': 'astrofisica', 'energia-solar': 'economia'})
        self.assertEqual(result['red-solar'], ['viento-solar'])
        self.assertEqual(result['otro'], [])


if __name__ == '__main__':
    unittest.main()
