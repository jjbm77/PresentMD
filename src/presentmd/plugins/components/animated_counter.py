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

class AnimatedCounterComponent:
    @property
    def name(self) -> str: return "animated-counter"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs, "content": content}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        from_val = attrs.get("from", "0")
        to_val = attrs.get("to", "100")
        prefix = attrs.get("prefix", "")
        suffix = attrs.get("suffix", "")
        duration = attrs.get("duration", "1500")
        title = attrs.get("title", "")
        
        title_html = f'<div class="animated-counter-title">{render_inline(title)}</div>' if title else ""
        
        return (
            f'<div class="animated-counter-container">'
            f'  <span class="animated-counter" data-from="{escape(from_val)}" data-target="{escape(to_val)}" '
            f'        prefix="{escape(prefix)}" suffix="{escape(suffix)}" duration="{escape(duration)}">'
            f'    {escape(prefix)}{escape(from_val)}{escape(suffix)}'
            f'  </span>'
            f'  {title_html}'
            f'</div>'
        )

