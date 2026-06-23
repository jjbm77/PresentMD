# PresentMD 📊

**PresentMD** es un compilador y motor de presentaciones de nivel profesional que transforma documentos Markdown enriquecidos en diapositivas web interactivas (HTML) y archivos PDF de alta resolución. Diseñado específicamente para desarrolladores, arquitectos de software y modeladores de datos.

---

## 🚀 Requisitos Previos

Antes de instalar PresentMD, asegúrate de tener instalado:
* **Python 3.12** o superior.

### Motores de Diagramas Opcionales (Recomendado)
PresentMD detecta automáticamente si estas herramientas están disponibles en tu sistema. Si no lo están, mostrará un contenedor con el código fuente del diagrama y una indicación de instalación:

* **Para Diagramas D2 (Database/Architecture)**:
  * Instalar D2 globalmente.
  * **Linux/macOS**: `curl -fsSL https://d2lang.com/install.sh | sh`
  * **Windows**: `winget install Terrastruct.D2` o `choco install d2`
* **Para Diagramas Mermaid**:
  * Requiere Node.js. Instala Mermaid CLI globalmente con:
  * `npm install -g @mermaid-js/mermaid-cli`

---

## 🛠️ Procedimiento de Instalación

Sigue estos pasos para instalar PresentMD en la máquina del usuario final:

### 1. Clonar o copiar la carpeta del proyecto
Coloca los archivos de la aplicación en una ruta local del sistema (ej. `/opt/presentmd` o una carpeta de usuario).

### 2. Crear y activar un entorno virtual (Recomendado)
Para evitar conflictos con otras librerías globales de Python:

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar en Linux/macOS
source .venv/bin/activate

# Activar en Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

### 3. Instalar PresentMD y sus dependencias
Instala el paquete en modo normal o con el grupo opcional de desarrollo (`serve`):

```bash
# Instalación estándar (compilación HTML/PDF)
pip install .

# Instalación completa con soporte de Hot-Reload / Live-Preview
pip install ".[serve]"
```

### 4. Instalar navegadores para la exportación a PDF
PresentMD utiliza Playwright headless para compilar PDFs perfectos en 16:9. Debes inicializar los binarios de Chromium ejecutando:

```bash
playwright install chromium
```

---

## 💻 Guía de Uso Rápido

Una vez instalado, el comando `presentmd` estará disponible en tu terminal (mientras el entorno virtual esté activo).

### 1. Compilar a HTML
Genera una presentación interactiva autónoma:
```bash
presentmd build presentacion.md
```
El archivo de salida se guardará en `output/presentacion.html`.

### 2. Compilar a PDF
Genera un archivo PDF listo para imprimir o compartir, donde cada diapositiva ocupa exactamente una página 16:9:
```bash
presentmd build presentacion.md --format pdf
```
El archivo de salida se guardará en `output/presentacion.pdf`.

### 3. Servidor de Vista Previa en Vivo (Hot-Reload)
Inicia un servidor local de desarrollo. Cada vez que guardes cambios en tu archivo `.md`, la presentación en el navegador se recargará automáticamente manteniendo la diapositiva actual en pantalla:
```bash
presentmd serve presentacion.md
```
* **Opciones**:
  * Cambiar puerto: `presentmd serve presentacion.md --port 8080`
  * No abrir navegador automáticamente: `presentmd serve presentacion.md --no-open`

### 4. Diagnosticar el Entorno (`doctor`)
Verifica de manera rápida si todos los binarios externos de diagramas (D2, Mermaid), Playwright y Chromium están bien instalados y configurados:
```bash
presentmd doctor
```

---

## 👨‍🏫 Modo Presentador de Doble Ventana Offline

PresentMD incluye una consola de presentador profesional y autocontenida que funciona sin internet.

1. Abre tu presentación compilada en el navegador.
2. Presiona la tecla **`P`** o haz clic en el icono del profesor (👨‍🏫) en los controles.
3. Se abrirá una segunda ventana que muestra:
   - Vista previa de la diapositiva actual.
   - Vista previa de la siguiente diapositiva.
   - Reloj local y cronómetro transcurrido.
   - Notas de presentador en texto claro y legible.
4. **Sincronización Bidireccional:** Al cambiar de lámina en cualquiera de las dos ventanas, la otra se sincronizará automáticamente mediante eventos de almacenamiento local (`localStorage`) y `postMessage`.

