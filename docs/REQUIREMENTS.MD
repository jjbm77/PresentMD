# PresentMD — Documento de Funcionalidades del Sistema
**Versión 1.0 (Release Candidate) · Mayo 2026**
*Sistema de presentaciones profesionales generado desde texto plano (Markdown / YAML)*

**Filosofía de diseño:** 80% contenido, 20% impacto visual. El usuario no toma decisiones de micro-posicionamiento; escribe la estructura lógica y el motor renderiza una presentación técnica impecable, dinámica y lista para producción.

---

## 01 · Autoría — Escritura del contenido

* **Formato de entrada estandarizado:** El sistema utilizará exclusivamente **Markdown enriquecido** con una capa de metadatos YAML al inicio (frontmatter). Esto minimiza la curva de aprendizaje y permite usar editores estándar. Las diapositivas se separan con `---`.
* **Directivas explícitas de Layout:** Para evitar errores de inferencia automática, el autor puede forzar la estructura visual con etiquetas semánticas directamente en el texto: `::layout{split-50-50}` o `::layout{hero-diagram}`.
* **Bloques de Código Paso a Paso (Code Stepping):** Soporte avanzado para bloques de código con resaltado de sintaxis. Capacidad de iluminar líneas específicas al avanzar la diapositiva (ej. ````sql {1, 4-5}`), ideal para explicar modelos de datos o scripts de migración línea por línea.
* **Diagramas y flujos nativos:** Integración profunda con **D2 y Mermaid**. No se desarrollará sintaxis propia. El motor inyectará automáticamente los estilos, fuentes y colores del tema activo para que diagramas complejos (como la lógica de un Ciclo Ancla aplicado a un RUT completo o arquitecturas de sistemas transaccionales) se vean consistentes y corporativos.
* **Jerarquía y aserciones:** Soporte para H1 (títulos), listas con viñetas, y blockquotes renderizados como "citas de impacto".
* **Gestión de notas:** Bloques `notes:` ocultos para el presentador, visibles en la vista de orador o exportación de lectura.

## 02 · Sistema visual — Temas y diseño

* **Biblioteca de temas curados (Top 20):** Se incluirá un conjunto cerrado de estilos profesionales (ej. *Executive Dark*, *Tech Forward*, *Data Driven*). Estos definen tipografía, paleta, bordes y animaciones globales.
* **Layouts Semánticos Estrictos:** * *Contenido con bullets:* Jerarquizado visualmente.
    * *Dos columnas:* Simétrica o asimétrica.
    * *Métricas y números clave:* KPIs en cuadrícula (número grande + descripción).
    * *Diagrama Central:* Contenedor limpio sin ruido visual.
* **Personalización corporativa controlada:** Se permite configurar en el YAML inicial un color de acento (`accent: '#hex'`), logotipo y texto para el pie de página, adaptando el tema sin romper el diseño curado.

## 03 · Navegación y estructura dinámica

* **Menú y TOC automáticos:** El sistema genera un menú lateral dinámico y una tabla de contenidos interactiva basados en los H1 y H2 del documento.
* **Indicadores visuales:** Numeración relativa de sección e indicador de progreso visual en el marco del slide.
* **Navegación no lineal:** Menús colapsables para saltar entre secciones, facilitando respuestas rápidas en sesiones de Q&A.

## 04 · Motor de generación — Pipeline y escalado

* **Renderizado HAML / HTML Vectorial:** Output primario en HTML/CSS responsivo. Escalado perfecto a cualquier resolución.
* **Auto-escalado inteligente:** Si el contenido excede el layout, el sistema ajusta la tipografía o advierte mediante logs, redistribuyendo imágenes inteligentemente (sin estirar) y adaptando los gráficos.
* **Live Preview (Recarga en caliente):** Servidor local ultra-ligero que refresca el navegador en milisegundos al guardar el archivo `.md`, manteniendo la diapositiva actual activa.

## 05 · Exportación multi-formato

* **HTML/Web (P0):** Formato nativo interactivo con animaciones y transiciones. Empaquetado automático de imágenes en base64 para envío rápido (cero enlaces rotos).
* **PDF Píxel-Perfect (P0):** Exportación de alta resolución. Integra impresión silenciosa preservando diagramas vectoriales y el estilo exacto.
* **PowerPoint / PPTX (P2):** *Restricción arquitectónica:* Generará un PPTX empaquetando cada diapositiva renderizada como una imagen estática de altísima calidad, priorizando la fidelidad visual absoluta por sobre la edición de objetos individuales.
* **Modo Documento Técnico:** Compilación secundaria que transforma el Markdown y sus notas en un documento de lectura (Handout) formato artículo.

## 06 · Sistema de plugins e integraciones de datos

* **API y Data Connectors en tiempo de compilación:** Capacidad de definir scripts simples o conectores REST en el YAML para consultar datos externos. Los datos se inyectan en tablas o gráficos de ECharts durante el comando `build`.
* **Componentes MDX (Snippets):** En lugar de macros complejas, uso de componentes semánticos reusables para insertar alertas, arquitecturas pre-guardadas o tablas de estado.

## 07 · Modo presentación y experiencia

* **Vista de presentador:** Pantalla dividida con cronómetro, notas de orador, y miniatura de la lámina siguiente.
* **Controles y Puntero:** Atajos estándar de teclado, soporte para pasadores inalámbricos y un láser pointer integrado activable con el mouse.
* **Dark/Light Toggle de Sala:** Cambio rápido de tema claro a oscuro para adaptarse a las condiciones de luz del proyector o pantalla.

## 08 · Integración con herramientas del ecosistema TI

* **CLI Binario Autocontenido:** Distribución mediante un ejecutable nativo limpio (`presentmd`) que no requiera lidiar con dependencias de Python complejas, funcionando *out-of-the-box* en entornos Linux, macOS y Windows.
* **Comandos Core:**
    * `presentmd serve archivo.md`: Levanta el Live Preview.
    * `presentmd build archivo.md -f pdf`: Genera exportación final.
* **Git-Friendly:** Al ser 100% texto plano, los diffs de revisión de presentaciones son limpios y perfectos para trabajar en repositorios corporativos.