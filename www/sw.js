const C='chinapaw-v48';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'])).catch(()=>{}))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('message',e=>{if(e.data==='skip')self.skipWaiting()});
/* 网页本身总是先向服务器确认最新版本（不使用浏览器旧缓存），断网时才用离线副本 */
self.addEventListener('fetch',e=>{const r=e.request,u=r.url;if(r.method!=='GET'||!u.startsWith(self.location.origin)||u.includes('version.json')||u.includes('/admin/')||u.includes('/app/'))return;
  const page=r.mode==='navigate'||/\/(index\.html)?(\?|$)/.test(u);
  const net=page?fetch(u,{cache:'no-cache',credentials:'same-origin'}):fetch(r);
  e.respondWith(net.then(x=>{if(x&&x.ok){const cp=x.clone();caches.open(C).then(c=>c.put(page?'index.html':r,cp))}return x}).catch(()=>caches.match(page?'index.html':r).then(m=>m||caches.match('./'))))});
