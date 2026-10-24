import { createPDFReader } from './pdf-reader.js';

const $ = selector => document.querySelector(selector);
const pdfReader = createPDFReader($('#pdf-page'));
let book;
let videos = [];
let edition;
let totalPages = 0;
let page = 1;
let activeView = 'read';
let selectedVideo;
let initialPage;
let loadId = 0;
let paintId = 0;
let resizeTimer;

function updateURL() {
  const url = new URL(location.href);
  url.searchParams.set('vista', activeView);
  if (edition) { url.searchParams.set('edicion', edition.id); url.searchParams.set('pagina', page); }
  if (selectedVideo) url.searchParams.set('video', selectedVideo.id);
  history.replaceState(null, '', url);
}

function storedPage(id) {
  try { return Math.max(1, Number(localStorage.getItem(`entre-nosotros-pagina-${id}`)) || 1); }
  catch { return 1; }
}

function showError(message) {
  $('#reader-status').hidden = true;
  $('#reader-error').hidden = false;
  $('#reader-error-message').textContent = message;
  $('#pdf-page').setAttribute('aria-busy', 'false');
}

async function paintPage(scroll = false) {
  if (!totalPages || activeView !== 'read') return;
  const current = ++paintId;
  $('#pdf-page').setAttribute('aria-busy', 'true');
  $('#reader-error').hidden = true;
  $('#page-number').value = page;
  $('#previous-page').disabled = page <= 1;
  $('#next-page').disabled = page >= totalPages;
  const text = $('#reading-mode').value === 'text';
  $('#zoom').hidden = text;
  try {
    const rendered = await pdfReader.render(page, {zoom:Number($('#zoom').value), text});
    if (current !== paintId || !rendered) return;
    $('#pdf-page').setAttribute('aria-busy', 'false');
    $('#reader-status').hidden = true;
    try { localStorage.setItem(`entre-nosotros-pagina-${edition.id}`, String(page)); } catch { /* Lectura disponible sin almacenamiento. */ }
    updateURL();
    if (scroll) $('#pdf-page').scrollIntoView({block:'start', behavior:'instant'});
  } catch {
    if (current === paintId) showError('No pudimos dibujar esta página. Intenta de nuevo; también puedes abrir o descargar el PDF original.');
  }
}

async function openEdition(requestedPage = initialPage) {
  initialPage = null;
  edition = book.documents.find(item => item.id === $('#edition').value);
  if (!edition) return;
  const current = ++loadId;
  ++paintId;
  totalPages = 0;
  page = Math.max(1, Math.floor(Number(requestedPage) || storedPage(edition.id)));
  $('#open-pdf').href = edition.url;
  $('#download-pdf').href = edition.url + '?download=1';
  $('#official-source').href = edition.source;
  $('#reader-actions').hidden = false;
  $('#reader-error').hidden = true;
  $('#pdf-reader').hidden = true;
  $('#reader-status').hidden = false;
  $('#reader-status').textContent = 'Preparando las páginas del libro…';
  updateURL();
  if (location.protocol === 'file:') {
    showError('La lectura integrada necesita el sitio web o el servidor local. En esta vista previa puedes abrir el PDF original.');
    return;
  }
  const timeout = setTimeout(() => {
    if (loadId === current) {
      ++loadId;
      pdfReader.destroy();
      showError('La carga está tardando demasiado. Revisa tu conexión y vuelve a intentar.');
    }
  }, 30000);
  try {
    const count = await pdfReader.open(edition.url);
    if (current !== loadId || !count) return;
    totalPages = count;
    page = Math.min(page, totalPages);
    $('#page-number').max = totalPages;
    $('#page-total').textContent = `de ${totalPages}`;
    $('#pdf-reader').hidden = false;
    $('#reader-status').hidden = true;
    await paintPage();
  } catch {
    if (current === loadId) showError('No pudimos cargar el PDF. Vuelve a intentar o usa el original; los videos y la ficha siguen disponibles.');
  } finally { clearTimeout(timeout); }
}

function selectVideo(id) {
  const video = videos.find(item => item.id === id);
  if (!video) return;
  const player = $('#reader-video');
  player.pause();
  selectedVideo = video;
  player.src = '/media/' + video.file.split('/').map(encodeURIComponent).join('/');
  player.poster = video.poster;
  player.setAttribute('aria-label', video.title);
  $('#video-direct').href = player.src;
  $('#video-error').hidden = true;
  $('#reader-video-title').textContent = video.title;
  $('#reader-video-description').textContent = video.description;
  $('#book-player').hidden = false;
  $('#resume-reading').hidden = !book.documents.length;
  for (const button of document.querySelectorAll('[data-video]')) button.setAttribute('aria-current', String(button.dataset.video === id));
  player.load();
  updateURL();
}

