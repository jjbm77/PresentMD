# Documento de Arquitectura Técnica y Diseño de Implementación: PresentMD
**Versión:** 1.0 (Release Candidate)  
**Autor:** Arquitecto de Software Senior & Escritor Técnico Principal  
**Fecha:** Junio 2026  

---

## 1. Resumen Ejecutivo y Filosofía de Diseño

### 1.1 Propósito del Sistema
**PresentMD** es un motor de transformación de alto rendimiento y un generador de sitios estáticos (SSG) especializado en la creación de presentaciones técnicas e interactivas a partir de texto plano en formato Markdown enriquecido con metadatos YAML. 

El sistema resuelve las ineficiencias inherentes a las herramientas de software tradicionales de presentaciones visuales (como Microsoft PowerPoint o Apple Keynote), las cuales sufren de:
1. **Falta de interoperabilidad con sistemas de control de versiones (Git):** Los archivos binarios pesados generan conflictos de combinación (merge conflicts) indescifrables.
2. **Desplazamiento del foco del autor:** Los desarrolladores y arquitectos pierden tiempo valioso en micro-ajustes visuales (alineación, márgenes, distribución manual) en lugar de centrarse en la consistencia de la lógica y los datos.
3. **Pérdida de portabilidad:** Dependencia de entornos de ejecución específicos o conectividad a internet para renderizar fuentes, temas y animaciones complejas.

### 1.2 Principios de Diseño
El diseño de PresentMD se rige por cuatro principios fundamentales:

*   **Markdown-First (La estructura es la verdad):** El contenido textual es soberano. La semántica del Markdown define automáticamente el layout y flujo de la información. El usuario nunca escribe HTML o CSS directo en el documento de contenido.
*   **Declarativo sobre Imperativo:** El autor declara *qué* componentes lógicos desea visualizar (ej: `:::kpi-grid` para métricas clave o `:::timeline` para roadmaps) y el motor infiere y optimiza de forma autónoma la posición, la tipografía y el flujo volumétrico según el tema visual activo.
*   **Rendimiento y Portabilidad Offline Extremos:** Las presentaciones finales se compilan en un único documento HTML autocontenido de carga instantánea, con tipografías y recursos críticos inyectados en Base64. Las transiciones interactivas se ejecutan nativamente en el navegador a 60 FPS mediante aceleración por hardware.
*   **Developer Experience (DX) Profesional:** Diseñado como una herramienta CLI que se integra en pipelines de CI/CD, permite depuración en vivo del Árbol de Sintaxis Abstracta (AST), diagnóstico de dependencias de sistema mediante comandos dedicados y recarga en caliente (Live Preview) sin parpadeo del navegador.

---

## 2. Stack Tecnológico

El motor de PresentMD está desacoplado en dos capa independientes: una capa de compilación en tiempo de build escrita en Python y una capa de interacción y renderizado en tiempo de ejecución escrita en Javascript Vanilla y CSS moderno.

