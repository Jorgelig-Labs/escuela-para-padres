import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { build, root } from './build.mjs';

// Vista de revisión local cuando no se puede abrir un servidor HTTP.
// No se incluye en dist/ ni se publica; reemplaza únicamente el transporte.
const catalog = await build();
const [html, css, source] = await Promise.all(['index.html','styles.css','app.js'].map(file => readFile(path.join(root, 'public', file), 'utf8')));
const images = new Map();
for (const video of catalog.videos) {
  const original = video.poster;
  const data = await readFile(path.join(root, 'public', original));
  video.poster = `data:image/jpeg;base64,${data.toString('base64')}`;
  images.set(original, video.poster);
}
for (const book of catalog.books) {
  for (const document of book.documents) document.url = '../' + document.file.split('/').map(encodeURIComponent).join('/');
}
const code = source.replace("await fetch('/catalog.json')", 'new Response(JSON.stringify(window.__previewCatalog))').replaceAll('/media/', '../').replaceAll('/leer.html?', 'lectura.html?');
let preview = html.replace('<link rel="stylesheet" href="/styles.css">', () => `<style>${css}</style>`)
  .replace('<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">', '<link rel="icon" href="../public/assets/favicon.svg" type="image/svg+xml">')
  .replace('<script type="module" src="/app.js"></script>', () => `<script>window.__previewCatalog=${JSON.stringify(catalog).replaceAll('<', '\\u003c')};</script><script type="module">${code}</script>`);
for (const [url, data] of images) preview = preview.replaceAll(url, data);
await mkdir(path.join(root, 'artifacts'), { recursive:true });
await writeFile(path.join(root, 'artifacts/preview.html'), preview);
console.log('Vista previa local: artifacts/preview.html (datos integrados, videos originales locales).');

const [readerHTML, readerCSS, readerSource] = await Promise.all(['leer.html','reader.css','reader.js'].map(file => readFile(path.join(root, 'public', file), 'utf8')));
const readerCode = readerSource.replace("await fetch('/catalog.json')", 'new Response(JSON.stringify(window.__previewCatalog))').replace("'/?type=book#referencias'", "'preview.html?type=book#referencias'");
const reader = readerHTML.replace('<link rel="stylesheet" href="/styles.css">', () => `<style>${css}</style>`)
  .replace('<link rel="stylesheet" href="/reader.css">', () => `<style>${readerCSS}</style>`)
  .replace('href="/assets/favicon.svg"', 'href="../public/assets/favicon.svg"')
  .replace('href="/#biblioteca"', 'href="preview.html#biblioteca"')
  .replace('<script type="module" src="/reader.js"></script>', () => `<script>window.__previewCatalog=${JSON.stringify(catalog).replaceAll('<', '\\u003c')};</script><script type="module">${readerCode}</script>`);
await writeFile(path.join(root, 'artifacts/lectura.html'), reader);
