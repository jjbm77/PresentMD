# Especificación Técnica del Sistema de Temas (THEMES_SPEC.md)

**Versión:** 1.1  
**Target Parser:** `markdown-it-py` (Contenedores Personalizados y Directivas Inline)  
**Entorno de Renderizado:** HTML5 Semántico + CSS Vanilla (CSS Grid, Variables CSS y Custom Elements)  
**Ecosistema:** PresentMD Core Engine

Este documento define la especificación técnica final y oficial para la creación, extensión y personalización de temas visuales en PresentMD. Está diseñado tanto para diseñadores de interfaces como para desarrolladores del motor, basándose rigurosamente en la implementación real de las plantillas Jinja2, el gestor de temas (`theme_manager.py`) y el runtime Javascript del cliente.

---

## 1. Arquitectura y Ubicación del Sistema de Temas

PresentMD admite temas integrados (built-in) y temas personalizados de usuario. El módulo `ThemeManager` (`theme_manager.py`) se encarga de resolver y cargar el código CSS correspondiente al tema indicado en el frontmatter del archivo Markdown (`theme: <nombre_tema>`).

### Prioridad de Búsqueda del Compilador
Cuando el motor procesa una presentación, busca el archivo `styles.css` del tema solicitado siguiendo este orden de prioridad:

1. **Directorio del Usuario (`~/.config` o `%APPDATA%`):**
   * **Linux/macOS:** `~/.config/presentmd/themes/<nombre_tema>/styles.css`
   * **Windows:** `%APPDATA%\presentmd\themes\<nombre_tema>\styles.css`
2. **Directorio Interno (Built-in Themes):**
   * Ruta en el paquete del motor: `src/presentmd/templates/themes/<nombre_tema>/styles.css`
3. **Respaldo Global (Fallback):**
   * Si no se encuentra en las rutas anteriores, el motor carga el tema por defecto: `src/presentmd/templates/themes/nexus-blueprint/styles.css`

> [!NOTE]
> El motor realiza un alias automático para temas renombrados. Por ejemplo, si el usuario define `theme: nexus-minimal`, `ThemeManager` lo redirigirá internamente a `minimal`.

### Estructura Requerida de la Carpeta de un Tema
Para que un tema sea reconocido por el sistema, debe estar empaquetado en una subcarpeta homónima con la siguiente estructura mínima:

```bash
<nombre_tema>/
├── styles.css           # Archivo CSS obligatorio con todas las reglas y tokens.
└── assets/              # Carpeta opcional para tipografías locales, logos y fondos.
```

---

## 2. Tokens de Diseño y Variables CSS Obligatorias

El Runtime JavaScript y las plantillas HTML asumen la existencia de variables CSS específicas dentro del selector `:root` del tema activo. Estas variables permiten que tanto la interfaz del reproductor (controles, barra de progreso, menús) como los diagramas SVG (Mermaid) se integren de forma cohesiva.

### Definición de Variables CSS de la Interfaz (`:root`)

Cada tema debe implementar obligatoriamente las siguientes variables en su bloque `:root`:

| Variable | Propósito | Ejemplo (Nexus Blueprint) |
| :--- | :--- | :--- |
| `--accent-primary` | Color de énfasis principal (líneas activas, botones, resaltados) | `#C8006B` |
| `--accent-secondary` | Color de énfasis secundario (gráficas alternas, comparaciones) | `#2563eb` |
| `--accent-yellow` | Color funcional para alertas y estados intermedios | `#D97706` |
| `--accent-green` | Color funcional para estados de éxito o positivos | `#059669` |
| `--accent-red` | Color funcional para estados críticos o errores | `#DC2626` |
| `--accent-blue` | Color funcional alternativo para flujos informativos | `var(--accent-secondary)` |
| `--bg-canvas` | Fondo del lienzo principal de cada diapositiva | `#f7f7f8` |
| `--bg-chrome` | Fondo de cabeceras, barra lateral de contenidos y cabeceras de tablas | `#1a1a2e` |
| `--card-bg` | Fondo para los contenedores modulares (`kpi-card`, `card-box`, etc.) | `#ffffff` |
| `--text-main` | Color del texto del cuerpo principal (alta legibilidad) | `#111111` |
| `--text-muted` | Color para subtítulos, etiquetas y metadatos secundarios | `#6b7280` |
| `--font-body` | Familia tipográfica principal para el texto común | `'Segoe UI', system-ui, sans-serif` |
| `--font-mono` | Familia tipográfica monoespaciada para códigos y métricas | `'DM Mono', monospace` |
| `--radius` | Radio de curvatura global de bordes para tarjetas y bloques | `8px` |
| `--transition` | Configuración por defecto para animaciones y hover | `0.3s ease` |

