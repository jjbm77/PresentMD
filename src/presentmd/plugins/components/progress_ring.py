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

class ProgressRingComponent:
    @property
    def name(self) -> str: return "progress-ring"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs, "content": content}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        value = float(attrs.get("value", "0"))
        size = int(attrs.get("size", "120"))
        stroke = int(attrs.get("stroke", "8"))
        color = attrs.get("color", "1")
        title = attrs.get("title", "")
        
        center = size / 2
        radius = (size - stroke) / 2
        circumference = 2 * 3.14159265 * radius
        
        title_html = f'<div class="progress-ring-title">{render_inline(title)}</div>' if title else ""
        
        return (
            f'<div class="progress-ring-wrapper">'
            f'  <div class="progress-ring-container" data-ring-size="{size}">'
            f'    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'      <circle cx="{center}" cy="{center}" r="{radius}" stroke-width="{stroke}" fill="transparent" class="progress-ring-bg"></circle>'
            f'      <circle cx="{center}" cy="{center}" r="{radius}" stroke-width="{stroke}" fill="transparent" class="progress-ring-fill" data-color="{escape(color)}" '
            f'              stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{circumference:.2f}" data-value="{value}" data-circumference="{circumference:.2f}" '
            f'              transform="rotate(-90 {center} {center})"></circle>'
            f'    </svg>'
            f'    <div class="progress-ring-percentage">{value:.0f}%</div>'
            f'  </div>'
            f'  {title_html}'
            f'</div>'
        )