function setView(view, scroll = false) {
  if (!['read', 'videos', 'details'].includes(view)) return;
  if (view === 'read' && !book.documents.length) view = 'details';
  if (view === 'videos' && !videos.length) view = 'details';
  if (activeView === 'videos' && view !== 'videos') $('#reader-video').pause();
  activeView = view;
  for (const name of ['read', 'videos', 'details']) $(`#${name}-panel`).hidden = name !== view;
  for (const button of document.querySelectorAll('#book-nav [data-view]')) {
    if (button.dataset.view === view) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
  updateURL();
  if (view === 'videos' && !selectedVideo) selectVideo(videos[0].id);
  if (view === 'read') {
    if (totalPages) paintPage();
    else openEdition();
  }
  if (scroll) $('#book-nav').scrollIntoView({block:'start', behavior:'instant'});
}

function renderVideos() {
  const list = $('#book-video-list');
  list.replaceChildren();
  for (const [group, label] of [['resumen','Resumen del libro'], ['refuerzo','Ideas para poner en práctica'], ['serie','Serie por episodios'], ['junta','Conversaciones']]) {
    const items = videos.filter(item => item.group === group);
    if (!items.length) continue;
    const heading = document.createElement('h3');
    heading.textContent = label;
    list.append(heading);
    for (const video of items) {
      const button = document.createElement('button');
      button.className = 'reader-video-item';
      button.dataset.video = video.id;
      const image = document.createElement('img');
      image.src = video.poster; image.alt = ''; image.loading = 'lazy';
      const body = document.createElement('span');
      const title = document.createElement('strong'); title.textContent = video.title;
      const detail = document.createElement('small');
      const seconds = Math.round(video.duration);
      detail.textContent = `${video.episode ? `Episodio ${video.episode} de ${video.of} · ` : ''}${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')} · Ver video`;
      body.append(title, detail); button.append(image, body); list.append(button);
    }
  }
}

async function loadReader() {
  try {
    const response = await fetch('/catalog.json');
    if (!response.ok) throw new Error('Catálogo no disponible');
    const catalog = await response.json();
    const params = new URLSearchParams(location.search);
    initialPage = params.get('pagina');
    book = catalog.books.find(item => item.id === params.get('libro'));
    if (!book) {
      $('#reader-title').textContent = 'Libro no disponible';
      $('#retry-pdf').hidden = true;
      showError('Este enlace no corresponde a un libro. Vuelve a la biblioteca para elegir uno.');
      return;
    }
    book.documents ||= [];
    const order = {resumen:0, refuerzo:1, serie:2, junta:3};
    videos = catalog.videos.filter(video => video.book === book.id && video.status === 'published').sort((a,b) => (order[a.group] ?? 4) - (order[b.group] ?? 4) || (a.episode || a.order || 0) - (b.episode || b.order || 0));
    document.title = `${book.title} · Leer y explorar`;
    $('#reader-title').textContent = book.title;
    $('#reader-author').textContent = book.author;
    $('#reader-back').href = `/?type=book&recurso=${encodeURIComponent(book.id)}`;
    $('#catalog-details').href = $('#reader-back').href;
    $('#detail-title').textContent = book.title;
    $('#detail-description').textContent = book.description;
    $('#detail-meta').replaceChildren();
    for (const [label,value] of [['Autor',book.author],['Editorial',book.publisher],['Edición',book.year],['Tema',book.topic]]) {
      const term = document.createElement('dt'); term.textContent = label;
      const detail = document.createElement('dd'); detail.textContent = value;
      $('#detail-meta').append(term, detail);
    }
    $('#edition').replaceChildren(...book.documents.map(item => {
      const option = document.createElement('option'); option.value = item.id; option.textContent = item.label; return option;
    }));
    const selected = book.documents.find(item => item.id === params.get('edicion')) || book.documents[0];
    if (selected) $('#edition').value = selected.id;
    $('#reader-controls').hidden = book.documents.length < 2;
    for (const button of document.querySelectorAll('[data-view="read"]')) button.disabled = !selected;
    for (const button of document.querySelectorAll('[data-view="videos"]')) button.disabled = !videos.length;
    $('#video-count').textContent = `(${videos.length})`;
    renderVideos();
    $('#book-nav').hidden = false;
    activeView = params.get('vista') || (selected ? 'read' : 'videos');
    if (!['read','videos','details'].includes(activeView)) activeView = 'read';
    if (activeView === 'read' && selected) {
      await openEdition(params.get('pagina'));
    } else {
      setView(activeView);
      if (activeView === 'videos' && videos.some(video => video.id === params.get('video'))) selectVideo(params.get('video'));
    }
  } catch {
    showError('No pudimos cargar la información del libro. Revisa tu conexión y vuelve a intentar.');
  }
}

function goToPage(value) {
  if (!totalPages || !Number.isFinite(Number(value))) return;
  page = Math.min(totalPages, Math.max(1, Math.floor(Number(value))));
  paintPage(true);
}
$('#previous-page').onclick = () => goToPage(page - 1);
$('#next-page').onclick = () => goToPage(page + 1);
$('#page-form').onsubmit = event => { event.preventDefault(); goToPage($('#page-number').value); };
$('#reading-mode').onchange = () => paintPage();
$('#zoom').onchange = () => paintPage();
$('#edition').onchange = () => openEdition();
$('#retry-pdf').onclick = () => book ? openEdition(page) : loadReader();
$('#reader-video').onerror = () => { $('#video-error').hidden = false; };
$('#resume-reading').onclick = () => setView('read', true);
document.addEventListener('click', event => {
  const tab = event.target.closest('[data-view]');
  if (tab && !tab.disabled) setView(tab.dataset.view, true);
  const video = event.target.closest('[data-video]');
  if (video) { selectVideo(video.dataset.video); $('#book-player').scrollIntoView({block:'start'}); }
});
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => paintPage(), 150); });
loadReader();
