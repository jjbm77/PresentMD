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

class AlertComponent:
    @property
    def name(self) -> str: return "alert"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        return {"attrs": attrs}
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        alert_type = attrs.get("type", "1")
        icon = attrs.get("icon", "ℹ️")
        layout = attrs.get("layout", "vertical")
        size = attrs.get("size", "")
        color_attr = attrs.get("color", alert_type)
        
        size_html = f' data-size="{escape(size)}"' if size else ''
        color_html = f' data-color="{escape(color_attr)}"'
        
        lines = content.strip().splitlines()
        if layout == "horizontal":
            items = []
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    items.append(f'<div class="alert-h-item">{render_inline(line[2:].strip())}</div>')
            rendered_content = f'<div class="alert-horizontal">{"".join(items)}</div>'
            return (
                f'<div class="alert-box layout-horizontal"{size_html}{color_html}>'
                f'<span class="alert-icon">{icon}</span>'
                f'<div class="alert-content">{rendered_content}</div>'
                f'</div>'
            )
        else:
            # Vertical layout: separate the first non-empty line as the title and the rest as the body.
            title_line = ""
            body_lines = []
            found_title = False
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                if not found_title:
                    title_line = line_stripped
                    found_title = True
                else:
                    body_lines.append(line)
            
            title_html = f'<div class="alert-title">{render_inline(title_line)}</div>' if title_line else ""
            body_content = "\n".join(body_lines).strip()
            
            # Support nested block components like typewriter
            if ":::" in body_content or "```" in body_content:
                body_html = render_inline(body_content)
            else:
                body_html_list = []
                in_list = False
                for line in body_lines:
                    line = line.strip()
                    if not line: continue
                    if line.startswith("- ") or line.startswith("* "):
                        if not in_list:
                            body_html_list.append('<ul class="alert-list">')
                            in_list = True
                        body_html_list.append(f'<li>{render_inline(line[2:].strip())}</li>')
                    else:
                        if in_list:
                            body_html_list.append('</ul>')
                            in_list = False
                        body_html_list.append(f'<p>{render_inline(line)}</p>')
                if in_list:
                    body_html_list.append('</ul>')
                body_html = "\n".join(body_html_list)
            
            body_div = f'<div class="alert-body">{body_html}</div>' if body_html else ""
            
            return (
                f'<div class="alert-box layout-vertical"{size_html}{color_html}>'
                f'  <div class="alert-header">'
                f'    <span class="alert-icon">{icon}</span>'
                f'    {title_html}'
                f'  </div>'
                f'  {body_div}'
                f'</div>'
            )

