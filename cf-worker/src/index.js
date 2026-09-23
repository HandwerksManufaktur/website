/**
 * Handwerksmanufaktur Onboarding – Cloudflare Worker
 */

import { createClickUpTasks, addPipelineExtrasForTask } from './clickup.js';

const FOLDER_IDS = {
  webdesign: '0AEItEqlPzyB0Uk9PVA',
  shk: '0AC4XaHzbPF-HUk9PVA',
};

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

function jsonResp(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function b64u(str) {
  return btoa(str).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
}

function bufToB64u(buf) {
  const bytes = new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return b64u(s);
}

async function getAccessToken(clientEmail, privateKeyPem) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iss: clientEmail,
    scope: 'https://www.googleapis.com/auth/drive',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now,
    exp: now + 3600,
  };

  const enc = obj => b64u(JSON.stringify(obj));
  const signingInput = `${enc(header)}.${enc(payload)}`;

  const pemNormalized = privateKeyPem.replace(/\\n/g, '\n');
  const pemClean = pemNormalized
    .replace(/-----BEGIN PRIVATE KEY-----/g, '')
    .replace(/-----END PRIVATE KEY-----/g, '')
    .replace(/\s+/g, '')
    .trim();

  const binaryStr = atob(pemClean);
  const derBytes = new Uint8Array(binaryStr.length);
  for (let i = 0; i < binaryStr.length; i++) derBytes[i] = binaryStr.charCodeAt(i);

  const cryptoKey = await crypto.subtle.importKey(
    'pkcs8', derBytes.buffer,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false, ['sign']
  );

  const sigBuffer = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', cryptoKey, new TextEncoder().encode(signingInput));
  const jwt = `${signingInput}.${bufToB64u(sigBuffer)}`;

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${jwt}`,
  });

  const data = await res.json();
  if (!data.access_token) throw new Error('Token error: ' + JSON.stringify(data));
  return data.access_token;
}

async function mkdir(token, name, parentId) {
  const res = await fetch('https://www.googleapis.com/drive/v3/files?supportsAllDrives=true', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, mimeType: 'application/vnd.google-apps.folder', parents: [parentId] }),
  });
  const data = await res.json();
  if (!data.id) throw new Error('mkdir failed: ' + JSON.stringify(data));
  return data.id;
}

async function createGoogleDoc(token, name, htmlContent, folderId) {
  const metadata = JSON.stringify({
    name,
    parents: [folderId],
    mimeType: 'application/vnd.google-apps.document',
  });
  const boundary = 'hwm_doc_boundary';
  const body = [
    `--${boundary}`,
    'Content-Type: application/json; charset=UTF-8',
    '',
    metadata,
    `--${boundary}`,
    'Content-Type: text/html; charset=UTF-8',
    '',
    htmlContent,
    `--${boundary}--`,
  ].join('\r\n');

  const res = await fetch(
    'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': `multipart/related; boundary=${boundary}`,
      },
      body,
    }
  );
  const data = await res.json();
  if (!data.id) console.error('createGoogleDoc failed:', JSON.stringify(data));
  return data.id;
}

async function sendNotification(env, firmaName, serviceType, driveLink, formData, missing = []) {
  if (!env.RESEND_API_KEY) { console.error('[Email] RESEND_API_KEY not set'); return; }
  if (!env.NOTIFY_EMAIL)   { console.error('[Email] NOTIFY_EMAIL not set'); return; }

  const typ = serviceType === 'webdesign' ? 'Webdesign' : 'LeadGen & Recruiting';

  const missingHtml = missing.length ? `<div style="background:#fff7e6;border:1.5px solid #D4860A;border-radius:8px;padding:13px 16px;margin-bottom:18px">
      <div style="font-size:11px;font-weight:700;color:#9a6100;letter-spacing:1px;text-transform:uppercase;margin-bottom:7px">⚠️ Noch offen — mit Kunde klären (${missing.length})</div>
      <ul style="margin:0;padding-left:18px;font-size:12.5px;color:#333;line-height:1.75">${missing.map(m => `<li>${escHtml(m)}</li>`).join('')}</ul>
    </div>` : `<div style="background:#eefaf0;border:1.5px solid #2e9e4f;border-radius:8px;padding:11px 16px;margin-bottom:18px;font-size:12.5px;color:#1d6b35;font-weight:600">✅ Vollständig ausgefüllt — nichts offen.</div>`;
  const rows = formData ? Object.entries(formData).map(([k, v]) => {
    if (k.startsWith('\u2500\u2500')) {
      const title = escHtml(k.replace(/\u2500/g,'').trim());
      return `<tr><td colspan="2" style="padding:11px 16px 5px;background:#1a3a52;font-size:10px;font-weight:700;color:#ffffff;letter-spacing:1.2px;text-transform:uppercase">${title}</td></tr>`;
    }
    if (!v) return '';
    const isIndented = k.startsWith('  ');
    const labelStyle = isIndented
      ? 'padding:6px 14px 6px 28px;color:#999;font-size:12px;vertical-align:top;width:210px;'
      : 'padding:7px 14px;color:#444;font-size:12px;font-weight:500;vertical-align:top;width:210px;';
    return `<tr style="border-bottom:1px solid #f2f2f2"><td style="${labelStyle}">${escHtml(k.trim())}</td>` +
    `<td style="padding:7px 14px;font-size:12px;color:#111">${escHtml(String(v)).replace(/\n/g, '<br>').replace(/\|/g,'·')}</td></tr>`;
  }).join('') : '';

  const html = `<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto">
    <div style="background:#1a3a52;padding:22px 26px">
      <div style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Neues Onboarding</div>
      <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700">${escHtml(firmaName)}</h1>
      <p style="color:rgba(255,255,255,0.6);margin:5px 0 0;font-size:12px">Leistung: ${escHtml(typ)}</p>
    </div>
    <div style="padding:20px 24px;background:#f4f6f8">
      <a href="${driveLink}" style="display:inline-block;background:#D4860A;color:#fff;padding:11px 22px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;margin-bottom:20px">→ Drive-Ordner öffnen</a>
      ${missingHtml}
      <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.10)">
        ${rows}
      </table>
    </div>
  </div>`;

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'Onboarding <onboarding@handwerksmanufaktur.digital>',
      to: [env.NOTIFY_EMAIL],
      subject: `Neues Onboarding: ${firmaName} (${typ})${missing.length ? ` — ${missing.length} Punkte offen` : ''}`,
      html,
    }),
  });
  const result = await res.json().catch(() => ({}));
  console.log('[Email] Status:', res.status, JSON.stringify(result));
}

async function handleCreateFolders(request, env, ctx) {
  const body = await request.json();
  const { firmaName, leistungen = [], serviceType = 'webdesign', formData = {}, missing = [], clientV = 0 } = body;
  if (!firmaName) return jsonResp({ error: 'firmaName required' }, 400);
  // Versions-Sperre: veraltete, im Browser gecachte Formular-Versionen haben fehlerhafte
  // Upload-Logik (Abbruch bei Foto-Fehlern, doppelte Ordner-Sets). Klare Ansage statt Chaos.
  if (clientV < 4) {
    return jsonResp({ error: 'Diese Seite wurde zwischenzeitlich aktualisiert. Bitte lade die Seite einmal neu (Strg+R bzw. Cmd+R) und sende das Formular danach erneut ab — deine Texteingaben bleiben dabei gespeichert, nur die Fotos musst du nochmal auswählen.' }, 409);
  }

  const token    = await getAccessToken(env.GOOGLE_CLIENT_EMAIL, env.GOOGLE_PRIVATE_KEY);
  const parentId = FOLDER_IDS[serviceType] || FOLDER_IDS.webdesign;

  const rootId     = await mkdir(token, `${firmaName} - Allgemein`, parentId);
  const internId   = await mkdir(token, '_INTERN', rootId);
  await mkdir(token, 'Vertrag', internId);
  const customerFolderId = await mkdir(token, firmaName, rootId);

  const folderIds = {};

  if (serviceType === 'webdesign') {
    folderIds.logo        = await mkdir(token, 'Logo', customerFolderId);
    folderIds.inhaberfoto = await mkdir(token, 'Inhaberfoto', customerFolderId);
    folderIds.teamfotos   = await mkdir(token, 'Teamfotos', customerFolderId);
    const leistungenFolderId = await mkdir(token, 'Leistungen', customerFolderId);
    for (let i = 0; i < leistungen.length; i++) {
      folderIds[`leistung_${i}`] = await mkdir(token, leistungen[i] || `Leistung ${i + 1}`, leistungenFolderId);
    }
    folderIds.sonstiges = await mkdir(token, 'Sonstiges', customerFolderId);
  } else {
    folderIds.inhaberfoto = await mkdir(token, 'Inhaberfoto', customerFolderId);
    folderIds.teamfotos   = await mkdir(token, 'Teamfotos', customerFolderId);
    const leistungenSHKId = await mkdir(token, 'Leistungen', customerFolderId);
    for (let i = 0; i < leistungen.length; i++) {
      folderIds[`leistung_${i}`] = await mkdir(token, leistungen[i] || `Leistung ${i + 1}`, leistungenSHKId);
    }
    const videosId = await mkdir(token, 'Videos', customerFolderId);
    await mkdir(token, 'Rohmaterial', videosId);
    await mkdir(token, 'Fertige Videos', videosId);
    folderIds.skripte   = await mkdir(token, 'Skripte', customerFolderId);
    folderIds.sonstiges = await mkdir(token, 'Sonstiges', customerFolderId);
  }

  const driveLink = `https://drive.google.com/drive/folders/${customerFolderId}`;

  // Create Google Doc with form data
  if (formData && Object.keys(formData).length > 0) {
    const typ  = serviceType === 'webdesign' ? 'Webdesign' : 'LeadGen & Recruiting';
    const date = new Date().toLocaleString('de-DE', { timeZone: 'Europe/Berlin' });
    const rows = Object.entries(formData).map(function(entry) {
      var k = entry[0]; var v = entry[1];
      if (k.indexOf('──') === 0) {
        return '<tr><td colspan="2" style="padding:12px 16px 6px;background:#1a3a52;font-weight:700;font-size:11px;color:#ffffff;letter-spacing:1px;text-transform:uppercase;border-top:0">' + escHtml(k.replace(/─/g,'').trim()) + '</td></tr>';
      }
      if (!v) return '';
      var isIndented = k.indexOf('  ') === 0;
      var labelStyle = isIndented
        ? 'padding:6px 14px 6px 28px;color:#999;font-size:12px;vertical-align:top;width:210px;'
        : 'padding:7px 14px;color:#333;font-size:12px;font-weight:500;vertical-align:top;width:210px;';
      return '<tr style="border-bottom:1px solid #f2f2f2"><td style="' + labelStyle + '">' + escHtml(k.trim()) + '</td>' +
      '<td style="padding:7px 14px;font-size:12px;color:#111">' + escHtml(String(v)).replace(/\n/g,'<br>').replace(/\|/g,'·') + '</td></tr>';
    }).join('')
    const docHtml = `<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">` +
      `<div style="background:#1a3a52;padding:20px 24px;border-radius:6px;margin-bottom:20px">` +
      `<div style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Onboarding</div>` +
      `<h1 style="color:#ffffff;margin:0;font-size:22px">${escHtml(firmaName)}</h1>` +
      `<p style="color:rgba(255,255,255,0.6);margin:5px 0 0;font-size:12px">Leistung: ${escHtml(typ)} | Eingegangen: ${date}</p>` +
      `</div>` +
      `<table style="width:100%;border-collapse:collapse;box-shadow:0 1px 3px rgba(0,0,0,0.08);border-radius:6px;overflow:hidden">${rows}</table>` +
      `</body></html>`;
    await createGoogleDoc(token, `Onboarding - ${firmaName}`, docHtml, customerFolderId)
      .catch(e => console.error('Doc failed:', e.message));
  }

  // Send email
  try {
    await sendNotification(env, firmaName, serviceType, driveLink, formData, missing);
  } catch(e) {
    console.error('[Email ERROR]', e.message);
  }

  // ClickUp: Tasks anlegen (non-blocking, aber via ctx.waitUntil damit Worker nicht killt)
  if (env.CLICKUP_API_TOKEN) {
    const clickupPromise = createClickUpTasks({
      token: env.CLICKUP_API_TOKEN,
      firmaName,
      serviceType,
      formData,
      driveLink,
      leistungen,
      selfService: env.SELF, // Service Binding: Extras pro Task in eigener Invocation
    }).then(r => console.log('[ClickUp OK]', JSON.stringify(r)))
      .catch(err => console.error('[ClickUp ERROR]', err.message, err.stack));
    if (ctx && ctx.waitUntil) {
      ctx.waitUntil(clickupPromise);
    }
  } else {
    console.error('[ClickUp] CLICKUP_API_TOKEN not set');
  }

  return jsonResp({ success: true, folderIds, customerFolderId, rootId, driveLink });
}

