self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("nes-lab-cache").then((cache) => {
      return cache.addAll(["./"]);
    })
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});
