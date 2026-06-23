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

class PyramidComponent:
    @property
    def name(self) -> str: return "pyramid"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "items": _parse_pyramid_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        items = metadata.get("items", [])
        total = len(items)
        if total == 0:
            return ""
            
        attrs = metadata.get("attrs", {})
        layout = attrs.get("layout", "pyramid")
        is_steps = _is_truthy(attrs.get("steps", False))
        
        steps_class = " step-hidden" if is_steps else ""
        steps_attr = " data-step" if is_steps else ""
        
        items_html = []
        for idx, item in enumerate(items):
            color = item.get("color", "1")
            icon = item.get("icon", "")
            step_text = item.get("text", "")
            
            icon_html = f'<div class="pmd-pyramid-icon">{render_inline(icon)}</div>' if icon else ""
            text_html = f'<div class="pmd-pyramid-text">{render_inline(step_text)}</div>' if step_text else f'<div class="pmd-pyramid-text">{idx + 1}</div>'
            desc_html = f'<div class="pmd-pyramid-desc">{render_inline(item["desc"])}</div>' if item.get("desc") else ""
            label_html = f'<div class="pmd-pyramid-label">{render_inline(item["label"])}</div>' if item.get("label") else ""
            
            items_html.append(
                f'<div class="pmd-pyramid-item{steps_class}"{steps_attr} data-color="{escape(color)}">'
                f'  {icon_html}'
                f'  {text_html}'
                f'  {label_html}'
                f'  {desc_html}'
                f'</div>'
            )
            
        layout_attr = f' data-layout="{escape(layout)}"'
        steps_container_attr = ' data-steps="true"' if is_steps else ''
        
        return (
            f'<pmd-pyramid{layout_attr}{steps_container_attr}>\n'
            f'  {"".join(items_html)}\n'
            f'</pmd-pyramid>'
        )

