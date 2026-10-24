import { cp, mkdir, open, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export const root = fileURLToPath(new URL('../', import.meta.url));
export const dist = path.join(root, 'dist');

export function parseBook(source, filename) {
  const match = source.match(/^---\r?\n([\s\S]+?)\r?\n---\r?\n/);
  if (!match) throw new Error(`${filename}: falta el bloque de metadatos entre ---`);
  try { return JSON.parse(match[1]); }
  catch { throw new Error(`${filename}: los metadatos deben ser JSON válido`); }
}

export function publishedVideos(videos) {
  return videos.filter(video => video.status === 'published');
}

export function validateCatalog(catalog) {
  const ids = new Set();
  const documentIds = new Set();
  for (const item of [...catalog.books, ...catalog.videos]) {
    for (const field of ['id', 'title', 'author', 'topic', 'description']) {
      if (typeof item[field] !== 'string' || !item[field].trim()) throw new Error(`${item.id || 'Recurso'}: falta ${field}`);
    }
    if (!/^[a-z0-9-]+$/.test(item.id) || ids.has(item.id)) throw new Error(`ID inválido o duplicado: ${item.id}`);
    ids.add(item.id);
    if (item.type === 'book') {
      if (!['complete', 'sample', 'purchase'].includes(item.access)) throw new Error(`${item.id}: acceso inválido`);
      if (!['sage', 'ochre', 'terracotta', 'navy', 'rose', 'lavender'].includes(item.palette)) throw new Error(`${item.id}: paleta inválida`);
      if (!Array.isArray(item.links) || !item.links.length) throw new Error(`${item.id}: faltan enlaces`);
      for (const link of item.links) {
        if (!link.label || !['read', 'download', 'purchase'].includes(link.kind) || new URL(link.url).protocol !== 'https:') throw new Error(`${item.id}: enlace inválido`);
      }
      if (item.access !== 'purchase' && !item.links.some(link => link.kind === 'read')) throw new Error(`${item.id}: falta enlace de lectura`);
      if (item.documents !== undefined && !Array.isArray(item.documents)) throw new Error(`${item.id}: documentos inválidos`);
      for (const document of item.documents || []) {
        if (!/^[a-z0-9-]+$/.test(document.id) || documentIds.has(document.id)) throw new Error(`${item.id}: ID de PDF inválido o duplicado`);
        documentIds.add(document.id);
        if (!document.label || !/^libros\/[^/\\]+\.pdf$/.test(document.file) || document.file.includes('..')) throw new Error(`${item.id}: archivo PDF inválido`);
        const source = new URL(document.source);
        if (source.protocol !== 'https:' || !['media2.egwwritings.org', 'media4.egwwritings.org'].includes(source.hostname) || !source.pathname.endsWith('.pdf') || source.username || source.password || source.port) throw new Error(`${item.id}: fuente PDF no permitida`);
      }
    } else if (item.type === 'video') {
      if (!/^(?:[a-zA-Z0-9_-]+\/){0,3}[a-zA-Z0-9_-]+\.mp4$/.test(item.file)) throw new Error(`${item.id}: archivo de video inválido`);
      if (item.status !== undefined && !['draft', 'published'].includes(item.status)) throw new Error(`${item.id}: estado inválido`);
      if (item.group !== undefined && !['junta', 'refuerzo', 'resumen', 'serie'].includes(item.group)) throw new Error(`${item.id}: grupo inválido`);
      if (item.orientation !== undefined && !['horizontal', 'vertical'].includes(item.orientation)) throw new Error(`${item.id}: orientación inválida`);
      if (item.book !== undefined && !catalog.books.some(book => book.id === item.book)) throw new Error(`${item.id}: referencia de libro inválida`);
      for (const field of ['note', 'series']) if (item[field] !== undefined && (typeof item[field] !== 'string' || !item[field].trim())) throw new Error(`${item.id}: ${field} inválido`);
      if (item.episode !== undefined || item.of !== undefined) {
        if (!item.series || !Number.isInteger(item.episode) || !Number.isInteger(item.of) || item.episode < 1 || item.of < item.episode) throw new Error(`${item.id}: episodio inválido`);
      }
      if (!Number.isFinite(item.duration) || item.duration <= 0) throw new Error(`${item.id}: duración inválida`);
      if (!/^\/assets\/[a-zA-Z0-9_.-]+$/.test(item.poster)) throw new Error(`${item.id}: poster inválido`);
    } else throw new Error(`${item.id}: tipo inválido`);
  }
  if (catalog.site.featuredVideo && !catalog.videos.some(item => item.id === catalog.site.featuredVideo)) throw new Error('El video destacado no existe');
  if (!Array.isArray(catalog.questions) || catalog.questions.some(q => !q.title || !q.question)) throw new Error('Preguntas inválidas');
}

export async function build() {
  const readJSON = async name => JSON.parse(await readFile(path.join(root, 'content', name), 'utf8'));
  const [site, videos, questions, files] = await Promise.all([
    readJSON('site.json'), readJSON('videos.json'), readJSON('questions.json'), readdir(path.join(root, 'content/libros')),
  ]);
  const books = await Promise.all(files.filter(name => name.endsWith('.md')).sort().map(async name => {
    const book = parseBook(await readFile(path.join(root, 'content/libros', name), 'utf8'), name);
    return book;
  }));
  const catalog = { version: 1, site, books: books.sort((a, b) => a.order - b.order), videos: videos.sort((a, b) => a.order - b.order), questions };
  validateCatalog(catalog);
  catalog.videos = publishedVideos(catalog.videos);
  catalog.site = { ...site, featuredVideo: catalog.videos.find(video => video.id === site.featuredVideo)?.id || catalog.videos[0]?.id || null };
  const documents = books.flatMap(book => (book.documents || []).map(document => ({ ...document, bookId:book.id, key:`pdf/${document.id}.pdf` })));
  for (const document of documents) {
    let file;
    try { file = await open(path.join(root, document.file), 'r'); }
    catch (error) { if (error.code === 'ENOENT') continue; throw error; }
    try {
      const signature = Buffer.alloc(5);
      await file.read(signature, 0, 5, 0);
      if (signature.toString() !== '%PDF-') throw new Error(`${document.file}: el archivo no es un PDF`);
    } finally { await file.close(); }
  }
  await mkdir(path.join(root, '.generated'), { recursive:true });
  await writeFile(path.join(root, '.generated/videos.json'), JSON.stringify(catalog.videos, null, 2) + '\n');
  await writeFile(path.join(root, '.generated/documents.json'), JSON.stringify(documents, null, 2) + '\n');
  for (const book of books) {
    book.documents = (book.documents || []).map(document => ({ ...document, url:`/pdf/${document.id}.pdf` }));
  }
  for (const video of catalog.videos) await readFile(path.join(root, 'public', video.poster));
  await rm(dist, { recursive: true, force: true });
  await mkdir(dist, { recursive: true });
  await cp(path.join(root, 'public'), dist, { recursive: true });
  const pdfjs = path.join(root, 'node_modules/pdfjs-dist');
  const vendor = path.join(dist, 'vendor/pdfjs');
  await mkdir(vendor, { recursive:true });
  for (const file of ['pdf.min.mjs', 'pdf.worker.min.mjs']) await cp(path.join(pdfjs, 'legacy/build', file), path.join(vendor, file));
  for (const directory of ['cmaps', 'standard_fonts']) await cp(path.join(pdfjs, directory), path.join(vendor, directory), { recursive:true });
  await cp(path.join(pdfjs, 'LICENSE'), path.join(vendor, 'LICENSE'));
  await writeFile(path.join(dist, 'catalog.json'), JSON.stringify(catalog, null, 2) + '\n');
  return catalog;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const catalog = await build();
  console.log(`Catálogo listo: ${catalog.books.length} libros, ${catalog.videos.length} videos y ${catalog.questions.length} preguntas → dist/`);
}
