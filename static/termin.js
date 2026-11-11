/* 📅 Termin-Dialog „Kostenloses Beratungsgespräch" (11.11.2026, 🌐 Helena) — gleiche Datei auf handwerksmanufaktur.digital
 * (/static/termin.js) und shk.handwerksmanufaktur.digital (/termin.js). Einbinden:
 *   <script src="…/termin.js?v=…" data-seite="hwm|shk" data-knopf="btn btn-tinte|btn btn-ink" defer></script>
 * Noah, 11.11.2026: „Jetzt Termin buchen … zuerst eine kurze Auswahl: worum geht es … dann Namen/Firmennamen
 * … und beim Weiterklicken gleich im Kalender eingetragen." Ablauf: 1 Themen (mehrere) → 2 Name, Betrieb, Telefon,
 * E-Mail → Worker /termin-anfrage (Close-Lead + Aufgabe + Mail an info@) → 3 Calendly „Kostenloses Beratungsgespräch" (Slug potenzial-erstgespraech) eingebettet
 * und vorausgefüllt → Buchung steht in Noahs Kalender, Worker trägt sie in Close nach → 4 „Dein Termin steht".
 * Öffnet sich über [data-termin] und über jeden Potenzial-Link auf calendly.com/noahseelau (ohne JS bleibt der Link). */
