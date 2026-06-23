"""
Plugins custom para markdown-it-py.

Implementa las extensiones de parsing requeridas por PresentMD:
- Container blocks: :::kpi-grid, :::alert, :::progress-bars
- Inline badges: [TEXT]{.badge-color}
- Layout directives: ::layout{name}

Estos plugins modifican el tokenizer de markdown-it-py para reconocer
sintaxis custom y generar tokens semánticos en el AST.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markdown_it import MarkdownIt
    from markdown_it.rules_block import StateBlock
    from markdown_it.rules_inline import StateInline


# ---------------------------------------------------------------------------
# A. Container Plugin (:::name{attrs} ... :::)
# ---------------------------------------------------------------------------
# Soporta: kpi-grid, alert, progress-bars
# Inspirado en markdown-it-container pero implementado directamente
# para mayor control sobre los atributos {key="value"}.

_CONTAINER_OPEN_RE = re.compile(
    r"^:{3,}\s*([\w-]+)(?:\s*\{(.+?)\})?\s*$"
)
_CONTAINER_CLOSE_RE = re.compile(r"^:{3,}\s*$")


def _container_block_rule(
    state: StateBlock, startLine: int, endLine: int, silent: bool
) -> bool:
    """Regla de bloque para parsear containers :::name{attrs}...:::."""
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]
    line_text = state.src[pos:maximum]

    match = _CONTAINER_OPEN_RE.match(line_text)
    if not match:
        return False

    container_name = match.group(1)
    attrs_raw = match.group(2) or ""

    if silent:
        return True

    # Buscar el cierre ::: (teniendo en cuenta contenedores anidados)
    nextLine = startLine + 1
    has_close = False
    depth = 1
    while nextLine < endLine:
        pos_next = state.bMarks[nextLine] + state.tShift[nextLine]
        max_next = state.eMarks[nextLine]
        close_text = state.src[pos_next:max_next].strip()
        
        # Ignorar líneas vacías o espacios antes de validar
        if not close_text:
            nextLine += 1
            continue
            
        if _CONTAINER_OPEN_RE.match(close_text):
            depth += 1
        elif _CONTAINER_CLOSE_RE.match(close_text):
            depth -= 1
            if depth == 0:
                has_close = True
                break
        nextLine += 1

    if not has_close:
        return False

    # Parsear atributos {type="red" icon="⚠️"}
    parsed_attrs = _parse_container_attrs(attrs_raw)

    # Token de apertura
    token_open = state.push(f"container_{container_name}_open", "div", 1)
    token_open.markup = ":::"
    token_open.block = True
    token_open.info = container_name
    token_open.meta = {"attrs": parsed_attrs, "name": container_name}
    token_open.map = [startLine, nextLine]

    # Contenido interno (se almacena como texto raw para parsing posterior)
    content_start = startLine + 1
    content_end = nextLine
    inner_lines = []
    for ln in range(content_start, content_end):
        p = state.bMarks[ln] + state.tShift[ln]
        m = state.eMarks[ln]
        inner_lines.append(state.src[p:m])

    token_content = state.push(f"container_{container_name}_body", "", 0)
    token_content.content = "\n".join(inner_lines)
    token_content.map = [content_start, content_end]

    # Token de cierre
    token_close = state.push(f"container_{container_name}_close", "div", -1)
    token_close.markup = ":::"
    token_close.block = True

    state.line = nextLine + 1
    return True


def _parse_container_attrs(attrs_raw: str) -> dict:
    """Parsea atributos de container: type='red' icon='⚠️' → dict."""
    if not attrs_raw:
        return {}
    result = {}
    # Matchea key="value" o key='value' (soporta guiones en la clave)
    # Usa regex que respeta el tipo de comilla de apertura y cierre
    for m in re.finditer(r"""([\w-]+)\s*=\s*"([^"]*)"|\'([^\']*)\'|([\w-]+)\s*=\s*([\w-]+)""", attrs_raw):
        groups = m.groups()
        # key="value" case
        if groups[0] and groups[1] is not None:
            result[groups[0]] = groups[1]
        # key='value' case  
        elif groups[2] is not None:
            result[groups[2]] = groups[3]
        # key=value sin comillas
        elif groups[4]:
            result[groups[4]] = groups[5]
    return result


# ---------------------------------------------------------------------------
# B. Inline Badge Plugin: [TEXT]{.badge-color}
# ---------------------------------------------------------------------------
# Reconoce [TEXT]{.class} donde NO hay (url) intermedio (no es un link).

_BADGE_RE = re.compile(r"\[([^\]]+)\]\{\.([a-zA-Z0-9_. -]+)\}")


