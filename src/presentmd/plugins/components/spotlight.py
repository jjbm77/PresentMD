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

class SpotlightComponent:
    @property
    def name(self) -> str: return "spotlight"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "steps": _parse_spotlight_steps(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        raw_steps = metadata.get("steps", [])
        
        final_steps = []
        targets_html = []
        
        for step in raw_steps:
            selector_or_label = step.get("selector_or_label") or step.get("selector", "")
            desc = step.get("content", "")
            options = step.get("options", {})
            
            if selector_or_label.startswith("#") or selector_or_label.startswith("."):
                final_steps.append({
                    "selector": selector_or_label,
                    "content": desc
                })
            else:
                tgt_id = f"spot-tgt-{uuid.uuid4().hex[:6]}"
                variant = options.get("variant", "box")
                custom_class = options.get("class", "")
                cls = f"spotlight-target-{variant}"
                if custom_class:
                    cls += f" {custom_class}"
                
                rendered_label = render_inline(selector_or_label)
                targets_html.append(f'<div id="{tgt_id}" class="{cls}">{rendered_label}</div>')
                
                final_steps.append({
                    "selector": f"#{tgt_id}",
                    "content": desc
                })
        
        steps_json = escape(json.dumps(final_steps))
        container_html = ""
        if targets_html:
            container_html = f'<div class="spotlight-targets-container">{"".join(targets_html)}</div>'
            
        return f'{container_html}<div class="spotlight-config" data-spotlight-steps="{steps_json}"></div>'

