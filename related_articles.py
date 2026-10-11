"""Deterministic thematic recommendations; curated overrides take precedence."""
import math
import re
import unicodedata
from collections import Counter

CURATED = {
    'semana-laboral-dos-dias': ['desempleo-global-automatizacion', 'salario-universal-obligatorio', 'sin-jubilacion-trabajo-eterno'],
    'salario-emocional-realidad-virtual': ['realidad-virtual-indistinguible', 'turismo-virtual-quiebra-aerolineas', 'salario-universal-obligatorio'],
    'redes-neuronales-planetarias': ['internet-cuantico-encriptacion', 'boton-de-apagado-ia-global', 'apagon-global-internet-7-dias'],
    'virus-antiguos-permafrost': ['hielo-derretido-nuevo-mapa', 'retorno-megafauna-mamuts', 'resistencia-radiacion-nuclear'],
    'semillas-extraterrestres-invasion': ['paradoja-de-fermi-silencio-espacial', 'el-ultimo-arbol-original-protegido', 'flora-bioluminiscente-ciudades-arboles'],
    'silencio-movil-sin-smartphones': ['apagon-global-internet-7-dias', 'ceguera-digital-pantallas-oculares', 'interfaces-hapticas-dolor-internet'],
    'universo-holografico-realidad-falsa': ['error-matrix-pruebas-simulacion', 'materia-espejo-universo-paralelo', 'tiempo-y-espacio-relativo-gps'],
    'viento-solar-auroras-urbanas-letales': ['tormenta-solar-fin-tecnologia', 'inversion-polos-magneticos-tierra', 'anomalia-magnetica-del-atlantico-espacio'],
    'ropa-inteligente-emociones': ['medicion-estres-impuestos', 'telepatia-sintetica-fin-mentira', 'dispositivos-invisibilidad-seguridad'],
    'vida-planeta-anclado-marea': ['tierra-orbita-enana-roja', 'sol-doble-sistema-binario-tierra', 'planeta-errante-cruza-sistema'],
    'salario-universal-obligatorio': ['semana-laboral-dos-dias', 'desempleo-global-automatizacion', 'un-millon-al-nacer-hiperinflacion'],
    'apagon-global-internet-7-dias': ['gps-caido-caos-logistico', 'ciberataque-red-electrica-europea', 'tormenta-solar-fin-tecnologia'],
}
STOP = set('que pasaria si la el los las un una unos unas de del en al y o a con sin por para se su sus mundo mundos simulados humanidad impacto global tierra fin consecuencias escenario escenarios hipotetico hipotetica como es no mas'.split())


def terms(entry):
    value = entry['title'] + ' ' + entry['slug'].replace('-', ' ')
    value = ''.join(c for c in unicodedata.normalize('NFD', value.lower()) if unicodedata.category(c) != 'Mn')
    return {word for word in re.findall(r'[a-z]+', value) if len(word) > 3 and word not in STOP}


def build_related(entries, categories):
    """Use title overlap within a category; otherwise link its hub, not random posts."""
    index = {e['slug']: e for e in entries}
    tokens = {slug: terms(entry) for slug, entry in index.items()}
    frequency = Counter(word for words in tokens.values() for word in words)
    result = {}
    for slug in index:
        selected = [target for target in CURATED.get(slug, []) if target in index and target != slug]
        category = categories.get(slug)
        candidates = []
        for target in index:
            if target == slug or target in selected or not category or categories.get(target) != category:
                continue
            shared = tokens[slug] & tokens[target]
            if not shared:
                continue
            score = sum(math.log(1 + len(index) / frequency[word]) for word in shared)
            candidates.append((score, target))
        candidates.sort(key=lambda pair: (-pair[0], pair[1]))
        result[slug] = (selected + [target for _, target in candidates])[:3]
    return result
