import subprocess
import unittest
from unittest.mock import patch
import exportar_sitio_estatico as exporter


class DownloadValidationTests(unittest.TestCase):
    def test_http_errors_are_rejected(self):
        with patch.object(exporter.subprocess, 'run', return_value=subprocess.CompletedProcess([], 22, b'error')) as run:
            self.assertIsNone(exporter.run_curl('https://example.invalid/article/'))
            self.assertIn('--fail', run.call_args.args[0])

    def test_error_document_with_success_status_is_rejected(self):
        for status in (429, 502, 503, 504):
            response = subprocess.CompletedProcess([], 0, f'<html><title>{status} — Error</title></html>'.encode())
            with patch.object(exporter.subprocess, 'run', return_value=response):
                self.assertIsNone(exporter.run_curl('https://example.invalid/article/'))

    def test_valid_article_is_preserved(self):
        body = b'<html><title>Escenario</title><article>Texto original</article></html>'
        with patch.object(exporter.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, body)):
            self.assertEqual(exporter.run_curl('https://example.invalid/article/'), body.decode())


if __name__ == '__main__':
    unittest.main()
