import test from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import { createPDFReader } from '../public/pdf-reader.js';

function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return {promise,resolve}; }
const tick = () => new Promise(resolve => setImmediate(resolve));
function setup(t, getDocument) {
  const dom = new JSDOM('<div id="pages"></div>');
  t.after(() => dom.window.close());
  const container = dom.window.document.querySelector('#pages');
  const engine = {GlobalWorkerOptions:{},getDocument};
  return {container,engine,reader:createPDFReader(container, async () => engine)};
}
function textPage(text) { return {getTextContent:async () => ({items:[{str:text}]}),cleanup() {}}; }

test('cambiar de página mientras se extrae texto descarta el resultado atrasado', async t => {
  const slow = deferred();
  const pdf = {numPages:3,getPage:async n => n === 1 ? {...textPage(''),getTextContent:() => slow.promise} : textPage('Página 2')};
  const {reader,container} = setup(t, () => ({promise:Promise.resolve(pdf),destroy:async () => {}}));
  await reader.open('/uno.pdf');
  const first = reader.render(1, {text:true}); await tick();
  await reader.render(2, {text:true});
  slow.resolve({items:[{str:'Página 1'}]});
  assert.equal(await first, false);
  assert.equal(container.textContent, 'Página 2');
});

test('cambiar de tomo antes de terminar la descarga conserva el documento más reciente', async t => {
  const slow = deferred();
  const second = {numPages:8,getPage:async () => textPage('Tomo 2')};
  const {reader,container} = setup(t, ({url}) => ({promise:url === '/uno.pdf' ? slow.promise : Promise.resolve(second),destroy:async () => {}}));
  const first = reader.open('/uno.pdf'); await tick();
  assert.equal(await reader.open('/dos.pdf'), 8);
  slow.resolve({numPages:2});
  assert.equal(await first, null);
  await reader.render(1, {text:true});
  assert.equal(container.textContent, 'Tomo 2');
});

test('un fallo al descargar el motor permite reintentar y el texto del PDF no ejecuta HTML', async t => {
  const {container,engine} = setup(t, () => ({promise:Promise.resolve({numPages:1,getPage:async () => textPage('<img src=x onerror=alert(1)>')}),destroy:async () => {}}));
  let attempts = 0;
  const reader = createPDFReader(container, async () => { if (++attempts === 1) throw new Error('Red caída'); return engine; });
  await assert.rejects(reader.open('/uno.pdf'), /Red caída/);
  assert.equal(await reader.open('/uno.pdf'), 1);
  await reader.render(1, {text:true});
  assert.equal(container.querySelector('img'), null);
  assert.match(container.textContent, /<img/);
});
