/** Native Cloudflare contact delivery; recipient is never supplied by visitors. */
const ORIGIN = 'https://nubeparapymes.online';
const CATEGORIES = Object.freeze({software: 'Elegir software', herramientas: 'Ayuda con una herramienta', correccion: 'Corrección editorial', servicios: 'Apoyo digital', colaboracion: 'Colaboración', otra: 'Otra consulta'});
const json = (data, status = 200) => Response.json(data, {status, headers: {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'}});
const email = value => typeof value === 'string' && value.length <= 254 && /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$/.test(value);
const text = (value, max) => typeof value === 'string' && value.trim().length <= max && !/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value);

async function readBody(request) {
  if (Number(request.headers.get('Content-Length')) > 16000) throw new Error('size');
  const reader = request.body?.getReader();
  if (!reader) throw new Error('body');
  let bytes = 0, chunks = [];
  for (;;) {
    const {value, done} = await reader.read();
    if (done) break;
    bytes += value.byteLength;
    if (bytes > 16000) { await reader.cancel(); throw new Error('size'); }
    chunks.push(value);
  }
  const body = new Uint8Array(bytes); let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder().decode(body));
}

export async function handleContact(request, env, verifyFetch = fetch) {
  const origin = env.CONTACT_ORIGIN || ORIGIN;
  const hostname = new URL(origin).hostname;
  const brand = env.CONTACT_BRAND || 'Nube para Pymes';
  const categories = env.CONTACT_CATEGORIES ? JSON.parse(env.CONTACT_CATEGORIES) : CATEGORIES;
  if (new URL(request.url).pathname.replace(/\/$/, '') !== '/api/contact') return json({success:false}, 404);
  const ready = Boolean(env.EMAIL && env.CONTACT_RATE_LIMITER && env.TURNSTILE_SECRET && env.TURNSTILE_SITE_KEY && email(env.CONTACT_TO));
  if (request.method === 'GET') return json({ready, siteKey: ready ? env.TURNSTILE_SITE_KEY : null});
  if (request.method !== 'POST') return json({success:false}, 405);
  if (request.headers.get('Origin') !== origin) return json({success:false}, 403);
  if (!ready) return json({success:false}, 503);
  if (!request.headers.get('Content-Type')?.startsWith('application/json')) return json({success:false}, 415);
  const limit = await env.CONTACT_RATE_LIMITER.limit({key: request.headers.get('CF-Connecting-IP') || 'unknown'});
  if (!limit.success) return json({success:false}, 429);
  let data;
  try { data = await readBody(request); } catch { return json({success:false}, 400); }
  if (!data || typeof data !== 'object' || Array.isArray(data) || data.website || data.consent !== true ||
      !Object.hasOwn(categories, data.category) || !text(data.name,100) || !data.name.trim() || !email(data.email) ||
      !text(data.message,5000) || data.message.trim().length < 20 || !text(data.business || '',150) ||
      !text(data.subject || '',160) || /[\r\n]/.test(data.subject || '') ||
      !text(data.reference || '',500) || typeof data.turnstile !== 'string' || !data.turnstile || data.turnstile.length > 2048) return json({success:false},400);
  if (data.reference) { try { if (!['https:','http:'].includes(new URL(data.reference).protocol)) return json({success:false},400); } catch { return json({success:false},400); } }
  try {
    const verified = await verifyFetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {method:'POST', body: new URLSearchParams({secret:env.TURNSTILE_SECRET, response:data.turnstile, remoteip:request.headers.get('CF-Connecting-IP') || ''}), signal:AbortSignal.timeout(8000)});
    const proof = await verified.json();
    if (!verified.ok || proof.success !== true || proof.hostname !== hostname || proof.action !== 'contact') return json({success:false},403);
    const id = crypto.randomUUID();
    await env.EMAIL.send({from:'formularios@' + hostname, to:env.CONTACT_TO,
      replyTo:data.email, subject:'[' + brand + '] ' + categories[data.category],
      text:`Consulta: ${categories[data.category]}\nAsunto: ${(data.subject || '').trim()}\nNombre: ${data.name.trim()}\nCorreo: ${data.email}\nNegocio: ${(data.business || '').trim()}\nEnlace: ${(data.reference || '').trim()}\nIdioma: ${data.language === 'en' ? 'en' : 'es'}\nReferencia: ${id}\n\n${data.message.trim()}\n\nConsentimiento: aceptado para responder a esta consulta.`});
    return json({success:true,reference:id});
  } catch { return json({success:false},503); }
}

export default {async fetch(request, env) {
  try { return await handleContact(request, env); }
  catch { return json({success:false},503); }
}};
