const CACHE_NAME = 'edumis-cache-v1';
const OFFLINE_URL = '/static/offline.html';

const PRECACHE_ASSETS = [
    OFFLINE_URL,
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json',
];

// O'rnatish - asosiy fayllarni keshga oladi
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_ASSETS))
    );
    self.skipWaiting();
});

// Faollashtirish - eski keshlarni tozalaydi
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// So'rovlarni ushlab olish
// Sahifa navigatsiyasi (HTML) uchun: internet-birinchi, xato bo'lsa offline sahifa
// Statik fayllar (rasm, manifest) uchun: keshdan, bo'lmasa tarmoqdan
self.addEventListener('fetch', (event) => {
    const req = event.request;

    if (req.mode === 'navigate') {
        event.respondWith(
            fetch(req).catch(() => caches.match(OFFLINE_URL))
        );
        return;
    }

    if (req.url.includes('/static/')) {
        event.respondWith(
            caches.match(req).then((cached) => cached || fetch(req))
        );
    }
});
