import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorker } from '../worker.mjs';
const worker = createWorker([{ file:'videos-libros/03-refuerzo/final.mp4', status:'published' }, {file:'test.mp4',status:'draft'}, {file:'sin-estado.mp4'}]);
import { parseRange } from '../scripts/range.mjs';

const bytes = new TextEncoder().encode('0123456789');
const meta = { size:10, httpEtag:'"video-v1"', uploaded:new Date('2026-10-22T12:00:00Z') };
const url = 'https://biblioteca.example/media/videos-libros/03-refuerzo/final.mp4';
function environment() {
  return {
    ASSETS:{ fetch:async () => new Response('sitio') },
    MEDIA:{
      head:async () => meta,
      get:async (_, options) => {
        const range = options?.range;
        const body = range ? bytes.slice(range.offset, range.offset + range.length) : bytes;
        return { ...meta, body };
      },
    },
  };
}
test('sirve archivos del front y el video completo', async () => {
  assert.equal(await (await worker.fetch(new Request('https://biblioteca.example/'), environment())).text(), 'sitio');
  const response = await worker.fetch(new Request(url), environment());
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('Content-Type'), 'video/mp4');
  assert.equal(await response.text(), '0123456789');
});
test('soporta rangos acotados, abiertos y sufijos para adelantar y retroceder', async () => {
  for (const [range, expected, contentRange] of [['bytes=2-5','2345','bytes 2-5/10'], ['bytes=7-','789','bytes 7-9/10'], ['bytes=-3','789','bytes 7-9/10'], ['bytes=7-99','789','bytes 7-9/10']]) {
    const response = await worker.fetch(new Request(url, { headers:{ Range:range } }), environment());
    assert.equal(response.status, 206);
    assert.equal(response.headers.get('Content-Range'), contentRange);
    assert.equal(Number(response.headers.get('Content-Length')), expected.length);
    assert.equal(await response.text(), expected);
  }
});
test('rangos inválidos devuelven 416 y el tamaño real', async () => {
  for (const range of ['bytes=99-','bytes=6-3','bytes=-0','bytes=-','bytes=0-1,5-6','bytes=9007199254740992-']) {
    const response = await worker.fetch(new Request(url, { headers:{ Range:range } }), environment());
    assert.equal(response.status, 416, range);
    assert.equal(response.headers.get('Content-Range'), 'bytes */10');
  }
  assert.equal(parseRange('bytes=0-', 0), false);
});
test('HEAD no descarga el objeto y los ETag permiten 304', async () => {
  const env = environment();
  env.MEDIA.get = () => { throw new Error('No debería descargar'); };
  const head = await worker.fetch(new Request(url, { method:'HEAD', headers:{ Range:'bytes=1-3' } }), env);
  assert.equal(head.status, 200);
  assert.equal(head.headers.get('Content-Length'), '10');
  assert.equal(await head.text(), '');
  const cached = await worker.fetch(new Request(url, { headers:{ 'If-None-Match':'W/"video-v1"' } }), env);
  assert.equal(cached.status, 304);
});
test('If-Range obsoleto devuelve el video completo', async () => {
  const response = await worker.fetch(new Request(url, { headers:{ Range:'bytes=2-5', 'If-Range':'"viejo"' } }), environment());
  assert.equal(response.status, 200);
  assert.equal(await response.text(), '0123456789');
});
test('rechaza archivos fuera del catálogo y métodos de escritura', async () => {
  assert.equal((await worker.fetch(new Request('https://biblioteca.example/media/.env'), environment())).status, 404);
  assert.equal((await worker.fetch(new Request(url, { method:'PUT' }), environment())).status, 405);
  const env = environment(); env.MEDIA.head = async () => null;
  assert.equal((await worker.fetch(new Request(url), env)).status, 404);
  assert.equal((await worker.fetch(new Request(url), { ASSETS:env.ASSETS })).status, 503);
});

test('no sirve borradores ni entradas sin publicación explícita', async () => {
  assert.equal((await worker.fetch(new Request('https://biblioteca.example/media/test.mp4'), environment())).status, 404);
  assert.equal((await worker.fetch(new Request('https://biblioteca.example/media/sin-estado.mp4'), environment())).status, 404);
});

const pdfURL = 'https://biblioteca.example/pdf/el-hogar-cristiano.pdf';
test('PDF original desde R2: rangos, descarga y prioridad sobre fuente caída', async t => {
  t.mock.method(globalThis, 'fetch', async () => { throw new Error('Fuente oficial caída'); });
  const env = environment();
  const keys = [];
  env.MEDIA.head = async key => { keys.push(key); return meta; };
  const response = await worker.fetch(new Request(pdfURL, {headers:{Range:'bytes=2-5'}}), env);
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('Content-Type'), 'application/pdf');
  assert.equal(response.headers.get('X-Document-Source'), 'r2');
  assert.match(response.headers.get('Content-Disposition'), /^inline/);
  assert.equal(await response.text(), '2345');
  assert.deepEqual(keys, ['pdf/el-hogar-cristiano.pdf']);
  const download = await worker.fetch(new Request(pdfURL + '?download=1'), env);
  assert.match(download.headers.get('Content-Disposition'), /^attachment/);
});
test('sin respaldo usa solo la fuente oficial configurada y conserva rangos', async t => {
  const calls = [];
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({url,options});
    return new Response('PDF', {status:206,headers:{'Content-Type':'application/pdf','Content-Range':'bytes 0-2/10'}});
  });
  const env = environment(); env.MEDIA.head = async () => null;
  const response = await worker.fetch(new Request(pdfURL + '?source=https://evil.example/test.pdf', {headers:{Range:'bytes=0-2'}}), env);
  assert.equal(response.status, 206);
  assert.equal(response.headers.get('X-Document-Source'), 'official');
  assert.equal(response.headers.get('Content-Range'), 'bytes 0-2/10');
  assert.match(calls[0].url, /^https:\/\/media[24]\.egwwritings\.org\//);
  assert.equal(calls[0].options.headers.get('Range'), 'bytes=0-2');
});
test('rechaza HTML disfrazado de PDF y no permite documentos fuera del catálogo', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => new Response('<html>Error</html>', {headers:{'Content-Type':'text/html'}}));
  const env = environment(); env.MEDIA.head = async () => null;
  assert.equal((await worker.fetch(new Request(pdfURL), env)).status, 503);
  assert.equal((await worker.fetch(new Request('https://biblioteca.example/pdf/privado.pdf'), env)).status, 404);
  assert.equal(fetch.mock.callCount(), 1);
});