### Paleta Universal de Colores para SmartArts (`--color-X`)
Para garantizar la consistencia en componentes complejos de datos (gráficos, flujos de procesos, tablas prémium y pirámides), los temas deben asignar colores y sus respectivos colores de contraste a los siguientes 6 tokens universales:

* **Colores de Fondo:** `--color-1` a `--color-6` (mapeados por defecto a los colores funcionales de `:root`).
* **Colores de Contraste (Texto):** `--color-1-contrast` a `--color-6-contrast` (usados para asegurar contraste AA/AAA sobre los fondos de color correspondientes, ej. `#ffffff` o `#000000`).

La inyección de estos colores se realiza en el DOM a través del atributo `data-color="X"` o la clase `.c-X`. El CSS del tema debe mapear esta inyección dinámicamente:
```css
[data-color="1"], .c-1 { --ui-color: var(--color-1); --ui-contrast: var(--color-1-contrast); }
[data-color="2"], .c-2 { --ui-color: var(--color-2); --ui-contrast: var(--color-2-contrast); }
/* Repetir para data-color 3, 4, 5 y 6 */
[data-color] { --segment-color: var(--ui-color); }
```

### Reglas críticas para el Auto-Escalado (Fit-to-Screen)
El motor opera bajo un canvas lógico rígido de **1280px x 720px (relación de aspecto 16:9)**. El Runtime del cliente realiza un escalado dinámico en dos fases:
1. **Escalado del Canvas:** Mide el viewport del navegador (`window.innerWidth` / `window.innerHeight`) y aplica un valor de `transform: scale(...)` de manera uniforme sobre todas las diapositivas `.slide` para que encajen perfectamente en la pantalla sin desbordamientos físicos.
2. **Auto-ajuste de Texto:** Si el contenido excede verticalmente el límite físico del contenedor de la diapositiva (`scrollHeight > 720px`), un algoritmo iterativo disminuye el `font-size` del elemento `html` en pasos de `2%` (desde `16px` hasta un mínimo de `9.6px` [60%]) hasta que el contenido encaje de forma nativa.

> [!IMPORTANT]
> Para no romper este algoritmo de ajuste, **toda tipografía, padding y margen dentro de las diapositivas debe definirse usando unidades relativas (`rem` o porcentajes)**. Si se definen tamaños de texto absolutos en píxeles (`px`), el algoritmo de auto-ajuste no surtirá efecto y el contenido se desbordará.

---

## 3. Estilos Base y Estructura de Diapositivas (Layouts)

El generador de HTML inyecta un árbol estructurado de selectores dentro del contenedor `.presentation-container`. Cada diapositiva se representa mediante un elemento `<section class="slide">` con posiciones absolutas.

```html
<div class="presentation-container">
  <section class="slide layout-<tipo_layout> [diagram-only] [annex]" data-index="0" id="slide-id" data-notes="Notas del orador...">
    <!-- Inyección opcional de imagen de fondo -->
    <div class="slide-bg-overlay" style="background-image: url(...); opacity: 0.15;"></div>
    
    <div class="slide-header">
      <div class="eyebrow">Ceja de Título (Eyebrow)</div>
      <h1 class="slide-h1">Título de la Diapositiva</h1>
      <h2 class="slide-h2">Subtítulo o contexto</h2>
    </div>
    
    <div class="slide-body">
      <!-- Elementos e inyecciones de Markdown -->
    </div>
    
    <div class="slide-footer">
      <span class="footer-text">Texto de pie de página</span>
      <span class="footer-logo"></span>
    </div>
  </section>
</div>
```

### Selectores de Estilos Base Requeridos

```css
.presentation-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 1280px;
  height: 720px;
  background: var(--bg-canvas);
  transform-origin: top left;
  display: none;
  flex-direction: column;
  overflow: hidden;
}

.slide.active {
  display: flex; /* El runtime activa/desactiva la diapositiva usando esta clase */
}

.slide-bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 0;
  pointer-events: none; /* Asegura que la imagen de fondo no bloquee interacciones */
}
```

### Especificación de los Diseños Estructurales (Layouts)

La heurística del compilador asigna uno de los siguientes diseños en función de la estructura detectada en el AST de Markdown o por directivas explícitas (`::layout{name}`):

