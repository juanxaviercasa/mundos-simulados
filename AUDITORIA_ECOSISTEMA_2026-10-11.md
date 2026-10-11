# Auditoría del ecosistema: Todo Lima, Nube para Pymes y Mundos Simulados

Revisión del 11 de octubre de 2026. Cambios exclusivamente locales; sin push, despliegue, publicación de entradas ni envío de formularios o mensajes. Se preservaron los cambios existentes en las otras carpetas y se guardaron respaldos de los ajustes de esta revisión.

## Dictamen

La integración encontrada es parcial. Hay enlaces reales y algunos encajan con la necesidad del lector. Eso todavía no demuestra un ecosistema autosustentable ni conversiones: varios recorridos publicados terminan en una portada, contienen promesas que la página de destino no respalda o no incluyen los recursos que ya existen localmente.

No se atribuye la autoría de cada cambio a Antigravity sin un historial que la confirme. Se evalúan el código encontrado, las exportaciones locales y una muestra concreta de páginas públicas.

## Evidencia pública observada

| Recorrido | Observación | Evaluación |
| --- | --- | --- |
| Nube → Todo Lima | En `punto-de-venta-restaurantes/` hay enlaces a pollerías, chifas y cevicherías | Útil para explorar oferta gastronómica; el dueño que quiere publicar necesita una ruta adicional hacia `/para-negocios` |
| Nube → Todo Lima / Mundos | La entrada `automatizacion-ia-pymes-criterios-decision/` no mostraba enlaces a estos dos dominios en la inspección | La integración preparada en `scripts/integrate_ecosystem.py` existe localmente, pero no aparece en esa versión pública |
| Todo Lima → Nube | El centro de herramientas enlaza a herramientas de Nube; las fuentes locales usaban rutas antiguas `.html` | Recorrido útil; se corrigieron localmente 16 enlaces a rutas canónicas y se añadieron parámetros de campaña |
| Todo Lima → Mundos | El artículo sobre museos contiene un enlace de lectura a la portada de Mundos | Es navegación complementaria, no una prueba científica ni un recorrido comercial; mejor elegir una lectura específica pertinente |
| Mundos → Todo Lima / Nube | La portada pública incluye ambos proyectos en el pie; fuentes locales contienen puentes a categorías de Todo Lima | Aporta descubrimiento, pero un enlace de pie no explica por sí solo la siguiente acción del lector |
| Consulta comercial en Todo Lima | Al visitar `https://todolima.com/auditoria`, el contenido observado fue la portada del directorio | El destino comercial esperado no estaba disponible en esa revisión pública; la página específica sí existe y compila localmente |

La inspección pública es una muestra, no un rastreo exhaustivo de los tres dominios. El JSON `editorial/ecosistema_inventario_2026-10-11.json` recoge enlaces de las exportaciones locales; sus recuentos incluyen duplicados de navegación y no representan clientes ni dominios referidores distintos.

## Base local que ya estaba preparada

En Nube, `scripts/integrate_ecosystem.py` distingue revisión de ficha y consulta digital; tiene 14 artículos seleccionados y tres lecturas temáticas hacia Mundos, además de rutas en inglés cuando existen. El ensamblador llama al integrador y al normalizador de créditos. No se reemplazó esta arquitectura ni se descartaron sus cambios pendientes.

En Todo Lima, `components/EcosystemResources.js` selecciona recursos según el artículo; `/auditoria` separa consulta digital de inclusión en el directorio. Este planteamiento es más claro que exigir que todos los artículos enlacen a los otros dos sitios. Su existencia local no equivale a despliegue.

En Mundos, `inyectar_puentes_todolima.py` contiene recomendaciones por tema. Algunas usan términos como «verificados», «colegiados» o certificaciones sin que la mera inclusión en Todo Lima lo pruebe. Deben revisarse contra evidencia de cada proveedor; no se certificó a negocios durante esta tarea.

## Cambios realizados

