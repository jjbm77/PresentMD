import re
from html import escape
from presentmd.plugins.registry import _is_truthy

_RADIAL_ITEM_RE = re.compile(
    r"\[([^\]]+)\]\s*(.+)$"
)

def _parse_radial_items(content: str) -> list[dict]:
    items = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("+ "):
            line = line[2:].strip()
        match = _RADIAL_ITEM_RE.match(line)
        if match:
            label = match.group(1).strip()
            rest = match.group(2).strip() if match.group(2) else ""
            
            # Extract color from options at end
            color_match = re.search(r'\{color:\s*("([^"]+)"|\'([^\']+)\'|(\w+))\}', rest)
            color = "primary"
            if color_match:
                color = color_match.group(2) or color_match.group(3) or color_match.group(4) or "primary"
                # Remove the {color: ...} part from rest
                rest = re.sub(r'\s*\{color:\s*("[^"]+"|\'[^\']+\'|\w+)\}', '', rest).strip()
            
            item = {
                "label": label,
                "desc": rest,
                "icon": "",
                "text": "",
                "color": color,
            }
            items.append(item)
    return items

class RadialProcessComponent:
    @property
    def name(self) -> str: return "radial-process"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "center_title": attrs.get("center-title", ""),
            "items": _parse_radial_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        if not items:
            return ""
        
        attrs = metadata.get("attrs", {})
        center_title = metadata.get("center_title", "")
        is_steps = _is_truthy(attrs.get("steps", False))
        
        steps_class = " step-hidden" if is_steps else ""
        steps_attr = " data-step" if is_steps else ""
        
        items_html = []
        for idx, item in enumerate(items):
            color = item.get("color", "1")
            icon = item.get("icon", "")
            step_text = item.get("text", "")
            
            icon_html = f'<div class="pmd-radial-process-icon">{render_inline(icon)}</div>' if icon else ""
            text_html = f'<div class="pmd-radial-process-text">{render_inline(step_text)}</div>' if step_text else ""
            desc_html = f'<div class="pmd-radial-process-desc">{render_inline(item["desc"])}</div>' if item.get("desc") else ""
            label_html = f'<div class="pmd-radial-process-label">{render_inline(item["label"])}</div>' if item.get("label") else ""
            
            items_html.append(
                f'<div class="pmd-radial-process-item{steps_class}"{steps_attr} data-color="{escape(color)}">'
                f'  {icon_html}'
                f'  {text_html}'
                f'  {label_html}'
                f'  {desc_html}'
                f'</div>'
            )
        
        center_attr = center_title.replace('"', '&quot;').replace("'", '&apos;').replace('<', '&lt;').replace('>', '&gt;')
        steps_container_attr = ' data-steps="true"' if is_steps else ''
        
        return (
            f'<pmd-radial-process center-title="{center_attr}"{steps_container_attr}>\n'
            f'  {"".join(items_html)}\n'
            f'</pmd-radial-process>'
        )