
const CACHE = 'tqqq-signal-v2';
const SHELL = ['/', '/index.html'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // Network-first for all API/proxy calls
  const url = e.request.url;
  const isApi = url.includes('yahoo') ||
                url.includes('corsproxy') ||
                url.includes('allorigins') ||
                url.includes('codetabs') ||
                url.includes('cors-anywhere') ||
                url.includes('cloudflare-cors-anywhere') ||
                url.includes('cors.x2u.in') ||
                url.includes('thebugging');

  if (isApi) {
    e.respondWith(
      fetch(e.request, { cache: 'no-store' })
        .catch(() => new Response(JSON.stringify({ chart: { error: 'offline' } }), {
          headers: { 'Content-Type': 'application/json' }
        }))
    );
    return;
  }

  // Cache-first for shell files
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(resp => {
      const clone = resp.clone();
      caches.open(CACHE).then(c => c.put(e.request, clone));
      return resp;
    }))
  );
});
