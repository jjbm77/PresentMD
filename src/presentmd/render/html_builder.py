"""
HTML Builder — Convierte SlideElements del AST en fragmentos HTML semánticos.

Cada tipo de elemento tiene su función de renderizado dedicada,
mapeando directamente a las clases CSS del tema Nexus Blueprint.
"""
from __future__ import annotations

import re
import re
from html import escape

from markdown_it import MarkdownIt
from presentmd.parser.models import SlideElement
from presentmd.parser.plugins import badge_plugin, mark_plugin
from presentmd.render.code_highlighter import highlight_code
from presentmd.plugins.registry import component_registry

# Configure a shared inline MarkdownIt parser with custom plugins
_md_inline = MarkdownIt("commonmark", {"breaks": False, "html": True})
badge_plugin(_md_inline)
mark_plugin(_md_inline)

def _render_inline_badge(self, tokens, idx, options, env):
    token = tokens[idx]
    raw = token.meta.get("class", "")
    classes = [c for c in re.split(r'[. ]+', raw) if c and c != 'badge']
    return f'<span class="badge {" ".join(classes)}">{escape(token.content)}</span>'

_md_inline.add_render_rule("inline_badge", _render_inline_badge)

def render_block_markdown(text: str) -> str:
    """Parsea y renderiza recursivamente bloques completos de markdown en HTML."""
    from presentmd.parser.ast_builder import _create_markdown_parser, _convert_tokens_to_elements
    md = _create_markdown_parser()
    tokens = md.parse(text)
    elements = _convert_tokens_to_elements(tokens)
    return "\n".join(render_element(el) for el in elements)

def render_any_markdown(text: str) -> str:
    """Rutea dinámicamente el renderizado a nivel de bloque o inline según el contenido."""
    stripped = text.strip()
    if not stripped:
        return ""
    
    # Heurística para detectar si es bloque markdown
    is_block = (
        "\n" in stripped or
        stripped.startswith(("#", "-", "*", "+", ">", ":::", "::", "|", "```")) or
        re.search(r"^\d+\.\s", stripped) is not None
    )
    
    if is_block:
        return render_block_markdown(stripped)
    return render_inline_markdown(stripped)

def render_element(el: SlideElement) -> str:
    """Despacha el renderizado al handler correcto según el tipo."""
    if el.type.startswith("container_"):
        component_name = el.type.replace("container_", "")
        plugin = component_registry.get(component_name)
        if plugin:
            return plugin.render_html(el.content, el.metadata, render_any_markdown)
        return _render_fallback(el)

    handlers = {
        "heading": _render_heading,
        "paragraph": _render_paragraph,
        "list": _render_list,
        "blockquote": _render_blockquote,
        "code_block": _render_code_block,
        "diagram": _render_diagram,
        "inline_badge": _render_badge,
        "table": _render_table,
    }
    handler = handlers.get(el.type, _render_fallback)
    return handler(el)

def render_inline_markdown(text: str) -> str:
    """Renderiza markup inline usando markdown-it-py con soporte para enlaces con atributos y contadores animados."""
    # Pre-procesar enlaces con atributos para convertirlos a HTML que markdown-it-py pasará tal cual
    # Ej: [Anexo A](#anexo-a){.link-anexo} -> <a href="#anexo-a" class="link-anexo" data-target="#anexo-a">Anexo A</a>
    # Ej: [Caja a resaltar](#){#mi-caja style="padding:20px;"} -> <a href="#" id="mi-caja" style="padding:20px;">Caja a resaltar</a>
    def replace_link(match):
        label, url, attrs_str = match.groups()
        if attrs_str is None:
            attrs_str = ""
        
        url_stripped = url.strip().lower()
        if any(url_stripped.startswith(scheme) for scheme in ("javascript:", "data:", "vbscript:")):
            sanitized_url = "#"
        else:
            sanitized_url = url
            
        attrs = {}
        parts = re.findall(r'(?:[^\s"\']|"[^"]*"|\'[^\']*\')+', attrs_str)
        allowed_attributes = {"id", "class", "target", "rel", "title", "download"}
        for part in parts:
            if part.startswith('#'):
                attrs['id'] = part[1:]
            elif part.startswith('.'):
                existing_class = attrs.get('class', '')
                attrs['class'] = f"{existing_class} {part[1:]}".strip()
            elif '=' in part:
                key, val = part.split('=', 1)
                key_lower = key.strip().lower()
                val = val.strip('"\'')
                if key_lower in allowed_attributes or key_lower.startswith("data-"):
                    attrs[key_lower] = val
        
        attr_pairs = []
        for k, v in attrs.items():
            attr_pairs.append(f'{k}="{v}"')
        
        if 'data-target' not in attrs:
            attr_pairs.append(f'data-target="{sanitized_url}"')
            
        attrs_html = " ".join(attr_pairs)
        if attrs_html:
            attrs_html = " " + attrs_html
            
        return f'<a href="{sanitized_url}"{attrs_html}>{label}</a>'
    
    # Pre-procesar contadores animados: [[+9000]]{.animated-counter suffix="%"}
    def replace_counter(match):
        value_raw = match.group(1).strip()
        attrs_str = match.group(2).strip()
        attrs = {}
        parts = re.findall(r'(?:[^\s"\']|"[^"]*"|\'[^\']*\')+', attrs_str)
        for part in parts:
            if part.startswith('#'):
                attrs['id'] = part[1:]
            elif part.startswith('.'):
                existing_class = attrs.get('class', '')
                attrs['class'] = f"{existing_class} {part[1:]}".strip()
            elif '=' in part:
                key, val = part.split('=', 1)
                val = val.strip('"\'')
                attrs[key] = val
                
        existing_class = attrs.get('class', '')
        if 'animated-counter' not in existing_class:
            attrs['class'] = f"{existing_class} animated-counter".strip()
            
        # Extraer valor numérico target (e.g. "+9000" -> 9000)
        target_val = re.sub(r'[^\d-]', '', value_raw)
        attrs['data-target'] = target_val
        
        attr_pairs = []
        for k, v in attrs.items():
            attr_pairs.append(f'{k}="{v}"')
            
        attrs_html = " ".join(attr_pairs)
        if attrs_html:
            attrs_html = " " + attrs_html
            
        return f'<span{attrs_html}>{value_raw}</span>'
    
    processed = re.sub(
        r'\[\[([^\]]+)\]\]\{([^}]+)\}',
        replace_counter,
        text
    )
    
    processed = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)(?:\{([^}]+)\})?',
        replace_link,
        processed
    )
    
    return _md_inline.renderInline(processed)


