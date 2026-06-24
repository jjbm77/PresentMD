"""
TOC Builder — Genera la tabla de contenidos desde los títulos de slides.
"""
from __future__ import annotations

from presentmd.parser.models import Presentation


def build_toc(presentation: Presentation) -> list[dict]:
    """
    Construye la estructura del Table of Contents.

    Returns:
        Lista de dicts con {index, title, level, is_annex, annex_label} por cada slide con título.
    """
    normal_toc: list[dict] = []
    annex_toc: list[dict] = []
    annex_count = 0
    
    # Identify how many non-annex slides there are to correctly index the closing slide
    non_annex_count = sum(1 for slide in presentation.slides if slide.layout != "annex")
    
    for slide in presentation.slides:
        # Include first slide in TOC
            
        is_annex = (slide.layout == "annex")
        title = slide.title
        if not title and is_annex:
            title = f"Anexo {annex_count + 1}"
            
        if title:
            # Determinar el nivel del heading principal
            level = 1
            for el in slide.elements:
                if el.type == "heading":
                    level = el.metadata.get("level", 1)
                    break
            
            annex_label = None
            if is_annex:
                annex_count += 1
                annex_label = f"A{annex_count}"

            item = {
                "index": slide.index,
                "title": title,
                "level": level,
                "is_annex": is_annex,
                "annex_label": annex_label,
            }
            if is_annex:
                annex_toc.append(item)
            else:
                normal_toc.append(item)

    # Añadir slide de cierre automático al final del TOC normal
    if presentation.frontmatter.get("closing_slide", True) is not False:
        closing_title = presentation.frontmatter.get("closing_message") or "Final"
        normal_toc.append({
            "index": non_annex_count,  # El índice de cierre siempre es la cantidad de slides no-anexos
            "title": closing_title,
            "level": 1,
            "is_annex": False,
            "annex_label": None,
        })
                
    return normal_toc + annex_toc

