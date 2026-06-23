# PresentMD — Guía de Autoría y Funcionalidades
**Versión 1.0**

Esta guía explica en extremo detalle todas las funcionalidades de PresentMD, qué hacen, y cómo utilizarlas en tus presentaciones Markdown.

---

## 1. Estructura y Configuración

### 1.1 Frontmatter YAML
El bloque YAML al inicio del archivo configura globalmente la presentación. Se define entre tres guiones `---`.

**¿Qué hace?**
Configura metadatos, temas visuales, logotipo, y comportamiento de navegación global de la presentación.

**Uso:**
```yaml
---
title: "Título de la Presentación"
theme: nexus-blueprint    # 5 temas disponibles
accent: "#C8006B"         # Override del color primario
footer: "Texto pie"
logo: logo.png
logo_position: bottom     # top | bottom
nav_arrows: true
slide_number: true
animations: true
closing_message: "¡Gracias!"
closing_subtitle: "¿Preguntas?"
---
```

### 1.2 Separación de Slides
**¿Qué hace?**
Divide el contenido continuo en diapositivas individuales.

**Uso:**
Utiliza tres guiones `---` en una línea vacía.
```markdown
Contenido del primer slide.

---

Contenido del segundo slide.
```

### 1.3 Layouts Custom (`::layout`)
**¿Qué hace?**
Fuerza un diseño estructural específico para la diapositiva actual.

**Layouts disponibles:**
- `::layout{title}`: Fondo completo (oscuro/temático) para títulos principales.
- `::layout{standard}`: Estándar (título superior, cuerpo abajo).
- `::layout{scrollable}`: Para contenido largo que requiere scroll vertical.
- `::layout{split-comparison}`: Divide el slide en dos mitades horizontales (ideal para comparar `|||`).
- `::layout{annex}`: Marca la lámina como un anexo, excluyéndola del flujo principal secuencial.

**Uso:**
```markdown
::layout{split-comparison}
# Título
Lado Izquierdo
|||
Lado Derecho
```

### 1.4 Hero Backgrounds (`::bg-image`)
**¿Qué hace?**
Asigna una imagen inmersiva de fondo a la diapositiva actual, con control de opacidad.

**Uso:**
```markdown
::bg-image{src="assets/fondo.png" opacity="0.4"}
# Diapositiva con fondo
```

### 1.5 Notas de Presentador
**¿Qué hace?**
Oculta notas de la vista pública pero las expone al presentador a través del atributo `data-notes`.

**Uso:**
```markdown
:::notes
Estas notas solo las ve el presentador al inspeccionar.
:::
```

---

## 2. Componentes Especiales (Directivas de Bloque)

### 2.1 KPI Grid (`:::kpi-grid`)
**¿Qué hace?**
Muestra métricas o indicadores clave (KPIs) en forma de cuadrícula de tarjetas de impacto.

**Uso:**
```markdown
:::kpi-grid
- [55M] Usuarios Activos {status: green}
- [12ms] Latencia Media
- [5%] Margen de Error {status: amber}
- [Caída] Servidor B {status: critical}
:::
```

### 2.2 Alert Boxes (`:::alert`)
**¿Qué hace?**
Despliega cajas de alerta para enfatizar advertencias, notas o información importante.

**Uso:**
Acepta colores (`red`, `amber`, `green`, `blue`), iconos custom, y un layout `horizontal` opcional.
```markdown
:::alert{type="red" icon="⚠️" layout="vertical"}
**Cuidado:** Operación destructiva.
:::

:::alert{type="blue" icon="ℹ️" layout="horizontal"}
- Primer punto horizontal
- Segundo punto horizontal
:::
```

### 2.3 Progress Bars (`:::progress-bars`)
**¿Qué hace?**
Muestra barras de progreso horizontales animadas.

**Uso:**
```markdown
:::progress-bars
- Fase de Diseño: 100% {color: secondary}
- Fase de Desarrollo: 65% {color: primary}
:::
```

### 2.4 Info Grid (`:::info-grid`)
**¿Qué hace?**
Muestra pares de Clave-Valor de forma elegante.

**Uso:**
```markdown
:::info-grid
- Base de Datos: PostgreSQL 15
- Servidor: Ubuntu 22.04 LTS
:::
```

### 2.5 Timeline (`:::timeline`)
**¿Qué hace?**
Dibuja una línea de tiempo para mostrar fases sucesivas de un proyecto.

**Uso:**
```markdown
:::timeline
- **Q1**: Análisis
  - Toma de requerimientos
  > Documento aprobado
- **Q2**: Desarrollo
  - Codificación
  > Beta lista
:::
```

### 2.6 Parallel Compare (`:::parallel-compare`)
**¿Qué hace?**
Muestra dos columnas frente a frente con un divisor central, útil para "Antes vs Después".

**Uso:**
```markdown
:::parallel-compare{center-badge="VS"}
### Legacy
- Monolito
---
### Moderno
- Microservicios
:::
```

### 2.7 Cards (`:::cards`)
**¿Qué hace?**
Genera una grilla de tarjetas semánticas avanzadas con íconos y contenido complejo.

**Uso:**
```markdown
:::cards{cols="2"}
::card{title="Frontend" icon="🖥️" color="primary"}
- React
- Vite
::
::card{title="Backend" icon="⚙️" color="secondary"}
- FastAPI
- Python
::
:::
```

### 2.8 Feature Grid (`:::feature-grid`)
**¿Qué hace?**
Crea una cuadrícula de características destacadas.

**Uso:**
```markdown
:::feature-grid{cols="3"}
- [⚡] Alta Velocidad {color: primary}
- [🔒] Seguridad Extrema {color: secondary}
- [☁️] Cloud Native
:::
```

