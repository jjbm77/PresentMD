# Catálogo Completo de Componentes (docs/OBJECTS_SPEC.md)

Este documento contiene la especificación técnica definitiva y rigurosa de todos los contenedores y componentes visuales (SmartArt) soportados de forma nativa por el motor de PresentMD. 

El propósito de este catálogo es servir de referencia exacta tanto para autores de presentaciones que necesiten conocer la sintaxis y los atributos admitidos, como para desarrolladores y diseñadores que deseen implementar o personalizar estilos CSS en sus temas.

---

## 1. Introducción y Estándar de la Sintaxis de Bloques

### Sintaxis de Bloques con Triples Dos Puntos
El motor de PresentMD utiliza un compilador basado en `markdown-it-py` con soporte para directivas de contenedores personalizados. Todos los componentes de bloque se invocan usando la sintaxis de triples dos puntos (`:::`):

```markdown
:::nombre-componente{atributo_1="valor" atributo_2="valor"}
Líneas de contenido interno en Markdown
:::
```

### Reglas de Atributos (Metadatos)
1. **Paso de Atributos:** Los atributos de configuración se colocan inmediatamente después del nombre del componente entre llaves `{}`.
2. **Formato:** Deben seguir la estructura clásica `clave="valor"` o `clave=valor`. Las comillas son opcionales para valores simples pero obligatorias para textos con espacios o caracteres especiales.
3. **Atributo de Pasos (`steps`):** Muchos componentes admiten el atributo booleano `{steps="true"}`. Cuando se activa, el Runtime de JavaScript retrasará la visualización de los sub-elementos del componente, revelándolos uno a uno en cada avance de la diapositiva.

### El Sistema de Colores Cromáticos (`data-color` / `color`)
Para garantizar la compatibilidad entre temas de diseño, PresentMD no utiliza nombres de colores específicos ni valores hexadecimales embebidos en el contenido. En su lugar, utiliza un sistema abstracto de variables del `1` al `6`:

| Token | Propósito Común | Variable CSS (Clase de Tema) |
| :---: | :--- | :--- |
| **`1`** | Color primario de acento | `--color-1` / `--color-1-contrast` |
| **`2`** | Color secundario de acento | `--color-2` / `--color-2-contrast` |
| **`3`** | Color de advertencia / precaución | `--color-3` / `--color-3-contrast` |
| **`4`** | Color de éxito / confirmación | `--color-4` / `--color-4-contrast` |
| **`5`** | Color de acento terciario | `--color-5` / `--color-5-contrast` |
| **`6`** | Color de peligro / error crítico | `--color-6` / `--color-6-contrast` |

Cuando un componente define un color (por ejemplo, `color="3"` o `status: green`), el compilador mapea el valor y genera un atributo HTML `data-color="X"`. La hoja de estilo del tema activo es responsable de asignar los colores reales basándose en dicho atributo.

---

## 2. Catálogo Exhaustivo de Componentes

A continuación se detallan los 25 componentes nativos registrados en el sistema:

---

### 1. Alert (`:::alert`)
* **Descripción:** Diseñado para destacar notas, advertencias, confirmaciones o errores críticos dentro de una diapositiva. Admite layouts verticales (con título y descripción en lista) u horizontales (elementos en línea).
* **Sintaxis de Autor:**
  ```markdown
  :::alert{type="warning" icon="⚠️" layout="vertical"}
  Atención con el Desbordamiento
  - Asegúrate de limpiar los observadores en JS.
  - Utiliza unidades relativas para los contenedores.
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `type` | String | `"1"` | Define el tipo de alerta (mapea al valor semántico de color). |
  | `icon` | String | `"ℹ️"` | Emoji o carácter que sirve de icono cabecera. |
  | `layout` | String | `"vertical"` | Distribución del contenido: `"vertical"` o `"horizontal"`. |
  | `size` | String | `""` | Modificador de escala opcional (ej: `"small"` o `"large"`). |
  | `color` | String | (Mismo de `type`) | Sobrescribe el valor del atributo `data-color` inyectado. |

* **HTML Generado:**
  ```html
  <div class="alert-box layout-vertical" data-color="warning">
    <div class="alert-header">
      <span class="alert-icon">⚠️</span>
      <div class="alert-title">Atención con el Desbordamiento</div>
    </div>
    <div class="alert-body">
      <ul class="alert-list">
        <li>Asegúrate de limpiar los observadores en JS.</li>
        <li>Utiliza unidades relativas para los contenedores.</li>
      </ul>
    </div>
  </div>
  ```

---

### 2. Animated Counter (`:::animated-counter`)
* **Descripción:** Incrementa o decrementa de forma fluida un valor numérico en pantalla al entrar en la diapositiva, ideal para estadísticas llamativas.
* **Sintaxis de Autor:**
  ```markdown
  :::animated-counter{from="0" to="99.9" prefix="" suffix="%" duration="1500" title="Disponibilidad Anual"}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `from` | String/Number | `"0"` | Valor numérico inicial de la animación. |
  | `to` | String/Number | `"100"` | Valor numérico final de llegada. |
  | `prefix` | String | `""` | Símbolo o texto a anteponer al número (ej: `$`). |
  | `suffix` | String | `""` | Símbolo o texto a posponer al número (ej: `%`). |
  | `duration` | String/Number | `"1500"` | Duración de la animación en milisegundos. |
  | `title` | String | `""` | Etiqueta descriptiva que se sitúa debajo de la cifra. |

