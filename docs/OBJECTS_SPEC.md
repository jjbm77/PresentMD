# OBJECTS_SPEC.md — PresentMD v1.0 Component Library
**Target:** Python AST Parser (`markdown-it-py` + plugins) & Vanilla HTML/CSS
**Dependency:** Must conform strictly to `THEMES_SPEC.md` Design Tokens.

## 1. Core Philosophy
Objects in PresentMD are generated exclusively through Markdown syntax (standard or custom directives). The user NEVER writes HTML. The engine intercepts these directives during the AST build phase and outputs highly opinionated, semantic HTML structures. 

*New in Architecture Update:* Custom components are now decoupled from the core renderer using the `ComponentRegistry` (`plugins/registry.py`). This allows developers to easily inject new Markdown `:::` directives and custom Python handlers without modifying the underlying engine.

---

## 2. Tipografía y Estructura Base (Core Markdown)

### A. Encabezados (H1, H2, H3)
* **Sintaxis:** `#`, `##`, `###`
* **Funcionalidad:** * `H1` define el título principal de la lámina. Si un `H1` está solo, infiere automáticamente el `layout-title` (portada).
  * `H2` actúa como subtítulo (renderizado en color texto mutado).
  * `H3` se usa dentro de columnas o contenedores para agrupar información.
* **Técnica:** El parser mapea los tags a `<h1 class="slide-h1">`, inyectando las tipografías corporativas.

### B. Citas de Impacto (Blockquotes)
* **Sintaxis:** `> Texto de impacto`
* **Funcionalidad:** Destaca mensajes clave. Genera un bloque con un borde lateral grueso del color primario (`--accent-primary`), fondo tintado sutilmente y tipografía más grande.
* **Técnica:** Interceptado como `<blockquote>`. El CSS le inyecta la clase `.impact-quote`.

### C. Tablas Estilizadas (Styled Tables)
* **Sintaxis:** Tablas Markdown estándar (`| Col 1 | Col 2 |`).
* **Funcionalidad:** Diseño "Zebra" (filas con fondo alternado). Los encabezados siempre se renderizan en tipografía monoespaciada en mayúsculas para un look técnico.
* **Técnica:** Envuelve la tabla cruda en `<table class="styled-table">`.

---

## 3. Objetos de Datos y Métricas (Custom Directives)

### D. Grilla de KPIs (KPI Grid)
* **Sintaxis:**
  :::kpi-grid
  - [55,424M] Registros {status: critical}
  - [13 TB] Export estimado
  :::
* **Funcionalidad:** Muestra métricas clave. El número destaca masivamente. El parámetro `{status}` colorea el valor numérico (ej. `critical` = rojo, `amber` = amarillo).
* **Técnica:** Genera `<div class="kpi-grid">` y cada ítem en `<div class="kpi-card">`.

### E. Grilla de Información (Info Grid)
* **Sintaxis:**
  :::info-grid
  - Formato: Apache Parquet (columnar)
  - Transporte: AWS S3 (bucket dedicado)
  :::
* **Funcionalidad:** A diferencia de los KPIs, esta caja es para metadatos técnicos y texto corto. Muestra la etiqueta arriba (monoespaciada) y el valor abajo.
* **Técnica:** Genera `<div class="info-grid">` y `<div class="info-box">`. Separa el string por los dos puntos (`:`) asignando la clave a `.ib-label` y el valor a `.ib-value`.

### F. Barras de Progreso (Progress Bars)
* **Sintaxis:**
  :::progress-bars
  - Fase 1: 73%
  - Fase 2: 100% {color: secondary}
  :::
* **Funcionalidad:** Visualiza avances. Las barras crecen desde 0% al entrar a la lámina.
* **Técnica:** El motor lee el porcentaje y lo inyecta como estilo inline: `<div class="bar-fill" style="width: 73%">`.

---

## 4. Objetos de Arquitectura y Flujo

### G. Línea de Tiempo (Timeline / Roadmap)
* **Sintaxis:**
  :::timeline
  - **Fase 1 · Preparalelo**: Carga de Historia
    - ETL Evertec
    > Historia migrada y validada
  - **Fase 2 · Paralelo**: Validación
    - Pay Studio shadow
  :::
