/* 🎁 Aktionsseite /konzept (29.09.2026): „Konzept anfordern" in sieben kleinen Schritten.
   Ein Feld pro Schritt, Enter = weiter, Website und Logo lassen sich überspringen, der Code kommt aus der Adresse
   (?code=KLEINANZEIGEN oder ?c=…). Versand an den Onboarding-Worker → Close-Lead, Mails, D1 (firma/website/cf-worker/src/konzept.js). */
(() => {
  const ZIEL = 'https://handwerksmanufaktur-onboarding.handwerksmanufaktur.workers.dev/konzept-anfrage';
  const f = document.querySelector('form.ka-form'); if (!f) return;
  const $ = (s, r = f) => r.querySelector(s), $$ = (s, r = f) => [...r.querySelectorAll(s)];
  const schritte = $$('.sf-schritt'), nr = $('.sf-nr'), balken = $('.sf-balken i'), zurueck = $('.sf-zurueck');
  const LOGO_MAX = 5 * 1024 * 1024, LOGO_OK = /\.(png|jpe?g|svg|pdf)$/i;
  let n = 0;

  const q = new URLSearchParams(location.search);
  const code = String(q.get('code') || q.get('c') || '').trim().toUpperCase().replace(/[^A-Z0-9-]/g, '').slice(0, 30);
  if (code) {
    $('input[name=code]').value = code;
    const chip = $('.ka-code-chip'); chip.hidden = false; $('b', chip).textContent = code;
  }

  // 📈 Google Ads (30.09.2026): Klick-Kennungen, die tracking.js beim Aufruf im Speicher der Seite hält (window.hwmKlick()),
  // reisen erst JETZT mit — mit dem Absenden (Einwilligung in die Kontaktaufnahme). Der Worker legt sie an den Close-Lead.
  const klickFelder = fd => {
    try {
      const k = typeof window.hwmKlick === 'function' ? window.hwmKlick() : JSON.parse(sessionStorage.getItem('hwm-klick') || '{}');
      ['gclid', 'gbraid', 'wbraid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
        .forEach(n => { if (k[n]) fd.set(n, String(k[n]).slice(0, 200)); });
    } catch (e) {}
  };

  const zeig = (k, fokus = true) => {
    n = Math.max(0, Math.min(schritte.length - 1, k));
    schritte.forEach((s, i) => { s.hidden = i !== n; s.classList.toggle('an', i === n); });
    nr.textContent = n + 1; balken.style.transform = `scaleX(${(n + 1) / schritte.length})`;
    zurueck.hidden = n === 0;
    const feld = $('input:not([type=file])', schritte[n]); if (fokus && feld) feld.focus({ preventScroll: true });
  };
  const fehler = (text) => { const p = $('.ka-fehler', schritte[n]); if (p) { p.textContent = text || ''; p.hidden = !text; } };
  const pruef = {
    text: v => v.trim().length > 1 || 'Bitte kurz ausfüllen.',
    mail: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || 'Bitte eine gültige E-Mail-Adresse eintragen.',
    tel: v => ((v.replace(/\D/g, '').length >= 6) && /^[+()\d\s\/.-]+$/.test(v.trim())) || 'Bitte eine Telefonnummer eintragen, zum Beispiel 0170 1234567.',
    web: v => !v.trim() || /^[^\s]+\.[a-z]{2,}(\/.*)?$/i.test(v.trim().replace(/^https?:\/\//i, '')) || 'Das sieht nicht nach einer Adresse aus. Sonst einfach „Noch keine“ drücken.',
    frei: () => true,
  };
  const gueltig = () => {
    const s = schritte[n], feld = $('input[data-pruef]', s); if (!feld) return true;
    const r = pruef[feld.dataset.pruef](feld.value);
    feld.classList.toggle('fehlt', r !== true); fehler(r === true ? '' : r);
    if (r !== true) feld.focus(); return r === true;
  };
  const weiter = () => { if (gueltig()) zeig(n + 1); };

  $$('[data-weiter]').forEach(b => b.addEventListener('click', weiter));
  $$('[data-skip]').forEach(b => b.addEventListener('click', () => {
    $$('input', schritte[n]).forEach(i => { if (i.type === 'file') { i.value = ''; logoZeigen(); } else i.value = ''; i.classList.remove('fehlt'); });
    fehler(''); zeig(n + 1);
  }));
  zurueck.addEventListener('click', () => zeig(n - 1));
  f.addEventListener('keydown', e => {
    if (e.key !== 'Enter' || e.target.tagName !== 'INPUT' || e.target.type === 'file') return;
    e.preventDefault();
    if (n < schritte.length - 1) weiter(); else f.requestSubmit();
  });

  // Logo: Datei wählen oder hineinziehen, sofort prüfen (Typ + 5 MB)
  const logo = $('input[type=file]'), drop = $('.ka-drop');
  const logoZeigen = () => {
    const d = logo.files && logo.files[0];
    drop.classList.toggle('hat', !!d);
    $('b', drop).textContent = d ? d.name : 'Logo auswählen';
    $('small', drop).textContent = d ? `${Math.max(1, Math.round(d.size / 1024))} KB · tippen zum Ändern` : 'PNG, JPG, SVG oder PDF, bis 5 MB';
    $('[data-logo-weiter]').hidden = !d;
  };
  logo.addEventListener('change', () => {
    const d = logo.files && logo.files[0];
    if (d && (d.size > LOGO_MAX || !LOGO_OK.test(d.name))) {
      fehler(d.size > LOGO_MAX ? 'Die Datei ist größer als 5 MB. Schick das Logo später einfach per Mail.' : 'Bitte als PNG, JPG, SVG oder PDF.');
      logo.value = '';
    } else fehler('');
    logoZeigen();
  });
  ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, () => drop.classList.add('ueber')));
  ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, () => drop.classList.remove('ueber')));

  let laeuft = false;   // In-Flight-Schutz: ein zweites Absenden (Enter während der Antwort) wird verworfen, sonst zwei POSTs + zwei Conversions
  f.addEventListener('submit', async e => {
    e.preventDefault();
    if (laeuft || !gueltig()) return;
    laeuft = true;
    const knopf = $('button[type=submit]'); knopf.disabled = true; fehler('');
    const fd = new FormData(f); fd.append('seite', location.pathname + location.search);
    klickFelder(fd);
    if (!(logo.files && logo.files[0])) fd.delete('logo');
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
    const kanal = code || 'OHNE-CODE';
    document.dispatchEvent(new CustomEvent('hwm:lead', { detail: { formular: 'konzept', kanal } }));
    document.dispatchEvent(new CustomEvent('hwm:konzept', { detail: { kanal, logo: !!j.hat_logo } }));
    schritte.forEach(s => s.hidden = true); zurueck.hidden = true;
    $('.sf-kopf').hidden = true; $('.sf-balken').hidden = true; $('.ka-code-chip').hidden = true;
    const fertig = $('.ka-fertig'); fertig.hidden = false;
    $('[data-betrieb]', fertig).textContent = fd.get('betrieb');
    $('[data-ohne-logo]', fertig).hidden = !!j.hat_logo;
    $('h3', fertig).focus({ preventScroll: true });
  });
  zeig(0, false);
})();
