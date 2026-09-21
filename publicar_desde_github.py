import os
import glob
import requests
import frontmatter
import markdown as md
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import subprocess

load_dotenv()

WP_URL = os.environ.get("WP_URL_TARGET") or "https://dev-simulandomundos.pantheonsite.io"
WP_USER = os.environ.get("WP_USER")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")

POSTS_PER_RUN = 1
BORRADORES_DIR = "borradores"

def publicar_posts():
    if not WP_USER or not WP_APP_PASSWORD:
        print("Error: Credenciales WP_USER o WP_APP_PASSWORD no configuradas en el entorno.")
        return

    auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)
    archivos_md = glob.glob(os.path.join(BORRADORES_DIR, "*.md"))
    archivos_a_procesar = archivos_md[:POSTS_PER_RUN]
    
    if not archivos_a_procesar:
        print("No hay borradores en la carpeta para publicar.")
        return
        
    exitosos = 0
    
    for filepath in archivos_a_procesar:
        print(f"\nProcesando {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        cuerpo_html = md.markdown(post.content, extensions=["extra"])
        
        payload = {
            "title": post.get('title'),
            "slug": post.get('slug'),
            "status": "publish",
            "content": cuerpo_html
        }
        
        if post.get('categories'): payload["categories"] = post['categories']
        if post.get('tags'): payload["tags"] = post['tags']
        
        meta = {}
        if post.get('rank_math_title'): meta['rank_math_title'] = post['rank_math_title']
        if post.get('rank_math_description'): meta['rank_math_description'] = post['rank_math_description']
        if post.get('rank_math_focus_keyword'): meta['rank_math_focus_keyword'] = post['rank_math_focus_keyword']
        if meta: payload['meta'] = meta
        
        # If the post has a wp_id, we can UPDATE it, otherwise CREATE it.
        wp_id = post.get('wp_id')
        try:
            if wp_id:
                endpoint = f"{WP_URL}/wp-json/wp/v2/posts/{wp_id}"
                resp = requests.post(endpoint, json=payload, auth=auth, timeout=30)
            else:
                endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
                resp = requests.post(endpoint, json=payload, auth=auth, timeout=30)
                
            if resp.status_code in [200, 201]:
                print(f"✅ Publicado con éxito: {post.get('title')} (ID: {resp.json().get('id')})")
                os.remove(filepath)
                # Try to use git rm if inside a git repo
                try:
                    subprocess.run(["git", "rm", filepath], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    pass
                exitosos += 1
            else:
                print(f"❌ Error al publicar: {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            
    print(f"\n--- Resumen: {exitosos}/{len(archivos_a_procesar)} publicados con éxito ---")

if __name__ == "__main__":
    publicar_posts()
