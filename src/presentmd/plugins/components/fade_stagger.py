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

class FadeStaggerComponent:
    @property
    def name(self) -> str: return "fade-stagger"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs, "content": content}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        delay = attrs.get("delay", "100")
        speed = attrs.get("speed", "300")
        
        rendered_content = render_inline(metadata.get("content", ""))
        
        return (
            f'<div class="fade-stagger-container" data-delay="{escape(delay)}" data-speed="{escape(speed)}">'
            f'  {rendered_content}'
            f'</div>'
        )

