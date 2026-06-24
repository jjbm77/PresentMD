# Guía de Autor y Sintaxis (docs/AUTHORING_GUIDE.md)

¡Bienvenido al manual oficial de escritura de PresentMD! Esta guía está diseñada para que puedas dominar la creación de diapositivas interactivas y profesionales en cuestión de minutos, directamente en texto plano Markdown.

---

## 1. 🚀 ¡Bienvenido a PresentMD! (Tu Nueva Superpotencia)

Si alguna vez has perdido horas alineando cuadros de texto en PowerPoint, lidiando con fuentes rotas en Keynote o resolviendo conflictos de fusión imposibles en Git por culpa de archivos binarios, **PresentMD es tu solución**.

PresentMD te permite diseñar presentaciones como si escribieras código:
* **Foco en el Contenido:** Escribe en Markdown simple y deja que el motor de temas y renderizado se encargue del diseño pixel-perfect.
* **Control de Versiones Limpio:** Tus diapositivas son archivos `.md` de texto plano. Dile adiós a los conflictos de Git.
* **Diseñado para Desarrolladores:** Incluye soporte nativo para ejecución de pasos en bloques de código (Code Stepping), diagramas embebidos, componentes modulares dinámicos y notas del orador integradas.

---

## 2. 🏁 Tu Primera Presentación en 60 Segundos

Crear tu primera presentación es tan simple como definir un encabezado de configuración (Frontmatter) y separar tus láminas con tres guiones (`---`).

Crea un archivo llamado `presentacion.md` y pega el siguiente código:

```markdown
---
title: "Construyendo el Futuro del Software"
theme: "nexus-blueprint"
accent: "#C8006B"
footer: "PresentMD Inc. · 2026"
---

# Transformación Digital
## Rediseñando arquitecturas heredadas

Bienvenidos a la nueva era de las herramientas de presentación técnicas.

---

::layout{standard}

# ¿Por qué PresentMD?
## El poder de escribir tus ideas en texto plano

* **Portabilidad:** Corre offline y genera bundles HTML auto-contenidos.
* **SmartArt Nativo:** Inserta diagramas complejos, KPIs y alertas directamente desde Markdown.
* **Lienzo 16:9 Rígido:** Diseñado específicamente para pantallas modernas.

---

::layout{split-comparison}

# Comparativa de Flujos
## Modernización de infraestructura y desarrollo

### El Pasado
* Diseño manual en diapositivas binarias
* Cero integración con ramas de Git
* Inconsistencia visual de marca

|||

### El Futuro (PresentMD)
* Automatización mediante CSS Vanilla
* Pull Requests legibles en texto plano
* Consistencia garantizada por tokens de diseño
```

### El Comando "Mágico" para Vista en Vivo:
Para ver tus cambios reflejados en tiempo real mientras editas tu archivo Markdown, abre tu terminal y ejecuta el servidor de previsualización en vivo (Live Preview):

```bash
presentmd serve presentacion.md
```

Esto abrirá automáticamente tu navegador en `http://localhost:8000`. Cada vez que guardes tu archivo `.md`, la presentación se actualizará de forma instantánea sin perder la diapositiva en la que estás.

---

## 3. 🏗️ Estructurando Diapositivas y Layouts

### El Lienzo Lógico 16:9 y el Auto-Escalado
PresentMD trabaja sobre una resolución virtual rígida de **1280px x 720px**. Para evitar desbordamientos visuales, el motor ejecuta dos técnicas automáticas:
1. **Escalado de Relación de Aspecto:** Escala todo el lienzo dinámicamente usando `transform: scale` para ajustarse perfectamente al tamaño del navegador (evitando barras de desplazamiento globales).
2. **Auto-Ajuste de Tipografía (Fit-to-Screen):** Si el contenido vertical de una diapositiva es demasiado extenso, disminuye automáticamente el tamaño de la tipografía base para forzar que todo encaje en pantalla.
   
> [!IMPORTANT]
> Para no romper el auto-escalado de fuentes, define márgenes, paddings y tamaños de tipografías personalizadas en tu CSS utilizando unidades relativas (`rem` o porcentajes), nunca píxeles fijos (`px`).

---

### Los Diseños Estructurales (Layouts)
Puedes forzar el comportamiento de la rejilla de una diapositiva usando la directiva `::layout{nombre}` al inicio de tu lámina:

#### 1. `::layout{title}`
* **Cuándo usar:** Portadas de inicio, finales o separadores de grandes bloques.
* **Estructura:** Centra vertical y horizontalmente todo el contenido sobre un fondo de alto contraste decorado con líneas de énfasis cromáticas.

#### 2. `::layout{standard}`
* **Cuándo usar:** La diapositiva diaria de viñetas, párrafos o diagramas.
* **Estructura:** Organiza el contenido en una rejilla vertical de tres filas fijas (Cabecera, Cuerpo de Contenido y Pie de Diapositiva).

#### 3. `::layout{scrollable}`
* **Cuándo usar:** Tablas muy grandes, listados de auditoría extensos o diapositivas destinadas a anexos técnicos.
* **Estructura:** Activa una barra de desplazamiento interno vertical en el cuerpo de la diapositiva para evitar que la información se corte.

#### 4. `::layout{split-comparison}`
* **Cuándo usar:** Para comparar en paralelo dos conceptos, productos o flujos técnicos.
* **Estructura:** Divide la diapositiva en dos columnas laterales de contenido (`.pc-left` y `.pc-right`) y un divisor central (`.pc-center`).
  * Usa el separador especial `|||` en una línea sola para marcar dónde termina la columna izquierda y comienza la derecha.
  * Inyecta una medalla de contraste central que puedes renombrar agregando la propiedad `center_badge: "VS"` (o el texto que gustes) en el Frontmatter.

