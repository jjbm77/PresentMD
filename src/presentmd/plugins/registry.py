import re
import json
import uuid
from html import escape
from typing import Protocol, Dict, Any

from presentmd.parser.models import KPIItem, ProgressItem

class ComponentPlugin(Protocol):
    @property
    def name(self) -> str: ...
    def parse_metadata(self, content: str, attrs: Dict[str, Any]) -> Dict[str, Any]: ...
    def render_html(self, content: str, metadata: Dict[str, Any], render_inline: callable) -> str: ...

class ComponentRegistry:
    def __init__(self):
        self._plugins: Dict[str, ComponentPlugin] = {}

    def register(self, plugin: ComponentPlugin):
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> ComponentPlugin | None:
        return self._plugins.get(name)

    def has(self, name: str) -> bool:
        return name in self._plugins

component_registry = ComponentRegistry()

# --- Parsing Helpers ---

def _is_truthy(val) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        val_lower = val.strip().lower()
        return val_lower in ("true", "yes", "1", "steps", "")
    if isinstance(val, int):
        return val != 0
    return False

_KPI_ITEM_RE = re.compile(
    r"^\-\s*\[(.+?)\]\s*(.+?)(?:\s*\{status:\s*(\w+)\})?\s*$"
)
_PROGRESS_ITEM_RE = re.compile(
    r"^\-\s*(.+?):\s*(\d+)%(?:\s*\{color:\s*([\"']?[\w-]+[\"']?)\})?\s*$"
)
_INFO_ITEM_RE = re.compile(r"^\-\s*(.+?):\s*(.+)$")

def _parse_item_options(options_str: str) -> dict:
    if not options_str:
        return {}
    options = {}
    for m in re.finditer(r"""([\w-]+)\s*[:=]\s*(?:"([^"]*)"|'([^']*)'|([\w/%.-]+))""", options_str):
        key = m.group(1)
        val = m.group(2) or m.group(3) or m.group(4)
        options[key] = val
    return options

def _parse_kpi_items(content: str) -> list[KPIItem]:
    items: list[KPIItem] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = _KPI_ITEM_RE.match(line)
        if match:
            items.append(
                KPIItem(
                    value=match.group(1).strip(),
                    label=match.group(2).strip(),
                    status=match.group(3),
                )
            )
    return items

def _parse_progress_items(content: str) -> list[ProgressItem]:
    items: list[ProgressItem] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = _PROGRESS_ITEM_RE.match(line)
        if match:
            items.append(
                ProgressItem(
                    label=match.group(1).strip(),
                    percentage=int(match.group(2)),
                    color=(match.group(3) or "primary").strip('\'"'),
                )
            )
    return items

def _parse_info_items(content: str) -> list[dict]:
    items: list[dict] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = _INFO_ITEM_RE.match(line)
        if match:
            items.append({
                "label": match.group(1).strip(),
                "value": match.group(2).strip(),
            })
    return items

def _parse_steps_items(content: str) -> list[str]:
    items: list[str] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("+ "):
            items.append(line[2:].strip())
        else:
            num_match = re.match(r"^\d+\.\s*(.*)$", line)
            if num_match:
                items.append(num_match.group(1).strip())
            else:
                items.append(line)
    return items

def _parse_layer_stack_images(content: str) -> list[dict]:
    images: list[dict] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if match:
            images.append({
                "alt": match.group(1).strip(),
                "src": match.group(2).strip()
            })
    return images

def _parse_hotspots_items(content: str) -> list[dict]:
    pins: list[dict] = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("+ "):
            line = line[2:].strip()
        match = re.match(r"^\[\s*([\d\.]+%?)\s*,\s*([\d\.]+%?)\s*\]\s*(.*)$", line)
        if match:
            x_val = match.group(1).strip()
            y_val = match.group(2).strip()
            desc = match.group(3).strip()
            if not x_val.endswith("%"):
                x_val += "%"
            if not y_val.endswith("%"):
                y_val += "%"
            pins.append({
                "x": x_val,
                "y": y_val,
                "content": desc
            })
    return pins

def _parse_spotlight_steps(content: str) -> list[dict]:
    steps = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("+ "):
            line = line[2:].strip()
        match = re.match(r"^\[(.*?)\]\s*([^{]*?)(?:\s*\{([^}]*)\})?\s*$", line)
        if match:
            selector_or_label = match.group(1).strip()
            desc = match.group(2).strip()
            options_str = match.group(3) or ""
            if desc.startswith('"') and desc.endswith('"'):
                desc = desc[1:-1].strip()
            elif desc.startswith("'") and desc.endswith("'"):
                desc = desc[1:-1].strip()
            options = _parse_item_options(options_str)
            steps.append({
                "selector_or_label": selector_or_label,
                "content": desc,
                "options": options
            })
    return steps

