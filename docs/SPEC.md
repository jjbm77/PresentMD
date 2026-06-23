# SPEC.md — PresentMD Core Architecture & Implementation Plan
**Version:** 1.0
**Target Framework:** Python 3.12+ CLI Application
**Methodology:** Spec-Driven Development (SDD)

## 1. System Overview
PresentMD is a highly specialized Static Site Generator (SSG) packaged as a Command Line Interface (CLI) tool. It transforms enriched Markdown files (with YAML frontmatter) into pixel-perfect, interactive HTML presentations and high-resolution PDFs. It is designed specifically for software architecture, database modeling, and complex technical presentations.

## 2. Hard Constraints (STRICTLY ENFORCED)
The AI agent MUST adhere to the following rules without exception. Failure to do so will result in a rejected build:
* **NO JavaScript Frameworks:** The use of Node.js, React, Vue, Svelte, or any heavy frontend framework is strictly forbidden. The generated frontend must rely solely on Vanilla JS and CSS Grid/Custom Properties (Variables).
* **Python Only for Backend:** All parsing, building, and CLI logic must be written in Python 3.12+. 
* **Target Environment OS:** The resulting CLI must run flawlessly on modern Linux distributions (specifically tested against Pop!_OS 24.04 and Fedora), as well as macOS and Windows.
* **NO Custom Diagram Syntaxes:** Do not attempt to write a custom parser for diagrams. Rely exclusively on existing D2 and Mermaid CLI/libraries.
* **Self-Contained Output:** The default HTML output must be a single file or a clean directory with local assets. Base64 encoding for images is preferred for single-file exports.
* **Idempotent Builds:** Running the `build` command multiple times on the same `.md` file must produce the exact same output without side effects.

## 3. Fixed Technology Stack
Do not substitute these libraries unless explicitly authorized by the human user:
* **CLI Engine:** `typer` (for command routing) + `rich` (for beautiful terminal UI, progress bars, and error formatting).
* **Markdown Parser:** `markdown-it-py` (crucial for AST generation and plugin support).
* **Frontmatter:** `PyYAML`.
* **Templating:** `Jinja2` (for rendering the AST into HTML layouts).
* **Code Highlighting:** `pygments` or equivalent Python-based pre-processor to avoid heavy client-side JS. It MUST support step-by-step line highlighting logic.
* **PDF Engine:** `playwright` (Python sync API) to print the HTML to PDF.

## 4. Target Directory Structure
The codebase must be structured as follows:

    presentmd/
    ├── src/
    │   ├── presentmd/
    │   │   ├── __init__.py
    │   │   ├── cli/             # Typer command definitions (main, build, serve)
    │   │   ├── parser/          # markdown-it-py extensions and AST logic
    │   │   ├── plugins/         # Extensible component plugin registry
    │   │   ├── render/          # Jinja2 rendering pipeline, layout inference, and theme/diagram managers
    │   │   ├── templates/       # HTML/CSS base layouts and the built-in themes
    │   │   └── export/          # Playwright PDF logic and Base64 packager
    ├── tests/
    ├── pyproject.toml           # Dependency and package management
    └── SPEC.md
    └── REQUIREMENTS.MD

---

## 5. Implementation Milestones & Acceptance Criteria

The AI agent must complete these milestones sequentially. Do not proceed to the next milestone until the current one is tested and verified.

### Milestone 1: CLI Skeleton & Setup
* **Objective:** Initialize the project structure, `pyproject.toml`, and the basic Typer CLI.
* **Acceptance Criteria:**
  1. Running `python -m src.presentmd --help` displays a Rich-formatted help menu.
  2. The CLI exposes two commands: `build [FILE]` and `serve [FILE]`.
  3. Commands currently print a dummy Rich panel acknowledging the file path.

### Milestone 2: Parser Core & AST Generation
* **Objective:** Read a Markdown file, extract the YAML frontmatter, and split the document into an array of slide objects using `markdown-it-py`.
* **Acceptance Criteria:**
  1. The parser correctly identifies `---` as slide separators.
  2. The parser extracts the YAML frontmatter into a Python dictionary.
  3. The parser successfully builds an AST for each slide (identifying explicit directives like `::layout{split-50-50}`, H1s, code blocks, and paragraphs).
  4. **Test Case:** Create `test.md`. Running a debug command prints the structured AST and parsed frontmatter to the terminal.

### Milestone 3: Semantic Layout Inference & HTML Rendering
* **Objective:** Map the parsed AST to specific Jinja2 layouts and apply CSS variables based on the selected theme.
* **Acceptance Criteria:**
  1. The engine wraps the content in the layout specified by the directive. If no directive exists, it infers the layout gracefully.
  2. Running `presentmd build test.md` generates an `index.html`.
  3. Opening `index.html` shows the slides with correct Vanilla CSS styling based on the theme specified in the YAML.

