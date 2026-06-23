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

class TabsComponent:
    @property
    def name(self) -> str: return "tabs"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        tabs = []
        current_tab = None
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("===") and stripped.endswith("==="):
                if current_tab:
                    tabs.append(current_tab)
                tab_title = stripped.strip("=").strip()
                current_tab = {"title": tab_title, "content_lines": []}
            elif current_tab is not None:
                current_tab["content_lines"].append(line)
            else:
                current_tab = {"title": "Default", "content_lines": [line]}
        if current_tab:
            tabs.append(current_tab)
            
        for tab in tabs:
            tab["content"] = "\n".join(tab["content_lines"]).strip()
            del tab["content_lines"]
            
        return {"attrs": attrs, "tabs": tabs}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        tabs = metadata.get("tabs", [])
        if not tabs:
            return ""
            
        attrs = metadata.get("attrs", {})
        variant = attrs.get("variant", "")
        variant_html = f' data-variant="{escape(variant)}"' if variant else ''
            
        tab_id_prefix = f"tabs-{uuid.uuid4().hex[:6]}"
        headers = []
        panels = []
        
        for idx, tab in enumerate(tabs):
            tab_id = f"{tab_id_prefix}-tab-{idx}"
            panel_id = f"{tab_id_prefix}-panel-{idx}"
            active_class = " active" if idx == 0 else ""
            aria_selected = "true" if idx == 0 else "false"
            tabindex = "0" if idx == 0 else "-1"
            
            headers.append(
                f'<button class="tab-button{active_class}" id="{tab_id}" role="tab" '
                f'aria-selected="{aria_selected}" aria-controls="{panel_id}" tabindex="{tabindex}">'
                f'{escape(tab["title"])}'
                f'</button>'
            )
            
            panels.append(
                f'<div class="tab-panel{active_class}" id="{panel_id}" role="tabpanel" '
                f'aria-labelledby="{tab_id}" { "hidden" if idx > 0 else "" }>'
                f'{render_inline(tab["content"])}'
                f'</div>'
            )
            
        return (
            f'<div class="tabs-container"{variant_html} id="{tab_id_prefix}-container">'
            f'  <div class="tabs-list" role="tablist" aria-label="Contenido en pestañas">'
            f'    {"".join(headers)}'
            f'  </div>'
            f'  <div class="tabs-panels">'
            f'    {"".join(panels)}'
            f'  </div>'
            f'</div>'
        )

