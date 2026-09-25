import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
import requests

from purffle_shorts import llm, tts
from purffle_shorts.factory import demo_script, factory_settings, validate_free_settings
from purffle_shorts.pipeline import Studio
from purffle_shorts.studio import StudioServer, _handler


@pytest.fixture
def factory(tmp_path):
    return factory_settings(tmp_path / "missing.json").with_overrides(
        data_dir=str(tmp_path / "data"), output_dir=str(tmp_path / "videos"),
        media_dir=str(tmp_path / "media"), caption_font="C:/Windows/Fonts/arialbd.ttf")


def test_factory_ignores_paid_shell_settings(monkeypatch, tmp_path):
    for name, value in {"OPENAI_API_KEY": "fake", "LLM_PROVIDER": "openai", "UPLOAD": "true",
                        "VISUAL_SOURCES": "openai-images", "TTS_ENGINE": "elevenlabs",
                        "OLLAMA_HOST": "https://remote.invalid"}.items():
        monkeypatch.setenv(name, value)
    s = factory_settings(tmp_path / "none.json")
    assert s.language == "tr" and s.llm_provider == "ollama"
    assert s.llm_base_url == "http://127.0.0.1:11434/v1"
    assert not s.upload and not s.llm_fallbacks and s.keep_videos
    assert s.visual_sources == ["local"] and s.tts_engine == "supertonic"


@pytest.mark.parametrize("override", [
    {"llm_provider": "openai"}, {"llm_fallbacks": ["openai"]},
    {"llm_base_url": "https://api.openai.com/v1"}, {"llm_base_url": "http://127.0.0.1.evil.invalid/v1"},
    {"llm_base_url": "http://user:password@localhost:11434/v1"},
    {"llm_model": "model:cloud"}, {"visual_sources": ["pollinations"]},
    {"tts_engine": "elevenlabs"}, {"align": "openai"}, {"upload": True},
    {"target_seconds": -1}, {"target_seconds": True}, {"language": "en"},
    {"topic_sources": ["trending"]}, {"tts_voice": "en-US-GuyNeural"},
])
def test_paid_or_remote_settings_rejected(factory, override):
    with pytest.raises(ValueError):
        validate_free_settings(factory.with_overrides(**override))


def test_no_edge_fallback_for_local_voice(factory, monkeypatch, tmp_path):
    calls = []

    def fail(text, out, settings):
        calls.append(settings.tts_engine)
        raise RuntimeError("missing model")

    monkeypatch.setattr(tts, "synthesize", fail)
    with pytest.raises(RuntimeError, match="missing model"):
        Studio(factory.with_overrides(tts_engine="supertonic"))._speak("Türkçe", tmp_path)
    assert calls == ["supertonic"]


def test_unknown_engine_never_silently_uses_edge(factory, tmp_path):
    with pytest.raises(Exception, match="Bilinmeyen"):
        tts.synthesize("Türkçe", tmp_path, factory.with_overrides(free_mode=False, tts_engine="typo"))


def test_native_ollama_uses_schema_and_releases_memory(factory, monkeypatch):
    calls = []

    class Response:
        status_code = 200

        def json(self):
            return {"message": {"content": '{"title":"Türkçe"}'}, "done_reason": "stop"}

    class Session:
        trust_env = True

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def post(self, url, **kwargs):
            assert not self.trust_env
            calls.append((url, kwargs))
            return Response()

    monkeypatch.setattr(requests, "Session", Session)
    provider = llm.build_provider("ollama", factory, factory.llm_model)
    assert isinstance(provider, llm.OllamaProvider)
    schema = {"type": "object"}
    assert "Türkçe" in provider.complete("s", "u", schema=schema)
    assert calls[0][0].endswith("/api/show")
    url, kw = calls[1]
    assert url == "http://127.0.0.1:11434/api/chat"
    assert kw["json"]["format"] == schema and kw["json"]["keep_alive"] == 0
    assert kw["json"]["stream"] is False
    assert kw["allow_redirects"] is False
    assert kw["timeout"][1] >= 600


def test_utf8_demo_and_windows_path(factory, tmp_path, monkeypatch):
    from purffle_shorts.script import load_script
    path = tmp_path / "İçerik üretimi's" / "Türkçe.json"
    demo_script(path)
    script = load_script(path, factory)
    assert script.language == "tr" and "üç" in script.narration
    assert json.loads(path.read_text(encoding="utf-8"))["title"].endswith("Var?")
    calls = []
    monkeypatch.setattr(tts.sys, "platform", "win32")
    monkeypatch.setattr(tts.subprocess, "run", lambda cmd, **kw: calls.append(cmd))
    tts._system("Çığ, ışık, öğüt.", path.parent, factory.with_overrides(tts_voice=""))
    assert "''" in calls[0][-1] and "GetCultureInfo('tr')" in calls[0][-1]


@pytest.fixture
def server(factory, monkeypatch):
    # Hold queued jobs without producing media; exercise the real HTTP handler.
    monkeypatch.setattr(StudioServer, "_worker", lambda self: None)
    app = StudioServer(factory)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _handler(app))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    yield app, base
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=3)


