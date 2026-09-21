#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar que no haya nombres de imágenes duplicados en el Excel
Analiza las columnas: Archivo Destacada, Archivo Interna 1, Archivo Interna 2
"""

import pandas as pd
import sys
from pathlib import Path
from collections import defaultdict

def validar_imagenes_duplicadas():
    """
    Lee el Excel y detecta nombres de imágenes duplicadas
    """
    # Ruta del archivo Excel
    excel_path = Path("Estructura Mundos Simulados.xlsx")
    
    if not excel_path.exists():
        print(f"❌ Error: No se encuentra {excel_path}")
        return False
    
    try:
        # Leer el Excel
        df = pd.read_excel(excel_path)
        print(f"✓ Cargado Excel con {len(df)} filas\n")
        
        # Columnas que contienen nombres de imágenes
        columnas_imagenes = [
            "Archivo Destacada",
            "Archivo Interna 1", 
            "Archivo Interna 2"
        ]
        
        # Verificar que las columnas existan
        columnas_faltantes = [col for col in columnas_imagenes if col not in df.columns]
        if columnas_faltantes:
            print(f"⚠️  Columnas no encontradas: {columnas_faltantes}")
            print(f"Columnas disponibles: {list(df.columns)}\n")
            return False
        
        # Diccionario para rastrear dónde aparece cada imagen
        imagen_ubicaciones = defaultdict(list)
        
        # Recorrer todas las filas y columnas de imágenes
        for idx, row in df.iterrows():
            tema = row.get("Tema General (H1)", f"Fila {idx+1}")
            
            for col in columnas_imagenes:
                imagen = row[col]
                if pd.notna(imagen) and str(imagen).strip():
                    imagen = str(imagen).strip().lower()
                    imagen_ubicaciones[imagen].append({
                        'fila': idx + 1,
                        'columna': col,
                        'tema': tema[:50] + "..." if len(tema) > 50 else tema
                    })
        
        # Encontrar duplicados
        duplicados = {img: ubicaciones for img, ubicaciones in imagen_ubicaciones.items() 
                     if len(ubicaciones) > 1}
        
        if not duplicados:
            print("✅ No hay nombres de imágenes duplicados\n")
            print(f"Total de imágenes únicas: {len(imagen_ubicaciones)}")
            return True
        
        # Mostrar duplicados encontrados
        print(f"⚠️  DUPLICADOS ENCONTRADOS: {len(duplicados)}\n")
        print("=" * 100)
        
        for imagen, ubicaciones in sorted(duplicados.items()):
            print(f"\n📸 Imagen: {imagen}")
            print(f"   Repetida {len(ubicaciones)} veces:\n")
            for ubicacion in ubicaciones:
                print(f"   • Fila {ubicacion['fila']:3d} | {ubicacion['columna']:20s} | {ubicacion['tema']}")
            print()
        
        print("=" * 100)
        print(f"\n⚠️  Total de imágenes únicas: {len(imagen_ubicaciones)}")
        print(f"⚠️  Total de duplicados: {len(duplicados)}")
        print(f"⚠️  Total de ocurrencias duplicadas: {sum(len(u) for u in duplicados.values())}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error al procesar el Excel: {e}")
        return False

if __name__ == "__main__":
    validar_imagenes_duplicadas()
