import re
import json
import uuid
from html import escape
from presentmd.plugins.registry import (
    _is_truthy,
    _parse_item_options,
    _parse_kpi_items,
    _parse_progress_items,
    _parse_info_items,
    _parse_steps_items,
    _parse_layer_stack_images,
    _parse_hotspots_items,
    _parse_spotlight_steps,
    _parse_timeline_phases,
    _parse_parallel_columns,
    _parse_cards_items,
    _parse_feature_grid_items,
    _parse_process_flow_items,
    _parse_pyramid_items,
)
from presentmd.parser.models import KPIItem, ProgressItem

class KPIGridComponent:
    @property
    def name(self) -> str: return "kpi-grid"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        items = _parse_kpi_items(content)
        return {
            "attrs": attrs,
            "items": [{"value": k.value, "label": k.label, "status": k.status} for k in items]
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        cards = []
        for item in items:
            status = item.get("status") or ""
            color_map = {"critical": "6", "amber": "3", "green": "4", "up": "4", "down": "6", "warning": "3"}
            color_attr = color_map.get(status, status if status and status.isdigit() else "1")
            cards.append(
                f'<div class="kpi-card" data-color="{color_attr}">'
                f'<div class="kpi-value">{escape(item["value"])}</div>'
                f'<div class="kpi-label">{escape(item["label"])}</div>'
                f'</div>'
            )
        return f'<div class="kpi-grid">\n{"".join(cards)}\n</div>'

