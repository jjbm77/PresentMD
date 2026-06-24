# Registro de Cambios (`CHANGELOG.md`)

Todos los cambios notables realizados en el proyecto **PresentMD** se documentan en este archivo, siguiendo el formato estandarizado de [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y respetando el versionado semántico ([Semantic Versioning](https://semver.org/spec/v2.0.0.html)).

---

## [1.1.0] - 2026-06-24

### Added
* **Componente de Bloque Premium de Tablas (`:::pmd-table`)**: Soporte para estilizar tablas de Markdown estándar con variantes visuales de tema (`striped`, `angled`, `minimal`), filas de totales resaltadas y variables de color dinámicas mapeadas.
* **Componentes de Gráficos Nativos**:
  * Componente `:::bar-chart` para columnas verticales puras con CSS flex.
  * Envoltorio `:::chart` para renderizar lienzos de Chart.js con soporte de accesibilidad mediante tablas ocultas semánticas.
* **Efecto de Escritura (`:::typewriter`)**: Animación de teletipo personalizable con parámetros de velocidad, retraso, tamaño y color.
* **Indicador Circular (`:::progress-ring`)**: Anillo indicador circular animado utilizando SVG interactivos del lado del cliente.
* **Ecosistema de Mantenimiento**: Generación de políticas formales de seguridad (`SECURITY.md`), guías de desarrollo (`CONTRIBUTING.md`) y resolución de problemas (`docs/TROUBLESHOOTING.md`).

### Changed
* **Optimización de Expresión Regular para Progreso**: Se modificó `_PROGRESS_ITEM_RE` en `registry.py` para admitir valores de color sin comillas (por ejemplo, `{color: secondary}`), flexibilizando la sintaxis del autor.
* **Refactorización de Pruebas**: Se actualizaron las pruebas en `tests/test_render.py` para emplear aserciones basadas en la especificación cromática de atributos `data-color` en lugar de clases CSS desactualizadas.

### Fixed
* **Fallo de Variable en Feature Grid**: Corrección de un error de inicialización `NameError` en `src/presentmd/plugins/components/feature_grid.py` que impedía renderizar correctamente el listado de tarjetas de características.

---

## [1.0.0] - 2026-06-12

Esta versión marca la estabilidad del núcleo del motor de presentaciones PresentMD, consolidando la arquitectura basada en AST y eliminando dependencias externas de rendering en el backend.

### Added
* **Esquema de Transición CSS View Transitions**: Soporte nativo para animaciones de transición fluidas en navegadores compatibles.
* **Controlador de Avance Paso a Paso (Steps)**: Mecanismo de animación progresiva que detecta elementos marcados con `data-step` e inyecta la clase `.step-hidden` para revelados secuenciales.
* **Layouts Multicolumna Flexibles (`:::grid` y `::col`)**: Implementación de contenedores dinámicos con anchos fraccionales personalizables.
* **Soporte de Diapositivas de Anexo (`layout: annex`)**: Estructura de anexo que ordena estas diapositivas al final del índice del TOC y proporciona botones de retorno automático al slide de origen.

### Changed
* **Migración del Parsing de Diagramas Mermaid**: El renderizado de diagramas Mermaid se trasladó completamente al cliente web final, utilizando la librería Mermaid nativa en el navegador y evitando la traducción previa del lado del servidor.
* **Exportación PDF Simplificada**: Se reemplazó la compilación forzada basada en headless browsers pesados por una exportación a PDF simplificada y optimizada que aprovecha las media queries de impresión `@media print` nativas del navegador (accesible mediante el diálogo Ctrl+P).

### Removed
* **Invocación de Subprocesos Externos**: Se eliminaron por completo las llamadas a utilidades del sistema (`subprocess.run()`) para traducir diagramas (como ejecutables NodeJS o D2), mejorando radicalmente la seguridad contra inyecciones de comandos en la terminal.

---

## [0.1.0] - 2026-05-30

### Added
* **Lanzamiento Inicial**: Estructura del compilador de Markdown a HTML en Python con soporte para CLI básico (`serve` y `build`).
* **Soporte de Temas Nexus Blueprint y Obsidian Glass**: Estructuración del sistema de tokens visuales y layouts de portada, estándar y scrollable.
