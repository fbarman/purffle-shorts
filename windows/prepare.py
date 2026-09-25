"""Explicit downloads performed only during Windows setup."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

OLLAMA_VERSION = "v0.34.4"
VOICE_REVISION = "aafc6e32416a594460b32413efc49d7fe4ce6d46"
VOICE_REPO = "supertone-oss-archive/supertonic-3"


def download(url: str, dest: Path, digest: str = ""):
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_suffix(dest.suffix + ".part")
    print(f"İndiriliyor: {dest.name}", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response, temp.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)
    if digest:
        h = hashlib.sha256()
        with temp.open("rb") as f:
            while chunk := f.read(1024 * 1024):
                h.update(chunk)
        if h.hexdigest() != digest.removeprefix("sha256:"):
            raise RuntimeError(f"İndirme doğrulanamadı: {dest.name}")
    temp.replace(dest)


def install_ollama():
    root = Path(".tools/ollama")
    if (root / "ollama.exe").is_file():
        return
    url = f"https://api.github.com/repos/ollama/ollama/releases/tags/{OLLAMA_VERSION}"
    request = urllib.request.Request(url, headers={"User-Agent": "PurffleTurkceFactory"})
    with urllib.request.urlopen(request, timeout=30) as r:
        release = json.load(r)
    asset = next(a for a in release["assets"] if a["name"] == "ollama-windows-amd64.zip")
    archive = Path(".tools/ollama-windows-amd64.zip")
    download(asset["browser_download_url"], archive, asset.get("digest") or "")
    with zipfile.ZipFile(archive) as z:
        root.mkdir(parents=True, exist_ok=True)
        for item in z.infolist():
            target = (root / item.filename).resolve()
            if not target.is_relative_to(root.resolve()):
                raise RuntimeError("Paket içinde geçersiz dosya yolu.")
        z.extractall(root)
    print("Ollama hazır.", flush=True)


def install_voice():
    api = f"https://huggingface.co/api/models/{VOICE_REPO}/revision/{VOICE_REVISION}?blobs=true"
    with urllib.request.urlopen(api, timeout=30) as r:
        model = json.load(r)
    for item in model["siblings"]:
        filename = item["rfilename"]
        if filename not in {"LICENSE", "README.md", "config.json"} and not filename.startswith(("onnx/", "voice_styles/")):
            continue
        target = Path("models/supertonic-3") / filename
        if target.is_file() and (not item.get("size") or target.stat().st_size == item["size"]):
            continue
        download(f"https://huggingface.co/{VOICE_REPO}/resolve/{VOICE_REVISION}/{filename}",
                 target, (item.get("lfs") or {}).get("sha256", ""))
    print("Supertonic 3 hazır. Lisans: models/supertonic-3/LICENSE", flush=True)


def configure(voice: str = "supertonic"):
    path = Path("factory.local.json")
    if path.exists():
        print("Mevcut factory.local.json korundu; ses seçimini bu dosyadan değiştirebilirsiniz.")
        return
    data = {"llm_model": "qwen3:4b-instruct", "tts_engine": voice,
            "tts_voice": "M1",
            "tts_model": "models/supertonic-3",
            "resolution": "720x1280", "target_seconds": 40}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for folder in ("media", "music", "output_videos"):
        Path(folder).mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["ollama", "voice", "config"])
    parser.add_argument("--voice", choices=["supertonic"], default="supertonic")
    args = parser.parse_args()
    if args.action == "ollama":
        install_ollama()
    elif args.action == "voice":
        install_voice()
    else:
        configure(args.voice)


if __name__ == "__main__":
    main()
