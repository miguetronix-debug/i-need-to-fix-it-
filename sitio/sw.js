/* Service worker de «I Need To Fix It».
   Estrategia: la app y sus figuras se guardan la primera vez y a partir de ahí
   se sirven del caché. Es lo que permite usarla en quirófano sin conexión. */
const CACHE='infi-v20260805-33bb30ccdf';
// En el sitio publicado el app se llama index.html; prototipo.html solo existe
// en el repositorio. Y como addAll es atómico, basta con que uno de estos
// devuelva 404 para que la instalación entera falle y el modo sin conexión no
// llegue a funcionar nunca. Por eso se cachea uno a uno y se tolera el fallo.
const BASE=['./','./index.html','./manifest.webmanifest','./icono.svg'];

self.addEventListener('install',e=>{{
  e.waitUntil(
    caches.open(CACHE)
      .then(c=>Promise.all(BASE.map(u=>c.add(u).catch(err=>
        console.warn('[sw] no se pudo cachear',u,err&&err.message)))))
      .then(()=>self.skipWaiting()));
}});
self.addEventListener('activate',e=>{{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
}});
/* Dos estrategias, y la distinción importa.

   El APP (la navegación y el index.html) va a RED PRIMERO: si hay conexión se
   sirve la versión recién publicada y se guarda una copia; si no la hay, se
   sirve la copia guardada. Con caché primero, como estaba antes, el usuario se
   quedaba clavado en la versión que se descargó el primer día y ninguna
   corrección le llegaba nunca.

   Las FIGURAS del compendio van a CACHÉ PRIMERO: son 604 imágenes que no
   cambian, y volver a pedirlas por red sería tirar datos y batería. */
function esApp(req){{
  return req.mode==='navigate' ||
         req.url.indexOf('/index.html')>=0 ||
         req.url.replace(/[?#].*$/,'').endsWith('/');
}}
self.addEventListener('fetch',e=>{{
  if(e.request.method!=='GET') return;
  if(esApp(e.request)){{
    e.respondWith(
      fetch(e.request).then(res=>{{
        if(res && res.ok){{
          const copia=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copia));
        }}
        return res;
      }}).catch(()=>caches.match('./index.html').then(r=>r||caches.match('./')))
    );
    return;
  }}
  e.respondWith(
    caches.match(e.request).then(hit=>{{
      if(hit) return hit;
      return fetch(e.request).then(res=>{{
        if(res.ok && e.request.url.indexOf('/figuras/')>=0){{
          const copia=res.clone(); caches.open(CACHE).then(c=>c.put(e.request,copia));
        }}
        return res;
      }}).catch(()=>caches.match('./index.html').then(r=>r||caches.match('./')));
    }})
  );
}});