```
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND (Python)                      │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────────┐  │
│  │    Typer     │   │ markdown-it-py│   │     Jinja2     │  │
│  │ (CLI Engine) │   │ (AST Parser)  │   │  (Templating)  │  │
│  └──────────────┘   └───────────────┘   └────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Compila a HTML Autocontenido
┌──────────────────────────────▼──────────────────────────────┐
│                      FRONTEND (Vanilla JS)                  │
│  ┌────────────────────────┐         ┌────────────────────┐  │
│  │   View Transitions API │         │   Canvas 2D API    │  │
│  │ (Cinematic Slide Anim) │         │ (Live Drawing/Lsr) │  │
│  └────────────────────────┘         └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Backend: Motor de Compilación (Python 3.12+)
*   **CLI Engine:** Se utiliza **`typer`** en conjunto con **`rich`**. Typer proporciona enrutamiento rápido de comandos y validación estricta de tipos de entrada. Rich se encarga de la salida en consola mediante paneles formateados, tablas visuales y árboles de renderizado jerárquicos para la visualización del AST.
*   **Parsing y AST:** **`markdown-it-py`**. Se selecciona debido a su arquitectura basada en tokens y reglas flexibles que permiten la inserción de plugins a nivel de lexer para procesar sintaxis personalizada sin romper el estándar CommonMark.
*   **Motor de Plantillas:** **`Jinja2`**. Permite aislar los archivos estructurales de layouts (`.html.j2`) y realizar una inyección segura y dinámica de variables del tema visual, diagramas pre-compilados y scripts JavaScript.
*   **Generador PDF:** **`playwright`** (Python Sync API). Permite instanciar un navegador Chromium Headless de forma programática, garantizando la renderización y rasterización pixel-perfect de diagramas SVG, scripts interactivos y fuentes inyectadas bajo reglas `@media print`.

### 2.2 Frontend: Motor de Interacción (Vanilla JS & CSS Nativos)
*   **Framework Frontend:** **Ninguno (Vanilla JS puro)**. Está estrictamente prohibida la introducción de React, Vue, Svelte o dependencias de Node.js en el cliente. Esto garantiza portabilidad total y un tiempo de carga inferior a 10ms.
*   **Estructura y Maquetación:** **CSS Grid y CSS Flexbox**. Se prohíbe el uso de posicionamiento absoluto para contenidos estructurados. CSS Grid proporciona el control bidimensional exacto para layouts complejos (como la comparación en paralelo), mientras que Flexbox distribuye los flujos verticales.
*   **Sistema de Variables:** **CSS Custom Properties (`--accent-primary`, etc.)**. Permiten desacoplar por completo el estilo estético del tema de la lógica de renderizado del motor.
*   **Animaciones y Transiciones:** **View Transitions API nativa** (`document.startViewTransition`). Permite capturar capturas de pantalla de los estados DOM salientes y entrantes y realizar transiciones cruzadas (cross-fade) o animaciones cinemáticas complejas a nivel del compositor del navegador, con fallback automático de opacidad en navegadores no compatibles.

### 2.3 Motores de Gráficos y Renderizado de Diagramas
El sistema procesa bloques de código con identificadores de lenguaje específicos (`d2` y `mermaid`) delegando la generación a herramientas de línea de comandos locales:
*   **D2:** Compilador local `d2` que genera layouts declarativos optimizados para diagramas de arquitectura.
*   **Mermaid:** Compilador CLI `mmdc` que genera diagramas de flujo y secuencias.
*   **Búsqueda Dinámica de Ejecutables:** El sistema no utiliza rutas absolutas fijas para invocar las herramientas externas. En su lugar, realiza un escaneo ordenado y dinámico en el sistema para encontrar `d2` y `mmdc` en el `PATH` global, en carpetas de control de versiones de Node (**NVM** como `~/.nvm/versions/node/v*/bin/mmdc`), **Volta** (`~/.volta/bin/mmdc`), y directorios globales de npm (`~/.npm-global/bin/mmdc`).
*   **Caché Persistente de Diagramas:** Se implementa un mecanismo de persistencia local en `~/.cache/presentmd/diagrams/`. Las compilaciones se guardan como SVGs indexados mediante un hash MD5 único calculado a partir del código fuente, motor utilizado y tokens de color del tema activo.
*   **Integración Cromática:** PresentMD intercepta la salida SVG cruda de estos motores y reemplaza dinámicamente las propiedades de estilo e inyecta reglas CSS inline para mapear los colores de conexión y bordes directamente a las variables del tema activo (ej: `--accent-primary` y `--accent-secondary`).

---

## 3. Arquitectura de Alto Nivel y Flujo de Datos

El flujo de procesamiento de PresentMD sigue un pipeline lineal unidireccional estructurado desde la ingesta del archivo plano hasta la entrega del entregable interactivo.

### 3.1 Pipeline de Transformación de Datos

```mermaid
graph TD
    A[Archivo Markdown (.md) + YAML Frontmatter] --> B[Slide Splitter: Separación por '---']
    B --> C[Frontmatter Extractor: Carga de metadatos YAML vía PyYAML]
    C --> D[Markdown-It-Py Parser: Tokenización del documento]
    D --> E[Custom Extension Plugins: Procesamiento de directivas y layouts]
    E --> F[AST Generator: Construcción de SlideElements Semánticos]
    F --> G[Engine Orchestrator: Inspección de diagramas D2/Mermaid]
    G --> H[ThreadPoolExecutor: Compilación concurrente de diagramas a SVG]
    H --> I[DiagramCache: Lectura/Escritura en cache local .cache/presentmd/]
    I --> J[Jinja2 Renderer: Unión de layouts HTML e inyección de CSS/JS]
    J --> K[HTML Autocontenido Final]
    K --> L[CLI Serve: Inyección de SSE / Servidor HTTP]
    K --> M[Playwright Headless: Generación de PDF Pixel-Perfect]
