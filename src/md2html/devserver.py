"""Development server with live reload for md2html."""

from __future__ import annotations

import argparse
import logging
import queue
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer  # type: ignore[import]

from .cli import resolve_configuration
from .config import AppConfig
from .converter import SiteBuilder, _WatchHandler
from .theme import ThemeManager

LOG_FORMAT = "[%(levelname)s] %(message)s"
LIVE_RELOAD_SNIPPET = (
    "<script>\n"
    "(function () {\n"
    "  var source = new EventSource('/__livereload__');\n"
    "  source.addEventListener('reload', function () {\n"
    "    window.location.reload();\n"
    "  });\n"
    "  source.addEventListener('ping', function () {});\n"
    "  source.onerror = function () {\n"
    "    source.close();\n"
    "    setTimeout(function () { window.location.reload(); }, 2000);\n"
    "  };\n"
    "})();\n"
    "</script>"
)

logger = logging.getLogger(__name__)


class DevServer:
    """Coordinate static builds, file watching, and live reload HTTP serving."""

    def __init__(self, config: AppConfig, *, host: str, port: int, open_browser: bool) -> None:
        self.config = config
        self.host = host
        self.port = port
        self.open_browser = open_browser

        theme_manager = ThemeManager(config.theme_dirs)
        theme = theme_manager.load(config.theme)
        self.builder = SiteBuilder(config, theme)

        self._server: Optional[ThreadingHTTPServer] = None
        self._observer: Optional[Observer] = None
        self._clients: list[queue.Queue[Optional[str]]] = []
        self._clients_lock = threading.Lock()
        self._running = False

    def serve(self) -> None:
        self.builder.build_all()
        self._server = self._create_server()
        self._running = True
        self._start_watchdog()
        self._start_heartbeat()
        if self.open_browser:
            self._open_browser()
        logger.info("Serving %s at http://%s:%d", self.config.output_dir, self.host, self.port)
        self._server.serve_forever()

    def shutdown(self) -> None:
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        self._close_clients()
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def _create_server(self) -> ThreadingHTTPServer:
        handler_class = self._build_handler()
        try:
            return ThreadingHTTPServer((self.host, self.port), handler_class)
        except OSError as exc:  # pragma: no cover - platform specific
            raise RuntimeError(f"Failed to bind to {self.host}:{self.port}: {exc}") from exc

    def _build_handler(self):
        dev_server = self
        output_dir = self.config.output_dir

        class LiveReloadRequestHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(output_dir), **kwargs)

            def handle(self) -> None:  # type: ignore[override]
                try:
                    super().handle()
                except ConnectionResetError:  # pragma: no cover - platform specific
                    logger.debug("Client connection reset during request handling")

            def do_GET(self):  # type: ignore[override]
                if self.path == "/__livereload__":
                    dev_server._handle_livereload(self)
                    return
                super().do_GET()

            def end_headers(self) -> None:  # type: ignore[override]
                if self.path.endswith(".html"):
                    self.send_header("Cache-Control", "no-cache")
                super().end_headers()

            def log_message(self, format: str, *args) -> None:  # type: ignore[override]
                logger.info("HTTP %s %s", self.command, self.path)

        return LiveReloadRequestHandler

    def _handle_livereload(self, handler: SimpleHTTPRequestHandler) -> None:
        handler.send_response(200)
        handler.send_header("Content-Type", "text/event-stream")
        handler.send_header("Cache-Control", "no-cache")
        handler.send_header("Connection", "keep-alive")
        handler.end_headers()

        client_queue = self._register_client()
        client_queue.put(self._format_event("ping", str(time.time())))

        try:
            while True:
                payload = client_queue.get()
                if payload is None:
                    break
                handler.wfile.write(payload.encode("utf-8"))
                handler.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):  # pragma: no cover - platform specific
            logger.debug("Live reload client disconnected")
        finally:
            self._unregister_client(client_queue)

    def _register_client(self) -> queue.Queue[Optional[str]]:
        client_queue: queue.Queue[Optional[str]] = queue.Queue()
        with self._clients_lock:
            self._clients.append(client_queue)
        return client_queue

    def _unregister_client(self, client_queue: queue.Queue[Optional[str]]) -> None:
        with self._clients_lock:
            if client_queue in self._clients:
                self._clients.remove(client_queue)

    def _close_clients(self) -> None:
        with self._clients_lock:
            for client in self._clients:
                client.put(None)
            self._clients.clear()

    def _start_watchdog(self) -> None:
        handler = _WatchHandler(self.builder, on_rebuild=self._on_rebuild)
        observer = Observer()
        observer.schedule(handler, str(self.config.source_dir), recursive=True)
        observer.start()
        self._observer = observer

    def _on_rebuild(self, path: Path) -> None:
        try:
            relative = path.relative_to(self.config.source_dir)
        except ValueError:
            relative = path
        logger.info("Reload triggered by %s", relative)
        self._broadcast("reload", str(time.time()))

    def _start_heartbeat(self) -> None:
        def heartbeat_loop() -> None:
            while self._running:
                self._broadcast("ping", str(time.time()))
                time.sleep(15)

        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()

    def _broadcast(self, event: str, data: str) -> None:
        payload = self._format_event(event, data)
        with self._clients_lock:
            targets = list(self._clients)
        for client in targets:
            client.put(payload)

    @staticmethod
    def _format_event(event: str, data: str) -> str:
        payload_lines = [f"event: {event}"]
        if not data:
            payload_lines.append("data:")
        else:
            for line in data.splitlines() or [""]:
                payload_lines.append(f"data: {line}")
        return "\n".join(payload_lines) + "\n\n"

    def _open_browser(self) -> None:
        url = f"http://{self.host}:{self.port}"
        try:
            webbrowser.open(url, new=2)
        except Exception as exc:  # pragma: no cover - platform specific
            logger.debug("Failed to open browser: %s", exc)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2html-serve",
        description="Run the md2html development server with live reload.",
    )
    parser.add_argument("--config", dest="config", default="md2html.config.yaml", help="Path to configuration YAML file")
    parser.add_argument("--src", dest="source_dir", help="Source directory containing markdown files")
    parser.add_argument("--dst", dest="output_dir", help="Destination directory for generated HTML")
    parser.add_argument("--theme", dest="theme", help="Theme name or path to use")
    parser.add_argument(
        "--theme-dir",
        action="append",
        dest="theme_dirs",
        help="Additional directory to look for custom themes (can be supplied multiple times)",
    )
    parser.add_argument(
        "--no-clean",
        dest="clean_output",
        action="store_false",
        help="Do not clean the output directory before building",
    )
    parser.add_argument(
        "--no-copy-static",
        dest="copy_static",
        action="store_false",
        help="Disable copying non-markdown static assets",
    )
    parser.add_argument("--site-title", dest="site_title", help="Override site title metadata for templates")
    parser.add_argument("--site-description", dest="site_description", help="Override site description metadata for templates")
    parser.add_argument("--host", dest="host", default="127.0.0.1", help="Host interface to bind the development server")
    parser.add_argument("--port", dest="port", type=int, default=8000, help="Port to bind the development server")
    parser.add_argument("--open", dest="open_browser", action="store_true", help="Open the default web browser once the server starts")
    parser.add_argument("--verbose", dest="verbose", action="store_true", help="Enable verbose logging")
    parser.set_defaults(clean_output=None, copy_static=None, watch=False, open_browser=False)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format=LOG_FORMAT)

    try:
        config = resolve_configuration(args)
        config.watch = False
        config.source_dir = config.source_dir.resolve()
        config.output_dir = config.output_dir.resolve()
        if "live_reload_snippet" not in config.extra:
            config.extra["live_reload_snippet"] = LIVE_RELOAD_SNIPPET

        server = DevServer(config, host=args.host, port=args.port, open_browser=args.open_browser)
        try:
            server.serve()
        except KeyboardInterrupt:
            logger.info("Stopping development server")
        finally:
            server.shutdown()
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("md2html serve failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
