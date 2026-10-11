# Reparación de exportaciones — 11 de octubre de 2026

Se restauraron 130 artículos cuyo HTML era una respuesta 429 de Pantheon, incluidos los siete detectados en la auditoría del ecosistema. Se usaron exclusivamente sus Markdown existentes en la versión publicada del repositorio; no se consumieron borradores ni se publicaron revisiones editoriales locales pendientes.

El exportador ahora rechaza respuestas HTTP de error mediante curl --fail y documentos HTML de error 429/502/503/504 aunque el servidor responda HTTP 200. El publicador comprueba y recupera exportaciones 429 del catálogo antes de consumir nuevos borradores. La identidad del artículo, canonical, imagen y metadatos se reconstruyen desde su fuente.

Validación: nueve pruebas automáticas; 130 cuerpos con contenido y canonical correcto; 379 referencias de imágenes locales existentes; siete artículos en Chrome a 390 y 1366 píxeles, sin imágenes rotas ni desbordamiento horizontal. Restaurar el contenido no equivale a validar científicamente todas sus afirmaciones.

Artículos recuperados registrados en recovered-exports.json. El historial de Git conserva las exportaciones anteriores.
