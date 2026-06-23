"""
Tests unitarios para el parser de PresentMD.

Cubre: frontmatter, slide splitting, AST building,
directivas custom, code stepping, diagramas, y notas.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from presentmd.parser import parse_presentation
from presentmd.parser.frontmatter import extract_frontmatter
from presentmd.parser.slide_splitter import split_into_slides
from presentmd.parser.ast_builder import build_slide_ast
from presentmd.parser.models import Slide


# ──────────────────────────────────────────────
# Frontmatter Tests
# ──────────────────────────────────────────────

class TestFrontmatter:
    def test_basic_extraction(self):
        raw = dedent("""\
        ---
        title: "Test"
        theme: nexus-blueprint
        ---
        # Hello
        """)
        fm, content = extract_frontmatter(raw)
        assert fm["title"] == "Test"
        assert fm["theme"] == "nexus-blueprint"
        assert "# Hello" in content

    def test_no_frontmatter(self):
        raw = "# Just a heading\nSome content."
        fm, content = extract_frontmatter(raw)
        assert fm == {}
        assert content == raw

    def test_empty_frontmatter(self):
        raw = "---\n---\n# Content"
        fm, content = extract_frontmatter(raw)
        assert fm == {}
        assert "# Content" in content

    def test_invalid_yaml_raises(self):
        raw = "---\n[invalid: yaml: :\n---\n"
        with pytest.raises(ValueError, match="Error parseando YAML"):
            extract_frontmatter(raw)

    def test_non_dict_yaml_raises(self):
        raw = "---\n- just a list\n- of items\n---\n"
        with pytest.raises(ValueError, match="mapping YAML"):
            extract_frontmatter(raw)

    def test_complex_frontmatter(self):
        raw = dedent("""\
        ---
        title: "Presentación Compleja"
        theme: nexus-blueprint
        accent: "#C8006B"
        footer: "PresentMD v0.1"
        logo: logo.png
        ---
        # Content
        """)
        fm, _ = extract_frontmatter(raw)
        assert fm["accent"] == "#C8006B"
        assert fm["logo"] == "logo.png"


# ──────────────────────────────────────────────
# Slide Splitter Tests
# ──────────────────────────────────────────────

class TestSlideSplitter:
    def test_basic_split(self):
        content = "# Slide 1\n\n---\n\n## Slide 2\n\n---\n\n## Slide 3"
        slides = split_into_slides(content)
        assert len(slides) == 3
        assert slides[0].index == 0
        assert slides[1].index == 1
        assert slides[2].index == 2

    def test_single_slide(self):
        content = "# Only one slide"
        slides = split_into_slides(content)
        assert len(slides) == 1

    def test_empty_slides_skipped(self):
        content = "# Slide 1\n\n---\n\n---\n\n## Slide 2"
        slides = split_into_slides(content)
        assert len(slides) == 2

    def test_speaker_notes_extraction(self):
        content = dedent("""\
        ## My Slide
        Content here.

        <!-- notes -->
        Secret presenter notes.
        More notes.
        <!-- /notes -->
        """)
        slides = split_into_slides(content)
        assert len(slides) == 1
        assert slides[0].speaker_notes is not None
        assert "Secret presenter notes" in slides[0].speaker_notes
        assert "More notes" in slides[0].speaker_notes
        # Notes should be removed from raw content
        assert "<!-- notes -->" not in slides[0].raw_content

    def test_slide_without_notes(self):
        content = "## Simple slide\nJust content."
        slides = split_into_slides(content)
        assert slides[0].speaker_notes is None

    def test_speaker_notes_container_extraction(self):
        content = dedent("""\
        ## My Slide 2
        Content here.

        :::notes
        Secret presenter notes in container.
        More notes in container.
        :::
        """)
        slides = split_into_slides(content)
        assert len(slides) == 1
        assert slides[0].speaker_notes is not None
        assert "Secret presenter notes in container." in slides[0].speaker_notes
        assert "More notes in container." in slides[0].speaker_notes
        # Notes should be removed from raw content
        assert ":::notes" not in slides[0].raw_content


# ──────────────────────────────────────────────
# AST Builder Tests
# ──────────────────────────────────────────────

class TestASTBuilder:
    def test_heading_detection(self):
        slide = Slide(index=0, raw_content="# Título Principal")
        build_slide_ast(slide)
        assert len(slide.elements) >= 1
        heading = slide.elements[0]
        assert heading.type == "heading"
        assert heading.metadata["level"] == 1
        assert "Título Principal" in heading.content

    def test_paragraph_detection(self):
        slide = Slide(index=0, raw_content="Un párrafo simple.")
        build_slide_ast(slide)
        assert any(el.type == "paragraph" for el in slide.elements)

    def test_code_block_basic(self):
        slide = Slide(index=0, raw_content="```python\nprint('hello')\n```")
        build_slide_ast(slide)
        code = [el for el in slide.elements if el.type == "code_block"]
        assert len(code) == 1
        assert code[0].metadata["language"] == "python"
        assert code[0].metadata["highlight_lines"] == []

    def test_code_block_with_highlight(self):
        slide = Slide(
            index=0,
            raw_content="```sql {1, 4-5}\nSELECT *\nFROM t\nWHERE 1\nAND 2\nORDER BY 3\n```",
        )
        build_slide_ast(slide)
        code = [el for el in slide.elements if el.type == "code_block"]
        assert len(code) == 1
        assert code[0].metadata["language"] == "sql"
        assert code[0].metadata["highlight_lines"] == [1, 4, 5]

    def test_diagram_d2_is_code_block(self):
        slide = Slide(index=0, raw_content="```d2\nA -> B -> C\n```")
        build_slide_ast(slide)
        diagrams = [el for el in slide.elements if el.type == "diagram"]
        assert len(diagrams) == 0
        code_blocks = [el for el in slide.elements if el.type == "code_block"]
        assert len(code_blocks) == 1
        assert code_blocks[0].metadata["language"] == "d2"

    def test_diagram_mermaid(self):
        slide = Slide(
            index=0,
            raw_content="```mermaid\nsequenceDiagram\n    A->>B: msg\n```",
        )
        build_slide_ast(slide)
        diagrams = [el for el in slide.elements if el.type == "diagram"]
        assert len(diagrams) == 1
        assert diagrams[0].metadata["engine"] == "mermaid"

    def test_blockquote(self):
        slide = Slide(index=0, raw_content='> "Cita de impacto"')
        build_slide_ast(slide)
        bqs = [el for el in slide.elements if el.type == "blockquote"]
        assert len(bqs) == 1
        assert "Cita de impacto" in bqs[0].content

    def test_list_detection(self):
        slide = Slide(
            index=0,
            raw_content="- Primero\n- Segundo\n- Tercero",
        )
        build_slide_ast(slide)
        lists = [el for el in slide.elements if el.type == "list"]
        assert len(lists) == 1
        assert lists[0].metadata["list_type"] == "unordered"
        assert len(lists[0].metadata["items"]) == 3

    def test_layout_directive(self):
        slide = Slide(
            index=0,
            raw_content="::layout{split-comparison}\n\n## Título",
        )
        build_slide_ast(slide)
        assert slide.layout == "split-comparison"
        # The directive should not appear in elements
        assert not any(el.type == "directive_layout" for el in slide.elements)

    def test_container_kpi_grid(self):
        raw = dedent("""\
        :::kpi-grid
        - [55,424M] Registros {status: critical}
        - [13 TB] Export estimado
        :::
        """)
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        kpis = [el for el in slide.elements if el.type == "container_kpi-grid"]
        assert len(kpis) == 1
        items = kpis[0].metadata.get("items", [])
        assert len(items) == 2
        assert items[0]["value"] == "55,424M"
        assert items[0]["label"] == "Registros"
        assert items[0]["status"] == "critical"
        assert items[1]["status"] is None

    def test_container_alert(self):
        raw = dedent("""\
        :::alert{type="red" icon="⚠️"}
        **FASE 1:** Texto de alerta.
        :::
        """)
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        alerts = [el for el in slide.elements if el.type == "container_alert"]
        assert len(alerts) == 1
        assert alerts[0].metadata["attrs"]["type"] == "red"
        assert alerts[0].metadata["attrs"]["icon"] == "⚠️"

    def test_container_progress_bars(self):
        raw = dedent("""\
        :::progress-bars
        - P1 · Ene-Mar: 73%
        - P8 · Oct-May: 100% {color: secondary}
        :::
        """)
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        pbs = [el for el in slide.elements if el.type == "container_progress-bars"]
        assert len(pbs) == 1
        items = pbs[0].metadata.get("items", [])
        assert len(items) == 2
        assert items[0]["label"] == "P1 · Ene-Mar"
        assert items[0]["percentage"] == 73
        assert items[0]["color"] == "primary"
        assert items[1]["percentage"] == 100
        assert items[1]["color"] == "secondary"

    def test_table_parsing(self):
        raw = dedent("""\
        | Campo | Tipo | Nullable |
        |---|---|---|
        | rut | VARCHAR(12) | NO |
        | monto | DECIMAL(18,2) | SÍ |
        """)
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        tables = [el for el in slide.elements if el.type == "table"]
        assert len(tables) == 1
        meta = tables[0].metadata
        assert meta["headers"] == ["Campo", "Tipo", "Nullable"]
        assert len(meta["rows"]) == 2
        assert meta["rows"][0] == ["rut", "VARCHAR(12)", "NO"]
        assert meta["rows"][1] == ["monto", "DECIMAL(18,2)", "SÍ"]

    def test_heading_anchor_parsing(self):
        raw = "## Anexo de Costos {#anexo-costos}"
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        headings = [el for el in slide.elements if el.type == "heading"]
        assert len(headings) == 1
        assert headings[0].content == "Anexo de Costos"
        assert headings[0].metadata.get("anchor_id") == "anexo-costos"

    def test_annex_layout_parsing(self):
        raw = "::layout{annex}\n\n# Título del Anexo"
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        assert slide.layout == "annex"

    def test_mark_highlight_inline(self):
        # We can check that our render_inline_markdown converts ==text== to <mark class="token-highlight">text</mark>
        from presentmd.render.html_builder import render_inline_markdown
        text = "Texto con ==resaltado especial== en el párrafo."
        rendered = render_inline_markdown(text)
        assert '<mark class="token-highlight">resaltado especial</mark>' in rendered

    def test_animated_counter_inline_parsing(self):
        from presentmd.render.html_builder import render_inline_markdown
        text = "Eficiencia de [[+9000]]{.animated-counter suffix=\"%\"}"
        rendered = render_inline_markdown(text)
        assert 'class="animated-counter"' in rendered
        assert 'data-target="9000"' in rendered
        assert 'suffix="%"' in rendered
        assert '+9000' in rendered

    def test_bg_image_directive(self):
        raw = '::bg-image{src="background.jpg" opacity="0.3"}\n\n# Título'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        assert slide.bg_image == {"src": "background.jpg", "opacity": "0.3"}
        assert not any(el.type == "directive_bg_image" for el in slide.elements)

    def test_steps_container_parsing(self):
        raw = ":::steps\n- Paso A\n- Paso B\n:::"
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        steps_el = [el for el in slide.elements if el.type == "container_steps"]
        assert len(steps_el) == 1
        assert steps_el[0].metadata.get("items") == ["Paso A", "Paso B"]

    def test_layer_stack_container_parsing(self):
        raw = ":::layer-stack\n![Base](base.png)\n![Overlay](overlay.png)\n:::"
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        stack_el = [el for el in slide.elements if el.type == "container_layer-stack"]
        assert len(stack_el) == 1
        images = stack_el[0].metadata.get("images")
        assert len(images) == 2
        assert images[0] == {"alt": "Base", "src": "base.png"}
        assert images[1] == {"alt": "Overlay", "src": "overlay.png"}

    def test_code_stepping_parsing(self):
        raw = "```python {1|2-3|all}\nprint('hi')\nprint('two')\nprint('three')\n```"
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        code_el = [el for el in slide.elements if el.type == "code_block"]
        assert len(code_el) == 1
        metadata = code_el[0].metadata
        assert metadata.get("code_steps") == [[1], [2, 3], []]
    def test_hotspots_container_parsing(self):
        raw = ':::hotspots{image="base.png"}\n- [20%, 30%] Pin A\n- [50, 60] Pin B\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        hotspots_el = [el for el in slide.elements if el.type == "container_hotspots"]
        assert len(hotspots_el) == 1
        assert hotspots_el[0].metadata.get("image") == "base.png"
        pins = hotspots_el[0].metadata.get("pins")
        assert len(pins) == 2
        assert pins[0] == {"x": "20%", "y": "30%", "content": "Pin A"}
        assert pins[1] == {"x": "50%", "y": "60%", "content": "Pin B"}

    def test_spotlight_container_parsing(self):
        raw = ':::spotlight\n- [#target] Foco A\n- [.target-class] Foco B\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        spotlight_el = [el for el in slide.elements if el.type == "container_spotlight"]
        assert len(spotlight_el) == 1
        steps = spotlight_el[0].metadata.get("steps")
        assert len(steps) == 2
        assert steps[0] == {"selector_or_label": "#target", "content": "Foco A", "options": {}}
        assert steps[1] == {"selector_or_label": ".target-class", "content": "Foco B", "options": {}}

    def test_process_flow_container_parsing(self):
        raw = ':::process-flow\n- [Paso A] Descripcion A {icon: "💻", color: "secondary"}\n- [Paso B] {color: "success"}\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        el = [e for e in slide.elements if e.type == "container_process-flow"]
        assert len(el) == 1
        items = el[0].metadata.get("items")
        assert len(items) == 2
        assert items[0] == {"label": "Paso A", "desc": "Descripcion A", "icon": "💻", "color": "secondary"}
        assert items[1] == {"label": "Paso B", "desc": "", "icon": "", "color": "success"}

    def test_pyramid_container_parsing(self):
        raw = ':::pyramid\n- [Nivel A] Desc A {color: "primary"}\n- [Nivel B] {color: "danger"}\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        el = [e for e in slide.elements if e.type == "container_pyramid"]
        assert len(el) == 1
        items = el[0].metadata.get("items")
        assert len(items) == 2
        assert items[0] == {"label": "Nivel A", "desc": "Desc A", "color": "primary"}
        assert items[1] == {"label": "Nivel B", "desc": "", "color": "danger"}

    def test_bar_chart_parsing(self):
        raw = ':::bar-chart{title="Progreso"}\n- [Hito A] Desc A {color: "primary"}\n- [Hito B] Desc B {color: "secondary"}\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        el = [e for e in slide.elements if e.type == "container_bar-chart"]
        assert len(el) == 1
        assert el[0].metadata["attrs"]["title"] == "Progreso"
        items = el[0].metadata.get("items")
        assert len(items) == 2
        assert items[0] == {"label": "Hito A", "desc": "Desc A", "color": "primary"}

    def test_chart_parsing(self):
        raw = ':::chart{type="line" title="Ventas"}\nlabels: ["Ene", "Feb"]\ndata: [10, 20]\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        el = [e for e in slide.elements if e.type == "container_chart"]
        assert len(el) == 1
        assert el[0].metadata["attrs"]["type"] == "line"
        assert el[0].metadata["attrs"]["title"] == "Ventas"
        assert el[0].metadata.get("labels") == ["Ene", "Feb"]
        assert el[0].metadata.get("data") == [10, 20]

    def test_tabs_parsing(self):
        raw = ':::tabs\n=== Tab 1 ===\nContenido 1\n=== Tab 2 ===\nContenido 2\n:::'
        slide = Slide(index=0, raw_content=raw)
        build_slide_ast(slide)
        el = [e for e in slide.elements if e.type == "container_tabs"]
        assert len(el) == 1
        tabs = el[0].metadata.get("tabs")
        assert len(tabs) == 2
        assert tabs[0]["title"] == "Tab 1"
        assert tabs[0]["content"] == "Contenido 1"
        assert tabs[1]["title"] == "Tab 2"
        assert tabs[1]["content"] == "Contenido 2"




# ──────────────────────────────────────────────
# Integration Test (parse_presentation on test.md)
# ──────────────────────────────────────────────

class TestIntegration:
    @pytest.fixture
    def test_md_path(self) -> Path:
        p = Path(__file__).parent / "test_data.md"
        if not p.exists():
            pytest.skip("test_data.md not found inside tests directory")
        return p

    def test_full_parse(self, test_md_path: Path):
        pres = parse_presentation(test_md_path)

        # Frontmatter
        assert pres.frontmatter["title"] == "Demo Completa PresentMD"
        assert pres.frontmatter["theme"] == "nexus-blueprint"
        assert pres.frontmatter["accent"] == "#C8006B"

        # Multiple slides
        assert pres.slide_count >= 8

        # Check variety of element types across all slides
        all_types = set()
        for slide in pres.slides:
            for el in slide.elements:
                all_types.add(el.type)

        assert "heading" in all_types
        assert "code_block" in all_types
        assert "diagram" in all_types

    def test_speaker_notes_in_last_slide(self, test_md_path: Path):
        pres = parse_presentation(test_md_path)
        # Find the slide with speaker notes
        slides_with_notes = [s for s in pres.slides if s.speaker_notes is not None]
        assert len(slides_with_notes) > 0
        assert any("SLA" in s.speaker_notes for s in slides_with_notes)
