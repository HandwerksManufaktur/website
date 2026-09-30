/* 📍 Stadt- und Gewerkseiten (29.09.2026): Klick-Strecke im Hero statt Kontaktformular.
   Erst drei Fragen zum Antippen (Gewerk · Homepage heute · Ziel), dann Betrieb, Name, E-Mail, Telefon.
   Die Antworten reisen im Feld „seite“ mit, der Code (SEO-<SEITE>) zeigt in Close, woher die Anfrage kam.
   Versand an denselben Onboarding-Worker wie /konzept → Close-Lead, Mails, D1 (firma/website/cf-worker/src/konzept.js). */
(() => {
  const ZIEL = 'https://handwerksmanufaktur-onboarding.handwerksmanufaktur.workers.dev/konzept-anfrage';
  const f = document.querySelector('form.lp-form'); if (!f) return;
  const $ = (s, r = f) => r.querySelector(s), $$ = (s, r = f) => [...r.querySelectorAll(s)];
  const schritte = $$('.sf-schritt'), nr = $('.sf-nr'), gesamt = $('.sf-gesamt'), balken = $('.sf-balken i'), zurueck = $('.sf-zurueck');
  const antworten = f.dataset.gewerk ? { gewerk: f.dataset.gewerk } : {};
  let n = 0;

  const zeig = (k, fokus = true) => {
    n = Math.max(0, Math.min(schritte.length - 1, k));
    schritte.forEach((s, i) => { s.hidden = i !== n; s.classList.toggle('an', i === n); });
    nr.textContent = n + 1; gesamt.textContent = schritte.length;
    balken.style.transform = `scaleX(${(n + 1) / schritte.length})`;
    zurueck.hidden = n === 0;
    const feld = $('input.ka-feld', schritte[n]); if (fokus && feld) feld.focus({ preventScroll: true });
  };
  const fehler = (text) => { const p = $('.ka-fehler', schritte[n]); if (p) { p.textContent = text || ''; p.hidden = !text; } };
  const pruef = {
    text: v => v.trim().length > 1 || 'Bitte kurz ausfüllen.',
    mail: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || 'Bitte eine gültige E-Mail-Adresse eintragen.',
    tel: v => ((v.replace(/\D/g, '').length >= 6) && /^[+()\d\s\/.-]+$/.test(v.trim())) || 'Bitte eine Telefonnummer eintragen, zum Beispiel 0170 1234567.',
  };
  const gueltig = () => {
    const feld = $('input[data-pruef]', schritte[n]); if (!feld) return true;
    const r = pruef[feld.dataset.pruef](feld.value);
    feld.classList.toggle('fehlt', r !== true); fehler(r === true ? '' : r);
    if (r !== true) feld.focus(); return r === true;
  };
  const weiter = () => { if (gueltig()) zeig(n + 1); };

  // 📈 Google Ads (30.09.2026): Klick-Kennungen, die tracking.js beim Aufruf im Speicher der Seite hält (window.hwmKlick()),
  // reisen erst JETZT mit — mit dem Absenden (Einwilligung in die Kontaktaufnahme). Der Worker legt sie an den Close-Lead.
  const klickFelder = fd => {
    try {
      const k = typeof window.hwmKlick === 'function' ? window.hwmKlick() : JSON.parse(sessionStorage.getItem('hwm-klick') || '{}');
      ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
        .forEach(n => { if (k[n]) fd.set(n, String(k[n]).slice(0, 200)); });
    } catch (e) {}
  };

  // Antipp-Schritte: ein Tipp = Antwort + weiter (kein Extra-Knopf)
  $$('[data-wahl]').forEach(b => b.addEventListener('click', () => {
    const feld = b.dataset.wahl;
    antworten[feld] = b.dataset.wert;
    $$(`[data-wahl="${feld}"]`).forEach(x => x.classList.toggle('gewaehlt', x === b));
    document.dispatchEvent(new CustomEvent('hwm:lp-schritt', { detail: { feld, wert: b.dataset.wert } }));
    setTimeout(() => zeig(n + 1), 140);
  }));
  $$('[data-weiter]').forEach(b => b.addEventListener('click', weiter));
  zurueck.addEventListener('click', () => zeig(n - 1));
  f.addEventListener('keydown', e => {
    if (e.key !== 'Enter' || e.target.tagName !== 'INPUT') return;
    e.preventDefault();
    if (n < schritte.length - 1) weiter(); else f.requestSubmit();
  });

  let laeuft = false;   // In-Flight-Schutz: ein zweites Absenden (Enter während der Antwort) wird verworfen, sonst zwei POSTs + zwei Conversions
  f.addEventListener('submit', async e => {
    e.preventDefault();
    if (laeuft || !gueltig()) return;
    laeuft = true;
    const knopf = $('button[type=submit]'); knopf.disabled = true; fehler('');
    const fd = new FormData(f);
    const zusatz = Object.entries(antworten).map(([k, v]) => `${k}=${v}`).join('&');
    fd.set('seite', (location.pathname + (zusatz ? '?' + zusatz : '')).slice(0, 200));
    klickFelder(fd);
    let j = null;
    try {
      const r = await fetch(ZIEL, { method: 'POST', body: fd });
      j = await r.json().catch(() => null);
      if (!r.ok || !j || !j.ok) throw new Error((j && j.fehler) || 'Versand');
    } catch (x) {
      knopf.disabled = false; laeuft = false;
      fehler(x && x.message && x.message !== 'Versand' && x.message !== 'Failed to fetch' ? x.message : 'Das hat gerade nicht geklappt. Ruf gern direkt an: +49 8194 7174990');
      return;
    }
    document.dispatchEvent(new CustomEvent('hwm:lead', { detail: { formular: 'landingpage', kanal: fd.get('code') } }));
    schritte.forEach(s => s.hidden = true); zurueck.hidden = true;
    $('.sf-kopf').hidden = true; $('.sf-balken').hidden = true;
    const fertig = $('.ka-fertig'); fertig.hidden = false;
    $('[data-betrieb]', fertig).textContent = fd.get('betrieb');
    $('h3', fertig).focus({ preventScroll: true });
  });
  zeig(0, false);
})();