---

## 3. Interactividad y Stepping

### 3.1 Listas Secuenciales (`:::steps`)
**¿Qué hace?**
Aparece los elementos de la lista uno a uno con cada pulsación de tecla/clic.

**Uso:**
```markdown
:::steps
- Paso 1
- Paso 2
- Paso 3
:::
```

### 3.2 Layer Stack (`:::layer-stack`)
**¿Qué hace?**
Apila imágenes y las revela de forma secuencial.

**Uso:**
```markdown
:::layer-stack
![Base](assets/base.png)
![Capa 1](assets/capa1.png)
:::
```

### 3.3 Code Stepping Mágico
**¿Qué hace?**
Resalta secuencialmente líneas específicas en bloques de código.

**Uso:**
```markdown
```python {1|2-3|all}
def inicio():
    x = 1
    y = 2
    return x + y
```
(Debe usarse con 3 backticks, aquí escapado por el formato)

### 3.4 Hotspots (`:::hotspots`)
**¿Qué hace?**
Coloca pines interactivos sobre una imagen que revelan tooltips al tocarlos.

**Uso:**
```markdown
:::hotspots{image="assets/mapa.png"}
- [20%, 30%] **Motor**: Punto vital 1.
- [80%, 50%] **Filtro**: Punto vital 2.
:::
```

### 3.5 Spotlight (`:::spotlight`)
**¿Qué hace?**
Atenúa la diapositiva y resalta selectores CSS específicos de manera interactiva.

**Uso:**
```markdown
:::spotlight
- [#mi-id] Explicación de mi-id.
- [.mi-clase] Explicación de mi-clase.
:::
```

---

## 4. Contenido Técnico y Markdown Estándar

### 4.1 Bloques de Código Estáticos
**¿Qué hace?**
Muestra código con resaltado de sintaxis y líneas resaltadas fijas.

**Uso:**
```markdown
```json {2,4}
{
  "clave": "valor",
  "otro": "dato"
}
```

### 4.2 Diagramas (Mermaid)
**¿Qué hace?**
Renderiza diagramas de flujo y secuencias a SVG vectorial.

**Uso:**
```markdown
```mermaid
graph TD;
    A-->B;
```
```

### 4.3 Tablas Markdown
**¿Qué hace?**
Dibuja tablas clásicas.

**Uso:**
```markdown
| Col 1 | Col 2 |
|-------|-------|
| Val 1 | Val 2 |
```

### 4.4 Blockquotes
**¿Qué hace?**
Destaca citas importantes.

**Uso:**
```markdown
> "Este es un mensaje clave."
```

---

## 5. Elementos Inline

### 5.1 Badges
**¿Qué hace?**
Inserta etiquetas pequeñas de estado en medio del texto.

**Uso:**
```markdown
El servidor está [ONLINE]{.badge-green}.
```

### 5.2 Resaltado Natural (Mark)
**¿Qué hace?**
Marca con estilo "destacador" el texto.

**Uso:**
```markdown
Esto es ==muy importante==.
```

### 5.3 Navegación Dinámica a Anexos
**¿Qué hace?**
Permite navegar no linealmente. Puedes asignar un ID a un slide anexo y enlazarlo.

**Uso:**
Slide de Origen:
```markdown
Ver [Anexo A](#anexo-a){.link-anexo}
```

Slide de Destino (al final del documento):
```markdown
::layout{annex}
## Anexo A {#anexo-a}

<button class="btn-volver">Volver</button>
```

---

## 6. Funcionalidades del Reproductor (UI)

- **Menú Lateral Desplegable**: Acerca el cursor al borde izquierdo de la pantalla. Agrupa anexos automáticamente.
- **Transiciones Cinemáticas**: View Transitions API interpola las vistas.
- **Auto-Escalado (Fit-to-Screen)**: Ajusta la fuente para evitar desbordamientos.
- **Herramientas de Presentador Vivo**: Presiona `L` para láser, `D` para dibujar, `C` para limpiar.
- **Pantalla Completa**: Presiona `F` o haz clic en el icono inferior derecho.

### 6.1 Modo Presentador de Doble Ventana Offline
Presionando la tecla `p` o `P` (o pulsando el icono del profesor 👨‍🏫 en la barra de controles), se abre una ventana secundaria optimizada como consola de presentador:
- **Slide Actual + Notas**: Renderiza una versión a escala del slide actual con las notas del presentador legibles en la parte inferior.
- **Siguiente Slide + Reloj/Cronómetro**: Permite ver qué diapositiva viene después, la hora actual del sistema y cronometrar el tiempo transcurrido (con botón de reinicio).
- **Sincronización Total Offline**: Funciona sin conectividad mediante `localStorage` y `postMessage`. Al avanzar diapositivas o interactuar en cualquiera de las dos ventanas, la otra se actualiza instantáneamente.

---

## 7. Exportación y CLI

El CLI de PresentMD provee los siguientes comandos:

- `presentmd build archivo.md`: Construye un HTML autocontenido (con base64 o copia de assets en `/output`).
- `presentmd build archivo.md -f pdf`: Exporta directamente a PDF (requiere Chromium/Playwright).
- `presentmd serve archivo.md`: Servidor local con Live-Reload.
- `presentmd debug archivo.md`: Muestra el AST (Árbol de Sintaxis Abstracta) parseado en consola.
- `presentmd doctor`: Realiza un diagnóstico completo de dependencias locales (Python, D2, Mermaid CLI, Playwright y Chromium) para confirmar que el entorno esté correctamente configurado.
