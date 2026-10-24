import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';

const [html, script, sourceCatalog] = await Promise.all([
  readFile(new URL('../public/index.html', import.meta.url), 'utf8'),
  readFile(new URL('../public/app.js', import.meta.url), 'utf8'),
  readFile(new URL('../dist/catalog.json', import.meta.url), 'utf8').then(JSON.parse),
]);

const catalog = structuredClone(sourceCatalog);
catalog.videos = [{ id:'video-final', type:'video', status:'published', title:'Conversar en familia', author:'Entre nosotros', topic:'Comunicación', description:'Ideas para escuchar.', duration:75, file:'videos-libros/03-refuerzo/final.mp4', poster:'/assets/final.jpg', group:'refuerzo', orientation:'vertical', book:'el-hogar-cristiano' }];
catalog.site.featuredVideo = 'video-final';
const total = catalog.books.length + catalog.videos.length;

async function app(t, { query='', fail=false, stored=null, data=catalog, mobile=false } = {}) {
  // Prueba el JS real y el DOM; no sustituye la revisión visual o multimedia.
  const dom = new JSDOM(html, { url:`https://biblioteca.example/${query}`, runScripts:'outside-only', pretendToBeVisual:true });
  t.after(() => dom.window.close());
  const w = dom.window;
  const mediaListeners = [];
  const media = {matches:mobile,addEventListener:(_, listener) => mediaListeners.push(listener)};
  w.matchMedia = () => media;
  w.fetch = async () => ({ ok:!fail, json:async () => structuredClone(data) });
  w.scrollTo = () => {};
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new w.Event('close')); };
  w.HTMLMediaElement.prototype.pause = () => {};
  w.HTMLMediaElement.prototype.load = () => {};
  if (stored) w.localStorage.setItem('entre-nosotros-guardados', stored);
  w.eval(script);
  await new Promise(resolve => setImmediate(resolve));
  const $ = selector => w.document.querySelector(selector);
  const count = () => w.document.querySelectorAll('.resource-card').length;
  function input(selector, value, event='input') { $(selector).value = value; $(selector).dispatchEvent(new w.Event(event, { bubbles:true })); }
  function setMobile(matches) { media.matches = matches; mediaListeners.forEach(listener => listener()); }
  return { w, $, count, input, setMobile };
}

test('en móvil los filtros se pliegan sin perder la selección y se muestran al ampliar la pantalla', async t => {
  const {w,$,input,setMobile} = await app(t, {mobile:true,data:seriesCatalog(),query:'?type=video&group=libros&topic=Comunicación'});
  assert.equal($('#refinement-panel').hidden, true);
  assert.equal($('#toggle-refinements').getAttribute('aria-expanded'), 'false');
  assert.equal($('#refinement-label').textContent, 'Comunicación');
  $('#toggle-refinements').click();
  assert.equal($('#refinement-panel').hidden, false);
  input('#related-book', 'el-hogar-cristiano', 'change');
  $('#toggle-refinements').click();
  assert.equal($('#refinement-panel').hidden, true);
  assert.match($('#refinement-label').textContent, /Comunicación · 1 libro/);
  assert.equal(new URL(w.location.href).searchParams.get('book'), 'el-hogar-cristiano');
  setMobile(false);
  assert.equal($('#refinement-panel').hidden, false);
  setMobile(true);
  assert.equal($('#refinement-panel').hidden, true);
  $('#clear-selection').click();
  assert.equal($('#refinement-label').textContent, 'Filtrar por tema o libro');
});

test('la portada ofrece colecciones breves, Ver más abre la colección completa y buscar encuentra videos no mostrados', async t => {
  const data = structuredClone(catalog);
  data.videos = Array.from({length:8},(_,i) => ({...data.videos[0],id:`capsula-${i}`,title:`Consejo ${i}`,group:'junta',orientation:'horizontal'}));
  const {w,$,count,input} = await app(t, {data});
  assert.equal(count(), data.books.length + 3);
  assert.equal($('[data-id="capsula-7"]'), null);
  assert.match($('[data-show-group="junta"]').textContent, /Ver 5 más/);
  $('[data-show-group="junta"]').click();
  assert.equal(count(), 8);
  assert.equal(new URL(w.location.href).searchParams.get('group'), 'junta');
  assert.equal(w.document.activeElement, $('#junta h3'));
  $('#reset-filters').click();
  input('#search', 'Consejo 7');
  assert.equal(count(), 1);
  assert.equal($('.resource-card').dataset.id, 'capsula-7');
});