async function handleStartUpload(request, env) {
  const { fileName, mimeType, folderId, totalSize } = await request.json();
  if (!fileName || !folderId) return jsonResp({ error: 'fileName and folderId required' }, 400);

  const token   = await getAccessToken(env.GOOGLE_CLIENT_EMAIL, env.GOOGLE_PRIVATE_KEY);
  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
    'X-Upload-Content-Type': mimeType || 'application/octet-stream',
  };
  if (totalSize) headers['X-Upload-Content-Length'] = String(totalSize);

  const res = await fetch(
    'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true',
    { method: 'POST', headers, body: JSON.stringify({ name: fileName, parents: [folderId] }) }
  );

  if (!res.ok) { const txt = await res.text(); throw new Error(`Drive session ${res.status}: ${txt}`); }
  const sessionUrl = res.headers.get('location');
  if (!sessionUrl) throw new Error('No session URL from Drive');
  return jsonResp({ sessionUrl });
}

async function handleUploadChunk(request, env) {
  const formData  = await request.formData();
  const chunk     = formData.get('chunk');
  const sessionUrl = formData.get('sessionUrl');
  const byteStart = parseInt(formData.get('byteStart'));
  const byteEnd   = parseInt(formData.get('byteEnd'));
  const totalSize = parseInt(formData.get('totalSize'));

  if (!chunk || !sessionUrl) return jsonResp({ error: 'chunk and sessionUrl required' }, 400);

  const chunkBuffer  = await chunk.arrayBuffer();
  const isLast       = byteEnd + 1 >= totalSize;
  const contentRange = isLast
    ? `bytes ${byteStart}-${byteEnd}/${totalSize}`
    : `bytes ${byteStart}-${byteEnd}/*`;

  const res = await fetch(sessionUrl, {
    method: 'PUT',
    headers: { 'Content-Range': contentRange, 'Content-Type': chunk.type || 'application/octet-stream' },
    body: chunkBuffer,
  });

  if (res.status === 200 || res.status === 201 || res.status === 308) {
    return jsonResp({ ok: true, done: res.status !== 308 });
  }
  const txt = await res.text();
  throw new Error(`Chunk upload failed ${res.status}: ${txt}`);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    if (request.method !== 'POST')    return new Response('Method not allowed', { status: 405, headers: CORS });

    try {
      const p = url.pathname;
      if (p === '/create-folders'  || p === '/api/create-folders')  return handleCreateFolders(request, env, ctx);
      // Subtasks + Checklisten für EINEN Projekt-Task. Bewusst ein eigener Request:
      // bei zwei Projekt-Tasks (Recruiting + Leadgen) reichte die Laufzeit eines einzigen
      // Worker-Aufrufs nicht, der zweite Task blieb ohne Subtasks/Checklisten.
      if (p === '/clickup-extras') {
        // Nur der Worker selbst (via Service Binding) darf das aufrufen — der Endpoint
        // ist sonst öffentlich und würde beliebige Task-IDs mit Gerüsten befüllen.
        if (!env.CLICKUP_API_TOKEN) return jsonResp({ error: 'kein Token' }, 500);
        if (request.headers.get('x-internal-auth') !== env.CLICKUP_API_TOKEN) {
          return new Response('Not found', { status: 404, headers: CORS });
        }
        const { taskId, todayMs } = await request.json();
        if (!taskId) return jsonResp({ error: 'taskId fehlt' }, 400);
        // Bewusst SYNCHRON (kein waitUntil): der Aufrufer ist der Worker selbst via
        // Service Binding und wartet auf das Ergebnis — so ist deterministisch fertig,
        // was fertig gemeldet wird.
        await addPipelineExtrasForTask(env.CLICKUP_API_TOKEN, taskId, todayMs || Date.now());
        console.log('[ClickUp Extras OK]', taskId);
        return jsonResp({ ok: true, taskId });
      }
      if (p === '/start-upload'    || p === '/api/start-upload')    return handleStartUpload(request, env);
      if (p === '/upload-chunk'    || p === '/api/upload-chunk')    return handleUploadChunk(request, env);
      return new Response('Not found', { status: 404, headers: CORS });
    } catch (err) {
      console.error('[Worker]', err.message);
      return jsonResp({ error: err.message }, 500);
    }
  },
};
