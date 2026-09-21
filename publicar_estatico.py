import os
import glob
import json
import frontmatter
import markdown as md
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import subprocess

POSTS_PER_RUN = 1
BORRADORES_DIR = "borradores"
EXPORT_DIR = "mundossimuladosexport"
TEMPLATE_HTML = os.path.join(EXPORT_DIR, "piel-camaleonica-camuflaje", "index.html")
SEARCH_INDEX = os.path.join(EXPORT_DIR, "search-index.json")

def publicar_posts():
    archivos_md = glob.glob(os.path.join(BORRADORES_DIR, "*.md"))
    archivos_a_procesar = archivos_md[:POSTS_PER_RUN]
    
    if not archivos_a_procesar:
        print("No hay borradores en la carpeta para publicar.")
        return
        
    if not os.path.exists(TEMPLATE_HTML):
        print(f"Error: No se encontr la plantilla base {TEMPLATE_HTML}")
        return

    with open(TEMPLATE_HTML, 'r', encoding='utf-8') as f:
        html_base = f.read()
        
    try:
        with open(SEARCH_INDEX, 'r', encoding='utf-8') as f:
            search_db = json.load(f)
    except Exception as e:
        print(f"Error cargando search-index.json: {e}")
        search_db = []

    exitosos = 0
    
    for filepath in archivos_a_procesar:
        print(f"\nProcesando {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        slug = post.get('slug')
        title = post.get('title')
        
        # RankMath SEO
        rm_title = post.get('rank_math_title', title)
        rm_desc = post.get('rank_math_description', '')
        
        cuerpo_html = md.markdown(post.content, extensions=["extra"])
        
        # Inyectar en HTML
        soup = BeautifulSoup(html_base, 'html.parser')
        
        # Reemplazar Ttulos
        if soup.title:
            soup.title.string = rm_title
        for og_title in soup.find_all('meta', property=['og:title', 'twitter:title']):
            og_title['content'] = rm_title
            
        # Reemplazar Descripcin
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag: desc_tag['content'] = rm_desc
        for og_desc in soup.find_all('meta', property=['og:description', 'twitter:description']):
            og_desc['content'] = rm_desc
            
        # Reemplazar URLs
        canonical = soup.find('link', rel='canonical')
        if canonical: canonical['href'] = f"../{slug}/"
        og_url = soup.find('meta', property='og:url')
        if og_url: og_url['content'] = f"../{slug}/"
            
        # Ttulo H1
        h1 = soup.find('h1', class_='entry-title')
        if h1: h1.string = title
            
        # Contenido
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            # Clear old content
            content_div.clear()
            # Parse new HTML and append
            new_content = BeautifulSoup(cuerpo_html, 'html.parser')
            content_div.append(new_content)
            
        # Guardar archivo esttico
        post_dir = os.path.join(EXPORT_DIR, slug)
        os.makedirs(post_dir, exist_ok=True)
        
        out_file = os.path.join(post_dir, "index.html")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print(f"Generado HTML en: {out_file}")
        
        # Actualizar search-index.json
        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y-%m-%d')
        
        # Obtener un snippet limpio (primeros 130 caracteres de texto)
        clean_text = BeautifulSoup(cuerpo_html, 'html.parser').get_text(separator=' ')
        snippet = clean_text[:130] + " [&hellip;]"
        
        new_entry = {
            "title": title,
            "slug": slug,
            "url": f"/{slug}/",
            "snippet": snippet,
            "date": date_str
        }
        search_db.insert(0, new_entry) # Agregar al principio
        
        # Eliminar borrador
        try:
            subprocess.run(["git", "rm", filepath], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            os.remove(filepath)
            
        exitosos += 1
            
    # Guardar index actualizado
    if exitosos > 0:
        with open(SEARCH_INDEX, 'w', encoding='utf-8') as f:
            json.dump(search_db, f, indent=2, ensure_ascii=False)
        print("search-index.json actualizado.")
        
    print(f"\n--- Resumen: {exitosos}/{len(archivos_a_procesar)} procesados con xito ---")

if __name__ == "__main__":
    publicar_posts()
