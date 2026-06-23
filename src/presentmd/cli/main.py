import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich import box

from pathlib import Path

app = typer.Typer(
    help="PresentMD: Generador de presentaciones técnicas desde Markdown",
    no_args_is_help=True
)
console = Console()


@app.command()
def build(
    file: str = typer.Argument(..., help="Ruta al archivo Markdown a compilar"),
    format: str = typer.Option("html", "--format", "-f", help="Formato de salida (html, pdf)"),
):
    """
    Construye la presentación a partir de un archivo Markdown.
    """
    from presentmd.parser import parse_presentation
    from presentmd.render import render_presentation

    filepath = Path(file)
    if not filepath.exists():
        console.print(f"[bold red]Error:[/bold red] Archivo no encontrado: {file}")
        raise typer.Exit(code=1)

    message = f"Iniciando compilación de [bold cyan]{file}[/bold cyan] en formato [bold green]{format}[/bold green]..."
    console.print(Panel(message, title="PresentMD Build", border_style="cyan"))

    try:
        presentation = parse_presentation(filepath)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[bold red]Error de parsing:[/bold red] {exc}")
        raise typer.Exit(code=1)

    if format.lower() == "html":
        try:
            html_output = render_presentation(presentation)
            output_dir = filepath.parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Copiar recursos locales al directorio de salida
            import shutil
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.svg", "*.gif"):
                for img_path in filepath.parent.glob(pattern):
                    if img_path.parent == output_dir:
                        continue
                    shutil.copy2(img_path, output_dir / img_path.name)
            
            output_file = output_dir / f"{filepath.stem}.html"
            output_file.write_text(html_output, encoding="utf-8")
            console.print(f"\n[bold green]✓[/bold green] Presentación HTML generada exitosamente en [bold cyan]{output_file}[/bold cyan]\n")
        except Exception as exc:
            console.print(f"[bold red]Error de renderizado:[/bold red] {exc}")
            import traceback
            console.print(traceback.format_exc())
            raise typer.Exit(code=1)
    elif format.lower() == "pdf":
        try:
            # Primero generar el HTML
            html_output = render_presentation(presentation)
            output_dir = filepath.parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Copiar recursos locales al directorio de salida
            import shutil
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.svg", "*.gif"):
                for img_path in filepath.parent.glob(pattern):
                    if img_path.parent == output_dir:
                        continue
                    shutil.copy2(img_path, output_dir / img_path.name)
            
            html_file = output_dir / f"{filepath.stem}.html"
            html_file.write_text(html_output, encoding="utf-8")
            console.print(f"[green]✓[/green] HTML intermedio generado")

            console.print("\n[bold yellow]Aviso sobre Exportación a PDF:[/bold yellow]")
            console.print("PresentMD ya no utiliza Playwright para ahorrar espacio y optimizar el rendimiento.")
            console.print(f"Para generar el PDF, abre el archivo [bold cyan]{html_file}[/bold cyan] en tu navegador (Chrome/Edge/Firefox) y usa [bold white]Ctrl + P[/bold white] o [bold white]Cmd + P[/bold white].")
            console.print("El diseño nativo ha sido preparado específicamente para una impresión pixel-perfect en 16:9.\n")
        except Exception as exc:
            console.print(f"[bold red]Error de renderizado:[/bold red] {exc}")
            import traceback
            console.print(traceback.format_exc())
            raise typer.Exit(code=1)
    else:
        console.print(f"[bold yellow]Advertencia:[/bold yellow] Formato '{format}' no soportado. Usa 'html' o 'pdf'.")
        raise typer.Exit(code=1)


@app.command()
def serve(
    file: str = typer.Argument(..., help="Ruta al archivo Markdown a servir"),
    port: int = typer.Option(8000, "--port", "-p", help="Puerto del servidor HTTP"),
    no_open: bool = typer.Option(False, "--no-open", help="No abrir el navegador automáticamente"),
):
    """
    Levanta un servidor local con recarga en caliente (Live Preview).
    """
    filepath = Path(file)
    if not filepath.exists():
        console.print(f"[bold red]Error:[/bold red] Archivo no encontrado: {file}")
        raise typer.Exit(code=1)

    message = f"Iniciando servidor Live Preview para [bold cyan]{file}[/bold cyan] en [bold green]http://localhost:{port}[/bold green]..."
    console.print(Panel(message, title="PresentMD Serve", border_style="green"))

    from presentmd.serve.server import start_serve

    output_dir = filepath.parent / "output"
    start_serve(
        source_path=filepath,
        output_dir=output_dir,
        port=port,
        open_browser=not no_open,
    )


