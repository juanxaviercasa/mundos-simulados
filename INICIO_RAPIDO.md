# 🎯 INICIO RÁPIDO - Mundos Simulados

## 📋 Lo que tienes listo

✅ **Verificación de imágenes sin duplicados**

- Script: `validar_imagenes_sin_duplicados.py`
- Resultado: 720 imágenes únicas, sin problemas

✅ **Google Colab para generar imágenes**

- Notebook: `Mundos_Simulados_GoogleColab.ipynb`
- Guía: `GUIA_GOOGLE_COLAB.md`
- Tiempo: 3-6 horas | Costo: $0

✅ **Scripts de generación y publicación**

- `01_generar_articulos.py` — Generar contenido
- `02_publicar_wordpress.py` — Publicar en WP
- `03_crear_pines_pinterest.py` — Crear pines

---

## 🚀 Los 3 Pasos para Empezar

### PASO 1: Verificar estructura

```powershell
python verificacion_base.py
```

Debe mostrar: ✅ TODAS LAS VERIFICACIONES PASARON

---

### PASO 2: Generar imágenes en Colab

1. Abre: https://colab.research.google.com/
2. Sube el notebook: `Mundos_Simulados_GoogleColab.ipynb`
3. Lee la guía: `GUIA_GOOGLE_COLAB.md` (5 min)
4. Ejecuta las celdas
5. Descarga el Excel con URLs

---

### PASO 3: Elegir siguiente proyecto

**Option A:** Generar artículos de texto

```powershell
python 01_generar_articulos.py
```

**Option B:** Publicar en WordPress

```powershell
python 02_publicar_wordpress.py
```

**Option C:** Crear pines Pinterest

```powershell
python 03_crear_pines_pinterest.py
```

---

## 📚 Documentación Completa

- **FLUJO_TRABAJO.md** — Workflow completo con todos los comandos
- **GUIA_GOOGLE_COLAB.md** — Paso a paso para Google Colab
- **LEEME_PRIMERO.md** — Información general del proyecto
- **COMANDOS_REFERENCIA.md** — Referencia de comandos

---

## 🔑 Configuración (.env)

✅ Ya está configurado con:

- `GEMINI_API_KEY` — Para generar texto
- `WP_URL`, `WP_USER`, `WP_PASSWORD` — Para WordPress
- `WP_SEO_PLUGIN` — Para SEO (Rank Math)

---

## 🎨 El Flujo Completo (Resumen)

```
1. Verificación base ✅ (5 min)
   ↓
2. Generar 720 imágenes (3-6 horas)
   ├─ Leer Excel
   ├─ Generar en Colab
   └─ Subir a WordPress
   ↓
3. Generar 240 artículos (1-2 horas)
   ├─ Leer prompts del Excel
   ├─ Generar con Gemini API
   └─ Guardar en .md
   ↓
4. Publicar en WordPress (1-2 horas)
   ├─ Leer artículos generados
   ├─ Crear posts
   ├─ Subir imágenes
   └─ Configurar SEO
   ↓
5. Crear pines Pinterest (30 min)
   ├─ Generar miniaturas
   ├─ Subir a Pinterest
   └─ Publicar en boards
```

---

## ⚡ Próximos Pasos

1. **Ahora:** Lee `GUIA_GOOGLE_COLAB.md`
2. **Luego:** Sube el notebook a Colab y ejecuta
3. **Después:** Descarga el Excel con URLs
4. **Finalmente:** Elige si generar artículos o publicar

---

## 🆘 Ayuda Rápida

| Pregunta                      | Respuesta                                                             |
| ----------------------------- | --------------------------------------------------------------------- |
| ¿Qué archivo ejecuto primero? | `python verificacion_base.py`                                         |
| ¿Cómo genero imágenes?        | Google Colab + `Mundos_Simulados_GoogleColab.ipynb`                   |
| ¿Necesito pagar?              | No, todo es gratis (Colab GPU + tu servidor WP)                       |
| ¿Cuánto tiempo tarda?         | ~12 horas total (imágenes + artículos + publicación)                  |
| ¿Puedo hacer todo a la vez?   | No, es secuencial (primero imágenes, luego artículos, luego publicar) |

---

**¡Listo para empezar! Lee GUIA_GOOGLE_COLAB.md primero.** 🚀

---

Última actualización: 15 ago 2026
