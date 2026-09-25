"""Windows Türkçe video fabrikası: local Ollama, free speech, local footage."""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from .config import Settings

DEFAULT_MODEL = "qwen3:4b-instruct"
VOICE_MODEL = "models/supertonic-3"
NICHES = ["şaşırtıcı bilimsel gerçekler", "uzay ve gezegenler", "hayvanların ilginç özellikleri",
          "icatların hikâyeleri", "doğa ve okyanuslar", "gündelik hayatın bilimi"]
CONFIG_FILE = Path("factory.local.json")


def factory_settings(config_file: Path = CONFIG_FILE) -> Settings:
    """Only explicitly supported preferences are read; shell API keys are ignored."""
    data = json.loads(config_file.read_text(encoding="utf-8-sig")) if config_file.exists() else {}
    if not isinstance(data, dict):
        raise ValueError("factory.local.json bir JSON nesnesi olmalıdır.")
    allowed = {"llm_model", "tts_engine", "tts_voice", "tts_model", "target_seconds", "resolution",
               "channel_name", "media_dir", "music_dir", "output_dir", "caption_style", "niches",
               "tts_rate", "video_encoder", "caption_font"}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError("Bilinmeyen fabrika ayarı: " + ", ".join(sorted(unknown)))
    if "resolution" in data:
        from .config import parse_resolution
        if not isinstance(data["resolution"], str) or data["resolution"] not in {"360x640", "720x1280", "1080x1920"}:
            raise ValueError("Çözünürlük: 360x640, 720x1280 veya 1080x1920")
        data["resolution"] = parse_resolution(data["resolution"])
    s = Settings(
        free_mode=True, language="tr", trends_geo="TR", audience="Türkçe konuşan meraklı izleyiciler",
        niches=list(NICHES), llm_provider="ollama", llm_model=DEFAULT_MODEL,
        llm_base_url="http://127.0.0.1:11434/v1", llm_temperature=0.7,
        tts_engine="supertonic", tts_voice="M1", tts_rate="+0%", tts_model=VOICE_MODEL,
        align="none", visual_sources=["local"], resolution=(720, 1280), fps=25,
        transition="fade", caption_style="bold", caption_uppercase=False,
        caption_position="lower", end_cta="Daha fazlası için takip et!",
        channel_name="Türkçe Video Fabrikası", watermark="Yapay zekâ seslendirmesi", upload=False, privacy="private", keep_videos=True,
        timezone="Europe/Istanbul", workers=1, render_workers=2, batch_delay=0,
    ).with_overrides(**data)
    validate_free_settings(s)
    return s


def validate_free_settings(s: Settings, *, source: str | None = None, upload: bool | None = None):
    if not s.free_mode:
        return
    url = urlparse(s.llm_base_url)
    if (s.llm_provider != "ollama" or s.llm_fallbacks or url.scheme != "http"
            or url.hostname not in {"127.0.0.1", "localhost", "::1"}
            or url.username or url.password or url.query or url.fragment
            or url.path.rstrip("/") not in {"", "/v1"}):
        raise ValueError("Fabrika yalnızca bu bilgisayardaki Ollama ile çalışır; ücretli yedek sağlayıcı yoktur.")
    if not isinstance(s.llm_model, str) or not s.llm_model.strip() or "cloud" in s.llm_model.lower():
        raise ValueError("İndirilmiş yerel bir Ollama modeli seçin; bulut modelleri desteklenmez.")
    if s.language != "tr":
        raise ValueError("Fabrika dili Türkçedir.")
    if s.tts_engine not in {"supertonic", "silent"} or s.align != "none":
        raise ValueError("Fabrikada ücretsiz ses motoru ve yerel zamanlama kullanılmalıdır.")
    if s.tts_engine == "supertonic" and any(v.strip() not in {f"{gender}{i}" for gender in ("M", "F") for i in range(1, 6)}
                                           for v in s.tts_voice.split(",") if v.strip()):
        raise ValueError("Supertonic sesi M1–M5 veya F1–F5 olmalıdır.")
    if set(s.visual_sources) - {"local", "generated"}:
        raise ValueError("Fabrika görselleri yalnızca yerel medya veya hareketli arka plandır.")
    if source not in {None, "", "niche", "file"} or set(s.topic_sources) - {"niche", "file"}:
        raise ValueError("Fabrikada yerel konu listesi veya Ollama konu seçimi kullanılır.")
    if s.upload or upload:
        raise ValueError("Fabrika videoları bilgisayara kaydeder; otomatik yükleme kapalıdır.")
    if isinstance(s.target_seconds, bool) or not isinstance(s.target_seconds, int) or not 10 <= s.target_seconds <= 120:
        raise ValueError("Video süresi 10–120 saniye arasında olmalıdır.")
    if s.video_encoder not in {"libx264", "h264_nvenc", "auto"}:
        raise ValueError("Video kodlayıcı: libx264, h264_nvenc veya auto")
    if not isinstance(s.niches, list) or not s.niches or any(not isinstance(n, str) or not n.strip() for n in s.niches):
        raise ValueError("En az bir geçerli Türkçe konu kategorisi gerekli.")


