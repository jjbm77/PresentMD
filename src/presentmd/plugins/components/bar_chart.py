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

class BarChartComponent:
    @property
    def name(self) -> str: return "bar-chart"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "items": _parse_pyramid_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        attrs = metadata.get("attrs", {})
        title = attrs.get("title", "")
        is_steps = _is_truthy(attrs.get("steps", False))
        step_attrs = " data-step" if is_steps else ""
        
        bars_html = []
        for idx, item in enumerate(items):
            color = item.get("color", "1")
            value_str = item.get("desc", "0").replace('%', '').strip()
            try:
                height_val = float(value_str)
            except ValueError:
                height_val = 0.0
            
            bars_html.append(
                f'<div class="bar-chart-column"{step_attrs} data-step-idx="{idx}">'
                f'  <div class="bar-value-label">{render_inline(item.get("desc", ""))}</div>'
                f'  <div class="bar-track">'
                f'    <div class="chart-bar-fill" data-color="{escape(color)}" data-bar-height="{height_val}%"></div>'
                f'  </div>'
                f'  <div class="bar-label">{render_inline(item["label"])}</div>'
                f'</div>'
            )
            
        title_html = f'<div class="bar-chart-title">{render_inline(title)}</div>' if title else ""
        return f'<div class="bar-chart-wrapper">\n{title_html}\n<div class="bar-chart-container">\n{"".join(bars_html)}\n</div>\n</div>'

