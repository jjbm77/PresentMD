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

class InfoGridComponent:
    @property
    def name(self) -> str: return "info-grid"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "items": _parse_info_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        boxes = []
        for item in items:
            boxes.append(
                f'<div class="info-box">'
                f'<div class="ib-label">{render_inline(item["label"])}</div>'
                f'<div class="ib-value">{render_inline(item["value"])}</div>'
                f'</div>'
            )
        return f'<div class="info-grid">\n{"".join(boxes)}\n</div>'

