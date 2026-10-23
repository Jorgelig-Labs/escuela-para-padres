const $ = selector => document.querySelector(selector);
const paths = {
  arrow: '<path d="M4 12h15m-6-6 6 6-6 6"/>',
  book: '<path d="M12 5v15M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2Z"/>',
  bookmark: '<path d="M6 3h12v18l-6-4-6 4Z"/>',
  play: '<path d="m9 5 11 7-11 7Z"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  plus: '<path d="M5 12h14M12 5v14"/>',
  heart: '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0l-1 1-1-1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
  chat: '<path d="M21 11a9 9 0 0 1-13 8l-5 2 1-5A9 9 0 1 1 21 11Z"/><path d="M8 10h8m-8 4h5"/>',
  spark: '<path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3Z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/>',
  link: '<path d="m10 13 4-4m-6 6-2 2a4 4 0 0 1-5-5l4-4a4 4 0 0 1 6 0m2 1 2-2a4 4 0 0 1 6 5l-4 4a4 4 0 0 1-6 0" transform="translate(1 -1)"/>',
};
const icon = name => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.book}</svg>`;
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const duration = seconds => { const total = Math.round(seconds); return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`; };
const videoGroups = [
  { id:'junta', title:'Cápsulas', description:'Una pausa para entendernos mejor y abrir nuevas conversaciones.' },
  { id:'refuerzo', title:'Para hoy', description:'Una idea breve y una acción pequeña para poner en práctica.' },
  { id:'resumen', title:'Resúmenes de libros', description:'Conoce las ideas de cada libro y elige en cuál profundizar.' },
  { id:'serie', title:'Series', description:'Tres episodios por libro. Sigue las ideas, un paso a la vez.' },
];
const groupLabels = Object.fromEntries(videoGroups.map(group => [group.id, group.title]));
const bookVideoGroups = ['refuerzo', 'resumen', 'serie'];
const videoPath = item => item.file.split('/').map(encodeURIComponent).join('/');
const accessLabels = { complete:'Lectura completa gratis', sample:'Muestra gratis', purchase:'Disponible en librerías' };
let catalog;
let resources = [];
let currentFilter = 'all';
let currentGroup = 'all';
let refinementsOpen = false;
const mobileLayout = window.matchMedia?.('(max-width: 600px)');
let showAllQuestions = false;
let toastTimer;
let activeResource = null;
let dialogOpener = null;
let saved = new Set();
try {
  const stored = JSON.parse(localStorage.getItem('entre-nosotros-guardados') || '[]');
  if (Array.isArray(stored)) saved = new Set(stored.filter(id => typeof id === 'string'));
} catch { /* La biblioteca funciona también sin almacenamiento local. */ }

document.querySelectorAll('[data-icon]').forEach(node => { node.innerHTML = icon(node.dataset.icon); });

function notify(message) {
  clearTimeout(toastTimer);
  $('#toast').textContent = message;
  $('#toast').classList.add('visible');
  toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 3500);
}

function cover(book) {
  return `<div class="book-cover" aria-hidden="true"><span class="cover-number">BIBLIOTECA · ${String(book.order).padStart(2, '0')}</span><span class="cover-decoration"></span><span class="cover-title ${book.title.length > 33 ? 'long' : ''}">${escape(book.title)}</span><span class="cover-rule"></span><span class="cover-author">${escape(book.author)}</span></div>`;
}

function saveButton(item) {
  const isSaved = saved.has(item.id);
  return `<button class="bookmark-button" data-save="${item.id}" aria-pressed="${isSaved}" aria-label="${isSaved ? 'Quitar de guardados' : 'Guardar'}: ${escape(item.title)}">${icon('bookmark')}</button>`;
}

function cardAction(item) {
  if (item.type === 'book' && item.documents?.length) return `<div class="reading-actions"><a class="button primary read-book" href="${readerURL(item)}">${icon('book')} Leer libro</a><a class="pdf-direct" href="${escape(item.documents[0].url)}" target="_blank" rel="noopener noreferrer">Abrir PDF ↗</a></div>`;
  const sample = item.type === 'book' && item.access === 'sample' && item.links.find(link => link.kind === 'read');
  if (sample) return `<a class="button secondary" href="${escape(sample.url)}" target="_blank" rel="noopener noreferrer">Leer muestra ${icon('arrow')}</a>`;
  const label = item.type === 'book' ? 'Acerca del libro' : 'Ver video';
  return `<button class="card-action" data-open="${item.id}">${label}${icon('arrow')}</button>`;
}

