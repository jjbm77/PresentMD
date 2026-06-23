"""
Tests unitarios e integrados para el módulo de exportación PDF de PresentMD.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest

from presentmd.export.pdf_exporter import export_to_pdf


def test_export_to_pdf_generates_file(tmp_path):
    # Crear un archivo HTML de prueba mínimo
    html_file = tmp_path / "test_presentation.html"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: sans-serif; background: white; margin: 0; }
            .slide { width: 1280px; height: 720px; display: flex; align-items: center; justify-content: center; page-break-after: always; }
        </style>
    </head>
    <body>
        <div class="slide"><h1>Slide 1</h1></div>
        <div class="slide"><h1>Slide 2</h1></div>
    </body>
    </html>
    """
    html_file.write_text(html_content, encoding="utf-8")

    pdf_file = tmp_path / "output_presentation.pdf"

    # Exportar a PDF
    export_to_pdf(html_file, pdf_file)

    # Verificar que el archivo PDF existe y tiene tamaño
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0
