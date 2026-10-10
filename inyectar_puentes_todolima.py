#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inyector de Enlazado Estratégico y Sinergia: Mundos Simulados -> Todo Lima (todolima.com)
Ancla los artículos de simulación científica, urbanismo, IA y crisis de recursos
a la realidad urbana, económica y comercial de Lima Metropolitana (Ate, Santa Clara, etc.).
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTICULOS_DIR = ROOT / "articulos"

# Mapeo estratégico de artículos con anclaje a la realidad limeña
BRIDGES_CONFIG = {
    # 1. TRANSPORTE, LOGÍSTICA & URBANISMO (Ate, Santa Clara, Lima Este)
    "gps-caido-caos-logistico": {
        "title": "Anclaje a la Realidad: Logística y Transporte en Lima Metropolitana",
        "desc": "En escenarios reales de contingencia en arterias de alto tránsito como la Carretera Central (Ate Vitarte, Santa Clara y Chosica), la continuidad de las cadenas de suministro depende de redes físicas de asistencia inmediata. Descubre a los operadores de auxilio y talleres mecánicos verificados en el <a href=\"https://todolima.com/auxilio-mecanico\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Auxilio Mecánico de Lima</a> y el mapa comercial de <a href=\"https://todolima.com/directorio?distrito=ate\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Ate en Todo Lima</a>.",
        "url": "https://todolima.com/auxilio-mecanico",
        "cta": "Explorar Directorio de Auxilio en Lima",
        "distrito": "Ate / Lima Este"
    },
    "apagon-global-internet-7-dias": {
        "title": "Anclaje a la Realidad: Servicios Físicos de Emergencia en Lima",
        "desc": "Si las redes de telecomunicaciones se interrumpen, la seguridad de inmuebles y la movilidad urbana exigen soporte técnico presencial de cerrajería de alta seguridad y auxilio vehicular. Conoce la red de <a href=\"https://todolima.com/cerrajeros\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Cerrajerías 24 Horas en Lima</a> y <a href=\"https://todolima.com/auxilio-mecanico\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Auxilio Mecánico en Lima</a>.",
        "url": "https://todolima.com/cerrajeros",
        "cta": "Ver Cerrajerías de Emergencia en Lima",
        "distrito": "Lima Metropolitana"
    },
    "ciudades-inteligentes-control": {
        "title": "Anclaje a la Realidad: Seguridad Perimetral y Monitoreo en Lima",
        "desc": "Frente a las simulaciones de vigilancia algorítmica total, en los distritos de Lima Metropolitana las comunidades y negocios protegen sus instalaciones mediante sistemas de circuito cerrado y videovigilancia local. Consulta las empresas certificadas en <a href=\"https://todolima.com/camaras-de-seguridad\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Cámaras de Seguridad en Lima</a>.",
        "url": "https://todolima.com/camaras-de-seguridad",
        "cta": "Ver Especialistas en Cámaras de Seguridad",
        "distrito": "Lima Metropolitana"
    },
    "arquitectura-dinamica-ciudades": {
        "title": "Anclaje a la Realidad: Desarrollo Inmobiliario y Acabados en Lima",
        "desc": "La evolución arquitectónica en distritos consolidados como Miraflores, San Isidro y Surco demanda soluciones avanzadas de ventanería acústica, muros cortina e intermediación profesional. Conoce los proyectos y asesores en el <a href=\"https://todolima.com/agentes-inmobiliarios\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Agentes Inmobiliarios de Lima</a> y <a href=\"https://todolima.com/vidrierias\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Vidrierías en Lima</a>.",
        "url": "https://todolima.com/agentes-inmobiliarios",
        "cta": "Consultar Agentes Inmobiliarios en Lima",
        "distrito": "Miraflores / San Isidro"
    },
    "ceguera-global-adaptacion-ciudades": {
        "title": "Anclaje a la Realidad: Salud Visual y Ópticas en Lima",
        "desc": "La salud ocular y prevención de afecciones visuales en la población limeña cuenta con una amplia red de consultorios oftalmológicos y laboratorios ópticos en los 43 distritos. Accede al <a href=\"https://todolima.com/opticas\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Ópticas en Lima</a> y <a href=\"https://todolima.com/oftalmologos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Oftalmólogos de Lima</a>.",
        "url": "https://todolima.com/opticas",
        "cta": "Ver Directorio de Ópticas en Lima",
        "distrito": "Lima Metropolitana"
    },

    # 2. LEGAL, JUSTICIA Y REGULACIÓN
    "jueces-ia-sistema-legal": {
        "title": "Anclaje a la Realidad: Asesoría Jurídica y Notarial en Lima",
        "desc": "En contraposición a las decisiones algorítmicas, la defensa jurídica corporativa y la fe pública en el Perú requieren profesionales colegiados con criterio ético humano. Revisa los estudios legales calificados en el <a href=\"https://todolima.com/abogados\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Abogados de Lima</a> y <a href=\"https://todolima.com/notarias\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Notarías de Lima</a>.",
        "url": "https://todolima.com/abogados",
        "cta": "Consultar Abogados Colegiados en Lima",
        "distrito": "Lima Metropolitana"
    },
    "deepfakes-evidencia-legal": {
        "title": "Anclaje a la Realidad: Peritaje Legal y Ciberdelincuencia en Perú",
        "desc": "El derecho penal informático y la validación de pruebas documentales en Lima se apoyan en juristas y peritos forenses especializados. Conoce a los profesionales habilitados en el <a href=\"https://todolima.com/abogados\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio Legal de Todo Lima</a>.",
        "url": "https://todolima.com/abogados",
        "cta": "Explorar Directorio Legal de Lima",
        "distrito": "Lima Metropolitana"
    },
    "multas-segun-ingresos": {
        "title": "Anclaje a la Realidad: Asesoría Contable y Tributaria en Lima",
        "desc": "El cumplimiento de obligaciones tributarias ante SUNAT y la gestión contable de personas y empresas en Lima Metropolitana exige respaldo técnico continuo. Encuentra asesores en el <a href=\"https://todolima.com/contadores\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Contadores de Lima</a>.",
        "url": "https://todolima.com/contadores",
        "cta": "Ver Contadores Colegiados en Lima",
        "distrito": "Lima Metropolitana"
    },
    "fin-patentes-investigacion-medica": {
        "title": "Anclaje a la Realidad: Registro de Marcas y Propiedad Intelectual en Perú",
        "desc": "Para proteger invenciones y signos distintivos comerciales ante Indecopi en la capital, se requiere patrocinio legal en propiedad industrial. Revisa los estudios destacados en el <a href=\"https://todolima.com/abogados\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Abogados de Lima</a>.",
        "url": "https://todolima.com/abogados",
        "cta": "Ver Abogados Especialistas en Marcas",
        "distrito": "Lima Metropolitana"
    },
    "carceles-virtuales-cadenas-perpetuas": {
        "title": "Anclaje a la Realidad: Sistema Penitenciario y Derecho Penal en Lima",
        "desc": "La tutela de garantías constitucionales y representación penal en el fuero judicial de Lima y Callao se gestiona mediante abogados litigantes especializados. Consulta el <a href=\"https://todolima.com/abogados\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio Legal de Todo Lima</a>.",
        "url": "https://todolima.com/abogados",
        "cta": "Ver Abogados Penalistas en Lima",
        "distrito": "Lima Metropolitana"
    },

    # 3. SALUD, MEDICINA Y PSICOLOGÍA
    "atencion-medica-privada-latido": {
        "title": "Anclaje a la Realidad: Consultorios y Red de Salud Privada en Lima",
        "desc": "Frente a escenarios de atención médica robotizada, el diagnóstico temprano, la consulta médica de cabecera y los análisis clínicos de confianza siguen siendo fundamentales para las familias limeñas. Encuentra clínicas y consultorios en el <a href=\"https://todolima.com/doctores\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Doctores de Lima</a> y <a href=\"https://todolima.com/laboratorios-clinicos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Laboratorios Clínicos en Lima</a>.",
        "url": "https://todolima.com/doctores",
        "cta": "Ver Consultorios Médicos en Lima",
        "distrito": "Lima Metropolitana"
    },
    "medicion-estres-impuestos": {
        "title": "Anclaje a la Realidad: Salud Mental y Terapia Clínica en Lima",
        "desc": "La gestión de la ansiedad, el estrés laboral y el bienestar psicológico en la metrópoli limeña cuenta con terapeutas y centros de salud mental calificados en cada distrito. Accede al <a href=\"https://todolima.com/psicologos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Psicólogos de Lima</a>.",
        "url": "https://todolima.com/psicologos",
        "cta": "Buscar Psicólogos Calificados en Lima",
        "distrito": "Lima Metropolitana"
    },
    "inmunidad-absoluta-fin-enfermedades": {
        "title": "Anclaje a la Realidad: Pediatría y Control del Desarrollo en Lima",
        "desc": "El esquema de inmunización infantil y la atención preventiva de niños y recién nacidos en distritos limeños es liderado por médicos colegiados. Consulta el <a href=\"https://todolima.com/pediatras\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Pediatras de Lima</a>.",
        "url": "https://todolima.com/pediatras",
        "cta": "Ver Pediatras en Lima Metropolitana",
        "distrito": "Lima Metropolitana"
    },
    "bebes-diseno-genetico-clases": {
        "title": "Anclaje a la Realidad: Ginecología y Salud Reproductiva en Lima",
        "desc": "La atención obstétrica, control prenatal y salud integral femenina en la capital cuenta con centros médicos ginecológicos de primer nivel. Conoce a los especialistas en el <a href=\"https://todolima.com/ginecologos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Ginecólogos de Lima</a>.",
        "url": "https://todolima.com/ginecologos",
        "cta": "Ver Ginecólogos en Lima",
        "distrito": "Lima Metropolitana"
    },
    "borrado-social-psicologia-global": {
        "title": "Anclaje a la Realidad: Terapia Psicológica y Vínculos en Lima",
        "desc": "El impacto emocional del aislamiento y las dinámicas sociales urbanas requiere acompañamiento profesional personalizado en consultorios de la capital. Revisa el <a href=\"https://todolima.com/psicologos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Psicólogos de Lima</a>.",
        "url": "https://todolima.com/psicologos",
        "cta": "Buscar Terapeutas en Lima",
        "distrito": "Lima Metropolitana"
    },

    # 4. ECONOMÍA, COMERCIO LOCAL Y FINANZAS
    "desaparicion-comercio-minorista": {
        "title": "Anclaje a la Realidad: El Tejido Comercial Pyme en Lima",
        "desc": "Lejos de la extinción del comercio local, en Lima Metropolitana operan cientos de miles de tiendas de cercanía, bodegas y comercios de barrio que impulsan la economía de distritos populares y residenciales. Conoce la red comercial en el <a href=\"https://todolima.com\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio Oficial Todo Lima</a>.",
        "url": "https://todolima.com",
        "cta": "Explorar Comercios Locales de Lima",
        "distrito": "Lima Metropolitana"
    },
    "monopolio-corporativo-unico-omnicorp": {
        "title": "Anclaje a la Realidad: Emprendimientos Independientes en los 43 Distritos",
        "desc": "Frente a las megacorporaciones distópicas, la fortaleza económica de Lima radica en la diversidad de sus 56 rubros comerciales independientes, desde ferreterías hasta gastronomía. Revisa el catálogo oficial en <a href=\"https://todolima.com\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">todolima.com</a>.",
        "url": "https://todolima.com",
        "cta": "Ver Directorio de Pymes Limeñas",
        "distrito": "Lima Metropolitana"
    },
    "cero-impuestos-pais-privado": {
        "title": "Anclaje a la Realidad: Asesoría Tributaria y Contabilidad en Lima",
        "desc": "En el marco fiscal peruano, la correcta tributación y optimización de costos para pymes y personas con negocio requiere contadores colegiados con experiencia en normativa SUNAT. Conoce especialistas en el <a href=\"https://todolima.com/contadores\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Contadores de Lima</a>.",
        "url": "https://todolima.com/contadores",
        "cta": "Ver Contadores Tributarios en Lima",
        "distrito": "Lima Metropolitana"
    },
    "colapso-financiero-virus-digital": {
        "title": "Anclaje a la Realidad: Casas de Cambio y Mercado de Divisas en Lima",
        "desc": "Ante la volatilidad de los mercados cambiarios, los centros financieros de San Isidro, Miraflores y Cercado de Lima concentran casas de cambio y operadores formales registrados ante la SBS. Consulta las opciones en el <a href=\"https://todolima.com/casas-de-cambio\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Casas de Cambio de Lima</a>.",
        "url": "https://todolima.com/casas-de-cambio",
        "cta": "Ver Casas de Cambio en Lima",
        "distrito": "San Isidro / Miraflores"
    },
    "moneda-global-unica-soberania": {
        "title": "Anclaje a la Realidad: Operaciones Cambiarias Seguras en Lima",
        "desc": "La compra y venta de dólares y euros en los distritos financieros de Lima demanda agentes autorizados para garantizar operaciones transparentes. Accede al <a href=\"https://todolima.com/casas-de-cambio\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Casas de Cambio de Lima</a>.",
        "url": "https://todolima.com/casas-de-cambio",
        "cta": "Consultar Casas de Cambio en Lima",
        "distrito": "Lima Metropolitana"
    },
    "mineria-asteroides-desplome-economia": {
        "title": "Anclaje a la Realidad: Talleres Metalmecánicos y Repuestos en Lima",
        "desc": "En la actividad industrial real de Lima Este y Lima Norte, el maquinado de piezas, tornería y mantenimiento automotriz es sostenido por talleres especializados. Conoce los mejores talleres en el <a href=\"https://todolima.com/talleres-mecanicos\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Talleres Mecánicos de Lima</a>.",
        "url": "https://todolima.com/talleres-mecanicos",
        "cta": "Ver Talleres Mecánicos en Lima",
        "distrito": "Lima Metropolitana"
    },

    # 5. AGUA, HOGAR Y MASCOTAS (Lima como ciudad en el desierto)
    "burbuja-agua-dulce-bolsa": {
        "title": "Anclaje a la Realidad: Redes Hídricas y Gasfitería en Lima Desértica",
        "desc": "Lima es la segunda ciudad desértica más habitada del planeta. La presión hídrica, el bombeo desde pozos y el mantenimiento de cisternas y redes sanitarias en distritos como Ate, Surco o San Martín de Porres es vital. Encuentra técnicos calificados en el <a href=\"https://todolima.com/gasfiteros\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Gasfiteros de Lima</a>.",
        "url": "https://todolima.com/gasfiteros",
        "cta": "Ver Gasfiteros Calificados en Lima",
        "distrito": "Lima Metropolitana"
    },
    "oceanos-agua-dulce-extincion": {
        "title": "Anclaje a la Realidad: Mantenimiento Sanitario e Hidráulico en Lima",
        "desc": "La gestión del agua potable y la detección de fugas en edificaciones y residencias de Lima Metropolitana requiere gasfitería especializada con equipos de detección electrónica. Accede al <a href=\"https://todolima.com/gasfiteros\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Gasfiteros en Lima</a>.",
        "url": "https://todolima.com/gasfiteros",
        "cta": "Consultar Gasfiteros en Lima",
        "distrito": "Lima Metropolitana"
    },
    "mascotas-roboticas-reemplazo": {
        "title": "Anclaje a la Realidad: Clínicas Veterinarias y Cuidado Animal en Lima",
        "desc": "Frente a las simulaciones robóticas, el bienestar de perros y gatos en los hogares de Lima demanda médicos veterinarios colegiados, vacunación y estética profesional. Encuentra centros de confianza en el <a href=\"https://todolima.com/veterinarias\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Veterinarias de Lima</a> y <a href=\"https://todolima.com/grooming-canino\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Grooming Canino en Lima</a>.",
        "url": "https://todolima.com/veterinarias",
        "cta": "Buscar Veterinarias en Lima",
        "distrito": "Lima Metropolitana"
    },
    "agricultura-robotica-fin-hambruna": {
        "title": "Anclaje a la Realidad: Control de Plagas y Fumigación en Lima",
        "desc": "El saneamiento ambiental de almacenes de alimentos, restaurantes y locales comerciales en distritos industriales de Lima Metropolitana se certifica mediante empresas autorizadas por el MINSA. Consulta el <a href=\"https://todolima.com/fumigacion\" target=\"_blank\" rel=\"noopener\" style=\"color: #00F0FF; font-weight: 700; text-decoration: underline;\">Directorio de Fumigación en Lima</a>.",
        "url": "https://todolima.com/fumigacion",
        "cta": "Ver Empresas de Fumigación en Lima",
        "distrito": "Lima Metropolitana"
    }
}

