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

class LayerStackComponent:
    @property
    def name(self) -> str: return "layer-stack"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "images": _parse_layer_stack_images(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        images = metadata.get("images", [])
        img_html = []
        for idx, img in enumerate(images):
            active_class = " active" if idx == 0 else " layer-hidden"
            alt = escape(img.get("alt", ""))
            src = escape(img.get("src", ""))
            img_html.append(
                f'<img src="{src}" alt="{alt}" class="layer-image{active_class}" />'
            )
        return f'<div class="layer-stack">\n{"".join(img_html)}\n</div>'

