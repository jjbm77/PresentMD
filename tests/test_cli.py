import pytest
from pathlib import Path
from typer.testing import CliRunner
from presentmd.cli.main import app

runner = CliRunner()

def test_build_missing_file():
    result = runner.invoke(app, ["build", "non_existent_file.md"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "Archivo no encontrado" in result.stdout

def test_serve_missing_file():
    result = runner.invoke(app, ["serve", "non_existent_file.md"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "Archivo no encontrado" in result.stdout

def test_build_valid_file(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "---\ntitle: Mi Presentación\ntheme: nexus-blueprint\n---\n# Portada\nAutor: Jaime\n",
        encoding="utf-8"
    )
    result = runner.invoke(app, ["build", str(md_file)])
    assert result.exit_code == 0
    assert "Presentación HTML generada exitosamente" in result.stdout
    
    output_html = tmp_path / "output" / "test.html"
    assert output_html.exists()
    content = output_html.read_text(encoding="utf-8")
    assert "Mi Presentación" in content
    assert "Portada" in content
    assert "Autor: Jaime" in content

def test_build_invalid_format(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "---\ntitle: Mi Presentación\n---\n# Portada\n",
        encoding="utf-8"
    )
    result = runner.invoke(app, ["build", str(md_file), "-f", "txt"])
    assert result.exit_code == 1
    assert "no soportado" in result.stdout