def generate_cyber_bridge_html(bridge_data):
    return f"""<!-- [MS_TODOLIMA_BRIDGE_START] -->
<div class="ms-todolima-bridge" style="margin: 2.5em 0; padding: 1.5em 1.8em; background: rgba(13, 20, 36, 0.95); border: 1.5px solid rgba(0, 240, 255, 0.35); border-left: 5px solid #00F0FF; border-radius: 16px; color: #F8FAFC; font-family: inherit; box-shadow: 0 10px 30px rgba(0, 240, 255, 0.08);">
  <div style="display: flex; align-items: flex-start; gap: 14px;">
    <div style="font-size: 26px; line-height: 1; flex-shrink: 0; margin-top: 2px;">🏙️</div>
    <div>
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
        <h4 style="margin: 0; color: #00F0FF; font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em;">{bridge_data['title']}</h4>
        <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 9999px; background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); color: #38BDF8;">{bridge_data['distrito']}</span>
      </div>
      <p style="margin: 0 0 12px 0; color: #CBD5E1; font-size: 0.92rem; line-height: 1.6;">
        {bridge_data['desc']}
      </p>
      <a href="{bridge_data['url']}" target="_blank" rel="noopener" style="display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; background: rgba(0, 240, 255, 0.15); border: 1px solid #00F0FF; color: #00F0FF; font-weight: 700; font-size: 0.82rem; border-radius: 8px; text-decoration: none; transition: all 0.2s;">
        <span>{bridge_data['cta']}</span> →
      </a>
    </div>
  </div>
</div>
<!-- [MS_TODOLIMA_BRIDGE_END] -->
"""

