"""
PresentMD Serve — Servidor HTTP local con hot-reload vía Server-Sent Events (SSE).

Levanta un servidor HTTP que sirve la presentación compilada y vigila cambios
en el archivo fuente para recompilar automáticamente y notificar al browser.
"""
from __future__ import annotations

import os
import threading
import time
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from rich.console import Console

console = Console()

# Lista de clientes SSE activos
_sse_clients: list[threading.Event] = []
_sse_clients_lock = threading.Lock()


class PresentMDHandler(SimpleHTTPRequestHandler):
    """Handler HTTP que sirve archivos estáticos y un endpoint SSE para live reload."""

    def __init__(self, *args, serve_dir: str = ".", **kwargs):
        self._serve_dir = serve_dir
        super().__init__(*args, directory=serve_dir, **kwargs)

    def do_GET(self):
        if self.path == "/events":
            self._handle_sse()
        else:
            super().do_GET()

    def _handle_sse(self):
        """Endpoint SSE que envía 'reload' cuando se detecta un cambio."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Registrar un evento de recarga exclusivo para esta conexión cliente
        client_event = threading.Event()
        with _sse_clients_lock:
            _sse_clients.append(client_event)

        try:
            while True:
                # Esperar hasta que se señale un evento de recarga para este cliente
                if client_event.wait(timeout=1.0):
                    self.wfile.write(b"data: reload\n\n")
                    self.wfile.flush()
                    client_event.clear()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with _sse_clients_lock:
                if client_event in _sse_clients:
                    _sse_clients.remove(client_event)

    def log_message(self, format, *args):
        """Silenciar logs HTTP normales para mantener la consola limpia."""
        pass


def _poll_for_changes(filepath: Path, interval: float = 0.5) -> None:
    """
    Vigila cambios en el archivo fuente usando polling con os.stat().
    Fallback cuando watchdog no está disponible.
    """
    last_mtime = filepath.stat().st_mtime

    while True:
        time.sleep(interval)
        try:
            current_mtime = filepath.stat().st_mtime
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                yield filepath
        except FileNotFoundError:
            pass


def _watch_with_watchdog(filepath: Path):
    """
    Vigila cambios usando watchdog (más eficiente que polling).
    Genera el filepath cada vez que se modifica.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        return None  # Fallback a polling

    change_detected = threading.Event()

    class ChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if Path(event.src_path).resolve() == filepath.resolve():
                change_detected.set()

    observer = Observer()
    observer.schedule(ChangeHandler(), str(filepath.parent), recursive=False)
    observer.start()

    return observer, change_detected


def start_serve(
    source_path: Path,
    output_dir: Path,
    port: int = 8000,
    open_browser: bool = True,
) -> None:
    """
    Inicia el servidor de desarrollo con hot-reload.

    Args:
        source_path: Ruta al archivo .md fuente
        output_dir: Directorio donde se genera el HTML
        port: Puerto del servidor HTTP
        open_browser: Si True, abre el navegador automáticamente
    """
    from presentmd.parser import parse_presentation
    from presentmd.render.engine import render_presentation

    source_path = source_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / source_path.with_suffix(".html").name

    # Compilación inicial
    def _rebuild():
        try:
            # Copiar recursos locales al directorio de salida
            import shutil
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.svg", "*.gif"):
                for img_path in source_path.parent.glob(pattern):
                    if img_path.parent == output_dir:
                        continue
                    shutil.copy2(img_path, output_dir / img_path.name)

            presentation = parse_presentation(source_path)
            html = render_presentation(presentation, live_reload=True)
            output_file.write_text(html, encoding="utf-8")
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Error de compilación:[/bold red] {e}")
            return False

    console.print(f"\n[bold cyan]🔄 Compilación inicial de[/bold cyan] {source_path.name}...")
    if not _rebuild():
        return

    console.print(f"[bold green]✓ Compilación exitosa[/bold green]")

    # Iniciar servidor HTTP
    handler = partial(PresentMDHandler, serve_dir=str(output_dir))
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    url = f"http://localhost:{port}/{output_file.name}"
    console.print(f"\n[bold green]🌐 Servidor iniciado en[/bold green] [link={url}]{url}[/link]")
    console.print("[dim]Presiona Ctrl+C para detener[/dim]\n")

    if open_browser:
        webbrowser.open(url)

    # Configurar watcher
    watchdog_result = _watch_with_watchdog(source_path)

    try:
        if watchdog_result:
            observer, change_detected = watchdog_result
            console.print("[dim]Modo: watchdog (filesystem events)[/dim]")
            try:
                while True:
                    if change_detected.wait(timeout=1.0):
                        change_detected.clear()
                        time.sleep(0.1)  # Debounce
                        ts = time.strftime("%H:%M:%S")
                        console.print(f"[yellow]↻ {ts}[/yellow] Cambio detectado, recompilando...")
                        if _rebuild():
                            console.print(f"[green]✓ {ts}[/green] Recarga enviada al navegador")
                            with _sse_clients_lock:
                                for ev in _sse_clients:
                                    ev.set()
            finally:
                observer.stop()
                observer.join()
        else:
            # Fallback: polling
            console.print("[dim]Modo: polling (watchdog no instalado — instálalo con: pip install watchdog)[/dim]")
            last_mtime = source_path.stat().st_mtime
            while True:
                time.sleep(0.5)
                try:
                    current_mtime = source_path.stat().st_mtime
                    if current_mtime != last_mtime:
                        last_mtime = current_mtime
                        time.sleep(0.1)  # Debounce
                        ts = time.strftime("%H:%M:%S")
                        console.print(f"[yellow]↻ {ts}[/yellow] Cambio detectado, recompilando...")
                        if _rebuild():
                            console.print(f"[green]✓ {ts}[/green] Recarga enviada al navegador")
                            with _sse_clients_lock:
                                for ev in _sse_clients:
                                    ev.set()
                except FileNotFoundError:
                    pass

    except KeyboardInterrupt:
        console.print("\n[bold yellow]⏹ Servidor detenido[/bold yellow]")
        server.shutdown()