def _render_heading(el: SlideElement) -> str:
    level = el.metadata.get("level", 1)
    tag = f"h{level}"
    css = f"slide-h{level}"
    return f'<{tag} class="{css}">{escape(el.content)}</{tag}>'

def _render_paragraph(el: SlideElement) -> str:
    content = render_inline_markdown(el.content)
    return f'<p>{content}</p>'

def _render_list(el: SlideElement) -> str:
    list_type = el.metadata.get("list_type", "unordered")
    tag = "ul" if list_type == "unordered" else "ol"
    items = el.metadata.get("items", [])
    li_html = "\n".join(f'<li>{render_inline_markdown(item)}</li>' for item in items)
    return f'<{tag} class="content-list">\n{li_html}\n</{tag}>'

def _render_blockquote(el: SlideElement) -> str:
    content = render_inline_markdown(el.content)
    return f'<blockquote class="impact-quote">{content}</blockquote>'

def _render_code_block(el: SlideElement) -> str:
    language = el.metadata.get("language", "")
    highlight_lines = el.metadata.get("highlight_lines", [])
    code_steps = el.metadata.get("code_steps")
    return highlight_code(el.content, language, highlight_lines, code_steps)

def _render_diagram(el: SlideElement) -> str:
    svg_content = el.metadata.get("svg_content")
    if svg_content:
        return f'<div class="diagram-container">{svg_content}</div>'
    engine = el.metadata.get("engine", "unknown").lower()
    source = escape(el.content.strip())
    
    if engine == "mermaid":
        return f'<div class="diagram-container"><pre class="mermaid">{source}</pre></div>'
        
    return (
        f'<div class="diagram-container fallback">'
        f'  <div class="diagram-fallback-header">'
        f'    <span class="diagram-icon">📊</span>'
        f'    <span class="diagram-title">Diagrama {engine.upper()} (Vista Previa de Código)</span>'
        f'    <span class="diagram-badge">CÓDIGO FUENTE</span>'
        f'  </div>'
        f'  <pre class="diagram-fallback-code"><code>{source}</code></pre>'
        f'  <div class="diagram-fallback-footer">'
        f'    💡 Este diagrama requiere un plugin del lado del cliente o no es compatible.'
        f'  </div>'
        f'</div>'
    )


def _render_badge(el: SlideElement) -> str:
    css_class = el.metadata.get("class", "badge-blue")
    return f'<span class="badge {css_class}">{escape(el.content)}</span>'


def _render_fallback(el: SlideElement) -> str:
    return f'<div class="unknown-element"><!-- {el.type} -->{escape(el.content)}</div>'


def _render_table(el: SlideElement) -> str:
    headers = el.metadata.get("headers", [])
    rows = el.metadata.get("rows", [])

    thead = ""
    if headers:
        th_cols = "".join(f"<th>{render_inline_markdown(h)}</th>" for h in headers)
        thead = f"<thead>\n<tr>{th_cols}</tr>\n</thead>\n"

    tbody_rows = []
    for r in rows:
        td_cols = "".join(f"<td>{render_inline_markdown(c)}</td>" for c in r)
        tbody_rows.append(f"<tr>{td_cols}</tr>")
    tbody = f"<tbody>\n" + "\n".join(tbody_rows) + "\n</tbody>\n"

    return f'<table class="styled-table">\n{thead}{tbody}</table>'
