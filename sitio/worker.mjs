import videos from './.generated/videos.json' with { type: 'json' };
import documents from './.generated/documents.json' with { type: 'json' };
import { parseRange } from './scripts/range.mjs';

const pdfFiles = new Map(documents.map(document => [`${document.id}.pdf`, document]));

async function serveR2(request, bucket, key, headers) {
  const object = await bucket.head(key);
  if (!object) return null;
  headers.set('ETag', object.httpEtag);
  headers.set('Last-Modified', object.uploaded.toUTCString());
  headers.set('Accept-Ranges', 'bytes');
  headers.set('Cache-Control', 'public, max-age=3600');
  const etags = request.headers.get('If-None-Match')?.split(',').map(tag => tag.trim());
  if (etags?.some(tag => tag === '*' || tag.replace(/^W\//, '') === object.httpEtag)) return new Response(null, { status:304, headers });
  const ifRange = request.headers.get('If-Range');
  const canRange = !ifRange || ifRange === object.httpEtag || ifRange === object.uploaded.toUTCString();
  const range = parseRange(request.method === 'GET' && canRange ? request.headers.get('Range') : null, object.size);
  if (range === false) {
    headers.set('Content-Range', `bytes */${object.size}`);
    return new Response(null, { status:416, headers });
  }
  headers.set('Content-Length', String(range ? range.length : object.size));
  if (range) headers.set('Content-Range', `bytes ${range.start}-${range.end}/${object.size}`);
  if (request.method === 'HEAD') return new Response(null, { status:200, headers });
  const data = await bucket.get(key, range ? { range:{ offset:range.start, length:range.length } } : undefined);
  if (!data) return null;
  return new Response(data.body, { status:range ? 206 : 200, headers });
}

function pdfHeaders(request, document) {
  const disposition = new URL(request.url).searchParams.get('download') === '1' ? 'attachment' : 'inline';
  return new Headers({
    'Content-Type':'application/pdf',
    'Content-Disposition':`${disposition}; filename="${document.id}.pdf"`,
    'X-Content-Type-Options':'nosniff',
    'X-Frame-Options':'SAMEORIGIN',
    'Content-Security-Policy':"frame-ancestors 'self'",
  });
}

async function serveOfficialPDF(request, document) {
  const headers = new Headers();
  for (const name of ['Range', 'If-Range', 'If-None-Match']) {
    if (request.headers.has(name) && (request.method === 'GET' || name === 'If-None-Match')) headers.set(name, request.headers.get(name));
  }
  const source = await fetch(document.source, { method:request.method, headers, signal:AbortSignal.timeout(10000), redirect:'follow' });
  const validStatus = [200,206,304,416].includes(source.status);
  const isPDF = /^application\/pdf(?:;|$)/i.test(source.headers.get('Content-Type') || '');
  if (!validStatus || ([200,206].includes(source.status) && !isPDF)) {
    await source.body?.cancel();
    return null;
  }
  const output = pdfHeaders(request, document);
  for (const name of ['Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag', 'Last-Modified']) {
    if (source.headers.has(name)) output.set(name, source.headers.get(name));
  }
  output.set('Cache-Control', 'public, max-age=300');
  output.set('X-Document-Source', 'official');
  const hasBody = request.method === 'GET' && [200,206].includes(source.status);
  if (!hasBody) await source.body?.cancel();
  return new Response(hasBody ? source.body : null, { status:source.status, headers:output });
}

async function servePDF(request, env, document) {
  // La copia original en R2 mantiene la lectura disponible aunque el proveedor falle.
  try {
    if (env.MEDIA) {
      const headers = pdfHeaders(request, document);
      headers.set('X-Document-Source', 'r2');
      const response = await serveR2(request, env.MEDIA, document.key, headers);
      if (response) return response;
    }
  } catch { /* Si no se puede usar el respaldo, probar la fuente oficial. */ }
  try {
    const response = await serveOfficialPDF(request, document);
    if (response) return response;
  } catch { /* El lector mostrará el enlace directo y la opción de reintentar. */ }
  return new Response('No se pudo cargar el PDF. Intenta de nuevo o abre la fuente oficial.', { status:503, headers:{ 'Cache-Control':'no-store', 'Retry-After':'60' } });
}

export function createWorker(videoCatalog = videos) {
  const mediaFiles = new Set(videoCatalog.filter(video => video.status === 'published').map(video => video.file));
  return {
    async fetch(request, env) {
      const url = new URL(request.url);
      const isPDF = url.pathname.startsWith('/pdf/');
      if (!isPDF && !url.pathname.startsWith('/media/')) return env.ASSETS.fetch(request);
      if (!['GET', 'HEAD'].includes(request.method)) return new Response('Método no permitido', { status:405, headers:{ Allow:'GET, HEAD' } });
      let filename;
      try { filename = decodeURIComponent(url.pathname.slice(isPDF ? '/pdf/'.length : '/media/'.length)); }
      catch { return new Response('Ruta inválida', { status:400 }); }
      if (isPDF) {
        const document = pdfFiles.get(filename);
        if (!document) return new Response('PDF no encontrado', { status:404 });
        return servePDF(request, env, document);
      }
      if (!mediaFiles.has(filename)) return new Response('Video no encontrado', { status:404 });
      if (!env.MEDIA) return new Response('Almacenamiento de videos no configurado', { status:503 });
      try {
        const response = await serveR2(request, env.MEDIA, filename, new Headers({ 'Content-Type':'video/mp4', 'X-Content-Type-Options':'nosniff' }));
        return response || new Response('Video no encontrado', { status:404 });
      } catch {
        return new Response('El video no está disponible temporalmente', { status:503, headers:{ 'Retry-After':'60' } });
      }
    },
  };
}

export default createWorker();
