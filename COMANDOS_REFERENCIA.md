# Comandos y Rutas de Referencia — Mundos Simulados

## Información del Proyecto

- **Ruta del Proyecto:** `C:\Users\cabel\Music\mundos_simulados`
- **Usuario:** `cabel`
- **Versión Python:** 3.12
- **Ruta Python:** `C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe`

---

## ¿Cómo Usar Este Documento?

Cada comando tiene esta estructura:

```
COMANDO ORIGINAL (para este proyecto):
[comando específico]

PLANTILLA GENÉRICA (para otros proyectos):
[comando con placeholders entre {{}}]

EJEMPLO PARA OTRO PROYECTO:
[ejemplo con rutas diferentes]
```

---

## 1. Configuración Inicial

### 1.1 Crear Alias de Python (Una sola vez)

**COMANDO ORIGINAL:**

```powershell
Set-Alias -Name python -Value 'C:\Users\cabel\AppData\Local\Programs\Python\Python312\python.exe'
```

**PLANTILLA GENÉRICA:**

```powershell
Set-Alias -Name python -Value '{{RUTA_PYTHON}}'
```

**REEMPLAZOS:**

- `{{RUTA_PYTHON}}` = Ruta completa a `python.exe` en tu instalación

**EJEMPLO PARA OTRO USUARIO:**
Si otro usuario es "maria" y Python está en `D:\Python312`:

```powershell
Set-Alias -Name python -Value 'D:\Python312\python.exe'
```

---

### 1.2 Hacer Permanente el Alias (Opcional)

**COMANDO ORIGINAL:**

```powershell
Add-Content $PROFILE "Set-Alias -Name python -Value 'C:\Users\cabel\AppData\Local\Programs\Python\Python312\python.exe'"
```

**PLANTILLA GENÉRICA:**

```powershell
Add-Content $PROFILE "Set-Alias -Name python -Value '{{RUTA_PYTHON}}'"
```

---

## 2. Instalación de Dependencias

### 2.1 Instalar Paquetes Python

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe -m pip install google-generativeai python-frontmatter markdown requests pandas python-dotenv openpyxl
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} -m pip install google-generativeai python-frontmatter markdown requests pandas python-dotenv openpyxl
```

**NOTA:** Si usas alias `python`, puedes simplificar a:

```powershell
python -m pip install google-generativeai python-frontmatter markdown requests pandas python-dotenv openpyxl
```

---

## 3. Gestión del CSV

### 3.1 Convertir Excel a CSV

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe -c "import pandas as pd; df = pd.read_excel('Estructura Mundos Simulados.xlsx'); df.to_csv('Estructura Mundos Simulados.csv', index=False, sep=',', encoding='utf-8'); print('✓ CSV regenerado')"
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} -c "import pandas as pd; df = pd.read_excel('{{NOMBRE_EXCEL}}'); df.to_csv('{{NOMBRE_CSV}}', index=False, sep=',', encoding='utf-8'); print('✓ CSV regenerado')"
```

**REEMPLAZOS:**

- `{{RUTA_PYTHON}}` = Ruta completa a `python.exe`
- `{{NOMBRE_EXCEL}}` = Nombre del archivo Excel (ej: `datos.xlsx`)
- `{{NOMBRE_CSV}}` = Nombre del archivo CSV resultante (ej: `datos.csv`)

**EJEMPLO PARA OTRO PROYECTO:**

```powershell
python -c "import pandas as pd; df = pd.read_excel('articulos_fuente.xlsx'); df.to_csv('articulos_fuente.csv', index=False, sep=',', encoding='utf-8'); print('✓ CSV regenerado')"
```

---

## 4. Scripts Principales

### 4.1 Mapa de Imágenes (Una sola vez)

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 00_mapa_imagenes.py
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} {{NOMBRE_SCRIPT}}
```

**DESDE CUALQUIER CARPETA CON ALIAS:**

```powershell
cd {{RUTA_PROYECTO}}
python 00_mapa_imagenes.py
```

---

### 4.2 Generar Artículos (Paso 1 del pipeline)

#### Con Límite (Prueba)

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 01_generar_articulos.py --limite 5 --categoria tecnologia
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} 01_generar_articulos.py --limite {{CANTIDAD}} --categoria {{CATEGORIA}}
```

**REEMPLAZOS:**

- `{{RUTA_PYTHON}}` = Ruta a python.exe
- `{{CANTIDAD}}` = Número de artículos (ej: 5, 10, 50)
- `{{CATEGORIA}}` = Slug de categoría del CSV (ej: tecnologia, economia)

**EJEMPLO PARA OTRO PROYECTO:**

```powershell
python 01_generar_articulos.py --limite 10 --categoria noticias
```

#### Sin Límite (Todos los Artículos)

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 01_generar_articulos.py
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} 01_generar_articulos.py
```

**NOTA:** Genera todos los artículos. Si se interrumpe, ejecuta de nuevo y continúa desde donde paró.

---

### 4.3 Publicar en WordPress (Paso 2 del pipeline)

#### Prueba en Seco (Sin Publicar)

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 02_publicar_wordpress.py --limite 5 --seco
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} 02_publicar_wordpress.py --limite {{CANTIDAD}} --seco
```

