"""Normalize author credits and offer practical follow-ups to selected scenarios."""
from pathlib import Path
from urllib.parse import urlencode
from html import escape
import re

ROOT = Path(__file__).resolve().parent
AUTHOR_URL = 'https://xavier.cabellosalirrosas.com'
OLD_AUTHOR = re.compile(r'https?://(?:juan|xavier)\.(?:cabellorosas|cabellosalirosas|cabellosalirrosas)\.com', re.I)
BRIDGES = {
    'profesores-ia-cierre-escuelas': ('herramientas-profesores-particulares', 'Herramientas para organizar clases y academias'),
    'robots-con-derechos-laborales': ('automatizacion-ia-pymes-criterios-decision', 'Evaluar una automatización antes de implementarla'),
    'turismo-virtual-quiebra-aerolineas': ('herramientas', 'Probar herramientas gratuitas para organizar un negocio'),
}

def url(host, path, slug):
    return escape(f'https://{host}/{path}/?' + urlencode({'utm_source':'mundossimulados','utm_medium':'referral','utm_campaign':'ecosistema','utm_content':slug}), quote=True)

def integrate(root=ROOT):
    changed = 0
    for file in root.rglob('*.html'):
        if any(part in ('backups_posts', 'editorial', '.git') for part in file.relative_to(root).parts):
            continue
        text = file.read_text(encoding='utf-8')
        result = OLD_AUTHOR.sub(AUTHOR_URL, text)
        slug = file.parent.name
        if file.name == 'index.html' and slug in BRIDGES:
            result = re.sub(r'<!-- \[ECOSYSTEM_BRIDGE_START\] -->[\s\S]*?<!-- \[ECOSYSTEM_BRIDGE_END\] -->\s*', '', result)
            target, label = BRIDGES[slug]
            card = f'''<!-- [ECOSYSTEM_BRIDGE_START] -->
<aside class="ms-ecosystem-bridge" aria-label="Del escenario a una decisión actual" style="margin:2rem 0;padding:1.4rem;border:1px solid #475569;border-radius:12px;background:#0f172a;color:#f8fafc">
<h2 style="font-size:1.25rem">Del escenario a una decisión actual</h2>
<p>Este escenario es un ejercicio de reflexión. Si gestionas un negocio y quieres preparar una decisión concreta, Nube para Pymes ofrece guías y herramientas prácticas.</p>
<p><a style="color:#7dd3fc;text-decoration:underline" data-ecosystem-destination="nubeparapymes" href="{url('nubeparapymes.online', target, slug)}">{label} →</a></p>
<p>¿Tu negocio está en Lima y necesitas apoyo con su web, consultas o automatización?</p>
<a style="display:inline-block;padding:.65rem 1rem;border-radius:8px;background:#0369a1;color:white;text-decoration:none" data-ecosystem-destination="todolima" href="{url('todolima.com','auditoria',slug)}">Consultar una revisión digital en Todo Lima →</a>
</aside><!-- [ECOSYSTEM_BRIDGE_END] -->'''
            anchor = '</div><!-- .entry-content .clear -->' if '</div><!-- .entry-content .clear -->' in result else '</article>'
            if anchor not in result:
                raise ValueError(f'No article anchor: {file}')
            result = result.replace(anchor, card + '\n' + anchor, 1)
        if result != text:
            file.write_text(result,encoding='utf-8')
            changed += 1
    print(f'Ecosystem: updated author credits and selected article resources in {changed} pages.')

if __name__ == '__main__':
    integrate()
