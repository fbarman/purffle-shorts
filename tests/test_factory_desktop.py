import io
import threading
import time
import wave
from http.server import ThreadingHTTPServer
from types import SimpleNamespace

import pytest
import requests
from PIL import Image

from purffle_shorts.auto_factory import AutoFactory
from purffle_shorts.factory import factory_settings
from purffle_shorts.illustrations import draw_scene
from purffle_shorts.local_music import compose_music
from purffle_shorts.studio import StudioServer, _handler


@pytest.fixture
def panel(tmp_path, monkeypatch):
    monkeypatch.setattr(StudioServer, "_worker", lambda s: None)
    s = factory_settings(tmp_path / "missing").with_overrides(
        data_dir=str(tmp_path / "data"), output_dir=str(tmp_path / "out")
    )
    app = StudioServer(s)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _handler(app))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield app, f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_reference_upload_validation_and_scope(panel):
    app, url = panel
    headers = {"X-Studio-Token": app.token, "X-File-Name": "image.png"}
    stream = io.BytesIO()
    Image.new("RGB", (32, 32), "red").save(stream, format="PNG")
    assert requests.post(url + "/api/reference", data=stream.getvalue()).status_code == 403
    r = requests.post(url + "/api/reference", headers=headers, data=stream.getvalue())
    assert r.status_code == 200
    group = r.json()["media_set"]
    assert len(list((app.upload_root / group).iterdir())) == 1
    headers["X-Media-Set"] = "../escape"
    assert requests.post(url + "/api/reference", headers=headers, data=stream.getvalue()).status_code == 400
    headers.pop("X-Media-Set")
    assert requests.post(url + "/api/reference", headers=headers, data=b"fake image").status_code == 400
    r = requests.post(url + "/api/make", headers=headers, json={"topic": "test", "media_set": group, "music": "off"})
    assert r.status_code == 200 and len(r.json()["jobs"]) == 3
    assert all(j.params["music"] == "off" for j in app.jobs.values())
    assert requests.post(url + "/api/make", headers=headers, json={"count": 4}).status_code == 400


def test_automatic_deduplicates_and_requires_open_panel(tmp_path):
    import queue

    calls = []
    app = SimpleNamespace(
        settings=SimpleNamespace(data_path=tmp_path),
        current=None,
        queue=queue.Queue(),
        submit_many=lambda p, n: calls.append((p, n)),
    )
    auto = AutoFactory(app)
    auto.updated = time.time()
    auto.items = [{"title": "Uzay", "key": "one"}]
    auto.tick()
    assert not calls
    auto.ping()
    auto.tick()
    auto.tick()
    assert len(calls) == 1 and calls[0][1] == 3
    assert "one" in AutoFactory(app).used
    auto.items = [{"title": "Doğa", "key": "two"}]
    auto.set_enabled(False)
    auto.tick()
    assert len(calls) == 1


def test_music_is_local_and_changes_by_topic(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    assert compose_music("uzay", 2, a) == "wonder"
    assert compose_music("orman", 2, b) == "calm"
    assert a.read_bytes() != b.read_bytes()
    with wave.open(str(a)) as f:
        assert f.getnframes() == 48000
    with pytest.raises(ValueError):
        compose_music("x", 1, a, "invalid")


def test_illustrations_reject_untrusted_content(tmp_path):
    with pytest.raises(ValueError):
        draw_scene({"background": "https://remote", "shapes": []}, tmp_path / "x.png")


def test_references_repeat_for_all_scenes_without_ai(tmp_path, monkeypatch):
    from purffle_shorts import illustrations
    from purffle_shorts.media import Visuals

    Image.new("RGB", (32, 32)).save(tmp_path / "a.png")
    monkeypatch.setattr(illustrations, "generate", lambda *a: pytest.fail("No AI with references"))
    s = factory_settings(tmp_path / "missing").with_overrides(media_dir=str(tmp_path))
    result = Visuals(s).for_scenes([("q", "p", 1)] * 4, "topic", tmp_path / "work")
    assert len(result) == 4 and all(m.source == "local" for m in result)
