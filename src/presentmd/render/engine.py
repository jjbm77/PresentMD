"""
Render Engine — Genera el HTML autocontenido final para una presentación.

Orquesta la lectura de templates Jinja2, la inferencia de layouts,
y la inyección de fuentes base64 y estilos CSS.
"""
from __future__ import annotations

import base64
import os
import re
import mimetypes
import subprocess
import tempfile
import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from presentmd.parser.models import Presentation, Slide, SlideElement
from presentmd.render.layout_inference import infer_layout
from presentmd.render.html_builder import render_element
from presentmd.render.toc_builder import build_toc

import logging
logger = logging.getLogger("presentmd.engine")


# ThreadPoolExecutor and diagram_registry imports removed as compiling diagram engines server-side is deprecated.


# Ruta base de los templates de PresentMD
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _slugify(text: str) -> str:
    """Convierte texto a slug URL-friendly."""
    text = text.lower().strip()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n", "ü": "u"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def _get_logo_data_uri(logo_path_str: str, presentation_dir: Path) -> str:
    """Intenta convertir el logo en un Data URI base64 para autocontención."""
    if not logo_path_str:
        return ""
    
    # Intentar relativo a la presentación de forma segura (previniendo path traversal)
    try:
        logo_path = (presentation_dir / logo_path_str).resolve()
        if not logo_path.is_relative_to(presentation_dir.resolve()):
            from rich.console import Console
            Console().print(f"[bold red]⚠ Alerta de Seguridad:[/bold red] Ruta de logo '{logo_path_str}' denegada por Path Traversal.")
            return ""
    except Exception as e:
        logger.warning(f"Error parseando ruta de logo: {e}")
        return ""
        
    if logo_path.exists() and logo_path.is_file():
        try:
            # Validación estricta de MIME y extensión
            valid_exts = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp'}
            if logo_path.suffix.lower() not in valid_exts:
                return ""
                
            mime_type, _ = mimetypes.guess_type(str(logo_path))
            if not mime_type:
                mime_type = "image/png"
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded}"
        except Exception as e:
            logger.warning(f"Error procesando data uri del logo: {e}")
            return ""
    return logo_path_str


def _check_logo_transparency(logo_path: Path) -> bool:
    """Retorna True si el logo es PNG/SVG y tiene canal alpha, False de lo contrario."""
    if logo_path.suffix.lower() == '.svg':
        return True # Asumimos transparente
    if logo_path.suffix.lower() in ('.jpg', '.jpeg'):
        return False # JPG no tiene canal alpha
    if logo_path.suffix.lower() == '.png':
        try:
            with open(logo_path, 'rb') as f:
                sig = f.read(8)
                if sig == b'\x89PNG\r\n\x1a\n':
                    # Leer IHDR chunk
                    f.seek(12)
                    chunk_type = f.read(4)
                    if chunk_type == b'IHDR':
                        # Saltear ancho (4 bytes) y alto (4 bytes) y bit depth (1 byte)
                        f.seek(24)
                        color_type = ord(f.read(1))
                        # 4 (Grey+Alpha) o 6 (RGBA)
                        if color_type in (4, 6):
                            return True
        except Exception as e:
            logger.debug(f"Error comprobando transparencia de logo: {e}")
    return False


