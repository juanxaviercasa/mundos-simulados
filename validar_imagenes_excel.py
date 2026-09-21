#!/usr/bin/env python3
"""Valida los nombres de imágenes del Excel/CSV antes de crear o publicar contenido.

Objetivo:
- detectar nombres repetidos
- detectar archivos con sufijo -1, -2, etc.
- avisar antes de que se creen imágenes duplicadas o se pierda tiempo

Uso:
    python validar_imagenes_excel.py
    python validar_imagenes_excel.py --archivo "Estructura Mundos Simulados.csv"
    python validar_imagenes_excel.py --aplicar
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


ARCHIVO_EXCEL = "Estructura Mundos Simulados.xlsx"
ARCHIVO_CSV = "Estructura Mundos Simulados.csv"


def elegir_archivo(path_excel: str | None, path_csv: str | None) -> Path:
    if path_excel and Path(path_excel).exists():
        return Path(path_excel)
    if path_csv and Path(path_csv).exists():
        return Path(path_csv)

    if Path(ARCHIVO_EXCEL).exists():
        return Path(ARCHIVO_EXCEL)
    if Path(ARCHIVO_CSV).exists():
        return Path(ARCHIVO_CSV)

    raise FileNotFoundError(
        "No se encontró ni el Excel ni el CSV del proyecto. "
        "Asegúrate de estar en la carpeta correcta."
    )


def columnas_imagenes(df: pd.DataFrame) -> list[str]:
    columnas = []
    for col in df.columns:
        nombre = str(col).strip().lower()
        if "archivo" in nombre and "prompt" not in nombre:
            columnas.append(str(col))
    return columnas


def base_nombre_imagen(nombre: str) -> str:
    if not isinstance(nombre, str):
        return ""
    nombre = nombre.strip()
    if not nombre:
        return ""
    nombre_sin_ext = Path(nombre).stem
    nombre_sin_ext = re.sub(r"-\d+$", "", nombre_sin_ext)
    return nombre_sin_ext.lower()


def detectar_duplicados(df: pd.DataFrame) -> list[dict]:
    imagenes = []
    for _, fila in df.iterrows():
        slug = fila.get("URL Slug (Post)", "")
        for col in columnas_imagenes(df):
            valor = fila.get(col, "")
            if isinstance(valor, str) and valor.strip():
                imagenes.append({
                    "slug": str(slug) if pd.notna(slug) else "",
                    "columna": col,
                    "valor": valor.strip(),
                    "base": base_nombre_imagen(valor),
                })

    duplicados: dict[str, list[dict]] = {}
    for item in imagenes:
        base = item["base"]
        if not base:
            continue
        duplicados.setdefault(base, []).append(item)

    resultado = []
    for base, items in sorted(duplicados.items()):
        if len(items) > 1:
            resultado.append({
                "base": base,
                "items": items,
            })

    return resultado


def sugerir_nombre(base: str, n: int = 1) -> str:
    # Genera un nombre más semántico para evitar el sufijo -1 genérico.
    # Ejemplo: "apagon-global-internet" -> "apagon-global-internet-caida-red"
    # La idea es que la revisión humana decida mejor, pero al menos evita el relleno automático.
    sufijo = ["caida-red", "ecosistema", "ruina-urbana", "panico", "escena-principal"]
    return f"{base}-{sufijo[(n - 1) % len(sufijo)]}.webp"


def detectar_variantes_duplicadas(df: pd.DataFrame) -> list[dict]:
    problemas = []
    for _, fila in df.iterrows():
        slug = fila.get("URL Slug (Post)", "")
        for col in columnas_imagenes(df):
            valor = fila.get(col, "")
            if not isinstance(valor, str):
                continue
            valor = valor.strip()
            if not valor:
                continue
            if re.search(r"-\d+\.[A-Za-z0-9]+$", valor):
                base = base_nombre_imagen(valor)
                sugerido = sugerir_nombre(base, 1)
                problemas.append({
                    "slug": str(slug) if pd.notna(slug) else "",
                    "columna": col,
                    "valor_actual": valor,
                    "valor_sugerido": sugerido,
                    "motivo": "Nombre duplicado con sufijo -1/-2",
                })
    return problemas


def cargar_dataframe(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    return pd.read_excel(path, dtype=str, keep_default_na=False)


def aplicar_sugerencias(df: pd.DataFrame, problemas: list[dict]) -> pd.DataFrame:
    df2 = df.copy()
    for item in problemas:
        slug = item["slug"]
        columna = item["columna"]
        valor_actual = item["valor_actual"]
        nuevo = item["valor_sugerido"]
        if slug:
            for idx, fila in df2.iterrows():
                if str(fila.get("URL Slug (Post)", "")) == slug:
                    if str(fila.get(columna, "")).strip() == valor_actual:
                        df2.at[idx, columna] = nuevo
                        break
    return df2


def guardar_dataframe(df: pd.DataFrame, path: Path) -> None:
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
    else:
        df.to_excel(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida nombres de imágenes antes de generar contenido.")
    parser.add_argument("--archivo", help="Ruta al Excel o CSV a validar")
    parser.add_argument("--aplicar", action="store_true", help="Aplica sugerencias de renombrado en el archivo original")
    parser.add_argument("--no-fail", action="store_true", help="Solo avisa pero no corta la ejecución")
    args = parser.parse_args()

    try:
        archivo = elegir_archivo(args.archivo, None)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)

    print(f"Revisando: {archivo}")
    df = cargar_dataframe(archivo)
    cols = columnas_imagenes(df)

    if not cols:
        print("ERROR: no se encontraron columnas de imagen en el archivo.")
        raise SystemExit(1)

    print(f"Columnas detectadas: {', '.join(cols)}")

    duplicados = detectar_duplicados(df)
    variantes = detectar_variantes_duplicadas(df)

    print("\n=== RESULTADO ===")
    print(f"Nombres de imagen duplicados detectados: {len(duplicados)} grupos")
    print(f"Nombres con sufijo -1/-2 detectados: {len(variantes)}")

    if not duplicados and not variantes:
        print("✅ Sin duplicados ni sufijos problemáticos. El archivo está bien para continuar.")
        return

    if duplicados:
        print("\n⚠️ Duplicados por nombre base:")
        for grupo in duplicados:
            print(f"- Base: {grupo['base']}")
            for item in grupo["items"]:
                print(f"  • {item['slug']} | {item['columna']} = {item['valor']}")

    if variantes:
        print("\n⚠️ Nombres con -1/-2 detectados:")
        for item in variantes:
            print(
                f"- {item['slug']} | {item['columna']} | "
                f"Actual: {item['valor_actual']} | Sugerido: {item['valor_sugerido']}"
            )

    if args.aplicar:
        print("\nAplicando sugerencias de renombrado...")
        df_nueva = aplicar_sugerencias(df, variantes)
        guardar_dataframe(df_nueva, archivo)
        print(f"✅ Archivo actualizado: {archivo}")
        return

    if not args.no_fail:
        print("\n❌ Validación fallida: se detiene la generación para evitar nombres duplicados.")
        raise SystemExit(2)

    print("\nPara aplicar los cambios usa: python validar_imagenes_excel.py --archivo \"<ruta>\" --aplicar")


if __name__ == "__main__":
    main()