def _badge_inline_rule(state: StateInline, silent: bool) -> bool:
    """Regla inline para parsear badges [TEXT]{.class}."""
    if state.src[state.pos] != "[":
        return False

    # Intentar matchear desde la posición actual
    rest = state.src[state.pos:]
    match = _BADGE_RE.match(rest)
    if not match:
        return False

    # Verificar que NO sea un link (no tiene (url) antes del {.class})
    # Si el caracter después del ] es (, es un link normal, no un badge
    bracket_close = state.pos + 1 + len(match.group(1))
    if bracket_close < len(state.src) and state.src[bracket_close] == "(":
        return False

    if silent:
        return True

    token = state.push("inline_badge", "span", 0)
    token.content = match.group(1)
    token.meta = {"class": match.group(2)}
    token.markup = "{.}"

    state.pos += match.end()
    return True


# ---------------------------------------------------------------------------
# C. Layout Directive Plugin: ::layout{name}
# ---------------------------------------------------------------------------
# Reconoce líneas que comienzan con ::layout{...} como directivas de bloque.

_LAYOUT_RE = re.compile(r"^::layout\{([a-zA-Z0-9_-]+)\}\s*$")


def _layout_block_rule(
    state: StateBlock, startLine: int, endLine: int, silent: bool
) -> bool:
    """Regla de bloque para parsear directivas ::layout{name}."""
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]
    line_text = state.src[pos:maximum]

    match = _LAYOUT_RE.match(line_text)
    if not match:
        return False

    if silent:
        return True

    token = state.push("directive_layout", "", 0)
    token.content = match.group(1)
    token.meta = {"layout_name": match.group(1)}
    token.map = [startLine, startLine + 1]
    token.markup = "::layout"

    state.line = startLine + 1
    return True


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Registro de plugins
# ---------------------------------------------------------------------------

def container_plugin(md: MarkdownIt) -> None:
    """Registra la regla de bloque para containers :::name{attrs}."""
    md.block.ruler.before(
        "fence", "presentmd_container", _container_block_rule
    )


def badge_plugin(md: MarkdownIt) -> None:
    """Registra la regla inline para badges [TEXT]{.class}."""
    md.inline.ruler.before(
        "link", "presentmd_badge", _badge_inline_rule
    )


def layout_directive_plugin(md: MarkdownIt) -> None:
    """Registra la regla de bloque para directivas ::layout{name}."""
    md.block.ruler.before(
        "fence", "presentmd_layout", _layout_block_rule
    )


# ---------------------------------------------------------------------------
# D. Natural Text Highlight Plugin: ==texto==
# ---------------------------------------------------------------------------

def _mark_inline_rule(state: StateInline, silent: bool) -> bool:
    """Regla inline para parsear el resaltado de texto natural ==texto==."""
    if state.pos + 2 > state.posMax:
        return False
    if state.src[state.pos:state.pos+2] != "==":
        return False

    # Buscar el cierre "=="
    start = state.pos
    pos = start + 2
    found = False
    while pos + 1 < state.posMax:
        if state.src[pos:pos+2] == "==":
            found = True
            break
        pos += 1

    if not found:
        return False

    if silent:
        return True

    # Purgar el delimitador y parsear el interior
    token_open = state.push("mark_open", "mark", 1)
    token_open.markup = "=="
    token_open.attrs = {"class": "token-highlight"}

    original_pos_max = state.posMax
    state.pos = start + 2
    state.posMax = pos
    state.md.inline.tokenize(state)
    
    token_close = state.push("mark_close", "mark", -1)
    token_close.markup = "=="

    state.pos = pos + 2
    state.posMax = original_pos_max
    return True


def mark_plugin(md: MarkdownIt) -> None:
    """Registra la regla inline para resaltado ==texto==."""
    md.inline.ruler.before(
        "emphasis", "presentmd_mark", _mark_inline_rule
    )


# ---------------------------------------------------------------------------
# E. Bg Image Directive Plugin: ::bg-image{src="..." opacity="..."}
# ---------------------------------------------------------------------------

_BG_IMAGE_RE = re.compile(r"^::bg-image\{(.+?)\}\s*$")


def _bg_image_block_rule(
    state: StateBlock, startLine: int, endLine: int, silent: bool
) -> bool:
    """Regla de bloque para parsear directivas ::bg-image{src="..." opacity="..."}."""
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]
    line_text = state.src[pos:maximum]

    match = _BG_IMAGE_RE.match(line_text)
    if not match:
        return False

    if silent:
        return True

    attrs = _parse_container_attrs(match.group(1))

    token = state.push("directive_bg_image", "", 0)
    token.content = match.group(1)
    token.meta = {"attrs": attrs}
    token.map = [startLine, startLine + 1]
    token.markup = "::bg-image"

    state.line = startLine + 1
    return True


def bg_image_directive_plugin(md: MarkdownIt) -> None:
    """Registra la regla de bloque para directivas ::bg-image{attrs}."""
    md.block.ruler.before(
        "fence", "presentmd_bg_image", _bg_image_block_rule
    )