* **HTML Generado:**
  ```html
  <div class="animated-counter-container">
    <span class="animated-counter" data-from="0" data-target="99.9" prefix="" suffix="%" duration="1500">
      0%
    </span>
    <div class="animated-counter-title">Disponibilidad Anual</div>
  </div>
  ```

---

### 3. Bar Chart (`:::bar-chart`)
* **Descripción:** Renderiza un gráfico de columnas verticales sencillo utilizando código HTML puro y estilos CSS flexibles.
* **Sintaxis de Autor:**
  ```markdown
  :::bar-chart{title="Ventas de Licencias" steps="true"}
  - [Q1] 45% {color="1"}
  - [Q2] 80% {color="2"}
  - [Q3] 95% {color="4"}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `title` | String | `""` | Título superior del gráfico. |
  | `steps` | Boolean | `false` | Si es `true`, las barras se elevan una a una secuencialmente. |

* **HTML Generado:**
  ```html
  <div class="bar-chart-wrapper">
    <div class="bar-chart-title">Ventas de Licencias</div>
    <div class="bar-chart-container">
      <div class="bar-chart-column data-step" data-step-idx="0">
        <div class="bar-value-label">45%</div>
        <div class="bar-track">
          <div class="chart-bar-fill" data-color="1" data-bar-height="45%"></div>
        </div>
        <div class="bar-label">Q1</div>
      </div>
      <!-- Resto de columnas... -->
    </div>
  </div>
  ```

---

### 4. Callout (`:::callout`)
* **Descripción:** Recuadros de notas laterales que admiten estados colapsables interactivos (usando los tags nativos `<details>` y `<summary>`).
* **Sintaxis de Autor:**
  ```markdown
  :::callout{type="warning" title="Precaución de Migración" collapsible="true"}
  La versión del motor de base de datos debe ser al menos la **15.4** para soportar llaves primarias compuestas.
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `type` | String | `"info"` | Tipo semántico: `"info"`, `"warning"`, `"error"`, `"success"`, `"tip"`. |
  | `title` | String | `""` | Título del encabezado del recuadro. |
  | `icon` | String | (Icono del `type`) | Permite sobrescribir el emoji del encabezado. |
  | `collapsible`| Boolean | `false` | Genera un bloque desplegable interactivo. |

* **HTML Generado (Con `collapsible="true"`):**
  ```html
  <details class="callout-box" data-color="warning">
    <summary class="callout-header">
      <span class="callout-icon">⚠️</span>
      <span class="callout-title">Precaución de Migración</span>
      <span class="callout-chevron">▼</span>
    </summary>
    <div class="callout-content">
      <p>La versión del motor de base de datos debe ser al menos la <strong>15.4</strong>...</p>
    </div>
  </details>
  ```

---