function card(item) {
  const isBook = item.type === 'book';
  const visual = isBook
    ? `<button class="card-visual book-visual palette-${item.palette}" data-open="${item.id}" aria-label="Acerca de ${escape(item.title)}">${cover(item)}</button>`
    : `<button class="card-visual video-visual ${item.orientation === 'vertical' ? 'vertical' : ''}" data-open="${item.id}" aria-label="Reproducir ${escape(item.title)}"><img src="${escape(item.poster)}" alt="" loading="lazy" width="${item.orientation === 'vertical' ? 540 : 960}" height="${item.orientation === 'vertical' ? 960 : 540}"><span class="play-circle">${icon('play')}</span><span class="duration">${duration(item.duration)}</span><span class="video-label">${escape(item.label || groupLabels[item.group] || 'Video')}${item.episode ? ` · ${item.episode}/${item.of}` : ''}</span></button>`;
  return `<article class="resource-card ${isBook ? 'book-card' : 'video-card'}" data-id="${item.id}">${visual}${saveButton(item)}<div class="card-content"><div class="card-topic"><span>${icon(isBook ? 'book' : 'play')}${isBook ? 'LIBRO' : 'VIDEO'}</span><span>${escape(item.topic)}</span></div><h4 class="card-title"><button class="title-button" data-open="${item.id}">${escape(item.title)}</button></h4><p class="card-author">${escape(item.author)}</p><p class="card-description">${escape(item.description)}</p><div class="card-bottom"><span class="access-badge ${isBook ? item.access : ''}">${isBook ? accessLabels[item.access] : 'Para ver en familia'}</span>${cardAction(item)}</div>${isBook && relatedVideos(item).length ? `<button class="related-count" data-open="${item.id}">${icon('play')} Ver ${relatedVideos(item).length} videos de este libro</button>` : ''}</div></article>`;
}

function updateURL() {
  const url = new URL(location.href);
  const values = { q: $('#search').value.trim(), type: currentFilter, topic: $('#topic').value, access: $('#access').value, group:currentGroup, book:$('#related-book').value };
  for (const [key, value] of Object.entries(values)) {
    if (value && value !== 'all') url.searchParams.set(key, value);
    else url.searchParams.delete(key);
  }
  history.replaceState(null, '', url);
}

