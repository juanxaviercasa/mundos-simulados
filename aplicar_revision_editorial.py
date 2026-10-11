"""Apply the reviewed manuscripts locally. Never commits, pushes or deploys."""
import hashlib
import json
import re
import shutil
from html import escape

import frontmatter
import markdown
from bs4 import BeautifulSoup
from editorial_site import BASE, sync_editorial

TITLES = {
    'semana-laboral-dos-dias': 'Semana laboral de dos días: productividad, ocio y límites del escenario',
    'salario-emocional-realidad-virtual': 'Salario en realidad virtual: límites económicos de una distopía',
    'redes-neuronales-planetarias': 'Redes neuronales planetarias: coordinación global y límites físicos',
    'virus-antiguos-permafrost': 'Virus del permafrost: qué demuestra la ciencia y qué sigue siendo hipotético',
    'semillas-extraterrestres-invasion': 'Semillas extraterrestres: los supuestos de una invasión hipotética',
    'silencio-movil-sin-smartphones': 'Un mundo sin smartphones: efectos posibles y límites de la evidencia',
    'universo-holografico-realidad-falsa': 'Universo holográfico: qué propone la teoría y qué no demuestra',
    'viento-solar-auroras-urbanas-letales': 'Auroras sobre ciudades: riesgos reales y límites del escenario',
    'ropa-inteligente-emociones': 'Ropa inteligente y emociones: qué miden los sensores y qué no',
    'vida-planeta-anclado-marea': 'Planeta anclado por marea: clima, atmósfera y habitabilidad',
    'salario-universal-obligatorio': 'Renta básica universal: financiación, precios y límites del modelo',
}


def apply():
    entries = json.loads((BASE / 'search-index.json').read_text(encoding='utf-8'))
    records = []
    for slug, title in TITLES.items():
        source = BASE / 'articulos' / (slug + '.md')
        page = BASE / slug / 'index.html'
        backup = BASE / 'editorial/originales_2026-10-11'
        for original, folder in ((source, 'articulos'), (page, 'html')):
            target = backup / folder / (slug + original.suffix)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(original, target)
        post = frontmatter.load(source)
        original_title = frontmatter.load(backup / 'articulos' / (slug + '.md')).get('title')
        body = (BASE / 'editorial/revisados' / (slug + '.md')).read_text(encoding='utf-8')
        sources = list(dict.fromkeys(re.findall(r'\]\((https?://[^\s)]+)\)', body)))
        if not sources:
            raise ValueError(f'Revisión sin fuentes: {slug}')
        rendered_source = BeautifulSoup(markdown.markdown(body), 'html.parser')
        plain = rendered_source.find('p').get_text(' ', strip=True)
        description = ' '.join(plain.split())[:155].rsplit(' ', 1)[0] + '…'
        post.metadata.update(title=title, meta_description=description, editorial_status='reviewed_draft',
                             editorial_review_date='2026-10-11', editorial_reviewed_by='Codex: revisión asistida por IA',
                             editorial_sources=sources)
        for key in ('alt_destacada', 'alt_interna_1', 'alt_interna_2'):
            alt = post.get(key, '')
            if not alt.startswith('Ilustración hipotética:'):
                post[key] = 'Ilustración hipotética: ' + alt
        post.content = body
        source.write_text(frontmatter.dumps(post) + '\n', encoding='utf-8')
        rendered = body
        for n in (1, 2):
            name = post.get(f'imagen_interna_{n}')
            tag = ''
            if name and (BASE / 'wp-content/uploads/2026/08' / name).exists():
                tag = f'<figure><img src="/wp-content/uploads/2026/08/{escape(name)}" alt="{escape(post.get(f"alt_interna_{n}", ""), quote=True)}" loading="lazy"/><figcaption>Ilustración del escenario hipotético; no es un registro científico.</figcaption></figure>'
            rendered = rendered.replace('{{IMAGEN_INTERNA_' + str(n) + '}}', tag)
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        content = soup.select_one('.entry-content')
        content.clear()
        content.append(BeautifulSoup(markdown.markdown(rendered, extensions=['extra']), 'html.parser'))
        note = soup.new_tag('p', attrs={'class': 'ms-editorial-review-note'})
        note.string = 'Revisión editorial asistida por IA, 11 de octubre de 2026. Se distinguen hipótesis y evidencia; esta revisión no equivale a una validación científica por especialistas.'
        content.insert(0, note)
        image = soup.select_one('.post-thumb img')
        if image:
            image['alt'] = post.get('alt_destacada', title)
        page.write_text(str(soup), encoding='utf-8')
        for entry in entries:
            if entry['slug'] == slug:
                entry.update(title=title, snippet=description)
        original_bytes = (backup / 'articulos' / (slug + '.md')).read_bytes()
        records.append({'slug': slug, 'original_title': original_title, 'reviewed_title': title,
                        'status': 'reviewed_draft', 'sources': sources,
                        'original_sha256': hashlib.sha256(original_bytes).hexdigest(),
                        'reviewed_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    (BASE / 'search-index.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    (BASE / 'editorial/revision_2026-10-11.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    sync_editorial()
    print(f'Revisiones locales aplicadas: {len(records)}. Ninguna publicada.')


if __name__ == '__main__':
    apply()
