---
title: "Dominio Transaccional - Estrategia de Migración"
theme: convergencia-tech
animations: true
slide_number: true
nav_arrows: true
footer: "Convergencia Tecnológica · Track Transacciones"
closing_slide: false
---

::layout{title}

[PROYECTO · CONVERGENCIA TECNOLÓGICA]{.cover-top}

# Dominio Transaccional
## Estrategia de Migración

Migración del historial transaccional (Transbank · BUT) hacia el modelo destino (evertec · Pay Studio)

[Mayo 2026]{.badge-transbank}

:::grid{class="cover-footer"}
::col
Track Transacciones · J. Bustamante
::col{class="tf-right"}
**Clasificación:** Confidencial · uso interno
:::

---

::layout{standard}
eyebrow: Dominio 2 · Transacciones · Roadmap
# Estrategia en 3 Fases
## De la carga histórica al cutover definitivo

:::timeline
- **Etapa 1 · Preparalelo**: Carga de Historia
  - Exportar 18 meses de BUT en Parquet
  - Transportar a S3 landing zone
  - ETL evertec carga en Pay Studio DWH
  - Validar integridad y conciliación volumétrica
  > Historia migrada y validada
- **Etapa 2 · Paralelo 15+1**: Validación en Paralelo
  - Pay Studio procesa en modo shadow
  - Flujo continuo vía Kafka (PTLF + ITM)
  - Comparar BUT productivo vs UBUT
  - Validar cuadratura por comercio
  > Métricas OK → habilita cutover
- **Cutover 17+1**: Producción
  - Pay Studio asume titularidad transaccional
  - Retorno de TRX liquidadas a BUT (Kafka + archivos)
  - Sistemas legacy siguen leyendo de BUT
  - Monitoreo post-corte intensivo
  > Pay Studio en producción
:::

---

::layout{standard}
eyebrow: Dominio 2 · Etapa 1 · Preparalelo
# Carga de Historia: BUT → Pay Studio [Ver detalle →](#detalle-ingesta){.link-anexo}
## Flujo de migración de 18 meses de data transaccional (8 tablas exportables · ~8.1 TB)

:::process-flow
- [BUT (Snowflake)] Capa refined · 8 tablas exportables {icon: "❄️", color: "1"}
- [Exportación] Parquet · Particionado trimestral {color: "2"}
- [Bucket S3] Landing zone · 8 particiones {icon: "🪣", color: "1"}
- [ETL evertec] Carga + validación integridad {color: "2"}
- [Pay Studio DWH] Historia 18m disponible {icon: "📊", color: "4"}
:::

:::info-grid
- Formato: Apache Parquet (columnar)
- Transporte: AWS S3 (bucket dedicado)
- Particiones: 8 trimestres independientes
- Validación: Conciliación volumétrica + integridad
:::

---

::layout{standard}
eyebrow: Dominio 2 · Transacciones · Volumetría
# Volumetría: El Desafío en Números [Ver detalle →](#detalle-volumetria){.link-anexo}
## 35 mil millones de registros exportables · ~8.1 TB exportación · 8 tablas a migrar

:::kpi-grid
- [35,011M] Registros exportables {status: "6"}
- [8.1 TB] Export estimado {status: "2"}
- [8] Tablas a migrar {status: "1"}
- [18 meses] Historia {status: "3"}
:::

:::grid
::col{width="1/2"}
### Tablas Principales (98% del volumen)
*   **TX_PTLF:** 11,862M reg (~4.4 TB)
*   **TX_TARIFICADA:** 10,603M reg (~2.0 TB)
*   **TX_ABONADA:** 11,661M reg (~1.6 TB)
::
::col{width="1/2"}
### Carga Incremental y Soporte
*   **TX_TARIFICADA_CUOTA:** 617M reg
*   **Otras 4 tablas:** 98M reg (Retenciones, abonos consolidados y cuota acción)
::
:::

---

::layout{standard}
eyebrow: Dominio 2 · Etapa 1 · Estrategia de carga
# Particionamiento de la Historia
## 8 particiones trimestrales (suma de 8 tablas exportables por período) — carga independiente

