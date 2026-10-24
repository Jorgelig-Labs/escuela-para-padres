import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';

const html = await readFile(new URL('../public/leer.html', import.meta.url), 'utf8');
const script = (await readFile(new URL('../public/reader.js', import.meta.url), 'utf8')).replace("import { createPDFReader } from './pdf-reader.js';", 'const createPDFReader = window.createPDFReader;');
const catalog = JSON.parse(await readFile(new URL('../dist/catalog.json', import.meta.url), 'utf8'));
const tick = () => new Promise(resolve => setImmediate(resolve));
async function reader(t, query, {fail=false, storedPage=null, data=catalog} = {}) {
  const dom = new JSDOM(html, {url:`https://biblioteca.example/leer.html?${query}`,runScripts:'outside-only'});
  t.after(() => dom.window.close());
  const w = dom.window;
  const calls = [];
  const renders = [];
  let pauses = 0;
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.HTMLMediaElement.prototype.pause = () => { pauses++; };
  w.HTMLMediaElement.prototype.load = () => {};
  w.createPDFReader = container => ({
    open:async url => { calls.push(url); if (fail) throw new Error('No disponible'); return 12; },
    render:async (page, options) => { renders.push({page,options}); container.textContent = `Página ${page}`; return true; },
    destroy:async () => {},
  });
  w.fetch = async () => ({ok:true,json:async () => structuredClone(data)});
  if (storedPage) w.localStorage.setItem('entre-nosotros-pagina-el-hogar-cristiano', String(storedPage));
  w.eval(script);
  await tick();
  return {w,$:selector => w.document.querySelector(selector),calls,renders,pauses:() => pauses};
}

test('lee dentro de la página sin iframe, limita páginas y permite texto cómodo', async t => {
  const {$,w,renders} = await reader(t, 'libro=el-hogar-cristiano');
  assert.equal($('iframe'), null);
  assert.equal($('#pdf-reader').hidden, false);
  assert.equal($('#page-total').textContent, 'de 12');
  assert.equal($('#previous-page').disabled, true);
  $('#next-page').click(); await tick();
  assert.equal(renders.at(-1).page, 2);
  $('#reading-mode').value = 'text'; $('#reading-mode').dispatchEvent(new w.Event('change')); await tick();
  assert.equal(renders.at(-1).options.text, true);
  assert.equal($('#zoom').hidden, true);
  $('#page-number').value = '999'; $('#page-form').dispatchEvent(new w.Event('submit', {cancelable:true})); await tick();
  assert.equal(renders.at(-1).page, 12);
  assert.equal($('#next-page').disabled, true);
});

test('conserva página al ir al resumen, a la ficha y volver; pausa el video al salir', async t => {
  const {$,w,renders,pauses} = await reader(t, 'libro=el-hogar-cristiano', {storedPage:7});
  assert.equal(renders.at(-1).page, 7);
  $('#book-nav [data-view="videos"]').click();
  assert.equal($('#videos-panel').hidden, false);
  assert.match($('#reader-video').src, /resumen-el-hogar-cristiano.mp4$/);
  assert.equal($('#book-video-list h3').textContent, 'Resumen del libro');
  assert.match($('.reader-video-item small').textContent, /^\d+:\d{2} · Ver video$/);
  const before = pauses();
  $('#book-nav [data-view="details"]').click();
  assert.ok(pauses() > before);
  assert.equal($('#details-panel').hidden, false);
  assert.equal($('#detail-title').textContent, 'El hogar cristiano');
  $('#book-nav [data-view="read"]').click(); await tick();
  assert.equal(renders.at(-1).page, 7);
  assert.equal(w.localStorage.getItem('entre-nosotros-pagina-el-hogar-cristiano'), '7');
  assert.equal(new URL(w.location.href).searchParams.get('pagina'), '7');
  assert.match($('#reader-back').href, /recurso=el-hogar-cristiano/);
});

test('selección de tomo actualiza PDF y descarga y recupera su propia página', async t => {
  const book = catalog.books.find(item => item.documents.length > 1);
  const {$,w,calls} = await reader(t, `libro=${book.id}&edicion=${book.documents[1].id}&pagina=4`);
  assert.equal(calls.at(-1), book.documents[1].url);
  w.localStorage.setItem(`entre-nosotros-pagina-${book.documents[2].id}`, '8');
  $('#edition').value = book.documents[2].id; $('#edition').dispatchEvent(new w.Event('change')); await tick();
  assert.equal(calls.at(-1), book.documents[2].url);
  assert.equal($('#page-number').value, '8');
  assert.equal($('#download-pdf').getAttribute('href'), book.documents[2].url + '?download=1');
});

test('enlace directo a videos evita descargar el PDF hasta elegir Leer', async t => {
  const {$,calls} = await reader(t, 'libro=el-hogar-cristiano&vista=videos&pagina=6');
  assert.equal(calls.length, 0);
  assert.equal($('#read-panel').hidden, true);
  assert.equal($('#videos-panel').hidden, false);
  $('#resume-reading').click(); await tick();
  assert.equal(calls.length, 1);
  assert.equal($('#read-panel').hidden, false);
  assert.equal($('#page-number').value, '6');
});

test('no muestra videos ajenos ni borradores y reproduce el episodio elegido', async t => {
  const data = structuredClone(catalog);
  const summary = data.videos.find(item => item.book === 'el-hogar-cristiano' && item.group === 'resumen');
  data.videos.push({...summary,id:'borrador',status:'draft'});
  const {$} = await reader(t, 'libro=el-hogar-cristiano&vista=videos', {data});
  assert.equal($('[data-video="borrador"]'), null);
  assert.equal($('[data-video="serie-conduccion-del-nino-1de3"]'), null);
  const episode = data.videos.find(item => item.book === 'el-hogar-cristiano' && item.episode === 2);
  $(`[data-video="${episode.id}"]`).click();
  assert.ok($('#reader-video').src.endsWith(episode.file));
  assert.equal($('#reader-video').autoplay, false);
});

test('un fallo del PDF mantiene resumen y ficha disponibles y ofrece original y reintento', async t => {
  const {$} = await reader(t, 'libro=el-hogar-cristiano', {fail:true});
  assert.equal($('#reader-error').hidden, false);
  assert.equal($('#reader-actions').hidden, false);
  assert.equal($('#open-pdf').getAttribute('href'), '/pdf/el-hogar-cristiano.pdf');
  $('#book-nav [data-view="videos"]').click();
  assert.equal($('#book-player').hidden, false);
  $('#book-nav [data-view="details"]').click();
  assert.equal($('#details-panel').hidden, false);
});

test('libro sin PDF conserva videos y ficha; enlace desconocido no abre otro libro', async t => {
  const book = catalog.books.find(item => !item.documents.length);
  const valid = await reader(t, `libro=${book.id}`);
  assert.equal(valid.$('#book-nav [data-view="read"]').disabled, true);
  assert.equal(valid.$('#videos-panel').hidden, false);
  assert.equal(valid.calls.length, 0);
  const invalid = await reader(t, 'libro=no-existe');
  assert.equal(invalid.$('#book-nav').hidden, true);
  assert.equal(invalid.calls.length, 0);
  assert.equal(invalid.$('#reader-error').hidden, false);
});
