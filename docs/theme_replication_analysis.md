# Análisis de Replicación de Tema — Convergencia Tecnológica

Este documento detalla el análisis arquitectónico y de diseño para replicar fielmente el estilo visual observado en las presentaciones de ejemplo (`20240601_MigracionDeDatos_Transacciones.html` y las láminas `.pptx`) en el motor de presentaciones **PresentMD**. 

El objetivo es lograr la consistencia estética y funcional (lámina de inicio, láminas de contenido, navegación por anexos e interactividad) **sin modificar la lógica de los plugins de Python** y utilizando las herramientas nativas disponibles en el sistema.

---

## 1. Mapeo del Sistema de Diseño (Design Tokens)

El tema de referencia define un conjunto de variables de CSS (`:root`) que se alinean casi perfectamente con las variables base del tema por defecto de PresentMD (`nexus-blueprint`). Podemos mapearlas de la siguiente forma en un nuevo tema llamado **`convergencia-tech`**:

### Paleta de Colores
| Variable de Referencia | Valor Hex / RGBA | Variable PresentMD | Rol Visual |
| :--- | :--- | :--- | :--- |
| `--transbank` | `#C8006B` | `--accent-primary` | Color acento principal (Rosa/Fucsia metálico) |
| `--transbank-d` | `#9a0052` | *Interna del tema* | Acento en hover / estados activos |
| `--transbank-l` | `rgba(200, 0, 107, 0.1)` | *Mapeada vía mix* | Fondos de alerta y resaltados de texto (`mark`) |
| `--evertec` | `#1a1a2e` | `--bg-chrome` | Fondos oscuros (portada, cabecera de slides, sidebar) |
| `--evertec-mid` | `#2d2d4a` | *Interna del tema* | Fondos secundarios oscuros |
| `--page` | `#f7f7f8` | `--bg-canvas` | Fondo claro de las láminas de contenido |
| `--ink` | `#1a1a2e` | `--text-main` | Texto principal del contenido |
| `--ink-soft` | `#6b7280` | `--text-muted` | Texto secundario y subtítulos |
| `--border` | `rgba(0, 0, 0, 0.08)` | `--border-color` | Líneas de división y bordes de componentes |
| `--card` | `#ffffff` | `--card-bg` | Fondos de tarjetas (`:::cards` y `:::kpi-grid`) |

### Tipografía
*   **Títulos y Textos de Cuerpo:** Calibri / Segoe UI / `system-ui`.
*   **Códigos, Números y Metadatos:** `'DM Mono', monospace` (cargada por defecto en PresentMD).

---

## 2. Replicación de Estructura y Layouts

PresentMD renderiza diapositivas lógicas de `1280px x 720px` (relación 16:9). El HTML de referencia utiliza un canvas de `1400px x 820px` con un look de "reproductor independiente" flotando sobre un fondo oscuro.

### A. Estilo "Player Canvas" (Lámina Flotante)
Podemos aplicar este diseño a nivel del contenedor global de PresentMD en la hoja de estilos del tema:
```css
body {
  background: #0d0d1a; /* Fondo ultra oscuro exterior */
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin: 0;
}

.presentation-container {
  max-width: 1400px;
  max-height: 820px;
  width: 90vw;
  height: calc(90vw * (9/16)); /* Mantener relación 16:9 */
  aspect-ratio: 16 / 9;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  position: relative;
}
```

### B. Lámina de Inicio (Layout Title Cover)
En la portada, la referencia presenta un fondo oscuro (`--evertec`), una barra vertical de acento fucsia en el borde izquierdo (`.transbank-accent`), y un footer con metadatos distribuidos a la izquierda y derecha.

*   **Barra Vertical Fucsia:** En lugar de modificar el HTML para meter un `<div>` adicional, usamos un pseudo-elemento CSS en la clase `.layout-title`:
    ```css
    .slide.layout-title::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 6px;
      background: var(--accent-primary);
      z-index: 10;
    }
    ```