:::progress-bars
- P1 · Ene-Mar 23: 73% {color: "1"}
- P2 · Abr-Jun 23: 79% {color: "1"}
- P3 · Jul-Sep 23: 83% {color: "1"}
- P4 · Oct-Dic 23: 87% {color: "1"}
- P5 · Ene-Mar 24: 91% {color: "2"}
- P6 · Abr-Jun 24: 95% {color: "2"}
- P7 · Jul-Sep 24: 99% {color: "2"}
- P8 · Oct-May 25: 100% {color: "2"}
:::

---

::layout{standard}
eyebrow: Dominio 2 · Desafío Crítico · PCI
# Desafío PCI: Tokenización [Ver detalle →](#detalle-tokenizacion){.link-anexo}
## Bloqueador sin solución arquitectónica definida — impacta Etapa 1 y Etapa 2

:::kpi-grid
- [35,011M] Registros tokenizados {status: "6"}
- [2] Tokenizadores distintos {status: "6"}
- [SIN DEFINIR] Solución Arquitectura {status: "6"}
- [PCI-DSS] Normativa impactada {status: "3"}
:::

:::alert{type="6" icon="⚠️" layout="vertical"}
**Etapa 1 (Historia):** Data en BUT tokenizada con tokenizador Transbank → requiere destokenización masiva para migrar a Pay Studio. Exposición temporal de PAN, impacto PCI directo, sin arquitectura aprobada.
:::

:::alert{type="6" icon="⚠️" layout="vertical"}
**Etapa 2 (Paralelo):** Pay Studio tokeniza con tokenizador evertec → UBUT (Transbank) no puede resolver esos tokens. Comparación de cuadratura a nivel PAN queda comprometida.
:::

---

::layout{standard}
eyebrow: Dominio 2 · Etapa 2 · Paralelo 15+1
# Validación en Paralelo: BUT vs UBUT [Ver detalle →](#detalle-ubut){.link-anexo}
## Pay Studio se ingesta de PTLF e ITM (sin tarjeta) — se compara contra BUT productivo

:::parallel-compare{center-badge="VS"}
### Productivo (Base24/BUT)
*   **Base24:** Autorización productiva
*   **Nuevo Abono:** Proceso actual
*   **BUT:** Producción (referencia)
---
### Shadow (Pay Studio/UBUT)
*   **Pay Studio:** Ingesta PTLF + ITM
*   **Kafka:** TRX procesadas → ingesta UBUT
*   **UBUT:** Modelo paralelo (validación)
:::

---

::layout{standard}
eyebrow: Dominio 2 · Post-Cutover 17+1
# Convivencia: Pay Studio → BUT [Ver detalle →](#detalle-retorno){.link-anexo}
## Pay Studio en producción retorna data a BUT para sistemas legacy

:::process-flow
- [Pay Studio] Producción · Titularidad TRX {icon: "📊", color: "4"}
- [Kafka + Archivos] TRX liquidadas · Layout {color: "2"}
- [Tablas BUT] PTLF · ABONADA · ADQUIRIDA {icon: "❄️", color: "1"}
- [Legacy] Facturación · Portal · ARC {color: "2"}
:::

:::alert{type="3" icon="⚠️" layout="horizontal"}
- **Pendiente (D2-004):** Validar con evertec si el layout de salida es compatible con BUT o requiere adaptador.
:::

---

::layout{standard}
eyebrow: Dominio 2 · Interdependencias
# Dependencias entre Dominios
## Qué necesitamos antes y quién depende de nosotros

| Dominio | Relación | Detalle | Criticidad |
| :--- | :--- | :--- | :--- |
| **D1 · Comercios** | Prerequisito | FK — debe migrar ANTES que transacciones | [ALTA]{.badge-red} |
| **D3 · Liquidaciones** | Dependiente | Se derivan de transacciones | [ALTA]{.badge-red} |
| **D6 · Terminales** | Bidireccional | Origen autorización · puertos F5 | [MEDIA]{.badge-amber} |
| **D8 · Contracargos** | Dependiente | Referencia TID de transacciones | [MEDIA]{.badge-amber} |

---

::layout{standard}
eyebrow: Dominio 2 · Definiciones con evertec
# Definiciones Técnicas Pendientes de Cierre
## 6 temas que requieren resolución conjunta con evertec