#### Publicar de Verdad

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 02_publicar_wordpress.py --limite 5
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} 02_publicar_wordpress.py --limite {{CANTIDAD}}
```

#### Sin Límite (Todos los Artículos)

**COMANDO ORIGINAL:**

```powershell
C:/Users/cabel/AppData/Local/Programs/Python/Python312/python.exe 02_publicar_wordpress.py
```

**PLANTILLA GENÉRICA:**

```powershell
{{RUTA_PYTHON}} 02_publicar_wordpress.py
```

---

## 5. Limpieza y Mantenimiento

### 5.1 Borrar Log de Publicación

**COMANDO ORIGINAL:**

```powershell
Remove-Item publicacion_log.csv
```

**NOTA:** Permite republicar artículos que ya tienen `.md`

---

## 6. Estructura de Carpetas Esperada

```
{{RUTA_PROYECTO}}/
├── 00_mapa_imagenes.py
├── 01_generar_articulos.py
├── 02_publicar_wordpress.py
├── articulos/                    (se crea automáticamente)
│   ├── articulo1.md
│   ├── articulo2.md
│   └── ...
├── Estructura_Datos.xlsx         (tu archivo fuente)
├── Estructura_Datos.csv          (generado desde Excel)
├── media_map.json                (creado por 00_mapa_imagenes.py)
├── generacion_log.csv            (creado por 01_generar_articulos.py)
├── publicacion_log.csv           (creado por 02_publicar_wordpress.py)
├── .env                          (configuración - NO subir a repositorio)
├── mu-plugin-campos-seo.php      (subir a wp-content/mu-plugins/)
└── LEEME_PRIMERO.md
```

---

## 7. Archivo .env (Configuración)

**UBICACIÓN:** Raíz del proyecto

**CONTENIDO REQUERIDO:**

```env
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-2.5-flash
CSV_PATH=Estructura Mundos Simulados.csv
WP_URL=https://tusite.com
WP_USER=tu_usuario
WP_APP_PASSWORD=tu_contraseña_aplicacion
WP_SEO_PLUGIN=rankmath
```

**REEMPLAZOS:**

- `GEMINI_API_KEY` = Tu clave de Google AI Studio (https://aistudio.google.com)
- `GEMINI_MODEL` = Modelo Flash disponible en tu cuenta
- `CSV_PATH` = Nombre exacto de tu archivo CSV
- `WP_URL` = URL de tu sitio WordPress
- `WP_USER` = Usuario/email de WordPress
- `WP_APP_PASSWORD` = Contraseña de aplicación (Perfil → Contraseñas de aplicación)
- `WP_SEO_PLUGIN` = `rankmath` o `yoast` según tu plugin

---

## 8. Flujo Completo para Cualquier Proyecto

1. **Instalar dependencias:**

   ```powershell
   cd {{RUTA_PROYECTO}}
   python -m pip install google-generativeai python-frontmatter markdown requests pandas python-dotenv openpyxl
   ```

2. **Configurar `.env`** con tus datos

3. **Convertir Excel a CSV:**

   ```powershell
   python -c "import pandas as pd; df = pd.read_excel('{{NOMBRE_EXCEL}}'); df.to_csv('{{NOMBRE_CSV}}', index=False, sep=',', encoding='utf-8'); print('✓ CSV regenerado')"
   ```

4. **Mapear imágenes:**

   ```powershell
   python 00_mapa_imagenes.py
   ```

5. **Generar artículos (prueba):**

   ```powershell
   python 01_generar_articulos.py --limite 5
   ```

6. **Publicar en seco:**

   ```powershell
   python 02_publicar_wordpress.py --limite 5 --seco
   ```

7. **Publicar de verdad:**

   ```powershell
   python 02_publicar_wordpress.py --limite 5
   ```

8. **Escalar (generar todos):**
   ```powershell
   python 01_generar_articulos.py
   python 02_publicar_wordpress.py
   ```

---

## 9. Troubleshooting Rápido

| Problema                   | Solución                                                        |
| -------------------------- | --------------------------------------------------------------- |
| Python no encontrado       | Usar ruta completa en lugar de alias, o crear alias como en 1.1 |
| CSV con errores de parsing | Regenerar desde Excel con comando 3.1                           |
| Imágenes no encontradas    | Ejecutar `00_mapa_imagenes.py` nuevamente                       |
| Artículos no se publican   | Verificar `.env`, credenciales WordPress y mu-plugin            |
| Límite de cuota Gemini     | Esperar a que se resetee (medianoche UTC) o cambiar `--pausa`   |
| Script interrumpido        | Ejecutar nuevamente; retoma desde donde paró                    |

---

## 10. Información del Proyecto Actual

**Proyecto:** Mundos Simulados  
**Inicio:** 14 de agosto de 2026  
**Estado:** Generando 240 artículos desde Gemini API  
**Cadencia:** 5 artículos/día automáticamente en WordPress
