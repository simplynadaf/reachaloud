#!/usr/bin/env python3
"""
ReachAloud - generate the static demo clip set.

Pre-renders one emergency alert into several languages ONCE and saves them as
static .mp3 files under audio/demo/, plus a manifest.json the frontend reads.
This is the "judge-proof" demo path: the site plays these static files with
zero live API calls and zero quota usage.

Usage:
    source .env && python3 scripts/generate_demo.py
"""
import os
import sys
import json
import hashlib
import urllib.request
import urllib.error

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
BASE = "https://api.elevenlabs.io/v1"
MODEL_ID = "eleven_multilingual_v2"
# Sarah - mature, reassuring, confident. A default premade voice (free-tier OK).
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
OUT_DIR = "audio/demo"

# One flood alert, translated. Kept short and calm - clear instructions that
# read well aloud and are cheap on the character quota.
# Language set centers South Asia (the Nepal-Tibet flood context) plus the
# widely-spoken languages a mixed trekking/border crowd would need.
# lang code -> (English name, native label, text)
DEMO = {
    "en": ("English", "English",
           "Flood warning. Water is rising fast in your area. Move to higher ground now. Take your family with you and leave heavy belongings behind."),
    "ne": ("Nepali", "नेपाली",
           "बाढीको चेतावनी। तपाईंको क्षेत्रमा पानी छिटो बढ्दै छ। अहिले नै अग्लो ठाउँमा जानुहोस्। परिवारलाई सँगै लैजानुहोस् र भारी सामान छोडिदिनुहोस्।"),
    "mr": ("Marathi", "मराठी",
           "पुराचा इशारा. तुमच्या भागात पाणी वेगाने वाढत आहे. आत्ताच उंच ठिकाणी जा. कुटुंबाला सोबत घ्या आणि जड सामान मागे सोडा."),
    "hi": ("Hindi", "हिन्दी",
           "बाढ़ की चेतावनी। आपके क्षेत्र में पानी तेज़ी से बढ़ रहा है। अभी ऊँची जगह पर चले जाएँ। अपने परिवार को साथ लें और भारी सामान छोड़ दें।"),
    "ar": ("Arabic", "العربية",
           "تحذير من الفيضان. المياه ترتفع بسرعة في منطقتك. اتجه إلى مكان مرتفع الآن. خذ عائلتك معك واترك الأمتعة الثقيلة."),
    "zh": ("Chinese", "中文",
           "洪水警报。您所在地区的水位正在迅速上涨。请立即前往高处。带上家人，留下沉重的物品。"),
}


def tts(text):
    url = f"{BASE}/text-to-speech/{VOICE_ID}"
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main():
    if not API_KEY.startswith("sk_"):
        print("ERROR: need a real ELEVENLABS_API_KEY (sk_...).")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {
        "scenario": "Flood evacuation alert",
        "voice": "Sarah (reassuring)",
        "model": MODEL_ID,
        "note": "Pre-generated static clips. The live demo plays these with no API calls.",
        "clips": [],
    }

    total_chars = 0
    for code, (name, native, text) in DEMO.items():
        try:
            audio = tts(text)
        except urllib.error.HTTPError as e:
            print(f"  {name}: FAILED (HTTP {e.code}) -> {e.read().decode()[:200]}")
            continue
        fn = f"alert_{code}.mp3"
        with open(os.path.join(OUT_DIR, fn), "wb") as f:
            f.write(audio)
        total_chars += len(text)
        manifest["clips"].append({
            "code": code, "language": name, "native": native,
            "text": text, "file": f"audio/demo/{fn}", "chars": len(text),
        })
        print(f"  {name:8s}: OK -> {OUT_DIR}/{fn} ({len(audio):,} bytes, {len(text)} chars)")

    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest written. Total characters used this run: {total_chars}")


if __name__ == "__main__":
    main()
