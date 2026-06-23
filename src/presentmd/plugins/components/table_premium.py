import re
from html import escape
from presentmd.plugins.registry import _is_truthy

TABLE_LINE_RE = re.compile(r'^\|(.+)\|$')

def _parse_table(content: str):
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    headers = []
    rows = []
    state = 'header'
    for line in lines:
        m = TABLE_LINE_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split('|')]
        if state == 'header':
            headers = cells
            state = 'separator'
        elif state == 'separator':
            state = 'data'
        else:
            rows.append(cells)
    return headers, rows

def _build_colors_style(colors_str: str) -> str:
    if not colors_str:
        return ''
    parts = [p.strip() for p in colors_str.split(',') if p.strip()]
    rules = []
    for p in parts:
        try:
            idx = int(p)
        except ValueError:
            continue
        rules.append(f'--tc-{idx}: var(--color-{idx})')
        rules.append(f'--tc-text-{idx}: var(--color-{idx}-contrast)')
    return 'style="' + '; '.join(rules) + '"' if rules else ''

class PremiumTableComponent:
    @property
    def name(self) -> str:
        return "pmd-table"

    def parse_metadata(self, content: str, attrs: dict) -> dict:
        headers, rows = _parse_table(content)
        return {
            "attrs": attrs,
            "headers": headers,
            "rows": rows
        }

    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        headers = metadata.get("headers", [])
        rows = metadata.get("rows", [])
        if not headers and not rows:
            return ""

        variant = attrs.get("variant", "angled")
        title = attrs.get("title", "")
        total_row = _is_truthy(attrs.get("total-row", False))
        colors_str = attrs.get("colors", "")
        colors_style = _build_colors_style(colors_str)
        total_attr = ' data-total-row="true"' if total_row else ''

        thead_rows = ""
        if headers:
            ths = "".join(f"<th>{render_inline(h)}</th>" for h in headers)
            thead_rows = f"<thead><tr>{ths}</tr></thead>"

        tbody_rows = []
        for row in rows:
            tds = "".join(f"<td>{render_inline(c)}</td>" for c in row)
            tbody_rows.append(f"<tr>{tds}</tr>")
        tbody = f"<tbody>{''.join(tbody_rows)}</tbody>"

        caption = f"<caption>{escape(title)}</caption>" if title else ""

        table_html = f"<table>{caption}{thead_rows}{tbody}</table>"

        wrapper = (
            f'<div class="pmd-table-wrapper" '
            f'data-variant="{escape(variant)}"{total_attr} '
            f'{colors_style}>'
            f'{table_html}'
            f'</div>'
        )
        return wrapper