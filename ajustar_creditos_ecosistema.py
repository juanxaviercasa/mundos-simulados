"""Owner-authorized local edits; no network, Git commands, or publishing."""
import hashlib
import json
import re
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
AUTHOR = 'https://xavier.cabellosalirrosas.com'
OLD = re.compile(r'https?://(?:juan|xavier)\.(?:cabellorosas|cabellosalirosas|cabellosalirrosas)\.com', re.I)
RECORDS = []


def files(root):
    for folder, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in {'.git', 'node_modules', 'editorial', 'artifacts', 'backups_posts', '__pycache__', '.next', 'wp-content', 'wp-includes', 'assets', 'imagenes_generadas', '.vercel'}]
        for name in names:
            yield Path(folder) / name


def edit(path, transform):
    text = path.read_text(encoding='utf-8')
    updated = transform(text)
    backup = BASE / 'editorial/respaldo_ecosistema' / hashlib.sha256(str(path).encode()).hexdigest()
    if updated == text:
        if backup.exists():
            RECORDS.append({'path': str(path), 'backup': str(backup), 'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(), 'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        return
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_text(text, encoding='utf-8')
    path.write_text(updated, encoding='utf-8')
    RECORDS.append({'path': str(path), 'backup': str(backup), 'before_sha256': hashlib.sha256(text.encode()).hexdigest(), 'after_sha256': hashlib.sha256(updated.encode()).hexdigest()})


def main():
    nube = BASE.parent / 'nube_para_pymes'
    for root in (BASE, nube):
        print(f'Ajustando créditos: {root}', flush=True)
        for path in files(root):
            if path.suffix not in {'.html', '.py', '.js', '.md'} or any(part in {'.git', 'node_modules', 'editorial', 'artifacts', 'backups_posts', '__pycache__'} for part in path.parts):
                continue
            if path.name == Path(__file__).name:
                continue
            edit(path, lambda text: OLD.sub(AUTHOR, text))
    todo = Path('C:/Users/cabel/Pictures/Todo_Lima')
    print('Créditos de exportaciones terminados; ajustando fuentes de Todo Lima.', flush=True)
    for relative in ('components/Footer.js', 'lib/contact.js'):
        edit(todo / relative, lambda text: OLD.sub(AUTHOR, text))
    # Point at the current canonical tool URLs, rather than legacy .html stubs.
    categories = {
        'finanzas': ['calculadora-precios-venta-igv', 'calculadora-sobrecostos-laborales', 'calculadora-prestamos-amortizaciones', 'flujo-caja-pymes'],
        'ventas': ['generador-codigos-qr', 'creador-facturas-proforma', 'generador-cotizaciones', 'crm-pymes'],
        'operaciones': ['calculadora-flete-envio-local'],
        'legal': ['generador-contratos-servicios', 'generador-politicas-devolucion', 'generador-politicas-terminos'],
        'marketing': ['auditor-seo-basico', 'analizador-titulares'],
        'productividad': ['conversor-optimizador-imagenes', 'generador-paletas-corporativas'],
    }
    def tool_routes(text):
        for category, slugs in categories.items():
            for slug in slugs:
                text = text.replace(f'https://nubeparapymes.online/{slug}.html', f'https://nubeparapymes.online/herramientas/{category}/{slug}/?utm_source=todolima&utm_medium=referral&utm_campaign=ecosistema&utm_content=herramientas-{slug}')
        return text
    edit(todo / 'app/herramientas/page.js', tool_routes)
    # Remove unsubstantiated promises from the legacy banner and its build normalization.
    banner = nube / 'scripts/inject_todolima_synergy.py'
    def promises(text):
        return text.replace('Publica tu ficha comercial gratis y capta clientes directos en los 43 distritos de la capital.', 'Solicita la revisión de tu ficha y presenta ubicación, servicios y formas de contacto. La inclusión no garantiza consultas ni ventas.').replace('Publicar mi Negocio en Todo Lima →', 'Solicitar revisión de mi ficha →').replace('Directorio Comercial Oficial de Todo Lima', 'Directorio comercial de Todo Lima').replace('especialistas de salud verificados', 'opciones de atención publicadas')
    edit(banner, promises)
    integration = nube / 'scripts/integrate_ecosystem.py'
    def normalize_banner(text):
        old = "return match[0].replace('href=\"https://todolima.com\"'"
        new = "return match[0].replace('Publica tu ficha comercial gratis y capta clientes directos en los 43 distritos de la capital.', 'Solicita la revisión de tu ficha y presenta ubicación, servicios y formas de contacto. La inclusión no garantiza consultas ni ventas.').replace('Publicar mi Negocio en Todo Lima →', 'Solicitar revisión de mi ficha →').replace('href=\"https://todolima.com\"'"
        return text.replace(old, new)
    edit(integration, normalize_banner)
    for root in (nube / 'dist', nube / 'nubepymesexport'):
        for path in root.rglob('*.html'):
            edit(path, promises)
    (BASE / 'editorial/cambios_ecosistema_2026-10-11.json').write_text(json.dumps(RECORDS, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Archivos ajustados localmente: {len(RECORDS)}. Respaldos conservados. Sin publicación.')


if __name__ == '__main__':
    main()