def generate_markdown_bridge(bridge_data):
    # Genera bloque limpio para el archivo markdown
    clean_desc = re.sub(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)', bridge_data['desc'])
    return f"""

<!-- [MS_TODOLIMA_BRIDGE_START] -->
> **🏙️ {bridge_data['title']} ({bridge_data['distrito']}):**
> {clean_desc}  
> [👉 {bridge_data['cta']}]({bridge_data['url']})
<!-- [MS_TODOLIMA_BRIDGE_END] -->
"""

def inject_in_markdown():
    print("[MUNDOS SIMULADOS] Inyectando puentes en archivos markdown (articulos/)...")
    count = 0
    for slug, bridge_data in BRIDGES_CONFIG.items():
        md_file = ARTICULOS_DIR / f"{slug}.md"
        if not md_file.exists():
            continue

        text = md_file.read_text(encoding="utf-8")
        if "[MS_TODOLIMA_BRIDGE_START]" in text:
            text = re.sub(r'\n*<!-- \[MS_TODOLIMA_BRIDGE_START\] -->.*?<!-- \[MS_TODOLIMA_BRIDGE_END\] -->\n*', '', text, flags=re.DOTALL)

        text += generate_markdown_bridge(bridge_data)
        md_file.write_text(text, encoding="utf-8")
        count += 1
        print(f"  [OK] Markdown actualizado: {slug}.md")

    print(f"[MUNDOS SIMULADOS] Total markdown actualizados: {count}")