(function () {
  'use strict';
  var skript = document.currentScript || {};
  var ds = skript.dataset || {};
  var SEITE = ds.seite === 'shk' ? 'shk' : 'hwm';
  var KNOPF = ds.knopf || 'btn btn-tinte';
  var API = 'https://handwerksmanufaktur-onboarding.handwerksmanufaktur.workers.dev/termin-anfrage';
  var CAL = 'https://calendly.com/noahseelau/potenzial-erstgespraech';
  var SLUG_THEMA = { 'website-potenzial': 'website', 'leadgen-potenzial': 'kunden', 'recruiting-potenzial': 'mitarbeiter', 'recruiting-potenzial-hwm': 'mitarbeiter', 'potenzial-erstgespraech': '' };
  var IC = {
    website: '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
    kunden: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    mitarbeiter: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 20h6a5 5 0 0 0-3.5-4.8"/>',
    seo: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    ads: '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1z"/><path d="M15 9a4 4 0 0 1 0 6M18 6a8 8 0 0 1 0 12"/>',
    offen: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    kalender: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>',
    zu: '<path d="M18 6 6 18M6 6l12 12"/>',
    ok: '<path d="m5 12 4 4L19 7"/>',
    schloss: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    pfeil: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    bad: '<path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/><path d="m10 5-2 2"/><path d="M2 12h20"/><path d="M7 19v2"/><path d="M17 19v2"/>'
  };
  // Genau drei Themen nebeneinander (Noah, 11.11.2026: SHK „nur 3 sachen - aufträge, monteure oder website", HWM „generell eigentlich auch nur 3 sachen …
  // seo oder sea oder shooting fällt ja unter webdesign") — der Satz darunter fängt SEO, Google-Anzeigen und Shootings ab.
  var THEMEN = SEITE === 'shk' ? [
    ['kunden', 'Aufträge', 'Bad, Heizung, Wärmepumpe', 'bad'],
    ['mitarbeiter', 'Monteure', 'Bewerber aus deiner Region'],
    ['website', 'Website', 'Neu oder überarbeitet']
  ] : [
    ['website', 'Website', 'Neu oder überarbeitet'],
    ['kunden', 'Neue Kunden', 'Mehr Anfragen über Werbung'],
    ['mitarbeiter', 'Neue Mitarbeiter', 'Bewerbungen über Social Media']
  ];
  function svg(n, k) { return '<svg class="' + (k || 'td-ic') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + IC[n] + '</svg>'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var CSS = '.td .td-satz{margin:-10px 0 16px;font-size:15px;opacity:.75}' +
    '.td .rd-wahl button{justify-content:flex-start;text-align:left;gap:12px;padding:12px 16px;min-height:64px;line-height:1.25}' +
    '.td .rd-wahl button small{display:block;font-weight:500;font-size:13px;opacity:.72;margin-top:2px}' +
    '.td .rd-wahl button.an small{opacity:.85}' +
    '.td .td-ic{width:22px;height:22px;flex:none}' +
    '.td .rd-kick .td-ic{width:20px;height:20px}' +
    '.td .rd-zu .td-ic{width:20px;height:20px}' +
    '.td .td-knopf{width:100%;justify-content:center;margin-top:14px;gap:8px}' +
    '.td .td-knopf .td-ic{width:18px;height:18px}' +
    '.td .td-zeile2{display:grid;grid-template-columns:1fr;gap:0 10px}' +
    '@media (min-width:520px){.td .td-zeile2{grid-template-columns:1fr 1fr}}' +
    '.td .td-fehler{color:#9E2F22;font-size:14px;font-weight:600;margin:6px 0 0}' +
    '.td .td-hinweis{font-size:13px;opacity:.75;margin:6px 0 0}.td .td-hinweis a,.td .td-alt a{text-decoration:underline}' +
    '.td.td-weit{width:min(760px,calc(100vw - 24px))}.td.td-weit .rd-form{padding:30px 34px 32px}' +
    '.td .rd-wahl.td-drei{grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}' +
    '.td .rd-wahl.td-drei button{flex-direction:column;justify-content:flex-start;align-items:center;text-align:center;gap:10px;min-height:150px;padding:22px 12px;border-radius:20px}' +
    '.td .rd-wahl.td-drei button>span{font-size:18px}.td .rd-wahl.td-drei button small{font-size:13px;margin-top:4px}' +
    '.td .rd-wahl.td-drei .td-ic{width:30px;height:30px}' +
    '.td .td-mail{display:flex;gap:10px;align-items:flex-start;font-size:14px;line-height:1.45;margin:4px 0 4px;padding:12px 14px;border-radius:14px;background:rgba(127,127,127,.08)}.td .td-mail .td-ic{width:18px;height:18px;margin-top:1px;opacity:.7}' +
    '.td .td-fuss{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:18px}.td .td-fuss .td-zurueck{margin-top:0}' +
    '.td .td-fs{flex:1;display:flex;flex-direction:column;align-items:flex-end;gap:6px;max-width:260px;margin-left:auto}.td .td-fs span{font-size:13px;font-weight:600;opacity:.7}.td .td-fs .rd-balken{width:100%;margin:0}' +
    '.td .rd-kopf{margin-bottom:18px}' +
    '.td .td-unter{font-size:14px;opacity:.75;margin:14px 0 0;text-align:center}' +
    '@media (max-width:520px){.td.td-weit .rd-form{padding:22px 16px 22px}.td .rd-wahl.td-drei{gap:8px}.td .rd-wahl.td-drei button{min-height:104px;padding:18px 6px 14px;gap:8px;border-radius:16px}.td .rd-wahl.td-drei button>span{font-size:15px;line-height:1.2}.td .rd-wahl.td-drei button small{display:none}.td .td-kick-rest{display:none}.td .rd-wahl.td-drei .td-ic{width:26px;height:26px}}' +
    '.td.td-breit{width:min(860px,calc(100vw - 32px))}' +
    '.td .td-cal{height:min(700px,calc(100dvh - 230px));min-height:480px;margin:0 -8px;position:relative}' +
    '.td .td-cal .td-laedt{position:absolute;inset:0;display:grid;place-items:center;font-weight:600;opacity:.6}' +
    '.td .td-alt{font-size:14px;margin:10px 0 0;opacity:.8}' +
    '.td .td-danke{text-align:center;padding:12px 0 4px}.td .td-danke p{opacity:.8;margin:8px auto 18px;max-width:420px}' +
    '.td .td-ok{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;margin:0 auto 14px;background:rgba(61,220,132,.16);color:#1F7A4D}.td .td-ok .td-ic{width:30px;height:30px}' +
    '.td .td-zurueck{margin-top:12px;min-height:44px;font:inherit;font-weight:600;background:none;border:0;cursor:pointer;opacity:.7}' +
    '@media (max-width:480px){.td .td-cal{margin:0 -12px;min-height:520px;height:calc(100dvh - 190px)}}' +
    '@media (max-width:1099px) and (min-width:901px){.nav-termin .nt-lang{display:none}}' +
    'a.nav-cta.nav-termin{border-color:var(--ink,#0b1424)}' +
    '@media (max-width:1099px) and (min-width:901px){.nav-termin svg{display:none}a.nav-termin.nav-termin{padding-left:14px;padding-right:14px}}' +
    '@media (max-width:1023px) and (min-width:901px){a.nav-termin.nav-termin{font-size:14px;padding-left:12px;padding-right:12px}}' +
    '@media (max-width:900px){.nav-termin svg{display:none}.nav-termin .nt-text{font-size:min(16px,3.9vw);white-space:nowrap}a.nav-cta.nav-termin{padding-left:14px;padding-right:14px}}' +
    '.wx-cta-karte .wx-cta-knoepfe{flex-direction:column;align-items:stretch}.wx-cta-karte .wx-cta-knoepfe .btn{justify-content:center}' +
    '@media (max-width:480px){.wx-cta-karte .btn[data-termin] svg,.kontakt-termin svg,.uk-termin svg{display:none}.wx-cta-karte .btn[data-termin],.kontakt-termin,.uk-termin{padding-left:10px;padding-right:10px;white-space:normal;text-align:center;line-height:1.25;font-size:14px}}' +
    '@media (max-width:480px){.hero-cta .btn[href*="potenzial-erstgespraech"]{font-size:15px;padding-left:16px;padding-right:16px;white-space:nowrap}.hero-cta .btn[href*="potenzial-erstgespraech"] svg{display:none}}' +
    '.uk-termin,.kontakt-termin{width:100%;justify-content:center;gap:10px;margin-top:12px}.uk-termin svg,.kontakt-termin svg{width:20px;height:20px}';
  (function () { var st = document.createElement('style'); st.textContent = CSS; (document.head || document.documentElement).appendChild(st); })();

  var dlg, form, schritte, balken, zurueck, stand = { schritt: 1, themen: [], tok: null, cal: false };

  function bauen() {
    dlg = document.createElement('dialog');
    dlg.className = 'rd td td-weit'; dlg.id = 'termin-dialog'; dlg.setAttribute('aria-labelledby', 'td-titel');
    var wahl = THEMEN.map(function (t) {
      return '<button type="button" data-thema="' + t[0] + '" aria-pressed="false">' + svg(t[3] || t[0]) + '<span>' + esc(t[1]) + '<small>' + esc(t[2]) + '</small></span></button>';
    }).join('');
    dlg.innerHTML = '<form class="rd-form" novalidate>' +
      '<input type="text" name="bot" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0">' +
      '<div class="rd-kopf"><p class="rd-kick" id="td-titel">' + svg('kalender') + '<span>Kostenloses Beratungsgespräch<span class="td-kick-rest"> · 30 Min.</span></span></p><button type="button" class="rd-zu" data-zu aria-label="Schließen">' + svg('zu') + '</button></div>' +
      '<section class="rd-schritt an" data-schritt="1"><h3>Worum soll es gehen?</h3><div class="rd-wahl td-drei">' + wahl + '</div>' +
      '<p class="td-unter">Es geht um SEO, Google-Anzeigen oder ein Foto- und Videoshooting? Das läuft alles unter Website.</p></section>' +
      '<section class="rd-schritt" data-schritt="2" hidden><h3>Wer bist du?</h3><p class="td-satz" data-passt></p>' +
      '<div class="td-zeile2"><label class="rd-feld"><span>Dein Name</span><input name="name" autocomplete="name" placeholder="Vor- und Nachname" required></label>' +
      '<label class="rd-feld"><span>Betrieb</span><input name="betrieb" autocomplete="organization" placeholder="' + (SEITE === 'shk' ? 'z. B. Müller Haustechnik GmbH' : 'z. B. Müller Holzbau GmbH') + '" required></label></div>' +
      '<p class="td-fehler" data-fehler="2" hidden></p>' +
      '<button type="button" class="' + KNOPF + ' td-knopf" data-weiter="2">Weiter ' + svg('pfeil') + '</button></section>' +
      '<section class="rd-schritt" data-schritt="3" hidden><h3>Wohin schicken wir die Terminbestätigung?</h3>' +
      '<label class="rd-feld"><span>E-Mail</span><input name="email" type="email" autocomplete="email" inputmode="email" placeholder="name@betrieb.de" required></label>' +
      '<p class="td-mail">' + svg('schloss') + '<span>Die Mail brauchen wir nur für die Terminbestätigung und den Link zum Gespräch. Kein Newsletter, keine Werbung.</span></p>' +
      '<p class="td-fehler" data-fehler="3" hidden></p>' +
      '<button type="submit" class="' + KNOPF + ' td-knopf" data-weiter="3">Weiter zum Kalender ' + svg('pfeil') + '</button>' +
      '<p class="td-hinweis">Der Kalender kommt von Calendly. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p></section>' +
      '<section class="rd-schritt" data-schritt="4" hidden><h3>Such dir einen Termin aus.</h3><div class="td-cal"><div class="td-laedt">Kalender lädt …</div></div>' +
      '<p class="td-alt" data-alt>Kein passender Termin dabei? Ruf an: <a href="tel:+4981947174990">+49 8194 7174990</a></p></section>' +
      '<section class="rd-schritt" data-schritt="5" hidden><div class="td-danke"><span class="td-ok">' + svg('ok') + '</span><h3>Dein Termin steht.</h3>' +
      '<p>Die Bestätigung mit dem Link zum Gespräch kommt gleich per Mail. Wir schauen uns deinen Betrieb vorher an.</p>' +
      '<button type="button" class="' + KNOPF + '" data-zu>Schließen</button></div></section>' +
      '<div class="td-fuss"><button type="button" class="td-zurueck" data-zurueck hidden>← Zurück</button>' +
      '<div class="td-fs" aria-hidden="true"><span data-fs-text>Schritt 1 von 3</span><div class="rd-balken"><i></i></div></div></div>' +
      '</form>';
    document.body.appendChild(dlg);
    form = dlg.querySelector('form');
    schritte = dlg.querySelectorAll('.rd-schritt');
    balken = dlg.querySelector('.rd-balken i');
    zurueck = dlg.querySelector('[data-zurueck]');

    dlg.addEventListener('click', function (e) {
      if (e.target === dlg) return schliessen();
      var b = e.target.closest('button'); if (!b) return;
      if (b.hasAttribute('data-zu')) return schliessen();
      if (b.hasAttribute('data-zurueck')) return zeigen(Math.max(1, stand.schritt - 1));
      if (b.dataset.thema) {
        // Klick auf die Kachel = Auswahl UND weiter (Noah, 11.11.2026: „Der Klick auf die Kachel heißt gleichzeitig ‚Weiter‘")
        [].forEach.call(dlg.querySelectorAll('[data-thema]'), function (x) { var an = x === b; x.classList.toggle('an', an); x.setAttribute('aria-pressed', an ? 'true' : 'false'); });
        stand.themen = [b.dataset.thema];
        setTimeout(function () { zeigen(2); var n = form.elements.name; if (n && !n.value) n.focus(); }, 180);
        return;
      }
      if (b.dataset.weiter === '2') return weiterZuMail();
    });
    form.addEventListener('keydown', function (e) { if (e.key === 'Enter' && stand.schritt === 2) { e.preventDefault(); weiterZuMail(); } });
    form.addEventListener('submit', function (e) { e.preventDefault(); if (stand.schritt === 3) absenden(); });
    form.addEventListener('input', function (e) { if (e.target.classList) e.target.classList.remove('fehlt'); if (!dlg.querySelector('.fehlt')) [].forEach.call(dlg.querySelectorAll('.td-fehler'), function (f) { f.hidden = true; }); });
    dlg.addEventListener('close', function () { document.documentElement.classList.remove('rd-offen'); });
    window.addEventListener('message', function (e) {
      if (!/^https:\/\/([a-z0-9-]+\.)?calendly\.com$/.test(e.origin) || !e.data || e.data.event !== 'calendly.event_scheduled') return;
      var uri = (e.data.payload && e.data.payload.event && e.data.payload.event.uri) || '';
      if (stand.tok) senden({ schritt: 'gebucht', tok: stand.tok, event_uri: uri });
      melden('termin_gebucht');
      zeigen(5);
    });
  }

  var FS = ['', 'Schritt 1 von 3', 'Schritt 2 von 3', 'Fast geschafft', 'Nur noch den Termin wählen', ''];
  function zeigen(n) {
    stand.schritt = n;
    [].forEach.call(schritte, function (s) { var an = +s.dataset.schritt === n; s.hidden = !an; s.classList.toggle('an', an); });
    balken.style.transform = 'scaleX(' + Math.min(1, n / 4) + ')';
    dlg.querySelector('[data-fs-text]').textContent = FS[n] || '';
    dlg.querySelector('.td-fs').hidden = n === 5;
    zurueck.hidden = !(n >= 2 && n <= 4);
    dlg.classList.toggle('td-breit', n === 4);
    if (n === 2) { var t = stand.themen[0]; dlg.querySelector('[data-passt]').textContent = PASST[t] || ''; }
    if (n === 4) kalender();
  }
  var PASST = {
    kunden: 'Wir schauen uns vorher an, wie viele Anfragen in deinem Umkreis drin sind.',
    mitarbeiter: 'Wir schauen uns vorher an, wie viele passende Leute es in deiner Region gibt.',
    website: 'Wir schauen uns vorher deine jetzige Seite und deinen Google-Auftritt an.'
  };

  function oeffnen(thema) {
    if (!dlg) bauen();
    if (stand.schritt === 5) { stand = { schritt: 1, themen: [], tok: null, cal: false }; form.reset(); dlg.querySelector('.td-cal').innerHTML = '<div class="td-laedt">Kalender lädt …</div>'; }
    [].forEach.call(dlg.querySelectorAll('[data-thema]'), function (b) { var an = !!thema && b.dataset.thema === thema; b.classList.toggle('an', an); b.setAttribute('aria-pressed', an ? 'true' : 'false'); });
    if (thema) { stand.themen = [thema]; zeigen(2); }          // Thema schon über die Kachel auf der Seite gewählt → gleich Name/Betrieb
    else zeigen(stand.schritt === 4 && stand.cal ? 4 : 1);
    document.documentElement.classList.add('rd-offen');
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    melden('termin_dialog_auf');
  }
  function schliessen() { if (dlg.open) dlg.close(); else dlg.removeAttribute('open'); }

  function wert(n) { return (form.elements[n] && form.elements[n].value || '').trim(); }
  function pruefe(felder, nr) {
    var f = dlg.querySelector('[data-fehler="' + nr + '"]'), fehl = '';
    felder.forEach(function (p) { form.elements[p[0]].classList.remove('fehlt'); });
    felder.forEach(function (p) { if (!p[1]) { form.elements[p[0]].classList.add('fehlt'); if (!fehl) { fehl = p[2]; form.elements[p[0]].focus(); } } });
    if (fehl) { f.textContent = fehl; f.hidden = false; return false; }
    f.hidden = true; return true;
  }
  function weiterZuMail() {
    if (!pruefe([['name', wert('name').length >= 2, 'Bitte deinen Namen eintragen.'],
      ['betrieb', wert('betrieb').length >= 2, 'Bitte den Namen deines Betriebs eintragen.']], 2)) return;
    zeigen(3); var m = form.elements.email; if (m && !m.value) m.focus();
  }
  function absenden() {
    if (!pruefe([['email', /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(wert('email')), 'Bitte eine gültige E-Mail-Adresse eintragen.']], 3)) return;
    var knopf = dlg.querySelector('[data-weiter="3"]'); knopf.disabled = true;
    stand.cal = false;
    senden({ schritt: 'kontakt', seite: SEITE, themen: stand.themen, name: wert('name'), betrieb: wert('betrieb'), email: wert('email'), pfad: location.pathname, bot: wert('bot') })
      .then(function (r) { if (r && r.tok) stand.tok = r.tok; })
      .then(function () { knopf.disabled = false; melden('termin_kontakt'); zeigen(4); });
  }
  function senden(body) {
    // Ein Ausfall von Worker/Close darf die Buchung nie blockieren: nach 6 s geht es ohne Antwort weiter.
    var zeit = new Promise(function (ok) { setTimeout(function () { ok(null); }, 6000); });
    var anfrage = fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), keepalive: true })
      .then(function (r) { return r.json(); }).catch(function () { return null; });
    return Promise.race([anfrage, zeit]);
  }

  function themenText() {
    return stand.themen.map(function (k) { for (var i = 0; i < THEMEN.length; i++) if (THEMEN[i][0] === k) return THEMEN[i][1]; return k; }).join(', ');
  }
  function calUrl(einbetten) {
    var a1 = 'Worum es geht: ' + themenText() + '\nBetrieb: ' + wert('betrieb') + '\nGebucht über ' + location.hostname + location.pathname;
    var q = { name: wert('name'), email: wert('email'), a1: a1, hide_gdpr_banner: '1', hide_event_type_details: '1', hide_landing_page_details: '1', utm_source: SEITE === 'shk' ? 'website-shk' : 'website-hwm', utm_medium: 'termin-dialog', utm_content: stand.themen.join('-') };
    if (einbetten) { q.embed_domain = location.hostname; q.embed_type = 'Inline'; }
    return CAL + '?' + Object.keys(q).map(function (k) { return k + '=' + encodeURIComponent(q[k]); }).join('&');
  }
  function kalender() {
    if (stand.cal) return; stand.cal = true;
    var box = dlg.querySelector('.td-cal');
    box.innerHTML = '<div class="td-laedt">Kalender lädt …</div>';
    var ifr = document.createElement('iframe');
    ifr.src = calUrl(true); ifr.title = 'Termin auswählen'; ifr.loading = 'eager';
    ifr.setAttribute('frameborder', '0'); ifr.style.cssText = 'width:100%;height:100%;border:0;position:relative;z-index:1;background:transparent';
    ifr.addEventListener('load', function () { var l = box.querySelector('.td-laedt'); if (l) l.remove(); });
    box.appendChild(ifr);
    dlg.querySelector('[data-alt]').innerHTML = 'Kein passender Termin dabei? Ruf an: <a href="tel:+4981947174990">+49 8194 7174990</a> · <a href="' + esc(calUrl(false)) + '" target="_blank" rel="noopener">Kalender im neuen Tab</a>';
  }

  function melden(was) { try { if (window.hwmMessung && hwmMessung.ereignis) hwmMessung.ereignis(was); } catch (e) { /* Messung ist Zubehör */ } }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var el = e.target.closest('[data-termin], a[href*="calendly.com/noahseelau/"]');
    if (!el || el.closest('.rd') || el.hasAttribute('data-termin-aus')) return;
    var thema = '';
    if (el.hasAttribute('data-termin')) thema = el.getAttribute('data-termin') || '';
    else {
      var m = (el.getAttribute('href') || '').match(/calendly\.com\/noahseelau\/([a-z0-9-]+)/);
      if (!m || !(m[1] in SLUG_THEMA)) return;
      thema = SLUG_THEMA[m[1]];
    }
    e.preventDefault();
    oeffnen(thema);
  });
  window.hwmTermin = { oeffnen: oeffnen };
  if (/[#&]termin\b/.test(location.hash)) oeffnen('');
})();
