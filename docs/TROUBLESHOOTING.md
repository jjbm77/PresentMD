# Resolución de Problemas y FAQ (`docs/TROUBLESHOOTING.md`)

Este documento provee soluciones técnicas rápidas ("Primeros Auxilios") para resolver problemas comunes relacionados con la visualización, la recarga en tiempo real, el rendimiento y la exportación de diapositivas en **PresentMD**.

---

## 1. Desbordamiento y Cortes de Texto (Fuentes y Contenedores)

### ❓ ¿Por qué algunos textos o bloques se cortan o sobresalen del contenedor de la diapositiva?
**Causa:** 
El motor de PresentMD ejecuta un algoritmo de auto-escalado y ajuste interactivo (Fit-to-Screen) del lado del cliente. Este algoritmo calcula las proporciones del canvas virtual de `1280px × 720px` (relación de aspecto 16:9). Si se definen tamaños de fuentes, espaciados (`margin`, `padding`) o anchos en píxeles absolutos (`px`), estos valores no escalarán de forma proporcional cuando cambie el tamaño de la ventana de visualización, provocando desbordamientos (overflow).

**Solución:**
1. **Usa unidades relativas:** Utiliza exclusivamente unidades `rem` o `em` para los tamaños de fuente y espaciados, y porcentajes (`%`) o `vw`/`vh` para los anchos y altos en las hojas de estilo del tema.
2. **Evita declarar alturas fijas:** Evita declarar `height: 400px` en tus componentes o selectores. En su lugar, utiliza `max-height` o deja que el flujo natural del texto (basado en flexbox/grid con unidades relativas) determine el tamaño.
3. **Advertencia de Desbordamiento del Compilador:** Al compilar, presta atención a la advertencia del CLI en la terminal: `[bold yellow]ADVERTENCIA DE DESBORDAMIENTO[/bold yellow]`. Si tu diapositiva excede los 15 elementos o los 1200 caracteres, el compilador activará automáticamente el layout `scrollable` de seguridad para evitar que el contenido se pierda.

---

## 2. Problemas de Live-Reload (Recarga en Vivo)

### ❓ Ejecuto `presentmd serve` pero las diapositivas no se actualizan al guardar cambios en el Markdown.
**Causa:**
El servidor local utiliza Server-Sent Events (SSE) a través de la ruta `/events` para notificar al navegador de los cambios. La detección en el backend de Python depende de la librería `watchdog` para interactuar con la API de eventos de archivos del sistema operativo (por ejemplo, `inotify` en Linux o `FSEvents` en macOS). Si `watchdog` no está instalado o los límites del sistema de inotify se han agotado, el servidor no enviará la señal de actualización.

**Solución:**
1. **Verifica la instalación de watchdog:** Asegúrate de haber instalado el extra `serve` al preparar el entorno:
   ```bash
   pip install ".[serve]"
   ```
2. **Ajusta los límites de inotify (Linux):** Si ves un error de inotify en la terminal, incrementa el número máximo de relojes de archivos del sistema operativo:
   ```bash
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
   ```
3. **Mecanismo de Polling (Fallback):** Si estás trabajando en un entorno virtualizado (como Docker o WSL) donde los eventos del sistema de archivos no se propagan correctamente, puedes forzar un comportamiento de sondeo (polling) del lado del navegador en la consola de JavaScript para verificar cambios cada 500ms si el canal SSE `/events` falla.

---

## 3. Caché de Imágenes y Activos Locales

### ❓ Cambié una imagen o el logotipo en mi carpeta local pero el navegador sigue mostrando la versión vieja.
**Causa:**
Para que la presentación sea portátil e independiente de una conexión de red, PresentMD convierte las imágenes locales a Data URIs codificados en Base64 en el HTML de salida (`/output`). El navegador web tiende a cachear fuertemente las peticiones de recursos embebidos o del mismo servidor local.

**Solución:**
1. **Forzar reconstrucción limpia:** Ejecuta el comando de compilación o servidor forzando la reescritura del directorio compilado `/output`:
   ```bash
   # Compilar limpiando el output
   presentmd build presentation.md --output-dir ./output
   ```
2. **Forzar recarga en el navegador (Hard Refresh):** Abre las herramientas de desarrollo de tu navegador (F12) y realiza una recarga forzada limpia presionando `Ctrl + F5` o `Cmd + Shift + R` (en macOS).
3. **Desactivar caché de red:** En las herramientas de desarrollo (pestaña "Network" o "Red"), marca la casilla **Disable cache** (Desactivar caché) mientras el panel esté abierto para asegurar que siempre se recargue la última compilación.

---

## 4. Problemas de Exportación a PDF (Cortes de Lámina)

### ❓ Al imprimir a PDF (Ctrl + P) o exportar, las láminas se cortan a la mitad o salen en páginas adicionales vacías.
**Causa:**
El motor utiliza estilos CSS media queries `@media print` específicos en sus plantillas base para ajustar la página web al formato físico/digital de impresión. Si el navegador no está configurado correctamente, agregará márgenes de impresión estándar, rompiendo la proporción 16:9 y dividiendo una sola lámina en dos páginas PDF.

**Solución:**
1. **Configurar Márgenes a "Ninguno" (None):** En el diálogo de impresión de tu navegador (Chrome, Edge o Firefox), busca la sección de configuración de márgenes y cámbiala obligatoriamente de *Predeterminado* a **Ninguno** (o *None*).
2. **Activar Gráficos de Fondo (Background Graphics):** Marca obligatoriamente la casilla **Gráficos de fondo** (o *Background graphics*) en las opciones adicionales del diálogo de impresión. De lo contrario, los colores de fondo del tema, los degradados CSS y las imágenes insertadas no aparecerán en el PDF.
3. **Desactivar Encabezados y Pies de Página:** Desmarca la opción *Encabezados y pies de página* (o *Headers and footers*) para evitar que el navegador imprima la fecha, el título o la URL de visualización en los bordes del PDF.