### 5. Cards Grid (`:::cards`)
* **Descripción:** Genera una rejilla de tarjetas estructuradas mediante una directiva interna de escape especial (`::card`).
* **Sintaxis de Autor:**
  ```markdown
  :::cards{cols="2" animate="true"}
  ::card{title="Servicios Micro" icon="⚙️" color="1"}
  Administración de tokens y autorización OAuth2 externa.
  - Rápido
  - Seguro
  ::
  ::card{title="Portal Web" icon="🖥️" color="2"}
  Aplicación Next.js para administración de proyectos.
  ::
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `cols` | String/Number | `"2"` | Número de columnas de la rejilla (`"1"` al `"4"`). |
  | `animate` | String/Boolean | `""` | Si es `"true"`, aplica una animación de aparición escalonada. |

* **HTML Generado:**
  ```html
  <div class="cards-grid has-staggered-animations" data-cols="2">
    <div class="card-box" data-color="1">
      <div class="card-header">
        <span class="card-icon">⚙️</span>
        <span class="card-title">Servicios Micro</span>
      </div>
      <div class="card-content">
        <p>Administración de tokens y autorización OAuth2 externa.</p>
        <ul class="card-list">
          <li>Rápido</li>
          <li>Seguro</li>
        </ul>
      </div>
    </div>
    <!-- Resto de tarjetas... -->
  </div>
  ```

---

### 6. Chart.js Wrapper (`:::chart`)
* **Descripción:** Declara un gráfico dinámico renderizado del lado del cliente mediante la librería Chart.js, manteniendo compatibilidad de accesibilidad para lectores de pantalla.
* **Sintaxis de Autor:**
  ```markdown
  :::chart{title="Ingresos Mensuales" type="line"}
  labels: ["Ene", "Feb", "Mar"]
  data: [12000, 15000, 19500]
  colors: [1, 2, 3]
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `title` | String | `""` | Título del gráfico. |
  | `type` | String | `"bar"` | Tipo de gráfico: `"bar"`, `"line"`, `"pie"`, `"doughnut"`. |

* **HTML Generado:**
  ```html
  <div class="chart-wrapper">
    <div class="chart-title">Ingresos Mensuales</div>
    <div class="chart-container">
      <canvas class="presentmd-chart" data-chart-config="{&quot;type&quot;: &quot;line&quot;, &quot;labels&quot;: [&quot;Ene&quot;, &quot;Feb&quot;, &quot;Mar&quot;], &quot;data&quot;: [12000, 15000, 19500], &quot;colors&quot;: [1, 2, 3]}"></canvas>
    </div>
    <table class="sr-only" aria-hidden="true">
      <thead><tr><th>Categoría</th><th>Valor</th></tr></thead>
      <tbody>
        <tr><th>Ene</th><td>12000</td></tr>
        <tr><th>Feb</th><td>15000</td></tr>
        <tr><th>Mar</th><td>19500</td></tr>
      </tbody>
    </table>
  </div>
  ```

---

### 7. Fade Stagger (`:::fade-stagger`)
* **Descripción:** Contenedor de animación genérico para desvanecer elementos internos con retrasos progresivos automáticos.
* **Sintaxis de Autor:**
  ```markdown
  :::fade-stagger{delay="200" speed="500"}
  - [Badge 1]{.badge-blue}
  - [Badge 2]{.badge-green}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `delay` | String/Number | `"100"` | Retraso en milisegundos entre la animación de cada elemento. |
  | `speed` | String/Number | `"300"` | Velocidad de la transición de opacidad (milisegundos). |

* **HTML Generado:**
  ```html
  <div class="fade-stagger-container" data-delay="200" data-speed="500">
    <ul class="content-list">
      <li><span class="badge badge-blue">Badge 1</span></li>
      <li><span class="badge badge-green">Badge 2</span></li>
    </ul>
  </div>
  ```

---

### 8. Feature Grid (`:::feature-grid`)
* **Descripción:** Bloques de visualización orientados a características destacadas, con soporte para rejillas multicolumnas e iconos prominentes.
* **Sintaxis de Autor:**
  ```markdown
  :::feature-grid{cols="2"}
  - [🔒] **Cifrado de Extremo a Extremo** mediante llaves AES-256. {color: 4}
  - [⚡] **Baja Latencia** con tiempos inferiores a 10ms globales. {color: 1}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `cols` | String/Number | `"3"` | Número de columnas de la rejilla de características. |

* **HTML Generado:**
  ```html
  <div class="feature-grid" data-cols="2">
    <div class="feature-card" data-color="4">
      <div class="fc-icon">🔒</div>
      <div class="fc-content"><strong>Cifrado de Extremo a Extremo</strong> mediante llaves AES-256.</div>
    </div>
    <div class="feature-card" data-color="1">
      <div class="fc-icon">⚡</div>
      <div class="fc-content"><strong>Baja Latencia</strong> con tiempos inferiores a 10ms globales.</div>
    </div>
  </div>
  ```

