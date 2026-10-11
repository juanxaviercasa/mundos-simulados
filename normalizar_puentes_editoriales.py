"""Keep existing Markdown referrals consistent with the reviewed public blocks."""
import re
from editorial_site import BASE
from inyectar_puentes_todolima import BRIDGES_CONFIG, generate_markdown_bridge


def normalize():
    count = 0
    for slug, config in BRIDGES_CONFIG.items():
        path = BASE / 'articulos' / (slug + '.md')
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        value = re.sub(r'<!-- \[MS_TODOLIMA_BRIDGE_START\] -->.*?<!-- \[MS_TODOLIMA_BRIDGE_END\] -->', lambda _: generate_markdown_bridge(config).strip(), text, flags=re.S)
        if value != text:
            path.write_text(value, encoding='utf-8')
            count += 1
    print(f'Puentes Markdown normalizados: {count}')


if __name__ == '__main__':
    normalize()
