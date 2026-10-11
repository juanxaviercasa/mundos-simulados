# Auditoría de frontend — 11 de octubre de 2026

## Dictamen

La identidad de Mundos Simulados es adecuada para un blog de escenarios científicos y especulativos: tiene personalidad, categorías reconocibles y un catálogo amplio. La presentación anterior daba demasiado protagonismo al efecto visual y a afirmaciones de rigor no demostradas. Un blog profesional necesita que lectura, confianza editorial y navegación tengan la misma prioridad que la portada. No se puede certificar calidad mundial ni capacidad de monetización solo por su apariencia.

La estructura local ya permite conducir tráfico con intención hacia Nube para Pymes y Todo Lima. Eso todavía no demuestra conversiones: los destinos comerciales públicos y la medición deben completar el recorrido.

## Cambios realizados en local

- Restaurado el control claro/oscuro en las cabeceras de escritorio y móvil de 246 páginas exportadas. La exportación carecía del botón y `dark-branding.css` imponía colores oscuros mediante reglas `!important`. El nuevo control respeta inicialmente la preferencia del sistema, conserva la elección al navegar y permite uso con teclado.
- Ajustada la paleta clara de tarjetas, formularios, artículos y barras laterales. La portada mantiene una cabecera ilustrada oscura como parte de su identidad.
- Mejorada la lectura de artículos: título separado de la imagen, menor altura de portada, longitud de línea acotada, espaciado legible y eliminación del desplazamiento y zoom al pasar el cursor sobre el artículo.
- Blog con últimas entradas, búsqueda, categorías, orden y carga progresiva. Los filtros se despliegan bajo demanda en móvil; los 234 artículos permanecen en el HTML. Barra lateral con entradas recientes, índice y navegación.
- Eliminado el pie duplicado de la portada, corregidos créditos y retiradas afirmaciones como un supuesto simulador cuántico activo o una garantía del 100 % de rigor científico.
- Sustituido el formulario de newsletter sin funcionamiento por una indicación honesta y acceso al blog. No se creó un servicio de suscripción.
- Añadidos accesos diferenciados en portada: herramientas de Nube, directorio de Todo Lima y revisión de ficha para propietarios. Tres artículos incorporan recursos prácticos relacionados con su asunto, separados de las fuentes científicas y con parámetros UTM.

## Recorrido entre los proyectos

| Origen e intención | Destino pertinente | Resultado a medir |
| --- | --- | --- |
| Mundos: curiosidad sobre tecnología y economía | Herramienta específica de Nube | Uso de herramienta y posterior consulta |
| Nube: resolver una tarea empresarial | Ficha de negocio o consulta digital en Todo Lima | Solicitud cualificada |
| Todo Lima: buscar un proveedor | Contacto con el negocio | Consulta real y contratación |
| Todo Lima: propietario que necesita digitalización | Nube para preparar requisitos y servicio digital | Propuesta aceptada e ingresos |

Conviene seleccionar enlaces por necesidad del lector, sin imponer enlaces recíprocos en cada artículo. En la revisión pública, `/auditoria` de Todo Lima mostraba la portada; la página comercial está preparada en las fuentes locales. Algunos artículos recientes de Nube tampoco mostraban aún los puentes presentes en su exportación local. Estos cambios requieren una publicación posterior autorizada.

## Prioridades pendientes

1. **Cerrar la conversión y atribución.** Confirmar que las páginas comerciales desplegadas expliquen servicio, destinatario y siguiente paso. Todo Lima envía `page_location` sin el query string en su implementación actual; revisar la conservación de UTM y registrar solicitud, propuesta y venta. Un clic de WhatsApp no acredita una conversación ni una venta.
2. **Consolidar el diseño.** El tema restaurado resuelve el problema inmediato sobre la exportación de Astra. A medio plazo, reunir colores y componentes en un sistema común y reducir reglas duplicadas, estilos en línea y sobrescrituras `!important`.
3. **Curar el descubrimiento editorial.** Crear páginas temáticas con selecciones y artículos relacionados por intención. Revisar la navegación heredada entre entradas y las recomendaciones comerciales antiguas; no todas sus afirmaciones sobre proveedores están verificadas.
4. **Continuar la mejora de rendimiento móvil.** Ya se ejecutó Lighthouse: el blog pasó de 50 a 74 en móvil y obtuvo 98 en escritorio, con CLS móvil de 0,004. No se obtuvieron datos de Core Web Vitals de visitantes. El catálogo completo sigue en HTML; evaluar paginación rastreable y reducir CSS heredado. Los resultados y condiciones están en `RENDIMIENTO_FRONTEND_2026-10-11.md`.
5. **Hacer visibles responsabilidades editoriales.** Mantener metodología, autoría, fechas, fuentes y distinción entre hipótesis y evidencia. Las once revisiones editoriales son borradores asistidos por IA; no validan científicamente los otros 223 artículos.
6. **Activar funciones solo cuando existan.** Suscripción, comentarios y formularios necesitan un servicio real, respuesta al usuario y pruebas de envío. La monetización debe acompañar la intención del contenido sin ocupar el espacio principal de lectura.

## Verificación y límites

Se comprobó en navegador el cambio de tema, persistencia entre páginas y recarga, activación con Enter, menú móvil, búsqueda y restablecimiento de filtros. En anchuras de 320 y 360 píxeles el botón cabe en la cabecera y no se observó desbordamiento horizontal en la página comprobada. Se guardaron capturas de escritorio en ambos modos y de móvil en claro. Esto no constituye una auditoría completa de accesibilidad de las 246 páginas.

Referencias para una revisión de accesibilidad completa: [contraste de texto WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) y [reflujo a 320 píxeles CSS](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html). Falta medir el contraste de todos los estados y componentes, además de revisar lectores de pantalla y formularios.

Capturas locales: `blog-modo-claro.png`, `blog-modo-oscuro.png` y `blog-movil-claro.png`. Informes complementarios: `AUDITORIA_ECOSISTEMA_2026-10-11.md` y `REVISION_EDITORIAL_2026-10-11.md`.

Esta auditoría documentó inicialmente cambios sin publicar. Después, el propietario autorizó el commit y push de la revisión terminada, manteniendo fuera la medición comercial. Las automatizaciones remotas preexistentes siguen activas. La entrega actual está documentada en `RENDIMIENTO_FRONTEND_2026-10-11.md`.
