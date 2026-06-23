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

class TypewriterComponent:
    @property
    def name(self) -> str: return "typewriter"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs, "content": content}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        speed = attrs.get("speed", "50")
        delay = attrs.get("delay", "200")
        size = attrs.get("size", "")
        color = attrs.get("color", "")
        raw_text = metadata.get("content", "").strip()
        
        size_html = f' data-size="{escape(size)}"' if size else ''
        color_html = f' data-color="{escape(color)}"' if color else ''
        
        return (
            f'<div class="typewriter-container"{size_html}{color_html} data-speed="{escape(speed)}" data-delay="{escape(delay)}">'
            f'  <span class="typewriter-text">{escape(raw_text)}</span>'
            f'  <span class="typewriter-cursor">|</span>'
            f'</div>'
        )
