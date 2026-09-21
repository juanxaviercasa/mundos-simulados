#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script maestro: Verificación base antes de cualquier proyecto
Ejecuta todas las validaciones iniciales requeridas
"""

import subprocess
import sys
from pathlib import Path

def ejecutar_verificacion(nombre, comando):
    """Ejecuta un comando de verificación y reporta resultado"""
    print(f"\n{'='*70}")
    print(f"🔍 {nombre}")
    print(f"{'='*70}\n")
    
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=False)
        if resultado.returncode == 0:
            print(f"\n✅ {nombre}: PASÓ\n")
            return True
        else:
            print(f"\n❌ {nombre}: FALLÓ\n")
            return False
    except Exception as e:
        print(f"\n❌ Error en {nombre}: {e}\n")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 VERIFICACIÓN BASE - MUNDOS SIMULADOS")
    print("="*70)
    
    # Ruta de Python
    python_path = r"C:\Users\cabel\AppData\Local\Programs\Python\Python312\python.exe"
    
    # Lista de verificaciones obligatorias
    verificaciones = [
        ("Validar imágenes sin duplicados", f'"{python_path}" validar_imagenes_sin_duplicados.py'),
    ]
    
    resultados = {}
    for nombre, comando in verificaciones:
        resultados[nombre] = ejecutar_verificacion(nombre, comando)
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("="*70 + "\n")
    
    todas_ok = True
    for nombre, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado:8s} | {nombre}")
        if not resultado:
            todas_ok = False
    
    print("\n" + "="*70)
    
    if todas_ok:
        print("\n✅ TODAS LAS VERIFICACIONES PASARON")
        print("\n📋 Puedes proceder con:")
        print("   • python 01_generar_articulos.py")
        print("   • python 02_publicar_wordpress.py")
        print("   • python 03_crear_pines_pinterest.py")
        print("\n" + "="*70 + "\n")
        return 0
    else:
        print("\n❌ ALGUNAS VERIFICACIONES FALLARON")
        print("⛔ Resuelve los problemas antes de continuar\n")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
