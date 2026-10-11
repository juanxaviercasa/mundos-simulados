"""Read-only local inventory of outbound ecosystem links and bridge coverage."""
import json
import re
import os
from html import unescape
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
ROOTS = {'mundos': BASE, 'nube_export': BASE.parent / 'nube_para_pymes/nubepymesexport',
         'nube_dist': BASE.parent / 'nube_para_pymes/dist',
         'todo_out': Path('C:/Users/cabel/Pictures/Todo_Lima/out')}
HOSTS = {'todolima.com', 'nubeparapymes.online', 'mundossimulados.online', 'mundosimulados.online'}


def inventory():
    report = {}
    for name, root in ROOTS.items():
        print(f'Inventario: {name}', flush=True)
        rows, domains, paths = [], Counter(), Counter()
        external = HOSTS - ({'mundossimulados.online', 'mundosimulados.online'} if name == 'mundos' else {'todolima.com'} if name == 'todo_out' else {'nubeparapymes.online'})
        candidates = []
        for folder, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', 'editorial', 'wp-content', 'wp-includes', 'assets', '_next'}]
            candidates.extend(Path(folder) / filename for filename in names if filename.endswith('.html'))
        for file in candidates:
            relative = file.relative_to(root).as_posix()
            if any(part in {'editorial', '.git', 'node_modules', '.editorial-test-'} for part in file.parts):
                continue
            raw = file.read_text(encoding='utf-8')
            if not any(host in raw for host in external):
                continue
            for match in re.finditer(r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>(.*?)</a>', raw, re.I | re.S):
                url = unescape(match[1])
                host = urlsplit(url).hostname
                if host in external:
                    domains[host] += 1
                    paths[url] += 1
                    label = re.sub(r'<[^>]+>', ' ', match[2])
                    rows.append({'page': relative, 'url': url, 'text': ' '.join(unescape(label).split())})
        report[name] = {'domains': dict(domains), 'destinations': dict(paths), 'links': rows}
    destination = BASE / 'editorial/ecosistema_inventario_2026-10-11.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, result in report.items():
        print(name, result['domains'], 'pages:', len({row['page'] for row in result['links']}))
    return report


if __name__ == '__main__':
    inventory()
