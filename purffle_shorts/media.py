"""Visual sourcing: per-scene stock footage and photos (Pexels, Pixabay), your own media folder,
and AI-generated images (OpenAI gpt-image-1 / DALL·E, Pollinations). Clips are never reused across
videos, portrait footage is preferred, and a scene always gets *something* (animated gradient)."""

from __future__ import annotations

import base64
import concurrent.futures
import logging
import random
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from .config import Settings
fro…12447 tokens truncated…= None) -> str:
        if self.s.free_mode:
            raise ValueError("Ücretsiz fabrika modunda yükleme kapalı; videoyu önce kontrol edin.")
        rec = self.history.get(rid)
        if not rec or not rec.get("video_path") or not Path(rec["video_path"]).exists():
            log.error("Video #%s has no file to upload", rid)
            return "missing"
        if self.quota_left() <= 0:
            log.warning("Daily upload limit (%d) reached — video #%d queued for tomorrow", self.s.daily_upload_limit, rid)
            self.history.update_video(rid, status="queued")
            if result:
                result.status = "queued"
            return "queued"
        folder = Path(rec["folder"])
        meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8")) if (folder / "metadata.json").exists() else {}
        publish = youtube.next_publish_slot(self.s, self.history.scheduled_times())
        body = youtube.build_body(self.s, rec["title"], rec["description"] or "",
                                  json.loads(rec["tags"] or "[]"), meta.get("category_id", "27"),
                                  meta.get("language", self.s.language), publish)
        try:
            resp = youtube.upload(self.s, Path(rec["video_path"]), body)
        except youtube.QuotaExceeded:
            log.warning("YouTube quota exhausted — video #%d queued", rid)
            self.history.update_video(rid, status="queued")
            if result:
                result.status = "queued"
            return "queued"
        except youtube.NotAuthorized:
            raise
        except Exception as e:
            log.error("Upload of #%d failed: %s", rid, e)
            self.history.update_video(rid, status="failed", error=str(e)[:500])
            if result:
                result.status, result.error = "upload-failed", str(e)
            return "failed"
        vid = resp.get("id")
        status = "scheduled" if publish else "uploaded"
        publish_iso = youtube.to_rfc3339(publish) if publish else None
        fields = dict(status=status, youtube_id=vid, uploaded_at=now_iso(), publish_at=publish_iso, error=None)
        if not self.s.keep_videos:
            Path(rec["video_path"]).unlink(missing_ok=True)
            fields["video_path"] = None
        self.history.update_video(rid, **fields)
        when = f", goes public {publish.strftime('%a %d %b %H:%M %Z')}" if publish else ""
        log.info("%s: https://youtube.com/shorts/%s%s", status.capitalize(), vid, when)
        if result:
            result.status, result.youtube_id, result.publish_at = status, vid, publish_iso
        return status

    def flush_queue(self, include_rendered: bool = False) -> int:
        statuses = ("queued", "rendered") if include_rendered else ("queued",)
        done = 0
        for rec in self.history.pending_uploads(statuses):
            if self.quota_left() <= 0:
                break
            if self.upload_record(rec["id"]) in ("uploaded", "scheduled"):
                done += 1
        return done

    # ------------------------------------------------------------------ autopilot
    def autopilot(self, *, count: int | None = None, once: bool = False, upload: bool | None = None,
                  topic: str | None = None, source: str | None = None) -> int:
        s = self.s
        upload = s.upload if upload is None else upload
        produced, batch, empty_batches = 0, 0, 0
        mode = "upload" if upload else "no-upload"
        _ = self.llm  # fail fast on LLM configuration problems
        log.info("Autopilot started (%s, batch %d, workers %d%s)", mode, s.batch_size, s.workers,
                 f", target {count}" if count else "")
        try:
            while True:
                batch += 1
                if upload:
                    self.flush_queue()
                    if self.quota_left() <= 0 and self.history.pending_uploads():
                        wait = seconds_until_quota_reset()
                        log.info("Upload limit reached and videos are queued; sleeping %.1fh until quota resets",
                                 wait / 3600)
                        time.sleep(wait)
                        continue
                n = s.batch_size if count is None else min(s.batch_size, count - produced)
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(s.workers, n)) as ex:
                    futs = [ex.submit(self.make, topic, source=source, upload=upload) for _ in range(n)]
                    results = [f.result() for f in futs]
                ok = sum(r.ok for r in results)
                produced += ok
                log.info("Batch %d: %d/%d succeeded (total %d)", batch, ok, n, produced)
                empty_batches = empty_batches + 1 if ok == 0 else 0
                if once or (count is not None and produced >= count):
                    break
                if empty_batches >= 3:
                    log.error("Three batches in a row produced nothing — stopping. Check the log above.")
                    break
                if s.batch_delay:
                    log.info("Next batch in %ds", s.batch_delay)
                    time.sleep(s.batch_delay)
        except KeyboardInterrupt:
            log.info("Stopped by user.")
        return produced
