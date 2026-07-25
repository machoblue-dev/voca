/* 학문당 VOCA꾹 — 서비스워커 v2.2
   전략:
   - 페이지(내비게이션): 네트워크 우선 → 실패 시 캐시된 index.html (오프라인에서도 앱이 뜬다)
     ※ 앱의 자동 업데이트(checkUpdate)는 no-store fetch를 쓰므로 이 전략과 충돌하지 않는다.
   - 폰트·아이콘·매니페스트: 캐시 우선 (한 번 받으면 빠르게)
   - Supabase 등 다른 출처 요청: 개입하지 않음 (그대로 네트워크)
   - push: 알림 표시 / notificationclick: 앱 열기 */
const CACHE = 'vocakkuk-v2.2.0';
const PRECACHE = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './fonts/PretendardVariable.woff2',
  './fonts/Paperlogy-4Regular.woff2',
  './fonts/Paperlogy-7Bold.woff2',
  './fonts/Paperlogy-8ExtraBold.woff2',
  './fonts/Paperlogy-9Black.woff2'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c =>
      /* 하나가 없어도 설치가 죽지 않게 개별 addAll */
      Promise.allSettled(PRECACHE.map(u => c.add(u)))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   /* Supabase 등은 그대로 통과 */

  /* 페이지 요청 — 네트워크 우선, 실패하면 캐시 index */
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put('./index.html', copy)).catch(() => {});
        return res;
      }).catch(() =>
        caches.match('./index.html').then(hit => hit || caches.match('./'))
      )
    );
    return;
  }

  /* 정적 자원 — 캐시 우선 */
  if (/\.(woff2|png|json|ico|svg)$/.test(url.pathname)) {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
        return res;
      }))
    );
  }
});

/* ── 웹푸시 수신 ── */
self.addEventListener('push', e => {
  let data = {};
  try { data = e.data ? e.data.json() : {}; } catch (err) { data = { body: e.data ? e.data.text() : '' }; }
  const title = data.title || 'VOCA꾹';
  const opts = {
    body: data.body || '오늘 치 복습이 기다리고 있어요 🔒',
    icon: './icons/icon-192.png',
    badge: './icons/icon-192.png',
    tag: data.tag || 'vocakkuk',
    data: { url: data.url || './' }
  };
  e.waitUntil(self.registration.showNotification(title, opts));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || './';
  e.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      for (const c of list) {
        if ('focus' in c) return c.focus();
      }
      return self.clients.openWindow(url);
    })
  );
});
