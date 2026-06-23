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

class HotspotsComponent:
    @property
    def name(self) -> str: return "hotspots"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {
            "attrs": attrs,
            "image": attrs.get("image", ""),
            "pins": _parse_hotspots_items(content)
        }
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        image = escape(metadata.get("image", ""))
        pins = metadata.get("pins", [])
        pins_html = []
        for idx, pin in enumerate(pins):
            x = escape(pin.get("x", "0%"))
            y = escape(pin.get("y", "0%"))
            desc = render_inline(pin.get("content", ""))
            pins_html.append(
                f'<div class="hotspot-pin" data-left="{x}" data-top="{y}" data-index="{idx}">'
                f'  <div class="pin-marker"><span class="pin-number">{idx + 1}</span></div>'
                f'  <div class="pin-tooltip">'
                f'    <div class="pin-tooltip-arrow"></div>'
                f'    <div class="pin-tooltip-content">{desc}</div>'
                f'  </div>'
                f'</div>'
            )
        return (
            f'<div class="hotspots-container">'
            f'  <img src="{image}" class="hotspots-image" />'
            f'  <div class="hotspots-pins-layer">'
            f'    {"".join(pins_html)}'
            f'  </div>'
            f'</div>'
        )

