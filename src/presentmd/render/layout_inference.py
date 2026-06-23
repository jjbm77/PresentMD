"""
Layout Inference — Inferencia automática de layout por contenido del AST.

Cuando un slide no tiene directiva ::layout{} explícita, se analiza
su contenido para asignar el layout más apropiado.
"""
from __future__ import annotations

from presentmd.parser.models import Slide


def infer_layout(slide: Slide) -> str:
    """
    Infiere el layout de un slide basándose en su contenido.

    Reglas (LAYOUTS_SPEC.md):
    1. Solo H1 (opcionalmente H2 o párrafo corto) → layout-title
    2. Contiene tabla o contenido muy extenso → layout-scrollable
    3. Default → layout-standard

    split-comparison NUNCA se infiere; requiere directiva explícita.
    """
    if slide.layout:
        return slide.layout

    elements = slide.elements
    if not elements:
        return "standard"

    types = [el.type for el in elements]

    # Regla 1: Solo heading(s) y opcionalmente un párrafo corto → title
    non_trivial = [
        el for el in elements
        if el.type not in ("heading",)
        or (el.type == "heading" and el.metadata.get("level", 1) > 2)
    ]
    headings = [el for el in elements if el.type == "heading"]

    if not non_trivial and headings:
        max_level = max(h.metadata.get("level", 1) for h in headings)
        if max_level <= 2:
            return "title"

    # H1 solo con un párrafo corto
    if (
        len(elements) == 2
        and elements[0].type == "heading"
        and elements[0].metadata.get("level") == 1
        and elements[1].type == "paragraph"
        and len(elements[1].content) < 120
    ):
        return "title"

    # Regla 2: Tablas o contenido extenso → scrollable
    total_content_len = sum(len(el.content) for el in elements)
    
    # Heurística mejorada para tablas
    for el in elements:
        if el.type == "table":
            rows = el.metadata.get("rows", [])
            if len(rows) > 5 or total_content_len > 400:
                return "scrollable"
                
    # Contenido extenso general (más de 1200 caracteres)
    if total_content_len > 1200:
        return "scrollable"

    # Default
    return "standard"