### Milestone 4: Diagram & Code Stepping Integration
* **Objective:** Intercept D2/Mermaid blocks and code blocks for advanced rendering.
* **Acceptance Criteria:**
  1. D2 code blocks are processed by the D2 engine and injected as SVGs into the HTML. 
  2. The SVGs automatically inherit the colors of the active theme.
  3. Code blocks support highlight annotations (e.g., `{1, 4-5}`). 
  4. **Stress Test Requirement:** The `test.md` file must include a complex D2 diagram (e.g., illustrating a global transaction sweep across an entire RUT, like a "Ciclo Ancla") and a multi-line code block (e.g., a Snowflake data model or FastAPI route) to verify rendering density and line-stepping functionality.

### Milestone 5: The Hot-Reload Server (Serve Command)
* **Objective:** Implement the `serve` command to provide Live Preview.
* **Acceptance Criteria:**
  1. Running `presentmd serve test.md` starts a lightweight HTTP server.
  2. Modifying and saving `test.md` triggers an automatic rebuild and pushes a refresh to the browser without full reload flash (e.g., via simple WebSockets or Server-Sent Events).
  3. The browser maintains the current slide view/index after reload.

### Milestone 6: PDF Export Engine
* **Objective:** Implement the PDF printing functionality using Playwright.
* **Acceptance Criteria:**
  1. Running `presentmd build test.md --format pdf` triggers a headless browser.
  2. The system outputs a high-resolution `presentation.pdf`.
  3. The PDF respects `@media print` CSS rules, ensuring no diagrams are cut in half and slide dimensions are perfectly constrained to presentation ratios.

### Milestone 7: Advanced Presentation Interactions & Layered Components (Phase A)
* **Objective:** Implement collapsible hover sidebar, fullscreen toggles, natural text highlighting, speaker notes containers, background images with overlays, and cinematic view transitions.
* **Acceptance Criteria:**
  1. Sidebar menu slides in on hover over an 18px trigger area on the left edge.
  2. Index headers ("── Anexos ──") and annex indicators ("A1", "A2"...) are displayed in the sidebar menu.
  3. A fullscreen floating button `⛶` and keyboard shortcut `f`/`F` toggle native fullscreen presentation mode.
  4. Natural text highlight via `==texto==` renders as `<mark class="token-highlight">`.
  5. Immersive slide background images via `::bg-image` parse custom opacity overlays.
  6. Speaker notes containers `:::notes` extract note text and serialize it in `data-notes`.
  7. Cinematic view transitions animate slide changes using `document.startViewTransition`.

### Milestone 8: Interactive Presentation Flows & Step-by-Step Navigation (Phase B)
* **Objective:** Implement sequential steps lists, image layers stacks, and magic code transition highlights via a unified JS stepping system.
* **Acceptance Criteria:**
  1. **Steps List (`:::steps`):** Markdown lists in a `:::steps` container are parsed into a `<ul class="steps-list">` with `li` items initially hidden (`.step-hidden`). Navigation forward reveals elements sequentially before changing the slide; navigation backward hides them sequentially.
  2. **Layer Stack (`:::layer-stack`):** Images in a `:::layer-stack` container are absolutely stacked. SUCCESSIVE navigation clicks/keystrokes trigger a fade-in opacity transition to reveal the next layer (from index 1 to N) while preceding layers remain visible.
  3. **Code Stepping Transitions:** Fenced code blocks with step definitions (e.g. `{1|2-3|all}`) parse the pipe-separated steps and serialize them to JSON format in `data-code-steps` on `.code-container.stepping`. The JS manager steps through these highlighted lines, dimming other lines to `0.3` opacity and highlighting active line groups.
  4. **Click-to-Advance Bindings:** Clicks on `.code-container.stepping`, `.steps-list`, and `.layer-stack` containers propagate to the navigation flow, triggering the next step reveal.

### Milestone 9: Advanced Presentation Interactions & Live Presenter Tools (Phase C)
* **Objective:** Implement interactive pin hotspots, spatial spotlight step sequences, live presentation drawing overlay tools, and container overflow auto-scaling.
* **Acceptance Criteria:**
  1. **Explanation Hotspots (`:::hotspots`):** Parses hotspots container with an `image` attribute and a list of pin markers. Pins are absolutely positioned using coordinates (e.g. `[25%, 35%]`). Click on pin marker toggles its popup explanation. Hotspots step through sequentially during presenter navigation.
  2. **Magnetic Spotlight (`:::spotlight`):** Parses spotlight steps mapping selectors to custom descriptions. Stepping through slide triggers spotlight mask centered on targeted selector with floating card explanation.
  3. **Live Presenter Tools (Drawing & Laser Pointer):** Drawing canvas overlay captures mouse/touch events when active. Keyboard shortcuts (`d`/`D` to toggle drawing, `c`/`C` to clear canvas) and toolbar buttons (`✏️`, `🧹`) control drawings.
  4. **Autonomous Fit-to-Screen Auto-Scaling:** Auto-scaling algorithm runs on slide load/resize. If a slide's scrollHeight exceeds 720px, it dynamically shrinks the root font-size down (to 60% minimum) to ensure contents fit perfectly within 720px internal dimensions without scrollbars or vertical layout breaks.