def inject_in_html_posts():
    print("[MUNDOS SIMULADOS] Inyectando puentes en HTMLs existentes...")
    count = 0
    for slug, bridge_data in BRIDGES_CONFIG.items():
        html_file = ROOT / slug / "index.html"
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding="utf-8")
        # Saltar si es página de error de rate limit
        if "Too Many Requests" in content:
            continue

        if "[MS_TODOLIMA_BRIDGE_START]" in content:
            content = re.sub(r'<!-- \[MS_TODOLIMA_BRIDGE_START\] -->.*?<!-- \[MS_TODOLIMA_BRIDGE_END\] -->\n?', '', content, flags=re.DOTALL)

        bridge_html = generate_cyber_bridge_html(bridge_data)

        # Anclar antes de ms-external-box o antes de cierre de .entry-content
        if '<p class="ms-external-box"' in content:
            content = content.replace('<p class="ms-external-box"', f'{bridge_html}\n<p class="ms-external-box"')
            html_file.write_text(content, encoding="utf-8")
            count += 1
            print(f"  [OK] HTML actualizado (antes de ms-external-box): {slug}")
        elif "</div><!-- .entry-content .clear -->" in content:
            content = content.replace("</div><!-- .entry-content .clear -->", f"{bridge_html}\n</div><!-- .entry-content .clear -->")
            html_file.write_text(content, encoding="utf-8")
            count += 1
            print(f"  [OK] HTML actualizado (en .entry-content): {slug}")
        elif "</article>" in content:
            content = content.replace("</article>", f"{bridge_html}\n</article>")
            html_file.write_text(content, encoding="utf-8")
            count += 1
            print(f"  [OK] HTML actualizado (antes de </article>): {slug}")

    print(f"[MUNDOS SIMULADOS] Total HTMLs actualizados: {count}")

