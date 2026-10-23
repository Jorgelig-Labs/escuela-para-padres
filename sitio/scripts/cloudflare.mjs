import { readFile } from 'node:fs/promises';
import { parseEnv } from 'node:util';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { listRemoteObjects, planUploads, uploadPlanned } from './uploads.mjs';
import { build, root } from './build.mjs';
import { resolveCredentials, createCloudflareAPI, checkCapabilities, wranglerEnvironment } from './cloudflare-auth.mjs';

const action = process.argv[2] || 'check';
if (!['login', 'check', 'upload', 'backup', 'deploy'].includes(action)) throw new Error('Usa login, check, upload, backup o deploy');
const oauth = action === 'login' || process.argv.includes('--oauth');
const sources = [];
// Se leen únicamente las claves de Cloudflare; nunca se copian al sitio o a logs.
for (const filename of [path.join(root, '../.env'), path.join(root, '.env')]) {
  try {
    const values = parseEnv(await readFile(filename, 'utf8'));
    sources.push({ name:path.relative(root, filename), values });
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
}
sources.push({ name:'variables de la terminal', values:process.env });
let { token, account, tokenSource, accountSource } = resolveCredentials(sources);
const config = JSON.parse(await readFile(path.join(root, 'wrangler.jsonc'), 'utf8'));
const bucket = config.r2_buckets[0].bucket_name;

async function wrangler(args, { capture = false } = {}) {
  return new Promise((resolve, reject) => {
    let output = '';
    const child = spawn(process.execPath, [path.join(root, 'node_modules/wrangler/bin/wrangler.js'), ...args], {
      cwd:root, stdio:capture ? ['ignore', 'pipe', 'inherit'] : 'inherit',
      env:wranglerEnvironment(process.env, { oauth, token, account }),
    });
    if (capture) child.stdout.on('data', chunk => { output += chunk; });
    child.once('error', reject);
    child.once('exit', code => code === 0 ? resolve(output) : reject(new Error(`Wrangler terminó con código ${code}`)));
  });
}

async function main() {
  if (action === 'login') {
    console.log('Inicio de sesión de Wrangler con permisos OAuth seleccionados. OAuth no se limita a un proyecto.');
    const scopes = ['account:read', 'user:read', 'workers:write', 'workers_scripts:write'];
    if (config.routes?.length) scopes.push('zone:read', 'workers_routes:write');
    await wrangler(['login', '--scopes', ...scopes]);
    return;
  }
  if (oauth) {
    // Capturar el token exclusivamente en memoria: nunca imprimir stdout de auth token.
    let credentials;
    try { credentials = JSON.parse(await wrangler(['auth', 'token', '--json'], { capture:true })); }
    catch { throw new Error('No se pudo obtener la sesión de Wrangler. Ejecuta npm run cf:login y vuelve a intentarlo.'); }
    if (credentials.type !== 'oauth' || !credentials.token) throw new Error('Wrangler no está usando OAuth. Revisa los tokens de API en los archivos .env y ejecuta npm run cf:login.');
    token = credentials.token;
    tokenSource = 'sesión OAuth de Wrangler (sin utilizar el token de ../.env)';
  }
  if (!token || !account) throw new Error('Faltan CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID. También se aceptan CLOUDFLARE_API y CLOUDFLARE_R2_ACCOUNT_ID en ../.env.');
  const api = createCloudflareAPI(token);
  if (!/^[a-f0-9]{32}$/i.test(account)) throw new Error('CLOUDFLARE_ACCOUNT_ID debe ser el Account ID de 32 caracteres hexadecimales, no el Zone ID, nombre o URL.');
  console.log(`Token: ${tokenSource}. Cuenta: ${accountSource}.`);
  console.log('Comprobando acceso a R2' + (['upload', 'backup'].includes(action) ? '…' : ' y Workers…'));
  const { bucketExists } = await checkCapabilities(api, account, action === 'backup' ? 'upload' : action, bucket);
  console.log(`Lectura de los servicios confirmada. Bucket del proyecto: ${bucketExists ? 'existente' : 'por crear'}. Los permisos de escritura se comprobarán al publicar.`);
  if (action !== 'check') {
    const catalog = await build();
    const documents = catalog.books.flatMap(book => book.documents).map(document => ({ ...document, key:`pdf/${document.id}.pdf`, contentType:'application/pdf' }));
    const videos = catalog.videos.map(video => ({ ...video, key:video.file, contentType:'video/mp4' }));
    const files = [...documents, ...(action === 'backup' ? [] : videos)];
    const remote = bucketExists ? await listRemoteObjects(api, account, bucket) : new Map();
    const plan = await planUploads(root, files, remote, { force:process.argv.includes('--force') });
    const changed = plan.filter(item => item.upload);
    const bytes = changed.reduce((sum, item) => sum + item.size, 0);
    console.log(`Plan: ${changed.length} nuevos o cambiados (${(bytes / 1024 / 1024).toFixed(1)} MiB), ${plan.length - changed.length} sin cambios.`);
    if (process.argv.includes('--dry-run')) {
      for (const item of plan) console.log(`${item.upload ? 'SUBIR' : 'OMITIR'} ${item.key}`);
      console.log('Simulación: sin crear bucket, subir archivos ni publicar Worker.');
      return;
    }
    if (!bucketExists) { await api(`/accounts/${account}/r2/buckets`, { method:'POST', body:JSON.stringify({ name:bucket }) }, 'Crear bucket R2 del proyecto'); console.log('Bucket del proyecto creado.'); }
    await uploadPlanned(root, plan, async item => {
      console.log(`Subiendo ${item.key}…`);
      await wrangler(['r2','object','put',`${bucket}/${item.key}`,'--file',item.file,'--content-type',item.contentType,'--remote']);
    }, (status, item) => { if (status === 'skip') console.log(`Sin cambios: ${item.key}`); });
    // Un alta concurrente no debe publicar un catálogo cuyos videos todavía no se subieron.
    if (JSON.stringify(JSON.parse(await readFile(path.join(root, 'dist/catalog.json'), 'utf8'))) !== JSON.stringify(catalog)) throw new Error('El catálogo cambió durante las subidas. Vuelve a ejecutar el despliegue; los objetos ya subidos se omitirán.');
    if (action === 'deploy') await wrangler(['deploy']);
    else console.log('Archivos respaldados. Publica el front con npm run deploy o npm run deploy:oauth según tu autenticación.');
  }
}

try { await main(); } catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
