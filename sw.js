/* Xưởng Nhà — service worker.
   Mục đích: mở được app khi mất mạng, kể cả ba thư viện nạp từ jsDelivr.
   Chiến lược: đọc từ kho trước rồi âm thầm làm mới (stale-while-revalidate).
   Tăng KHO mỗi lần đổi index.html để bản cũ bị dọn đi. */
const KHO = 'xuongnha-v2';
const VON = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  'https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js',
  'https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js',
  'https://cdn.jsdelivr.net/npm/@babel/standalone@7.23.6/babel.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(KHO);
    /* mỗi món tải riêng: một đường hỏng không được kéo cả mẻ xuống */
    await Promise.all(VON.map(u =>
      fetch(u, {mode: u.startsWith('http') ? 'cors' : 'same-origin'})
        .then(r => r.ok && c.put(u, r))
        .catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const ten = await caches.keys();
    await Promise.all(ten.filter(t => t !== KHO).map(t => caches.delete(t)));
    self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith((async () => {
    const c = await caches.open(KHO);
    const cu = await c.match(req, {ignoreSearch: true});
    const mang = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; })
                           .catch(() => null);
    return cu || (await mang) || new Response('Mất mạng và chưa có bản lưu.', {status: 503});
  })());
});
