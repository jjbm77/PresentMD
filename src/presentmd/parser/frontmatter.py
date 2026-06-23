"""
Extractor de YAML Frontmatter.

Separa el bloque YAML delimitado por '---' al inicio del documento
del contenido Markdown restante.
"""
from __future__ import annotations

import re

import yaml


# Regex: captura el bloque YAML entre los primeros dos '---'
# Flags: DOTALL para que '.' matchee saltos de línea
_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n?",
    re.DOTALL,
)


def extract_frontmatter(raw_text: str) -> tuple[dict, str]:
    """
    Extrae el frontmatter YAML y retorna el contenido restante.

    Args:
        raw_text: Contenido completo del archivo .md.

    Returns:
        Tupla (frontmatter_dict, remaining_content).
        Si no hay frontmatter, retorna ({}, raw_text).

    Raises:
        ValueError: Si el YAML es inválido o malformado.
    """
    match = _FRONTMATTER_RE.match(raw_text)
    if not match:
        return {}, raw_text

    yaml_block = match.group(1)
    remaining = raw_text[match.end():]

    try:
        frontmatter = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parseando YAML frontmatter: {exc}") from exc

    # safe_load puede retornar None si el bloque está vacío
    if frontmatter is None:
        frontmatter = {}

    if not isinstance(frontmatter, dict):
        raise ValueError(
            f"El frontmatter debe ser un mapping YAML (dict), "
            f"se encontró: {type(frontmatter).__name__}"
        )

    return frontmatter, remaining