---

### 9. Flexible Grid (`:::grid`)
* **Descripción:** Permite dividir el contenido en columnas de anchos fraccionales o porcentuales definidos por el usuario de manera flexible.
* **Sintaxis de Autor:**
  ```markdown
  :::grid
  ::col{width="1/3" class="col-highlight"}
  ### Bloque Menor
  Texto descriptivo del primer tercio del contenedor.
  ::
  ::col{width="2/3"}
  ### Bloque Mayor
  Texto que ocupa los dos tercios restantes del espacio disponible.
  ::
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `class` | String | `""` | Clase CSS personalizada inyectada al contenedor padre. |

* **HTML Generado:**
  ```html
  <div class="grid-container" data-grid-cols="2">
    <div class="grid-column col-highlight" data-width="1/3" data-col-width="33.333%" data-col-frac="0.33333">
      <h3 class="slide-h3">Bloque Menor</h3>
      <p>Texto descriptivo del primer tercio del contenedor.</p>
    </div>
    <div class="grid-column" data-width="2/3" data-col-width="66.667%" data-col-frac="0.66667">
      <h3 class="slide-h3">Bloque Mayor</h3>
      <p>Texto que ocupa los dos tercios restantes del espacio disponible.</p>
    </div>
  </div>
  ```

---

### 10. Interactive Hotspots (`:::hotspots`)
* **Descripción:** Superpone puntos interactivos (pins) numerados sobre una imagen de fondo de forma precisa. Cada pin despliega un tooltip al pasar el cursor.
* **Sintaxis de Autor:**
  ```markdown
  :::hotspots{image="architecture_map.png"}
  - [25%, 40%] **Gateway API**: Balancea las peticiones externas.
  - [80%, 75%] **Clúster BD**: Almacén principal replicado.
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `image` | String | (Obligatorio) | Ruta o URL de la imagen sobre la cual superponer los pins. |

* **HTML Generado:**
  ```html
  <div class="hotspots-container">
    <img src="architecture_map.png" class="hotspots-image" />
    <div class="hotspots-pins-layer">
      <div class="hotspot-pin" data-left="25%" data-top="40%" data-index="0">
        <div class="pin-marker"><span class="pin-number">1</span></div>
        <div class="pin-tooltip">
          <div class="pin-tooltip-arrow"></div>
          <div class="pin-tooltip-content"><strong>Gateway API</strong>: Balancea las peticiones externas.</div>
        </div>
      </div>
      <!-- Resto de pins... -->
    </div>
  </div>
  ```

---

### 11. Info Grid (`:::info-grid`)
* **Descripción:** Diseñado para resumir metadatos estructurados de manera tabular limpia en una rejilla compacta.
* **Sintaxis de Autor:**
  ```markdown
  :::info-grid
  - [Licencia] MIT License
  - [Estado] Estable v2.4
  - [Autor] Core Team
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <div class="info-grid">
    <div class="info-box">
      <div class="ib-label">Licencia</div>
      <div class="ib-value">MIT License</div>
    </div>
    <!-- Resto de cajas... -->
  </div>
  ```

---

