"""
Code Highlighter — Wrapper de Pygments con soporte para line highlighting.

Genera HTML con spans por línea, cada una con data-line="N",
y marca las líneas activas con la clase highlight-active.
"""
from __future__ import annotations

import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


class _LineWrappingFormatter(HtmlFormatter):
    """Formatter que envuelve cada línea en un span con data-line."""

    def __init__(self, highlight_lines: list[int] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._highlight_lines = set(highlight_lines or [])

    def _format_lines(self, tokensource):
        line_num = 0
        for t, piece in super()._format_lines(tokensource):
            if t == 1:
                line_num += 1
                classes = "code-line"
                if line_num in self._highlight_lines:
                    classes += " highlight-active"
                yield 1, f'<span class="{classes}" data-line="{line_num}">{piece}</span>'
            else:
                yield t, piece


def highlight_code(
    code: str,
    language: str = "",
    highlight_lines: list[int] | None = None,
    code_steps: list[list[int]] | None = None,
) -> str:
    """
    Resalta código con Pygments y envuelve líneas con data attributes.

    Args:
        code: Código fuente a resaltar.
        language: Lenguaje para el lexer (ej: "sql", "python").
        highlight_lines: Lista de líneas a marcar como activas.
        code_steps: Opcional, lista de pasos con líneas a resaltar por paso.

    Returns:
        HTML string con el código resaltado.
    """
    try:
        lexer = get_lexer_by_name(language) if language else TextLexer()
    except Exception:
        lexer = TextLexer()

    total_lines = len(code.splitlines())

    resolved_steps = None
    data_steps_attr = ""
    stepping_class = ""
    initial_highlight_lines = highlight_lines

    if code_steps is not None:
        resolved_steps = []
        for step in code_steps:
            if not step:
                # "all"
                resolved_steps.append(list(range(1, total_lines + 1)))
            else:
                resolved_steps.append(step)
        
        # Serializar pasos para el JS
        data_steps_attr = f" data-code-steps='{json.dumps(resolved_steps)}' data-active-step='0'"
        stepping_class = " stepping"
        if resolved_steps:
            initial_highlight_lines = resolved_steps[0]
    elif highlight_lines:
        stepping_class = " stepping-static"

    formatter = _LineWrappingFormatter(
        highlight_lines=initial_highlight_lines,
        nowrap=True,
        noclasses=False,
    )

    highlighted = highlight(code, lexer, formatter)

    lang_label = language.upper() if language else "CODE"
    header = f'<div class="code-header">{lang_label}</div>'

    return (
        f'<div class="code-container{stepping_class}"{data_steps_attr}>'
        f'{header}'
        f'<pre><code>{highlighted}</code></pre>'
        f'</div>'
    )

