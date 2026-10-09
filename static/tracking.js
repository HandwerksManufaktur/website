/* HandwerksManufaktur — Analyse mit Einwilligung · /static/tracking.js
   🔴 Noah, 27.09.2026: „will auch dass hotjar da drauf läuft und auch von wo die leute klicken etc. —
   also analytics und alles, wo die von der benutzerführung klicken".
   • GA4 (dieselbe Property wie die Live-Seite) = Seiten, Quellen, Klicks auf Knöpfe als Ereignisse
   • Hotjar über Contentsquare (dasselbe Tag wie auf firma/website) = Heatmaps, Scrolltiefe, Aufnahmen
   • Beides lädt NUR nach „Alle akzeptieren" (§ 25 TDDDG). Schlüssel `cookie-consent` wie auf der
     alten Seite, damit eine dort gegebene Wahl hier gilt.
   • Google Ads (30.09.2026, vorbereitet, INERT): solange ADS_ID leer ist, lädt und feuert für Ads nichts. Mit ADS_ID:
     Consent-Update → gtag('config', ADS_ID) → Conversion bei „hwm:lead" (ADS_LABEL) und je Ereignis-Label (ADS_LABELS).
     Consent Mode v2: der Default steht VOR jedem Google-Tag und steht überall auf „denied"; erst „Alle akzeptieren"
     stellt per gtag('consent','update') auf „granted" (analytics_storage, ad_storage, ad_user_data, ad_personalization).
   • Klick-Kennungen (gclid, gbraid, wbraid, utm_*) nimmt /static/tracking.js beim Aufruf NUR in eine Variable im Speicher dieser
     einen Seite (window.hwmKlick()) — vor der Einwilligung kein sessionStorage, kein localStorage, kein Cookie (§ 25 TDDDG).
     Nichts wird gesendet; weitergegeben werden sie an Close erst mit dem Absenden des Formulars (Einwilligung in die
     Kontaktaufnahme; lp.js / konzept.js lesen window.hwmKlick() und hängen sie an den Versand — auf der Landingpage, wo das
     Formular steht, klappt das auch ohne „Ja"). In sessionStorage `hwm-klick` wird erst nach „Alle akzeptieren" geschrieben,
     damit ein Seitenwechsel innerhalb der Sitzung den Klick behält; ein vorhandener Eintrag wird nur GELESEN. Widerruf löscht ihn.
     Neuer Satz ersetzt den gemerkten nur, wenn er gclid/gbraid/wbraid oder utm_source trägt; sonst werden Schlüssel ergänzt.
   • Außerhalb der echten Domain lädt nichts (die Konzept-Vorschau auf localhost soll die Zahlen nicht
     verfälschen) — außer mit ?tracking=test, das gilt dann für die Sitzung. */
(() => {
'use strict';
const GA4 = 'G-NQNECGN6HT';
const HOTJAR = 'https://t.contentsquare.net/uxa/99d8993a2bc41.js';
const SCHLUESSEL = 'cookie-consent';
/* ---- Google Ads: leer = nichts wird für Ads geladen oder gefeuert ---- */
const ADS_ID = 'AW-17920994298';            // z. B. 'AW-1234567890' (Konto wird erst angelegt)
const ADS_LABEL = 'SOr3CN6tj4sdEPrXsuFC';         // Conversion-Label „Lead" (Primärziel, bei hwm:lead)
// 🔴 Noah, 09.10.2026: „nicht anruf, sondern klick-conversion“ → EINE sekundäre Conversion „Klick: Entwurf/Termin (Website)“
const KLICK_LABEL = 'e20bCI263ZYdEPrXsuFC';
const ADS_LABELS = { entwurf_klick: KLICK_LABEL, termin_klick: KLICK_LABEL, erstgespraech_klick: KLICK_LABEL, anruf_klick: '' };  // sekundäre Ziele; leer = keine eigene Conversion
const KLICK = 'hwm-klick';
const KLICK_KENNUNGEN = ['gclid', 'gbraid', 'wbraid'];   // streng: nur Buchstaben, Ziffern, _ und -
const KLICK_UTM = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];   // großzügig: Umlaute, Leerzeichen ok
const lies = () => { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } };
const schreib = w => { try { localStorage.setItem(SCHLUESSEL, w); } catch (e) {} };
// Einwilligungszustand zusätzlich im Speicher: schlägt localStorage.setItem fehl, gilt trotzdem die Wahl dieser Seite.
let zustimmung = lies() === 'accepted';
let test = false;
try {
  if (new URLSearchParams(location.search).get('tracking') === 'test') sessionStorage.setItem('hm-tracking-test', '1');
  test = sessionStorage.getItem('hm-tracking-test') === '1';
} catch (e) {}
const echt = /(^|\.)handwerksmanufaktur\.digital$/.test(location.hostname) || test;

/* Klick-Kennungen: im Speicher dieser Seite (klick), Rückfall aus sessionStorage nur LESEN. Geschrieben wird dorthin
   erst nach „Alle akzeptieren" (klickSichern). */
