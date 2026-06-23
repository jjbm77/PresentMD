"""
AST Builder — Pipeline de parsing de slides con markdown-it-py.

Recibe el raw content de cada slide y genera un AST enriquecido
con elementos semánticos (headings, code blocks, diagramas,
containers custom, badges, etc.).
"""
from __future__ import annotations

import re

from markdown_it import MarkdownIt

from presentmd.parser.models import (
    Slide,
    SlideElement,
)
from presentmd.parser.plugins import (
    badge_plugin,
    container_plugin,
    layout_directive_plugin,
    mark_plugin,
    bg_image_directive_plugin,
)
from presentmd.plugins.registry import component_registry


# Regex para parsear info-string de code fences con line highlighting
# Ejemplo: "sql {1, 4-5}" → language="sql", lines="1, 4-5"
_CODE_INFO_RE = re.compile(r"^(\w+)\s*\{(.+)\}\s*$")

# Regex para extraer anclas explícitas en headings. Ej: "Anexo de Costos {#anexo-costos}"
_HEADING_ANCHOR_RE = re.compile(r"^(.+?)\s*\{#([\w-]+)\}\s*$")



def _create_markdown_parser() -> MarkdownIt:
    """
    Crea y configura una instancia de markdown-it-py con todos
    los plugins custom de PresentMD.
    """
    md = MarkdownIt("commonmark", {"breaks": False, "html": False})
    md.enable("table")

    # Registrar plugins custom
    layout_directive_plugin(md)
    bg_image_directive_plugin(md)
    container_plugin(md)
    badge_plugin(md)
    mark_plugin(md)

    return md


def _parse_highlight_lines(spec: str) -> list[int]:
    """
    Parsea una especificación de líneas a resaltar.

    Ejemplos:
        "1, 4-5"  → [1, 4, 5]
        "3"       → [3]
        "1-3, 7"  → [1, 2, 3, 7]
    """
    lines: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            lines.extend(range(start, end + 1))
        else:
            lines.append(int(part))
    return sorted(set(lines))

