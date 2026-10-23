import { createServer } from 'node:http';
import { createReadStream, watch } from 'node:fs';
import { stat } from 'node:fs/promises';
import { pipeline } from 'node:stream/promises';
import path from 'node:path';
import { build, dist, root } from './build.mjs';
import { parseRange } from './range.mjs';

let catalog = await build();
const types = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.json':'application/json; charset=utf-8', '.md':'text/markdown; charset=utf-8', '.jpg':'image/jpeg', '.svg':'image/svg+xml', '.mp4':'video/mp4', '.pdf':'application/pdf' };
const server = createServer(async (request, response) => {
  try {
    if (!['GET','HEAD'].includes(request.method)) { response.writeHead(405, { Allow:'GET, HEAD' }).end(); return; }
    const url = new URL(request.url, 'http://localhost');
    const pathname = decodeURIComponent(url.pathname);
    let filename;
    if (pathname.startsWith('/media/')) {
      const file = pathname.slice('/media/'.length);
      if (!catalog.videos.some(video => video.file === file)) { response.writeHead(404).end('Video no encontrado'); return; }
      filename = path.join(root, file);
    } else if (pathname.startsWith('/pdf/')) {
      const document = catalog.books.flatMap(book => book.documents).find(document => document.url === pathname);
      if (!document) { response.writeHead(404).end('PDF no encontrado'); return; }
      filename = path.join(root, document.file);
    } else {
      filename = path.resolve(dist, '.' + (pathname === '/' ? '/index.html' : pathname));
      if (!filename.startsWith(dist + path.sep)) { response.writeHead(403).end(); return; }
    }
    const info = await stat(filename);
    if (!info.isFile()) { response.writeHead(404).end(); return; }
    const range = parseRange(request.method === 'GET' ? request.headers.range : null, info.size);
    const headers = { 'Content-Type':types[path.extname(filename)] || 'application/octet-stream', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', 'Accept-Ranges':'bytes' };
    if (pathname.startsWith('/pdf/')) headers['Content-Disposition'] = `${url.searchParams.get('download') === '1' ? 'attachment' : 'inline'}; filename="${path.basename(pathname)}"`;
    if (range === false) { response.writeHead(416, { ...headers, 'Content-Range':`bytes */${info.size}` }).end(); return; }
    headers['Content-Length'] = range ? range.length : info.size;
    if (range) headers['Content-Range'] = `bytes ${range.start}-${range.end}/${info.size}`;
    response.writeHead(range ? 206 : 200, headers);
    if (request.method === 'HEAD') { response.end(); return; }
    await pipeline(createReadStream(filename, range ? { start:range.start, end:range.end } : undefined), response);
  } catch (error) {
    if (!response.headersSent) response.writeHead(error.code === 'ENOENT' ? 404 : 400).end('Recurso no disponible');
    else response.destroy();
  }
});
const port = Number(process.env.PORT || 4173);
server.listen(port, '127.0.0.1', () => console.log(`Biblioteca disponible en http://127.0.0.1:${port}`));
server.on('error', error => {
  console.error(`No se puede iniciar el servidor local (${error.code}). Puedes crear la vista sin servidor con npm run preview:file.`);
  shutdown();
  process.exitCode = 1;
});
let timer;
let building = false;
let queued = false;
async function rebuild() {
  if (building) { queued = true; return; }
  building = true;
  try { catalog = await build(); console.log('Catálogo y sitio actualizados. Recarga el navegador.'); }
  catch (error) { console.error(error.message); }
  finally { building = false; if (queued) { queued = false; await rebuild(); } }
}
const watchers = ['content','public'].map(directory => watch(path.join(root, directory), { recursive:true }, () => { clearTimeout(timer); timer = setTimeout(rebuild, 200); }));
function shutdown() { clearTimeout(timer); watchers.forEach(watcher => watcher.close()); server.close(); }
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
