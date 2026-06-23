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

class ParallelCompareComponent:
    @property
    def name(self) -> str: return "parallel-compare"
    def parse_metadata(self, content: str, attrs: dict) -> dict:
        res = {"attrs": attrs}
        res.update(_parse_parallel_columns(content))
        return res
    def render_html(self, content: str, metadata: dict, render_inline: callable) -> str:
        columns = metadata.get("columns", [])
        center_badge = metadata.get("attrs", {}).get("center-badge", "VS")

        left = columns[0] if len(columns) > 0 else {"header": "", "items": []}
        right = columns[1] if len(columns) > 1 else {"header": "", "items": []}

        def _col_html(col: dict) -> str:
            items = "".join(
                f'<div class="pc-node">{render_inline(i)}</div>' for i in col.get("items", [])
            )
            return (
                f'<div class="pc-col-header">{render_inline(col.get("header", ""))}</div>'
                f'{items}'
            )

        return (
            f'<div class="parallel-container">'
            f'<div class="pc-left">{_col_html(left)}</div>'
            f'<div class="pc-center"><span class="vs-badge">{render_inline(center_badge)}</span></div>'
            f'<div class="pc-right">{_col_html(right)}</div>'
            f'</div>'
        )

