# Rendimiento y cierre de frontend — 11 de octubre de 2026

El propietario autorizó completar las mejoras y enviar los cambios a los repositorios. Se dejó fuera la integración de medición de clics, consultas y ventas.

## Mediciones reales de laboratorio

Lighthouse 13.5.0 con Chrome, sobre la exportación servida en localhost. Las pruebas móviles utilizan la configuración móvil predeterminada y las de escritorio `--preset=desktop`. El servidor Python no comprime ni configura caché de producción: los resultados no equivalen al rendimiento del CDN ni a Core Web Vitals de visitantes. No se afirma cumplimiento de todas las métricas móviles.

| Página / ejecución | Rendimiento | FCP | LCP | CLS | Transferencia |
| --- | ---: | ---: | ---: | ---: | ---: |
| Blog móvil antes | 50 | 5,25 s | 7,14 s | 0,246 | 1,83 MiB |
| Blog móvil terminado, repetición | 74 | 3,17 s | 5,28 s | 0,004 | 0,86 MiB |
| Blog escritorio terminado | 98 | 0,65 s | 1,02 s | 0,005 | 1,00 MiB |
| Portada móvil antes de optimizar sus recursos | 66 | 2,90 s | 8,05 s | 0,004 | 1,41 MiB |
| Portada móvil terminada | 74 | 2,41 s | 5,34 s | 0,017 | 0,78 MiB |
| Artículo móvil terminado: semana laboral | 76 | 2,72 s | 5,42 s | 0,004 | 0,77 MiB |
| Blog móvil en producción: mundossimulados.online | 88 | 2,12 s | 3,32 s | 0 | 0,44 MiB |

La repetición del blog móvil mantuvo 74 puntos; la ejecución anterior terminada también dio 74. Los valores son ejecuciones individuales, no percentiles de una población. Los JSON completos están en `artifacts/` como resultados locales; el resumen transportable está en `editorial/rendimiento_2026-10-11.json`.

Después del push se midió también el dominio público con Lighthouse móvil: 88 puntos, bloqueo de hilo principal de 0 ms, CLS de 0 y ninguna solicitud fallida. El navegador mostró el catálogo y el selector de tema actualizados. Esta ejecución verifica la entrega real por la red y el CDN, pero sigue siendo una medición de laboratorio, no una medición de visitantes.

## Mejoras comprobadas

- Miniaturas WebP para el listado y las imágenes secundarias de portada, conservando originales. La primera tarjeta usa carga inmediata y prioridad alta; las restantes carga diferida.
- Tipografía del sistema para evitar la cadena de descarga de Google Fonts y cambios tardíos de dimensiones.
- Carga diferida de los scripts exportados, excepto el pequeño selector de tema que aplica la preferencia antes de pintar.
- Eliminación del complemento de índice de contenido en el blog, donde no se utiliza.
- Estado inicial estable de tarjetas y filtros móviles. La búsqueda y carga progresiva conservan el catálogo completo rastreable.
- Eliminación de scripts de desafío y emoji caducados que quedaron copiados en el HTML exportado. No se modificó la configuración de seguridad de Cloudflare. Las pruebas finales del blog y portada no registraron solicitudes 404.
- Retirada del contador animado que descargaba el catálogo para mostrar una cifra ya generada en HTML; precarga de la imagen principal de portada.
- Versionado de recursos para que el navegador reciba el selector, filtros y estilos actualizados.

## Curación y funciones

Cada artículo dispone de navegación de lecturas relacionadas. Doce escenarios tienen selecciones explícitas; el resto usa coincidencias de tema dentro de su categoría, con ponderación de términos. Se excluyen la propia entrada y destinos inexistentes. Cuando no hay coincidencia útil, se ofrece el catálogo de la categoría en lugar de rellenar con artículos arbitrarios. Esto cura la navegación; no certifica la evidencia científica de los 234 artículos.

Se retiró la navegación heredada entre entradas y el formulario estático de comentarios que no tenía un servicio local. Ahora se ofrece un contacto editorial y se indica que los comentarios públicos no están habilitados. Los puentes antiguos a Todo Lima explican su carácter comercial y no aseguran que cada proveedor esté verificado o autorizado por una entidad. Sus bloques Markdown también se normalizaron para futuras exportaciones.

La página comercial de Todo Lima se completó con un contacto visible en cabecera, proceso en tres pasos, posibles entregables, condiciones y preguntas frecuentes. Se verificaron el HTML exportado, el canonical `/auditoria`, los enlaces de WhatsApp y la página 404 estática. La exportación de Next incluye la ruta como `auditoria.html`; Cloudflare Pages sirve la URL sin extensión de forma nativa: [documentación de entrega de Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/). La comprobación local no demuestra por sí sola que un despliegue remoto terminó.

## Límite que sigue visible

El LCP móvil local permanece alrededor de 5,3 segundos; en la ejecución sobre producción fue de 3,32 segundos. La siguiente mejora estructural sería reducir el HTML y CSS heredados de WordPress y evaluar paginación rastreable del catálogo. No se ocultó ese resultado ni se sustituyó por una puntuación de escritorio. No se añadió analítica ni seguimiento comercial.

Las copias originales y respaldos voluminosos permanecen locales y se excluyen del commit. Se preservan también las ediciones institucionales de otras tareas que están en curso en los proyectos vecinos.

## Validación final

El catálogo pasó la comprobación de 234 artículos, 556 enlaces relacionados, canonical, índices con anclas válidas, barras laterales y recursos de tema, sin imágenes locales faltantes. Pasaron ocho pruebas editoriales y temáticas, las comprobaciones de sintaxis de JavaScript y el control de espacios del diff. En navegador móvil se probaron búsqueda «virus» (tres resultados), restablecimiento (234, doce visibles), carga de doce a veinticuatro, cambio de tema y ausencia de desbordamiento horizontal a 360 píxeles.

Todo Lima compiló y su página comercial exportada pasó las comprobaciones de proceso, preguntas, canonical y contacto. Nube pasó 5.673 comprobaciones de localización, 33 recorridos del ecosistema y una auditoría de 610 HTML con 24.995 enlaces internos sin destinos faltantes. Un bloqueo de escritura en Windows se resolvió con sustitución atómica y reintentos. Las fases finales de Nube se validaron con la configuración institucional confirmada en HEAD, conservando fuera las páginas nuevas de otra tarea que todavía estaban incompletas.
