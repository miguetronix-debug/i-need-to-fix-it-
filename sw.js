/* Service worker de «I Need To Fix It».
   Estrategia: la app y sus figuras se guardan la primera vez y a partir de ahí
   se sirven del caché. Es lo que permite usarla en quirófano sin conexión. */
const CACHE='infi-v20260804';
const BASE=['./','./prototipo.html','./manifest.webmanifest','./icono.svg'];

self.addEventListener('install',e=>{{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(BASE)).then(()=>self.skipWaiting()));
}});
self.addEventListener('activate',e=>{{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
}});
self.addEventListener('fetch',e=>{{
  if(e.request.method!=='GET') return;
  e.respondWith(
    caches.match(e.request).then(hit=>{{
      if(hit) return hit;
      return fetch(e.request).then(res=>{{
        // las figuras del compendio se guardan según se van pidiendo
        if(res.ok && e.request.url.indexOf('/figuras/')>=0){{
          const copia=res.clone(); caches.open(CACHE).then(c=>c.put(e.request,copia));
        }}
        return res;
      }}).catch(()=>caches.match('./prototipo.html'));
    }})
  );
}});