*   **Metadatos en Footer:** El template `layouts/title.html.j2` inyecta un solo bloque `title-footer`. Podemos estructurar el contenido de la portada en Markdown usando bloques con clases específicas para distribuirlos horizontalmente con Flexbox:
    ```markdown
    <!-- Markdown de Portada -->
    ::layout{title}

    :::cover-top
    PROYECTO · CONVERGENCIA TECNOLÓGICA
    :::

    # Dominio Transaccional
    ## Estrategia de Migración

    :::cover-desc
    Migración del historial transaccional (Transbank · BUT) hacia el modelo destino (EVERTEC · Pay Studio)
    :::

    [Mayo 2026]{.badge-transbank}

    :::cover-footer
    :::left
    Track Transacciones · J. Bustamante
    :::
    :::right
    **Clasificación:** Confidencial · uso interno
    :::
    :::
    ```

### C. Láminas de Contenido (Layout Standard)
Muestran una cabecera con un "eyebrow" superior en fuente mono, el título principal y un subtítulo, seguidos de un cuerpo de lámina con fondo claro.
*   PresentMD soporta esto nativamente mapeando la variable `eyebrow` (configurada en el frontmatter como `section:` o `eyebrow:`) y extrayendo el primer `h1` como título y el primer `h2` del cuerpo como subtítulo en `layouts/standard.html.j2`.
*   El CSS del tema definirá:
    ```css
    .layout-standard .slide-header {
      background: var(--bg-chrome); /* #1a1a2e */
      color: #ffffff;
      padding: 24px 48px;
    }
    .layout-standard .slide-header .eyebrow {
      font-family: var(--font-mono);
      color: var(--accent-primary);
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
    }
    ```

---

## 3. Mecánica de Anexos y Navegación

La presentación de referencia tiene una estructura de flujo principal de diapositivas y una sección de **Anexos** no secuenciales a los que se salta usando hipervínculos como `Ver detalle →`. Esos anexos tienen un botón `← Volver`.

**Esta lógica ya está soportada nativamente en la arquitectura JS de PresentMD (en `base.html.j2`):**
1.  **Enlaces de Detalle:** El parser inline de PresentMD convierte enlaces como `[Ver detalle →](#particionamiento){.link-anexo}` en tags `<a>` interactivos. Al hacer click, el motor guarda la diapositiva actual en un array de historial (`history.push(current)`) y salta al slide con ID `#particionamiento`.
2.  **Lámina Anexo y Botón Volver:** Si una lámina se define con la directiva `::layout{annex}`, PresentMD renderiza el layout `scrollable` e inyecta automáticamente un botón `<button class="btn-volver">← Volver</button>`. El JS escucha los clicks en `.btn-volver` y ejecuta `goTo(history.pop())` para regresar al slide de origen.

---

## 4. Matriz de Replicación de Componentes

Podemos replicar todos los elementos visuales interactivos y estáticos usando la sintaxis nativa de componentes de PresentMD y aplicándoles el estilo correspondiente en el CSS del tema:

| Componente en Referencia | Sintaxis Markdown en PresentMD | Clases CSS / Implementación en Tema |
| :--- | :--- | :--- |
| **KPI Grid (Métricas)** | `:::kpi-grid` | `.kpi-card`, `.kpi-value`, `.kpi-label` (Cajas con números de color grande). |
| **Alert Boxes (Cajas de Alerta)** | `:::alert{type="amber" icon="⚠️"}` | `.alert-box`, `.alert-icon`. Coloreados usando `color-mix` en CSS según el tipo. |
| **Bar Charts (Historial/Cuatrimestres)** | `:::progress-bars` | `.progress-track`, `.bar-fill`. Define barras de progreso horizontales animadas. |
| **Línea de Tiempo (Pipeline)** | `:::timeline` | `.timeline-phase`, `.tl-badge`, `.tl-deliverable` para flujos ordenados. |
| **Tablas de Estado (Badges)** | Markdown Table estándar con `[ALTA]{.badge-red}` | `.styled-table` (zebra striping, headers oscuros, y badges coloreados en columnas). |
| **Gráficos y Diagramas** | ```mermaid ... ``` | Renderizado de diagramas SVG integrados nativamente con el Lightbox interactivo. |

