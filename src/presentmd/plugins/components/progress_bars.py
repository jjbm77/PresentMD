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

class ProgressBarsComponent:
    @property
    def name(self) -> str: return "progress-bars"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        items = _parse_progress_items(content)
        return {
            "attrs": attrs,
            "items": [{"label": p.label, "percentage": p.percentage, "color": p.color} for p in items]
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        rows = []
        for item in items:
            color = item.get("color", "1")
            pct = item["percentage"]
            rows.append(
                f'<div class="progress-row">'
                f'<span class="progress-label">{render_inline(item["label"])}</span>'
                f'<div class="progress-track">'
                f'<div class="bar-fill" data-color="{color}" data-target-width="{pct}%"></div>'
                f'</div>'
                f'<span class="progress-pct">{pct}%</span>'
                f'</div>'
            )
        return "\n".join(rows)

