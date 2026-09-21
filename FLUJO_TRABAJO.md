# 🚀 FLUJO DE TRABAJO - MUNDOS SIMULADOS

## 1️⃣ VERIFICACIÓN BASE (OBLIGATORIO - Ejecutar PRIMERO)

```powershell
python verificacion_base.py
```

**✅ Qué valida:**

- No hay nombres de imágenes duplicados en el Excel
- Estructura del archivo está correcta
- Todas las columnas requeridas existen

**⛔ Si falla:**

- El script detiene y señala el problema
- No continúes hasta resolver

---

## 2️⃣ GENERAR IMÁGENES CON GOOGLE COLAB ⭐ (Recomendado)

**Archivo:** `Mundos_Simulados_GoogleColab.ipynb`

**Características:**

- ✅ Genera 720 imágenes automáticamente
- ✅ Usa GPU T4 de Colab (gratis)
- ✅ Sube directamente a WordPress
- ✅ Actualiza Excel con URLs
- ✅ ~3-6 horas para todas

**Cómo usar:**

1. Lee: `GUIA_GOOGLE_COLAB.md` (instrucciones paso a paso)
2. Ve a: https://colab.research.google.com/
3. Sube el notebook `Mundos_Simulados_GoogleColab.ipynb`
4. Ejecuta las celdas en orden
5. Descarga el Excel con URLs completadas

---

## 3️⃣ PROYECTOS (Solo después de imágenes + validación OK)

### Opción A: Generar Artículos

```powershell
python 01_generar_articulos.py              # Genera todos (240 artículos)
python 01_generar_articulos.py --limite 5   # Prueba rápida con 5
```

### Opción B: Publicar en WordPress

```powershell
python 02_publicar_wordpress.py --limite 5 --seco     # Prueba (no publica)
python 02_publicar_wordpress.py --limite 5            # Publica 5 artículos
python 02_publicar_wordpress.py                       # Publica TODOS
```

### Opción C: Crear Pines para Pinterest

```powershell
python 03_crear_pines_pinterest.py
```

### Opción D: Obtener Board ID de Pinterest

```powershell
python obtener_board_id.py
```

---

## 📋 OTRAS UTILIDADES

### Validación detallada de imágenes

```powershell
python validar_imagenes_sin_duplicados.py
```

Muestra lista completa de todas las imágenes y detecta duplicados

### Regenerar CSV desde Excel

```powershell
python -c "import pandas as pd; df = pd.read_excel('Estructura Mundos Simulados.xlsx'); df.to_csv('Estructura Mundos Simulados.csv', index=False, sep=',', encoding='utf-8'); print('✓ CSV regenerado')"
```

### Validar imágenes en disco

```powershell
python validar_imagenes_excel.py
```

### Mapear imágenes

```powershell
python 00_mapa_imagenes.py
```

---

## 🔐 CONFIGURACIÓN REQUERIDA (.env)

El archivo `.env` debe tener:

```env
GEMINI_API_KEY=xxxxx
GEMINI_MODEL=gemini-2.5-flash
CSV_PATH=Estructura Mundos Simulados.csv
WP_URL=https://mundossimulados.online
WP_USER=email@gmail.com
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
WP_SEO_PLUGIN=rankmath
```

---

## 📊 LOGS Y ARCHIVOS DE SEGUIMIENTO

- `generacion_log.csv` — Registro de artículos generados
- `publicacion_log.csv` — Registro de publicaciones WordPress
- `media_map.json` — Mapeo de imágenes
- `articulos/` — Carpeta con archivos .md de artículos

---

## ⚡ RESUMEN RÁPIDO

1. **Primero:** `python verificacion_base.py` ✅
2. **Segundo:** Generar imágenes en Google Colab (Lee `GUIA_GOOGLE_COLAB.md`)
3. **Tercero:** Descargar Excel con URLs
4. **Cuarto:** Elegir proyecto (generar / publicar / pines)
5. **Quinto:** Ejecutar comando correspondiente
6. **Sexto:** Revisar logs

---

**Última actualización:** 15 ago 2026
