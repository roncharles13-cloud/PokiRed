// Service worker: cache the app shell so the installed PWA runs offline.
// The ROM is never cached here — it lives in the browser's IndexedDB.
const CACHE = "red-se-v2";
const SHELL = [
  "./", "index.html", "manifest.json",
  "vendor/gbo/js/other/base64.js",
  "vendor/gbo/js/other/resampler.js",
  "vendor/gbo/js/other/XAudioServer.js",
  "vendor/gbo/js/GameBoyCore.js",
  "vendor/gbo/js/GameBoyIO.js",
  "icons/icon-192.png", "icons/icon-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.pathname.endsWith(".gb") || url.pathname.endsWith(".gbc")) return; // never cache ROMs
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).catch(() => caches.match("index.html")))
  );
});
