# Directrices de Seguridad (`SECURITY.md`)

Este documento detalla las políticas y directrices oficiales de seguridad para el proyecto **PresentMD**. Como motor de compilación y presentación estática local, garantizar la integridad de los entornos de ejecución de nuestros usuarios y colaboradores es de máxima prioridad.

---

## 1. Versiones Soportadas

Actualmente, solo la rama principal de desarrollo activo recibe actualizaciones y parches de seguridad. Recomendamos mantener la instalación actualizada a la última versión menor publicada.

| Versión | Soportada | Parches de Seguridad |
| :--- | :---: | :--- |
| **>= 0.1.0** | Sí | Activos (Última versión menor/parche) |
| **< 0.1.0** | No | No soportada. Migre a la versión más reciente. |

---

## 2. Reporte de Vulnerabilidades

Si descubres un problema de seguridad en el motor o las plantillas de PresentMD, por favor **no abras un Issue público** en la plataforma de control de versiones. Esto expone a todos los usuarios activos antes de que contemos con una solución disponible.

### Proceso de Reporte Privado:
1. Envía un correo electrónico detallado a **`security@presentmd.org`** (dirección de seguridad del proyecto).
2. Incluye una descripción clara del fallo de seguridad, la versión exacta del software en la que se reproduce y un ejemplo de código Markdown o procedimiento paso a paso (PoC) para replicar la vulnerabilidad.
3. El equipo de mantenedores responderá en un plazo máximo de **48 horas** confirmando la recepción y validación del reporte.
4. Mantendremos la comunicación privada hasta que se desarrolle, pruebe y publique un parche corrector, momento en el cual se le dará el crédito correspondiente por el hallazgo de manera pública (si así lo desea).

---

## 3. Arquitectura de Seguridad y Mitigación de Riesgos

PresentMD implementa medidas técnicas de seguridad estrictas en el core del compilador para evitar la ejecución de código malicioso o accesos no autorizados a través de presentaciones de terceros:

### A. Prevención de Path Traversal (Ataques de Directorio)
Al compilar activos locales para su auto-contención en Base64 (tales como logotipos o imágenes de fondo de láminas), el motor valida rigurosamente las rutas relativas. 

El método `_get_logo_data_uri` ubicado en `src/presentmd/render/engine.py` utiliza la instrucción `.resolve()` y verifica de forma estricta si el archivo resultante se encuentra dentro del espacio de trabajo permitido:

```python
logo_path = (presentation_dir / logo_path_str).resolve()
if not logo_path.is_relative_to(presentation_dir.resolve()):
    # Se deniega la operación de lectura e inyección del recurso
```

Esto impide que un archivo Markdown malicioso ajeno intente forzar al compilador a leer y codificar en Base64 recursos críticos del sistema de archivos local del usuario (por ejemplo, llaves SSH privadas, archivos `.env` de configuración o archivos sensibles del sistema como `/etc/passwd`).

### B. Desactivación de Subprocesos Externos (Command Injection)
Para prevenir ataques de inyección de comandos a través del CLI del sistema operativo, **PresentMD tiene desactivada de manera estricta toda invocación de subprocesos externos**. 

Anteriormente, algunas herramientas llamaban de manera asíncrona a dependencias del sistema como el binario de D2 (`d2`) o el CLI de Mermaid de Node (`mmdc`) mediante módulos como `subprocess` de Python. En la arquitectura actual:
* **No se ejecutan comandos externos** en terminal durante la compilación.
* Los diagramas Mermaid se delegan al runtime de JavaScript nativo en el cliente final de forma segura.
* Esto elimina la superficie de ataque que permitiría a un documento malicioso ejecutar comandos no deseados en la terminal del desarrollador.

### C. Sanitización Contra XSS (Cross-Site Scripting)
Todos los datos e información parseados de los campos YAML frontmatter y los metadatos de los elementos son sanitizados mediante el motor autoescape de Jinja2 y llamadas a `html.escape()` antes de renderizar la página web final.
