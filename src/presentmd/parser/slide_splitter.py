"""
Divisor de Slides y extractor de notas del presentador.

Divide el contenido Markdown post-frontmatter en slides individuales
usando '---' como separador, y extrae los bloques <!-- notes --> de cada uno.
"""
from __future__ import annotations

import re

from presentmd.parser.models import Slide


# Separador de slides: una línea que contiene solo '---' (con whitespace opcional)
_SLIDE_SEPARATOR_RE = re.compile(r"\n---\s*\n")

# Notas del presentador: bloque entre <!-- notes --> y <!-- /notes -->
_SPEAKER_NOTES_RE = re.compile(
    r"<!--\s*notes\s*-->\s*\n(.*?)\n\s*<!--\s*/notes\s*-->",
    re.DOTALL,
)

# Notas del presentador (container format): :::notes ... :::
_SPEAKER_NOTES_CONTAINER_RE = re.compile(
    r":::notes\s*\n(.*?)\n\s*:::",
    re.DOTALL,
)


def split_into_slides(content: str) -> list[Slide]:
    """
    Divide el contenido Markdown en objetos Slide.

    Cada slide se separa por una línea '---'. Se ignoran los separadores
    '---' que se encuentren dentro de bloques de código (```) o contenedores
    custom (:::). Se extraen las notas del presentador (<!-- notes -->...<!-- /notes -->) 
    y se almacenan aparte en el campo speaker_notes.

    Args:
        content: Texto Markdown sin frontmatter.

    Returns:
        Lista de objetos Slide con raw_content y speaker_notes.
    """
    lines = content.splitlines()
    slides_raw: list[list[str]] = [[]]
    
    in_code_block = False
    in_container_level = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Detectar bloques de código
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            
        # Detectar contenedores custom
        elif stripped.startswith(":::"):
            if stripped == ":::":
                if in_container_level > 0:
                    in_container_level -= 1
            else:
                # Apertura de contenedor (ej: :::parallel-compare)
                in_container_level += 1
                
        # Detectar separador de slide
        if stripped == "---" and not in_code_block and in_container_level == 0:
            slides_raw.append([])
        else:
            slides_raw[-1].append(line)

    slides: list[Slide] = []
    for raw_lines in slides_raw:
        raw_stripped = "\n".join(raw_lines).strip()
        if not raw_stripped:
            continue

        # Extraer notas del presentador
        speaker_notes = None
        notes_match = _SPEAKER_NOTES_RE.search(raw_stripped)
        if notes_match:
            speaker_notes = notes_match.group(1).strip()
            # Remover el bloque de notas del contenido del slide
            raw_stripped = _SPEAKER_NOTES_RE.sub("", raw_stripped).strip()

        # Extraer notas del presentador (container format)
        container_notes_match = _SPEAKER_NOTES_CONTAINER_RE.search(raw_stripped)
        if container_notes_match:
            container_notes = container_notes_match.group(1).strip()
            if speaker_notes:
                speaker_notes += "\n\n" + container_notes
            else:
                speaker_notes = container_notes
            # Remover el bloque de notas del contenido del slide
            raw_stripped = _SPEAKER_NOTES_CONTAINER_RE.sub("", raw_stripped).strip()

        slides.append(
            Slide(
                index=len(slides),
                raw_content=raw_stripped,
                speaker_notes=speaker_notes,
            )
        )

    return slides
