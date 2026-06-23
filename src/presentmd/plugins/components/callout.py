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

class CalloutComponent:
    @property
    def name(self) -> str: return "callout"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs, "content": content}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        callout_type = attrs.get("type", "1").lower()
        title = attrs.get("title", "")
        icon = attrs.get("icon", "")
        collapsible = _is_truthy(attrs.get("collapsible", "false"))
        
        default_icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "tip": "💡"
        }
        if not icon:
            icon = default_icons.get(callout_type, "ℹ️")
            
        rendered_content = render_inline(metadata.get("content", ""))
        
        if collapsible:
            summary_html = (
                f'<summary class="callout-header">'
                f'  <span class="callout-icon">{escape(icon)}</span>'
                f'  <span class="callout-title">{escape(title or callout_type.capitalize())}</span>'
                f'  <span class="callout-chevron">▼</span>'
                f'</summary>'
            )
            return (
                f'<details class="callout-box" data-color="{escape(callout_type)}">'
                f'  {summary_html}'
                f'  <div class="callout-content">{rendered_content}</div>'
                f'</details>'
            )
        else:
            header_html = ""
            if title:
                header_html = (
                    f'<div class="callout-header">'
                    f'  <span class="callout-icon">{escape(icon)}</span>'
                    f'  <span class="callout-title">{escape(title)}</span>'
                    f'</div>'
                )
            else:
                header_html = f'<div class="callout-header"><span class="callout-icon">{escape(icon)}</span></div>'
                
            return (
                f'<aside class="callout-box" data-color="{escape(callout_type)}">'
                f'  {header_html}'
                f'  <div class="callout-content">{rendered_content}</div>'
                f'</aside>'
            )