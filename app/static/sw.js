// Service Worker básico para PWA
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Permite que todas las peticiones fluyan normalmente a FastAPI
  event.respondWith(fetch(event.request));
});