| # | Tema | Transbank entrega / publica | evertec resuelve / desarrolla | Criticidad |
| :-: | :--- | :--- | :--- | :--- |
| **1** | Ingesta de historia | Exporta Parquet particionado → S3 | Consume Parquet, desarrolla ETL, carga | [ALTA]{.badge-red} |
| **2** | Retorno Pay Studio → BUT | Provee diccionario de datos BUT | Emite por Kafka con layout BUT | [ALTA]{.badge-red} |
| **3** | Destokenización masiva | Archivos con token Transbank | Destokeniza en su ambiente PCI | [ALTA]{.badge-red} |
| **4** | Resolución PAN en paralelo | Acceso a PAN real para conciliación | Mecanismo: token bridge/enmascarado | [ALTA]{.badge-red} |
| **5** | Tópico Kafka PTLF | Publica autorizaciones en línea | Confirma consumo e integra ingesta | [MEDIA]{.badge-amber} |
| **6** | Tópico Kafka ITM | Publica movimientos sin tarjeta | Confirma consumo e integra ingesta | [MEDIA]{.badge-amber} |

---

::layout{standard}
eyebrow: Dominio 2 · Posición Transbank
# Propuesta de Resolución — División de Responsabilidades
## Transbank pone a disposición data e interfaces existentes · evertec construye la solución

| # | Posición Transbank | Expectativa hacia evertec | Criticidad |
| :-: | :--- | :--- | :--- |
| **1** | Exporta y deposita Parquet en S3 | Responsable de ingesta completa (ETL, carga DWH) | [ALTA]{.badge-red} |
| **2** | Provee diccionario de datos BUT (sin modificar) | Retorna mismo layout. evertec hace adaptador si varía | [ALTA]{.badge-red} |
| **3** | Entrega archivos con token Transbank tal cual | Destokeniza en su ambiente PCI (acceso facilitado) | [ALTA]{.badge-red} |
| **4** | Requiere PAN real para cuadratura en paralelo | Propone/desarrolla mecanismo de acceso seguro | [ALTA]{.badge-red} |
| **5-6** | Publica tópicos PTLF e ITM existentes | Confirma capacidad de consumo e integra | [MEDIA]{.badge-amber} |

---

::layout{title}

[Convergencia Tecnológica · Operaciones y Tecnología]{.cover-top}

# Gracias!

Track Transacciones · J. Bustamante

[Mayo 2026]{.badge-transbank}

:::grid{class="cover-footer"}
::col
Confidencial · uso interno
:::

---

::layout{annex}
eyebrow: Anexo · Volumetría
# Volumetría Completa — Tablas BUT {#detalle-volumetria}
## Detalle de las 14 tablas del modelo transaccional · 8 tablas exportables marcadas ✓

*   El modelo BUT comprende 14 tablas. De estas, **8 son exportables** hacia Pay Studio.
*   Las 3 tablas principales (PTLF, TARIFICADA, ABONADA) representan el 98% del volumen exportable.
*   Total exportable: ~35,011M registros / ~8,104 GB estimado de exportación.

| Tabla | Registros | Export Est. (GB) | Exportable | Criticidad |
| :--- | :--- | :--- | :--- | :--- |
| **TX_PTLF** | 11,862,493,600 | 4,394.75 | ✓ | [ALTA]{.badge-red} |
| **TX_ADQUIRIDA** | 11,343,157,138 | 2,085.63 | — | [ALTA]{.badge-red} |
| **TX_TARIFICADA** | 10,603,460,384 | 2,001.46 | ✓ | [ALTA]{.badge-red} |
| **TX_ABONADA** | 11,661,567,741 | 1,600.53 | ✓ | [ALTA]{.badge-red} |
| **TX_FACTURADA** | 3,853,742,990 | 454.05 | — | [MEDIA]{.badge-amber} |
| **TX_OUTGOING** | 3,787,010,024 | 435.59 | — | [MEDIA]{.badge-amber} |
| **TX_TARIFICADA_CUOTA** | 617,479,033 | 82.74 | ✓ | [MEDIA]{.badge-amber} |
| **TX_RETENCION_MOVIMIENTO** | 98,446,767 | 11.01 | ✓ | [MEDIA]{.badge-amber} |
| **TX_RETENCION_ADMIN** | 82,209,683 | 7.91 | ✓ | [MEDIA]{.badge-amber} |
| **TX_ABONO_CONSOLIDADO** | 73,078,070 | 4.86 | ✓ | [MEDIA]{.badge-amber} |

---

::layout{annex}
eyebrow: Anexo · Ingesta
# Mecanismo de Ingesta — Historia y Flujo Continuo {#detalle-ingesta}
## Detalle técnico del proceso de carga hacia Pay Studio

