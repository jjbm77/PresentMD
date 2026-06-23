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

class GridComponent:
    @property
    def name(self) -> str: return "grid"
    
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        cols = []
        current_col = None
        col_re = re.compile(r"^::col(?:umn)?(?:\{(.+?)\})?\s*$")
        
        for line in content.splitlines():
            match = col_re.match(line.strip())
            if match:
                if current_col:
                    cols.append(current_col)
                attrs_str = match.group(1) or ""
                col_attrs = _parse_item_options(attrs_str)
                current_col = {"attrs": col_attrs, "content_lines": []}
            elif current_col is not None:
                current_col["content_lines"].append(line)
            else:
                current_col = {"attrs": {}, "content_lines": [line]}
                
        if current_col:
            cols.append(current_col)
            
        for col in cols:
            col["content"] = "\n".join(col["content_lines"]).strip()
            del col["content_lines"]
            
        return {"attrs": attrs, "columns": cols}

    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        columns = metadata.get("columns", [])
        if not columns:
            return ""
            
        total_cols = len(columns)
        cols_html = []
        for col in columns:
            width = col.get("attrs", {}).get("width", "")
            custom_class = col.get("attrs", {}).get("class", "")
            class_str = f" {custom_class}" if custom_class else ""
            
            fraction = None
            if width:
                if "/" in width:
                    try:
                        num, den = width.split("/", 1)
                        fraction = float(num) / float(den)
                    except ValueError:
                        pass
                elif "%" in width:
                    try:
                        fraction = float(width.replace("%", "").strip()) / 100.0
                    except ValueError:
                        pass
            
            data_attrs = []
            
            if width:
                data_attrs.append(f'data-width="{escape(width)}"')
                if fraction is not None:
                    data_attrs.append(f'data-col-width="{fraction * 100:.3f}%"')
                    data_attrs.append(f'data-col-frac="{fraction:.5f}"')
            
            data_str = f' {" ".join(data_attrs)}' if data_attrs else ""
            
            col_content = col.get("content", "")
            rendered_col = render_inline(col_content)
            
            cols_html.append(
                f'<div class="grid-column{class_str}"{data_str}>'
                f'  {rendered_col}'
                f'</div>'
            )
            
        custom_grid_class = metadata.get("attrs", {}).get("class", "")
        grid_class_str = f" {custom_grid_class}" if custom_grid_class else ""
        
        return (
            f'<div class="grid-container{grid_class_str}" data-grid-cols="{total_cols}">'
            f'  {"".join(cols_html)}'
            f'</div>'
        )