#### 1. Portada o Título (`layout-title`)
* **Uso:** Primera página o separadores de sección.
* **Comportamiento:** Centrado absoluto vertical y horizontal, fondo oscuro (`--bg-chrome`), tipografías de escala masiva (`clamp(2.4rem, 5vw, 3.6rem)`), y una línea decorativa central `.accent-line` que utiliza `--accent-primary`.

#### 2. Estándar (`layout-standard`)
* **Uso:** 90% de las diapositivas de contenido.
* **Comportamiento:** Debe organizarse mediante un modelo de rejilla que prevenga el solapamiento de cajas:
  ```css
  .slide.layout-standard.active {
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 1fr;
  }
  ```
* El encabezado `.slide-header` se sitúa en la parte superior y el pie de página `.slide-footer` en la inferior. La sección intermedia `.slide-body` toma todo el espacio vertical disponible y debe ocultar o gestionar barras de scroll internas de forma sutil.

#### 3. Desplazable o Anexos (`layout-scrollable`)
* **Uso:** Diapositivas de datos profundos, tablas largas o secciones marcadas como anexos (`annex`).
* **Comportamiento:** Similar al estándar, pero permite el desplazamiento vertical del contenido en `.slide-body` (`overflow-y: auto`). Si el contenedor tiene el atributo `[data-annex="true"]` o la clase `.annex`, la cabecera debe incluir un botón de retorno a la diapositiva de origen (`.btn-volver`).

#### 4. Comparación Dividida (`layout-split-comparison`)
* **Uso:** Disposición en paralelo para contrastar dos bloques de datos.
* **Comportamiento:** Organiza `.slide-body` en una cuadrícula simétrica de 3 columnas:
  ```css
  .layout-split-comparison .slide-body {
    display: grid;
    grid-template-columns: 1fr 50px 1fr;
    gap: 0;
  }
  ```
  Genera las clases `.pc-left` (columna izquierda, recomendada con color de fondo atenuado de `--accent-primary`), `.pc-right` (columna derecha, recomendada con fondo atenuado de `--accent-secondary`), y `.pc-center` (para el divisor central que aloja una medalla divisoria `.vs-badge`).

---

## 4. Estilos para los 25+ Componentes Técnicos (SmartArt & Containers)

PresentMD extiende el estándar Markdown para renderizar componentes semánticos complejos sin requerir código HTML en el documento fuente. A continuación se listan todos los componentes del sistema con su correspondiente árbol DOM y requerimientos de CSS.

---

### 1. Cuadrícula de KPI (`:::kpi-grid`)
* **DOM:**
  ```html
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-value [critical|amber|green]">55M</div>
      <div class="kpi-label">Usuarios Activos</div>
    </div>
  </div>
  ```
* **CSS Requerido:** `.kpi-grid` debe usar `display: grid` con comportamiento flexible (`grid-template-columns: repeat(auto-fit, minmax(160px, 1fr))`). La clase `.kpi-value` debe usar `--font-mono` para alineación visual de números y jerarquía visual aumentada.

---

### 2. Contenedor de Alerta (`:::alert`)
* **DOM (Vertical):**
  ```html
  <div class="alert-box layout-vertical" data-color="1" [data-size="sm"]>
    <div class="alert-header">
      <span class="alert-icon">⚠️</span>
      <div class="alert-title">Título de Alerta</div>
    </div>
    <div class="alert-body">
      <p>Texto interno...</p>
    </div>
  </div>
  ```
* **DOM (Horizontal):**
  ```html
  <div class="alert-box layout-horizontal" data-color="2">
    <span class="alert-icon">ℹ️</span>
    <div class="alert-content">
      <div class="alert-horizontal">
        <div class="alert-h-item">Elemento inline 1</div>
      </div>
    </div>
  </div>
  ```
* **CSS Requerido:** Fondo atenuado mezclando el color de énfasis y transparencia (`color-mix(in srgb, var(--ui-color) 8%, transparent)`), borde izquierdo grueso (`border-left: 4px solid var(--ui-color)`), y flexbox para alinear iconos y contenidos.

---

### 3. Contador Animado (`:::animated-counter`)
* **DOM:**
  ```html
  <div class="animated-counter-container">
    <span class="animated-counter" data-from="0" data-target="99" prefix="$" suffix="k" duration="1500">$0k</span>
    <div class="animated-counter-title">Ventas Totales</div>
  </div>
  ```