def _convert_tokens_to_elements(tokens: list) -> list[SlideElement]:
    """
    Convierte la lista de tokens de markdown-it-py en SlideElements semánticos.

    Recorre los tokens linealmente, agrupando open/close pairs y
    extrayendo metadata de cada tipo reconocido.
    """
    elements: list[SlideElement] = []
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        tok_type = tok.type

        # --- Directiva de Layout ---
        if tok_type == "directive_layout":
            elements.append(
                SlideElement(
                    type="directive_layout",
                    content=tok.content,
                    metadata=tok.meta or {},
                )
            )
            i += 1
            continue

        # --- Directiva de BG Image ---
        if tok_type == "directive_bg_image":
            elements.append(
                SlideElement(
                    type="directive_bg_image",
                    content=tok.content,
                    metadata=tok.meta or {},
                )
            )
            i += 1
            continue

        # --- Headings (heading_open → inline → heading_close) ---
        if tok_type == "heading_open":
            level = int(tok.tag[1])  # h1 → 1, h2 → 2, etc.
            content = ""
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                content = tokens[i + 1].content
            
            anchor_id = None
            match = _HEADING_ANCHOR_RE.match(content)
            if match:
                content = match.group(1).strip()
                anchor_id = match.group(2)
            
            metadata = {"level": level}
            if anchor_id:
                metadata["anchor_id"] = anchor_id

            elements.append(
                SlideElement(
                    type="heading",
                    content=content,
                    metadata=metadata,
                )
            )
            # Saltar inline + heading_close
            i += 3
            continue

        # --- Párrafos (paragraph_open → inline → paragraph_close) ---
        if tok_type == "paragraph_open":
            content = ""
            inline_meta: dict = {}
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                inline_tok = tokens[i + 1]
                content = inline_tok.content

                # Buscar badges inline dentro de los children
                if inline_tok.children:
                    badges = [
                        {"text": c.content, "class": c.meta.get("class", "")}
                        for c in inline_tok.children
                        if c.type == "inline_badge"
                    ]
                    if badges:
                        inline_meta["badges"] = badges

            elements.append(
                SlideElement(
                    type="paragraph",
                    content=content,
                    metadata=inline_meta,
                )
            )
            i += 3
            continue

        # --- Code Fences ---
        if tok_type == "fence":
            info = tok.info.strip()
            code_content = tok.content

            # Verificar si es un diagrama Mermaid
            if info.lower() == "mermaid":
                elements.append(
                    SlideElement(
                        type="diagram",
                        content=code_content,
                        metadata={"engine": "mermaid"},
                    )
                )
                i += 1
                continue

            # Parsear info-string para language + highlight lines
            language = info
            highlight_lines: list[int] = []
            code_steps: list[list[int]] | None = None

            info_match = _CODE_INFO_RE.match(info)
            if info_match:
                language = info_match.group(1)
                spec_str = info_match.group(2)
                if "|" in spec_str:
                    code_steps = []
                    for step_spec in spec_str.split("|"):
                        step_spec = step_spec.strip()
                        if step_spec == "all" or not step_spec:
                            code_steps.append([])
                        else:
                            code_steps.append(_parse_highlight_lines(step_spec))
                    if code_steps:
                        highlight_lines = code_steps[0]
                else:
                    highlight_lines = _parse_highlight_lines(spec_str)

            elements.append(
                SlideElement(
                    type="code_block",
                    content=code_content,
                    metadata={
                        "language": language,
                        "highlight_lines": highlight_lines,
                        "code_steps": code_steps,
                    },
                )
            )
            i += 1
            continue

        # --- Blockquotes (blockquote_open → ... → blockquote_close) ---
        if tok_type == "blockquote_open":
            # Recolectar contenido hasta blockquote_close
            depth = 1
            bq_content_parts: list[str] = []
            j = i + 1
            while j < len(tokens) and depth > 0:
                if tokens[j].type == "blockquote_open":
                    depth += 1
                elif tokens[j].type == "blockquote_close":
                    depth -= 1
                elif tokens[j].type == "inline":
                    bq_content_parts.append(tokens[j].content)
                j += 1

            elements.append(
                SlideElement(
                    type="blockquote",
                    content="\n".join(bq_content_parts),
                )
            )
            i = j
            continue

        # --- Listas (bullet_list_open/ordered_list_open → ... → close) ---
        if tok_type in ("bullet_list_open", "ordered_list_open"):
            list_type = "unordered" if "bullet" in tok_type else "ordered"
            depth = 1
            list_items: list[str] = []
            j = i + 1
            close_type = tok_type.replace("_open", "_close")
            while j < len(tokens) and depth > 0:
                if tokens[j].type == tok_type:
                    depth += 1
                elif tokens[j].type == close_type:
                    depth -= 1
                elif tokens[j].type == "inline":
                    list_items.append(tokens[j].content)
                j += 1

            elements.append(
                SlideElement(
                    type="list",
                    content="\n".join(list_items),
                    metadata={"list_type": list_type, "items": list_items},
                )
            )
            i = j
            continue

        # --- Containers Custom (KPI, Alert, Progress) ---
        if tok_type.startswith("container_") and tok_type.endswith("_open"):
            container_name = tok.meta.get("name", "") if tok.meta else ""
            container_attrs = tok.meta.get("attrs", {}) if tok.meta else {}
            container_content = ""

            # El siguiente token debería ser el body
            if i + 1 < len(tokens) and "_body" in tokens[i + 1].type:
                container_content = tokens[i + 1].content

            metadata: dict = {"attrs": container_attrs}

            plugin = component_registry.get(container_name)
            if plugin and hasattr(plugin, "parse_metadata"):
                metadata = plugin.parse_metadata(container_content, container_attrs)

            elements.append(
                SlideElement(
                    type=f"container_{container_name}",
                    content=container_content,
                    metadata=metadata,
                )
            )

            # Saltar body + close tokens
            j = i + 1
            while j < len(tokens):
                if tokens[j].type.endswith("_close") and "container_" in tokens[j].type:
                    j += 1
                    break
                j += 1

            i = j
            continue

        # --- Tablas (table_open → ... → table_close) ---
        if tok_type == "table_open":
            headers = []
            rows = []
            current_row = []
            in_thead = False
            in_tbody = False
            cell_content = None

            j = i + 1
            while j < len(tokens):
                t_tok = tokens[j]
                if t_tok.type == "table_close":
                    break
                elif t_tok.type == "thead_open":
                    in_thead = True
                elif t_tok.type == "thead_close":
                    in_thead = False
                elif t_tok.type == "tbody_open":
                    in_tbody = True
                elif t_tok.type == "tbody_close":
                    in_tbody = False
                elif t_tok.type == "tr_open":
                    current_row = []
                elif t_tok.type == "tr_close":
                    if in_thead:
                        headers = current_row
                    elif in_tbody:
                        rows.append(current_row)
                elif t_tok.type in ("th_open", "td_open"):
                    cell_content = ""
                elif t_tok.type == "inline":
                    cell_content = t_tok.content
                elif t_tok.type in ("th_close", "td_close"):
                    if cell_content is not None:
                        current_row.append(cell_content)
                    cell_content = None
                j += 1

            elements.append(
                SlideElement(
                    type="table",
                    metadata={
                        "headers": headers,
                        "rows": rows,
                    },
                )
            )
            i = j + 1
            continue

        # --- Inline Badge (standalone, fuera de párrafo) ---
        if tok_type == "inline_badge":
            elements.append(
                SlideElement(
                    type="inline_badge",
                    content=tok.content,
                    metadata={"class": tok.meta.get("class", "")},
                )
            )
            i += 1
            continue

        # Token no reconocido: avanzar
        i += 1

    return elements


def build_slide_ast(slide: Slide, md: MarkdownIt | None = None) -> Slide:
    """
    Construye el AST de un slide individual.

    Parsea el raw_content con markdown-it-py y convierte los tokens
    en SlideElements semánticos. Detecta la directiva ::layout{} y
    la almacena en slide.layout.

    Args:
        slide: Slide con raw_content poblado.
        md: Instancia de MarkdownIt (reutilizable). Si es None, se crea una.

    Returns:
        El mismo Slide con .elements y .layout poblados.
    """
    if md is None:
        md = _create_markdown_parser()

    tokens = md.parse(slide.raw_content)
    elements = _convert_tokens_to_elements(tokens)

    # Extraer directivas de layout y bg_image si existen
    layout = None
    bg_image = None
    final_elements: list[SlideElement] = []
    for el in elements:
        if el.type == "directive_layout":
            layout = el.metadata.get("layout_name", el.content)
        elif el.type == "directive_bg_image":
            bg_image = el.metadata.get("attrs", {})
        else:
            final_elements.append(el)

    slide.layout = layout
    slide.bg_image = bg_image
    slide.elements = final_elements

    return slide


def build_presentation_ast(slides: list[Slide]) -> list[Slide]:
    """
    Construye el AST para todos los slides de una presentación.

    Reutiliza una única instancia del parser markdown-it-py
    para eficiencia.
    """
    md = _create_markdown_parser()
    for slide in slides:
        build_slide_ast(slide, md)
    return slides
