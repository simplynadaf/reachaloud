#!/usr/bin/env python3
"""
ReachAloud - local smoke test for the ElevenLabs Text-to-Speech API.

Verifies the API key works and that we can synthesize the same emergency alert
in multiple languages using the multilingual model. Writes .mp3 files to
audio/demo/ so we can listen and confirm before building the UI.

Usage:
    source .env && python3 scripts/test_tts.py
"""
import os
import sys
import json
import urllib.request
import urllib.error

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
BASE = "https://api.elevenlabs.io/v1"

# A single, calm, clear emergency alert. Kept short so it reads well aloud
# and does not burn the character quota during testing.
ALERTS = {
    "English": "Flood warning. Water is rising fast in your area. Move to higher ground now. Take your family and leave heavy belongings behind.",
    "Spanish": "Alerta de inundacion. El agua sube rapidamente en su zona. Vaya a un lugar alto ahora. Lleve a su familia y deje atras los objetos pesados.",
    "Hindi": "बाढ़ की चेतावनी। आपके क्षेत्र में पानी तेज़ी से बढ़ रहा है। अभी ऊँची जगह पर चले जाएँ। अपने परिवार को साथ लें और भारी सामान छोड़ दें।",
}

# Sarah - "Mature, Reassuring, Confident" - a default premade voice on the
# account (free-tier accessible). Multilingual v2 handles the target language.
DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
MODEL_ID = "eleven_multilingual_v2"


def req(path, method="GET", data=None, want_bytes=False):
    url = f"{BASE}{path}"
    headers = {"xi-api-key": API_KEY}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read()
            return resp.status, (raw if want_bytes else json.loads(raw.decode()))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    if not API_KEY or not API_KEY.startswith("sk_"):
        print("ERROR: ELEVENLABS_API_KEY missing or not an 'sk_' key.")
        print("Get the real key at https://elevenlabs.io/app/settings/api-keys (starts with sk_).")
        sys.exit(1)

    print("=== 1. Verify key / subscription ===")
    status, sub = req("/user/subscription")
    if status != 200:
        print(f"Auth failed (HTTP {status}): {sub}")
        sys.exit(1)
    print(json.dumps({k: sub.get(k) for k in
                      ["tier", "character_count", "character_limit", "status"]}, indent=2))

    remaining = (sub.get("character_limit") or 0) - (sub.get("character_count") or 0)
    print(f"Characters remaining: {remaining}")

    print("\n=== 2. Synthesize the alert in each language ===")
    os.makedirs("audio/demo", exist_ok=True)
    for lang, text in ALERTS.items():
        payload = {
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        status, out = req(f"/text-to-speech/{DEFAULT_VOICE_ID}",
                          method="POST", data=payload, want_bytes=True)
        if status != 200:
            print(f"  {lang}: FAILED (HTTP {status}) -> {out[:300]}")
            continue
        fn = f"audio/demo/alert_{lang.lower()}.mp3"
        with open(fn, "wb") as f:
            f.write(out)
        print(f"  {lang}: OK -> {fn} ({len(out):,} bytes)")

    print("\nDone. Listen to the files in audio/demo/ to confirm quality.")


if __name__ == "__main__":
    main()