def test_turkish_panel_batch_and_api_guards(server):
    app, base = server
    page = requests.get(base, timeout=5)
    assert 'lang="tr"' in page.text and "Türkçe Video Fabrikası" in page.text
    assert "default-src 'self'" in page.headers["Content-Security-Policy"]
    assert requests.post(base + "/api/make", json={}, timeout=5).status_code == 403
    headers = {"X-Studio-Token": app.token}
    r = requests.post(base + "/api/make", headers=headers,
                      json={"topic": "Işığın hızı", "count": 3, "duration": "20"}, timeout=5)
    assert r.status_code == 200 and len(r.json()["jobs"]) == 3 and app.queue.qsize() == 3
    for body in [{"count": 0}, {"count": 21}, {"count": True}, {"tts": "openai"},
                 {"provider": "openai"}, {"duration": "-5"}, {"source": "reddit"},
                 {"upload": True}, {"offline": True}, [], {"topic": "x" * 501}]:
        r = requests.post(base + "/api/make", headers=headers, json=body, timeout=5)
        assert r.status_code == 400, body
    assert app.queue.qsize() == 3
    assert requests.post(base + "/api/upload/1", headers=headers, json={}, timeout=5).status_code == 403


def test_free_media_and_font_do_not_download(factory, monkeypatch, tmp_path):
    from purffle_shorts import media, overlays

    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected external request")

    monkeypatch.setattr(media, "http", blocked)
    monkeypatch.setattr(overlays, "download", blocked)
    monkeypatch.setattr(overlays, "ensure_font", blocked)
    result = media.Visuals(factory).for_scenes([("ocean", "blue sea", 3)], "deniz", tmp_path)
    assert result[0].source == "generated"
    overlays.resolve_font(factory.with_overrides(caption_font=""))


def test_config_preserves_supported_choices_and_rejects_unknown(tmp_path):
    p = tmp_path / "factory.local.json"
    p.write_text(json.dumps({"resolution": "1080x1920", "tts_engine": "supertonic"}), encoding="utf-8")
    s = factory_settings(p)
    assert s.resolution == (1080, 1920) and s.tts_engine == "supertonic"
    p.write_text('{"upload":true}', encoding="utf-8")
    with pytest.raises(ValueError, match="Bilinmeyen"):
        factory_settings(p)


def test_prepare_does_not_overwrite_user_config(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("prepare", Path(__file__).parents[1] / "windows/prepare.py")
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "factory.local.json"
    p.write_text('{"channel_name":"Benim Kanalım"}', encoding="utf-8")
    before = p.read_bytes()
    prepare.configure("supertonic")
    assert p.read_bytes() == before


def test_turkish_uppercase():
    from purffle_shorts.overlays import display_word, upper_text
    assert upper_text("ilginç ışık", "tr") == "İLGİNÇ IŞIK"
    assert display_word("bilim,", True, "tr") == "BİLİM"
    assert upper_text("indigo", "en") == "INDIGO"


def test_supertonic_inference_is_local_and_turkish(factory, monkeypatch, tmp_path):
    import sys
    import types
    calls = []
    root = tmp_path / "models"
    (root / "onnx").mkdir(parents=True)
    (root / "onnx/tts.json").write_text("{}")
    class FakeTTS:
        def __init__(self, **kw):
            calls.append(kw)

        def get_voice_style(self, voice_name):
            return voice_name

        def synthesize(self, **kw):
            calls.append(kw)
            return [0], [1]

        def save_audio(self, samples, path):
            Path(path).write_bytes(b"test")
    monkeypatch.setitem(sys.modules, "supertonic", types.SimpleNamespace(TTS=FakeTTS))
    monkeypatch.setattr(tts, "_model_cache", {})
    audio, words, voice = tts._supertonic("Türkçe ışık", tmp_path, factory.with_overrides(tts_model=str(root)))
    assert audio.exists() and not words and voice == "M1"
    assert calls[0]["auto_download"] is False
    assert calls[0]["model"] == "supertonic-3"
    assert calls[1]["lang"] == "tr"


def test_remote_alias_rejected_before_generation(factory, monkeypatch):
    calls = []

    class Response:
        status_code = 200
        def json(self):
            return {"remote_model": "model", "remote_host": "https://ollama.com"}

    class Session:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def post(self, url, **kwargs):
            calls.append(url)
            return Response()

    monkeypatch.setattr(requests, "Session", Session)
    provider = llm.build_provider("ollama", factory, factory.llm_model)
    with pytest.raises(llm.LLMConfigError, match="Bulut"):
        provider.complete("system", "user")
    assert len(calls) == 1 and calls[0].endswith("/api/show")


def test_local_media_matches_turkish_filenames(factory, tmp_path):
    from purffle_shorts.media import Visuals
    media = tmp_path / "media"
    media.mkdir()
    (media / "başka.jpg").touch()
    (media / "güneş_ışığı.jpg").touch()
    items = Visuals(factory)._local("güneş ışığı")
    assert items[0].path.name == "güneş_ışığı.jpg"
    assert items[0].extra["overlap"] == 2