/* 🎁 Geschenk-Fenster (30.09.2026). Geht auf, sobald der Besucher 15 s auf der Seite ist UND gescrollt hat — einmal je Sitzung.
   Runde 3: Wer schließen will (×, Escape, Klick daneben), sieht erst die Warnung „verfällt für diesen Besuch".
   Bestätigt er, ist es für diese Sitzung weg — kein Knopf, kein zweites Aufgehen. Erst ein neuer Besuch zeigt es wieder. */
(() => {
  const d = document.querySelector('dialog.lp-geschenk'); if (!d) return;
  const MERK = 'hwm-geschenk';
  const gesehen = () => { try { return sessionStorage.getItem(MERK) === '1'; } catch (e) { return false; } };
  const merken = () => { try { sessionStorage.setItem(MERK, '1'); } catch (e) {} };
  const teil = s => d.querySelector(s);
  let vorher = '.lg-auf';
  const zeige = s => { ['.lg-auf', '.lg-form', '.lg-warnung'].forEach(x => teil(x).hidden = x !== s); };
  const auf = () => {
    if (d.open) return;
    d.showModal(); d.classList.add('an'); merken();
    document.dispatchEvent(new CustomEvent('hwm:geschenk', { detail: { schritt: 'auf' } }));
  };
  const warnen = () => {
    if (!teil('.lg-warnung').hidden) return;
    vorher = teil('.lg-form').hidden ? '.lg-auf' : '.lg-form';
    const fertig = teil('.ka-fertig'); if (fertig && !fertig.hidden) return schliessen();   // nach dem Absenden ohne Warnung
    zeige('.lg-warnung'); teil('.lg-zurueck').focus({ preventScroll: true });
  };
  const schliessen = () => { d.classList.remove('an'); d.close(); document.dispatchEvent(new CustomEvent('hwm:geschenk', { detail: { schritt: 'verfallen' } })); };
  teil('.lg-zu').addEventListener('click', warnen);
  d.addEventListener('cancel', e => { e.preventDefault(); warnen(); });
  d.addEventListener('click', e => { if (e.target === d) warnen(); });
  teil('.lg-zurueck').addEventListener('click', () => { zeige(vorher); });
  teil('.lg-verfallen').addEventListener('click', schliessen);
  teil('.lg-los').addEventListener('click', () => {
    zeige('.lg-form');
    const b = teil('.lg-form .lp-wahl button, .lg-form input.ka-feld'); if (b) b.focus({ preventScroll: true });
  });
  if (gesehen()) return;
  let gescrollt = false, zeitUm = false;
  const pruef = () => { if (gescrollt && zeitUm && !gesehen()) auf(); };
  addEventListener('scroll', () => { if (scrollY > 200) { gescrollt = true; pruef(); } }, { passive: true });
  setTimeout(() => { zeitUm = true; pruef(); }, 15000);
})();
