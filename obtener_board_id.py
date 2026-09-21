#!/usr/bin/env python3
"""Obtiene el Board ID correcto de Pinterest"""

import requests
import json
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")

print("🔍 Consultando tus tableros en Pinterest...\n")

url = "https://api.pinterest.com/v5/me/boards"
params = {
    "access_token": TOKEN,
    "fields": "id,name,description"
}

try:
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        boards = data.get('items', [])
        
        if boards:
            print("✅ Tableros encontrados:\n")
            for board in boards:
                print(f"   📌 Nombre: {board.get('name')}")
                print(f"      Board ID: {board.get('id')}")
                print(f"      Descripción: {board.get('description', 'Sin descripción')}")
                print()
        else:
            print("❌ No se encontraron tableros")
            print(f"Response: {data}")
    else:
        print(f"❌ Error en la API (Status {response.status_code}):")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
