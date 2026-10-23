// Cada fuente reemplaza a la anterior, incluso cuando usa un alias distinto.
export function resolveCredentials(sources) {
  const result = {};
  for (const { name, values } of sources) {
    const tokenKey = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_API'].find(key => values[key]?.trim());
    const accountKey = ['CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_R2_ACCOUNT_ID'].find(key => values[key]?.trim());
    if (tokenKey) {
      result.token = values[tokenKey].trim();
      result.tokenSource = `${name} (${tokenKey})`;
    }
    if (accountKey) {
      result.account = values[accountKey].trim();
      result.accountSource = `${name} (${accountKey})`;
    }
  }
  return result;
}

export function wranglerEnvironment(environment, { oauth = false, token, account } = {}) {
  const result = { ...environment, WRANGLER_SEND_METRICS:'false' };
  // Evitar que el token anterior o la Global API Key oculten la sesión OAuth.
  for (const key of ['CLOUDFLARE_API_TOKEN','CF_API_TOKEN','CLOUDFLARE_API_KEY','CF_API_KEY','CLOUDFLARE_EMAIL','CF_EMAIL']) delete result[key];
  if (!oauth && token) result.CLOUDFLARE_API_TOKEN = token;
  if (account) result.CLOUDFLARE_ACCOUNT_ID = account;
  return result;
}

export function createCloudflareAPI(token, fetcher = fetch) {
  async function request(route, options = {}, operation = 'consultar Cloudflare') {
    let response;
    try {
      response = await fetcher(`https://api.cloudflare.com/client/v4${route}`, {
        ...options, signal:AbortSignal.timeout(30000),
        headers:{ Authorization:`Bearer ${token}`, 'Content-Type':'application/json' },
      });
    } catch (error) {
      throw new Error(`${operation}: no se pudo conectar con Cloudflare (${error.cause?.code || error.name}). Comprueba el acceso a internet de esta terminal.`);
    }
    let body;
    try { body = await response.json(); }
    catch { throw new Error(`${operation}: Cloudflare HTTP ${response.status}, respuesta no válida.`); }
    if (!response.ok || !body.success) {
      const detail = body.errors?.map(error => `${error.code}: ${error.message}`).join('; ') || 'Solicitud rechazada';
      const error = new Error(`${operation}: Cloudflare HTTP ${response.status}: ${detail}`.replaceAll(token, '[token omitido]'));
      error.status = response.status;
      throw error;
    }
    return body;
  }
  const api = async (...args) => (await request(...args)).result;
  api.page = request;
  return api;
}

export async function checkCapabilities(api, account, action, bucket) {
  const checks = [{
    name:'R2', route:`/accounts/${account}/r2/buckets?per_page=1000`, operation:'Listar buckets R2',
    permission:'Workers R2 Storage: Edit',
  }];
  if (action !== 'upload') checks.push({
    name:'Workers', route:`/accounts/${account}/workers/scripts`, operation:'Listar Workers',
    permission:'Workers Scripts: Edit',
  });
  const failures = [];
  let bucketExists = false;
  for (const check of checks) {
    try {
      const result = await api(check.route, {}, check.operation);
      if (check.name === 'R2') bucketExists = result.buckets.some(item => item.name === bucket);
    } catch (error) {
      let detail = error.message;
      if ([401,403].includes(error.status)) {
        detail += `\n  Revisa que el API token corresponda a la cuenta configurada y tenga ${check.permission} sobre esa cuenta. No uses una Global API Key ni credenciales S3.`;
      }
      failures.push(detail);
    }
  }
  if (failures.length) throw new Error(failures.join('\n'));
  return { bucketExists };
}