- Se actualizó el dominio de los créditos encontrados en fuentes y exportaciones de Mundos y Nube, y en `components/Footer.js` y `lib/contact.js` de Todo Lima, a **https://xavier.cabellosalirrosas.com**, exactamente como confirmó el propietario. Se conservó el nombre Xavier Cabello. No se cambió DNS ni se certificó la disponibilidad del dominio.
- En Todo Lima se sustituyeron 16 rutas antiguas de herramientas por rutas canónicas de Nube con `utm_source=todolima`, medio referral, campaña ecosistema y contenido específico.
- Se retiraron del banner heredado de Nube la promesa de publicar gratis y la garantía implícita de captar clientes. Su texto pide una revisión de ficha y aclara que la inclusión no garantiza consultas ni ventas. La corrección también está en el proceso que normaliza los banners al construir.
- En Mundos se añadieron tres bloques prácticos seleccionados: semana laboral, redes planetarias y apagón de internet. Enlazan a una herramienta pertinente de Nube y, para dueños de negocios en Lima, a la consulta digital de Todo Lima. Identifican que son proyectos del mismo autor y separan la recomendación comercial de la evidencia científica.
- La revisión editorial de las once entradas recientes se documentó aparte. No se alteró la cola editorial de Todo Lima ni se publicaron borradores.

Los respaldos están en `editorial/respaldo_ecosistema/`; `editorial/cambios_ecosistema_2026-10-11.json` identifica los archivos y hashes. Hay numerosas exportaciones duplicadas; el número de archivos modificados no equivale al número de funciones nuevas.

## Modelo comercial recomendado

| Sitio | Función | Siguiente paso útil | Resultado a medir |
| --- | --- | --- | --- |
| Mundos Simulados | Atraer lectores interesados en ciencia, tecnología y consecuencias sociales | Herramienta o guía concreta de Nube cuando el tema encaja; consulta digital solo si el lector tiene esa necesidad | Clic temático y posterior consulta cualificada |
| Nube para Pymes | Resolver tareas y preparar decisiones de software | Revisar ficha de negocio en Todo Lima o consultar implementación digital; Mundos como lectura complementaria | Uso de herramienta, solicitud de ficha y consulta digital |
| Todo Lima | Ayudar a elegir servicios locales y ofrecer un canal para negocios | Contactar proveedor, revisar ficha propia o consultar web/automatización; Nube ayuda a preparar requisitos | Contactos cualificados, propuestas aceptadas e ingresos |

La autosustentabilidad exige comparar ingresos cobrados con adquisición, producción editorial, mantenimiento y atención comercial. Un clic no es una venta. Conviene registrar fuente → destino → solicitud → propuesta → venta, distinguiendo consumidores del directorio y propietarios interesados en servicios digitales.

## Medición pendiente

Los parámetros UTM y los atributos de eventos ya presentes son una base, no una medición completa. En Todo Lima, `SiteEnhancements.js` envía `page_location` con dominio y pathname, dejando fuera el query string; eso debe revisarse antes de asumir que todas las campañas UTM se conservan. No se inspeccionaron una propiedad de Analytics, CRM, ingresos ni atribución real. El evento de WhatsApp mide un clic, no una conversación enviada ni una contratación.

El enlazado debe responder a la intención del lector. Google considera problemáticos los intercambios excesivos destinados a manipular rankings y las páginas creadas solo para cruzar enlaces; no hay motivo para forzar los seis recorridos en todos los artículos. Referencia: [políticas de spam de Google Search](https://developers.google.com/search/docs/essentials/spam-policies). Los vínculos pagados o de afiliación requieren su identificación correspondiente; aquí no se asumió que los tres proyectos se paguen entre sí.

## Publicación gradual de Todo Lima

El blog público mostraba **tres artículos**. Las fuentes de la configuración de Actions programan un artículo por ejecución en tres turnos: 08:00, 14:00 y 20:00 de Lima. Eso corresponde a tres por día si los trabajos se ejecutan y terminan correctamente, no a tres en cada turno. El comando manual permite otra cantidad. No se ejecutó el publicador, no se modificó el ritmo y no se consumió la cola de 180 artículos preparados. Los tres públicos incluyen entradas de fechas distintas: no debe interpretarse el total actual como tres publicaciones nuevas realizadas hoy.

## Validación

Todo Lima compiló correctamente: 375 rutas estáticas, incluidas las tres entradas publicadas en sus datos. Nube pasó la verificación de producción, 5.673 comprobaciones de localización y el inventario de 610 HTML con 24.974 enlaces internos sin destinos faltantes. La última fase de `npm test` encontró el alias de Python de Microsoft Store; se completó por separado con Python 3.12 instalado. Mundos pasó seis pruebas del generador editorial, incluida la actualización de schema conservando la fecha original de publicación.

Pendiente para una futura publicación autorizada: revisar los textos e imágenes locales, comprobar destinos comerciales en el despliegue, terminar la atribución de consultas y evaluar conversiones con datos reales. Las automatizaciones remotas preexistentes siguen activas: no publicar esta revisión no las desactiva.