```

### 3.2 Flujo de Procesamiento Detallado

1.  **Ingesta y Segmentación:** El archivo de entrada es leído como UTF-8. El módulo `slide_splitter.py` realiza un pre-escaneo y segmenta el archivo utilizando la directiva lógica `---` (delimitador de diapositiva).
2.  **Extracción de Metadatos:** El primer bloque delimitado (Frontmatter) es parseado con `PyYAML`, extrayendo la configuración global de la presentación: tema visual, color de acento personalizado, logo, transiciones y estructura de barra de navegación.
3.  **Procesamiento del Lexer y Tokens:** Para cada diapositiva, una única instancia configurada de `markdown-it-py` procesa el contenido textual. Los plugins registrados interceptan la sintaxis personalizada (ej: directivas de bloque `:::` y de inline `[]{.badge}`).
4.  **Generación de la AST Interna:** Los tokens del parser se recorren linealmente y se agrupan en una lista de objetos `SlideElement` (definidos en `models.py`), los cuales tipifican con precisión el contenido (KPIs, tablas estructuradas, bloques de código, diagramas vectoriales, etc.) y su metadata asociada.
5.  **Compilación y Enlace de Gráficos:** El motor identifica los elementos tipo `diagram` y, utilizando un pool de hilos (`ThreadPoolExecutor`), compila los fragmentos concurrentemente a SVG vectorial utilizando la caché local basada en el hash MD5 del código y tema.
6.  **Ensamblaje del Layout (Jinja2):** La presentación completa se inyecta en el entorno de plantillas de Jinja2. Cada diapositiva es enviada a su template de layout específico (ej: `layouts/standard.html.j2` o `layouts/split_comparison.html.j2`) resolviendo la herencia visual y las variables del tema.
7.  **Inyección y Compilación Final:** Se realiza el inlining de las fuentes tipográficas en formato Base64 a partir del archivo binario local WOFF2, y se inyecta el código Javascript del controlador de navegación y presentación. El resultado es un único string HTML autocontenido.

---

## 4. Desglose de Componentes del Núcleo (Core Engine)

### 4.1 Markdown Parser Extensible (`ast_builder.py` & `plugins/registry.py`)
El parsing extensible está diseñado bajo un patrón de registro de componentes desacoplado. En lugar de procesar los tokens de forma imperativa dentro del compilador central, el sistema registra clases de plugins en `ComponentRegistry` que implementan el protocolo `ComponentPlugin`.

```python
class ComponentPlugin(Protocol):
    @property
    def name(self) -> str: ...
    def render_html(self, content: str, metadata: Dict[str, Any], render_inline: callable) -> str: ...
