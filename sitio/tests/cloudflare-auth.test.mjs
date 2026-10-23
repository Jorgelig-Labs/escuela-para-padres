import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveCredentials, createCloudflareAPI, checkCapabilities, wranglerEnvironment } from '../scripts/cloudflare-auth.mjs';

test('el modo OAuth elimina credenciales heredadas sin modificar el entorno original', () => {
  const original = { PATH:'/bin', CLOUDFLARE_API_TOKEN:'viejo', CF_API_TOKEN:'alias', CLOUDFLARE_API_KEY:'global', CF_API_KEY:'global-alias', CLOUDFLARE_EMAIL:'email', CF_EMAIL:'alias-email' };
  const env = wranglerEnvironment(original, { oauth:true, token:'ignorar', account:'cuenta' });
  assert.equal(env.PATH, '/bin');
  assert.equal(env.CLOUDFLARE_ACCOUNT_ID, 'cuenta');
  for (const key of Object.keys(original).filter(key => key !== 'PATH')) assert.equal(env[key], undefined);
  assert.equal(original.CLOUDFLARE_API_TOKEN, 'viejo');
  assert.equal(wranglerEnvironment(original, { token:'nuevo' }).CLOUDFLARE_API_TOKEN, 'nuevo');
});

test('las credenciales locales y de la terminal prevalecen aunque usen aliases diferentes', () => {
  const sources = [
    { name:'../.env', values:{ CLOUDFLARE_API_TOKEN:'heredado', CLOUDFLARE_R2_ACCOUNT_ID:'cuenta-heredada' } },
    { name:'.env', values:{ CLOUDFLARE_API:' local ', CLOUDFLARE_ACCOUNT_ID:'cuenta-local' } },
  ];
  assert.equal(resolveCredentials(sources).token, 'local');
  assert.equal(resolveCredentials(sources).account, 'cuenta-local');
  const fromShell = resolveCredentials([...sources, { name:'terminal', values:{ CLOUDFLARE_API:'terminal' } }]);
  assert.equal(fromShell.token, 'terminal');
  assert.equal(fromShell.account, 'cuenta-local');
  assert.equal(resolveCredentials([{ name:'.env', values:{ CLOUDFLARE_API_TOKEN:'', CLOUDFLARE_API:'alias' } }]).token, 'alias');
});
test('el preflight comprueba servicios, no exige lectura general de la cuenta', async () => {
  const paths = [];
  const api = async route => { paths.push(route); return route.includes('/r2/') ? { buckets:[{ name:'biblioteca' }] } : []; };
  assert.deepEqual(await checkCapabilities(api, 'account', 'deploy', 'biblioteca'), { bucketExists:true });
  assert.deepEqual(paths, ['/accounts/account/r2/buckets?per_page=1000', '/accounts/account/workers/scripts']);
  paths.length = 0;
  await checkCapabilities(api, 'account', 'upload', 'biblioteca');
  assert.equal(paths.length, 1);
});
test('un 403 identifica ambos servicios y los permisos sin revelar el token', async () => {
  const token = 'secreto-de-prueba';
  const api = createCloudflareAPI(token, async () => new Response(JSON.stringify({ success:false, errors:[{ code:9109, message:`Unauthorized ${token}` }] }), { status:403 }));
  await assert.rejects(checkCapabilities(api, 'account', 'check', 'biblioteca'), error => {
    assert.match(error.message, /Listar buckets R2: Cloudflare HTTP 403/);
    assert.match(error.message, /Listar Workers: Cloudflare HTTP 403/);
    assert.match(error.message, /Workers R2 Storage: Edit/);
    assert.match(error.message, /Workers Scripts: Edit/);
    assert.ok(!error.message.includes(token));
    return true;
  });
});
test('distingue problemas de red y respuestas no JSON de permisos insuficientes', async () => {
  const offline = createCloudflareAPI('token', async () => { throw Object.assign(new Error(), { cause:{ code:'ENOTFOUND' } }); });
  await assert.rejects(offline('/test', {}, 'R2'), /R2:.*ENOTFOUND/);
  const html = createCloudflareAPI('token', async () => new Response('Unavailable', { status:503 }));
  await assert.rejects(html('/test', {}, 'Workers'), /Workers: Cloudflare HTTP 503/);
});