let klick = {};
try { const alt = JSON.parse(sessionStorage.getItem(KLICK) || '{}'); if (alt && typeof alt === 'object') klick = alt; } catch (e) {}
function klickSichern() { try { if (zustimmung && Object.keys(klick).length) sessionStorage.setItem(KLICK, JSON.stringify(klick)); } catch (e) {} }
function klickMerken() {
  try {
    const q = new URLSearchParams(location.search), neu = {};
    // Kennungen: ganz gültig oder gar nicht — eine „reparierte" Kennung („ab cd" → „abcd") wäre für Googles Import wertlos
    KLICK_KENNUNGEN.forEach(k => { const v = q.get(k) || ''; if (/^[\w\-]{1,200}$/.test(v)) neu[k] = v; });
    KLICK_UTM.forEach(k => { const v = (q.get(k) || '').replace(/[\u0000-\u001f\u007f<>"']/g, '').trim().slice(0, 200); if (v) neu[k] = v; });
    if (!Object.keys(neu).length) return;
    // ein neuer Satz ersetzt den alten nur, wenn er eine Kennung oder utm_source trägt; sonst werden nur Schlüssel ergänzt
    klick = (neu.gclid || neu.gbraid || neu.wbraid || neu.utm_source) ? neu : Object.assign({}, klick, neu);
    klickSichern();
  } catch (e) {}
}
window.hwmKlick = () => Object.assign({}, klick);   // die Formulare (lp.js, konzept.js) lesen den Klick hier
klickMerken();

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
window.gtag = window.gtag || gtag;
let geladen = false;
function laden() {
  if (geladen || !echt) return; geladen = true;
  // Consent Mode v2: Default VOR jedem Google-Tag, alles „denied". laden() läuft nur nach „Alle akzeptieren" —
  // das Update direkt danach stellt auf „granted".
  gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
  gtag('js', new Date());
  gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted' });
  gtag('config', GA4, { debug_mode: test });
  if (ADS_ID) gtag('config', ADS_ID);
  const g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4; document.head.appendChild(g);
  const h = document.createElement('script'); h.async = true; h.src = HOTJAR; document.head.appendChild(h);
}
/* Ereignis nur senden, wenn eingewilligt und geladen — sonst geht nichts raus. */
function ereignis(name, daten) {
  if (!geladen || !zustimmung) return;
  gtag('event', name, Object.assign({ seite: location.pathname }, daten || {}));
  // Ads: Primärziel = Lead; sekundär = Ereignisse mit eigenem Label. Ohne ADS_ID (bzw. Label) passiert hier nichts.
  if (ADS_ID) {
    const label = name === 'generate_lead' ? ADS_LABEL : (ADS_LABELS[name] || '');
    if (label) gtag('event', 'conversion', Object.assign({ send_to: ADS_ID + '/' + label }, daten && daten.transaction_id ? { transaction_id: daten.transaction_id } : {}));
  }
}

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
    const w = b.dataset.wahl, vorher = zustimmung || lies() === 'accepted'; schreib(w); zustimmung = w === 'accepted';
    const gespeichert = lies() === w;   // localStorage kann blockiert sein — dann steht dort noch die alte Wahl
    box.classList.remove('da'); setTimeout(() => { box.hidden = true; }, 300);
    if (w === 'accepted') { laden(); klickSichern(); }
    else if (vorher) {
      // Widerruf nach vorherigem „Ja": Google sofort auf denied, eigene Ereignisse sind gesperrt (zustimmung = false),
      // gemerkter Klick verschwindet aus dem Browser; geladene Dienste (Hotjar) nur per Neuladen los.
      // 🔴 Neu geladen wird NUR, wenn das „Nein" auch gespeichert ist — sonst liest die Seite das alte „Ja" und
      // startet alles wieder (Gegenprobe 30.09.2026). Ohne Speicher bleibt die Seite stehen, gesperrt und auf denied.
      if (geladen) gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      try { sessionStorage.removeItem(KLICK); } catch (x) {}
      if (geladen && gespeichert) location.reload();
    }
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
  // Klick auf „Entwurf anfordern“ / „Angebot sichern“ / Weg zur Aktionsseite /konzept — nicht die Weiter-/Abschicken-Knöpfe im Formular
  if (!a.matches('.rd-weiter, [type=submit]') && (/entwurf|angebot sichern|doch sichern/i.test(text) || /(^|\/)konzept(\.html|\/|$)/.test(href))) return ereignis('entwurf_klick', { text, bereich });
  if (a.classList.contains('btn')) return ereignis('knopf_klick', { text, bereich });
}, { capture: true });
// Runde 18: Lead erst zählen, wenn die Anfrage wirklich angekommen ist (/static/main.js schickt „hwm:lead" nach dem Versand)
// transaction_id (Zeitstempel + Zufall) je Absenden, damit Google eine Conversion nicht doppelt zählt; liefert der Absender eine, gilt seine.
document.addEventListener('hwm:lead', e => {
  const d = Object.assign({}, e.detail || {});
  if (!d.transaction_id) d.transaction_id = Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
  ereignis('generate_lead', d);
});
// 🎁 Aktionsseite /konzept (29.09.2026): eigenes Ereignis mit Kanal (Code aus ?code=), nur mit Einwilligung wie alles hier
document.addEventListener('hwm:konzept', e => ereignis('konzept_anfrage', e.detail || {}));

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
    // 🎁 ?code=KLEINANZEIGEN (Aktionsseite /konzept) zählt als Herkunft → Aufrufe je Kanal ohne Cookie
    const kanal = (q.get('code') || q.get('c') || '').toUpperCase().replace(/[^A-Z0-9-]/g, '').slice(0, 30);
    if (kanal) ref = 'code:' + kanal;
    else if (q.get('utm_source')) ref = 'utm:' + q.get('utm_source');
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