```

#### Mecanismo de Intercepción de Directivas:
1.  **Directivas de Layout (`::layout{name}`):** Interceptadas por `layout_directive_plugin` en la fase de tokenización. Se extrae el nombre del layout y los atributos opcionales colocándolos en la metadata del slide para determinar el template Jinja2 de destino.
2.  **Contenedores Personalizados (`:::`):** Interceptadas por `container_plugin`. El lexer de `markdown-it` detecta el inicio y fin de las tres marcas de dos puntos (`:::kpi-grid` ... `:::`) y asocia el bloque con un token tipo `container_name_open`.
3.  **Extracción Semántica:** En `ast_builder.py`, el método `_convert_tokens_to_elements` procesa estos tokens especializados aplicando expresiones regulares optimizadas para extraer colecciones tipadas de datos:
    *   **KPIs:** `^\-\s*\[(.+?)\]\s*(.+?)(?:\s*\{status:\s*(\w+)\})?\s*$` extrae el valor masivo, etiqueta explicativa y el estado semántico de criticidad.
    *   **Timeline:** Identifica fases mediante viñetas en negrita (`- **Badge**: Título`), sub-items e hitos de entrega representados por citas (`> entregable`).
    *   **Progress-bars:** `^\-\s*(.+?):\s*(\d+)%(?:\s*\{color:\s*(\w+)\})?\s*$` captura etiquetas, porcentajes y variaciones de color de barra.
    *   **Parallel-compare:** Divide el cuerpo interno del bloque utilizando el delimitador secundario `---`, mapeando el contenido a un layout de doble columna (izquierdo y derecho) con un badge central opcional (`center-badge="VS"`).

### 4.2 Gestor de Estado de la Presentación (Javascript Controller)
El estado de la presentación interactiva es gestionado en el cliente a través de una función autoejecutable (IIFE) que encapsula el contexto y evita la polución del espacio de nombres global.

```javascript
(function() {
  const slides = document.querySelectorAll('.slide');
  const total = slides.length;
  let current = 0;
  let history = []; // Pila LIFO para navegación no lineal
  let laserActive = false;
  let drawingActive = false;
  // ...
})();
```

#### Control de Secuencias e Historial:
*   **Segmentación del Flujo Cronológico:** Durante la inicialización, el motor recorre los slides del DOM y construye un mapa de secuencia normal (`normalSequence`). Los slides marcados como anexos (`data-annex="true"`) reciben un valor de secuencia nulo (`null`).
*   **Persistencia del Estado:** Cada cambio de diapositiva exitoso registra el índice actual en el almacenamiento de sesión del navegador (`sessionStorage.setItem('pmd_current_slide', current)`). Esto garantiza que el flujo de presentación continúe en la diapositiva exacta en caso de recargas en caliente (hot-reloads) del servidor de desarrollo o recarga manual del usuario.
*   **Enrutamiento de Diapositivas:** El método central `goTo(idx, direction)` coordina la remoción de la clase `.active` de la diapositiva anterior, aplica la clase a la nueva diapositiva, fuerza un reflow del DOM (`slide.offsetHeight`) para reiniciar animaciones CSS y llama a la función de auto-escalado de fuentes.

### 4.3 Motor de Interactividad (Stepping System)
El motor de interactividad permite realizar pasos secuenciales (sub-pasos) dentro de una única diapositiva antes de cambiar el índice de slide. Cuando el usuario presiona las teclas de navegación o hace clic en el canvas, el controlador intercepta el evento e inspecciona la cola de pasos activos (`slideSteps`) del slide actual.

```javascript
function handleNext() {
  if (currentSlideStepIndex < slideSteps.length) {
    slideSteps[currentSlideStepIndex].action();
    currentSlideStepIndex++;
  } else {
    next(); // Cambiar de diapositiva
  }
}
```

El sistema inicializa la colección `slideSteps` dinámetamente cada vez que se carga un slide en función de su contenido interactivo:

1.  **Pasos de Listas (`:::steps`):**
    *   **Estructura:** Lista ordenada o desordenada donde cada elemento posee inicialmente la clase CSS `.step-hidden` (`opacity: 0`).
    *   **Acción:** La llamada progresiva remueve `.step-hidden` e inyecta la clase `.step-visible` aplicando transiciones de opacidad y transformaciones verticales suaves.
    *   **Deshacer:** En caso de navegación reversa (`handlePrev`), el paso aplica nuevamente `.step-hidden`.

2.  **Pilas de Capas (`:::layer-stack`):**
    *   **Estructura:** Contenedor de imágenes posicionadas de forma absoluta y apiladas jerárquicamente en el eje Z. La primera imagen (índice 0) posee la clase `.active`, mientras que las demás poseen `.layer-hidden`.
    *   **Acción:** Cada paso sucesivo aplica `.active` a la siguiente capa del stack, permitiendo la sobreposición progresiva de diagramas técnicos sin cambiar de slide.

3.  **Paso a Paso de Líneas de Código (Code Stepping):**
    *   **Estructura:** Bloques de código con marcado de líneas específicas (ej: `{1|2-3|all}`). Durante la compilación, el parser inyecta los grupos de líneas estructuradas en el atributo `data-code-steps` en formato JSON y envuelve las líneas en elementos `span.code-line` con el atributo `data-line`.
    *   **Acción:** El paso dinámico lee las líneas activas del paso actual. Inyecta la clase `.highlight-active` a las líneas indicadas y atenúa el resto de las líneas del bloque reduciendo su opacidad a `0.3` a nivel de CSS del contenedor `.code-container.stepping`.

---

## 5. Implementación de Funcionalidades Avanzadas

### 5.1 View Transitions API Nativa
PresentMD saca provecho de la API nativa de transición de vistas de los navegadores modernos para proporcionar transiciones cinemáticas fluidas a 60 FPS sin necesidad de sobrecargar el frontend con librerías de animación pesadas (como GreenSock o Framer Motion).

```javascript
const performGoTo = () => {
  // Código de manipulación de clases DOM para cambiar el slide activo
};