* **CSS Requerido:** El número `.animated-counter` debe tener peso tipográfico destacado y usar `--font-mono` para evitar oscilaciones de ancho durante la animación ejecutada por el Runtime.

---

### 4. Gráfico de Columnas (`:::bar-chart`)
* **DOM:**
  ```html
  <div class="bar-chart-wrapper">
    <div class="bar-chart-title">Título del Gráfico</div>
    <div class="bar-chart-container">
      <div class="bar-chart-column" data-step-idx="0">
        <div class="bar-value-label">85%</div>
        <div class="bar-track">
          <div class="chart-bar-fill" data-color="1" data-bar-height="85%"></div>
        </div>
        <div class="bar-label">Q1</div>
      </div>
    </div>
  </div>
  ```
* **CSS Requerido:** `.bar-chart-container` alinea columnas usando flexbox con `align-items: flex-end`. `.chart-bar-fill` lee el valor inyectado en `--bar-height` (a través de `data-bar-height` procesado por el runtime) para asignar la altura de la columna.

---

### 5. Caja de Llamado (`:::callout`)
* **DOM:**
  ```html
  <div class="callout-box" data-color="1">
    <span class="callout-icon">💡</span>
    <div class="callout-content">
      <div class="callout-title">Nota Técnica</div>
      <div class="callout-body">Contenido de la nota...</div>
    </div>
  </div>
  ```
* **CSS Requerido:** Diseño acolchado con bordes curvos y un filete lateral alineado a la izquierda usando el color de énfasis seleccionado (`var(--ui-color)`).

---

### 6. Cuadrícula de Tarjetas (`:::cards`)
* **DOM:**
  ```html
  <div class="cards-grid" style="--cols: 3;">
    <div class="card-box">
      <div class="card-header">
        <span class="card-icon">⚡</span>
        <div class="card-title">Título de Tarjeta</div>
      </div>
      <div class="card-content">
        <ul class="card-list">
          <li>Punto de lista</li>
        </ul>
      </div>
    </div>
  </div>
  ```
* **CSS Requerido:** Cuadrícula basada en la variable `--cols` (`grid-template-columns: repeat(var(--cols, 2), 1fr)`). Los elementos `.card-box` deben comportarse como tarjetas elevadas usando `--card-bg`, bordes finos e iluminación por sombra (`--shadow-card`).

---

### 7. Gráficos dinámicos Canvas (`:::chart`)
* **DOM:**
  ```html
  <div class="chart-wrapper">
    <div class="chart-title">Visualización de Datos</div>
    <div class="chart-container">
      <canvas class="presentmd-chart" data-chart-config="{...}"></canvas>
    </div>
    <table class="sr-only" aria-hidden="true">...</table>
  </div>
  ```
* **CSS Requerido:** Contenedores flexibles que aíslen el canvas para evitar que rompa las proporciones físicas de la diapositiva. Tabla oculta mediante accesibilidad estructural (`.sr-only`).

---

### 8. Desvanecimiento Escalonado (`:::fade-stagger`)
* **DOM:**
  ```html
  <div class="fade-stagger-container">
    <div class="fade-stagger-item">Elemento A</div>
    <div class="fade-stagger-item">Elemento B</div>
  </div>
  ```
* **CSS Requerido:** Animación de opacidad y desplazamiento vertical (`translateY`) con retrasos incrementales (staggering) aplicados por CSS o clases dinámicas.

---

### 9. Cuadrícula de Características (`:::feature-grid`)
* **DOM:**
  ```html
  <div class="feature-grid" style="--cols: 3;">
    <div class="feature-card" data-color="1">
      <div class="fc-icon">🔒</div>
      <div class="fc-content">Seguridad Certificada</div>
    </div>
  </div>
  ```
* **CSS Requerido:** Distribución simétrica en CSS Grid. Cada `.feature-card` debe tener hover interactivo con elevación suave (`transform: translateY(-4px)`) y cambio en el color del borde inferior mapeado a `--ui-color`.

---

### 10. Contenedor de Rejilla Flex (`:::grid`)
* **DOM:**
  ```html
  <div class="grid-container" style="--grid-cols: 1fr 2fr; --grid-gap: 20px; --grid-align: center; --grid-valign: middle;">
    <div class="grid-column" data-col-width="300px">...</div>
  </div>
  ```
* **CSS Requerido:** Rejilla flexible controlada mediante las variables de estilo inyectadas en línea (`grid-template-columns: var(--grid-cols)` o flexbox con anchos configurables en `.grid-column` mediante `data-col-width` y `data-col-frac`).

