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

class FeatureGridComponent:
    @property
    def name(self) -> str: return "feature-grid"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "items": _parse_feature_grid_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        cols = metadata.get("attrs", {}).get("cols", "3")
        items = metadata.get("items", [])
        
        cards = []
        for item in items:
            icon = item.get("icon", "")
            color = item.get("color", "1")
            
            cards.append(
                f'<div class="feature-card" data-color="{escape(color)}">'
                f'<div class="fc-icon">{render_inline(icon)}</div>'
                f'<div class="fc-content">{render_inline(item["content"])}</div>'
                f'</div>'
            )
        return f'<div class="feature-grid" data-cols="{cols}">\n{"".join(cards)}\n</div>'