function render() {
  if (!catalog) return;
  const expandedSeries = [...document.querySelectorAll('.series-card:has(details[open])')].map(card => card.dataset.series);
  const query = normalize($('#search').value.trim());
  const topic = $('#topic').value;
  const access = $('#access').value;
  const book = $('#related-book').value;
  const visible = resources.filter(item => {
    const typeMatch = currentFilter === 'all' || currentFilter === item.type || (currentFilter === 'saved' && saved.has(item.id));
    const reference = catalog.books.find(reference => reference.id === item.book);
    const searchMatch = normalize([item.title, item.author, item.topic, item.description, reference?.title, ...(reference?.aliases || []), ...(item.aliases || [])].join(' ')).includes(query);
    const groupMatch = currentGroup === 'all' || (item.type === 'video' && (currentGroup === 'libros' ? bookVideoGroups.includes(item.group) : item.group === currentGroup));
    const bookMatch = book === 'all' || (item.type === 'book' ? item.id === book : item.book === book);
    return typeMatch && searchMatch && groupMatch && bookMatch && (topic === 'all' || item.topic === topic) && (access === 'all' || item.access === access);
  });
  renderGroupFilters();
  renderTopicFilters();
  const sections = [];
  const overview = ['all', 'libros'].includes(currentGroup) && currentFilter !== 'saved' && !query && topic === 'all' && book === 'all';
  for (const group of videoGroups) {
    const items = visible.filter(item => item.type === 'video' && item.group === group.id);
    if (items.length) {
      sections.push(group.id === 'serie' ? seriesSection(items, overview) : resourceSection(group.id, group.title, group.description, items, overview));
    }
  }
  const ungrouped = visible.filter(item => item.type === 'video' && !videoGroups.some(group => group.id === item.group));
  if (ungrouped.length) sections.push(resourceSection('videos', 'Más videos', 'Ideas para compartir en familia.', ungrouped));
  if (!catalog.videos.length && ['all', 'video'].includes(currentFilter) && !query && topic === 'all' && access === 'all') sections.push(`<section id="videos" class="resource-group video-group video-pending"><div class="pending-icon">${icon('play')}</div><div><span class="eyebrow">PRÓXIMAMENTE</span><h3>Un espacio para ver y aprender.</h3><p>Estamos preparando nuevos clips y videos para acompañarte en la vida en familia.</p></div><a href="#referencias" data-jump="book">Mientras tanto, explora las lecturas ${icon('arrow')}</a></section>`);
  const books = visible.filter(item => item.type === 'book');
  if (books.length) sections.push(resourceSection('referencias', 'Un libro para ir más allá.', 'Lecturas que acompañan los videos. Abre el libro completo aquí o consulta una muestra cuando esté disponible.', books));
  $('#resource-grid').innerHTML = sections.join('');
  document.querySelectorAll('.series-card').forEach(card => {
    if (expandedSeries.includes(card.dataset.series)) card.querySelector('details').open = true;
  });
  $('#resource-grid').setAttribute('aria-busy', 'false');
  $('#results-count').textContent = resultSummary(visible);
  $('#saved-count').textContent = resources.filter(item => saved.has(item.id)).length;
  $('#empty-state').hidden = visible.length > 0 || (!catalog.videos.length && currentFilter === 'video' && !query && topic === 'all');
  const emptySaved = currentFilter === 'saved' && !resources.some(item => saved.has(item.id));
  $('#empty-title').textContent = emptySaved ? 'Tu próxima lectura puede empezar aquí' : 'No encontramos coincidencias';
  $('#empty-description').textContent = emptySaved ? 'Toca el marcador de un libro o video para encontrarlo después en este navegador.' : 'Prueba con otro título, autor o tema, o cambia los filtros.';
  document.querySelectorAll('[data-filter]').forEach(button => {
    const active = button.dataset.filter === currentFilter;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  $('#access').hidden = currentFilter === 'video';
  $('#related-book').hidden = currentGroup === 'junta' || currentFilter === 'book';
  $('#clear-selection').hidden = !query && topic === 'all' && access === 'all' && book === 'all' && currentGroup === 'all';
  renderRefinements();
  updateURL();
}

function renderRefinements() {
  const expanded = !mobileLayout?.matches || refinementsOpen;
  $('#refinement-panel').hidden = !expanded;
  $('#toggle-refinements').setAttribute('aria-expanded', String(expanded));
  const selected = [];
  if ($('#topic').value !== 'all') selected.push($('#topic').value);
  if ($('#related-book').value !== 'all') selected.push('1 libro');
  if ($('#access').value !== 'all') selected.push($('#access').selectedOptions[0].textContent);
  $('#refinement-label').textContent = selected.join(' · ') || 'Filtrar por tema o libro';
}

function collectionMore(id, label, remaining) {
  if (remaining <= 0) return '';
  return `<button class="collection-more" data-show-group="${id}">Ver ${remaining} más · ${escape(label)} ${icon('arrow')}</button>`;
}

function groupedSeries(videos) {
  const groups = new Map();
  for (const video of videos) {
    const key = video.series || video.id;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(video);
  }
  return [...groups.values()].map(episodes => episodes.sort((a,b) => a.episode - b.episode));
}

function resultSummary(items) {
  const episodes = items.filter(item => item.group === 'serie');
  const videos = items.filter(item => item.type === 'video' && item.group !== 'serie');
  const books = items.filter(item => item.type === 'book');
  const series = groupedSeries(episodes);
  const parts = [];
  if (videos.length) parts.push(`${videos.length} ${videos.length === 1 ? 'video' : 'videos'}`);
  if (series.length) parts.push(`${series.length} ${series.length === 1 ? 'serie' : 'series'} (${episodes.length} ${episodes.length === 1 ? 'episodio' : 'episodios'})`);
  if (books.length) parts.push(`${books.length} ${books.length === 1 ? 'libro' : 'libros'}`);
  return parts.join(' · ') || 'Sin resultados';
}

function seriesSection(videos, overview = false) {
  const groups = groupedSeries(videos);
  const shown = overview ? groups.slice(0, 2) : groups;
  return `<section id="serie" class="resource-group video-group series-group" aria-label="Series"><div class="resource-group-heading"><h3>Series para seguir paso a paso <span>${groups.length}</span></h3><p>Elige un libro y descubre sus ideas en episodios cortos, en orden.</p></div><div class="group-grid">${shown.map(seriesCard).join('')}</div>${collectionMore('serie', 'Series', groups.length - shown.length)}</section>`;
}

function seriesCard(episodes) {
  const first = episodes[0];
  const book = catalog.books.find(book => book.id === first.book);
  const allEpisodes = seriesEpisodes(first);
  const title = book?.title || first.title;
  const partial = episodes.length < allEpisodes.length;
  let count = `${episodes.length} ${episodes.length === 1 ? 'episodio disponible' : 'episodios disponibles'}`;
  if (episodes.length < first.of) count = `${episodes.length} de ${first.of} episodios disponibles`;
  if (partial) count = `${episodes.length} de ${allEpisodes.length} episodios coinciden`;
  return `<article class="resource-card series-card" data-series="${escape(first.series || first.id)}"><div class="series-card-heading"><button class="series-poster" data-open="${first.id}" aria-label="Ver episodio ${first.episode}: ${escape(title)}"><img src="${escape(first.poster)}" alt="" loading="lazy" width="540" height="960"><span class="play-circle">${icon('play')}</span></button><div><p class="eyebrow">SERIE · ${escape(book?.topic || first.topic)}</p><h4 class="card-title">${escape(title)}</h4><p class="card-author">${escape(book?.author || first.author)}</p><p class="series-count">${count} · ${duration(episodes.reduce((sum, video) => sum + video.duration, 0))} min</p></div></div><p class="series-description">${escape(book?.description || first.description)}</p><button class="button primary series-start" data-open="${first.id}">${icon('play')} ${first.episode === 1 ? 'Empezar la serie' : `Ver episodio ${first.episode}`}</button><details class="series-episodes"><summary><span>${partial ? 'Ver episodios que coinciden' : 'Elegir episodio'}</span>${icon('plus')}</summary><ol>${episodes.map(video => `<li><button class="episode-open" data-open="${video.id}"><span class="episode-number">${video.episode}</span><span>Episodio ${video.episode}<small>${duration(video.duration)} min</small></span>${icon('play')}</button>${saveButton(video)}</li>`).join('')}</ol></details>${book ? `<button class="series-book" data-open="${book.id}">${icon('book')} Acerca del libro ${icon('arrow')}</button>` : ''}</article>`;
}

function resourceSection(id, title, description, items, overview = false) {
  const kind = items[0].type === 'book' ? 'book' : 'video';
  const vertical = kind === 'video' && items.every(item => item.orientation === 'vertical');
  const shown = overview ? items.slice(0, 3) : items;
  return `<section id="${id}" class="resource-group ${kind}-group ${vertical ? 'vertical-group' : ''}" aria-label="${escape(title)}"><div class="resource-group-heading"><h3>${escape(title)} <span>${items.length}</span></h3><p>${escape(description)}</p></div><div class="group-grid">${shown.map(card).join('')}</div>${collectionMore(id, title, items.length - shown.length)}</section>`;
}

function renderGroupFilters() {
  const nav = $('#video-groups');
  nav.hidden = currentFilter === 'book' || !catalog.videos.length;
  const fromBooks = ['libros', 'refuerzo', 'resumen'].includes(currentGroup);
  const collections = [
    {id:'junta',title:'Cápsulas',shortTitle:'Cápsulas',icon:'chat',description:'Clips para reflexionar sobre la vida en familia.',items:catalog.videos.filter(video => video.group === 'junta')},
    {id:'libros',title:'Ideas de los libros',shortTitle:'De libros',icon:'book',description:'Ideas para hoy, resúmenes y series para profundizar.',items:catalog.videos.filter(video => bookVideoGroups.includes(video.group))},
    {id:'serie',title:'Series por episodios',shortTitle:'Series',icon:'play',description:'Un libro, varias ideas. Elige una serie y síguela en orden.',items:catalog.videos.filter(video => video.group === 'serie')},
  ];
  nav.innerHTML = `<div class="collection-heading"><p class="explorer-label">¿Cómo quieres explorar?</p><button class="group-filter ${currentGroup === 'all' ? 'active' : ''}" data-group="all" aria-pressed="${currentGroup === 'all'}">Todos los videos</button></div><div class="collection-options">${collections.map(collection => {
    const active = currentGroup === collection.id || (collection.id === 'libros' && fromBooks);
    const count = collection.id === 'serie' ? `${groupedSeries(collection.items).length} series · ${collection.items.length} episodios` : `${collection.items.length} videos`;
    return `<button data-group="${collection.id}" class="collection-option ${active ? 'active' : ''}" aria-pressed="${active}" ${collection.items.length ? '' : 'disabled'}><span class="collection-icon">${icon(collection.icon)}</span><strong><span class="collection-full">${collection.title}</span><span class="collection-short">${collection.shortTitle}</span></strong><span class="collection-description">${collection.description}</span><span class="collection-total">${count} ${icon('arrow')}</span></button>`;
  }).join('')}</div>${fromBooks ? `<div class="book-video-types" role="group" aria-label="Formato del video de libro"><span>Quiero ver</span>${[{id:'libros',title:'Todo del libro'}, ...videoGroups.filter(group => bookVideoGroups.includes(group.id))].map(group => `<button class="group-filter ${currentGroup === group.id ? 'active' : ''}" data-group="${group.id}" aria-pressed="${currentGroup === group.id}">${group.title}</button>`).join('')}</div>` : ''}`;
}

function renderTopicFilters() {
  $('#topic-filters').innerHTML = [...$('#topic').options].map(option => `<button class="topic-filter" data-topic="${escape(option.value)}" aria-pressed="${$('#topic').value === option.value}">${escape(option.textContent)}</button>`).join('');
}

function relatedVideos(book) {
  return catalog.videos.filter(video => video.book === book.id);
}

function bookVideos(book) {
  const videos = relatedVideos(book);
  if (!videos.length) return '';
  return `<section class="related-videos" aria-label="Videos de este libro"><h3>Explora este libro en video</h3>${videoGroups.map(group => {
    const items = videos.filter(video => video.group === group.id).sort((a,b) => (a.episode || a.order) - (b.episode || b.order));
    if (!items.length) return '';
    return `<h4>${group.title}</h4><ul>${items.map(video => `<li><button data-open="${video.id}">${icon('play')}<span>${escape(video.title)}<small>${video.episode ? `Episodio ${video.episode} de ${video.of} · ` : ''}${duration(video.duration)}</small></span>${icon('arrow')}</button></li>`).join('')}</ul>`;
  }).join('')}</section>`;
}

function toggleSaved(id) {
  if (saved.has(id)) saved.delete(id);
  else saved.add(id);
  let persisted = true;
  try { localStorage.setItem('entre-nosotros-guardados', JSON.stringify([...saved])); }
  catch { persisted = false; }
  const scrollY = window.scrollY;
  render();
  window.scrollTo({ top: scrollY, behavior:'instant' });
  const button = document.querySelector(`[data-save="${id}"]`);
  if (button) button.focus({ preventScroll:true });
  if (activeResource?.id === id) updateDialogSave();
  notify(saved.has(id) ? (persisted ? 'Guardado en este navegador para volver después.' : 'Guardado solo durante esta visita.') : 'Recurso eliminado de tus guardados.');
}

function dialogActions(item) {
  return `<div class="dialog-actions"><button class="text-button" id="dialog-save" aria-pressed="${saved.has(item.id)}">${icon('bookmark')}<span>${saved.has(item.id) ? 'Quitar de guardados' : 'Guardar para después'}</span></button><button class="text-button" id="share-resource">${icon('link')} Copiar enlace</button></div>`;
}

function updateDialogSave() {
  const button = $('#dialog-save');
  button.setAttribute('aria-pressed', String(saved.has(activeResource.id)));
  button.querySelector('span').textContent = saved.has(activeResource.id) ? 'Quitar de guardados' : 'Guardar para después';
}

function externalLink(link, primary = false) {
  return `<a class="button ${primary ? 'primary' : 'secondary'}" href="${escape(link.url)}" target="_blank" rel="noopener noreferrer">${escape(link.label)} ${icon('arrow')}</a>`;
}

function readerURL(book, document = book.documents?.[0]) {
  return `/leer.html?libro=${encodeURIComponent(book.id)}&edicion=${encodeURIComponent(document.id)}`;
}

function bookDetails(item) {
  const documents = item.documents || [];
  const readingLinks = item.links.filter(link => link.kind === 'read');
  const purchaseLinks = item.links.filter(link => link.kind === 'purchase');
  const downloadLinks = item.links.filter(link => link.kind === 'download');
  let reading = '';
  if (documents.length) {
    reading = `<div class="dialog-links"><a class="button primary" href="${readerURL(item)}">${icon('book')} Leer libro</a><a class="button secondary" href="${documents[0].url}" target="_blank" rel="noopener noreferrer">Abrir PDF original ${icon('arrow')}</a></div>`;
    if (documents.length > 1) reading += `<div class="edition-links"><span>Tomos y ediciones</span>${documents.map(document => `<a href="${readerURL(item, document)}">${escape(document.label)}</a>`).join('')}</div>`;
  } else if (readingLinks.length) {
    reading = `<div class="dialog-links">${readingLinks.map(link => externalLink(link, true)).join('')}</div>`;
  }
  const extraLinks = [...readingLinks.filter(() => documents.length), ...downloadLinks];
  const sources = extraLinks.map(link => {
    const document = documents.find(document => document.source === link.url);
    const url = document ? document.url : link.url;
    const label = link.kind === 'read' ? 'Leer en la fuente oficial' : link.label;
    return `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)}</a>`;
  }).join('');
  const stores = purchaseLinks.map(link => `<a data-purchase href="${escape(link.url)}" target="_blank" rel="noopener noreferrer">${new URL(link.url).hostname.endsWith('amazon.com.mx') ? 'Amazon México' : escape(link.label)}</a>`).join(' · ');
  return `<div class="dialog-book-hero palette-${item.palette}">${cover(item)}<div><span class="eyebrow">REFERENCIA · ${escape(item.topic)}</span><h2 id="dialog-title">${escape(item.title)}</h2><p>${escape(item.author)}</p></div></div><div class="dialog-body"><p>${escape(item.description)}</p><div class="dialog-meta"><span>${escape(item.publisher)}</span><span>Edición ${escape(item.year)}</span>${item.pages ? `<span>${item.pages} páginas</span>` : '<span>2 tomos · 2 ediciones</span>'}</div><span class="access-badge ${item.access}">${accessLabels[item.access]}</span>${reading}${sources ? `<div class="download-links">${sources}</div>` : ''}<p class="dialog-note">${documents.length ? 'PDF originales de Ellen G. White Estate. Puedes leerlos aquí o abrirlos en el visor de tu dispositivo.' : 'Las muestras, cuando están disponibles, son parciales.'}</p>${stores ? `<p class="purchase-reference">Referencia comercial: ${stores}</p>` : ''}${bookVideos(item)}${dialogActions(item)}</div>`;
}

function seriesEpisodes(item) {
  if (!item.series) return [];
  return catalog.videos.filter(video => video.group === 'serie' && video.series === item.series).sort((a,b) => a.episode - b.episode);
}

function seriesNavigation(item) {
  const episodes = seriesEpisodes(item);
  if (!episodes.length) return '';
  const index = episodes.findIndex(video => video.id === item.id);
  const previous = episodes[index - 1];
  const next = episodes[index + 1];
  return `<nav class="series-navigation" aria-label="Episodios de la serie"><p>Episodio ${item.episode} de ${item.of}</p><div class="episode-list">${episodes.map(video => `<button data-open="${video.id}" ${video.id === item.id ? 'aria-current="step" disabled' : ''} aria-label="Episodio ${video.episode}: ${escape(video.title)}">${video.episode}/${video.of}</button>`).join('')}</div><div class="episode-arrows">${previous ? `<button data-open="${previous.id}">← Episodio anterior</button>` : ''}${next ? `<button data-open="${next.id}">Siguiente episodio →</button>` : '<span>Último episodio disponible</span>'}</div></nav>${next ? `<div id="next-episode" class="next-episode" hidden><p>¿Seguimos con la siguiente idea?</p><button class="button primary" data-open="${next.id}">Ver episodio ${next.episode}: ${escape(next.title)} ${icon('arrow')}</button></div>` : ''}`;
}

function videoDetails(item) {
  return `<video class="dialog-video ${item.orientation === 'vertical' ? 'vertical' : ''}" controls playsinline preload="metadata" poster="${escape(item.poster)}" aria-label="${escape(item.title)}"><source src="/media/${videoPath(item)}" type="video/mp4">Tu navegador no puede reproducir este video.</video><p class="video-error" hidden>No se pudo cargar el video. Puedes <a href="/media/${videoPath(item)}" target="_blank" rel="noopener">abrir el archivo directamente</a> o volver a intentarlo más tarde.</p><div class="dialog-body"><span class="eyebrow">${escape(item.label || groupLabels[item.group] || 'Video')} · ${duration(item.duration)}</span><h2 id="dialog-title">${escape(item.title)}</h2>${seriesNavigation(item)}<p>${escape(item.description)}</p><p class="dialog-note">${escape(item.author)}${item.note ? ` · ${escape(item.note)}` : ''}</p><button class="text-button" id="fullscreen-video">Ver a pantalla completa ${icon('play')}</button>${item.book ? `<button class="text-button" data-open="${item.book}">${icon('book')} Ver libro de referencia</button>` : ''}${dialogActions(item)}</div>`;
}

function stopDialogVideo() {
  const video = $('#resource-dialog video');
  if (!video) return;
  video.pause();
  video.removeAttribute('src');
  video.querySelector('source')?.removeAttribute('src');
  video.load();
}

function openResource(id) {
  const item = resources.find(resource => resource.id === id);
  if (!item) return;
  const dialog = $('#resource-dialog');
  if (!dialog.open) dialogOpener = document.activeElement;
  stopDialogVideo();
  activeResource = item;
  dialog.classList.toggle('vertical-dialog', item.type === 'video' && item.orientation === 'vertical');
  $('#dialog-content').innerHTML = item.type === 'book' ? bookDetails(item) : videoDetails(item);
  if (item.type === 'video') {
    const video = dialog.querySelector('video');
    const showError = () => { $('.video-error').hidden = false; };
    video.addEventListener('error', showError);
    video.querySelector('source').addEventListener('error', showError);
    video.addEventListener('ended', () => {
      const next = $('#next-episode');
      if (next) { next.hidden = false; next.scrollIntoView({block:'nearest'}); }
    });
    $('#fullscreen-video').onclick = async () => {
      try {
        if (video.requestFullscreen) await video.requestFullscreen();
        else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
        else notify('Usa el control de pantalla completa del reproductor.');
      } catch { notify('Usa el control de pantalla completa del reproductor.'); }
    };
  }
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
  $('#close-dialog').focus();
  const url = new URL(location.href);
  url.searchParams.set('recurso', id);
  history.replaceState(null, '', url);
  $('#dialog-save').onclick = () => toggleSaved(item.id);
  $('#share-resource').onclick = async () => {
    try { await navigator.clipboard.writeText(location.href); notify('Enlace copiado. Ya puedes compartirlo.'); }
    catch { window.prompt('Copia este enlace para compartir el recurso:', location.href); }
  };
}

function renderQuestions() {
  const visible = showAllQuestions ? catalog.questions : catalog.questions.slice(0, 5);
  $('#questions').innerHTML = visible.map((item, index) => `<details><summary><span>${String(index + 1).padStart(2, '0')} &nbsp; ${escape(item.title)}</span>${icon('plus')}</summary><p>${escape(item.question)}</p></details>`).join('');
  $('#more-questions').innerHTML = `${showAllQuestions ? 'Mostrar menos preguntas' : `Ver las ${catalog.questions.length} preguntas`} ${icon('arrow')}`;
  $('#more-questions').setAttribute('aria-expanded', String(showAllQuestions));
  $('#more-questions').hidden = catalog.questions.length <= 5;
}

function resetFilters() {
  currentFilter = 'all';
  currentGroup = 'all';
  $('#search').value = '';
  $('#topic').value = 'all';
  $('#access').value = 'all';
  $('#related-book').value = 'all';
  render();
}

async function loadCatalog() {
  $('#error-state').hidden = true;
  $('#results-count').textContent = 'Cargando la biblioteca…';
  $('#resource-grid').setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/catalog.json');
    if (!response.ok) throw new Error('No se pudo cargar el catálogo');
    catalog = await response.json();
    catalog.videos = catalog.videos.filter(video => video.status === 'published');
    resources = [...catalog.videos, ...catalog.books];
    document.title = `${catalog.site.title} · ${catalog.site.subtitle}`;
    document.querySelectorAll('.brand strong').forEach(node => { node.textContent = catalog.site.title; });
    $('.brand small').textContent = catalog.site.subtitle.toLocaleUpperCase('es');
    $('#hero-title').innerHTML = escape(catalog.site.headline).replace('. ', '.<br>');
    const featured = catalog.videos.find(video => video.id === catalog.site.featuredVideo) || catalog.videos[0];
    $('#featured-video').hidden = !featured;
    $('#hero-upcoming').hidden = Boolean(featured);
    if (featured) {
      $('#featured-title').textContent = featured.title;
      $('#featured-duration').textContent = duration(featured.duration);
      $('#featured-video img').src = featured.poster;
      $('#featured-video').classList.toggle('vertical', featured.orientation === 'vertical');
      $('#featured-video').disabled = false;
      $('#featured-video').onclick = () => openResource(featured.id);
    }
    $('#hero-description').textContent = catalog.site.description;
    $('#collection-count').textContent = `${catalog.videos.length} videos · ${catalog.books.length} referencias`;
    $('#all-total').textContent = resources.length;
    $('#book-total').textContent = catalog.books.length;
    $('#video-total').textContent = catalog.videos.length;
    $('#topic').innerHTML = '<option value="all">Todos los temas</option>' + [...new Set(resources.map(item => item.topic))].sort((a,b) => a.localeCompare(b, 'es')).map(topic => `<option value="${escape(topic)}">${escape(topic)}</option>`).join('');
    $('#related-book').innerHTML = '<option value="all">Cualquier libro</option>' + catalog.books.filter(book => relatedVideos(book).length).map(book => `<option value="${escape(book.id)}">${escape(book.title)}</option>`).join('');
    const params = new URLSearchParams(location.search);
    currentFilter = ['all', 'book', 'video', 'saved'].includes(params.get('type')) ? params.get('type') : 'all';
    currentGroup = currentFilter !== 'book' && ['libros', ...videoGroups.map(group => group.id)].includes(params.get('group')) ? params.get('group') : 'all';
    $('#search').value = params.get('q') || '';
    for (const field of ['topic', 'access']) {
      if ([...$(`#${field}`).options].some(option => option.value === params.get(field))) $(`#${field}`).value = params.get(field);
    }
    if ([...$('#related-book').options].some(option => option.value === params.get('book'))) $('#related-book').value = params.get('book');
    if (currentFilter === 'book' || currentGroup === 'junta') $('#related-book').value = 'all';
    if (currentGroup !== 'all' || currentFilter === 'video') $('#access').value = 'all';
    render();
    renderQuestions();
    if (params.has('recurso')) openResource(params.get('recurso'));
  } catch {
    $('#error-state').hidden = false;
    $('#results-count').textContent = 'Biblioteca no disponible';
    $('#resource-grid').setAttribute('aria-busy', 'false');
  }
}

document.querySelectorAll('[data-filter]').forEach(button => {
  button.onclick = () => {
    currentFilter = button.dataset.filter;
    currentGroup = 'all';
    if (currentFilter === 'book') $('#related-book').value = 'all';
    if (currentFilter === 'video') $('#access').value = 'all';
    render();
  };
});
$('#saved-nav').onclick = () => { resetFilters(); currentFilter = 'saved'; render(); $('#biblioteca').scrollIntoView(); };
$('#search').addEventListener('input', render);
$('#topic').addEventListener('change', render);
$('#access').addEventListener('change', render);
$('#related-book').addEventListener('change', render);
$('#toggle-refinements').onclick = () => {
  refinementsOpen = !refinementsOpen;
  renderRefinements();
};
mobileLayout?.addEventListener('change', renderRefinements);
$('#topic-filters').onclick = event => {
  const button = event.target.closest('[data-topic]');
  if (!button) return;
  $('#topic').value = button.dataset.topic;
  render();
  // El control se vuelve a dibujar; conserva el foco para navegar con teclado.
  [...$('#topic-filters').children].find(node => node.dataset.topic === button.dataset.topic)?.focus({preventScroll:true});
};
$('#clear-selection').onclick = () => {
  const filter = currentFilter;
  resetFilters();
  currentFilter = filter;
  render();
  $('#search').focus({preventScroll:true});
};
$('#reset-filters').onclick = resetFilters;
$('#retry').onclick = loadCatalog;
$('#more-questions').onclick = () => { if (catalog) { showAllQuestions = !showAllQuestions; renderQuestions(); } };
$('#resource-grid').onclick = event => {
  const save = event.target.closest('[data-save]');
  const open = event.target.closest('[data-open]');
  const more = event.target.closest('[data-show-group]');
  if (save) toggleSaved(save.dataset.save);
  else if (open) openResource(open.dataset.open);
  else if (more) {
    selectGroup(more.dataset.showGroup);
    const heading = $(`#${currentGroup} h3`);
    heading?.setAttribute('tabindex', '-1');
    heading?.focus({preventScroll:true});
    heading?.scrollIntoView({block:'start'});
  }
};
function selectGroup(group) {
  currentGroup = group;
  if (currentFilter !== 'saved') currentFilter = 'video';
  if (currentGroup === 'junta') $('#related-book').value = 'all';
  $('#access').value = 'all';
  render();
}
$('#video-groups').onclick = event => {
  const button = event.target.closest('[data-group]');
  if (!button) return;
  selectGroup(button.dataset.group);
  $(`#video-groups [data-group="${currentGroup}"]`)?.focus({preventScroll:true});
};
$('#dialog-content').onclick = event => {
  const button = event.target.closest('[data-open]');
  if (button) openResource(button.dataset.open);
};
$('#close-dialog').onclick = () => $('#resource-dialog').close();
$('#resource-dialog').addEventListener('click', event => { if (event.target === $('#resource-dialog')) { const rect = event.target.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.target.close(); } });
$('#resource-dialog').addEventListener('close', () => {
  const previousId = activeResource?.id;
  stopDialogVideo();
  $('#dialog-content').innerHTML = '';
  activeResource = null;
  const url = new URL(location.href);
  url.searchParams.delete('recurso');
  history.replaceState(null, '', url);
  const focusTarget = dialogOpener?.isConnected ? dialogOpener : document.querySelector(`[data-open="${previousId}"]`) || $('#saved-nav');
  focusTarget?.focus({ preventScroll:true });
});
document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !$('#resource-dialog').open && !event.target.matches('input, textarea, select, [contenteditable]')) { event.preventDefault(); $('#search').focus(); }
});
loadCatalog();

document.addEventListener('click', event => {
  const jump = event.target.closest('[data-jump]');
  if (!jump || !catalog) return;
  event.preventDefault();
  resetFilters();
  currentFilter = jump.dataset.jump;
  render();
  const target = currentFilter === 'book' ? $('#referencias') : $('#biblioteca');
  target?.scrollIntoView({behavior:'smooth'});
});
