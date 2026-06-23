# THEMES_SPEC.md — PresentMD Visual Architecture & Components
**Version:** 1.0
**Target Parser:** `markdown-it-py` (Custom Containers & Inline rules)
**Rendering Target:** Vanilla CSS (CSS Grid + Custom Properties)

## 1. System Overview
PresentMD relies on a strict set of Markdown extensions (Directives) to render complex UI components (KPIs, Alerts, Badges) without allowing the user to write raw HTML. The parser must intercept these directives and map them to semantic HTML blocks.

## 2. The Reference Theme: "Nexus Blueprint"
This is the default theme the engine must implement. It uses a high-contrast hybrid approach (Dark sidebar/headers, light content canvas) optimized for data-heavy engineering presentations.

### Design Tokens (CSS Variables required in `nexus-blueprint.css`)
The CSS must implement these exact variables. D2/Mermaid integrations must dynamically inherit `--accent-primary` and `--accent-secondary`.

* **Color Palette:**
  * `--accent-primary`: `#C8006B` (Deep Copper/Magenta - used for primary flows, active states, progress bars)
  * `--accent-secondary`: `#2563eb` (Tech Blue - used for secondary flows or comparisons)
  * `--bg-chrome`: `#1a1a2e` (Dark Iron - used for sidebar, slide title backgrounds, and table headers)
  * `--bg-canvas`: `#f7f7f8` (Off-white - main slide background for high legibility)
  * `--text-main`: `#111111` (Body text)
  * `--text-muted`: `#6b7280` (Subtitles, metadata)
* **Typography:**
  * `--font-body`: `'Segoe UI', Calibri, system-ui, sans-serif`
  * `--font-mono`: `'DM Mono', monospace` (Crucial for metrics, badges, and technical labels)

## 3. Structural Layouts (CSS Grid)
The Jinja2 templates must support these 4 base layouts. The layout is triggered either by AST inference or an explicit `::layout{name}` directive.

1. **`layout-title`**: Full-bleed dark background (`--bg-chrome`). Massive H1 centered, copper accent line.
2. **`layout-standard`**: 90% of slides. Includes a top header (Eyebrow text + H1 + Subtitle) and a flexbox body. Overflows are strictly hidden.
3. **`layout-scrollable`**: Used for Annexes. Same as standard but `overflow-y: auto` is active. Includes a "← Back" button.
4. **`layout-split-comparison`**: A strict 3-column CSS Grid (`1fr 50px 1fr`). Left side styled with `--accent-primary` tint, right side with `--accent-secondary` tint.

## 4. Markdown Custom Directives (Parser Requirements)
The AI agent MUST configure `markdown-it-py` to parse the following custom block and inline directives into their corresponding HTML components.

### A. KPI Grid Container
**Markdown Input:**
:::kpi-grid
- [55,424M] Registros {status: critical}
- [13 TB] Export estimado
- [14] Tablas
- [18 meses] Historia {status: amber}
:::

**Parser HTML Output Target:**
A CSS Grid (`grid-template-columns: repeat(4, 1fr)`) where each list item becomes a `.kpi-card`. The bracketed value uses `--font-mono` and scales up. The `{status}` injects modifier classes (e.g., `.critical` applies red text).

### B. Alert Boxes
**Markdown Input:**
:::alert{type="red" icon="⚠️"}
**FASE 1:** Data tokenizada. Requiere destokenización masiva.
:::

**Parser HTML Output Target:**
A flexbox container `.alert-box.red`. The icon is placed on the left, and the parsed Markdown content goes on the right.

### C. Progress Bars
**Markdown Input:**
:::progress-bars
- P1 · Ene-Mar: 73%
- P8 · Oct-May: 100% {color: secondary}
:::

**Parser HTML Output Target:**
Generates rows with a label and a track. The percentage dictates the `width` of the inner fill div.

### D. Inline Badges & Deep Links
**Markdown Input:**
Criticidad [ALTA]{.badge-red}. Ver detalle en [Anexo 2](#anexo-2){.link-detalle}.

**Parser HTML Output Target:**
* `[TEXT]{.badge-color}` -> `<span class="badge b-color">TEXT</span>` (Uses `--font-mono` and capsule borders).
* `[TEXT](#id){.link-detalle}` -> `<a href="#id" class="link-detalle">TEXT</a>` (Triggers JS slide navigation).

### E. Highlight Inline Mark & Background Directive
* `==TEXT==` -> `<mark class="token-highlight">TEXT</mark>` (Uses standard background highlight styling).
* `::bg-image{src="URL" opacity="0.3"}` -> `<div class="slide-bg-overlay" style="background-image: url('URL'); opacity: 0.3;"></div>` injected at the slide root.

## 5. UI Controls & Interactions
The default layout templates must support:
* **Hover Sidebar Trigger:** An 18px trigger area on the left edge of the screen reveals the TOC sidebar.
* **TOC Annex Structure:** Annex layout slides are listed in the TOC sidebar under a `── Anexos ──` header, prefixed with an `A{number}` badge.
* **Fullscreen Buttons & Shortcuts:** Bottom controls contain a `⛶` button, and the key `f`/`F` triggers native document fullscreen mode.
* **Cinematic View Transitions:** Slide changes use the browser's native `document.startViewTransition` API when available.
* **Explanation Hotspots (`:::hotspots`):** Displays numbered interactive pin markers absolutely positioned on a background image. Navigation steps focus and display custom descriptions in popup tooltip cards sequentially.
* **Magnetic Spotlight (`:::spotlight`):** Injects a radial-gradient mask dimming overlay to focus on targeted selectors with floating explanation cards.
* **Live Presenter Canvas:** A transparent canvas overlay that allows drawing freehand annotation strokes using the theme's primary color, toggled via `d`/`D` and cleared via `c`/`C`.
* **Autonomous Fit-to-Screen Auto-Scaling:** Automatically adjusts root font size between 100% and 60% if slide height exceeds 720px limit.


## 6. Diagram Engine Integration (D2 & Mermaid)
When the parser encounters a diagram code block (` ```d2 ` or ` ```mermaid `):
1. It must NOT attempt to parse it as HTML boxes.
2. It delegates the content to the `DiagramRegistry` and the corresponding `DiagramEngine` (`D2LocalEngine` or `MermaidLocalEngine`).
3. It dynamically injects theme configuration, mapping the diagram's primary connections to the `--accent-primary` specified in the frontmatter.
4. The resulting SVG is embedded directly into the HTML output within a `.diagram-container` wrapper.

## 7. Custom Themes System (Pluggable)
PresentMD supports external user-defined themes via the `ThemeManager`.
Users can place their own custom CSS files in the local configuration directory:
* **Linux/macOS:** `~/.config/presentmd/themes/<theme-name>/styles.css`
* **Windows:** `%APPDATA%\presentmd\themes\<theme-name>\styles.css`

To apply it, the user simply sets `theme: <theme-name>` in the YAML frontmatter. The `ThemeManager` will prioritize this local directory before falling back to the built-in themes.