test('front carga las tarjetas del catálogo y busca sin acentos y por títulos alternativos', async t => {
  const { $, count, input } = await app(t);
  assert.equal(count(), total);
  assert.equal($('#resource-grid').getAttribute('aria-busy'), 'false');
  input('#search', 'conduccion del nino');
  assert.equal(count(), 1);
  assert.match($('.title-button').textContent, /Conducción/);
  input('#search', 'fe que perdura');
  assert.equal(count(), 1);
  assert.match($('.title-button').textContent, /fe sólida/);
  input('#search', 'zzzzzz-inexistente');
  assert.equal(count(), 0);
  assert.equal($('#empty-state').hidden, false);
  $('#reset-filters').click();
  assert.equal(count(), total);
});
test('filtros combinan tipo, tema y disponibilidad sin confundir muestras con libros completos', async t => {
  const { $, count, input } = await app(t);
  $('[data-filter="video"]').click();
  assert.equal(count(), catalog.videos.length);
  input('#topic', 'Comunicación', 'change');
  assert.equal(count(), catalog.videos.filter(v => v.topic === 'Comunicación').length);
  $('#reset-filters').click();
  input('#access', 'complete', 'change');
  assert.equal(count(), 4);
  $('[data-filter="video"]').click();
  assert.equal(count(), catalog.videos.length);
  assert.equal($('#access').value, 'all');
});
test('guardados persisten, se pueden filtrar y se pueden quitar', async t => {
  const { w, $, count } = await app(t);
  $('[data-save="el-hogar-cristiano"]').click();
  assert.equal($('#saved-count').textContent, '1');
  assert.deepEqual(JSON.parse(w.localStorage.getItem('entre-nosotros-guardados')), ['el-hogar-cristiano']);
  $('#saved-nav').click();
  assert.equal(count(), 1);
  $('[data-save="el-hogar-cristiano"]').click();
  assert.equal(count(), 0);
  assert.equal($('#empty-state').hidden, false);
  const restored = await app(t, { stored:'["la-educacion"]', query:'?type=saved' });
  assert.equal(restored.count(), 1);
  assert.match(restored.$('.title-button').textContent, /La educación/);
});
test('detalle ofrece lectura oficial sin fichas técnicas y restaura foco al cerrar', async t => {
  const { w, $ } = await app(t);
  const opener = $('[data-open="el-hogar-cristiano"]');
  opener.focus(); opener.click();
  assert.equal($('#resource-dialog').open, true);
  assert.equal($('#dialog-title').textContent, 'El hogar cristiano');
  assert.ok($('#dialog-content a[href="https://www.egwwritings.org/es/book/177"]'));
  assert.equal($('#dialog-content a[href$=".md"]'), null);
  assert.doesNotMatch($('#dialog-content').textContent, /ficha MD|presentación|bibliografía original/i);
  assert.equal(new URL(w.location.href).searchParams.get('recurso'), 'el-hogar-cristiano');
  $('#close-dialog').click();
  assert.equal($('#resource-dialog').open, false);
  assert.equal(w.document.activeElement, opener);
});
test('enlace directo abre el video correcto y el marcador se sincroniza en el modal', async t => {
  const { w, $ } = await app(t, { query:'?recurso=video-final' });
  assert.equal($('#resource-dialog').open, true);
  assert.equal($('video source').getAttribute('src'), '/media/videos-libros/03-refuerzo/final.mp4');
  assert.equal($('video').hasAttribute('autoplay'), false);
  $('#dialog-save').click();
  assert.equal($('#dialog-save').getAttribute('aria-pressed'), 'true');
  $('#close-dialog').click();
  assert.equal(new URL(w.location.href).searchParams.has('recurso'), false);
});
test('carga fallida muestra error y permite reintentar', async t => {
  const { w, $, count } = await app(t, { fail:true });
  assert.equal($('#error-state').hidden, false);
  assert.equal(count(), 0);
  w.fetch = async () => ({ ok:true, json:async () => catalog });
  $('#retry').click();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(count(), total);
  assert.equal($('#error-state').hidden, true);
});
test('las 15 preguntas se expanden y los datos HTML no se ejecutan', async t => {
  const { w, $, count } = await app(t);
  assert.equal(w.document.querySelectorAll('#questions details').length, 5);
  $('#more-questions').click();
  assert.equal(w.document.querySelectorAll('#questions details').length, 15);
  assert.equal($('#more-questions').getAttribute('aria-expanded'), 'true');
  const altered = structuredClone(catalog);
  altered.books[0].title = '<img src=x onerror="alert(1)">';
  w.fetch = async () => ({ ok:true, json:async () => altered });
  $('#retry').click();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(count(), total);
  assert.equal($('[data-id="el-hogar-cristiano"] .title-button').textContent, '<img src=x onerror="alert(1)">');
  assert.equal($('.title-button img'), null);
});

