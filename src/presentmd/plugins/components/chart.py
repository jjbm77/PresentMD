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

class ChartComponent:
    @property
    def name(self) -> str: return "chart"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        metadata = {"attrs": attrs}
        for line in content.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                try:
                    metadata[key] = json.loads(val)
                except json.JSONDecodeError:
                    metadata[key] = val
        return metadata
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        attrs = metadata.get("attrs", {})
        title = attrs.get("title", "")
        chart_type = attrs.get("type", "bar")
        
        config = {
            "type": chart_type,
            "labels": metadata.get("labels", []),
            "data": metadata.get("data", []),
            "colors": metadata.get("colors", [])
        }
        
        config_json = escape(json.dumps(config))
        title_html = f'<div class="chart-title">{render_inline(title)}</div>' if title else ""
        
        labels = metadata.get("labels", [])
        data = metadata.get("data", [])
        rows = []
        for label, val in zip(labels, data):
            rows.append(f"<tr><th>{escape(str(label))}</th><td>{escape(str(val))}</td></tr>")
            
        table_html = (
            f'<table class="sr-only" aria-hidden="true">'
            f'  <thead><tr><th>Categoría</th><th>Valor</th></tr></thead>'
            f'  <tbody>{"".join(rows)}</tbody>'
            f'</table>'
        )
        
        return (
            f'<div class="chart-wrapper">'
            f'  {title_html}'
            f'  <div class="chart-container">'
            f'    <canvas class="presentmd-chart" data-chart-config="{config_json}"></canvas>'
            f'  </div>'
            f'  {table_html}'
            f'</div>'
        )