---

### 11. Puntos Calientes Interactivos (`:::hotspots`)
* **DOM:**
  ```html
  <div class="hotspots-container">
    <img src="..." class="hotspots-image">
    <div class="hotspots-pins-layer">
      <div class="hotspot-pin" style="left: 20%; top: 30%;">
        <div class="pin-marker">1</div>
        <div class="pin-tooltip">
          Texto descriptivo del punto caliente
          <div class="pin-tooltip-arrow"></div>
        </div>
      </div>
    </div>
  </div>
  ```
* **CSS Requerido:** `.hotspots-container` debe tener posicionamiento relativo. Los `.hotspot-pin` se posicionan de manera absoluta. El marcador `.pin-marker` debe emitir una animación de pulso infinito (`@keyframes pinPulse`) usando `--accent-primary` para llamar la atención del espectador, desactivándose al ganar la clase `.active`.

---

### 12. Cuadrícula de Información de Metadatos (`:::info-grid`)
* **DOM:**
  ```html
  <div class="info-grid">
    <div class="info-box">
      <div class="ib-label">Base de Datos</div>
      <div class="ib-value">PostgreSQL 16</div>
    </div>
  </div>
  ```
* **CSS Requerido:** Tarjetas informativas de dos niveles. `.ib-label` usa `--font-mono` y transformaciones a mayúsculas con tracking expandido para simular una etiqueta técnica.

---

### 13. Pila de Capas de Imágenes (`:::layer-stack`)
* **DOM:**
  ```html
  <div class="layer-stack">
    <img src="img1.png" class="layer-image active">
    <img src="img2.png" class="layer-image layer-hidden">
  </div>
  ```
* **CSS Requerido:** Las imágenes se superponen de forma absoluta en el centro del contenedor. Las capas inactivas reciben la clase `.layer-hidden` (que reduce la opacidad a `0` y aplica `scale(0.98)`), mientras que la activa recibe `.active` (opacidad `1`, `scale(1)`), permitiendo transiciones cinematográficas fluidas.

---

### 14. Comparación en Paralelo (`:::parallel-compare`)
* **DOM:**
  ```html
  <div class="parallel-container">
    <div>
      <div class="pc-col-header">Antes</div>
      <div class="pc-node">Legacy System</div>
    </div>
    <div class="timeline-arrow">→</div>
    <div>
      <div class="pc-col-header">Después</div>
      <div class="pc-node">PresentMD Core</div>
    </div>
  </div>
  ```
* **CSS Requerido:** Alineación horizontal de las columnas y el nodo conector central (`.timeline-arrow` o `.vs-badge`), aplicando colores y contrastes según el estado de la comparación.

---

### 15. Flujo de Procesos (`:::process-flow`)
* **DOM:**
  ```html
  <pmd-process-flow [data-steps="true"]>
    <div class="pmd-process-card [step-hidden]" data-color="1" [data-step]>
      <div class="pmd-process-icon">⚙️</div>
      <div class="pmd-process-text">Fase 1</div>
      <div class="pmd-process-label">Análisis</div>
      <div class="pmd-process-desc">Descripción...</div>
    </div>
  </pmd-process-flow>
  ```
* **CSS Requerido:** El Custom Element `<pmd-process-flow>` debe organizar sus tarjetas hijas en una línea de tiempo horizontal. Si cuenta con animación de pasos (`[data-steps]`), las tarjetas deben ocultarse mediante la clase `.step-hidden` e ir apareciendo secuencialmente con transiciones suaves.

---

### 16. Filas de Progreso Lineales (`:::progress-bars`)
* **DOM:**
  ```html
  <div class="progress-row">
    <span class="progress-label">Rendimiento</span>
    <div class="progress-track">
      <div class="bar-fill" data-color="1" style="--target-width: 75%;"></div>
    </div>
    <span class="progress-pct">75%</span>
  </div>
  ```
* **CSS Requerido:** `.bar-fill` se inicializa con `width: 0` y escala de manera animada en el cliente hasta alcanzar el valor inyectado en `--target-width`.

---

### 17. Anillo de Progreso Circular (`:::progress-ring`)
* **DOM:**
  ```html
  <div class="progress-ring-wrapper">
    <div class="progress-ring-container" data-ring-size="120">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" class="progress-ring-bg"></circle>
        <circle cx="60" cy="60" r="56" class="progress-ring-fill" data-color="1" stroke-dasharray="351.86" stroke-dashoffset="351.86" data-value="75" data-circumference="351.86"></circle>
      </svg>
      <div class="progress-ring-percentage">75%</div>
    </div>
    <div class="progress-ring-title">Métrica Clave</div>
  </div>
  ```
