"""Original synthesized accompaniment: no samples, recordings or external songs."""

from __future__ import annotations

import hashlib
import wave
from pathlib import Path

import numpy as np

MOODS = {
    "calm": (68, [0, 4, 7, 11]),
    "wonder": (82, [0, 3, 7, 10]),
    "bright": (104, [0, 4, 7, 9]),
    "dramatic": (78, [0, 3, 7, 10]),
}


def mood_for(topic):
    text = topic.casefold()
    if any(w in text for w in ("uzay", "bilim", "gezegen", "keşif", "yıldız", "teknoloji")):
        return "wonder"
    if any(w in text for w in ("doğa", "deniz", "orman", "hayvan", "uyku", "okyanus")):
        return "calm"
    if any(w in text for w in ("spor", "futbol", "oyun", "eğlence", "başarı")):
        return "bright"
    return "dramatic"


def compose_music(topic: str, seconds: float, path: Path, mood: str = "auto"):
    mood = mood_for(topic) if mood == "auto" else mood
    if mood not in MOODS:
        raise ValueError("Geçersiz müzik havası")
    bpm, chord = MOODS[mood]
    rate = 24000
    n = int(min(180, max(1, seconds)) * rate)
    output = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(topic.encode()).digest()[:8], "little"))
    beat = 60 / bpm
    base = int(rng.choice([45, 48, 50, 52]))
    progression = [0, 5, 3, 7]
    for bar, start in enumerate(np.arange(0, seconds, beat * 4)):
        root = base + progression[bar % 4]
        offset = int(start * rate)
        length = min(int(beat * 4 * rate), n - offset)
        if length <= 0:
            break
        t = np.arange(length) / rate
        envelope = np.minimum(t / 0.35, 1) * np.minimum((length / rate - t) / 0.5, 1)
        for note in chord:
            hz = 440 * 2 ** ((root + note - 69) / 12)
            output[offset : offset + length] += (
                (np.sin(2 * np.pi * hz * t) + 0.2 * np.sin(4 * np.pi * hz * t)) * envelope * 0.075
            )
        for step in range(4):
            off = offset + int(step * beat * rate)
            ln = min(int(beat * 0.9 * rate), n - off)
            if ln <= 0:
                continue
            t = np.arange(ln) / rate
            hz = 440 * 2 ** ((root + 12 + int(rng.choice(chord)) - 69) / 12)
            output[off : off + ln] += 0.09 * np.sin(2 * np.pi * hz * t) * np.exp(-t * 6) * np.minimum(t / 0.015, 1)
    fade = min(rate, n // 2)
    output[:fade] *= np.linspace(0, 1, fade)
    output[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes((np.clip(output, -0.9, 0.9) * 32767).astype("<i2").tobytes())
    return mood