### 12. KPI Grid (`:::kpi-grid`)
* **Descripción:** Panel de tarjetas de números impactantes y KPIs con colores semánticos asociados a su estado.
* **Sintaxis de Autor:**
  ```markdown
  :::kpi-grid
  - [125ms] Tiempo de Respuesta {status: green}
  - [34%] Sobrecarga de Memoria {status: warning}
  - [8] Errores en Pipeline {status: critical}
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **Mapeo de Status en Código:**
  * `green` o `up` -> `data-color="4"`
  * `warning` o `amber` -> `data-color="3"`
  * `critical` o `down` -> `data-color="6"`
  * (Si es un número del 1 al 6, se inyecta directamente como `data-color`).

* **HTML Generado:**
  ```html
  <div class="kpi-grid">
    <div class="kpi-card" data-color="4">
      <div class="kpi-value">125ms</div>
      <div class="kpi-label">Tiempo de Respuesta</div>
    </div>
    <!-- Resto de métricas... -->
  </div>
  ```

---

### 13. Layer Stack (`:::layer-stack`)
* **Descripción:** Superpone una secuencia de imágenes en una sola posición. Cada avance de diapositiva (paso) oculta la capa actual y revela la siguiente, simulando animaciones de capas.
* **Sintaxis de Autor:**
  ```markdown
  :::layer-stack
  ![Capa Base](infra_step1.png)
  ![Capa Servicios](infra_step2.png)
  ![Capa Aplicación](infra_step3.png)
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <div class="layer-stack">
    <img src="infra_step1.png" alt="Capa Base" class="layer-image active" />
    <img src="infra_step2.png" alt="Capa Servicios" class="layer-image layer-hidden" />
    <img src="infra_step3.png" alt="Capa Aplicación" class="layer-image layer-hidden" />
  </div>
  ```

---

### 14. Parallel Compare (`:::parallel-compare`)
* **Descripción:** Versión modularizada del layout de comparación en paralelo que puede anidarse dentro de cualquier diapositiva. Columnas separadas mediante tres guiones (`---`).
* **Sintaxis de Autor:**
  ```markdown
  :::parallel-compare{center-badge="VS"}
  ### Monolito Tradicional
  - Acoplamiento fuerte
  - Escalado complejo
  ---
  ### Microservicios
  - Despliegue modular
  - Alta resiliencia
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `center-badge`| String | `"VS"` | Texto de la medalla de contraste central entre las columnas. |

* **HTML Generado:**
  ```html
  <div class="parallel-container">
    <div class="pc-left">
      <div class="pc-col-header">Monolito Tradicional</div>
      <div class="pc-node">Acoplamiento fuerte</div>
      <div class="pc-node">Escalado complejo</div>
    </div>
    <div class="pc-center">
      <span class="vs-badge">VS</span>
    </div>
    <div class="pc-right">
      <div class="pc-col-header">Microservicios</div>
      <div class="pc-node">Despliegue modular</div>
      <div class="pc-node">Alta resiliencia</div>
    </div>
  </div>
  ```

---

### 15. Process Flow (`:::process-flow`)
* **Descripción:** Dibuja cajas de flujo de procesos horizontales y secuenciales ordenadas numéricamente de manera lineal.
* **Sintaxis de Autor:**
  ```markdown
  :::process-flow{steps="true"}
  - [Fase A] Planificación de Arquitectura {color: 1}
  - [Fase B] Construcción del Backend Core {color: 2}
  - [Fase C] Validación de Pruebas e QA {color: 4}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `steps` | Boolean | `false` | Controla si el flujo secuencial de cajas se revela paso a paso. |

* **HTML Generado:**
  ```html
  <pmd-process-flow data-steps="true">
    <div class="pmd-process-flow-item step-hidden" data-step data-color="1">
      <div class="pmd-process-flow-text">1</div>
      <div class="pmd-process-flow-label">Fase A</div>
      <div class="pmd-process-flow-desc">Planificación de Arquitectura</div>
    </div>
    <!-- Resto de fases... -->
  </pmd-process-flow>
  ```

---

### 16. Progress Bars (`:::progress-bars`)
* **Descripción:** Barras de porcentaje horizontales para mostrar el avance de tareas o componentes.
* **Sintaxis de Autor:**
  ```markdown
  :::progress-bars
  - Integración Continua: 95% {color: 4}
  - Cobertura de Test unitarios: 82% {color: 2}
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <div class="progress-row">
    <span class="progress-label">Integración Continua</span>
    <div class="progress-track">
      <div class="bar-fill" data-color="4" data-target-width="95%"></div>
    </div>
    <span class="progress-pct">95%</span>
  </div>
  ```

---

### 17. Progress Ring (`:::progress-ring`)
* **Descripción:** Muestra un indicador circular de porcentaje con trazados SVG animados.
* **Sintaxis de Autor:**
  ```markdown
  :::progress-ring{value="87" size="140" stroke="10" color="4" title="Optimización SEO"}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `value` | String/Number | `"0"` | Porcentaje de avance circular (de `0` a `100`). |
  | `size` | String/Number | `"120"` | Ancho y alto de la caja del SVG en píxeles. |
  | `stroke` | String/Number | `"8"` | Grosor de la línea del anillo indicador. |
  | `color` | String | `"1"` | Valor de variable cromática inyectada en `data-color`. |
  | `title` | String | `""` | Título del indicador ubicado abajo del anillo. |

