# ReachAloud

Multilingual text-to-speech accessibility tool that turns emergency alerts into
natural voice in any language, for the people that written alerts leave behind:
low-literacy, low-vision, and non-native readers. Built with ElevenLabs.

## How it works

- **Static demo (no backend, no keys):** 6 pre-generated flood-alert clips
  (English, Spanish, Hindi, Arabic, French, Chinese) play instantly with zero
  API calls. The "Preview a spoken alert" button plays a matching clip.
- **Live mode (optional backend):** set an `API_BASE` and the button turns into
  live, type-anything text-to-speech. The ElevenLabs key stays server-side in
  `api/speak.js` and is never exposed to the browser.

## Deploy the static site (GitHub Pages)

The site is a single `index.html` plus `config.js` and the `audio/` folder, all
served from the repo root (a `.nojekyll` file disables Jekyll processing).

1. Push to GitHub.
2. Settings -> Pages -> Deploy from branch -> `main` / root.
3. Visit `https://<user>.github.io/reachaloud/`.

`config.js` ships with `API_BASE: ""`, so Pages runs in pure-static preview mode.

## Enable live TTS (optional, Vercel)

1. Deploy this repo to Vercel (it will pick up `api/speak.js` as a serverless
   function automatically).
2. Add an `ELEVENLABS_API_KEY` environment variable in the Vercel project.
3. Point the static site at it by editing `config.js`:
   ```js
   window.REACHALOUD_CONFIG = { API_BASE: "https://your-app.vercel.app" };
   ```
   The button then calls `${API_BASE}/api/speak` and speaks any text you type.

## Regenerate the demo clips

```bash
cp .env.example .env   # add your ELEVENLABS_API_KEY
python3 scripts/generate_demo.py
```