*   **Batch de Historia:** Extracción Snowflake en Parquet particionado trimestral.
*   **Landing Zone:** AWS S3 dedicado para migración.
*   **ETL de Carga:** Orquestado por evertec con validación de volumen e integridad.

| Aspecto | Definición |
| :--- | :--- |
| **Origen** | BUT Snowflake · capa refined · 14 tablas |
| **Formato** | Apache Parquet (columnar, comprimido) |
| **Particionamiento** | Trimestral (8 particiones: Ene 2023 — Actual) |
| **Landing zone** | Bucket S3 dedicado para migración |
| **Orquestación** | ETL evertec (carga + validación de integridad) |
| **Destino final** | Pay Studio DWH |
| **Ventana** | 18 meses |

---

::layout{annex}
eyebrow: Anexo · Paralelo
# UBUT Paralelo — Estructura y Campo de Origen {#detalle-ubut}
## Modelo de validación durante el paralelo 15+1

*   **Shadowing:** Pay Studio shadow ingesta desde tópicos Kafka PTLF e ITM sin tarjeta.
*   **Estructura:** BUT productivo sin cambios. UBUT paralelo en Snowflake alimentado por Pay Studio.
*   **Origen de Autorización:** A partir del paralelo, la data transaccional debe clasificar el origen.

| Valor | Significado | Origen del dato |
| :--- | :--- | :--- |
| **ADVICE** | Autorizada por Base24 (passthrough) | PTLF tradicional |
| **OWNER** | Autorizada por Pay Studio | UBUT alimentado por Pay Studio |

---

::layout{annex}
eyebrow: Anexo · Seguridad
# Desafío PCI: Tokenización — Detalle Completo {#detalle-tokenizacion}
## Bloqueador crítico sin solución arquitectónica definida

*   **Incompatibilidad:** Tokenizadores de Transbank y evertec no se reconocen mutuamente.
*   **Etapa 1 (Masiva):** Destokenizar 55,424M registros expone PAN. Requiere ambiente seguro PCI y alta capacidad de procesamiento.
*   **Etapa 2 (Coexistencia):** Retorno de trx a UBUT con token evertec que Transbank no puede resolver. Comprometida la validación de cuadratura a nivel PAN.

| ID | Decisión Pendiente | Responsable | Criticidad |
| :-: | :--- | :--- | :--- |
| **D2-005** | Destokenización masiva (Etapa 1): ambiente PCI, capacidad, ventana | J.Bustamante + Seguridad + evertec | [ALTA]{.badge-red} |
| **D2-006** | Coexistencia tokenizadores (Etapa 2): token bridge, sin PAN, u otra | J.Bustamante + Seguridad + evertec | [ALTA]{.badge-red} |

---

::layout{annex}
eyebrow: Anexo · Convivencia
# Retorno Post-Cutover — Pay Studio → BUT {#detalle-retorno}
## Mecanismo de convivencia una vez que Pay Studio asume producción

*   **Mecanismo:** Tópicos Kafka (near-real time) y archivos de salida batch.
*   **Destino:** Inyección en tablas BUT (PTLF, ABONADA, ADQUIRIDA, TARIFICADA).
*   **Consumidores:** Facturación, portal comercios, ARC y reportería legacy.

> ⚠️ **Pendiente (D2-004):** Validar con evertec mecanismo exacto: layout, tópicos Kafka, frecuencia, necesidad de adaptador.

---

::layout{annex}
eyebrow: Anexo · Requisitos
# Requisitos Previos — Desglose Completo {#detalle-requisitos}
## Lo que se necesita antes de iniciar la migración

### 1. Infraestructura y Ambientes
*   Habilitación de ambiente Datawarehouse en Pay Studio (~13 TB).
*   Configuración de entorno UBUT (réplica de estructuras).
*   Conectividad: BUT → Pay Studio y Pay Studio → UBUT.

### 2. Mapeo y Transformación
*   Documentación modelo origen (BUT) vs destino (Pay Studio DWH).
*   Reglas de transformación y normalización de data histórica.
*   Identificación de campos críticos.

### 3. Procesos y Validación
*   Desarrollo de ETLs históricos y carga incremental real-time (Kafka).
*   Métricas de comparación BUT productivo vs UBUT y criterios de aceptación.