* **CSS Requerido:** Anillos vectoriales superpuestos. El anillo `.progress-ring-fill` se renderiza de manera antihoraria o rotado `-90deg` para que inicie en el eje norte, controlando su trazo dinámicamente mediante `stroke-dashoffset` en respuesta al script del cliente.

---

### 18. Pirámide de Niveles (`:::pyramid`)
* **DOM:**
  ```html
  <pmd-pyramid data-layout="pyramid" [data-steps="true"]>
    <div class="pmd-pyramid-item [step-hidden]" data-color="1" [data-step]>
      <div class="pmd-pyramid-icon">🔥</div>
      <div class="pmd-pyramid-text">L1</div>
      <div class="pmd-pyramid-label">Nivel Base</div>
      <div class="pmd-pyramid-desc">Descripción...</div>
    </div>
  </pmd-pyramid>
  ```
* **CSS Requerido:** Implementación del diseño piramidal donde cada nivel sucesivo tiene un ancho menor (o mayor si es pirámide invertida). Mapeo de colores en base a `data-color` y soporte para ocultación en pasos (`.step-hidden`).

---

### 19. Proceso Circular Radial (`:::radial-process`)
* **DOM:**
  ```html
  <pmd-radial-process center-title="Motor" [data-steps="true"]>
    <div class="pmd-radial-process-item [step-hidden]" data-color="2" [data-step]>
      <div class="pmd-radial-process-icon">⚙️</div>
      <div class="pmd-radial-process-text">P1</div>
      <div class="pmd-radial-process-label">Procesador</div>
      <div class="pmd-radial-process-desc">Núcleo Central</div>
    </div>
  </pmd-radial-process>
  ```
* **CSS Requerido:** Disposición circular alrededor de una etiqueta central (`center-title`). Se requiere posicionar cada elemento en un ángulo de coordenadas polares calculado o provisto mediante CSS dinámico.

---

### 20. Foco Spotlight de Atención (`:::spotlight`)
* **DOM (Generado en Diapositiva):**
  ```html
  <div class="spotlight-config" data-spotlight-steps='[{"selector": ".target-class", "content": "Texto explicativo"}]'></div>
  ```
* **DOM Global (Estructura de Runtime en `base.html.j2`):**
  ```html
  <div class="spotlight-overlay"></div>
  <div class="spotlight-tooltip">
    <div class="spotlight-tooltip-content">Texto explicativo</div>
  </div>
  ```
* **CSS Requerido:** El overlay `.spotlight-overlay` cubre toda la pantalla con un fondo oscuro translúcido (`rgba(0,0,0,0.85)`). El Runtime calcula la posición del elemento objetivo (`.target-class`), aplicando un recorte mediante `clip-path` o máscara radial de gradiente para iluminar el selector de forma exclusiva. La burbuja `.spotlight-tooltip` flota inmediatamente al lado del selector iluminado.

---

### 21. Lista Animada por Pasos (`:::steps`)
* **DOM:**
  ```html
  <ol class="steps-list">
    <li class="step-hidden">Primer hito</li>
    <li class="step-hidden">Segundo hito</li>
  </ol>
  ```
* **CSS Requerido:** Los elementos de lista con la clase `.step-hidden` deben tener opacidad `0` y un desplazamiento vertical hacia abajo (`transform: translateY(8px)`). Al activarse el sub-paso, el motor reemplaza la clase por `.step-visible`, la cual transiciona la opacidad a `1` y remueve el desplazamiento (`transform: translateY(0)`).

---

### 22. Tablas Prémium (`:::table-premium` / `:::pmd-table`)
* **DOM:**
  ```html
  <div class="pmd-table-wrapper" data-variant="angled" [data-total-row="true"] style="--tc-1: var(--color-1); ...">
    <table>
      <caption>Título de la Tabla</caption>
      <thead>
        <tr><th>Columna A</th></tr>
      </thead>
      <tbody>
        <tr><td>Valor 1</td></tr>
      </tbody>
    </table>
  </div>
  ```
* **CSS Requerido:** Soporte para variantes (`data-variant="angled|ribbon|simple"`). La variante `angled` requiere cabeceras inclinadas o con cortes poligonales. La variante `ribbon` añade un listón lateral de color en la primera celda. El atributo `[data-total-row]` destaca tipográficamente y añade bordes dobles a la última fila del cuerpo de la tabla.