---

## 5. Análisis de Brechas (Gap Analysis) y Soluciones

Durante el análisis del comportamiento visual de la referencia frente al motor base de PresentMD, se detectaron las siguientes diferencias específicas. Aquí se proponen soluciones técnicas limpias (no-plugin, no-código-Python) aprovechando al máximo la flexibilidad de CSS y la inyección en el template base:

### Brecha 1: Treemap de Bloques (Tamaño de Base de Datos)
*   **Problema:** En el Slide 4 de la referencia, se muestra un diagrama de bloques proporcionales (treemap) para ilustrar el peso de las tablas (ej: `Transacciones 5.4 TB`, `Retenciones 3.2 TB`). PresentMD no cuenta con un componente `:::treemap`.
*   **Solución (No-Plugin):** Podemos replicar este treemap de forma estática usando el componente nativo `:::grid` o mediante un contenedor genérico utilizando la propiedad CSS Grid o Flexbox flexible dentro del tema:
    ```markdown
    :::grid{cols=3}
    :::card{class="block-large color-transbank"}
    ### Transacciones
    5.4 TB (56%)
    :::
    :::card{class="block-medium color-evertec"}
    ### Retenciones
    3.2 TB (33%)
    :::
    :::card{class="block-small color-gray"}
    ### Otros
    1.1 TB (11%)
    :::
    :::
    ```
    Y en el CSS del tema, configuramos las cajas para que tengan tamaños o proporciones visuales simuladas (e.g. `.block-large` con mayor padding o altura).

### Brecha 2: Separadores y Layout de Anexos en la Sidebar (TOC)
*   **Problema:** En la referencia, el cajón de navegación (sidebar) tiene una línea separadora rotulada `-- Anexos --` que agrupa visualmente las láminas de detalle.
*   **Solución (Soportada):** `base.html.j2` ya cuenta con lógica para esto. Agrupa automáticamente los slides que tienen `is_annex` o `layout: annex` y añade el separador `<li class="toc-separator">── Anexos ──</li>`. Solo requerimos dar formato a esta clase en nuestro `styles.css`.

### Brecha 3: Doble Columna en el Footer de la Portada
*   **Problema:** El template de portada `title.html.j2` renderiza la variable `footer_text` en una sola línea centrada, mientras que el diseño de referencia tiene una estructura de dos columnas (Autor a la izquierda, Clasificación de Confidencialidad a la derecha).
*   **Solución (CSS-only):** Dado que `footer_text` se inyecta como HTML sin escape si lo deseamos, podemos definir un footer enriquecido en el frontmatter del archivo `.md`, o usar CSS en el selector `.title-footer` del tema para dividir el texto mediante un divisor (por ejemplo, dividiendo un string separado por `|` con selectores de pseudo-elementos, o permitiendo HTML básico en la variable `footer`):
    ```yaml
    # Frontmatter
    footer: "<div class='tf-container'><div class='tf-left'>Track Transacciones · J. Bustamante</div><div class='tf-right'><div class='tf-label'>Clasificación</div><div class='tf-value'>Confidencial · uso interno</div></div></div>"
    ```
    Y en el archivo CSS del tema damos estilo a `.tf-container` como flexbox con `justify-content: space-between`.

---

## 6. Código Base de CSS para el Nuevo Tema

A continuación se detalla la implementación completa del archivo `styles.css` para el nuevo tema **`convergencia-tech`**. 

Este archivo debe ser guardado en la ruta del proyecto:
`src/presentmd/templates/themes/convergencia-tech/styles.css`

