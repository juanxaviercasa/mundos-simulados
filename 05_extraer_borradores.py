import os
import requests
import frontmatter
from markdownify import markdownify as md
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv

load_dotenv()

WP_URL = "https://dev-simulandomundos.pantheonsite.io"
WP_USER = os.environ.get("WP_USER")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

BORRADORES_DIR = "borradores"
os.makedirs(BORRADORES_DIR, exist_ok=True)

def extraer_borradores():
    print(f"Conectando a {WP_URL}/wp-json/wp/v2/posts ...")
    params = {
        'status': 'draft,future,pending,private',
        'per_page': 100
    }
    
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/posts", auth=auth, params=params)
    if resp.status_code != 200:
        print(f"Error al conectar: {resp.status_code} - {resp.text}")
        return
        
    posts = resp.json()
    print(f"Se encontraron {len(posts)} borradores/programados.")
    
    for post in posts:
        slug = post.get('slug') or str(post['id'])
        title = post['title']['rendered']
        
        # WP SEO Meta
        meta_wp = post.get('meta', {})
        
        # Construir Markdown
        content_html = post['content']['rendered']
        content_md = md(content_html, heading_style="ATX")
        
        # Frontmatter post object
        fm_post = frontmatter.Post(content_md)
        fm_post['title'] = title
        fm_post['slug'] = slug
        fm_post['wp_id'] = post['id']
        fm_post['status'] = post['status']
        fm_post['date'] = post.get('date')
        
        if post.get('categories'):
            fm_post['categories'] = post['categories']
        if post.get('tags'):
            fm_post['tags'] = post['tags']
            
        # SEO
        rank_math_title = meta_wp.get('rank_math_title', '')
        if rank_math_title:
            fm_post['rank_math_title'] = rank_math_title
            fm_post['rank_math_description'] = meta_wp.get('rank_math_description', '')
            fm_post['rank_math_focus_keyword'] = meta_wp.get('rank_math_focus_keyword', '')
        
        filepath = os.path.join(BORRADORES_DIR, f"{slug}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(fm_post))
            
        print(f"Guardado: {filepath}")

if __name__ == "__main__":
    if not WP_USER or not WP_APP_PASSWORD:
        print("Falta WP_USER o WP_APP_PASSWORD en el .env")
    else:
        extraer_borradores()
