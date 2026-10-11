# Correcciones de lectura y presentación

Se corrigió el recorte de las imágenes destacadas: contenedor 16:9, imagen completa con `object-fit: contain`, sin alturas máximas ni zoom al pasar el cursor. Las imágenes con otra proporción conservan su contenido y pueden dejar espacio dentro del contenedor.

Los artículos mantienen una sola superficie exterior. Se quitaron el borde, la sombra y el fondo del artículo y del encabezado interiores. Se tradujeron la tabla de contenidos y su texto auxiliar al español, también en el HTML estático.

Se mejoraron los enlaces del índice en ambos temas, los metadatos en oscuro y los placeholders en claro. El texto de lectura usa 17 px en escritorio y 16 px en móvil, sin sombras ni filtros. La generación editorial y el optimizador conservan estas correcciones para futuras publicaciones. Los recursos llevan una versión nueva para renovar la caché.

Validación: 10 pruebas automatizadas aprobadas. Verificación del catálogo: 234 artículos, 556 enlaces relacionados, sin imágenes locales faltantes. Inspección visual del artículo de la Luna en claro y oscuro; sin desbordamiento horizontal a 320 y 360 px. En escritorio, la imagen midió 758,4 × 426,6 px (16:9); artículo y encabezado interiores con borde 0 y sombra `none`.

Esta revisión valida la presentación y navegación; no certifica la exactitud científica de los 234 artículos ni constituye una auditoría completa de accesibilidad.

## Revisión global de superficies y contraste

Se retiraron los fondos, bordes, esquinas y sombras exteriores de Astra en las páginas, incluidos los artículos anidados de Sobre mí y Términos. La portada conserva su estructura, con la sección final abierta sobre el fondo de página. Los botones usan colores sólidos y el pie ya no proyecta una sombra negra.

Los bloques incrustados con fondos oscuros adoptan una superficie blanca en modo claro. Los textos sobre imágenes mantienen un color claro en ambos temas. Se corrigieron también el índice de Privacidad y los metadatos de las tarjetas de categorías en oscuro.

Se inspeccionaron portada, escenarios, cuatro categorías, blog, autor, Sobre mí, Privacidad, Términos y Contacto. La comprobación calculada de contraste de texto sobre fondos sólidos no encontró casos pendientes en las últimas observaciones de cada plantilla y tema. Las imágenes y los gradientes se revisaron visualmente y se excluyeron del cálculo automático. No equivale a una certificación de accesibilidad. Portada, escenarios, Sobre mí, Astrofísica, blog y contacto también se comprobaron a 360 px en ambos modos, sin desbordamiento horizontal.
