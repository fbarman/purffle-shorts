"""Public Turkish trend feed and local, bounded automatic production queue."""

from __future__ import annotations

import json
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

FEED = "https://trends.google.com/trending/rss?geo=TR"


class AutoFactory:
    def __init__(self, app):
        self.app = app
        self.enabled = True
        self.last_seen = 0.0
        self.updated = 0.0
        self.error = ""
        self.items = []
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.path = Path(app.settings.data_path) / "factory-trends.json"
        try:
            self.used = set(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            self.used = set()
        self.thread = None

    def start(self):
        if not self.thread:
            self.thread = threading.Thread(target=self.run, daemon=True, name="factory-trends")
            self.thread.start()

    def snapshot(self):
        with self.lock:
            return {
                "enabled": self.enabled,
                "active": time.time() - self.last_seen < 90,
                "updated": self.updated,
                "error": self.error,
                "items": [dict(x, used=x["key"] in self.used) for x in self.items],
                "source": FEED,
            }

    def ping(self):
        with self.lock:
            self.last_seen = time.time()

    def set_enabled(self, value):
        if not isinstance(value, bool):
            raise ValueError("Geçersiz otomatik üretim ayarı")
        with self.lock:
            self.enabled = value

    def refresh(self):
        with requests.get(FEED, timeout=(5, 20), stream=True) as r:
            r.raise_for_status()
            raw = b""
            for chunk in r.iter_content(16384):
                raw += chunk
                if len(raw) > 2_000_000:
                    raise ValueError("Konu kaynağı çok büyük")
        root = ET.fromstring(raw)
        items = []
        for item in root.findall("./channel/item")[:25]:
            title = (item.findtext("title") or "").strip()[:200]
            date = (item.findtext("pubDate") or "")[:100]
            traffic = next((n.text for n in item if n.tag.endswith("approx_traffic")), "")
            if title:
                items.append({"title": title, "traffic": traffic or "", "date": date, "key": date + ":" + title})
        if not items:
            raise ValueError("Güncel popüler konu listesi boş")
        with self.lock:
            self.items = items
            self.updated = time.time()
            self.error = ""

    def tick(self):
        state = self.snapshot()
        if not state["active"]:
            return
        if time.time() - state["updated"] > 900:
            try:
                self.refresh()
            except Exception as e:
                with self.lock:
                    self.error = "Popüler konular alınamadı: " + str(e)
                return
        with self.lock:
            if not self.enabled or self.error:
                return
            if self.app.current or not self.app.queue.empty():
                return
            if self.items and all(i["key"] in self.used for i in self.items):
                return
            item = next((i for i in self.items if i["key"] not in self.used), None)
            if not item:
                return
            import shutil

            if shutil.disk_usage(Path.cwd()).free < 3 * 1024**3:
                self.error = "Disk alanı az; otomatik üretim durduruldu."
                self.enabled = False
                return
            self.app.submit_many(
                {
                    "topic": item["title"],
                    "style": "explainer",
                    "automatic": True,
                    "media_set": "",
                    "trend_key": item["key"],
                },
                3,
            )
            self.used.add(item["key"])
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix(".tmp")
            temp.write_text(json.dumps(sorted(self.used)[-2000:], ensure_ascii=False), encoding="utf-8")
            temp.replace(self.path)

    def run(self):
        while not self.stop.is_set():
            try:
                self.tick()
            except Exception as e:
                with self.lock:
                    self.error = str(e)
            self.stop.wait(15)
