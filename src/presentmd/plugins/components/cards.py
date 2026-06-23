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

class CardsComponent:
    @property
    def name(self) -> str: return "cards"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "cards": _parse_cards_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        cols = metadata.get("attrs", {}).get("cols", "2")
        animate = metadata.get("attrs", {}).get("animate", "")
        cards_data = metadata.get("cards", [])
        
        cards_html = []
        for card in cards_data:
            attrs = card.get("attrs", {})
            title = attrs.get("title", "")
            icon = attrs.get("icon", "")
            color = attrs.get("color", "1")
            
            body_html = []
            in_list = False
            for line in card.get("content", "").splitlines():
                line = line.strip()
                if not line: continue
                if line.startswith("- ") or line.startswith("* "):
                    if not in_list:
                        body_html.append('<ul class="card-list">')
                        in_list = True
                    body_html.append(f'<li>{render_inline(line[2:].strip())}</li>')
                else:
                    if in_list:
                        body_html.append('</ul>')
                        in_list = False
                    body_html.append(f'<p>{render_inline(line)}</p>')
            if in_list:
                body_html.append('</ul>')
            
            body_str = "\n".join(body_html)
            
            header_html = f'<div class="card-header"><span class="card-icon">{render_inline(icon)}</span><span class="card-title">{render_inline(title)}</span></div>' if title or icon else ''
            cards_html.append(
                f'<div class="card-box" data-color="{color}">'
                f'{header_html}'
                f'<div class="card-content">{body_str}</div>'
                f'</div>'
            )
            
        animate_class = " has-staggered-animations" if animate == "true" else ""
        return f'<div class="cards-grid{animate_class}" data-cols="{cols}">\n{"".join(cards_html)}\n</div>'