test('videos primero, lector PDF disponible y Amazon sin botón de compra', async t => {
  const { w, $ } = await app(t);
  assert.equal($('.resource-group').classList.contains('video-group'), true);
  $('[data-open="el-hogar-cristiano"]').click();
  assert.match($('#dialog-content a.button.primary').href, /leer.html\?libro=el-hogar-cristiano/);
  assert.match($('#dialog-content a.button.secondary').href, /pdf\/el-hogar-cristiano.pdf/);
  $('#close-dialog').click();
  const commercial = catalog.books.find(b => b.links.some(l => l.kind === 'purchase'));
  $(`[data-open="${commercial.id}"]`).click();
  assert.equal($('#dialog-content [data-purchase]').classList.contains('button'), false);
  $('#close-dialog').click();
  const withoutVideos = structuredClone(catalog);
  withoutVideos.videos = [{...catalog.videos[0],status:'draft'}];
  w.fetch = async () => ({ok:true,json:async () => withoutVideos});
  $('#retry').click();
  await new Promise(resolve => setImmediate(resolve));
  assert.ok($('.video-pending'));
  assert.equal($('.video-card'), null);
  assert.equal($('#featured-video').hidden, true);
  assert.equal($('#hero-upcoming').hidden, false);
  assert.equal($('.hero-visual').hidden, false);
  assert.equal($('#error-state').hidden, true);
});

test('navegación para lectores: libros completos accesibles desde las tarjetas, sin lenguaje del evento', async t => {
  const { w, $, count } = await app(t);
  $('[data-jump="book"]').click();
  assert.equal(count(), catalog.books.length);
  assert.equal($('.video-card'), null);
  assert.ok($('#referencias'));
  const links = [...w.document.querySelectorAll('.read-book')];
  assert.equal(links.length, catalog.books.filter(b => b.documents.length).length);
  for (const link of links) {
    assert.equal(link.textContent.trim(), 'Leer libro');
    assert.match(link.href, /leer.html\?libro=/);
  }
  assert.equal(w.document.querySelectorAll('.pdf-direct').length, links.length);
  $('[data-jump="video"]').click();
  assert.equal(count(), catalog.videos.length);
  assert.equal($('#access').hidden, true);
  $('#reset-filters').click();
  $('#more-questions').click();
  assert.doesNotMatch(w.document.body.textContent, /Denny|Perales|reunión|junta|presentación|ponente|diapositiva|dijiste|mencionaste|ficha MD/i);
  for (const book of catalog.books) {
    $(`[data-open="${book.id}"]`).click();
    assert.doesNotMatch($('#dialog-content').textContent, /Denny|Perales|reunión|junta|presentación|ponente|diapositiva|ficha MD/i);
    $('#close-dialog').click();
  }
});

