// Una sola página en memoria y un worker propio, sin el visor PDF del navegador.
export function createPDFReader(container, loadLibrary = () => import('/vendor/pdfjs/pdf.min.mjs')) {
  const document = container.ownerDocument;
  const window = document.defaultView;
  let library;
  let loading;
  let pdf;
  let task;
  let generation = 0;
  let rendering = 0;

  async function open(url) {
    const current = ++generation;
    ++rendering;
    task?.cancel();
    const previous = loading;
    loading = null;
    pdf = null;
    container.replaceChildren();
    await previous?.destroy();
    library ||= loadLibrary().catch(error => { library = null; throw error; });
    const engine = await library;
    if (current !== generation) return null;
    engine.GlobalWorkerOptions.workerSrc = '/vendor/pdfjs/pdf.worker.min.mjs';
    loading = engine.getDocument({
      url, cMapUrl:'/vendor/pdfjs/cmaps/', cMapPacked:true,
      standardFontDataUrl:'/vendor/pdfjs/standard_fonts/',
      useWasm:false, disableStream:true, disableAutoFetch:true,
    });
    const loadedPDF = await loading.promise;
    if (current !== generation) return null;
    pdf = loadedPDF;
    return pdf.numPages;
  }

  async function render(pageNumber, {zoom=1, text=false} = {}) {
    if (!pdf) return false;
    const current = ++rendering;
    const documentGeneration = generation;
    task?.cancel();
    task = null;
    let page;
    try {
      page = await pdf.getPage(pageNumber);
      if (current !== rendering || documentGeneration !== generation) return false;
      let element;
      if (text) {
        const content = await page.getTextContent();
        element = document.createElement('div');
        element.className = 'pdf-text';
        element.textContent = content.items.map(item => (item.str || '') + (item.hasEOL ? '\n' : ' ')).join('').trim() || 'Esta página contiene una imagen. Cambia a «Página original» para verla.';
      } else {
        const original = page.getViewport({scale:1});
        const width = Math.max(240, Math.min(container.clientWidth || 320, 1000) - 16);
        const viewport = page.getViewport({scale:width / original.width * zoom});
        // Limita el bitmap para que el zoom no agote la memoria del teléfono.
        const density = Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(4000000 / (viewport.width * viewport.height)));
        element = document.createElement('canvas');
        element.width = Math.floor(viewport.width * density);
        element.height = Math.floor(viewport.height * density);
        element.style.width = `${Math.floor(viewport.width)}px`;
        element.style.height = `${Math.floor(viewport.height)}px`;
        element.setAttribute('role', 'img');
        element.setAttribute('aria-label', `Página ${pageNumber}. Usa Texto cómodo para leer su contenido como texto.`);
        task = page.render({canvasContext:element.getContext('2d'), viewport, transform:[density,0,0,density,0,0]});
        await task.promise;
      }
      if (current !== rendering || documentGeneration !== generation) return false;
      container.replaceChildren(element);
      return true;
    } catch (error) {
      if (current !== rendering || documentGeneration !== generation || error.name === 'RenderingCancelledException') return false;
      throw error;
    } finally { page?.cleanup(); }
  }

  function destroy() {
    ++generation;
    ++rendering;
    task?.cancel();
    pdf = null;
    const previous = loading;
    loading = null;
    return previous?.destroy();
  }
  return {open, render, destroy};
}
