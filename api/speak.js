// ReachAloud - serverless Text-to-Speech proxy (Vercel-style handler).
//
// Holds the ElevenLabs API key server-side so it is NEVER exposed to the
// browser. Takes { text, voiceId } and returns audio/mpeg bytes.
//
// Free-tier notes baked in:
//  - Uses the multilingual v2 model, which auto-detects the language of `text`.
//  - Must use a default premade voice (library voices are blocked on free tier).
//  - Returns a clear JSON error (not a crash) when the character quota is hit,
//    so the UI can tell the user to use the pre-generated demo instead.

const ELEVEN_BASE = "https://api.elevenlabs.io/v1";
const MODEL_ID = "eleven_multilingual_v2";
const DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"; // Sarah - reassuring
const MAX_CHARS = 500; // guard: keep any single request small on free tier

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed. Use POST." });
    return;
  }

  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: "Server is missing ELEVENLABS_API_KEY." });
    return;
  }

  // Parse body (Vercel gives parsed JSON; guard for string bodies too).
  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const text = (body && body.text ? String(body.text) : "").trim();
  const voiceId = (body && body.voiceId) ? String(body.voiceId) : DEFAULT_VOICE_ID;

  if (!text) {
    res.status(400).json({ error: "Please provide some text to speak." });
    return;
  }
  if (text.length > MAX_CHARS) {
    res.status(400).json({
      error: `Message is too long (${text.length} chars). Keep alerts under ${MAX_CHARS} characters.`,
    });
    return;
  }

  try {
    const r = await fetch(`${ELEVEN_BASE}/text-to-speech/${voiceId}`, {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        Accept: "audio/mpeg",
      },
      body: JSON.stringify({
        text,
        model_id: MODEL_ID,
        voice_settings: { stability: 0.5, similarity_boost: 0.75 },
      }),
    });

    if (!r.ok) {
      const detail = await r.text();
      // 401 payment_required = free-tier quota exhausted.
      if (r.status === 401 || r.status === 402) {
        res.status(402).json({
          error: "The ElevenLabs free-tier quota is used up. Try the pre-generated demo alerts below - they play instantly with no quota.",
          detail,
        });
        return;
      }
      res.status(r.status).json({ error: "ElevenLabs request failed.", detail });
      return;
    }

    const audio = Buffer.from(await r.arrayBuffer());
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Cache-Control", "public, max-age=86400"); // cache identical requests
    res.status(200).send(audio);
  } catch (err) {
    res.status(500).json({ error: "Unexpected server error.", detail: String(err) });
  }
}
