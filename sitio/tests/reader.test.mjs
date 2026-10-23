import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';

const html = await readFile(new URL('../public/leer.html', import.meta.url), 'utf8');
const script = await readFile(new URL('../public/reader.js', import.meta.url), 'utf8');
const catalog = JSON.parse(await readFile(new URL('../dist/catalog.json', import.meta.url), 'utf8'));
async function reader(t, query, pdfOK = true, {mobile=false, pdfViewerEnabled=true} = {}) {
  const dom = new JSDOM(html, {url:`https://biblioteca.example/leer.html?${query}`,runScripts:'outside-only'});
  t.after(() => dom.window.close());
  const calls = [];
  let mediaListener;
  const media = {matches:mobile,addEventListener:(_, listener) => { mediaListener = listener; }};
  dom.window.matchMedia = () => media;
  Object.defineProperty(dom.window.navigator, 'pdfViewerEnabled', {value:pdfViewerEnabled});
  dom.window.fetch = async (url, options) => {
    calls.push({url,options});
    if (url === '/catalog.json') return {ok:true,json:async () => catalog};
    return {ok:pdfOK,headers:new Headers({'Content-Type':'application/pdf'})};
  };
  dom.window.eval(script);
  await new Promise(resolve => setImmediate(resolve));
  function setMobile(matches) { media.matches = matches; mediaListener(); }
  return {w:dom.window,$:selector => dom.window.document.querySelector(selector),calls,setMobile};
}
test('abre PDF completo sin redirección comercial y ofrece salida al visor del dispositivo', async t => {
  const {$,calls} = await reader(t, 'libro=el-hogar-cristiano');
  assert.equal($('#pdf-frame').hidden, false);
  assert.match($('#pdf-frame').src, /\/pdf\/el-hogar-cristiano.pdf#view=FitH$/);
  assert.equal($('#open-pdf').target, '_blank');
  assert.match($('#download-pdf').href, /download=1$/);
  assert.equal(calls[1].options.method, 'HEAD');
  assert.equal($('#edition').hidden, true);
});
test('permite cambiar entre tomos y ediciones conservando el enlace compartible', async t => {
  const book = catalog.books.find(b => b.documents.length > 1);
  const {$,w} = await reader(t, `libro=${book.id}&edicion=${book.documents[1].id}`);
  assert.equal($('#edition').value, book.documents[1].id);
  $('#edition').value = book.documents[2].id;
  $('#edition').dispatchEvent(new w.Event('change'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(new URL(w.location.href).searchParams.get('edicion'), book.documents[2].id);
  assert.equal($('#open-pdf').getAttribute('href'), book.documents[2].url);
});
test('fallo del documento ofrece reintento y PDF oficial; libro desconocido no abre otro archivo', async t => {
  const failed = await reader(t, 'libro=el-hogar-cristiano', false);
  assert.equal(failed.$('#reader-error').hidden, false);
  assert.equal(failed.$('#pdf-frame').hidden, true);
  assert.match(failed.$('#error-official').href, /^https:\/\/media/);
  const unknown = await reader(t, 'libro=no-existe');
  assert.equal(unknown.$('#reader-controls').hidden, true);
  assert.equal(unknown.$('#pdf-frame').hasAttribute('src'), false);
  assert.equal(unknown.calls.length, 1);
});

test('en móvil abre el PDF en la misma pestaña sin cargar un iframe y conserva el tomo elegido', async t => {
  const book = catalog.books.find(item => item.documents.length > 1);
  const {$,w,setMobile} = await reader(t, `libro=${book.id}&edicion=${book.documents[1].id}`, true, {mobile:true});
  assert.equal($('#pdf-frame').hidden, true);
  assert.equal($('#pdf-frame').hasAttribute('src'), false);
  assert.equal($('#reader-mobile-note').hidden, false);
  assert.equal($('#reader-hint').hidden, true);
  assert.equal($('#open-pdf').target, '_self');
  assert.equal($('#open-pdf').getAttribute('href'), book.documents[1].url);
  assert.equal($('#reader-status').hidden, true);
  $('#edition').value = book.documents[2].id;
  $('#edition').dispatchEvent(new w.Event('change'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal($('#open-pdf').getAttribute('href'), book.documents[2].url);
  assert.equal($('#download-pdf').getAttribute('href'), book.documents[2].url + '?download=1');
  assert.equal(new URL(w.location.href).searchParams.get('edicion'), book.documents[2].id);
  assert.equal($('#pdf-frame').hasAttribute('src'), false);
  setMobile(false);
  assert.equal($('#pdf-frame').hidden, false);
  assert.equal($('#open-pdf').target, '_blank');
  setMobile(true);
  assert.equal($('#pdf-frame').hasAttribute('src'), false);
  assert.equal($('#open-pdf').target, '_self');
});

test('un navegador sin visor PDF integrado ofrece lectura directa incluso en pantalla grande', async t => {
  const {$} = await reader(t, 'libro=el-hogar-cristiano', true, {pdfViewerEnabled:false});
  assert.equal($('#pdf-frame').hasAttribute('src'), false);
  assert.equal($('#open-pdf').target, '_self');
  assert.equal($('#reader-mobile-note').hidden, false);
});

test('si el PDF falla en móvil, mantiene descarga, fuente oficial y reintento sin incrustarlo', async t => {
  const {$} = await reader(t, 'libro=el-hogar-cristiano', false, {mobile:true});
  assert.equal($('#reader-error').hidden, false);
  assert.equal($('#pdf-frame').hasAttribute('src'), false);
  assert.equal($('#reader-launch').hidden, false);
  assert.equal($('#open-pdf').getAttribute('href'), '/pdf/el-hogar-cristiano.pdf');
  assert.equal($('#download-pdf').getAttribute('href'), '/pdf/el-hogar-cristiano.pdf?download=1');
  assert.equal($('#error-official').hidden, false);
  assert.equal($('#retry-pdf').hidden, false);
});