* **Funcionalidad:** Renderiza cajas secuenciales conectadas por flechas. El texto en negrita es la "medalla" (badge), el texto normal es el título, los bullets son descripciones y el blockquote (`>`) es el entregable final.
* **Técnica:** Genera un flexbox `.timeline`. Cada ítem principal es un `.timeline-phase`. Inserta automáticamente `.timeline-arrow` entre fases.

### H. Comparación Paralela (Parallel Flow)
* **Sintaxis:**
  :::parallel-compare{center-badge="COMPARA"}
  ### Productivo (Legacy)
  - Base24
  - BUT en Snowflake

  ---

  ### Shadow (Nuevo)
  - Pay Studio
  - UBUT
  :::
* **Funcionalidad:** Crea un layout estricto de 3 columnas (Izquierda, Centro, Derecha) ideal para comparar arquitectura actual vs. destino. Cada bullet se convierte en un nodo vertical.
* **Técnica:** El parser detecta el separador `---` dentro de la directiva para dividir las columnas. Genera `.parallel-container` y aplica los colores primary y secondary respectivamente a cada lado.

### I. Diagramas Complejos (D2 & Mermaid)
* **Sintaxis:** Bloques de código con lenguaje ` ```d2 ` o ` ```mermaid `.
* **Funcionalidad:** Renderiza diagramas vectoriales que no se pixelan.
* **Técnica (Crítica):** Ejecuta el binario de D2 en tiempo de compilación (`build`). Inyecta variables del tema activo e incrusta el SVG final en `<div class="diagram-container">`.

---

## 5. Anotaciones, Código y Navegación

### J. Código con Highlight Paso a Paso (Code Stepping)
* **Sintaxis:** ` ```sql {1, 3-5} `
* **Funcionalidad:** Bloques de código donde hacer clic oscurece el resto y resalta solo las líneas activas secuencialmente.
* **Técnica:** Genera el HTML con spans por línea `<span class="line" data-step="1">`. CSS maneja la opacidad controlada por Vanilla JS.

### K. Cajas de Alerta (Alert Boxes)
* **Sintaxis:**
  :::alert{type="red" icon="⚠️"}
  Bloqueador PCI: Requiere destokenización masiva.
  :::
* **Funcionalidad:** Cajas horizontales con ícono para denotar riesgos o notas.
* **Técnica:** Parser extrae los atributos y genera `<div class="alert-box red">`.

### L. Badges Inline (Etiquetas de Estado)
* **Sintaxis:** `[ALTA]{.badge-red}` o `[OWNER]{.badge-copper}`
* **Funcionalidad:** Cápsulas pequeñas para insertar en medio de párrafos o tablas.
* **Técnica:** Plugin `markdown-it-attrs`. Transforma a `<span class="badge b-red">ALTA</span>`.

### M. Deep Links (Navegación Interactiva)
* **Sintaxis:** `[Ver detalle →](#anexo-ingesta){.link-detalle}`
* **Funcionalidad:** Saltos directos a láminas de anexo.
* **Técnica:** Inyecta `<a href="#" data-target="anexo-ingesta" class="link-detalle">`. Vanilla JS empuja la lámina actual al historial y ejecuta el salto.

### N. Anclas de Explicación y Pines (Hotspots)
* **Sintaxis:**
  ```markdown
  :::hotspots{image="imagen.png"}
  - [20%, 30%] **Pin 1**: Explicación del primer punto.
  - [50%, 65%] **Pin 2**: Explicación del segundo punto.
  :::
  ```
* **Funcionalidad:** Muestra una imagen técnica de fondo con pines interactivos con números. Al hacer clic o avanzar, se despliega un tooltip contextual sobre el pin correspondiente.
* **Técnica:** El parser genera un contenedor `.hotspots-container` y calcula las posiciones absolutas `left` y `top` para cada pin `.hotspot-pin`.

### O. Foco Magnético (Spotlight)
* **Sintaxis:**
  ```markdown
  :::spotlight
  - [#id-elemento] **Foco 1**: Resalta el elemento con id `id-elemento`.
  - [.clase-elemento] **Foco 2**: Resalta el elemento con clase `clase-elemento`.
  :::
  ```
* **Funcionalidad:** Atenúa toda la pantalla excepto el selector indicado, y muestra una tarjeta flotante al lado de él con la explicación respectiva.
* **Técnica:** Serializa las coordenadas y descripciones en un atributo `data-spotlight-steps` en formato JSON, el cual es consumido por Vanilla JS para mover la máscara del spotlight.