@app.command()
def debug(
    file: str = typer.Argument(..., help="Ruta al archivo Markdown a inspeccionar"),
):
    """
    Parsea un archivo Markdown y muestra el AST estructurado en la terminal.
    """
    from presentmd.parser import parse_presentation

    filepath = Path(file)
    if not filepath.exists():
        console.print(f"[bold red]Error:[/bold red] Archivo no encontrado: {file}")
        raise typer.Exit(code=1)

    try:
        presentation = parse_presentation(filepath)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[bold red]Error de parsing:[/bold red] {exc}")
        raise typer.Exit(code=1)

    # --- Frontmatter ---
    fm_table = Table(
        title="YAML Frontmatter",
        box=box.ROUNDED,
        title_style="bold magenta",
        border_style="magenta",
    )
    fm_table.add_column("Clave", style="cyan", no_wrap=True)
    fm_table.add_column("Valor", style="green")

    for key, value in presentation.frontmatter.items():
        fm_table.add_row(str(key), str(value))

    console.print()
    console.print(fm_table)

    # --- Resumen ---
    console.print()
    console.print(
        Panel(
            f"[bold]{presentation.title}[/bold]\n"
            f"Tema: [cyan]{presentation.theme}[/cyan] · "
            f"Slides: [green]{presentation.slide_count}[/green] · "
            f"Fuente: [dim]{presentation.source_path}[/dim]",
            title="Presentación Parseada",
            border_style="blue",
        )
    )

    # --- AST por Slide ---
    for slide in presentation.slides:
        slide_label = f"Slide {slide.index}"
        if slide.title:
            slide_label += f" — {slide.title}"
        if slide.layout:
            slide_label += f"  [dim](layout: {slide.layout})[/dim]"

        tree = Tree(f"[bold yellow]{slide_label}[/bold yellow]")

        for el in slide.elements:
            el_label = _format_element(el)
            el_branch = tree.add(el_label)

            # Mostrar metadata relevante
            if el.metadata:
                for key, value in el.metadata.items():
                    if key == "items" and isinstance(value, list):
                        items_branch = el_branch.add("[dim]items:[/dim]")
                        for item in value:
                            items_branch.add(f"[dim]{item}[/dim]")
                    elif key == "highlight_lines" and value:
                        el_branch.add(f"[yellow]highlight: {value}[/yellow]")
                    elif key == "badges" and value:
                        for badge in value:
                            el_branch.add(
                                f"[magenta]badge: [{badge['text']}]"
                                f"{{.{badge['class']}}}[/magenta]"
                            )
                    elif key not in ("level",):
                        el_branch.add(f"[dim]{key}: {value}[/dim]")

        # Notas del presentador
        if slide.speaker_notes:
            tree.add(
                f"[italic dim]📝 Notes: {slide.speaker_notes[:80]}..."
                if len(slide.speaker_notes or "") > 80
                else f"[italic dim]📝 Notes: {slide.speaker_notes}[/italic dim]"
            )

        console.print(tree)
        console.print()


def _format_element(el) -> str:
    """Formatea un SlideElement para visualización en el árbol Rich."""
    type_colors = {
        "heading": "bold cyan",
        "paragraph": "white",
        "code_block": "green",
        "diagram": "bold blue",
        "blockquote": "italic yellow",
        "list": "white",
        "container_kpi-grid": "bold magenta",
        "container_alert": "bold red",
        "container_progress-bars": "bold green",
        "inline_badge": "magenta",
    }

    color = type_colors.get(el.type, "white")
    content_preview = el.content[:70].replace("\n", "↵ ") if el.content else ""

    if el.type == "heading":
        level = el.metadata.get("level", 1)
        return f"[{color}]H{level}: {content_preview}[/{color}]"
    elif el.type == "diagram":
        engine = el.metadata.get("engine", "?")
        return f"[{color}]📊 diagram ({engine}): {content_preview}[/{color}]"
    elif el.type == "code_block":
        lang = el.metadata.get("language", "")
        hl = el.metadata.get("highlight_lines", [])
        hl_str = f" hl={hl}" if hl else ""
        return f"[{color}]💻 code ({lang}{hl_str}): {content_preview}[/{color}]"
    elif el.type.startswith("container_"):
        name = el.type.replace("container_", "")
        attrs = el.metadata.get("attrs", {})
        attrs_str = f" {attrs}" if attrs else ""
        return f"[{color}]📦 :::{name}{attrs_str}[/{color}]"
    elif el.type == "blockquote":
        return f"[{color}]💬 {content_preview}[/{color}]"
    elif el.type == "list":
        list_type = el.metadata.get("list_type", "unordered")
        items = el.metadata.get("items", [])
        return f"[{color}]📋 list ({list_type}, {len(items)} items)[/{color}]"
    else:
        return f"[{color}]{el.type}: {content_preview}[/{color}]"


@app.command()
def doctor():
    """
    Diagnóstico del sistema y dependencias externas de PresentMD.
    """
    import sys
    console.print(Panel("[bold cyan]PresentMD Doctor[/bold cyan] — Diagnóstico del Sistema", border_style="cyan"))
    
    table = Table(box=box.ROUNDED)
    table.add_column("Componente", style="bold cyan")
    table.add_column("Estado / Versión", style="green")
    table.add_column("Detalles / Path", style="dim")
    
    # 1. Python Environment
    table.add_row(
        "Python",
        f"v{sys.version.split()[0]}",
        sys.executable
    )
    
    # 2. Mermaid Engine
    table.add_row(
        "Mermaid JS",
        "[green]✔ Integrado (Cliente)[/green]",
        "Renderizado nativo en navegador"
    )
    
    # 3. D2 Engine (Deprecado)
    table.add_row(
        "D2 CLI",
        "[red]✘ Deprecado / Desactivado[/red]",
        "El soporte para D2 ha sido eliminado por seguridad"
    )
        
    # 4. Playwright
    try:
        from playwright.sync_api import sync_playwright
        table.add_row("Playwright Python SDK", "[green]✔ Instalado[/green]", "-")
        
        # Probar Chromium
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            table.add_row("Playwright Chromium", "[green]✔ Disponible[/green]", "Listo para exportación PDF")
        except Exception as e:
            table.add_row("Playwright Chromium", "[red]✘ No disponible[/red]", "Ejecuta: playwright install chromium")
    except ImportError:
        table.add_row("Playwright Python SDK", "[red]✘ No instalado[/red]", "Instalar: pip install playwright")
        table.add_row("Playwright Chromium", "[red]✘ No disponible[/red]", "Requiere Playwright SDK")
            
    console.print(table)
    console.print()


if __name__ == "__main__":
    app()

