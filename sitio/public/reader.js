const $ = selector => document.querySelector(selector);
let book;
let request;
let loadId = 0;
let editionReady = false;
const mobileReader = window.matchMedia?.('(max-width: 850px), (any-pointer: coarse)');

function useDirectReader() {
  return mobileReader?.matches || navigator.pdfViewerEnabled === false;
}

function renderReaderMode() {
  if (!book?.documents?.length) return;
  const direct = useDirectReader();
  const edition = book.documents.find(item => item.id === $('#edition').value);
  document.body.classList.toggle('reader-direct', direct);
  $('#reader-mobile-note').hidden = !direct;
  $('#reader-return').hidden = !direct;
  $('#reader-hint').hidden = direct || !editionReady;
  $('#open-pdf').textContent = direct ? 'Leer PDF a pantalla completa' : 'Abrir PDF';
  // Un enlace normal, en la misma pestaña, no depende del visor incrustado ni de ventanas emergentes.
  $('#open-pdf').target = direct ? '_self' : '_blank';
  const frame = $('#pdf-frame');
  frame.hidden = direct || !editionReady;
  if (frame.hidden) frame.removeAttribute('src');
  else {
    const src = edition.url + '#view=FitH';
    frame.title = `${book.title} · ${edition.label}`;
    if (frame.getAttribute('src') !== src) frame.src = src;
  }
}

function showError(message) {
  editionReady = false;
  renderReaderMode();
  $('#reader-status').hidden = true;
  $('#pdf-frame').hidden = true;
  $('#reader-error').hidden = false;
  $('#reader-error-message').textContent = message;
}

async function openEdition() {
  const edition = book.documents.find(item => item.id === $('#edition').value);
  if (!edition) return;
  editionReady = false;
  request?.abort();
  request = new AbortController();
  const currentLoad = ++loadId;
  const timeout = setTimeout(() => { if (loadId === currentLoad) request.abort(); }, 20000);
  const url = new URL(location.href);
  url.searchParams.set('edicion', edition.id);
  history.replaceState(null, '', url);
  for (const selector of ['#open-pdf', '#hint-open-pdf']) $(selector).href = edition.url;
  $('#download-pdf').href = edition.url + '?download=1';
  for (const selector of ['#official-source', '#error-official']) { $(selector).href = edition.source; $(selector).hidden = false; }
  $('#reader-error').hidden = true;
  $('#pdf-frame').hidden = true;
  $('#pdf-frame').removeAttribute('src');
  $('#reader-status').hidden = false;
  $('#reader-status').textContent = 'Comprobando disponibilidad del libro…';
  renderReaderMode();
  try {
    // La vista de revisión en archivo usa los originales locales sin HTTP.
    if (location.protocol !== 'file:') {
      const response = await fetch(edition.url, { method:'HEAD', signal:request.signal });
      if (!response.ok || !/^application\/pdf(?:;|$)/i.test(response.headers.get('Content-Type') || '')) throw new Error('PDF no disponible');
    }
    if (loadId !== currentLoad) return;
    editionReady = true;
    renderReaderMode();
    $('#reader-status').hidden = true;
  } catch {
    if (loadId === currentLoad) showError('No se pudo cargar el documento en este momento. Intenta de nuevo o abre el PDF oficial.');
  } finally { clearTimeout(timeout); }
}

async function loadReader() {
  try {
    const response = await fetch('/catalog.json');
    if (!response.ok) throw new Error('Catálogo no disponible');
    const catalog = await response.json();
    const params = new URLSearchParams(location.search);
    book = catalog.books.find(item => item.id === params.get('libro'));
    if (!book?.documents?.length) {
      $('#reader-title').textContent = 'Referencia no disponible';
      $('#retry-pdf').hidden = true;
      showError('Este enlace no corresponde a un libro con PDF disponible. Vuelve al catálogo para elegir una referencia.');
      return;
    }
    document.title = `${book.title} · Lectura`;
    $('#reader-title').textContent = book.title;
    $('#reader-author').textContent = book.author;
    $('#reader-back').href = '/?type=book#referencias';
    $('#edition').replaceChildren(...book.documents.map(item => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.label;
      return option;
    }));
    const selected = book.documents.find(item => item.id === params.get('edicion')) || book.documents[0];
    $('#edition').value = selected.id;
    $('#edition').hidden = book.documents.length === 1;
    $('#edition-label').hidden = book.documents.length === 1;
    $('#reader-controls').hidden = book.documents.length === 1;
    for (const selector of ['#reader-launch', '#reader-source']) $(selector).hidden = false;
    $('#edition').onchange = openEdition;
    await openEdition();
  } catch {
    $('#reader-title').textContent = 'Lectura no disponible';
    showError('No pudimos cargar la información del libro. Revisa tu conexión y vuelve a intentar.');
  }
}

$('#retry-pdf').onclick = () => { if (book?.documents?.length) openEdition(); else loadReader(); };
$('#pdf-frame').onerror = () => showError('El visor no pudo mostrar este archivo. Usa Abrir PDF o el enlace a la fuente oficial.');
mobileReader?.addEventListener('change', renderReaderMode);
loadReader();
