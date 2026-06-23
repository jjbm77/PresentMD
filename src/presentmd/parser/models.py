"""
Modelos de datos para el AST de PresentMD.

Define las estructuras inmutables que representan una presentación parseada:
Presentation → Slide[] → SlideElement[] (con metadata enriquecida).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KPIItem:
    """Un ítem dentro de un bloque :::kpi-grid."""
    value: str
    label: str
    status: str | None = None


@dataclass
class ProgressItem:
    """Un ítem dentro de un bloque :::progress-bars."""
    label: str
    percentage: int
    color: str = "primary"


@dataclass
class SlideElement:
    """
    Nodo genérico del AST de un slide.

    Cada elemento tiene un tipo semántico y metadata asociada.
    Los tipos reconocidos incluyen:
        - heading, paragraph, code_block, blockquote, list
        - diagram (d2, mermaid)
        - container_kpi_grid, container_alert, container_progress
        - inline_badge
        - directive_layout
    """
    type: str
    content: str = ""
    metadata: dict = field(default_factory=dict)
    children: list[SlideElement] = field(default_factory=list)

    def __repr__(self) -> str:
        meta_str = f", meta={self.metadata}" if self.metadata else ""
        children_str = f", children={len(self.children)}" if self.children else ""
        content_preview = (
            self.content[:60] + "..." if len(self.content) > 60 else self.content
        )
        return f"SlideElement({self.type!r}, {content_preview!r}{meta_str}{children_str})"


@dataclass
class Slide:
    """Representa una diapositiva individual dentro de la presentación."""
    index: int
    raw_content: str
    layout: str | None = None
    elements: list[SlideElement] = field(default_factory=list)
    speaker_notes: str | None = None
    bg_image: dict | None = None

    @property
    def title(self) -> str | None:
        """Extrae el título (primer H1 o H2) del slide, si existe."""
        for el in self.elements:
            if el.type == "heading" and el.metadata.get("level", 99) <= 2:
                return el.content
        return None


@dataclass
class Presentation:
    """Modelo raíz: una presentación completa parseada desde un archivo .md."""
    frontmatter: dict
    slides: list[Slide]
    source_path: str

    @property
    def title(self) -> str:
        return self.frontmatter.get("title", "Sin título")

    @property
    def theme(self) -> str:
        return self.frontmatter.get("theme", "nexus-blueprint")

    @property
    def slide_count(self) -> int:
        return len(self.slides)
