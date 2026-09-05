// ReachAloud service worker.
//
// The whole point: once the page has loaded once, the emergency alert must
// still play when there is NO internet (exactly when a flood knocks out
// connectivity). We pre-cache the app shell and every pre-generated alert
// clip, and serve local requests cache-first.

const CACHE = "reachaloud-v1";

// App shell + all offline-critical assets. The manifest lists every clip.
const CORE = [
  "./",
  "./index.html",
  "./config.js",
  "./manifest.webmanifest",
  "./audio/demo/manifest.json",
  "./audio/demo/alert_en.mp3",
  "./audio/demo/alert_es.mp3",
  "./audio/demo/alert_hi.mp3",
  "./audio/demo/alert_ar.mp3",
  "./audio/demo/alert_fr.mp3",
  "./audio/demo/alert_zh.mp3",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  // Only handle same-origin requests. Never intercept the ElevenLabs API or
  // the CDNs - those need the live network and must fail normally offline.
  if (url.origin !== self.location.origin) return;

  // Cache-first for our own assets (instant + offline). Fall back to network,
  // and cache anything new we successfully fetch.
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match("./index.html"));
    })
  );
});
