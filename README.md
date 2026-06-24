# PresentMD 📊

### Convierte texto plano en diapositivas web interactivas y PDFs pixel-perfect mediante un motor declarativo y zero-framework.

---

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)]()
[![Development Status](https://img.shields.io/badge/status-active-orange.svg)]()

**PresentMD** es un compilador y motor de presentaciones técnico de alto rendimiento. Permite a desarrolladores, ingenieros y arquitectos de software escribir presentaciones completas usando Markdown estructurado y metadatos YAML, compilándolas en una aplicación web interactiva modular autocontenida que funciona al 100% offline.

---

## 💡 La Problemática (The Problem)

Las presentaciones técnicas (arquitectura de software, análisis de sistemas, roadmaps de desarrollo) sufren bajo los flujos de trabajo tradicionales:
* **Pérdida de Foco:** Las herramientas visuales de arrastrar y soltar (PowerPoint, Keynote) distraen a los ingenieros en micro-ajustes de diseño y maquetación en lugar de centrar la atención en el contenido.
* **Control de Versiones Incompatible:** Los archivos binarios pesados generan conflictos de combinación (`merge conflicts`) imposibles de rastrear o resolver en sistemas Git.
* **Sobrecarga de Herramientas de Compilación:** Muchos frameworks Markdown web requieren dependencias complejas y pesadas en el servidor, o ejecuciones lentas de Node.js en tiempo de diseño para renderizar diagramas o resaltar código.
* **Vulnerabilidades y Dependencias Externas:** El uso de motores de renderizado externos en el servidor web (como compiladores locales D2 o pipelines Playwright pesados) aumenta la superficie de ataque y el peso del entorno de desarrollo.

---

## 🛠️ La Solución (The Solution)

**PresentMD** aborda esto separando la semántica del diseño a través de un motor ligero y optimizado:
1. **Markdown-First y Declarativo:** Escribe el contenido técnico estructurado; el motor infiere el layout adecuado y distribuye los componentes automáticamente.
2. **Cliente Zero-Framework:** El renderizador genera un único archivo HTML con estilos y scripts incrustados. No requiere React, Vue ni librerías pesadas en tiempo de ejecución, logrando cargas instantáneas a 60 FPS.
3. **Mermaid Nativo en el Navegador:** Elimina la necesidad de instalar herramientas locales como `mmdc`. El renderizado de diagramas Mermaid se ejecuta directamente en el cliente.
4. **Impresión Nativa 16:9:** En lugar de ejecutar navegadores automatizados pesados en segundo plano, la exportación a PDF se delega al motor de impresión nativo del navegador del usuario final, optimizado visualmente mediante hojas de estilo print 16:9 en CSS.
5. **Seguridad Integrada:** Se desactiva el renderizado de motores con vulnerabilidades conocidas (como la ejecución local de D2 CLI) para garantizar la integridad del sistema.

---

## ✨ Características Principales (Features)

* ⌨️ **CLI Profesional:** Comandos simples para el flujo de vida del documento (`build`, `serve`, `debug`, `doctor`).
* 👨‍🏫 **Consola de Presentador Sincronizada:** Doble pantalla (vista de presentador y audiencia) que corre localmente sin internet, utilizando `localStorage` y `postMessage` para comunicación bidireccional instantánea.
* ⚡ **Code Stepping Interactivo:** Resalta líneas o rangos de código de forma animada paso a paso (`{1|2-3|all}`) al avanzar con el teclado.
* 🎨 **25+ Componentes Técnicos Integrados:** Contenedores ricos listos para usar (`:::kpi-grid`, `:::timeline`, `:::alert`, `:::cards`, `:::pyramid`, `:::typewriter`, `:::progress-ring`, `:::tabs`, `:::grid`, entre otros).
* 🔄 **Hot-Reload en Vivo:** Servidor de desarrollo integrado (`serve`) con detección de cambios y recarga automática en caliente manteniendo el estado del slide actual.
* 🔍 **Analizador de AST Visual:** Herramienta de depuración interactiva (`debug`) para volcar y depurar el árbol de sintaxis abstracta (AST) de la presentación.
* 🛠️ **Diagnóstico Automático:** Utilidad de diagnóstico (`doctor`) para validar el estado del intérprete, librerías y dependencias externas.

---

## 🚀 Instalación Rápida (Quick Start)

PresentMD requiere **Python 3.12 o superior**.

### 1. Clonar e Instalar
Instala el proyecto y sus herramientas de desarrollo directamente utilizando el gestor de dependencias estándar de Python:

```bash
# Instalar el paquete con soporte para el servidor Live Preview (serve)
pip install ".[serve]"
```

### 2. Verificar Entorno
Ejecuta la herramienta de diagnóstico integrada para validar el estado del sistema:

```bash
presentmd doctor
```

---

## 💻 Uso Básico (Basic Usage)

Crea un archivo llamado `presentacion.md` con la estructura base de PresentMD:

```markdown
---
title: "Guía de PresentMD"
theme: obsidian-glass
animations: true
footer: "PresentMD v0.1"
---

::layout{title}
# PresentMD
## Diapositivas técnicas escritas en Markdown

---

::layout{standard}
## Monitoreo del Entorno

:::kpi-grid
- [25ms] Latencia Media {status: "1"}
- [99.98%] SLA de Red {status: "4"}
- [0] Errores Críticos
:::

:::notes
Estas notas solo son visibles en la consola de presentador independiente (tecla P).
:::
```

### Comandos de Compilación y Servicio

* **Vista Previa en Vivo (Hot-Reload):**
  Lanza un servidor local en el puerto `8000` que detecta modificaciones en el archivo de texto y recarga la diapositiva en caliente:
  ```bash
  presentmd serve presentacion.md
  ```
* **Compilar a HTML Estático:**
  Genera el archivo web interactivo autocontenido en la carpeta `output/`:
  ```bash
  presentmd build presentacion.md
  ```
* **Exportar a PDF:**
  PresentMD prepara la maquetación web para una exportación pixel-perfect en 16:9. Compila a HTML e imprime la presentación directamente desde tu navegador:
  ```bash
  # 1. Genera el HTML preparado
  presentmd build presentacion.md --format pdf
  # 2. Abre el HTML resultante en Chrome/Firefox y presiona Ctrl + P / Cmd + P
  ```
* **Depurar el AST en Consola:**
  ```bash
  presentmd debug presentacion.md
  ```

---

## 📚 Ecosistema y Documentación Detallada

La documentación de PresentMD está segmentada para cubrir las necesidades de diseño, autoría y extensibilidad del framework:

### 📖 Manuales de Escritura y Diseño
* [Guía de Autor y Sintaxis (`docs/AUTHORING_GUIDE.md`)](docs/AUTHORING_GUIDE.md): Manual de escritura de diapositivas, transiciones y flujo secuencial.
* [Catálogo Completo de Componentes (`docs/OBJECTS_SPEC.md`)](docs/OBJECTS_SPEC.md): Especificación técnica de los contenedores y elementos visuales (KPIs, timelines, etc.).

### ⚙️ Desarrollo y Extensibilidad (Core)
* [Arquitectura del Sistema (`docs/ARCHITECTURE.md`)](docs/ARCHITECTURE.md): Detalle del flujo de datos, tokenización AST en Python y runtime en JavaScript Vanilla.
* [Diseño y Personalización de Temas (`docs/THEMES_SPEC.md`)](docs/THEMES_SPEC.md): Estructuración de archivos CSS y tokens de diseño para crear identidades de marca.
* [Guía de Desarrollo de Plugins (`docs/plugins.md`)](docs/plugins.md):  Manual de extensibilidad para registrar nuevas clases en `ComponentRegistry` y extender el parser.

### 🛠️ Mantenimiento y Comunidad
* [Guía de Contribución (`CONTRIBUTING.md`)](CONTRIBUTING.md): Flujo de desarrollo, configuración del entorno local y ejecución de pruebas con `pytest`.
* [Resolución de Problemas y FAQ (`docs/TROUBLESHOOTING.md`)](docs/TROUBLESHOOTING.md): Guía de primeros auxilios para fuentes, caché de imágenes, recarga en vivo y exportación a PDF.
* [Directrices de Seguridad (`SECURITY.md`)](SECURITY.md): Políticas de reporte de vulnerabilidades, sanitización XSS y prevención de Path Traversal.
* [Registro de Cambios (`CHANGELOG.md`)](CHANGELOG.md): Registro histórico de versiones, cambios en el motor y correcciones.

---

## 🤝 Contribución (Contributing)

¡Toda contribución es bienvenida! Para colaborar en el desarrollo de PresentMD, por favor lee nuestra [Guía de Contribución](CONTRIBUTING.md) *[Propuesto]* y asegúrate de verificar tus cambios ejecutando las pruebas unitarias:

```bash
# Instalar dependencias de testing
pip install ".[dev]"
# Ejecutar tests
pytest
```

---

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para obtener más detalles.