if (document.startViewTransition) {
  document.startViewTransition(performGoTo);
} else {
  performGoTo(); // Fallback tradicional
}
```

#### Ciclo de Vida de la Transición de Vistas:
1.  Al llamar a `document.startViewTransition()`, el navegador captura una instantánea visual del estado actual de la presentación (Lámina A).
2.  Se ejecuta el callback síncrono `performGoTo` que actualiza el DOM retirando la clase `.active` de la diapositiva A y asignándosela a la diapositiva B.
3.  El navegador captura el estado resultante (Lámina B).
4.  Se ejecuta una animación nativa por defecto (cross-fade) entre ambas vistas a nivel del motor del renderizador del navegador. Los temas visuales pueden personalizar esta animación extendiendo el pseudoelemento `::view-transition-group` en el archivo `styles.css`.

### 5.2 Navegación No Lineal e Historial de Anexos
Las presentaciones técnicas de arquitectura requieren la capacidad de responder a preguntas de la audiencia saltando a detalles profundos y retornando rápidamente al flujo principal.

```
                  Salto a Anexo (Ej: #anexo-costos)
  Lámina Normal ────────────────────────────────────► Diapositiva de Anexo
        ▲                                                      │
        │             Botón "Volver" / Back                    │
        └──────────────────────────────────────────────────────┘
                  history.pop() -> goTo(lastIndex)
```

*   **Identificación del Anexo:** Los slides con directiva `::layout{annex}` se compilan con el atributo `data-annex="true"` y la clase CSS `.annex`. Estos slides son ignorados por el indexador de páginas normal (no alteran el conteo de páginas de la presentación) y son omitidos de la secuencia de teclas directas (flecha derecha/izquierda no los cargan de forma accidental).
*   **Mecanismo de Enlace Profundo (Deep Linking):** Los hipervínculos marcados con la clase `.link-detalle` o `.link-anexo` (sintaxis Markdown: `[Ver detalle →](#anexo-costos){.link-detalle}`) poseen un escuchador de eventos click delegado en JavaScript. Al activarse:
    1.  Se captura el slide destino resolviendo el selector ID (ej: `#anexo-costos`).
    2.  Se guarda el índice de la diapositiva actual en la pila `history` (`history.push(current)`).
    3.  Se ejecuta la transición inmediata al slide anexo.
*   **Retorno al Contexto (Mecanismo "Volver"):** Las diapositivas anexas implementan de forma estructural un botón con la clase `.btn-volver`. Al hacer clic en este botón, el controlador de JavaScript ejecuta:
    ```javascript
    if (history.length > 0) {
      goTo(history.pop(), 'backward');
    } else {
      prev(); // En caso de que no haya historial previo
    }
    ```

### 5.3 Herramientas de Presentador en Vivo (Canvas API & Laser Mode)
Para mejorar la dinámica de las exposiciones en vivo, el shell base incluye dos capas de anotación superpuestas interactuando directamente con los eventos del dispositivo apuntador.

```
┌─────────────────────────────────────────────────────────────┐
│                    VIEWPORT DEL NAVEGADOR                   │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Capa Laser Pointer Overlay (#laserPointer)         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2. Capa Drawing Canvas Overlay (#drawingCanvas)       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 3. Capa Contenedor de Diapositiva (.slide.active)     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Capa de Dibujo Libre (Drawing Canvas):
*   **Implementación:** Un elemento HTML5 `<canvas id="drawingCanvas">` se posiciona de forma fija cubriendo el 100% de la pantalla por encima de las diapositivas (`z-index: 1000`).
*   **Captura de Trazos:** Al activarse mediante la tecla `d`/`D` o el botón de la interfaz, el canvas añade escuchadores para eventos `mousedown` / `mousemove` / `mouseup` (y sus contrapartes táctiles `touchstart` / `touchmove` / `touchend`).
*   **Estilos Dinámicos:** Los trazos se dibujan aplicando interpolación de líneas suaves en el contexto 2D (`canvasCtx.lineTo(x, y)`), utilizando un grosor de trazo de `4px` y recuperando el color primario del tema activo directamente desde el DOM mediante:
    `getComputedStyle(document.documentElement).getPropertyValue('--accent-primary')`.
*   **Persistencia por Slide:** Para evitar que las anotaciones se mezclen al cambiar de lámina, el controlador guarda el estado del canvas antes de realizar cualquier transición convirtiendo el lienzo a una URI de datos Base64 y almacenándolo en un diccionario indexado por el índice de la diapositiva:
    `savedDrawings[current] = drawingCanvas.toDataURL();`
    Al retornar o cargar una diapositiva, se limpia el lienzo y se vuelve a pintar la imagen almacenada.

#### Capa de Puntero Láser (Laser Mode):
*   **Implementación:** Un elemento circular `#laserPointer` posicionado absolutamente en el viewport con un diseño radial difuminado de color rojo brillante (`box-shadow: 0 0 20px 8px #ff0000`).
*   **Funcionamiento:** Al activarse mediante la tecla `l`/`L` o el botón respectivo, se interceptan los eventos globales de movimiento del ratón (`mousemove`), actualizando las propiedades CSS de posicionamiento `left` y `top` con las coordenadas del cursor del ratón. El puntero físico del sistema se oculta en CSS utilizando `cursor: none` en todo el cuerpo de la presentación.

### 5.4 Modo Presentador de Doble Ventana Offline
El sistema incorpora un modo de consola de presentador avanzado y autocontenido diseñado para ejecutarse en configuraciones de pantalla doble o proyecciones.

*   **Activación:** Se puede iniciar haciendo clic en el botón de presentador (👨‍🏫) en la barra de navegación o presionando la tecla `p` / `P`. Esto abre una ventana secundaria apuntando al parámetro de consulta `?presenter=true`.
*   **Layout de la Consola:**
    *   **Panel Izquierdo:** Muestra una vista previa en miniatura de la lámina actual (ajustada y escalada dinámicamente mediante JavaScript según el ancho disponible) y las notas de presentador (`data-notes`) renderizadas a un tamaño de fuente legible.
    *   **Panel Derecho:** Muestra la vista previa del siguiente slide no anexo y dos herramientas de temporización: un reloj digital local de sistema y un cronómetro con botón de reinicio rápido.
*   **Sincronización Bidireccional:** Las dos ventanas se comunican en tiempo real de forma bidireccional utilizando `localStorage` (mediante escuchas del evento `storage`) complementado con `postMessage`. Esto permite sincronizar de forma instantánea el cambio de diapositiva o de paso interactivo incluso si la máquina se encuentra completamente aislada de internet.

---

## 6. Pipeline de Build y Exportación (CLI)

El CLI de PresentMD (desarrollado con `typer` y formateado con `rich`) expone una interfaz limpia de comandos de sistema que controlan todo el ciclo de vida del desarrollo y entrega del material técnico.

### 6.1 Comando `serve` (Servidor de Desarrollo y Live Preview)
Levanta un entorno interactivo local diseñado para la co-creación de contenido en tiempo real.

```
 [Editor de Texto] (Guarda archivo.md)
        │
        ▼ (Sistema de archivos detecta modificación)
 [PresentMD CLI (watchdog)] ──► Recompila archivo.md a HTML
        │
        ▼ (Notifica recarga vía SSE /events)
 [Navegador Web (EventSource)] ──► Lee 'reload' ──► sessionStorage.save() ──► location.reload()
```

1.  **Orquestación del Servidor HTTP:** Instancia un servidor HTTP multihilo local utilizando `ThreadingHTTPServer` sobre un puerto configurable (por defecto, `8000`).
2.  **Monitoreo de Archivo:** El sistema de eventos de archivos de PresentMD intenta cargar la librería `watchdog` para suscribirse directamente a los eventos lógicos del kernel de sistema de archivos (`on_modified`). Si la librería no se encuentra instalada en el entorno, el CLI implementa un fallback transparente de polling pasivo utilizando un bucle secundario con chequeos periódicos de la fecha de última modificación del archivo (`os.stat(path).st_mtime`) cada 500ms.
3.  **Mecanismo de Recarga vía Server-Sent Events (SSE):** El handler del servidor HTTP expone el endpoint `/events`. Cuando un navegador abre la presentación compilada con la bandera `live_reload=True`, inicializa una conexión continua de lectura persistente vía `EventSource('/events')`.
4.  **Notificación de Cambio:** Al detectarse una modificación en el `.md` de origen, el subproceso del watcher ejecuta inmediatamente la compilación en caliente. Si la compilación es exitosa, se señalan todos los sockets de clientes activos registrados en la lista de hilos globales `_sse_clients` inyectando la cadena binaria `data: reload\n\n` en el socket, forzando la recarga instantánea del navegador.

### 6.2 Comando `build` (Generación Estática Autocontenida)
Construye la versión final optimizada para distribución o publicación web.

*   **Flujo de Trabajo:**
    1.  Parsea el Markdown de origen y procesa el frontmatter YAML.
    2.  Genera el AST lúdico e invoca el resolvedor de diagramas en paralelo.
    3.  Lee las fuentes tipográficas locales (ej: `DMMono-Regular.woff2`) y las inyecta directamente como una regla `@font-face` en base64 en la sección `<style>` del HTML.
    4.  Localiza el logotipo especificado en el frontmatter, valida su canal alfa de transparencia para evitar layouts rotos si es PNG/SVG, y lo empaqueta como Data URI base64 en el cuerpo de la presentación.
    5.  Crea un subdirectorio `output/` y escribe el archivo HTML resultante. Copia además los recursos de imagen locales referenciados en el documento Markdown para asegurar la visibilidad offline.

### 6.3 Comando `build -f pdf` (Exportación Pixel-Perfect)
Genera el documento en formato de impresión de alta resolución utilizando automatización de navegadores headless.

*   **Paso 1: Generación del HTML Intermedio:** Ejecuta de forma síncrona el flujo del comando `build` generando un archivo HTML local en el subdirectorio temporal.
*   **Paso 2: Instanciación Headless:** Invoca a `playwright.sync_api` e inicia un navegador Chromium aislado con un viewport configurado exactamente a una resolución de 16:9 (`1280x720`).
*   **Paso 3: Sincronización del Estado de Red:** El script carga el HTML local a través del protocolo `file://`. Espera a que se cumplan las promesas lógicas de red y renderizado utilizando los estados:
    *   `networkidle`: Asegura que no existan peticiones de red activas.
    *   `domcontentloaded`: Confirma la carga completa del árbol DOM.
    *   `wait_for_timeout(500)`: Agrega una pausa de 500ms requerida para la correcta inicialización y renderizado estático de los diagramas SVG generados por Mermaid o D2 y los bloques con resaltado de sintaxis.
*   **Paso 4: Impresión PDF:** Llama al método nativo de automatización del navegador `page.pdf` configurando:
    *   `print_background=True` para inyectar los colores del canvas y overlays.
    *   `width="1280px"` y `height="720px"` para coincidir con las proporciones de diapositiva.
    *   `prefer_css_page_size=True` para heredar las especificaciones de márgenes y saltos de página de `@media print`.

### 6.4 Comando `debug` (Inspección AST)
Diseñado para ingenieros y desarrolladores que desean extender el framework.
*   **Funcionamiento:** Parsea el archivo Markdown y vuelca en la terminal una representación visual y jerárquica del AST. Imprime una tabla estructurada de los metadatos leídos del Frontmatter y genera un árbol visual mediante la API `rich.tree.Tree`, mostrando detalladamente los tipos de elementos lógicos (`heading`, `diagram`, `code_block` con sus números de línea de highlight y variaciones paso a paso, `container` personalizados con sus atributos asociados) y las notas de presentador asociadas a cada lámina.

### 6.5 Comando `doctor` (Diagnóstico del Entorno)
Comando autocontenido para la resolución y verificación de requerimientos en la máquina del usuario final.
*   **Funcionamiento:** Realiza un escaneo de diagnóstico general y dibuja una tabla con el estado de:
    1.  La versión e intérprete activo de Python.
    2.  La disponibilidad y versión de la CLI de D2.
    3.  La disponibilidad y versión de la CLI de Mermaid (`mmdc`).
    4.  La instalación del SDK de Python de Playwright.
    5.  La descarga e instalación del navegador Chromium de Playwright requerido para la exportación a PDF.

---

## 7. Consideraciones de Rendimiento y Escalabilidad

### 7.1 Algoritmo de Auto-Escalado Lógico (Fit-to-Screen)
Una de las mayores problemáticas en presentaciones generadas desde código es el desbordamiento de texto (overflow) cuando el volumen de contenido excede los límites físicos de la diapositiva. PresentMD implementa un sistema híbrido de escalado que combina transformación geométrica coordinada de contenedores y compresión dinámica de fuentes tipográficas en base a mediciones del DOM en tiempo real.

```
┌─────────────────────────────────────────────────────────────┐
│                    ESCALADO BIDIMENSIONAL                   │
│                                                             │
│   [Ventana del Navegador (vw, vh)]                          │
│                  │                                          │
│                  ▼ Calcula factor de escala (X e Y)         │
│   Aplicación de transform: scale(factor) en .slide          │
│   (Garantiza proporciones exactas de aspecto 1280x720)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   COMPRESIÓN DE FUENTE (DOM)                │
│                                                             │
│   ¿slide.scrollHeight > 720px?                              │
│          ├── SI ──► Disminuye font-size raíz (16px -> 9.6px)│
│          └── NO ──► Mantiene tamaño de fuente óptimo        │
└─────────────────────────────────────────────────────────────┘
```

#### Fase 1: Ajuste de Relación de Aspecto (Escalado Geométrico)
Durante la carga de la diapositiva y en cada evento de redimensionamiento de ventana (`resize`), el controlador de JavaScript ejecuta la función `scaleSlides()`. Esta calcula la proporción óptima entre la ventana actual y la diapositiva base de 1280px x 720px:
```javascript
const scaleX = window.innerWidth / 1280;
const scaleY = window.innerHeight / 720;
const scale = Math.min(scaleX, scaleY);
```
Posteriormente aplica `transform: scale(${scale})` y calcula el desplazamiento central para centrar la diapositiva en el viewport.

#### Fase 2: Reducción de Fuente Dinámica por ScrollHeight
Tras escalar geométricamente, se invoca `autoScaleSlideContent(slide)`. 
1.  Se inicializa la propiedad de tamaño de fuente del documento raíz en `16px`.
2.  Se mide la altura real del contenido interno de la diapositiva utilizando `slide.scrollHeight`.
3.  Si `scrollHeight` es superior a la altura máxima permitida de `720px`, el script ejecuta un bucle iterativo de compresión: reduce progresivamente el tamaño de fuente en decrementos porcentuales de `2%` (disminuyendo el tamaño de fuente del elemento raíz html) mientras el contenido exceda los límites, deteniendo la reducción al alcanzar un tamaño mínimo seguro del `60%` (`9.6px`).
4.  Si la diapositiva aún presenta desbordamiento al alcanzar el límite, el CLI del backend emitirá una advertencia explícita en consola durante el build para alertar al diseñador de que simplifique la estructura de la diapositiva.

### 7.2 Caché de Diagramas Concurrente (DiagramCache & ThreadPool)
Compilar diagramas a SVG vectorial mediante procesos locales de NodeJS o D2 es una operación costosa en procesamiento y tiempo de CPU (usualmente oscilando entre 1 y 3 segundos por diagrama).
*   **Compilación Concurrente:** Para evitar retrasos lineales en la compilación de presentaciones masivas con múltiples diagramas, el módulo de compilación escanea la presentación y ejecuta los comandos de traducción en paralelo aprovechando la multiprogramación del procesador mediante `ThreadPoolExecutor` de Python.
*   **Estrategia de Caché Local:** Cada diagrama compilado exitosamente se guarda en el disco local en `~/.cache/presentmd/diagrams/`. El nombre del archivo SVG guardado corresponde al hash hexadecimal MD5 calculado a partir de la firma de entrada:
    `hash_key = md5(idioma_diagrama + codigo_fuente + color_accent + tema_d2)`.
    En compilaciones subsecuentes, el motor verifica la existencia del hash en la caché antes de realizar cualquier llamada a subprocesos externos, reduciendo el tiempo de build de segundos a milisegundos en ejecuciones sucesivas.

---

## 8. Guía de Extensibilidad (Para Desarrolladores)

### 8.1 Cómo Agregar un Nuevo Componente Personalizado
Para registrar un nuevo bloque estructurado (ej: `:::nuevo-componente`) en el pipeline de compilación de PresentMD, se deben seguir tres pasos de implementación:

#### Paso 1: Definición del Componente en el Registro de Plugins
Crear una nueva clase que cumpla el protocolo de plugin en `src/presentmd/plugins/registry.py` y registrarla:

```python
class NuevoComponente:
    @property
    def name(self) -> str:
        return "nuevo-componente"

    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        # Extraer variables personalizadas o iterar sobre elementos
        items = metadata.get("items", [])
        color = metadata.get("attrs", {}).get("color", "normal")
        
        rendered_items = "".join(f"<li>{render_inline(i)}</li>" for i in items)
        return f'<div class="nuevo-comp-box {color}"><ul>{rendered_items}</ul></div>'

# Registrar el componente al final del archivo
component_registry.register(NuevoComponente())
```

#### Paso 2: Configurar la Tokenización en el AST Builder
Modificar `src/presentmd/parser/ast_builder.py` para añadir la regla de parseo de datos correspondiente a tu componente en la función `_convert_tokens_to_elements`.

```python
# Dentro del bloque de parsing de containers custom:
elif container_name == "nuevo-componente":
    # Analizar el cuerpo de texto en container_content y extraer items
    # Ejemplo: parsing de viñetas simples
    metadata["items"] = _parse_steps_items(container_content)
```

#### Paso 3: Definir la Estructura y Estilos en el CSS
Añadir las reglas visuales para la clase `.nuevo-comp-box` y sus variaciones en el CSS de los temas o en `base.html.j2` si es un componente estructural global.

```css
.nuevo-comp-box {
  background: var(--bg-chrome);
  border-left: 4px solid var(--accent-primary);
  padding: 16px;
  border-radius: 8px;
}
.nuevo-comp-box.destacado {
  border-color: var(--accent-secondary);
}
```

### 8.2 Cómo Crear un Nuevo Tema Visual Completo
PresentMD delega la apariencia cromática a archivos CSS puros y autónomos. Para crear un tema llamado `custom-dark`:

#### Paso 1: Configurar el Directorio
Crea una carpeta en el directorio de plantillas del sistema o en la ruta de configuración del usuario:
*   **Ruta del framework:** `src/presentmd/templates/themes/custom-dark/styles.css`
*   **Ruta de usuario (Linux/macOS):** `~/.config/presentmd/themes/custom-dark/styles.css`
*   **Ruta de usuario (Windows):** `%APPDATA%\presentmd\themes\custom-dark\styles.css`

#### Paso 2: Implementar Design Tokens Obligatorios
El archivo `styles.css` debe declarar en la pseudo-clase `:root` los tokens tipográficos y cromáticos requeridos por el core y los plugins:

```css
:root {
  /* Paleta Cromática Principal */
  --bg-canvas: #0f172a;       /* Fondo del cuerpo de la diapositiva */
  --bg-chrome: #1e293b;       /* Fondos de títulos, menús e indexador */
  --text-main: #f8fafc;       /* Texto principal legible */
  --text-muted: #94a3b8;      /* Metadatos y subtítulos */

  /* Colores de Acento y Estados Semánticos */
  --accent-primary: #f59e0b;  /* Cobre/Amarillo de marca */
  --accent-secondary: #3b82f6;/* Azul secundario */
  --accent-blue: #3b82f6;     /* Alerta informativa */
  --accent-red: #ef4444;      /* Alerta crítica / KPI crítico */
  --accent-yellow: #f59e0b;   /* Alerta de precaución */
  --accent-green: #10b981;    /* Alerta de éxito */

  /* Tipografías Nativas Fallback (Compatibilidad Offline) */
  --font-body: 'Segoe UI', system-ui, -apple-system, sans-serif;
  --font-mono: 'DM Mono', monospace;
}
```

#### Paso 3: Estilar Componentes Específicos
Sobrescribe las clases estéticas de los componentes para asegurar legibilidad sobre el nuevo fondo (ej: `.kpi-card`, `.alert-box`, `.nav-arrow-btn`). El framework automáticamente aplicará los espaciados, layouts estructurales y la lógica de interacción basándose en estos tokens estéticos.
