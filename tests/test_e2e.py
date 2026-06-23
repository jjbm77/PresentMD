import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from presentmd.parser import parse_presentation
from presentmd.render.engine import render_presentation
from presentmd.parser.models import Presentation, Slide, SlideElement

def test_playwright_navigation_e2e(tmp_path):
    # 1. Crear una presentación con 3 slides (Portada, Contenido, y un Anexo de Costos)
    slide1 = Slide(
        index=0,
        raw_content="",
        elements=[
            SlideElement(type="heading", content="Portada Principal", metadata={"level": 1}),
            SlideElement(type="paragraph", content="Autor de prueba")
        ]
    )
    slide2 = Slide(
        index=1,
        raw_content="",
        elements=[
            SlideElement(type="heading", content="Lámina de Contenido", metadata={"level": 2}),
            SlideElement(
                type="paragraph",
                content="Acceda al [Anexo de Costos](#anexo-costos){.link-anexo}."
            )
        ]
    )
    slide3 = Slide(
        index=2,
        raw_content="",
        layout="annex",
        elements=[
            # Heading matching the anchor id
            SlideElement(type="heading", content="Anexo Costos", metadata={"level": 2, "anchor_id": "anexo-costos"})
        ]
    )

    pres = Presentation(
        source_path="dummy.md",
        frontmatter={"title": "E2E Navigation Test", "theme": "nexus-blueprint", "nav_arrows": True},
        slides=[slide1, slide2, slide3]
    )

    html_content = render_presentation(pres)
    html_file = tmp_path / "presentation.html"
    html_file.write_text(html_content, encoding="utf-8")

    # 2. Iniciar Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        url = f"file://{html_file.resolve()}"
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Slide 0 debe ser activo al inicio
        active_slide = page.locator(".slide.active")
        assert active_slide.count() == 1
        assert "Portada Principal" in active_slide.text_content()

        # Al presionar ArrowRight, debe cambiar al slide 1
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(100)
        active_slide = page.locator(".slide.active")
        assert "Lámina de Contenido" in active_slide.text_content()

        # Hacer clic en el enlace a Anexo Costos (que debe redirigir al slide 2)
        link = page.locator(".link-anexo")
        assert link.count() == 1
        link.click()
        page.wait_for_timeout(100)

        # Ahora el slide activo debe ser el anexo
        active_slide = page.locator(".slide.active")
        assert "Anexo Costos" in active_slide.text_content()
        assert active_slide.get_attribute("data-annex") == "true"

        # Debe tener el botón de "Volver" en el anexo
        btn_volver = page.locator(".btn-volver")
        assert btn_volver.count() == 1
        btn_volver.click()
        page.wait_for_timeout(100)

        # Debe volver al slide anterior (slide 1)
        active_slide = page.locator(".slide.active")
        assert "Lámina de Contenido" in active_slide.text_content()

        # Phase A: Fullscreen controls
        # Open FAB menu to make buttons visible/clickable
        fab_trigger = page.locator("#fabTrigger")
        if fab_trigger.count() > 0:
            fab_trigger.click()
            page.wait_for_timeout(300)
            
        fs_btn = page.locator("#fsBtn")
        assert fs_btn.count() == 1
        # Click on fsBtn should not throw
        fs_btn.click()
        # Pressing 'f' should also not throw
        page.keyboard.press("f")

        # Phase A: Sidebar trigger & TOC Annexes
        sidebar_trigger = page.locator("#sidebarTrigger")
        assert sidebar_trigger.count() == 1

        # TOC Sidebar items
        toc_separator = page.locator(".toc-separator")
        assert toc_separator.count() == 1
        assert "Anexos" in toc_separator.text_content()

        toc_annex_badge = page.locator(".toc-annex-badge")
        assert toc_annex_badge.count() == 1
        assert "A1" in toc_annex_badge.text_content()

        browser.close()
