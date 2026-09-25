"""Portable Windows application. All models/runtimes live beside the executable."""

from __future__ import annotations

import ctypes
import logging
import os
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import requests


def main():
    root = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    os.chdir(root)
    (root / "data").mkdir(exist_ok=True)
    logging.basicConfig(
        filename=root / "data" / "factory.log", level=logging.INFO, encoding="utf-8", format="%(asctime)s %(message)s"
    )
    os.environ["OLLAMA_NO_CLOUD"] = "1"
    os.environ["OLLAMA_MODELS"] = str(root / "models" / "ollama")
    os.environ["OLLAMA_HOST"] = "127.0.0.1:11436"
    os.environ["OLLAMA_NUM_PARALLEL"] = "1"
    # Fixed bundled FFmpeg prevents accidental dependency on a system installation.
    import imageio_ffmpeg

    from purffle_shorts import ffmpeg
    from purffle_shorts.factory import factory_settings
    from purffle_shorts.studio import StudioServer, _handler

    os.environ["FFMPEG_BINARY"] = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg.ffmpeg_bin.cache_clear()
    if "--doctor" in sys.argv:
        from purffle_shorts.factory import diagnostics

        data = diagnostics(factory_settings(), check_ollama=False)
        import json

        (root / "data" / "portable-check.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return
    ollama = None
    server = None
    app = None
    browser = None
    session = requests.Session()
    session.trust_env = False
    try:
        try:
            session.get("http://127.0.0.1:11436/api/tags", timeout=2).raise_for_status()
        except requests.RequestException:
            log = (root / "data" / "ollama.log").open("ab")
            ollama = subprocess.Popen(
                [str(root / "ollama" / "ollama.exe"), "serve"],
                stdout=log,
                stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        for _ in range(45):
            try:
                session.get("http://127.0.0.1:11436/api/tags", timeout=2).raise_for_status()
                break
            except requests.RequestException:
                time.sleep(1)
        else:
            raise RuntimeError("Yerel model motoru açılamadı. data/ollama.log dosyasını inceleyin.")
        settings = factory_settings().with_overrides(llm_base_url="http://127.0.0.1:11436/v1")
        app = StudioServer(settings)
        server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(app))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        app.auto.start()
        url = f"http://127.0.0.1:{server.server_port}/"
        (root / "data" / "panel-url.txt").write_text(url, encoding="utf-8")
        if "--smoke" in sys.argv:
            assert session.get(url, timeout=5).status_code == 200
            (root / "data" / "smoke-ok.txt").write_text("Portable server OK", encoding="utf-8")
            return
        edge = next(
            (
                p
                for p in [
                    Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
                    Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
                ]
                if p.is_file()
            ),
            None,
        )
        if not edge:
            raise RuntimeError("Windows Microsoft Edge bulunamadı.")
        browser = subprocess.Popen(
            [
                str(edge),
                f"--app={url}",
                f"--user-data-dir={root / 'data' / 'app-window'}",
                "--no-first-run",
                "--disable-extensions",
            ],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        browser.wait()
    except Exception as e:
        logging.exception("Factory Shorts")
        if "--smoke" not in sys.argv and "--doctor" not in sys.argv:
            ctypes.windll.user32.MessageBoxW(0, str(e), "Factory Shorts", 0x10)
        raise
    finally:
        if app:
            app.auto.stop.set()
            app.auto.set_enabled(False)
        if server:
            server.shutdown()
            server.server_close()
        if ollama:
            ollama.terminate()
        session.close()


if __name__ == "__main__":
    main()
