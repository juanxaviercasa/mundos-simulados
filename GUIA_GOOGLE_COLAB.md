# 🎨 Guía: Generar Imágenes en Google Colab

## 📋 Resumen Rápido

1. Abre Google Colab
2. Sube el notebook
3. Carga tu Excel
4. Ejecuta las celdas
5. ✅ 720 imágenes generadas y subidas a WordPress

**Tiempo:** 3-6 horas | **Costo:** $0 | **GPU:** T4 de Colab

---

## 🚀 Paso a Paso

### PASO 1: Preparar tu Excel

Tu archivo actual:

```
C:\Users\cabel\Music\mundos_simulados\Estructura Mundos Simulados.xlsx
```

**Opción A:** Subirlo a Google Drive (recomendado)

- Ve a Google Drive
- Sube el archivo `Estructura Mundos Simulados.xlsx`
- Copia su ID desde la URL (entre `/d/` y `/edit`)

**Opción B:** Compartir acceso directo

- Clic derecho → Compartir
- Obtener enlace compartible
- Copiarlo

**Opción C:** Subir manualmente en Colab (más lento)

- En el notebook → Celda 3
- Ejecutar y cargar archivo

---

### PASO 2: Abrir Google Colab

1. Ve a: https://colab.research.google.com/
2. Clic en **Archivo → Abrir notebook**
3. Selecciona **"Subir"**
4. Busca: `Mundos_Simulados_GoogleColab.ipynb`

**O carga directamente aquí:**

```
https://colab.research.google.com/notebook#fileId=YOUR_FILE_ID
```

---

### PASO 3: Editar las Credenciales

En la **Celda 4**, reemplaza:

```python
# ❌ ANTES (deja igual, ya está configurado)
WP_URL = "https://mundossimulados.online"
WP_USER = "jxaviercabellos@gmail.com"
WP_PASSWORD = "4soz XqeV beJE 9fmj wvCf ZrqI"
```

✅ Ya está con tus datos reales

---

### PASO 4: Cargar el Excel (Celda 3)

**Descomentar UNA de estas opciones:**

#### A. Si lo subiste a Google Drive:

```python
file_id = '1234567890abcdefghijk'  # Tu ID de Drive
import gdown
gdown.download(f'https://drive.google.com/uc?id={file_id}', 'Estructura.xlsx')
excel_path = 'Estructura.xlsx'
```

#### B. Si lo compartiste vía enlace:

```python
import gdown
url = 'https://drive.google.com/uc?id=YOUR_FILE_ID&export=download'
gdown.download(url, 'Estructura.xlsx')
excel_path = 'Estructura.xlsx'
```

#### C. Subir manual (más lento):

```python
from google.colab import files
uploaded = files.upload()
excel_path = list(uploaded.keys())[0]
```

---

### PASO 5: Ejecutar las Celdas EN ORDEN

```
1️⃣ Celda 1: Instalar dependencias (2-3 min)
   ↓
2️⃣ Celda 2: Montar Drive (opcional)
   ↓
3️⃣ Celda 3: Cargar Excel (30 seg)
   ↓
4️⃣ Celda 4: Config WordPress (1 seg)
   ↓
5️⃣ Celda 5: Descargar modelo Stable Diffusion (3-5 min) ⚠️ IMPORTANTE
   ↓
6️⃣ Celda 6: Función generar imagen (1 seg)
   ↓
7️⃣ Celda 7: Función subir WordPress (1 seg)
   ↓
8️⃣ Celda 8: 🔥 GENERAR Y SUBIR TODAS LAS IMÁGENES (3-6 horas)
   ↓
9️⃣ Celda 9: Guardar Excel actualizado (1 min)
   ↓
🔟 Celda 10: Ver resumen (1 seg)
```

---

## ⚠️ Cosas Importantes

### Si se desconecta Colab durante la generación:

- **No se pierden las imágenes** (ya están en WordPress)
- Las URLs quedan guardadas en Excel
- Solo repite con los artículos no procesados
- **La sesión de Colab dura máximo 12 horas**

### Si falla una imagen:

- El notebook continúa con la siguiente
- Ver el resumen final para ver cuáles fallaron
- No es crítico, puede reintentar después

### Velocidad esperada:

- Con GPU T4: 10-20 segundos por imagen
- 720 imágenes = 2-4 horas aproximadamente
- Colab no te desconectará en ese tiempo

---

## 📊 Qué Esperar

### Mientras se ejecuta Celda 8:

```
📄 [1/240] El día que el internet murió...
   🎨 apagon-global-internet-caida-red → 📤 Subiendo... ✅
   🎨 colapso-financiero-sin-red → 📤 Subiendo... ✅
   🎨 reconstruccion-red-analogica → 📤 Subiendo... ✅
   ⏱️ 45s | 3/3 exitosas

📄 [2/240] IA al mando: La aterradora simulación...
   🎨 mundo-gobernado-por-ia → 📤 Subiendo... ✅
   ...
```

### Al final:

```
======================================================================
✅ GENERACIÓN COMPLETADA
   Total: 720 | Exitosas: 720
   Tiempo: 18000s (~5 horas)
======================================================================
```

---

## ✅ Después de Terminar

1. **Descarga el Excel** (Celda 9)
   - Se llamará: `Estructura_Mundos_Simulados_CON_IMAGENES.xlsx`
   - Contiene todas las URLs de WordPress

2. **Reemplaza tu archivo local:**

   ```powershell
   # En tu PC:
   cp Estructura_Mundos_Simulados_CON_IMAGENES.xlsx "Estructura Mundos Simulados.xlsx"
   ```

3. **Verifica en WordPress:**
   - Ve a Media Library
   - Deberías ver todas las 720 imágenes subidas

4. **Próximo paso:** Publicar los artículos
   ```powershell
   python 02_publicar_wordpress.py
   ```

---

## 🆘 Troubleshooting

| Problema                                           | Solución                                                  |
| -------------------------------------------------- | --------------------------------------------------------- |
| "ModuleNotFoundError: No module named 'diffusers'" | Ejecuta Celda 1 de nuevo                                  |
| "Authentication failed"                            | Verifica WP_PASSWORD en Celda 4                           |
| "CUDA out of memory"                               | Restart runtime y reduce `num_inference_steps` de 30 a 20 |
| "Timeout downloading model"                        | Reinicia y ejecuta Celda 5 de nuevo                       |
| Excel no carga                                     | Verifica el file_id de Drive (sin /edit)                  |
| Falla generación después de X imágenes             | Reinicia, cambia seed, o reduce pasos                     |

---

## 📞 Notas Finales

- **GPU T4:** Gratis en Colab, pero con throttling si usas >12h continuas
- **Modelos:** Usando Stable Diffusion v1.5 (más rápido que SDXL)
- **Calidad:** 768x1024px, buena para WordPress
- **Seguridad:** Las credenciales NO se guardan en el notebook compartido

¡Listo! Ahora solo falta ejecutar. 🚀

---

**Última actualización:** 15 ago 2026
