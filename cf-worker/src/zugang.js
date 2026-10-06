/**
 * 🔐 POST /zugang (06.10.2026): verschlüsselte GitHub-Zugangsdaten vom Kunden.
 * Der Browser verschlüsselt (AES-GCM + RSA-OAEP-gewickelter Schlüssel), der Worker sieht NIE Klartext
 * und kann nicht entschlüsseln (der private Schlüssel liegt nur auf Noahs Mac).
 * Abgelegt wird nur der Chiffretext in D1 (kunden_zugang). Mail an info@ enthält keine Kundendaten außer dem Firmennamen.
 */
const INFO = 'info@handwerksmanufaktur.digital';
const MAX_BYTES = 16 * 1024;
const MAX_PRO_STUNDE = 5;
const CORS = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400' };
const antwort = (d, status = 200) => new Response(JSON.stringify(d), { status, headers: { ...CORS, 'Content-Type': 'application/json' } });
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const B64 = /^[A-Za-z0-9+/]+={0,2}$/;

async function ipHash(request, env) {
  const ip = request.headers.get('cf-connecting-ip') || 'unbekannt';
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${env.KONZEPT_SALT || 'hwm'}|zugang|${ip}`));
  return [...new Uint8Array(h)].slice(0, 8).map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function handleZugang(request, env, { fetchImpl = fetch, jetzt = () => new Date() } = {}) {
  const roh = await request.text();
  if (roh.length > MAX_BYTES) return antwort({ ok: false, fehler: 'Zu groß.' }, 413);
  let b;
  try { b = JSON.parse(roh); } catch { return antwort({ ok: false, fehler: 'Ungültige Anfrage.' }, 400); }
  if (!b || typeof b !== 'object') return antwort({ ok: false, fehler: 'Ungültige Anfrage.' }, 400);
  if (b.website) return antwort({ ok: true });                       // Honeypot: still schlucken
  const firma = String(b.firma || '').trim().slice(0, 120);
  const c = b.chiffre;
  if (!firma) return antwort({ ok: false, fehler: 'Firmenname fehlt.' }, 400);
  if (!c || ![c.k, c.iv, c.c].every((x) => typeof x === 'string' && x.length > 8 && B64.test(x))) {
    return antwort({ ok: false, fehler: 'Ungültige Verschlüsselung.' }, 400);
  }
  if (!env.RUN_DB) return antwort({ ok: false, fehler: 'Speicher nicht erreichbar.' }, 500);
  const now = jetzt();
  const hash = await ipHash(request, env);
  const seit = new Date(now.getTime() - 3600e3).toISOString();
  const n = await env.RUN_DB.prepare('SELECT COUNT(*) AS n FROM kunden_zugang WHERE ip_hash = ? AND erstellt > ?').bind(hash, seit).first();
  if (n && n.n >= MAX_PRO_STUNDE) return antwort({ ok: false, fehler: 'Zu viele Versuche. Bitte ruft uns kurz an.' }, 429);
  const chiffre = JSON.stringify({ k: c.k, iv: c.iv, c: c.c });
  const res = await env.RUN_DB.prepare('INSERT INTO kunden_zugang (firma, chiffre, erstellt, ip_hash) VALUES (?, ?, ?, ?)').bind(firma, chiffre, now.toISOString(), hash).run();
  const id = res && res.meta ? res.meta.last_row_id : null;

  let mail = false;
  if (env.RESEND_API_KEY) {
    const test = /test/i.test(firma);
    const betreff = `${test ? 'TEST: ' : ''}Neue GitHub-Zugangsdaten von ${firma.replace(/[\r\n]/g, ' ')} liegen bereit`;
    const html = `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#16130E"><p>Neue GitHub-Zugangsdaten von <strong>${esc(firma)}</strong> liegen verschlüsselt bereit.</p><p>Abholen auf deinem Mac: <code>.venv/bin/python system/scripts/zugang_abholen.py</code></p><p style="color:#6b6258;font-size:13px">Die Angaben stehen bewusst nicht in dieser Mail.</p></div>`;
    try {
      const r = await fetchImpl('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ from: 'HandwerksManufaktur Zugang <onboarding@handwerksmanufaktur.digital>', to: [INFO], subject: betreff, html, text: `Neue GitHub-Zugangsdaten von ${firma} liegen verschlüsselt bereit. Abholen: .venv/bin/python system/scripts/zugang_abholen.py` }),
      });
      mail = r.ok;
    } catch { mail = false; }
  }
  return antwort({ ok: true, id, mail });
}