def _get_font_base64() -> str:
    """Lee la fuente DM Mono y genera la regla @font-face en base64."""
    font_path = TEMPLATES_DIR / "fonts" / "DMMono-Regular.woff2"
    if not font_path.exists():
        return ""
    with open(font_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"""
    @font-face {{
      font-family: 'DM Mono';
      src: url('data:font/woff2;base64,{encoded}') format('woff2');
      font-weight: 400;
      font-style: normal;
    }}
    """


from presentmd.render.theme_manager import ThemeManager

def _get_theme_css(theme_name: str) -> str:
    """Carga el CSS del tema indicado usando ThemeManager."""
    manager = ThemeManager(TEMPLATES_DIR / "themes")
    return manager.get_theme_css(theme_name)


def render_slide_to_html(
    slide: Slide, env: Environment, presentation: Presentation, logo_data_uri: str
) -> str:
    """Convierte un Slide individual en su representación HTML usando su template de layout."""
    layout = infer_layout(slide)
    
    is_annex = False
    if layout == "annex":
        layout_template = "scrollable"
        is_annex = True
    else:
        layout_template = layout.replace("-", "_")
        
    # Check if this slide has only a diagram (and headings)
    non_heading_non_trivial = [
        el for el in slide.elements 
        if el.type not in ("heading",) and el.content.strip()
    ]
    is_diagram_only = len(non_heading_non_trivial) == 1 and non_heading_non_trivial[0].type == "diagram"
    
    # Determinar el ID del slide
    slide_id = None
    for el in slide.elements:
        if el.type == "heading" and "anchor_id" in el.metadata:
            slide_id = el.metadata["anchor_id"]
            break
    if not slide_id:
        if slide.title:
            slide_id = _slugify(slide.title)
        else:
            slide_id = f"slide-{slide.index}"
            
    # Separar headers y contenido de body
    eyebrow = presentation.frontmatter.get("eyebrow", "") or presentation.frontmatter.get("section", "")
    heading = slide.title or ""
    subtitle = ""
    
    # Extraer el primer H2 como subtítulo si existe en layout-standard
    body_elements = []
    found_subtitle = False
    
    left_elements = []
    right_elements = []
    in_right_column = False
    
    for el in slide.elements:
        if el.type == "heading" and el.metadata.get("level") == 2 and not found_subtitle:
            if el.content != slide.title:
                subtitle = el.content
            found_subtitle = True
            continue
        elif el.type == "heading" and el.metadata.get("level") == 1:
            # H1 ya está mapeado al header o slide.title
            pass
        elif el.type == "paragraph" and el.content.strip() == "|||":
            in_right_column = True
        else:
            rendered = render_element(el)
            body_elements.append(rendered)
            if in_right_column:
                right_elements.append(rendered)
            else:
                left_elements.append(rendered)
            
    # Renderizar todos los elementos para layout-title
    all_elements_html = [render_element(el) for el in slide.elements]

    # Warn if there's potential overflow in standard layout
    total_content_len = sum(len(el.content) for el in slide.elements)
    if layout == "standard" and (len(body_elements) > 15 or total_content_len > 1200):
        from rich.console import Console
        console = Console()
        console.print(
            f"\n[bold yellow]⚠ ADVERTENCIA DE DESBORDAMIENTO:[/bold yellow] La diapositiva {slide.index} ('{heading}') "
            f"tiene {len(body_elements)} elementos y {total_content_len} caracteres en el layout standard. "
            f"Esto podría causar desbordamiento visual. Se ha transformado automáticamente en layout 'scrollable'.\n"
        )
        layout = "scrollable"
        layout_template = "scrollable"

    # Cargar template correspondiente
    template_name = f"layouts/{layout_template}.html.j2"
    try:
        tmpl = env.get_template(template_name)
    except Exception:
        # Fallback a standard si no existe
        tmpl = env.get_template("layouts/standard.html.j2")
        
    # Convert bg_image source to base64 data URI for offline/self-contained portability
    bg_image = None
    if slide.bg_image:
        bg_image = dict(slide.bg_image)
        if "src" in bg_image:
            presentation_dir = Path(presentation.source_path).parent if presentation.source_path else Path.cwd()
            bg_image["src"] = _get_logo_data_uri(bg_image["src"], presentation_dir)

    context = {
        "index": slide.index,
        "slide_id": slide_id,
        "is_annex": is_annex,
        "is_diagram_only": is_diagram_only,
        "eyebrow": eyebrow,
        "heading": heading,
        "subtitle": subtitle,
        "body_elements": body_elements,
        "left_elements": left_elements,
        "right_elements": right_elements,
        "center_badge": presentation.frontmatter.get("center_badge", "VS"),
        "elements": all_elements_html,
        "logo": logo_data_uri,
        "logo_position": presentation.frontmatter.get("logo_position", "top"),
        "footer_text": presentation.frontmatter.get("footer", ""),
        "bg_image": bg_image,
        "speaker_notes": slide.speaker_notes,
    }
    
    return tmpl.render(context)


def _render_closing_slide(
    env: Environment, presentation: Presentation,
    logo_data_uri: str, slide_index: int
) -> str:
    """Genera el HTML del slide de cierre automático."""
    tmpl = env.get_template("layouts/title.html.j2")

    closing_message = presentation.frontmatter.get("closing_message", "")
    closing_subtitle = presentation.frontmatter.get("closing_subtitle", "")

    elements_html = []
    if closing_message:
        elements_html.append(f'<h1 class="slide-h1">{closing_message}</h1>')
        if closing_subtitle:
            elements_html.append(f'<p>{closing_subtitle}</p>')
    else:
        # Repetir la portada: título de la presentación
        title = presentation.frontmatter.get("title", presentation.title or "")
        elements_html.append(f'<h1 class="slide-h1">{title}</h1>')
        # Intentar extraer el subtítulo del primer slide
        if presentation.slides:
            first_slide = presentation.slides[0]
            for el in first_slide.elements:
                if el.type == "paragraph" and el.content.strip():
                    elements_html.append(f'<p>{el.content}</p>')
                    break

    context = {
        "index": slide_index,
        "slide_id": "closing",
        "is_annex": False,
        "is_diagram_only": False,
        "elements": elements_html,
        "logo": logo_data_uri,
        "logo_position": presentation.frontmatter.get("logo_position", "top"),
        "footer_text": presentation.frontmatter.get("footer", ""),
    }

    return tmpl.render(context)


def render_presentation(presentation: Presentation, live_reload: bool = False) -> str:
    """
    Renderiza la presentación completa en un HTML autocontenido.
    """
    # Detectar presencia de Mermaid y charts
    has_mermaid = False
    has_charts = False
    for slide in presentation.slides:
        for el in slide.elements:
            if el.type == "diagram":
                engine_name = el.metadata.get("engine", "").lower()
                if engine_name == "mermaid":
                    has_mermaid = True
            elif el.type == "container_chart":
                has_charts = True

    loader = FileSystemLoader(str(TEMPLATES_DIR))
    env = Environment(loader=loader, autoescape=True)
    
    # Preparar el directorio base de la presentación para buscar el logo
    presentation_dir = Path(presentation.source_path).parent if presentation.source_path else Path.cwd()
    logo_path_str = presentation.frontmatter.get("logo", "")
    logo_data_uri = _get_logo_data_uri(logo_path_str, presentation_dir)
    
    if logo_path_str:
        logo_path = presentation_dir / logo_path_str
        if not logo_path.exists():
            logo_path = Path(logo_path_str)
        if logo_path.exists() and logo_path.is_file():
            if not _check_logo_transparency(logo_path):
                from rich.console import Console
                console = Console()
                console.print("\n[bold yellow]⚠ ADVERTENCIA DE LOGO:[/bold yellow] El logo detectado no parece ser transparente.")
                console.print("[dim]Se recomienda encarecidamente utilizar una imagen con fondo transparente (PNG con canal alpha o SVG) para que se integre correctamente con el diseño y colores del tema.[/dim]\n")
    
    # Separar slides de contenido y anexos
    non_annex_slides = []
    annex_slides = []
    for slide in presentation.slides:
        if infer_layout(slide) == "annex":
            annex_slides.append(slide)
        else:
            non_annex_slides.append(slide)
    
    slides_html = []
    current_index = 0
    
    # Renderizar contenido normal
    for slide in non_annex_slides:
        slide.index = current_index
        html = render_slide_to_html(slide, env, presentation, logo_data_uri)
        slides_html.append(html)
        current_index += 1
        
    # Generar slide de cierre automático
    closing_html = _render_closing_slide(
        env, presentation, logo_data_uri,
        slide_index=current_index
    )
    slides_html.append(closing_html)
    current_index += 1
    
    # Renderizar anexos actualizando sus índices
    for slide in annex_slides:
        slide.index = current_index
        html = render_slide_to_html(slide, env, presentation, logo_data_uri)
        slides_html.append(html)
        current_index += 1
    
    # Contar total de diapositivas que NO son anexos (contenido + cierre)
    non_annex_count = len(non_annex_slides) + 1  # +1 por el slide de cierre
    
    # Generar Table of Contents
    toc = build_toc(presentation)
    
    # Obtener CSS del tema
    theme_name = presentation.frontmatter.get("theme", "nexus-blueprint")
    theme_css = _get_theme_css(theme_name)
    
    # Si hay accent color customizado, inyectarlo en las variables root
    accent = presentation.frontmatter.get("accent")
    if accent:
        theme_css = f":root {{ --accent-primary: {accent}; }}\n" + theme_css
        
    font_face = _get_font_base64()
    
    # Opciones YAML (por defecto desactivadas)
    nav_arrows = presentation.frontmatter.get("nav_arrows", False)
    slide_number = presentation.frontmatter.get("slide_number", False)
    animations = presentation.frontmatter.get("animations", False)
    
    # Extraer meta description para SEO/OpenGraph
    og_description = ""
    if presentation.slides:
        for el in presentation.slides[0].elements:
            if el.type == "paragraph" and el.content.strip():
                og_description = el.content.strip()
                break
                
    # Renderizar shell principal
    base_tmpl = env.get_template("base.html.j2")
    html_output = base_tmpl.render(
        title=presentation.frontmatter.get("title", "Presentación"),
        font_face=font_face,
        theme_css=theme_css,
        theme_name=theme_name,
        logo=logo_data_uri,
        toc=toc,
        slides=slides_html,
        nav_arrows=nav_arrows,
        slide_number=slide_number,
        animations=animations,
        total_non_annex_count=non_annex_count,
        live_reload=live_reload,
        og_description=og_description,
        has_mermaid=has_mermaid,
        has_charts=has_charts,
    )
    
    # Minificación ligera y segura (eliminar indentación inútil fuera de tags pre/code)
    try:
        # Se elimina el espacio al inicio de las líneas para achicar el payload final.
        # Solo se aplica si no estamos dentro de un pre/script (heurística simple)
        minified_lines = []
        in_pre = False
        in_script = False
        for line in html_output.splitlines():
            if "<pre" in line: in_pre = True
            if "<script" in line: in_script = True
            if "</pre" in line: in_pre = False
            if "</script" in line: in_script = False
            
            if not in_pre and not in_script:
                cleaned = line.strip()
                if cleaned:
                    minified_lines.append(cleaned)
            else:
                minified_lines.append(line)
        return "\n".join(minified_lines)
    except Exception:
        return html_output