function seriesCatalog() {
  const data = structuredClone(catalog);
  const base = data.videos[0];
  data.videos = [
    {...base,id:'capsule',group:'junta',orientation:'horizontal',order:1},
    {...base,id:'today',group:'refuerzo',duration:59.8,order:100},
    {...base,id:'summary',group:'resumen',orientation:'horizontal',order:201},
    ...[3,1,2].map(episode => ({...base,id:`episode-${episode}`,title:`Idea ${episode}`,group:'serie',series:base.book,episode,of:3,order:300+episode})),
    {...base,id:'private-episode',group:'serie',series:base.book,episode:4,of:4,status:'draft'},
    {...base,id:'other-series',group:'serie',book:'la-educacion',series:'la-educacion',episode:1,of:3},
  ];
  return data;
}

test('colecciones agrupan por group y el filtro se conserva en el enlace', async t => {
  const {w,$,count} = await app(t, {data:seriesCatalog()});
  assert.deepEqual([...w.document.querySelectorAll('.video-group')].map(node => node.id), ['junta','refuerzo','resumen','serie']);
  assert.equal($('[data-id="today"] .duration').textContent, '1:00');
  $('[data-group="serie"]').click();
  assert.equal(count(), 2);
  assert.match($('#results-count').textContent, /2 series \(4 episodios\)/);
  assert.equal(new URL(w.location.href).searchParams.get('group'), 'serie');
  assert.equal(w.document.querySelectorAll('.video-group').length, 1);
  $('[data-filter="book"]').click();
  assert.equal(count(), catalog.books.length);
  assert.equal($('#video-groups').hidden, true);
  const restored = await app(t, {data:seriesCatalog(),query:'?type=video&group=resumen'});
  assert.equal(restored.count(), 1);
  assert.equal(restored.$('.resource-card').dataset.id, 'summary');
});

test('colección de libros combina formato, tema y libro y restaura la selección desde URL', async t => {
  const data = seriesCatalog();
  data.videos.find(video => video.id === 'other-series').topic = 'Educación';
  const {w,$,count,input} = await app(t, {data});
  $('[data-group="libros"]').click();
  assert.equal($('[data-id="capsule"]'), null);
  assert.equal(count(), 4); // Para hoy, resumen y dos series.
  $('[data-topic="Comunicación"]').click();
  assert.equal(count(), 3);
  assert.equal(w.document.activeElement.dataset.topic, 'Comunicación');
  input('#related-book', 'el-hogar-cristiano', 'change');
  $('[data-group="resumen"]').click();
  assert.equal(count(), 1);
  assert.equal($('.resource-card').dataset.id, 'summary');
  const restored = await app(t, {data,query:w.location.search});
  assert.equal(restored.count(), 1);
  assert.equal(restored.$('#related-book').value, 'el-hogar-cristiano');
  assert.equal(restored.$('[data-topic="Comunicación"]').getAttribute('aria-pressed'), 'true');
  assert.equal(restored.$('[data-group="resumen"]').getAttribute('aria-pressed'), 'true');
  $('#clear-selection').click();
  assert.equal($('#related-book').value, 'all');
  assert.equal($('#topic').value, 'all');
  assert.equal(new URL(w.location.href).searchParams.get('type'), 'video');
  assert.equal(count(), 5);
});

test('serie presenta una tarjeta con episodios ordenados y permite abrir y guardar cada uno', async t => {
  const {w,$,count} = await app(t, {data:seriesCatalog(),query:'?type=video&group=serie'});
  assert.equal(count(), 2);
  const series = $('.series-card');
  assert.equal(series.querySelector('h4').textContent, 'El hogar cristiano');
  assert.deepEqual([...series.querySelectorAll('.episode-open')].map(button => button.dataset.open), ['episode-1','episode-2','episode-3']);
  assert.match($('[data-series="la-educacion"] .series-count').textContent, /1 de 3 episodios disponibles/);
  series.querySelector('details').open = true;
  series.querySelector('[data-save="episode-2"]').click();
  assert.equal($('.series-card details').open, true);
  const opener = $('.series-card .episode-open[data-open="episode-2"]');
  opener.focus(); opener.click();
  assert.equal($('#dialog-title').textContent, 'Idea 2');
  $('#close-dialog').click();
  assert.equal(w.document.activeElement, opener);
  $('#saved-nav').click();
  $('[data-group="serie"]').click();
  assert.equal(new URL(w.location.href).searchParams.get('type'), 'saved');
  assert.equal(count(), 1);
  assert.match($('.series-count').textContent, /1 de 3 episodios coinciden/);
  assert.equal($('.series-start').dataset.open, 'episode-2');
  assert.equal($('.episode-open[data-open="episode-1"]'), null);
  assert.match($('#results-count').textContent, /1 serie \(1 episodio\)/);
});

