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

class TimelineComponent:
    @property
    def name(self) -> str: return "timeline"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "phases": _parse_timeline_phases(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        phases = metadata.get("phases", [])
        parts = []
        for idx, phase in enumerate(phases):
            items_html = "".join(
                f'<div class="tl-desc">• {render_inline(i)}</div>' for i in phase.get("items", [])
            )
            deliverable = ""
            if phase.get("deliverable"):
                deliverable = f'<div class="tl-deliverable">→ {render_inline(phase["deliverable"])}</div>'

            parts.append(
                f'<div class="timeline-phase">'
                f'<span class="tl-badge">{render_inline(phase.get("badge", ""))}</span>'
                f'<div class="tl-title">{render_inline(phase.get("title", ""))}</div>'
                f'{items_html}{deliverable}'
                f'</div>'
            )
            if idx < len(phases) - 1:
                parts.append('<div class="timeline-arrow">→</div>')

        return f'<div class="timeline">\n{"".join(parts)}\n</div>'

