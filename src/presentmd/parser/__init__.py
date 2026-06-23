"""
PresentMD Parser — Módulo orquestador.

Expone la función principal `parse_presentation(path)` que ejecuta
el pipeline completo: lectura → frontmatter → split slides → AST.
"""
from __future__ import annotations

from pathlib import Path

from presentmd.parser.ast_builder import build_presentation_ast
from presentmd.parser.frontmatter import extract_frontmatter
from presentmd.parser.models import Presentation, Slide, SlideElement
from presentmd.parser.slide_splitter import split_into_slides

__all__ = [
    "parse_presentation",
    "Presentation",
    "Slide",
    "SlideElement",
]


def parse_presentation(path: str | Path) -> Presentation:
    """
    Pipeline completo de parsing de una presentación PresentMD.

    1. Lee el archivo .md desde disco.
    2. Extrae el YAML frontmatter.
    3. Divide el contenido restante en slides por '---'.
    4. Construye el AST enriquecido de cada slide.

    Args:
        path: Ruta al archivo .md de la presentación.

    Returns:
        Objeto Presentation con frontmatter, slides y AST completo.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el frontmatter YAML es inválido.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    if not filepath.suffix.lower() == ".md":
        raise ValueError(f"Se esperaba un archivo .md, se recibió: {filepath.suffix}")

    raw_text = filepath.read_text(encoding="utf-8")

    # Paso 1: Extraer frontmatter
    frontmatter, content = extract_frontmatter(raw_text)

    # Paso 2: Dividir en slides
    slides = split_into_slides(content)

    # Paso 3: Construir AST de cada slide
    build_presentation_ast(slides)

    return Presentation(
        frontmatter=frontmatter,
        slides=slides,
        source_path=str(filepath.resolve()),
    )