* **HTML Generado:**
  ```html
  <div class="progress-ring-wrapper">
    <div class="progress-ring-container" data-ring-size="140">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="65" stroke-width="10" fill="transparent" class="progress-ring-bg"></circle>
        <circle cx="70" cy="70" r="65" stroke-width="10" fill="transparent" class="progress-ring-fill" data-color="4"
                stroke-dasharray="408.41" stroke-dashoffset="408.41" data-value="87" data-circumference="408.41"
                transform="rotate(-90 70 70)"></circle>
      </svg>
      <div class="progress-ring-percentage">87%</div>
    </div>
    <div class="progress-ring-title">Optimización SEO</div>
  </div>
  ```

---

### 18. Pyramid (`:::pyramid`)
* **Descripción:** Dibuja diagramas jerárquicos de pirámide con soporte para layouts personalizados e incrementos en pasos.
* **Sintaxis de Autor:**
  ```markdown
  :::pyramid{layout="pyramid" steps="true"}
  - [Capa UI] React Native & Next {color: 1}
  - [Capa Backend] Python & Go {color: 2}
  - [Capa Datos] PostgreSQL {color: 5}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `layout` | String | `"pyramid"` | Estilo de renderizado del componente. |
  | `steps` | Boolean | `false` | Determina si las capas aparecen progresivamente. |

* **HTML Generado:**
  ```html
  <pmd-pyramid data-layout="pyramid" data-steps="true">
    <div class="pmd-pyramid-item step-hidden" data-step data-color="1">
      <div class="pmd-pyramid-text">1</div>
      <div class="pmd-pyramid-label">Capa UI</div>
      <div class="pmd-pyramid-desc">React Native & Next</div>
    </div>
    <!-- Resto de capas... -->
  </pmd-pyramid>
  ```

---

### 19. Radial Process (`:::radial-process`)
* **Descripción:** Representa un flujo de tareas dispuestas en un esquema circular o radial alrededor de un núcleo central.
* **Sintaxis de Autor:**
  ```markdown
  :::radial-process{center-title="SaaS Core" steps="true"}
  - [Auth] Gestión OAuth2 {color: 1}
  - [Billing] Cobros Stripe {color: 2}
  - [CDN] Caché Assets {color: 3}
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `center-title`| String | `""` | Texto que se dibuja en el nodo central del diagrama. |
  | `steps` | Boolean | `false` | Si es `true`, los nodos externos van apareciendo uno a uno. |

* **HTML Generado:**
  ```html
  <pmd-radial-process center-title="SaaS Core" data-steps="true">
    <div class="pmd-radial-process-item step-hidden" data-step data-color="1">
      <div class="pmd-radial-process-label">Auth</div>
      <div class="pmd-radial-process-desc">Gestión OAuth2</div>
    </div>
    <!-- Resto de nodos... -->
  </pmd-radial-process>
  ```

---

### 20. Interactive Spotlight (`:::spotlight`)
* **Descripción:** Inyecta configuraciones de foco y guías visuales sobre elementos específicos del DOM basándose en clases y selectores CSS.
* **Sintaxis de Autor:**
  ```markdown
  :::spotlight
  - [#kpi-response-time] Explicación del tiempo de respuesta del servidor.
  - [Caja Nueva] Creación y foco de una tarjeta ficticia para análisis. {variant="circle" class="highlight-action"}
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <div class="spotlight-targets-container">
    <div id="spot-tgt-1a2b3c" class="spotlight-target-circle highlight-action">Caja Nueva</div>
  </div>
  <div class="spotlight-config" data-spotlight-steps="[{&quot;selector&quot;: &quot;#kpi-response-time&quot;, &quot;content&quot;: &quot;Explicación del tiempo de respuesta del servidor.&quot;}, {&quot;selector&quot;: &quot;#spot-tgt-1a2b3c&quot;, &quot;content&quot;: &quot;Creación y foco de una tarjeta ficticia para análisis.&quot;}]"></div>
  ```

---

### 21. Steps (`:::steps`)
* **Descripción:** Contenedor básico diseñado para listas desordenadas en las que cada viñeta o bloque se revela secuencialmente en cada avance de diapositiva.
* **Sintaxis de Autor:**
  ```markdown
  :::steps
  - Iniciar sesión en el panel del administrador.
  - Generar el nuevo token de desarrollo.
  - Configurar las variables locales.
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <ul class="steps-list">
    <li data-step>Iniciar sesión en el panel del administrador.</li>
    <li data-step>Generar el nuevo token de desarrollo.</li>
    <li data-step>Configurar las variables locales.</li>
  </ul>
  ```