```css
/* ============================================================
   CONVERGENCIA TECNOLÓGICA — Tema de Presentación Premium
   Replicación exacta de paleta de Transbank, evertec y layouts flotantes.
   ============================================================ */

/* --- Design Tokens --- */
:root {
  --accent-primary: #C8006B;       /* Transbank */
  --accent-primary-hover: #9a0052; /* Transbank Dark */
  --accent-secondary: #2563eb;     /* Blue */
  --accent-yellow: #d97706;        /* Amber */
  --accent-green: #059669;         /* Green */
  --accent-red: #dc2626;           /* Red */
  
  --bg-chrome: #1a1a2e;            /* evertec (oscuro para headers y portada) */
  --bg-canvas: #f7f7f8;            /* Page (gris claro para contenido) */
  --card-bg: #ffffff;              /* Card (blanco) */
  --border-color: rgba(0, 0, 0, 0.08);
  
  --text-main: #1a1a2e;            /* Ink */
  --text-muted: #6b7280;           /* Ink Soft */
  --text-light: #ffffff;
  
  --font-body: 'Segoe UI', Calibri, system-ui, sans-serif;
  --font-mono: 'DM Mono', monospace;
  --radius: 12px;
  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-card: 0 4px 12px rgba(0,0,0,0.05);
  
  /* Mapeo para componentes premium */
  --color-1: var(--accent-primary);
  --color-1-contrast: #ffffff;
  --color-2: var(--accent-secondary);
  --color-2-contrast: #ffffff;
  --color-3: var(--accent-yellow);
  --color-3-contrast: #ffffff;
  --color-4: var(--accent-green);
  --color-4-contrast: #ffffff;
}

/* --- Estilos del Contenedor Principal (Aspecto Flotante) --- */
body {
  background: #090911;
  font-family: var(--font-body);
  color: var(--text-main);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin: 0;
}

.presentation-container {
  width: 1280px;
  height: 720px;
  border-radius: 16px;
  background: var(--bg-canvas);
  box-shadow: 0 25px 60px rgba(0,0,0,0.45);
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
}

.slide {
  width: 1280px;
  height: 720px;
  background: var(--bg-canvas);
  padding: 0;
  display: none;
  flex-direction: column;
}
.slide.active {
  display: flex;
}

/* --- Portada (Layout Title) --- */
.slide.layout-title {
  background: var(--bg-chrome);
  color: var(--text-light);
  justify-content: center;
  align-items: flex-start;
  padding: 80px 100px;
  text-align: left;
  position: relative;
}

/* Barra vertical Transbank en portada */
.slide.layout-title::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  background: var(--accent-primary);
}

.layout-title .slide-body {
  width: 100%;
}

.layout-title .slide-h1 {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.15;
  color: var(--text-light);
  margin-top: 10px;
  margin-bottom: 12px;
}

.layout-title .slide-h2 {
  font-size: 1.8rem;
  color: var(--accent-primary);
  font-weight: 400;
  margin-bottom: 20px;
}

.layout-title p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 800px;
  line-height: 1.6;
}

.layout-title .accent-line {
  display: none; /* Ocultar la línea por defecto, ya usamos la barra lateral */
}

/* Portada Footer (Flex horizontal de dos columnas) */
.layout-title .title-footer {
  position: absolute;
  bottom: 40px;
  left: 100px;
  right: 100px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.layout-title .tf-container {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.layout-title .tf-right {
  text-align: right;
}

.layout-title .tf-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  color: var(--accent-primary);
  letter-spacing: 0.1em;
  margin-bottom: 2px;
}

.layout-title .tf-value {
  color: var(--text-light);
}

/* --- Layout Standard (Hojas de Contenido) --- */
.slide.layout-standard.active {
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.layout-standard .slide-header {
  background: var(--bg-chrome);
  color: var(--text-light);
  padding: 30px 50px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.layout-standard .slide-header .eyebrow {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--accent-primary);
  letter-spacing: 0.12em;
  margin-bottom: 4px;
}

.layout-standard .slide-header .slide-h1 {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text-light);
  line-height: 1.2;
}

.layout-standard .slide-header .slide-h2 {
  font-size: 1.05rem;
  color: var(--text-muted);
  font-weight: 400;
  margin-top: 6px;
}

.layout-standard .slide-body {
  padding: 40px 50px;
  overflow-y: auto;
}

.layout-standard .slide-footer {
  padding: 16px 50px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
}

.layout-standard .slide-footer .footer-text {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* --- Navegación y Botón Volver en Anexos --- */
.btn-volver {
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: var(--transition);
  margin-bottom: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-volver:hover {
  background: var(--accent-primary);
  color: white;
  box-shadow: 0 4px 10px rgba(200, 0, 107, 0.25);
}

/* --- Sidebar Cajón de Navegación (TOC) --- */
.toc-sidebar {
  background: var(--bg-chrome);
  border-right: 4px solid var(--accent-primary);
  width: 280px;
  padding: 40px 24px;
}

.toc-sidebar h3 {
  font-family: var(--font-mono);
  color: var(--accent-primary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 10px;
}

.toc-sidebar li {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: var(--transition);
}

.toc-sidebar li:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.toc-sidebar li.active {
  background: rgba(200, 0, 107, 0.15);
  color: var(--accent-primary);
  font-weight: 600;
}

/* Separadores de Anexos */
.toc-sidebar .toc-separator {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  padding: 16px 0 8px;
  pointer-events: none;
  border-bottom: none;
}

/* --- Componentes Específicos --- */

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.kpi-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-card);
  border-top: 3px solid var(--accent-primary);
}

.kpi-value {
  font-family: var(--font-mono);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 8px;
  line-height: 1;
}

.kpi-label {
  font-family: var(--font-body);
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Styled Premium Table */
.styled-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
  font-size: 0.85rem;
}

.styled-table thead th {
  background: var(--bg-chrome);
  color: var(--text-light);
  font-family: var(--font-mono);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  padding: 12px 18px;
  text-align: left;
}

.styled-table tbody td {
  padding: 12px 18px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-main);
}

.styled-table tbody tr:nth-child(even) {
  background: rgba(0, 0, 0, 0.02);
}

/* Badges de Columnas */
.badge {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.badge-red {
  background: rgba(220, 38, 38, 0.1);
  color: var(--accent-red);
}

.badge-amber {
  background: rgba(217, 119, 6, 0.1);
  color: var(--accent-yellow);
}

.badge-green {
  background: rgba(5, 150, 105, 0.1);
  color: var(--accent-green);
}

.badge-transbank {
  background: rgba(200, 0, 107, 0.1);
  color: var(--accent-primary);
}

/* Cajas de Alerta */
.alert-box {
  border-left: 4px solid var(--accent-primary);
  background: rgba(200, 0, 107, 0.05);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  gap: 16px;
}

.alert-box.alert-amber {
  border-left-color: var(--accent-yellow);
  background: rgba(217, 119, 6, 0.05);
}

.alert-box.alert-red {
  border-left-color: var(--accent-red);
  background: rgba(220, 38, 38, 0.05);
}

/* Progress / Bar Charts */
.progress-row {
  margin-bottom: 16px;
}

.progress-track {
  background: rgba(0, 0, 0, 0.05);
  height: 18px;
  border-radius: 9px;
  overflow: hidden;
}

.bar-fill {
  background: var(--accent-primary);
  height: 100%;
}

.bar-fill.secondary {
  background: var(--accent-secondary);
}

/* Enlaces de anexo / detalle */
.link-anexo, .link-detalle {
  color: var(--accent-primary);
  font-family: var(--font-mono);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dashed var(--accent-primary);
  padding-bottom: 1px;
  transition: var(--transition);
}

.link-anexo:hover, .link-detalle:hover {
  color: var(--accent-primary-hover);
  border-bottom-style: solid;
}
```
