# PresentMD: AI Theme Generation Guide

> **Nota para Modelos de Lenguaje (LLMs / IAs):**  
> Si un usuario te solicita crear un tema para **PresentMD**, **NO** debes modificar el código fuente del framework (Python o `base.html.j2`). PresentMD utiliza una arquitectura 100% modular basada en CSS. Tu tarea es generar **únicamente** un archivo `styles.css`.

---

## 1. Arquitectura y "Guardrails" del Framework
Un tema en PresentMD consiste en un archivo `styles.css` dentro de la carpeta `src/presentmd/templates/themes/<nombre-del-tema>/`.

**¡IMPORTANTE!** El motor interno de PresentMD (`base.html.j2`) YA SE ENCARGA de la ingeniería estructural dura. El framework garantiza que la lámina nunca se rompa.
*   El framework ya maneja los `display: flex`, `display: grid`, y los centramientos estructurales de todos los Layouts.
*   **Tu responsabilidad en el tema CSS es puramente volumétrica y estética:** Colores, tipografías, opacidades, sombras (`box-shadow`), bordes, radios (`border-radius`), y los espaciados internos (`padding`, `gap`).

---

## 2. Tipografías y Soporte Offline (Fonts)
PresentMD está diseñado para poder ejecutarse 100% offline (sin internet). 

**Reglas de Tipografía:**
1.  Puedes intentar cargar una fuente web (ej. `@import url('https://fonts.googleapis.com/...');`) en la primera línea, **PERO**
2.  **SIEMPRE debes proveer una cadena de respaldo (fallback) hacia fuentes nativas del sistema** (`system-ui`, `-apple-system`, `Segoe UI`, `Roboto`, `sans-serif`) para garantizar que la presentación se vea perfecta si el usuario no tiene internet.

Debes proveer tres variables principales de fuentes en `:root`:
```css
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Product+Sans:wght@400;700&family=Fira+Code&display=swap');

:root {
  /* Falla de forma segura hacia system-ui si no hay internet */
  --font-body: 'Roboto', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-heading: 'Product Sans', 'Roboto', system-ui, -apple-system, sans-serif;
  --font-mono: 'Fira Code', ui-monospace, 'Cascadia Code', monospace;
}
```

---

## 3. Design Tokens (Variables Base)
Debes definir el bloque `:root`. Estos son los tokens obligatorios que PresentMD y sus plugins usan:

```css
:root {
  /* Paleta Core */
  --bg-canvas: #ffffff;       /* Fondo principal de la lámina */
  --bg-chrome: #f8f9fa;       /* Fondo de las barras de título/menú */
  --text-main: #202124;       /* Texto primario */
  --text-muted: #5f6368;      /* Texto secundario / metadatos */
  
  /* Acentos (Requeridos para componentes UI) */
  --accent-primary: #4285F4;  /* Resaltados, enlaces principales */
  --accent-blue: #4285F4;     /* Alertas informativas */
  --accent-red: #EA4335;      /* Errores / KPI Crítico */
  --accent-yellow: #FBBC05;   /* Precaución / KPI Medio */
  --accent-green: #34A853;    /* Éxito / KPI Bueno */
  
  --border-color: rgba(0, 0, 0, 0.1);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
}
```

---

## 4. Estilos de Layouts (Solo Espaciados)
Como el framework ya definió el modelo de cajas, tú solo debes inyectar los "aires" (espaciados) para que el diseño respire:

* `.layout-title`: Generalmente no requiere CSS adicional a menos que quieras ajustar el espacio entre el H1 y el H2.
* `.layout-standard`: Añade un padding general. (Ej. `padding: 40px;`).
* `.layout-standard .slide-body`: Ajusta el espaciado interior. (Ej. `gap: 20px; padding-top: 20px;`).
* `.layout-split-comparison .slide-body`: El framework ya armó la grilla. Tú solo define el espacio entre columnas. (Ej. `gap: 40px;`).

---

## 5. Componentes de UI Semánticos
Debes estilar los siguientes elementos para que el tema se vea completo y funcional:

### Controles de Navegación y UI Flotante
* `.nav-arrow-btn`, `.fs-btn`: Botones circulares (Color de fondo, `border-radius: 50%`, bordes, y un estado `:hover`).
* `.fs-btn.active`: El estado cuando herramientas como el láser o el lápiz están activadas. **Asegúrate de darle un color de fondo sólido llamativo** (ej. `background: var(--accent-primary)`) para que el usuario sepa que la herramienta está encendida.
* `.slide-counter`: Píldora de contador de láminas.
* `.nav-progress-fill`: El relleno de la barra de progreso inferior (`background: var(--accent-primary)`).
* `.spotlight-tooltip`: Caja informativa del foco magnético (Fondo, bordes redondeados y sombra).

### Interactividad Extendida
* `.lightbox-overlay`: Fondo modal oscuro o desenfocado (`background: rgba(0,0,0,0.9)` o `backdrop-filter`).
* `.lightbox-controls`, `.lightbox-btn`, `.lightbox-close`: Estética de los botones del visor de imágenes.
* `.diagram-container.fallback`, `.diagram-fallback-header`, `.diagram-fallback-code`: Estilos mostrados cuando un diagrama D2 falla.

### Componentes de Lámina
* `.kpi-card`: Tarjetas numéricas (`background`, `border-radius`, `box-shadow`). Las sub-clases `.critical`, `.amber` y `.green` colorean el `.kpi-value`.
* `.alert-box.red`, `.alert-box.green`, `.alert-box.amber`, `.alert-box.blue`: Cajas de notas / warnings.

### Código y Resaltado de Sintaxis
PresentMD utiliza Pygments (HTML) puro. Debes definir los colores de sintaxis:
* `.code-container`: Contenedor del bloque de código.
* `.highlight-active`: Línea activa en Code Stepping.
* Clases de Pygments (ej. `.c` comentarios, `.k` keywords).
