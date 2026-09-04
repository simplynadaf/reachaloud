// ReachAloud - runtime config.
//
// API_BASE controls the live "Speak this alert" feature.
//
//  - Leave it "" (empty) for a pure static site (GitHub Pages). The live box
//    becomes a graceful "listen to the pre-made alerts" prompt, and the 6
//    demo clips carry the whole experience with ZERO API calls.
//
//  - Set it to your deployed serverless backend to turn on live, type-anything
//    text-to-speech. The backend (api/speak.js) holds the ElevenLabs key so it
//    is never exposed in the browser. Example after deploying to Vercel:
//        window.REACHALOUD_CONFIG = { API_BASE: "https://reachaloud.vercel.app" };
//
// The endpoint called is `${API_BASE}/api/speak`.
window.REACHALOUD_CONFIG = { API_BASE: "" };
