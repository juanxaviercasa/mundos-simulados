# Auditoría de Mundos Simulados — 11 de octubre de 2026

## Dictamen

El proyecto tiene identidad visual y una temática con potencial, pero todavía no alcanza el rigor editorial ni la consistencia técnica de una publicación científica profesional. Las publicaciones automáticas funcionan; el problema es que el éxito de GitHub Actions valida la ejecución del script, no la calidad de las afirmaciones ni la coherencia del SEO.

El dominio observado en el navegador es **https://mundossimulados.online**, con dos letras «s» consecutivas entre «mundos» y «simulados». El dominio escrito en el mensaje fue `mundosimulados.online`. No se confirmó que ambos dominios estén configurados. El README usa también el dominio con dos «s».

## Evidencia de automatización

La página pública de [GitHub Actions](https://github.com/juanxaviercasa/mundos-simulados/actions) muestra 155 ejecuciones en el momento de la revisión. Se comprobaron:

- [Publicación programada #58](https://github.com/juanxaviercasa/mundos-simulados/actions/runs/38101942943): completada correctamente, 10 de octubre de 2026, 20:28 hora de Perú.
- [Despliegue en GitHub Pages #78](https://github.com/juanxaviercasa/mundos-simulados/actions/runs/38101956352): completado correctamente después de la publicación.
- [Generador con IA #19](https://github.com/juanxaviercasa/mundos-simulados/actions/runs/38049514260): completado correctamente, 10 de octubre, 06:45 hora de Perú. Este resultado no demuestra que haya generado contenido nuevo; no se inspeccionaron sus logs autenticados.

Configuración local:

| Flujo | Programación nominal en Perú | Qué hace realmente |
|---|---|---|
| `generar_articulos_ia.yml` | 01:00 diaria | Genera Markdown en `articulos/`; opcionalmente crea borradores en WordPress/Pantheon. |
| `publicar_diario.yml` | 08:00, 13:00 y 18:00 | Toma un archivo de `borradores/`, genera HTML estático, actualiza el índice y elimina ese borrador; hace commit y push. |
| `pages-build-deployment` | Después de los cambios | Se observaron ejecuciones exitosas de GitHub Pages. No se inspeccionó la configuración DNS/Cloudflare del dominio. |

Los horarios son nominales: GitHub puede retrasar los trabajos programados. La muestra observada registra retrasos de horas. El flujo llamado «Publicar Artículos en WordPress» en realidad publica HTML estático; se renombró localmente para evitar esa confusión.

**Los dos flujos editoriales no están conectados de extremo a extremo.** El generador guarda en `articulos/` y WordPress; el publicador consume `borradores/`. No existe un paso en esos workflows que convierta automáticamente los nuevos borradores de WordPress en archivos de `borradores/`. Existe el script `05_extraer_borradores.py`, pero no aparece en los workflows revisados.

La copia local tenía 231 artículos en `search-index.json` y 10 borradores al iniciar. El catálogo público muestra 234 artículos: las tres publicaciones adicionales son «Redes neuronales planetarias», «Salario emocional» y «Semana de dos días». **Antes de desplegar las mejoras locales hay que integrar la versión remota más reciente para conservar esas publicaciones.** No se hizo push ni despliegue en esta sesión.

## Defectos comprobados

| Prioridad | Hallazgo | Efecto |
|---|---|---|
| Crítica | 130 archivos locales de artículos eran documentos de error «429 Too Many Requests». Se confirmó la misma página de error en la URL pública de «Sol desaparece». | El índice contabiliza artículos cuyo contenido no está disponible. Se recuperaron localmente desde sus Markdown existentes, sin generar texto nuevo. |
| Crítica | El JSON-LD de artículos automáticos conserva el titular, URL, fecha e imagen de «Piel camaleónica». Se comprobó incluso en «Semana de dos días» en producción. | El contenido visible y los datos estructurados describen páginas diferentes. |
| Alta | El blog público sigue encabezado por entradas del 20 de septiembre, aunque el catálogo tiene publicaciones de octubre. | Las novedades se publican sin aparecer en el listado principal del blog. |
| Alta | Fechas visibles, Twitter image y otros metadatos quedan heredados de la plantilla. | Presentación y señales de actualización incoherentes. |
| Alta | Las fuentes enlazadas suelen ser portadas de instituciones o Wikipedia sobre temas generales. | No permiten rastrear las cifras y afirmaciones concretas. |
| Alta | Los índices de artículos enlazan a Pantheon con `?p=.../#...`. | El lector sale del dominio para navegar por el mismo artículo. |
| Alta | No hay un control editorial verificable antes de consumir un borrador. | Un artículo sin fuentes específicas puede publicarse automáticamente. |
| Media | La barra lateral existe, pero muestra «Últimas entradas» de septiembre y un buscador WordPress `?s=`. | No corresponde a un sitio estático actualizado. |
| Media | `robots.txt` anunciaba el sitemap de Pantheon. | Señal técnica equivocada para el dominio público. |
| Media | Portada con números diferentes: 234 en el encabezado, 212 en el panel y 241 modelados; pie de página duplicado. | Reduce la confianza y deja visible el ensamblaje de plantillas. |
| Media | Contacto `contacto@mundossimulados.onine`. | El dominio del correo parece tener un error; confirmar una dirección real antes de cambiarla. |
| Media | Promesas como «100% Ciencia & Datos Reales» y «modelados con ecuaciones» superan lo que demuestra la muestra. | Conviene ajustarlas a «experimentos mentales» y mostrar cálculos reales cuando existan. |

## Revisión de las publicaciones recientes

Se leyó la muestra de ocho artículos más recientes disponibles localmente y las tres novedades presentes solo en producción. No equivale a una comprobación exhaustiva de cada afirmación de todo el catálogo.

| Artículo | Evidencia y diagnóstico |
|---|---|
| Semana de dos días | Enlaza a la portada del Banco Mundial, pero cita cifras de la OCDE sin enlazar la serie. Declara la premisa «físicamente imposible» por termodinámica sin demostrarlo. Afirma demanda turística multiplicada por cinco y depresión clínica masiva sin respaldo específico. Tiene un H2 con «the turismo». No está listo para presentarse como análisis científico riguroso. |
| Salario emocional en realidad virtual | Cita una masa salarial mundial superior a cincuenta billones de dólares sin identificar fuente, año ni método. La referencia final es Wikipedia sobre criptomoneda. Introduce abolición del dinero, avances hápticos y estimulación neural, de modo que cambia varias variables. Las consecuencias necesitan marcarse como ficción especulativa y separar evidencia económica de neurología. |
| Redes neuronales planetarias | Advierte correctamente que la conciencia espontánea es especulativa, pero luego asegura latencia inferior a diez milisegundos entre cualquier punto del planeta: contradice las limitaciones de propagación a escala terrestre. Cita «500 billones» de organismos y «34 mil millones» de dispositivos sin fuentes rastreables. Enlaza Wikipedia sobre ciberseguridad. |
| Virus antiguos del permafrost | Unas 1029 palabras de texto extraído, contando índice y enlaces. Advierte sobre la especulación, pero pasa a describir infección humana por virus gigantes, fallo multiorgánico y falta absoluta de defensas como certezas. La referencia final es Wikipedia sobre evolución. El estudio primario de 2023 documenta virus reactivados que infectan amebas; no demuestra ese escenario humano. |
| Semillas extraterrestres | Unas 1372 palabras; referencia genérica a evolución. La plausibilidad y los mecanismos biológicos deben distinguirse de la narrativa hipotética. |
| Silencio móvil | Unas 1207 palabras; referencia genérica a ciberseguridad para afirmaciones biológicas. |
| Universo holográfico | Unas 1085 palabras; enlaza la portada de NASA Science. El titular «Las pruebas» y la afirmación sobre longitud mínima medible necesitan revisión física y una fuente concreta. |
| Auroras urbanas letales | Unas 1012 palabras; portada de NASA Science. Hay que separar auroras, radiación espacial y efectos sobre infraestructura. |
| Ropa inteligente | Unas 1097 palabras; Wikipedia sobre inteligencia artificial. Revisar unidades: el texto habla de resistencia y utiliza microsiemens, unidad de conductancia. |
| Planeta anclado por marea | Unas 965 palabras; portada de NASA Science. Necesita estudios específicos y supuestos climáticos definidos. |
| Salario universal | Unas 968 palabras; portada del Foro Económico Mundial. Falta precisar financiación, país/modelo y evidencia. |

El prompt exige 1400–1900 palabras, pero la muestra local no cumple el mínimo de forma consistente. **Esto es una desviación del contrato editorial del proyecto, no una regla de Google:** la calidad no depende de llegar a una cantidad fija de palabras.

Estudio primario para revisar el artículo del permafrost: [An Update on Eukaryotic Viruses Revived from Ancient Permafrost](https://www.mdpi.com/1999-4915/15/2/564).

## SEO, GEO y AEO

No basta con añadir keywords, FAQ, un archivo `llms.txt` o permitir bots. Para Google, la visibilidad en respuestas generativas sigue dependiendo del SEO básico, contenido útil y confiable, rastreabilidad y experiencia de página. No se puede prometer posicionamiento ni citas de motores de IA. Véase la [guía oficial de optimización para IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?hl=es-419).

La muestra tiene H1, descripción, imágenes y H2, pero falla en la trazabilidad de las fuentes y en la correspondencia entre schema y texto. Para preguntas que un lector haría a un buscador o asistente, conviene añadir una respuesta breve y precisa al inicio, desarrollar evidencia y límites, y responder preguntas relevantes al final solo cuando aporten valor. No debe añadirse una FAQ mecánica a cada artículo. Google anunció la retirada de los resultados enriquecidos FAQ en mayo de 2026: [registro oficial](https://developers.google.com/search/updates?hl=en).

Contrato editorial recomendado antes de publicar:

1. Definir la pregunta, el supuesto alterado y los supuestos constantes.
2. Separar explícitamente hecho observado, estimación, extrapolación e hipótesis narrativa.
3. Enlazar fuentes primarias específicas junto a las afirmaciones: artículo, conjunto de datos, documento técnico o serie, con fecha y unidades. Dos o tres fuentes relevantes pueden ser una pauta interna; la pertinencia importa más que el número.
4. Revisar matemáticas, unidades y restricciones físicas; evitar cifras sin fuente y consecuencias universales sobre salud o conducta.
5. Incluir autor y revisión editorial real; explicar el uso de IA cuando corresponda, sin inventar un revisor experto.
6. Comprobar título, descripción, canonical, imagen, fecha y schema del artículo actual, enlaces internos y texto alternativo.
7. Publicar únicamente contenido con aprobación editorial registrada. Un validador automático puede detectar problemas formales, pero no certificar verdad científica.

Google recomienda contenido creado para ayudar al lector y supervisión editorial de la automatización: [contenido útil y confiable](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).

## Cambios preparados localmente

- Nuevo listado estático del blog, ordenado por fecha, con los 231 artículos locales disponibles también sin JavaScript.
- Recuperación de 130 exportaciones dañadas desde `articulos/*.md` existentes, con imágenes internas y destacadas, sin consumir borradores ni redactar contenido adicional.
- Búsqueda que ignora acentos, filtro de temática, fecha inicial, orden reciente/antiguo, carga incremental de 12 tarjetas, contador y estado sin resultados.
- Barra lateral renovada en los artículos: búsqueda funcional hacia el blog, índice del contenido, últimas entradas, categorías y acceso al autor.
- Canonical absoluto de artículos; schema reconstruido cuando se detecta la plantilla copiada; fecha visible y metadatos sociales corregidos en esos artículos.
- Índices a Pantheon convertidos en anclas locales cuando el identificador existe.
- Sitemap correcto en `robots.txt`.
- Integración de la reconstrucción editorial en `sincronizar_metricas.py`, para que las publicaciones futuras actualicen también blog y barras laterales.
- Protección del publicador contra slugs inválidos y republicación de entradas que ya existen en el índice. Orden determinista de selección de borradores.
- Eliminación del `git push || true` que ocultaba errores del generador y aclaración del nombre/horarios del workflow estático.

Estas mejoras no reescriben ni certifican científicamente los artículos. Tampoco conectan aún el generador de WordPress con la cola estática ni introducen aprobación editorial obligatoria.

## Diseño y monetización profesional

No hay un único «modelo de los mejores blogs». Para este nicho propongo una publicación editorial de ciencia con identidad propia: jerarquía tipográfica clara, ancho de lectura cómodo, portada con novedades y selecciones del editor, archivo navegable, referencias visibles y páginas de autor/metodología/correcciones. Mantener el universo visual oscuro es compatible con esa dirección; conviene reducir lenguaje grandilocuente y repetir menos componentes.

Referencias revisadas: [Scientific American](https://www.scientificamerican.com/) separa novedades, temas, autores/fechas, archivo y newsletter, y presenta una oferta de suscripción; [BBC Science Focus](https://www.sciencefocus.com/) sirve como referencia de divulgación accesible y preguntas del lector; [Quanta Magazine](https://www.quantamagazine.org/) como referencia de edición de ciencia y matemáticas. Son comparables editoriales, no una clasificación auditada de los blogs que más posicionan o ingresan: no se accedió a sus métricas privadas. Para Mundos Simulados tomaría la organización y claridad de esos medios, con un producto propio basado en experimentos mentales y modelos explicados.

La ventaja competitiva debería ser el contenido que otros blogs no ofrecen: cálculos explicados, pequeños modelos interactivos, gráficos propios y comparación entre hipótesis. El diseño debe ayudar a leer y comprobar las afirmaciones.

Antes de monetizar, medir sesiones orgánicas, artículos de entrada, lectura y retorno, suscripciones y conversiones. Revisar Search Console y analítica con acceso autorizado; no se tuvo acceso a esos datos ni a ingresos, por lo que no puede afirmarse rentabilidad ni posicionamiento actual.

Secuencia propuesta:

1. **Prioridad inmediata:** integrar cambios remotos, desplegar la recuperación de las 130 exportaciones dañadas y las correcciones de identidad SEO, actualizar listados y añadir revisión editorial previa.
2. **Después:** revisar las once entradas muestreadas, conectar la cola de generación/publicación con estados explícitos y mejorar categorías y portada.
3. **Crecimiento:** construir guías centrales y simulaciones útiles, newsletter funcional y políticas editoriales transparentes.
4. **Monetización:** probar patrocinios relevantes, recursos educativos o productos propios, y publicidad con espacios reservados cuando el tráfico lo justifique. Añadir afiliación solo donde ayude a elegir recursos y con divulgación clara. No llenar la barra lateral de publicidad antes de demostrar audiencia y confianza.

## Validación y límites

Cinco pruebas automatizadas verifican recuperación desde fuentes existentes, corrección de schema copiado, fechas/canonical, anclas locales, buscador estático, escapado de títulos y reconstrucción idempotente. La sintaxis JavaScript pasó `node --check`.

En el navegador se comprobaron filtros combinados, búsqueda sin acentos, carga de 12 a 24 tarjetas, orden antiguo primero y estado vacío; se inspeccionaron el blog y una barra lateral local. No se ejecutó el publicador sobre la cola real ni se consumieron borradores.

También se comprobó el diseño móvil sin desbordamiento horizontal y un artículo recuperado. La búsqueda final de `Too Many Requests` en los archivos `index.html` devolvió cero coincidencias, y `git diff --check` pasó. Vista previa guardada en `blog-preview.png`.

No se publicaron los cambios. La inspección del dominio se completó con el navegador, aunque las herramientas de terminal y búsqueda no pudieron resolver/acceder al dominio. La configuración de DNS, secretos de Actions, WordPress, Search Console y monetización permanece sin auditar.
# Actualización de la revisión local

El catálogo local contiene ahora 234 entradas. Se prepararon once revisiones editoriales como `reviewed_draft`, se restauró el selector claro/oscuro y se añadieron recorridos contextualizados entre los proyectos. Las seis pruebas editoriales pasan. Los detalles actuales están en `REVISION_EDITORIAL_2026-10-11.md`, `AUDITORIA_ECOSISTEMA_2026-10-11.md` y `AUDITORIA_FRONTEND_2026-10-11.md`. Esta revisión no se publicó; las automatizaciones remotas preexistentes continúan activas.
