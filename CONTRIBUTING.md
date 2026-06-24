# Guía de Contribución a PresentMD (`CONTRIBUTING.md`)

¡Gracias por tu interés en contribuir a **PresentMD**! Este es un proyecto de código abierto diseñado para crear presentaciones profesionales y dinámicas a partir de texto plano en Markdown. Como maintainers y desarrolladores, valoramos tu tiempo y tus aportes para seguir robusteciendo este ecosistema.

Este documento establece las directrices oficiales de desarrollo, pruebas y flujos de trabajo en Git para asegurar que las contribuciones mantengan un nivel de excelencia técnica y consistencia arquitectónica.

---

## 1. Configuración del Entorno de Desarrollo Local

PresentMD utiliza `hatchling` como build-backend en cumplimiento con el estándar de empaquetado de Python modernos definido en el `pyproject.toml`. Las dependencias principales incluyen `rich` para la interfaz de terminal interactiva, mientras que herramientas de desarrollo clave como `pytest` y `watchdog` están configuradas en grupos de dependencias opcionales.

Sigue estos pasos para preparar tu entorno:

### Requisitos Previos
* Python **>= 3.12** instalado en tu sistema.
* Git para el control de versiones.

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/jjbm77/PresentMD.git
cd PresentMD
```

### Paso 2: Crear el Entorno Virtual
Se recomienda utilizar un entorno virtual aislado para evitar colisiones con librerías globales del sistema:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalación en Modo Editable (Editable Mode)
Instala el paquete en modo editable junto con todos los extras de desarrollo (`dev`) y del servidor de recarga en vivo (`serve`):
```bash
pip install --upgrade pip
pip install -e ".[dev,serve]"
```
* **Explicación del Comando:** `-e` instala el paquete en modo desarrollo (los cambios en el código fuente se reflejan inmediatamente en el comando ejecutable `presentmd` sin necesidad de reinstalar), mientras que `[dev,serve]` jala `pytest` para la suite de pruebas y `watchdog` para la detección de cambios del sistema de archivos en tiempo real.

---

## 2. Guía de Ejecución de Pruebas

Para garantizar que ningún cambio de código introduzca regresiones, PresentMD cuenta con una suite de pruebas unitarias y de integración administrada mediante `pytest`.

### Ejecutar todas las pruebas de forma local
Antes de proponer cualquier cambio, debes ejecutar y pasar con éxito toda la suite de pruebas (excluyendo pruebas e2e y de exportación si no tienes configurado Chromium/Playwright localmente):
```bash
PYTHONPATH=src .venv/bin/pytest --ignore=tests/test_e2e.py --ignore=tests/test_export.py
```

### Probar un componente de forma aislada
Si estás desarrollando o corrigiendo un componente específico, no necesitas correr todas las pruebas. Puedes aislar la ejecución apuntando directamente a un archivo de test y utilizando el filtro `-k` de pytest:

```bash
# Probar únicamente el parsing de un componente de bloque específico
PYTHONPATH=src .venv/bin/pytest tests/test_parser.py -k "test_container_progress_bars"

# Probar únicamente el renderizado de un componente visual
PYTHONPATH=src .venv/bin/pytest tests/test_render.py -k "test_timeline_rendering"
```

---

## 3. Políticas de Estilo y Calidad del Código

Para mantener la legibilidad y la facilidad de mantenimiento en todo el motor de Python, todos los contribuidores deben adherirse a los siguientes estándares:

1. **PEP 8:** El código Python debe respetar el estándar oficial PEP 8 de estilo de programación.
2. **Preservación de Firma:** No modifiques las firmas de los métodos del core de parsing en `src/presentmd/parser/` ni del registro de componentes en `src/presentmd/plugins/registry.py` sin una justificación de arquitectura previamente aprobada.
3. **Escapado Obligatorio:** Todo el contenido de texto que sea inyectado en el DOM final de la presentación y que proceda de parámetros ingresados por el autor debe ser sanitizado con `html.escape()` o a través de las plantillas auto-escapadas de Jinja2 para prevenir inyecciones XSS.

---

## 4. Políticas de Ramificación (Git Flow)

Adoptamos una variación del flujo de trabajo de **Git Flow** para gestionar las contribuciones de forma ordenadas:

* **`main`**: Es la rama estable de producción. El código aquí representa las versiones lanzadas oficialmente. Ningún desarrollador realiza commits directamente sobre `main`.
* **`develop`**: Es la rama de integración para desarrollo activo. Todas las características terminadas se integran primero aquí.
* **Ramas de Feature (`feature/nombre-de-la-caracteristica`)**: Creadas a partir de `develop` para el trabajo en una característica o componente nuevo.
* **Ramas de Hotfix (`hotfix/nombre-del-bug`)**: Creadas a partir de `main` para resolver bugs críticos de producción que requieren parches urgentes, integrándose posteriormente tanto a `main` como a `develop`.

### Ciclo de Trabajo Sugerido:
1. Crea tu rama desde `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/mi-nuevo-componente
   ```
2. Realiza los cambios locales escribiendo el código correspondiente, añadiendo el CSS al tema correspondiente y documentando el nuevo componente en `docs/OBJECTS_SPEC.md` si aplica.
3. Escribe y ejecuta los tests unitarios correspondientes.
4. Realiza commits limpios y descriptivos:
   ```bash
   git commit -m "feat(plugins): añadir soporte para el componente pmd-table"
   ```

---

## 5. Requisitos para enviar un Pull Request (PR) Exitoso

Al enviar un Pull Request en GitHub hacia la rama `develop`, asegúrate de cumplir con la siguiente lista de verificación:

1. **Suite de Pruebas Verde:** Todas las pruebas locales unitarias y de integración de la suite deben pasar sin fallos.
2. **Documentación Actualizada:** Si tu PR añade un componente o modifica un comportamiento existente, debes actualizar el manual oficial de sintaxis (`docs/AUTHORING_GUIDE.md`) o la especificación técnica (`docs/OBJECTS_SPEC.md`).
3. **Título y Descripción Claros:** Describe detalladamente qué problema resuelve tu PR, cuál es el enfoque técnico elegido y muestra capturas de pantalla/ejemplos en Markdown del componente funcionando si aplica.
4. **Sin Código Muerto:** Elimina `print` de depuración, comentarios obsoletos o código no utilizado antes de abrir el PR.
