# LAYOUTS_SPEC.md — PresentMD v1.0 Layout System
**Target:** Jinja2 Templates & Vanilla CSS (CSS Grid / Flexbox)
**Dependency:** Must conform strictly to `THEMES_SPEC.md` and wrap `OBJECTS_SPEC.md`.

## 1. Core Philosophy
Layouts act as the master containers for each slide. They are strictly structural and dictate how content flows. 
* **Assignment:** The layout is assigned either automatically by AST inference (e.g., an isolated H1 triggers a title slide) or explicitly via a Markdown directive `::layout{name}` directly after the slide separator `---`.
* **Constraint:** Layouts must never use absolute positioning for content. They rely entirely on CSS Grid and Flexbox to ensure perfect scaling across 1080p, 4K, and PDF exports.

---

## 2. Layout Definitions

### A. Title Cover (`layout-title`)
* **Trigger:** `::layout{title}` or inferred when the slide contains ONLY an `H1` and optionally an `H2` / `Eyebrow` text.
* **Functionality:** Used for presentation covers or major section breaks. It demands maximum attention.
* **Technical Output:**
  * **Background:** Uses `--bg-chrome` (dark theme).
  * **Structure:** Flexbox column, `justify-content: center`. 
  * **Typography:** `H1` is scaled to massive proportions (`clamp` function for responsiveness).
  * **Accents:** Must include a vertical or horizontal accent line using `--accent-primary` (e.g., Copper).

### B. Standard Content (`layout-standard`)
* **Trigger:** Default layout for any slide without an explicit directive.
* **Functionality:** The workhorse layout for 90% of the presentation. Designed to hold KPIs, text, code blocks, or D2 diagrams without breaking.
* **Technical Output:**
  * **Structure:** CSS Flexbox column.
    * **Header Zone (`.slide-header`):** Fixed height. Contains Eyebrow (metadata), H1, and Subtitle.
    * **Body Zone (`.slide-body`):** `flex: 1`, `display: flex`, `align-items: center`. 
  * **Constraint:** Strictly `overflow: hidden`. Content must auto-scale or fit. If content exceeds the box, the engine should warn in the CLI build log.

### C. Scrollable Detail (`layout-scrollable`)
* **Trigger:** `::layout{scrollable}`
* **Functionality:** Used for deep-dive tables or heavy documentation. Allows scrolling during Q&A.
* **Technical Output:**
  * **Structure:** Same as `layout-standard` but with `overflow-y: auto` in `.slide-body`.
  * **Components:** Injects a `<button class="btn-volver">← Volver</button>` interfacing with JS history.

### D. Split Comparison (`layout-split-comparison`)
* **Trigger:** `::layout{split-comparison}`
* **Functionality:** Divides the slide into two competing columns (Legacy vs. Target, Productive vs. Shadow) with a central separator. 
* **Technical Output:**
  * **Structure:** Strict CSS Grid: `grid-template-columns: 1fr 50px 1fr;`
  * **Left Column:** Subtle background tint of `--accent-primary` (rgba) and a border.
  * **Center Column:** Vertical divider containing a badge or an icon.
  * **Right Column:** Subtle background tint of `--accent-secondary` (rgba) and a border.

### E. Annex Layout (`layout-annex`)
* **Trigger:** `::layout{annex}`
* **Functionality:** Slide of annex. Excluded from the normal chronological pagination and sequential navigation keys. Access is done via `.link-anexo` deep links.
* **Technical Output:** Injects a `data-annex="true"` attribute at the slide root and is separated in the TOC menu.

## 3. Background Overlays
Every layout must render a `.slide-bg-overlay` element at the root of the slide:
* **HTML Markup:** `<div class="slide-bg-overlay" style="background-image: url('...'); opacity: ...;"></div>`
* **CSS Rules:** Positioned absolutely, filling 100% width and height of the slide, and positioned behind all content (`z-index: 1`).

---

## 4. Interactive Components & Stepping
Layouts support inline step-by-step interactive behaviors that intercept presentation navigation before shifting to the next/previous slide.

### A. Steps Container (`:::steps`)
* **Styling:** Rendered as `<ul class="steps-list">` with list items marked with `.step-hidden` class (opacity: 0, height/transform transition).
* **Behavior:** Successive "next" actions reveal the items sequentially by applying `.step-visible`.

### B. Layer Stack Container (`:::layer-stack`)
* **Styling:** Rendered as `<div class="layer-stack">` containing one or more `<img class="layer-image">` tags.
* **Layout:** Images are positioned absolutely (`top: 0`, `left: 0`, `width: 100%`, `height: 100%`) stacked on top of each other.
* **Behavior:** First image is `.active` (fully visible). Successive clicks trigger fade-in transitions (`opacity: 1`) on the subsequent layers.

### C. Stepping Code Blocks
* **Styling:** Rendered inside a `.code-container.stepping` element. Lines are styled as `.code-line`.
* **Behavior:** Uses a dimming layer where non-active lines get `opacity: 0.3` and active step line numbers get `.highlight-active`.

### D. Explanation Hotspots (`:::hotspots`)
* **Styling:** Rendered as `<div class="hotspots-container">` containing a background image and a overlay layer of absolutely positioned pin markers (`.hotspot-pin`).
* **Behavior:** Clicking a pin toggles `.active` class to reveal its hover/popup tooltip card (`.pin-tooltip`). Successive navigation actions highlight pins one by one in sequence.

### E. Magnetic Spotlight (`:::spotlight`)
* **Styling:** Injects a global fixed overlay (`#spotlightOverlay`) and description card (`#spotlightTooltip`).
* **Behavior:** Uses a CSS radial-gradient mask centering on the targeted element using viewport coordinates. Displays the step's explanation text in the floating card positioned relative to the highlighted element.

### F. Live Presenter Canvas (Drawing & Laser)
* **Styling:** A fixed canvas element (`#drawingCanvas`) covers the screen.
* **Behavior:** Presenter drawing mode (`d`/`D`) captures draw strokes on the canvas with smooth paths using the theme's primary color. Laser pointer (`l`/`L`) tracks a circular red glow next to the mouse.

### G. Autonomous Fit-to-Screen Scaling
* **Styling:** Dynamically recalculates root `html` font-size during transitions and window resizes.
* **Behavior:** Decrements root font-size dynamically if the slide's height (`scrollHeight`) exceeds the boundary of 720px, compressing the layout down to a minimum of 60% relative size.