def _parse_timeline_phases(content: str) -> list[dict]:
    phases: list[dict] = []
    current: dict | None = None
    for line in content.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- **") and "**" in stripped[4:]:
            if current:
                phases.append(current)
            rest = stripped[2:]
            bold_end = rest.index("**", 2)
            badge = rest[2:bold_end].strip()
            title = rest[bold_end + 2:].lstrip(":").strip()
            current = {"badge": badge, "title": title, "items": [], "deliverable": None}
        elif stripped.startswith("- ") and current:
            current["items"].append(stripped[2:].strip())
        elif stripped.startswith("> ") and current:
            current["deliverable"] = stripped[2:].strip()
    if current:
        phases.append(current)
    return phases

def _parse_parallel_columns(content: str) -> dict:
    parts = re.split(r"\n\s*---\s*\n", content)
    columns = []
    for part in parts:
        col: dict = {"header": "", "items": []}
        for line in part.strip().splitlines():
            stripped = line.strip()
            if stripped.startswith("### "):
                col["header"] = stripped[4:].strip()
            elif stripped.startswith("- "):
                col["items"].append(stripped[2:].strip())
        columns.append(col)
    return {"columns": columns}

def _parse_cards_items(content: str) -> list[dict]:
    cards = []
    current_card = None
    card_open_re = re.compile(r"^::card(?:\{(.+?)\})?\s*$")
    for line in content.strip().splitlines():
        stripped = line.strip()
        match = card_open_re.match(stripped)
        if match:
            if current_card:
                cards.append(current_card)
            attrs_raw = match.group(1) or ""
            attrs = {}
            for m in re.finditer(r"""([\w-]+)\s*=\s*["'](.+?)["']""", attrs_raw):
                attrs[m.group(1)] = m.group(2)
            current_card = {"attrs": attrs, "content_lines": []}
        elif stripped == "::":
            if current_card:
                cards.append(current_card)
                current_card = None
        elif current_card is not None:
            current_card["content_lines"].append(line)
    if current_card:
        cards.append(current_card)
    for card in cards:
        card["content"] = "\n".join(card["content_lines"])
    return cards

def _parse_feature_grid_items(content: str) -> list[dict]:
    items = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("+ "):
            line = line[2:].strip()
        match = re.match(r"^\[(.*?)\]\s*(.*?)(?:\s*\{color:\s*([\w-]+)\})?$", line)
        if match:
            items.append({
                "icon": match.group(1).strip(),
                "content": match.group(2).strip(),
                "color": match.group(3) or "primary"
            })
    return items

def _parse_process_flow_items(content: str) -> list[dict]:
    items = []
    item_re = re.compile(r"^[-\*+]\s*\[(.*?)\](?:\s*([^{]+?))?(?:\s*\{([^}]*)\})?\s*$")
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = item_re.match(line)
        if match:
            label = match.group(1).strip()
            desc = match.group(2).strip() if match.group(2) else ""
            options_raw = match.group(3) or ""
            options = _parse_item_options(options_raw)
            item = {
                "label": label,
                "desc": desc,
                "icon": "",
            }
            item.update(options)
            if "texto" in item and "text" not in item:
                item["text"] = item["texto"]
            if "color" not in item:
                item["color"] = "primary"
            items.append(item)
    return items

def _parse_pyramid_items(content: str) -> list[dict]:
    items = []
    item_re = re.compile(r"^[-\*+]\s*\[(.*?)\](?:\s*([^{]+?))?(?:\s*\{([^}]*)\})?\s*$")
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = item_re.match(line)
        if match:
            label = match.group(1).strip()
            desc = match.group(2).strip() if match.group(2) else ""
            options_raw = match.group(3) or ""
            options = _parse_item_options(options_raw)
            item = {
                "label": label,
                "desc": desc,
            }
            item.update(options)
            if "texto" in item and "text" not in item:
                item["text"] = item["texto"]
            if "color" not in item:
                item["color"] = "primary"
            items.append(item)
    return items

# --- Built-in Component Plugins ---

def discover_plugins():
    import importlib
    import pkgutil
    import inspect
    from presentmd.plugins import components
    
    for _, module_name, _ in pkgutil.iter_modules(components.__path__):
        try:
            module = importlib.import_module(f"presentmd.plugins.components.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    inspect.isclass(attr)
                    and hasattr(attr, "name")
                    and hasattr(attr, "render_html")
                    and attr.__name__ not in ("ComponentPlugin", "ComponentRegistry")
                ):
                    try:
                        component_registry.register(attr())
                    except Exception as e:
                        pass
        except Exception as e:
            pass

discover_plugins()