---

### 23. Contenedor de Pestañas (`:::tabs`)
* **DOM:**
  ```html
  <div class="tabs-container" [data-variant="custom-var"] id="tabs-xxx">
    <div class="tabs-list" role="tablist">
      <button class="tab-button active" id="tab-0" role="tab" aria-selected="true" aria-controls="panel-0">Pestaña 1</button>
      <button class="tab-button" id="tab-1" role="tab" aria-selected="false" aria-controls="panel-1" tabindex="-1">Pestaña 2</button>
    </div>
    <div class="tabs-panels">
      <div class="tab-panel active" id="panel-0" role="tabpanel" aria-labelledby="tab-0">Contenido 1</div>
      <div class="tab-panel" id="panel-1" role="tabpanel" aria-labelledby="tab-1" hidden>Contenido 2</div>
    </div>
  </div>
  ```
* **CSS Requerido:** Maquetación horizontal para `.tabs-list` mediante flexbox. Los botones `.tab-button` deben reaccionar con transiciones de color de fondo y bordes inferiores según ganen o pierdan la clase `.active`. Los `.tab-panel` deben alternar su visibilidad (`display: none` / `display: block`) en sincronía con la clase `.active` y el atributo `hidden`.

---

### 24. Línea de Tiempo de Hitos (`:::timeline`)
* **DOM:**
  ```html
  <div class="timeline">
    <div class="timeline-phase">
      <div class="tl-badge">Fase 1</div>
      <div class="tl-title">Planificación</div>
      <div class="tl-desc">Definición de alcance</div>
      <div class="tl-deliverable">Entregable: Especificación</div>
    </div>
    <div class="timeline-arrow">→</div>
  </div>
  ```
* **CSS Requerido:** `.timeline` fuerza una visualización horizontal (`display: flex`) habilitando desplazamiento lateral (`overflow-x: auto`) para layouts densos. Los elementos de desfase `.timeline-arrow` deben centrarse verticalmente entre las tarjetas.

---

### 25. Efecto Typewriter (`:::typewriter`)
* **DOM:**
  ```html
  <div class="typewriter-container" data-speed="50" data-delay="200" [data-color="1"]>
    <span class="typewriter-text">Texto siendo escrito línea por línea...</span>
    <span class="typewriter-cursor">|</span>
  </div>
  ```
* **CSS Requerido:** El cursor `.typewriter-cursor` debe contar con una animación de parpadeo infinito de opacidad (`@keyframes blink`). El texto `.typewriter-text` se alimenta de la lógica de inyección de caracteres del Runtime en base a los atributos de velocidad (`data-speed`) y retraso (`data-delay`).

---

### Interacción con Clases de Visibilidad en Sub-Pasos
El Runtime de PresentMD controla la secuenciación de sub-pasos evaluando el atributo `data-step` o los elementos internos de listas y contenedores.
* Al renderizar la diapositiva en sentido **adelante (forward)**, los elementos se inicializan con la clase `.step-hidden` para ocultarlos.
* Al avanzar, el Runtime sustituye progresivamente la clase `.step-hidden` por `.step-visible`.
* Al retroceder o inicializar en sentido **atrás (backward)**, los elementos de pasos se fuerzan directamente a `.step-visible`.
El tema debe asegurar transiciones de opacidad y transformación fluidas entre estas clases:
```css
.step-hidden {
  opacity: 0 !important;
  pointer-events: none;
}
.step-visible {
  opacity: 1 !important;
  pointer-events: auto;
}
```

---

## 5. Clases Especiales e Interactividad

El Runtime JavaScript gestiona dinámicamente interacciones complejas de teclado, ratón y redibujado de la pantalla. El tema debe proveer el diseño visual de soporte para estos estados interactivos.

### Resaltado de Sintaxis y Code Stepping Animado