---

### 22. Premium Table (`:::pmd-table`)
* **Descripción:** Envuelve una tabla estándar de Markdown con capacidades avanzadas de diseño de temas, filas de totales destacadas y colores asociados.
* **Sintaxis de Autor:**
  ```markdown
  :::pmd-table{title="Métricas Anuales" variant="striped" total-row="true" colors="1,2"}
  | Concepto | Q1 | Q2 |
  | :--- | :---: | :---: |
  | Ventas | $1200 | $1500 |
  | Totales | $1200 | $1500 |
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `title` | String | `""` | Título que se renderiza dentro del tag `<caption>` de la tabla. |
  | `variant` | String | `"angled"` | Diseño visual de la tabla (ej. `"angled"`, `"striped"` o `"minimal"`). |
  | `total-row` | Boolean | `false` | Resalta la última fila de la tabla como fila de totalización. |
  | `colors` | String | `""` | Lista de índices de colores separados por coma a declarar (ej. `"1,2"`). |

* **HTML Generado:**
  ```html
  <div class="pmd-table-wrapper" data-variant="striped" data-total-row="true" style="--tc-1: var(--color-1); --tc-text-1: var(--color-1-contrast); --tc-2: var(--color-2); --tc-text-2: var(--color-2-contrast)">
    <table>
      <caption>Métricas Anuales</caption>
      <thead>
        <tr><th>Concepto</th><th>Q1</th><th>Q2</th></tr>
      </thead>
      <tbody>
        <tr><td>Ventas</td><td>$1200</td><td>$1500</td></tr>
        <tr><td>Totales</td><td>$1200</td><td>$1500</td></tr>
      </tbody>
    </table>
  </div>
  ```

---

### 23. Tabs (`:::tabs`)
* **Descripción:** Panel contenedor accesible (bajo estándares WAI-ARIA) que organiza el contenido en pestañas de navegación horizontal.
* **Sintaxis de Autor:**
  ```markdown
  :::tabs{variant="pills"}
  === Endpoint REST ===
  `POST /api/v1/auth`
  === GraphQL ===
  `mutation { login { token } }`
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `variant` | String | `""` | Variante estética del selector de pestañas (ej: `"pills"` o `"underlined"`). |

* **HTML Generado:**
  ```html
  <div class="tabs-container" data-variant="pills" id="tabs-f3e2d1-container">
    <div class="tabs-list" role="tablist" aria-label="Contenido en pestañas">
      <button class="tab-button active" id="tabs-f3e2d1-tab-0" role="tab" aria-selected="true" aria-controls="tabs-f3e2d1-panel-0" tabindex="0">Endpoint REST</button>
      <button class="tab-button" id="tabs-f3e2d1-tab-1" role="tab" aria-selected="false" aria-controls="tabs-f3e2d1-panel-1" tabindex="-1">GraphQL</button>
    </div>
    <div class="tabs-panels">
      <div class="tab-panel active" id="tabs-f3e2d1-panel-0" role="tabpanel" aria-labelledby="tabs-f3e2d1-tab-0">
        <p><code>POST /api/v1/auth</code></p>
      </div>
      <div class="tab-panel" id="tabs-f3e2d1-panel-1" role="tabpanel" aria-labelledby="tabs-f3e2d1-tab-1" hidden>
        <p><code>mutation { login { token } }</code></p>
      </div>
    </div>
  </div>
  ```

---

### 24. Timeline (`:::timeline`)
* **Descripción:** Dibuja cronogramas u hojas de ruta de hitos temporales en formato horizontal conectado por flechas.
* **Sintaxis de Autor:**
  ```markdown
  :::timeline
  - **Fase 1**: Análisis Inicial
    - Entrevistas con stakeholders.
    - Levantamiento de requerimientos.
    > Especificación de Requerimientos Completa.
  - **Fase 2**: Implementación Core
    - Escritura de componentes base.
    > Entregable de Pipeline Integrado.
  :::
  ```
