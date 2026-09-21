# Mundos Simulados — pipeline CSV → Gemini (API gratis) → borradores en WordPress

Flujo automático, sin copiar y pegar, sin costo. Usa la capa gratuita de la
API de Gemini (modelos Flash), que es un medidor totalmente separado de tu
suscripción Gemini Pro del chat: esto no te consume tus 100 prompts/día de
Pro.

```
00_mapa_imagenes.py       → lee tu biblioteca de medios de WordPress y
                             arma media_map.json

01_generar_articulos.py   → lee el CSV, llama a Gemini (Flash, gratis),
                             escribe un .md por artículo en articulos/

02_publicar_wordpress.py  → resuelve categoría/etiquetas, inserta las tres
                             imágenes ya subidas, envía el post como
                             borrador
```

## 1. Instalar dependencias

```bash
pip install google-generativeai python-frontmatter markdown requests pandas python-dotenv --break-system-packages
```

## 2. Conseguir tu API key gratuita

Entra a https://aistudio.google.com con tu cuenta de Google (la misma o
distinta a la de tu suscripción Pro, da igual) y crea una API key. No pide
tarjeta. En esa misma consola revisa dos cosas antes de seguir:

- **Qué modelo Flash** está en capa gratuita para tu cuenta ahora mismo
  (puede que ya no se llame `gemini-2.5-flash` para cuando leas esto).
- **Tu límite de peticiones por minuto y por día.** En agosto de 2026
  rondaba entre 5 y 15 por minuto y hasta 1.000 al día, suficiente de sobra
  para los 240 artículos en una sola corrida, pero confírmalo tú.

## 3. Crear tu archivo `.env`

Copia `.env.ejemplo` a `.env` y completa `GEMINI_API_KEY`, `GEMINI_MODEL` y
los tres datos de WordPress. La contraseña de WordPress no es tu contraseña
normal: se genera en Perfil → Contraseñas de aplicación.

## 4. Instalar el mu-plugin de campos SEO (una sola vez)

Sube `mu-plugin-campos-seo.php` a `wp-content/mu-plugins/` de tu sitio
(créala si no existe). Sin esto, el título y la descripción SEO se publican
pero no se guardan en Rank Math.

## 5. Correr el mapa de imágenes (una sola vez)

```bash
python3 00_mapa_imagenes.py
```

Te dice cuántas de las 720 imágenes esperadas encontró en tu biblioteca de
medios y cuáles faltan. Corrige eso antes de seguir: un artículo sin sus
tres imágenes no se publica.

## 6. Generar un lote de prueba

```bash
python3 01_generar_articulos.py --limite 5 --categoria tecnologia
```

Abre los `.md` en `articulos/` y léelos. Si el tono no te convence, ajusta
`prompt_maestro_articulo.txt`, borra esos 5 archivos y corre el mismo
comando de nuevo. Recién cuando estés conforme, corre sin `--limite` para
las 240 filas.

Si en algún momento ves en pantalla "límite de la capa gratuita alcanzado",
el script ya lo maneja solo: espera y reintenta. Si pasa muy seguido, sube
el valor de `--pausa` (por defecto 4 segundos entre artículos).

## 7. Publicar ese mismo lote, primero en seco

```bash
python3 02_publicar_wordpress.py --limite 5 --seco
```

`--seco` arma el post completo y lo imprime, pero no lo envía. Revisa que
las tres imágenes, la categoría y las etiquetas sean correctas. Cuando estés
conforme, quita `--seco` para publicar de verdad como borrador.

## 8. Escalar

```bash
python3 01_generar_articulos.py
python3 02_publicar_wordpress.py
```

Sin `--limite`, cada script recorre las 240 filas, saltando las que ya
tienen su `.md` o ya están publicadas. Revisa `generacion_log.csv` y
`publicacion_log.csv` al terminar: ahí quedan los que fallaron y por qué.

## Notas

- No publiques los 240 el mismo día. Todos quedan en borrador — prográmalos
  desde WordPress a razón de 3 a 5 diarios.
- Si cambias algo en el CSV después de generar un artículo, borra su `.md`
  en `articulos/` para que se regenere.
- Flash escribe algo menos matizado que Pro. Si algún artículo puntual te
  queda flojo, puedes regenerar solo ese con `--forzar --limite 1` después
  de ajustar su fila en el CSV, o escribirlo a mano en el chat Pro y
  guardarlo directo como `.md` en `articulos/` con el mismo formato: para
  `02_publicar_wordpress.py` da igual de dónde salió.

## Si algún día quieres volver al copy-paste con Gemini Pro

`01a_generar_prompt_lote.py` y `01b_importar_lote.py` siguen en esta carpeta
y no dependen de ninguna API. Arman el mismo tipo de `.md`, así que puedes
mezclar: unos artículos generados por Flash automático, otros pegados a mano
desde el chat Pro, y `02_publicar_wordpress.py` los publica a todos igual.