Cuando un bloque de código Markdown incluye la sintaxis de pasos avanzados de resaltado (ej. ` ```python {1|2-3|all} `):
1. El motor inyecta el código envolviendo cada línea en una caja con la clase `.code-line` y su número de línea correspondiente en `data-line`.
2. Al activarse el flujo paso a paso:
   * El contenedor principal `.code-container` recibe la clase `.stepping-active` (o `.stepping`).
   * Las líneas correspondientes al paso actual reciben la clase `.step-active` (o `.highlight-active`).
   * Las líneas inactivas deben atenuarse para desviar la atención hacia el código activo.

```css
/* Estado en que el bloque de código está en medio de una secuencia de pasos */
.code-container.stepping-active .code-line {
  opacity: 0.3;
  transition: opacity var(--transition), background var(--transition);
}

/* Línea o conjunto de líneas activas dentro de la secuencia actual */
.code-container.stepping-active .code-line.step-active,
.code-container .code-line.highlight-active {
  opacity: 1;
  background: color-mix(in srgb, var(--accent-primary) 15%, transparent);
  border-left: 3px solid var(--accent-primary);
  padding-left: 8px; /* Ajuste visual por la inyección del borde */
  margin-left: -7px;
}
```

### Elementos de Control del Reproductor e Historial
El reproductor inyecta elementos fijos a nivel de ventana que no pertenecen directamente a los elementos del body de las diapositivas. El tema debe asegurar su correcta visualización y apilamiento (`z-index`):

* **Barra de Progreso de Navegación (`.nav-progress`):** Situada en el borde inferior o superior de la ventana (`position: fixed`). Cuenta con un hijo `.nav-progress-fill` que refleja la lectura de avance porcentual de la presentación mediante `transform: scaleX(...)` o asignación de ancho.
* **Contador de Páginas (`.slide-counter`):** Widget flotante con fondo atenuado y bordes redondeados que indica la posición actual (`Pág. X / Y`).
* **Lienzo de Dibujo Libre (`.drawing-canvas`):** Capa transparente superpuesta a todo el reproductor (`z-index: 990`) activada por teclado (`d`/`D`). Permite trazos de anotación a mano alzada. El cursor del ratón debe mutar a un icono de lápiz que utilice el color `--accent-primary`.
* **Consola de Presentador Sincronizada (`.presenter-console-container`):** Layout flotante que muestra notas del orador, vista previa de la diapositiva siguiente y cronómetro de tiempo transcurrido.
* **Caja de Luz para Diagramas (`#lightboxWrapper` / `.lightbox-overlay`):** Permite aislar y realizar zoom interactivo sobre diagramas vectoriales haciendo clic en ellos.

---

## 6. Especificación de Impresión (Print CSS for PDF)

El flujo de exportación a PDF en PresentMD se realiza abriendo la presentación compilada en el navegador y pulsando `Ctrl+P` (o `Cmd+P` en macOS). Para asegurar que el archivo resultante sea "Pixel-Perfect" y respete el diseño original de diapositivas de aspecto 16:9, el tema debe inyectar la siguiente declaración estricta de medios `@media print`:

```css
@media print {
  /* Forzar tamaño físico de página coincidente con la relación lógica 16:9 */
  @page {
    size: 1280px 720px;
    margin: 0;
  }
  
  /* Asegurar renderizado de colores de fondo e imágenes de fondo de servidor */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  
  /* Resetear el contenedor de presentación a modo bloque continuo */
  .presentation-container {
    position: static !important;
    width: 1280px !important;
    height: auto !important;
    overflow: visible !important;
    display: block !important;
  }
  
  html, body {
    width: 1280px !important;
    height: auto !important;
    overflow: visible !important;
    background-color: #000 !important; /* Mantiene cohesión cromática de bordes */
  }
  
  /* Forzar visualización y rotura de página en cada diapositiva */
  .slide {
    display: flex !important;
    position: relative !important;
    width: 1280px !important;
    height: 720px !important;
    transform: none !important; /* Desactiva escalado adaptativo de pantalla */
    opacity: 1 !important;
    visibility: visible !important;
    page-break-after: always !important;
    page-break-inside: avoid !important;
    break-after: page !important;
    break-inside: avoid !important;
    margin: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    border: none !important;
  }
  
  .slide:last-of-type {
    page-break-after: auto !important;
    break-after: auto !important;
  }
  
  .slide.layout-standard {
    display: grid !important;
    grid-template-rows: auto 1fr auto !important;
    grid-template-columns: 1fr !important;
  }
  
  /* Ocultar elementos interactivos, controles y barra de herramientas */
  .toc-sidebar, 
  .toc-overlay, 
  .nav-progress, 
  .bottom-controls, 
  .laser-pointer, 
  .lightbox-overlay, 
  .fab-container, 
  .nav-pill-container, 
  .presenter-console-container, 
  .sidebar-trigger {
    display: none !important;
  }
  
  /* Evitar roturas huérfanas en elementos de bloque pesados */
  .diagram-container, 
  .code-container {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }
}
```