def update_global_footer():
    print("[MUNDOS SIMULADOS] Actualizando pie de página global en index.html...")
    index_file = ROOT / "index.html"
    if not index_file.exists():
        return

    content = index_file.read_text(encoding="utf-8")
    
    # Agregar enlace de Todo Lima en nav si no existe
    if 'href="https://todolima.com"' not in content:
        target_link = '<a href="./terminos-y-condiciones/" style="color: #E2E8F0; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s;">Términos y Condiciones</a>'
        if target_link in content:
            replacement = (
                target_link + '\n'
                '      <span style="color: rgba(0,240,255,0.4); user-select: none;">·</span>\n'
                '      <a href="https://todolima.com" target="_blank" rel="noopener" style="color: #00F0FF; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: color 0.2s;">Directorio Todo Lima</a>\n'
                '      <span style="color: rgba(0,240,255,0.4); user-select: none;">·</span>\n'
                '      <a href="https://nubeparapymes.online" target="_blank" rel="noopener" style="color: #38BDF8; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: color 0.2s;">Nube para Pymes</a>'
            )
            content = content.replace(target_link, replacement)
            index_file.write_text(content, encoding="utf-8")
            print("  [OK] Enlaces aliados agregados al footer de index.html")
        else:
            print("  [INFO] No se encontró anclaje exacto en footer de index.html")
    else:
        print("  [INFO] Enlaces aliados ya presentes en index.html")

if __name__ == "__main__":
    inject_in_markdown()
    inject_in_html_posts()
    update_global_footer()
    print("[MUNDOS SIMULADOS] Inyección de sinergia completada.")
