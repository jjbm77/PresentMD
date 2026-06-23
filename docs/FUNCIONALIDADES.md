# Lista de Funcionalidades de PresentMD

PresentMD soporta un conjunto robusto de funcionalidades diseñadas para crear presentaciones técnicas avanzadas usando Markdown. 

A continuación se listan las funcionalidades actuales del sistema. Para aprender a utilizarlas y ver ejemplos de sintaxis, consulta la [Guía de Autoría (AUTHORING_GUIDE.md)](./AUTHORING_GUIDE.md).

## 1. Estructura y Configuración
- **Frontmatter YAML**: Configuración por presentación (tema, acentos, logo, opciones de navegación y animaciones).
- **Separación de Slides**: División de contenido usando separadores estándar (`---`).
- **Layouts Custom (`::layout`)**: Plantillas forzadas por slide (título, estándar, scrollable, comparativa, anexos).
- **Hero Backgrounds (`::bg-image`)**: Imágenes de fondo inmersivas con control de opacidad por diapositiva.
- **Notas de Presentador**: Extracción de notas desde comentarios HTML (`<!-- notes -->`) o bloques (`:::notes`).

## 2. Componentes Especiales (Directivas de Bloque)
- **KPI Grid (`:::kpi-grid`)**: Cuadrícula para métricas clave con indicadores de estado.
- **Alert Boxes (`:::alert`)**: Cajas de alerta estilizadas (rojo, ámbar, verde, azul) con iconos custom.
- **Progress Bars (`:::progress-bars`)**: Barras de progreso con porcentajes y colores temáticos.
- **Info Grid (`:::info-grid`)**: Cuadrícula de información clave-valor.
- **Timeline (`:::timeline`)**: Líneas de tiempo para hitos y fases de proyectos.
- **Parallel Compare (`:::parallel-compare`)**: Diseño a dos columnas para comparar sistemas o conceptos.

## 3. Interactividad y Stepping
- **Listas Secuenciales (`:::steps`)**: Aparición paso a paso de elementos de una lista.
- **Layer Stack (`:::layer-stack`)**: Capas de imágenes superpuestas que aparecen de forma secuencial.
- **Code Stepping Mágico**: Resaltado secuencial de líneas de código en bloques de código (`{1|2-3|all}`).
- **Hotspots (`:::hotspots`)**: Pines interactivos sobre imágenes que revelan explicaciones tipo tooltip.
- **Spotlight (`:::spotlight`)**: Foco magnético que atenúa el fondo y resalta un elemento del DOM específico.

## 4. Contenido Técnico y Markdown Estándar
- **Bloques de Código**: Resaltado de sintaxis con soporte para resaltar múltiples líneas estáticas (`{1, 3-4}`).
- **Diagramas Mermaid**: Renderizado de diagramas de flujo y secuencias.
- **Tablas Markdown**: Soporte nativo para tablas estándar de Markdown.
- **Blockquotes**: Citas de impacto con estilos visuales destacados.

### Componentes Adicionales
- **Callout**: Cajas de información destacadas.
- **Fade Stagger**: Aparición escalonada de contenido.
- **Animated Counter**: Contadores numéricos animados.
- **Grid**: Grilla flexible de columnas.
- **Progress Ring**: Anillos de progreso circulares.
- **Tabs**: Pestañas interactivas de contenido.
- **Typewriter**: Efecto máquina de escribir.
- **Chart**: Gráficos de barras con Canvas.

## 5. Elementos Inline
- **Badges**: Etiquetas visuales de estado (`[texto]{.badge-color}`).
- **Resaltado Natural (Mark)**: Marcado brillante de texto (`==texto==`).
- **Navegación Dinámica**: Enlaces a slides específicos mediante Custom IDs (`{#id}`) y botones de retorno.

## 6. Funcionalidades del Reproductor (UI)
- **Menú Lateral Desplegable**: Índice de diapositivas auto-generado, con soporte para agrupar Anexos.
- **Transiciones Cinemáticas**: Uso de la View Transitions API para cambios suaves entre slides.
- **Auto-Escalado (Fit-to-Screen)**: Reducción dinámica de tamaño de fuente si el contenido excede la pantalla.
- **Herramientas de Presentador Vivo**: Puntero láser (`L`) y herramientas de dibujo en pantalla (`D`).
- **Modo Pantalla Completa**: Alternancia nativa (`F`).

## 7. Exportación y CLI
- **Exportación HTML Autocontenida**: Generación de un único archivo `.html` con todo el código, fuentes y estilos inyectados listos para compartir (imágenes se copian a `/output`).
- **Exportación Headless a PDF**: Conversión directa a PDF usando el motor Chromium de Playwright vía CLI (`presentmd build test.md -f pdf`).
- **Live Server (Preview)**: Servidor de desarrollo con recarga instantánea (`presentmd serve test.md`).