---

### Imágenes de Fondo
Puedes añadir una imagen a toda la diapositiva usando la directiva `::bg-image` al inicio de la lámina:

```markdown
::bg-image{src="blueprint_bg.png" opacity="0.15"}
```
*(El motor incrustará la imagen en base64 de forma offline para asegurar la portabilidad total de la presentación).*

---

## 4. ✨ Animaciones y Flujo Secuencial (El Modo Presentador)

### Code Stepping Animado (Depuración de Código en Vivo)
Una de las funcionalidades más potentes para demostraciones de software es el resaltado secuencial de líneas de código. Puedes configurarlo usando llaves `{}` tras declarar el lenguaje de programación de tu bloque de código:

```javascript {1|3-4|all}
const presenter = "PresentMD";
console.log("Iniciando modo presentador...");
const init = () => {
  return presenter.toLowerCase();
};
```

* **`{1|3-4|all}`** le indica al motor lo siguiente:
  * Al ingresar a la diapositiva, se resalta la línea `1` (el resto se atenúa).
  * Al presionar *Avanzar*, se resalta el bloque de las líneas `3` a `4`.
  * En el siguiente paso, se resaltan todas las líneas.

---

### Revelado Secuencial de Elementos (Steps)
Para evitar que tu audiencia lea toda la diapositiva antes de que expliques cada punto, puedes agrupar elementos bajo el contenedor `:::steps`:

```markdown
:::steps
* **Paso 1:** Definir la estructura base en Markdown.
* **Paso 2:** Lanzar el servidor en vivo de PresentMD.
* **Paso 3:** Exportar a PDF en alta resolución.
:::
```

Cada viñeta o bloque interno se revelará secuencialmente cada vez que presiones la tecla *Avanzar*. 
*(También puedes forzar este comportamiento en SmartArt utilizando el atributo `{steps="true"}` tras definir el nombre del componente).*

---

### Notas del Orador y Consola Dual
Puedes guardar notas privadas para guiar tu discurso utilizando el contenedor `:::notes` al final de cualquier diapositiva:

```markdown
# Arquitectura Cloud
...
:::notes
Recordar hacer énfasis en el ahorro de costos del 35% de la infraestructura Serverless. No ahondar demasiado en los diagramas de VPC.
:::
```

* **Consola de Presentador:** Presiona la tecla **`P`** en tu navegador. Se abrirá una ventana secundaria sincronizada que muestra una vista previa de la diapositiva actual, la siguiente lámina, un temporizador del tiempo transcurrido y tus notas del orador en tamaño legible.

---

## 5. 🎨 Dale Vida a tus Datos (Uso de Componentes y Colores)

### KPI Grid (Indicadores Clave de Rendimiento)
Inserta números impactantes y métricas de rendimiento en una cuadrícula con estados de color:

```markdown
:::kpi-grid
- [120ms] Latencia Promedio {status: green}
- [99.99%] Disponibilidad SLA {status: warning}
- [0.02%] Tasa de Error {status: critical}
:::
```
*(Los estados `green`, `warning` y `critical` asignan colores semánticos de forma automática).*

---

### Cajas de Alertas e Información (Alerts)
Comunica advertencias, consejos o datos críticos:

```markdown
:::alert{type="warning" icon="⚠️"}
Cuidado con los Desbordamientos de Memoria
Asegúrate de limpiar los listeners del `MutationObserver` en el desmontado del componente para evitar fugas de recursos.
:::
```
* **Alertas Horizontales:** Si quieres una lista en línea, usa `layout="horizontal"` y viñetas internas:
```markdown
:::alert{type="success" icon="🚀" layout="horizontal"}
- Lanzamiento Exitoso
- Pipeline Verde
- Despliegue Completado
:::
```

---

### El Sistema de Colores Universales (`data-color`)
Todos los diagramas y cajas de PresentMD utilizan un selector de color abstracto del `1` al `6` que respeta la paleta cromática del tema de diseño seleccionado:

```markdown
:::progress-bars
- Backend API: 85% {color: 1}
- Frontend UI: 92% {color: 2}
- Infraestructura: 100% {color: 3}
:::
```

Esto te permite cambiar por completo el tema de color visual (`theme: obsidian-glass` por `theme: nexus-blueprint`) en el Frontmatter, y la presentación adaptará todos sus componentes gráficos automáticamente para mantener la armonía.

---

## 6. 🗺️ Cheat Sheet (Atajos de Teclado y Comandos Rápidos)

Presiona estos atajos en tu teclado cuando estés visualizando la presentación para activar herramientas de apoyo en el escenario:

| Tecla / Atajo | Acción Realizada |
| :--- | :--- |
| **`Flecha Derecha`** / **`Espacio`** / **`PageDown`** | Siguiente paso de animación / Siguiente diapositiva |
| **`Flecha Izquierda`** / **`PageUp`** | Paso de animación anterior / Diapositiva anterior |
| **`P`** | Abre o cierra la Consola del Presentador (pantalla dual sincronizada) |
| **`T`** / **`Esc`** | Abre o cierra el menú lateral de Tabla de Contenidos (TOC) |
| **`F`** | Alterna el modo Pantalla Completa |
| **`L`** | Activa/Desactiva el cursor de puntero láser virtual |
| **`D`** | Activa/Desactiva el Lienzo de Dibujo Libre para pintar sobre las diapositivas |
| **`C`** | Limpia todos los trazos dibujados en la diapositiva actual |
| **`Home`** | Salta a la primera diapositiva de la presentación |
| **`End`** | Salta a la última diapositiva útil (excluyendo anexos de datos) |
| **`Esc`** | Cierra cualquier vista de ampliación de diagramas activa (Lightbox) |
