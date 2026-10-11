"""Remove misleading or duplicated frontend elements in the local home page."""
import json
from editorial_site import BASE, fragment, write_html


def adjust():
    path = BASE / 'index.html'
    soup = fragment(path.read_text(encoding='utf-8'))
    footers = soup.select('footer.ms-native-footer')
    for footer in footers[:-1]:
        footer.decompose()
    count = len(json.loads((BASE / 'search-index.json').read_text(encoding='utf-8')))
    badge = soup.select_one('.ms-radar-badge')
    if badge:
        dot = badge.select_one('.ms-radar-dot')
        badge.clear()
        if dot:
            badge.append(dot)
        badge.append(f' EXPERIMENTOS MENTALES · {count} ESCENARIOS PUBLICADOS')
    hero = soup.select_one('.ms-hero-desc')
    if hero:
        hero.string = 'Experimentos mentales sobre ciencia, tecnología y sociedad. Exploramos qué cambiaría bajo distintos supuestos y qué límites tiene cada escenario.'
    for stat in soup.select('.ms-hud-stat'):
        if '100%' in stat.get_text() or 'Multiverso' in stat.get_text():
            stat.decompose()
    for text in soup.find_all(string=True):
        value = str(text)
        replacements = {
            'Seguimos un protocolo de análisis científico en 3 pasos para garantizar que cada simulación sea matemáticamente coherente.': 'Para leer los escenarios con contexto, conviene distinguir tres pasos.',
            '⚠️ SIMULACIÓN DE MÁXIMO RIESGO GLOBAL': 'TECNOLOGÍA Y SOCIEDAD',
            'Cronología minuciosa de un apagón de red mundial: la caída inmediata del sistema de pagos electrónicos, la interrupción del suministro de agua potable y el momento exacto en que la ley del orden se quiebra.': 'Un experimento mental sobre la dependencia de las redes de comunicación, las alternativas de continuidad y los límites de un escenario de interrupción global.',
            'HORA 0': 'PAGOS', 'DÍA 3': 'SERVICIOS', 'DÍA 7': 'LOGÍSTICA',
            'Caída de DNS y protocolos BGP mundiales': 'Dependencia de conexión y alternativas',
            'Agotamiento de combustible en generadores de soporte': 'Contingencias y recursos disponibles',
            'Parálisis absoluta de cadenas de suministro médico': 'Riesgos y límites del escenario',
        }
        for old, new in replacements.items():
            value = value.replace(old, new)
        if value != str(text):
            text.replace_with(value)
    newsletter = soup.select_one('.ms-newsletter-card')
    for old in soup.select('.ms-ecosystem-hub'):
        old.decompose()
    if newsletter:
        newsletter.find_parent('section').insert_before(fragment('''<section class="ms-section ms-ecosystem-hub"><div class="ms-container"><h2>Del escenario a una decisión práctica</h2><p>Recursos del mismo autor para necesidades diferentes.</p><div class="ms-ecosystem-cards"><article><h3>Nube para Pymes</h3><p>Herramientas gratuitas y guías para preparar cotizaciones, ordenar tareas y elegir software con contexto.</p><a href="https://nubeparapymes.online/herramientas/?utm_source=mundossimulados&amp;utm_medium=referral&amp;utm_campaign=ecosistema&amp;utm_content=portada">Explorar herramientas para mi negocio →</a></article><article><h3>Todo Lima</h3><p>Explora negocios y servicios locales y consulta directamente con cada proveedor. Si eres titular de un negocio, puedes solicitar la revisión de tu ficha.</p><a href="https://todolima.com/?utm_source=mundossimulados&amp;utm_medium=referral&amp;utm_campaign=ecosistema&amp;utm_content=portada">Buscar servicios en Lima →</a><p><a href="https://todolima.com/para-negocios?utm_source=mundossimulados&amp;utm_medium=referral&amp;utm_campaign=ecosistema&amp;utm_content=portada-negocios">Solicitar revisión de mi ficha →</a></p></article></div></div></section>'''))
        newsletter.clear()
        newsletter.append(fragment('<div><span class="ms-category-tag">CONTINÚA EXPLORANDO</span><h2 class="ms-section-title">Encuentra tu próxima lectura</h2><p>Consulta las publicaciones recientes y explora el catálogo por tema. La suscripción por correo todavía no está disponible.</p></div><div><a class="ms-btn-glow" href="/blog/">Leer las últimas entradas →</a></div>'))
    # Fix the visible typo without asserting that the mailbox has been verified.
    for link in soup.select('a[href^="mailto:"]'):
        if '.onine' in link['href']:
            link['href'] = link['href'].replace('.onine', '.online')
            link.string = link.get_text().replace('.onine', '.online')
    write_html(path, str(soup))
    print('Portada local: pie único, promesas revisadas y enlace útil en lugar de suscripción inactiva.')


if __name__ == '__main__':
    adjust()
