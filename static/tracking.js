/* HandwerksManufaktur — Analyse mit Einwilligung · /static/tracking.js
   🔴 Noah, 27.09.2026: „will auch dass hotjar da drauf läuft und auch von wo die leute klicken etc. —
   also analytics und alles, wo die von der benutzerführung klicken".
   • GA4 (dieselbe Property wie die Live-Seite) = Seiten, Quellen, Klicks auf Knöpfe als Ereignisse
   • Hotjar über Contentsquare (dasselbe Tag wie auf firma/website) = Heatmaps, Scrolltiefe, Aufnahmen
   • Beides lädt NUR nach „Alle akzeptieren" (§ 25 TDDDG). Schlüssel `cookie-consent` wie auf der
     alten Seite, damit eine dort gegebene Wahl hier gilt.
   • Außerhalb der echten Domain lädt nichts (die Konzept-Vorschau auf localhost soll die Zahlen nicht
     verfälschen) — außer mit ?tracking=test, das gilt dann für die Sitzung. */
(() => {
'use strict';
const GA4 = 'G-NQNECGN6HT';
const HOTJAR = 'https://t.contentsquare.net/uxa/99d8993a2bc41.js';
const SCHLUESSEL = 'cookie-consent';
const lies = () => { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } };
const schreib = w => { try { localStorage.setItem(SCHLUESSEL, w); } catch (e) {} };
let test = false;
try {
  if (new URLSearchParams(location.search).get('tracking') === 'test') sessionStorage.setItem('hm-tracking-test', '1');
  test = sessionStorage.getItem('hm-tracking-test') === '1';
} catch (e) {}
const echt = /(^|\.)handwerksmanufaktur\.digital$/.test(location.hostname) || test;

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
window.gtag = window.gtag || gtag;
let geladen = false;
function laden() {
  if (geladen || !echt) return; geladen = true;
  gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
  gtag('js', new Date());
  gtag('config', GA4, { debug_mode: test });
  const g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4; document.head.appendChild(g);
  const h = document.createElement('script'); h.async = true; h.src = HOTJAR; document.head.appendChild(h);
}
/* Ereignis nur senden, wenn eingewilligt und geladen — sonst geht nichts raus. */
function ereignis(name, daten) { if (geladen) gtag('event', name, Object.assign({ seite: location.pathname }, daten || {})); }

/* ---- Hinweis unten ---- */
let box = null;
function hinweis() {
  if (box) { box.hidden = false; requestAnimationFrame(() => box.classList.add('da')); box.querySelector('button').focus({ preventScroll: true }); return; }
  box = document.createElement('div');
  box.className = 'cookie-hinweis'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Cookie-Einstellungen');
  // 🔴 Noah, 27.09.2026: „wie dumm ist es das so zu erwähnen, einfach simpel cookies ja nein"
  box.innerHTML = '<p><b class="keks-zeile"><span class="keks" aria-hidden="true">🍪</span> Cookies erlauben?</b><a href="/datenschutz/">Datenschutz</a></p>'
    // 🔴 Runde 15 (28.09.2026), Noah: „Ja links und Ja soll schon vorausgewählt sein. Das Nein kann klein daneben stehen."
    + '<div class="cookie-knoepfe"><button type="button" class="btn btn-tinte cookie-ja" data-wahl="accepted"><span class="ck-haken" aria-hidden="true">✓</span>Ja</button><button type="button" class="cookie-nein" data-wahl="declined">Nein</button></div>';
  document.body.appendChild(box);
  box.addEventListener('click', e => {
    const b = e.target.closest('[data-wahl]'); if (!b) return;
    const w = b.dataset.wahl, vorher = lies(); schreib(w);
    box.classList.remove('da'); setTimeout(() => { box.hidden = true; }, 300);
    if (w === 'accepted') laden();
    else if (vorher === 'accepted' && geladen) location.reload(); // Widerruf: geladene Dienste nur per Neuladen los
  });
  requestAnimationFrame(() => requestAnimationFrame(() => { box.classList.add('da'); const ja = box.querySelector('.cookie-ja'); if (ja) ja.focus({ preventScroll: true }); }));
}
document.addEventListener('click', e => { if (e.target.closest('[data-cookie-wahl]')) hinweis(); });

const wahl = lies();
if (wahl === 'accepted') laden();
else if (!wahl) {
  // erst nach dem ersten Bild, damit der Hinweis Ladezeit und Hero nicht stört
  const zeigen = () => setTimeout(hinweis, 900);
  if (document.readyState === 'complete') zeigen(); else addEventListener('load', zeigen, { once: true });
}

/* ---- Benutzerführung als Ereignisse (GA4); Klicks und Scrolltiefe selbst zeichnet Hotjar auf ---- */
document.addEventListener('click', e => {
  const a = e.target.closest('a, button'); if (!a) return;
  const text = (a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
  const ort = a.closest('section, header, footer, nav');
  const bereich = ort ? (ort.className.split(' ')[0] || ort.tagName.toLowerCase()) : '';
  const href = a.getAttribute('href') || '';
  if (href.startsWith('tel:')) return ereignis('anruf_klick', { text, bereich });
  if (href.startsWith('mailto:')) return ereignis('mail_klick', { text, bereich });
  if (/calendly\.com/.test(href)) return ereignis('termin_klick', { text, bereich });
  if (/kontakt(\.html|\/)/.test(href) || /erstgespr/i.test(text)) return ereignis('erstgespraech_klick', { text, bereich });
  if (a.closest('.lb-k, .projekt')) {
    const b = a.closest('.lb-k, .projekt').querySelector('b');
    return ereignis('referenz_klick', { betrieb: b ? b.textContent.trim() : text });
  }
  if (a.classList.contains('btn')) return ereignis('knopf_klick', { text, bereich });
}, { capture: true });
// Runde 18: Lead erst zählen, wenn die Anfrage wirklich angekommen ist (/static/main.js schickt „hwm:lead" nach dem Versand)
document.addEventListener('hwm:lead', e => ereignis('generate_lead', e.detail || {}));

/* ---- Seiten-Zähler OHNE Cookies (29.09.2026) ----
   🔴 Noah: „bau da überall nen tracker rein … welche seiten aufrufe bekommen … wo die leute drauf drücken, wie viele, woher".
   GA4/Hotjar zählen nur nach „Ja" — in 28 Tagen 15 Startseiten-Aufrufe, fast nur Noah. Dieser Zähler speichert NICHTS
   im Browser (kein Cookie, kein localStorage) und schickt keine Nutzer-Kennung; die Aufruf-Kennung lebt nur im Speicher
   dieser einen Seite. Gespeichert wird im Worker seiten-zaehler (system/apps/seiten-zaehler): Seite, Ereignis, Klickziel,
   Herkunfts-Host, Handy/Desktop, Land — keine IP. Läuft nur auf der echten Domain. */
if (echt && !test) {
  const Z = 'https://seiten-zaehler.handwerksmanufaktur.workers.dev/z';
  const id = Math.random().toString(36).slice(2, 12);
  const geraet = innerWidth < 768 ? 'm' : 'd';
  const senden = (t, extra) => {
    const d = JSON.stringify(Object.assign({ t, s: location.hostname, p: location.pathname, g: geraet, id }, extra || {}));
    try { if (!(navigator.sendBeacon && navigator.sendBeacon(Z, new Blob([d], { type: 'text/plain' })))) fetch(Z, { method: 'POST', body: d, keepalive: true, mode: 'no-cors' }); } catch (x) {}
  };
  let ref = 'direkt';
  try {
    const q = new URLSearchParams(location.search);
    if (q.get('utm_source')) ref = 'utm:' + q.get('utm_source');
    else if (document.referrer) { const h = new URL(document.referrer).hostname.replace(/^www\./, ''); if (h && h !== location.hostname) ref = h; }
  } catch (x) {}
  senden('v', { r: ref });
  document.addEventListener('click', e => {
    const a = e.target.closest('a, button, summary'); if (!a || a.closest('.cookie-hinweis')) return;
    const text = (a.getAttribute('aria-label') || a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 70);
    const href = a.getAttribute && a.getAttribute('href') || '';
    const wohin = href.startsWith('tel:') ? ' → Anruf' : href.startsWith('mailto:') ? ' → Mail' : /calendly/.test(href) ? ' → Termin' : '';
    senden('k', { z: (text || a.tagName.toLowerCase()) + wohin });
  }, { capture: true });
  document.addEventListener('hwm:lead', e => senden('f', { z: (e.detail && e.detail.formular) || 'formular' }));
  const marken = [25, 50, 75, 100], erreicht = new Set();
  let lauf = false;
  const tiefe = () => {
    lauf = false;
    const h = document.documentElement.scrollHeight - innerHeight; if (h <= 0) return;
    const p = Math.round(scrollY / h * 100);
    marken.forEach(m => { if (p >= m - 2 && !erreicht.has(m)) { erreicht.add(m); senden('l', { z: String(m) }); } });
  };
  addEventListener('scroll', () => { if (!lauf) { lauf = true; requestAnimationFrame(tiefe); } }, { passive: true });
}
})();
