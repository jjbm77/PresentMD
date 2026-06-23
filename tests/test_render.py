"""
Tests unitarios e integrados para el motor de renderizado HTML de PresentMD (Milestone 3).
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
import pytest

from presentmd.parser import parse_presentation
from presentmd.parser.models import Presentation, Slide, SlideElement
from presentmd.render.layout_inference import infer_layout
from presentmd.render.code_highlighter import highlight_code
from presentmd.render.engine import render_presentation


# ──────────────────────────────────────────────
# Layout Inference Tests
# ──────────────────────────────────────────────

class TestLayoutInference:
    def test_inferred_as_title(self):
        # Un slide que tiene sólo H1 es portada
        slide = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Mi Presentación", metadata={"level": 1})
            ]
        )
        assert infer_layout(slide) == "title"

    def test_inferred_as_title_with_subtitle(self):
        # H1 + párrafo corto = portada
        slide = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Mi Presentación", metadata={"level": 1}),
                SlideElement(type="paragraph", content="Subtítulo corto o autor")
            ]
        )
        assert infer_layout(slide) == "title"

    def test_inferred_as_scrollable(self):
        # Slide con tabla y contenido largo = scrollable
        slide = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Anexo largo", metadata={"level": 2}),
                SlideElement(type="table", content="col1|col2\n---|---\nx|y" * 100, metadata={})
            ]
        )
        assert infer_layout(slide) == "scrollable"

    def test_inferred_as_standard_by_default(self):
        # Un slide normal con lista
        slide = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Slide Normal", metadata={"level": 2}),
                SlideElement(type="list", content="- Item 1\n- Item 2", metadata={"items": ["Item 1", "Item 2"]})
            ]
        )
        assert infer_layout(slide) == "standard"

    def test_explicit_layout_preserved(self):
        # Si ya tiene layout asignado de manera explícita por directiva, se respeta
        slide = Slide(
            index=0,
            raw_content="",
            layout="split-comparison",
            elements=[
                SlideElement(type="heading", content="Comparativa", metadata={"level": 2})
            ]
        )
        assert infer_layout(slide) == "split-comparison"


# ──────────────────────────────────────────────
# Code Highlighter Tests
# ──────────────────────────────────────────────

class TestCodeHighlighter:
    def test_highlight_code_basic(self):
        code = "print('hola')"
        html = highlight_code(code, "python")
        assert "code-container" in html
        assert "print" in html
        assert "stepping" not in html

    def test_highlight_code_with_stepping(self):
        code = "line 1\nline 2\nline 3"
        html = highlight_code(code, "python", highlight_lines=[2])
        assert "code-container" in html
        assert "stepping" in html
        assert 'data-line="2"' in html
        assert "highlight-active" in html


# ──────────────────────────────────────────────
# Render Presentation Tests
# ──────────────────────────────────────────────

class TestRenderPresentation:
    def test_render_integration(self):
        # Crear una presentación mínima en memoria
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Portada", metadata={"level": 1})
            ]
        )
        slide2 = Slide(
            index=1,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Contenido Principal", metadata={"level": 2}),
                SlideElement(
                    type="container_kpi-grid",
                    content="",
                    metadata={"items": [{"value": "100", "label": "Métrica", "status": "critical"}]}
                )
            ]
        )
        
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Integration", "theme": "nexus-blueprint", "accent": "#ff0000"},
            slides=[slide1, slide2]
        )
        
        html = render_presentation(pres)
        
        # Debe contener elementos clave de base.html.j2 y nexus-blueprint.css
        assert "<!DOCTYPE html>" in html
        assert "Test Integration" in html
        assert "--accent-primary: #ff0000" in html
        assert "DM Mono" in html  # Debe tener la tipografía embebida
        assert "toc-sidebar" in html
        
        # Deben estar ambos slides en HTML
        assert "layout-title" in html
        assert "layout-standard" in html
        
        # Deben estar los componentes mapeados
        assert "kpi-grid" in html
        assert "kpi-card critical" in html

    def test_render_table(self):
        el = SlideElement(
            type="table",
            metadata={
                "headers": ["Campo", "Tipo"],
                "rows": [["rut", "VARCHAR(12)"]]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<table class="styled-table">' in html
        assert '<th>Campo</th>' in html
        assert '<td>rut</td>' in html

    def test_inferred_as_scrollable_table_rows(self):
        # Slide con tabla de más de 5 filas debe inferirse como scrollable
        slide = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Tabla de Datos", metadata={"level": 2}),
                SlideElement(
                    type="table",
                    content="",
                    metadata={
                        "headers": ["A", "B"],
                        "rows": [["1", "2"]] * 6
                    }
                )
            ]
        )
        assert infer_layout(slide) == "scrollable"

    def test_render_diagram_fallback(self):
        el = SlideElement(
            type="diagram",
            content="block1 -> block2",
            metadata={"engine": "d2"}
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert "diagram-container fallback" in html
        assert "block1 -&gt; block2" in html
        assert "D2" in html

    def test_render_diagram_inline(self):
        el = SlideElement(
            type="diagram",
            content="block1 -> block2",
            metadata={"engine": "d2", "svg_content": "<svg id='test-svg'></svg>"}
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="diagram-container"><svg id=\'test-svg\'></svg></div>' in html

    def test_toc_includes_annex_labeled(self):
        from presentmd.render.toc_builder import build_toc
        
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[SlideElement(type="heading", content="Portada", metadata={"level": 1})]
        )
        slide_annex = Slide(
            index=1,
            raw_content="",
            layout="annex",
            elements=[SlideElement(type="heading", content="Anexo Costos", metadata={"level": 2})]
        )
        slide2 = Slide(
            index=2,
            raw_content="",
            elements=[SlideElement(type="heading", content="Final", metadata={"level": 2})]
        )
        
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test TOC"},
            slides=[slide1, slide_annex, slide2]
        )
        
        toc = build_toc(pres)
        # Should contain Portada (index 0), Anexo Costos (index 1), and Final (index 2)
        indices = [item["index"] for item in toc]
        assert 0 in indices
        assert 1 in indices
        assert 2 in indices
        
        # Verify the annex labels
        annex_items = [item for item in toc if item["is_annex"]]
        assert len(annex_items) == 1
        assert annex_items[0]["annex_label"] == "A1"
        assert annex_items[0]["title"] == "Anexo Costos"

    def test_render_annex_slide(self):
        # Verify an annex layout slide renders with data-annex="true", the annex class, and the btn-volver
        slide1 = Slide(
            index=0,
            raw_content="",
            layout="annex",
            elements=[
                SlideElement(type="heading", content="Anexo Costos", metadata={"level": 2})
            ]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Annex Render", "theme": "nexus-blueprint", "nav_arrows": True, "slide_number": True},
            slides=[slide1]
        )
        
        html = render_presentation(pres)
        
        # Check layout-scrollable with annex class
        assert "layout-scrollable" in html
        assert "annex" in html
        assert 'data-annex="true"' in html
        assert 'class="btn-volver"' in html
        
        # Check that normal scrollable layout (not annex) does NOT render the back button
        slide2 = Slide(
            index=0,
            raw_content="",
            layout="scrollable",
            elements=[
                SlideElement(type="heading", content="Scrollable Normal", metadata={"level": 2})
            ]
        )
        pres2 = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Scrollable Render", "theme": "nexus-blueprint", "nav_arrows": True, "slide_number": True},
            slides=[slide2]
        )
        html2 = render_presentation(pres2)
        assert 'class="btn-volver"' not in html2

    def test_render_closing_slide_custom(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[SlideElement(type="heading", content="Portada", metadata={"level": 1})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={
                "title": "Test Closing Custom",
                "closing_message": "¡Muchas Gracias!",
                "closing_subtitle": "¿Preguntas?"
            },
            slides=[slide1]
        )
        html = render_presentation(pres)
        assert "¡Muchas Gracias!" in html
        assert "¿Preguntas?" in html
        # Should have 2 slides: Portada + Closing
        assert 'id="closing"' in html
        assert 'data-index="1"' in html

    def test_render_closing_slide_default_replicates_cover(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(type="heading", content="Mi Increíble Portada", metadata={"level": 1}),
                SlideElement(type="paragraph", content="Autor: Jaime")
            ]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={
                "title": "Mi Increíble Portada"
            },
            slides=[slide1]
        )
        html = render_presentation(pres)
        # Should contain "Mi Increíble Portada" twice: cover and closing slide
        assert html.count("Mi Increíble Portada") >= 2
        # And "Autor: Jaime" on both cover and closing slide
        assert html.count("Autor: Jaime") >= 2

    def test_live_reload_script_injected(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[SlideElement(type="heading", content="Portada", metadata={"level": 1})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Live Reload"},
            slides=[slide1]
        )
        # Without live_reload
        html_normal = render_presentation(pres, live_reload=False)
        assert "Live Reload via Server-Sent Events" not in html_normal

        # With live_reload
        html_live = render_presentation(pres, live_reload=True)
        assert "Live Reload via Server-Sent Events" in html_live
        assert "new EventSource('/events')" in html_live

    def test_info_grid_markdown_rendering(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[
                SlideElement(
                    type="container_info-grid",
                    content="",
                    metadata={
                        "items": [
                            {"label": "Label **bold**", "value": "Value with [link](#dest){.class}"}
                        ]
                    }
                )
            ]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Info Grid"},
            slides=[slide1]
        )
        html = render_presentation(pres)
        assert "<strong>bold</strong>" in html
        assert 'href="#dest"' in html
        assert 'class="class"' in html

    def test_link_sanitization(self):
        from presentmd.render.html_builder import render_inline_markdown
        # Safe link should render correctly
        html_safe = render_inline_markdown("[Click](#dest){.class}")
        assert 'href="#dest"' in html_safe
        assert 'class="class"' in html_safe
        
        # Dangerous protocol should be sanitized to #
        html_danger_js = render_inline_markdown("[Click](javascript:alert(1)){.class}")
        assert 'href="#"' in html_danger_js
        
        html_danger_data = render_inline_markdown("[Click](data:text/html;base64,NDI=){.class}")
        assert 'href="#"' in html_danger_data

        # Disallowed event handler attributes should be filtered
        html_attr_injection = render_inline_markdown("[Click](#dest){onclick=alert(1) class=btn}")
        assert 'onclick' not in html_attr_injection
        assert 'class="btn"' in html_attr_injection

    def test_timeline_rendering(self):
        el = SlideElement(
            type="container_timeline",
            content="",
            metadata={
                "phases": [
                    {
                        "badge": "Hito 1",
                        "title": "Inicio",
                        "items": ["Item A", "Item B"],
                        "deliverable": "Entregable 1"
                    },
                    {
                        "badge": "Hito 2",
                        "title": "Fin",
                        "items": ["Item C"],
                        "deliverable": "Entregable 2"
                    }
                ]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="timeline">' in html
        assert '<div class="timeline-phase">' in html
        assert '<span class="tl-badge">Hito 1</span>' in html
        assert '<div class="tl-title">Inicio</div>' in html
        assert '<div class="tl-desc">• Item A</div>' in html
        assert '<div class="tl-desc">• Item B</div>' in html
        assert '<div class="tl-deliverable">→ Entregable 1</div>' in html
        assert '<div class="timeline-arrow">→</div>' in html
        assert '<span class="tl-badge">Hito 2</span>' in html

    def test_parallel_compare_rendering(self):
        el = SlideElement(
            type="container_parallel-compare",
            content="",
            metadata={
                "columns": [
                    {
                        "header": "Columna Izquierda",
                        "items": ["Punto L1", "Punto L2"]
                    },
                    {
                        "header": "Columna Derecha",
                        "items": ["Punto R1"]
                    }
                ],
                "attrs": {"center-badge": "VS Custom"}
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="parallel-container">' in html
        assert '<div class="pc-left">' in html
        assert '<div class="pc-col-header">Columna Izquierda</div>' in html
        assert '<div class="pc-node">Punto L1</div>' in html
        assert '<span class="vs-badge">VS Custom</span>' in html
        assert '<div class="pc-right">' in html
        assert '<div class="pc-col-header">Columna Derecha</div>' in html
        assert '<div class="pc-node">Punto R1</div>' in html

    def test_overflow_warning(self, capsys):
        # 1. Test elements count > 15
        elements_many = [
            SlideElement(type="paragraph", content=f"Párrafo {i}")
            for i in range(20)
        ]
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=elements_many
        )
        pres1 = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Overflow Elements"},
            slides=[slide1]
        )
        html1 = render_presentation(pres1)
        captured1 = capsys.readouterr()
        assert "ADVERTENCIA DE DESBORDAMIENTO" in captured1.out
        assert "layout-scrollable" in html1

        # 2. Test character count > 1200
        elements_long = [
            SlideElement(type="paragraph", content="A" * 1300)
        ]
        slide2 = Slide(
            index=0,
            raw_content="",
            layout="standard",
            elements=elements_long
        )
        pres2 = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Overflow Chars"},
            slides=[slide2]
        )
        html2 = render_presentation(pres2)
        captured2 = capsys.readouterr()
        assert "ADVERTENCIA DE DESBORDAMIENTO" in captured2.out
        assert "layout-scrollable" in html2

    def test_bg_image_rendering(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            bg_image={"src": "hero.jpg", "opacity": "0.4"},
            elements=[SlideElement(type="heading", content="Test bg_image", metadata={"level": 1})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test BG"},
            slides=[slide1]
        )
        html = render_presentation(pres)
        assert 'class="slide-bg-overlay"' in html
        assert 'background-image: url(\'hero.jpg\')' in html
        assert 'opacity: 0.4' in html

    def test_speaker_notes_rendering(self):
        slide1 = Slide(
            index=0,
            raw_content="",
            speaker_notes="Secret details about performance",
            elements=[SlideElement(type="heading", content="Test notes", metadata={"level": 1})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Notes"},
            slides=[slide1]
        )
        html = render_presentation(pres)
        assert 'data-notes="Secret details about performance"' in html

    def test_steps_rendering(self):
        el = SlideElement(
            type="container_steps",
            content="",
            metadata={"items": ["Primer paso", "Segundo paso"]}
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<ul class="steps-list">' in html
        assert '<li data-step>Primer paso</li>' in html
        assert '<li data-step>Segundo paso</li>' in html

    def test_layer_stack_rendering(self):
        el = SlideElement(
            type="container_layer-stack",
            content="",
            metadata={"images": [{"alt": "Layer 1", "src": "img1.png"}, {"alt": "Layer 2", "src": "img2.png"}]}
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="layer-stack">' in html
        assert '<img src="img1.png" alt="Layer 1" class="layer-image active" />' in html
        assert '<img src="img2.png" alt="Layer 2" class="layer-image layer-hidden" />' in html

    def test_code_stepping_rendering(self):
        el = SlideElement(
            type="code_block",
            content="x = 1\ny = 2",
            metadata={"language": "python", "highlight_lines": [1], "code_steps": [[1], [2]]}
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'class="code-container stepping"' in html
        assert "data-code-steps='[[1], [2]]'" in html
        assert "data-active-step='0'" in html

    def test_hotspots_rendering(self):
        el = SlideElement(
            type="container_hotspots",
            content="",
            metadata={
                "image": "blueprint.png",
                "pins": [{"x": "15%", "y": "25%", "content": "Pin desc"}]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="hotspots-container">' in html
        assert '<img src="blueprint.png" class="hotspots-image" />' in html
        assert '<div class="hotspot-pin" data-left="15%" data-top="25%" data-index="0">' in html
        assert '<span class="pin-number">1</span>' in html
        assert '<div class="pin-tooltip-content">Pin desc</div>' in html

    def test_spotlight_rendering(self):
        el = SlideElement(
            type="container_spotlight",
            content="",
            metadata={
                "steps": [{"selector": "#test", "content": "Focus content"}]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<div class="spotlight-config"' in html
        assert 'data-spotlight-steps=' in html
        assert '#test' in html
        assert 'Focus content' in html

    def test_toc_sorting_annexes_last(self):
        # M4: Test that TOC correctly sorts standard slides first, and annexes at the end
        from presentmd.render.toc_builder import build_toc
        slide1 = Slide(
            index=0,
            raw_content="",
            layout="standard",
            elements=[SlideElement(type="heading", content="Lámina 1", metadata={"level": 2})]
        )
        slide2 = Slide(
            index=3,
            raw_content="",
            layout="annex",
            elements=[SlideElement(type="heading", content="Anexo A", metadata={"level": 2})]
        )
        slide3 = Slide(
            index=1,
            raw_content="",
            layout="standard",
            elements=[SlideElement(type="heading", content="Lámina 2", metadata={"level": 2})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test TOC"},
            slides=[slide1, slide2, slide3]
        )
        
        toc_list = build_toc(pres)
        # Deben venir: index 0 (standard), index 1 (standard), index 2 (closing), index 3 (annex)
        assert len(toc_list) == 4
        assert toc_list[0]["index"] == 0
        assert toc_list[1]["index"] == 1
        assert toc_list[2]["index"] == 2  # closing slide
        assert toc_list[2]["title"] == "Final"
        assert toc_list[3]["index"] == 3
        assert toc_list[3]["is_annex"] is True

    def test_laser_btn_rendering(self):
        # Phase C: Test that laser button is present in bottom controls
        slide1 = Slide(
            index=0,
            raw_content="",
            elements=[SlideElement(type="heading", content="Portada", metadata={"level": 1})]
        )
        pres = Presentation(
            source_path="dummy.md",
            frontmatter={"title": "Test Laser", "theme": "nexus-blueprint"},
            slides=[slide1]
        )
        html = render_presentation(pres)
        assert 'id="laserBtn"' in html
        assert 'Láser (L)' in html

    def test_bar_chart_rendering(self):
        el = SlideElement(
            type="container_bar-chart",
            content="",
            metadata={
                "attrs": {"title": "Progreso"},
                "items": [{"label": "Hito A", "desc": "75%", "percentage": 75, "color": "primary"}]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'bar-chart-wrapper' in html
        assert 'Hito A' in html
        assert 'data-bar-height="75.0%"' in html

    def test_chart_rendering(self):
        el = SlideElement(
            type="container_chart",
            content="",
            metadata={
                "attrs": {"type": "pie", "title": "Distribución"},
                "labels": ["A", "B"],
                "data": [40, 60]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'chart-wrapper' in html
        assert 'Distribución' in html
        assert 'presentmd-chart' in html
        assert 'data-chart-config=' in html

    def test_tabs_rendering(self):
        el = SlideElement(
            type="container_tabs",
            content="",
            metadata={
                "tabs": [
                    {"title": "Pestaña 1", "content": "Contenido A"}
                ]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'tabs-container' in html
        assert 'tab-button' in html
        assert 'Pestaña 1' in html
        assert 'tab-panel' in html
        assert 'Contenido A' in html

    def test_tabs_variant_rendering(self):
        el = SlideElement(
            type="container_tabs",
            content="",
            metadata={
                "attrs": {"variant": "solid-accent"},
                "tabs": [
                    {"title": "Pestaña 1", "content": "Contenido A"}
                ]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'data-variant="solid-accent"' in html

    def test_alert_attributes_and_nesting(self):
        # We can construct an alert container SlideElement with size/color metadata attributes
        el = SlideElement(
            type="container_alert",
            content="Título\n:::typewriter {size=\"xl\" color=\"muted\"}\nTexto animado\n:::",
            metadata={
                "attrs": {
                    "type": "red",
                    "size": "lg",
                    "color": "danger"
                }
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert 'data-size="lg"' in html
        assert 'data-color="danger"' in html
        assert 'typewriter-container' in html
        assert 'data-size="xl"' in html
        assert 'data-color="muted"' in html
        assert 'Texto animado' in html

    def test_pyramid_rendering(self):
        el = SlideElement(
            type="container_pyramid",
            content="",
            metadata={
                "attrs": {"layout": "funnel", "steps": "true"},
                "items": [
                    {"color": "primary", "icon": "🚀", "label": "L1", "desc": "Desc 1"}
                ]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<pmd-pyramid' in html
        assert 'data-layout="funnel"' in html
        assert 'data-steps="true"' in html
        assert 'pmd-pyramid-item' in html
        assert 'smartart-color-primary' in html
        assert 'step-hidden' in html

    def test_process_flow_rendering(self):
        el = SlideElement(
            type="container_process-flow",
            content="",
            metadata={
                "attrs": {"steps": "true"},
                "items": [
                    {"color": "success", "icon": "🎯", "label": "Step 1", "desc": "Desc A"}
                ]
            }
        )
        from presentmd.render.html_builder import render_element
        html = render_element(el)
        assert '<pmd-process-flow' in html
        assert 'data-steps="true"' in html
        assert 'pmd-process-flow-item' in html
        assert 'smartart-color-success' in html
        assert 'step-hidden' in html