test('búsqueda de libro encuentra sus episodios sin duplicar la serie; búsqueda de episodio conserva solo coincidencias', async t => {
  const {w,$,count,input} = await app(t, {data:seriesCatalog(),query:'?type=video&group=serie'});
  input('#search', 'hogar cristiano');
  assert.equal(count(), 1);
  assert.equal(w.document.querySelectorAll('.episode-open').length, 3);
  input('#search', 'Idea 3');
  assert.equal(count(), 1);
  assert.equal(w.document.querySelectorAll('.episode-open').length, 1);
  assert.equal($('.series-start').dataset.open, 'episode-3');
  assert.equal($('.series-start').textContent.trim(), 'Ver episodio 3');
  input('#search', 'sin coincidencias');
  assert.equal(count(), 0);
  assert.equal($('#empty-state').hidden, false);
});

test('serie navega en orden, excluye borradores y otras series, y sugiere sin reproducir automáticamente', async t => {
  const {w,$} = await app(t, {data:seriesCatalog(),query:'?recurso=episode-1'});
  assert.equal($('#resource-dialog').classList.contains('vertical-dialog'), true);
  assert.deepEqual([...w.document.querySelectorAll('.episode-list button')].map(button => button.textContent), ['1/3','2/3','3/3']);
  assert.equal($('.episode-list [aria-current]').textContent, '1/3');
  assert.equal($('#next-episode').hidden, true);
  let paused = 0;
  $('video').pause = () => { paused++; };
  $('video').dispatchEvent(new w.Event('ended'));
  assert.equal($('#next-episode').hidden, false);
  assert.equal($('#dialog-title').textContent, 'Idea 1');
  $('#next-episode [data-open="episode-2"]').click();
  assert.equal(paused, 1);
  assert.equal($('#dialog-title').textContent, 'Idea 2');
  assert.equal(new URL(w.location.href).searchParams.get('recurso'), 'episode-2');
  assert.equal($('video').autoplay, false);
  $('.episode-arrows [data-open="episode-1"]').click();
  assert.equal($('#dialog-title').textContent, 'Idea 1');
  $('.episode-list [data-open="episode-3"]').click();
  assert.equal($('#next-episode'), null);
});

test('libro y videos se enlazan en ambos sentidos sin perder el foco original', async t => {
  const {w,$} = await app(t, {data:seriesCatalog()});
  const opener = $('[data-id="el-hogar-cristiano"] .related-count');
  opener.focus(); opener.click();
  assert.ok($('.related-videos [data-open="summary"]'));
  assert.ok($('.related-videos [data-open="episode-1"]'));
  assert.equal($('.related-videos [data-open="private-episode"]'), null);
  assert.equal($('.related-videos [data-open="other-series"]'), null);
  $('.related-videos [data-open="episode-1"]').click();
  assert.ok($('.book-context-nav [data-open="el-hogar-cristiano"]'));
  assert.match($('.book-context-nav a').href, /leer.html\?libro=el-hogar-cristiano/);
  $('.book-context-nav [data-open="summary"]').click();
  assert.equal(new URL(w.location.href).searchParams.get('recurso'), 'summary');
  $('#dialog-content [data-open="el-hogar-cristiano"]').click();
  assert.equal($('#dialog-title').textContent, 'El hogar cristiano');
  $('#close-dialog').click();
  assert.equal(w.document.activeElement, opener);
});
