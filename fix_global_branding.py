import os
from bs4 import BeautifulSoup
import re

print("Iniciando fix global de branding...")

# 1. Extraer CSS de index.html
with open('index.html', 'r', encoding='utf-8') as f:
    soup_index = BeautifulSoup(f, 'html.parser')

dark_style = None
for style in soup_index.find_all('style'):
    if 'GLOBAL & ASTRA' in style.text:
        dark_style = style.text
        break

if not dark_style:
    print("ERROR: No se encontr el CSS de branding en index.html")
    exit(1)

# Crear directorio si no existe (aunque wp-content/themes/astra debera existir)
os.makedirs('wp-content/themes/astra', exist_ok=True)
css_path = 'wp-content/themes/astra/dark-branding.css'

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(dark_style)

print(f"1. CSS extrado y guardado en {css_path}")

# 2. Extraer Footer de index.html
footer = soup_index.find('footer', class_='ms-native-footer')
if not footer:
    print("ERROR: No se encontr el ms-native-footer en index.html")
    exit(1)

# El footer tiene rutas que empiezan con "./". Necesitamos que sean relativas.
# Lo convertiremos a string para manipularlo luego.
footer_html = str(footer)
print("2. Footer ms-native-footer extrado.")

# 3. Iterar por todos los archivos .html
count = 0
for root_dir, dirs, files in os.walk('.'):
    if '.git' in root_dir or 'wp-includes' in root_dir or 'wp-content' in root_dir:
        continue
        
    for file in files:
        if file.endswith('.html'):
            fpath = os.path.join(root_dir, file)
            # Ignorar el index.html de la raz porque ya tiene el diseo
            if fpath == '.\index.html' or fpath == './index.html':
                continue
                
            depth = len(os.path.relpath(root_dir, '.').split(os.sep)) if os.path.relpath(root_dir, '.') != '.' else 0
            prefix = "../" * depth if depth > 0 else "./"
            
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            orig_content = content
            
            # Limpiar posible stylesheet existente roto
            content = re.sub(r'<link rel="stylesheet" href="[^"]*dark-branding\.css" />', '', content)
            
            # Inyectar CSS
            css_link = f'<link rel="stylesheet" href="{prefix}wp-content/themes/astra/dark-branding.css" />'
            if '</head>' in content:
                content = content.replace('</head>', f'  {css_link}\n</head>')
                
            # Parsear con BS4 para reemplazar el footer ms fcil
            soup_page = BeautifulSoup(content, 'html.parser')
            
            # Borrar todos los footers viejos
            old_footers = soup_page.find_all('footer')
            for of in old_footers:
                of.decompose()
                
            # Tambin borrar .site-footer o #colophon
            for bad_f in soup_page.find_all(id='colophon'):
                bad_f.decompose()
                
            # Agregar nuestro nuevo footer
            new_footer = BeautifulSoup(footer_html, 'html.parser')
            # Arreglar las rutas en el footer (los ./ por el prefix)
            for a in new_footer.find_all('a'):
                if a.get('href') and a['href'].startswith('./'):
                    a['href'] = a['href'].replace('./', prefix)
                elif a.get('href') and a['href'] == '../':
                    # Fix special cases if footer has hardcoded ../
                    if depth == 0:
                        a['href'] = './'
                    else:
                        a['href'] = prefix
                        
            for img in new_footer.find_all('img'):
                if img.get('src') and img['src'].startswith('./'):
                    img['src'] = img['src'].replace('./', prefix)
                    
            # Insertar footer al final del body
            body = soup_page.find('body')
            if body:
                body.append(new_footer)
                
            # Guardar
            final_html = str(soup_page)
            if final_html != orig_content:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(final_html)
                count += 1

print(f"3. Archivos HTML actualizados con CSS global y footer: {count}")