def diagnostics(s: Settings, *, check_ollama: bool = True) -> list[dict]:
    from . import ffmpeg
    from .overlays import SYSTEM_BOLD
    checks = []
    try:
        checks.append({"name": "Video birleştirme", "ok": True, "detail": "FFmpeg " + ffmpeg.version()})
    except Exception as e:
        checks.append({"name": "Video birleştirme", "ok": False, "detail": str(e)})
    font = next((p for p in [s.caption_font, *SYSTEM_BOLD] if p and Path(p).is_file()), None)
    checks.append({"name": "Türkçe yazı tipi", "ok": bool(font), "detail": font or "Yerel yazı tipi bulunamadı."})
    required = ["onnx/tts.json", "onnx/unicode_indexer.json", "onnx/text_encoder.onnx",
                "onnx/duration_predictor.onnx", "onnx/vector_estimator.onnx", "onnx/vocoder.onnx"]
    required += [f"voice_styles/{v.strip() or 'M1'}.json" for v in s.tts_voice.split(",")]
    voice_ok = (importlib.util.find_spec("supertonic") is not None
                and all((Path(s.tts_model) / f).is_file() for f in required))
    checks.append({"name": "Türkçe yerel ses", "ok": voice_ok,
                   "detail": "Supertonic 3 / " + (s.tts_voice or "M1") if voice_ok else
                             "Ses modeli eksik. KURULUM.cmd dosyasını çalıştırın."})
    if check_ollama:
        try:
            import requests
            with requests.Session() as session:
                session.trust_env = False
                root = s.llm_base_url.rstrip("/").removesuffix("/v1")
                r = session.get(root + "/api/tags", timeout=5, allow_redirects=False)
                r.raise_for_status()
                models = r.json().get("models", [])
                found = next((m for m in models if m.get("name") in {s.llm_model, s.llm_model + ":latest"}), None)
                local = bool(found and not found.get("remote_model") and not found.get("remote_host"))
                checks.append({"name": "Ollama modeli", "ok": local, "detail":
                               s.llm_model if local else f"Model yok: ollama pull {s.llm_model}"})
        except Exception:
            checks.append({"name": "Ollama", "ok": False, "detail": "Ollama çalışmıyor. BASLAT.cmd ile başlatın."})
    media = Path(s.media_dir)
    count = sum(1 for p in media.rglob("*") if p.is_file() and p.suffix.lower() in {".mp4", ".png", ".jpg", ".jpeg", ".webp", ".mov", ".mkv", ".webm"}) if media.is_dir() else 0
    checks.append({"name": "Görseller", "ok": True, "detail": f"{count} yerel dosya" if count else
                   "Medya klasörü boş: hareketli renkli arka planlar üretilecek."})
    return checks


def demo_script(path: Path):
    data = {
        "topic": "Ahtapotların üç kalbi", "title": "Ahtapotların Neden Üç Kalbi Var?",
        "hook_text": "Üç kalpli bir canlı!",
        "scenes": [
            {"narration": "Ahtapotların bir değil, üç kalbi vardır.", "search_query": "octopus"},
            {"narration": "İki kalp kanı solungaçlara gönderir. Üçüncü kalp ise vücudun geri kalanına pompalar.", "search_query": "ocean"},
            {"narration": "Kanları, oksijen taşıyan bakır içeren hemosiyanin nedeniyle mavidir.", "search_query": "blue ocean"},
            {"narration": "Denizin altında daha hangi şaşırtıcı canlılar var? Merak etmeye devam et!", "search_query": "coral reef"},
        ],
        "description": "Ahtapotların dolaşım sistemine kısa bir bakış.",
        "hashtags": ["#bilim", "#ahtapot", "#doğa"], "tags": ["ahtapot", "deniz", "bilim"],
        "category": "science", "language": "tr",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Ücretsiz Türkçe video fabrikası")
    parser.add_argument("command", nargs="?", default="studio", choices=["studio", "doctor", "make", "demo"])
    parser.add_argument("--topic", help="Video konusu")
    parser.add_argument("--count", type=int, default=1, help="Üretilecek video sayısı (1–20)")
    parser.add_argument("--duration", type=int)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--config", type=Path, default=CONFIG_FILE)
    args = parser.parse_args(argv)
    try:
        s = factory_settings(args.config)
        if args.duration is not None:
            s = s.with_overrides(target_seconds=args.duration)
        validate_free_settings(s)
        if not 1 <= args.count <= 20:
            raise ValueError("Video sayısı 1–20 arasında olmalıdır.")
        from .cli import setup_logging
        setup_logging(s)
        if args.command == "doctor":
            checks = diagnostics(s)
            for c in checks:
                print(f"{'HAZIR' if c['ok'] else 'EKSİK'} | {c['name']}: {c['detail']}")
            return 0 if all(c["ok"] for c in checks) else 1
        if args.command == "studio":
            from .studio import serve
            serve(s, port=args.port, open_browser=not args.no_browser)
            return 0
        from .pipeline import Studio
        studio = Studio(s)
        if args.command == "demo":
            path = s.data_path / "turkce-demo.json"
            demo_script(path)
            result = studio.make(script_file=path)
            print(result.video if result.ok else result.error)
            return 0 if result.ok else 1
        produced = studio.autopilot(count=args.count, topic=args.topic, upload=False)
        return 0 if produced == args.count else 1
    except (ValueError, OSError) as e:
        logging.getLogger("purffle").error("%s", e)
        print(str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