* **Atributos Soportados:** Ninguno.
* **HTML Generado:**
  ```html
  <div class="timeline">
    <div class="timeline-phase">
      <span class="tl-badge">Fase 1</span>
      <div class="tl-title">Análisis Inicial</div>
      <div class="tl-desc">• Entrevistas con stakeholders.</div>
      <div class="tl-desc">• Levantamiento de requerimientos.</div>
      <div class="tl-deliverable">→ Especificación de Requerimientos Completa.</div>
    </div>
    <div class="timeline-arrow">→</div>
    <div class="timeline-phase">
      <span class="tl-badge">Fase 2</span>
      <div class="tl-title">Implementación Core</div>
      <div class="tl-desc">• Escritura de componentes base.</div>
      <div class="tl-deliverable">→ Entregable de Pipeline Integrado.</div>
    </div>
  </div>
  ```

---

### 25. Typewriter (`:::typewriter`)
* **Descripción:** Genera animaciones de escritura dinámica por terminal (efecto de teletipo) sobre textos o bloques de comandos en pantalla.
* **Sintaxis de Autor:**
  ```markdown
  :::typewriter{speed="70" delay="300" color="primary" size="large"}
  presentmd serve document.md --theme obsidian-glass
  :::
  ```
* **Atributos Soportados:**
  | Atributo | Tipo | Por Defecto | Descripción |
  | :--- | :--- | :--- | :--- |
  | `speed` | String/Number | `"50"` | Velocidad de tipografía por carácter (milisegundos). |
  | `delay` | String/Number | `"200"` | Retraso inicial antes de que comience a escribir. |
  | `size` | String | `""` | Escala del texto (ej. `"small"`, `"large"` o `"huge"`). |
  | `color` | String | `""` | Modificador de color del texto. |

* **HTML Generado:**
  ```html
  <div class="typewriter-container" data-size="large" data-color="primary" data-speed="70" data-delay="300">
    <span class="typewriter-text">presentmd serve document.md --theme obsidian-glass</span>
    <span class="typewriter-cursor">|</span>
  </div>
  ```

---

## 3. Mecánica de Anidamiento y Contenedores Genéricos

### Reglas de Bloques y Escape de Contenido
Los parsers del core de PresentMD procesan los archivos Markdown línea por línea buscando las directivas de contenedores. Para poder anidar elementos o directivas secundarias de manera segura sin confundir al parser, se deben respetar las siguientes directrices:

1. **La directiva de nivel superior:** Mantiene la sintaxis estándar de triples dos puntos (`:::nombre`).
2. **Las directivas secundarias o de nodo:** Utilizan dobles dos puntos (`::nombre`) y terminan con un bloque de cierre limpio de dobles dos puntos (`::`).
3. **Anidamiento en Grids y Tarjetas:** En los componentes `:::grid` y `:::cards`, el contenido interno debe estar encapsulado estrictamente dentro de sus directivas hijas (`::col` o `::card`). Cualquier texto libre que no esté dentro de estas estructuras hijas provocará comportamientos de renderizado inesperados o fallos en el auto-ajuste de cajas del layout.

Ejemplo correcto de una alerta anidada dentro de una rejilla de dos columnas:

```markdown
:::grid
::col{width="1/2"}
### Columna Izquierda
Este texto se muestra en la primera mitad del lienzo.
::
::col{width="1/2"}
:::alert{type="success"}
¡Éxito!
Operación de migración completada en paralelo.
:::
::
:::
```

---

## 4. Compatibilidad con el Runtime de Animación (`:::steps`)

El Runtime de PresentMD controla los flujos de presentación mediante la interceptación de eventos de navegación. Para dar soporte a la animación paso a paso sin utilizar librerías externas de gran tamaño, se utiliza el siguiente contrato estructurado:

1. **El Atributo `data-step`:** Cualquier elemento HTML que contenga el atributo `data-step` se registra automáticamente en la pila de animaciones de la diapositiva en la que reside.
2. **La clase `.step-hidden`:** Al entrar a la diapositiva, todos los elementos marcados con `data-step` o pertenecientes a un contenedor con animaciones activas (`data-steps="true"`) reciben dinámicamente la clase CSS `.step-hidden` (que comúnmente define `opacity: 0; pointer-events: none;` o estilos similares en el tema).
3. **Acción de Avance:** Al presionar *Avanzar*, el controlador JS busca el siguiente elemento en la pila local y le retira la clase `.step-hidden`, aplicando opcionalmente clases de transición como `.step-active`.
4. **Reseteo en retrocesos:** Si el orador retrocede de lámina, el runtime restablece todos los estados agregando nuevamente `.step-hidden` para que la presentación se mantenga consistente en futuras pasadas.