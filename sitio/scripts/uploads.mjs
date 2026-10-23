import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import path from 'node:path';

// Wrangler: 300 MiB (315 MB redondeados en la documentación).
export const MAX_UPLOAD_BYTES = 300 * 1024 * 1024;

export async function preflightUploads(root, files, inspect = stat) {
  for (const { file } of files) {
    const info = await inspect(path.join(root, file));
    if (!info.isFile() || info.size === 0) throw new Error(`${file}: falta un archivo válido para subir`);
    if (info.size > MAX_UPLOAD_BYTES) throw new Error(`${file}: supera el límite de Wrangler de 300 MiB. Reduce su tamaño o usa una subida multipart con S3. No se subió ningún archivo.`);
  }
}

// Listar el estado remoto evita depender de manifiestos locales que puedan quedar obsoletos.
export async function listRemoteObjects(api, account, bucket) {
  const objects = new Map();
  const seen = new Set();
  let cursor;
  do {
    const params = new URLSearchParams({ per_page:'1000' });
    if (cursor) params.set('cursor', cursor);
    const page = await api.page(`/accounts/${account}/r2/buckets/${encodeURIComponent(bucket)}/objects?${params}`, {}, 'Listar objetos R2');
    if (!Array.isArray(page.result)) throw new Error('R2 devolvió una lista de objetos inválida. No se subió ningún archivo.');
    for (const object of page.result) {
      if (typeof object.key !== 'string' || !Number.isSafeInteger(object.size) || object.size < 0) throw new Error('R2 devolvió metadatos de objeto inválidos.');
      objects.set(object.key, object);
    }
    if (!page.result_info && page.result.length >= 1000) throw new Error('Falta la paginación de R2; no se puede calcular una subida segura.');
    if (!page.result_info?.is_truncated) break;
    cursor = page.result_info.cursor;
    if (!cursor || seen.has(cursor)) throw new Error('Paginación de R2 incompleta o repetida. No se subió ningún archivo.');
    seen.add(cursor);
  } while (cursor);
  return objects;
}

export async function fingerprint(filename) {
  const before = await stat(filename);
  const hash = createHash('md5'); // Compara con ETag de los PUT simples de R2; no se usa para seguridad.
  for await (const chunk of createReadStream(filename)) hash.update(chunk);
  const after = await stat(filename);
  if (before.size !== after.size || before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs) throw new Error(`${filename}: el archivo cambió mientras se comprobaba. Espera a que termine su producción.`);
  return { size:after.size, mtimeMs:after.mtimeMs, ctimeMs:after.ctimeMs, md5:hash.digest('hex') };
}

export async function planUploads(root, files, remote, { force = false } = {}) {
  await preflightUploads(root, files);
  const plan = [];
  // Lectura secuencial y por bloques, sin cargar videos enteros en RAM.
  for (const item of files) {
    const local = await fingerprint(path.join(root, item.file));
    const object = remote.get(item.key);
    const etag = object?.etag?.replace(/^"|"$/g, '').toLowerCase();
    const same = object?.size === local.size && etag === local.md5 && (!object.http_metadata?.contentType || object.http_metadata.contentType === item.contentType);
    plan.push({ ...item, ...local, upload:force || !same });
  }
  return plan;
}

export async function uploadPlanned(root, plan, upload, report = () => {}) {
  for (const item of plan) {
    const current = await stat(path.join(root, item.file));
    if (current.size !== item.size || current.mtimeMs !== item.mtimeMs || current.ctimeMs !== item.ctimeMs) throw new Error(`${item.file}: cambió después del plan. Vuelve a ejecutar el comando.`);
    if (!item.upload) { report('skip', item); continue; }
    await upload(item);
    const after = await stat(path.join(root, item.file));
    if (after.size !== item.size || after.mtimeMs !== item.mtimeMs || after.ctimeMs !== item.ctimeMs) throw new Error(`${item.file}: cambió durante la subida; no se publicará el sitio.`);
    report('uploaded', item);
  }
}
