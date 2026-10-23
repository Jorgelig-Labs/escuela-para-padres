import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { parseBook, validateCatalog, publishedVideos, root } from '../scripts/build.mjs';

async function loadCatalog() {
  const directory = path.join(root, 'content/libros');
  const files = (await readdir(directory)).filter(file => file.endsWith('.md'));
  const books = await Promise.all(files.map(async file => parseBook(await readFile(path.join(directory, file), 'utf8'), file)));
  const json = async name => JSON.parse(await readFile(path.join(root, 'content', name + '.json'), 'utf8'));
  return { books, videos:await json('videos'), questions:await json('questions'), site:await json('site') };
}

test('las fichas y las entradas de video forman un catálogo válido', async () => {
  const catalog = await loadCatalog();
  validateCatalog(catalog);
  assert.equal(catalog.books.length, 12);
  const built = JSON.parse(await readFile(path.join(root, 'dist/catalog.json'), 'utf8'));
  assert.deepEqual(built.videos.map(v => v.id).sort(), publishedVideos(catalog.videos).map(v => v.id).sort());
  assert.equal(catalog.questions.length, 15);
  assert.equal(catalog.books.filter(book => book.access === 'complete').length, 4);
});
test('no permite IDs duplicados, rutas de video arbitrarias ni enlaces ejecutables', async () => {
  const catalog = await loadCatalog();
  const duplicate = structuredClone(catalog);
  duplicate.books[1].id = duplicate.books[0].id;
  assert.throws(() => validateCatalog(duplicate), /duplicado/);
  const traversal = structuredClone(catalog);
  traversal.videos[0].file = '../.env';
  assert.throws(() => validateCatalog(traversal), /archivo de video/);
  const unsafe = structuredClone(catalog);
  unsafe.books[0].links[0].url = 'javascript:alert(1)';
  assert.throws(() => validateCatalog(unsafe), /enlace inválido/);
});
test('detecta metadatos incompletos y JSON inválido con el nombre del archivo', () => {
  assert.throws(() => parseBook('# Libro', 'libro.md'), /libro.md/);
  assert.throws(() => parseBook('---\n{no es JSON}\n---\n', 'libro.md'), /JSON válido/);
});

test('rutas anidadas seguras, publicación explícita y referencias de libros', async () => {
  const catalog = await loadCatalog();
  const video = catalog.videos[0];
  video.file = 'videos-libros/03-refuerzo/R01-por-que-dejan-de-contar.mp4';
  video.book = catalog.books[0].id;
  video.status = 'published';
  validateCatalog(catalog);
  for (const file of ['videos-libros/../.env', '/abs.mp4', 'a/b/c/d/e.mp4', 'a%2Fb.mp4', 'a\\b.mp4']) {
    video.file = file;
    assert.throws(() => validateCatalog(catalog), /archivo de video/);
  }
  assert.deepEqual(publishedVideos([{id:'test'}, {id:'draft',status:'draft'}, {id:'final',status:'published'}]).map(v => v.id), ['final']);
});

test('el catálogo público no publica evento ni fichas Markdown internas', async () => {
  const built = JSON.parse(await readFile(path.join(root, 'dist/catalog.json'), 'utf8'));
  assert.equal(built.site.event, undefined);
  assert.ok(built.books.every(book => book.markdown === undefined));
  assert.equal((await readdir(path.join(root, 'dist'))).includes('fichas'), false);
});
