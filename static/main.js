/* HandwerksManufaktur — Konzept „Der Aufbau" · /static/main.js */
(() => {
'use strict';
document.documentElement.classList.remove('kein-js');
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
const istMobil = () => innerWidth < 1000;

/* ---- Kopf ---- */
const kopf = $('.kopf');
const dunklerStart = !!$('.hero-bahn, .hero-klein');
function kopfStand() {
  if (!kopf) return;
  const y = scrollY;
  const grenze = dunklerStart ? 40 : 8;
  kopf.classList.toggle('fest', y > grenze);
}
if (kopf && !dunklerStart) kopf.classList.add('hell');
kopfStand();

/* ---- Mobilmenü ---- */
const burger = $('.burger'), menu = $('#mobilmenu');
function menuZu() { if (!menu) return; menu.classList.remove('offen'); document.body.classList.remove('menu-offen'); burger && burger.setAttribute('aria-expanded', 'false'); }
function menuAuf() { if (!menu) return; menu.classList.add('offen'); document.body.classList.add('menu-offen'); burger && burger.setAttribute('aria-expanded', 'true'); }
burger && burger.addEventListener('click', () => menu.classList.contains('offen') ? menuZu() : menuAuf());
addEventListener('keydown', e => { if (e.key === 'Escape') { menuZu(); $$('.hat-menu > a').forEach(a => a.blur()); } });
addEventListener('resize', () => { if (!istMobil()) menuZu(); });

/* ---- Intro: das Signet baut sich auf (einmal je Sitzung) ---- */
const intro = $('#intro');
if (intro) {
  let gesehen = false;
  try { gesehen = sessionStorage.getItem('hm-intro') === '1'; } catch (e) {}
  if (gesehen || ruhig) intro.remove();
  else {
    requestAnimationFrame(() => intro.classList.add('los'));
    // Runde 9: Linie, drei Balken (zack, zack, zack), Schriftzug. Steht bei 1,8 s, dann weg.
    setTimeout(() => { intro.classList.add('verschwindet'); try { sessionStorage.setItem('hm-intro', '1'); } catch (e) {} }, 1550); // Runde 18: kürzer (LCP mobil 3,9 s lag am Intro)
    setTimeout(() => intro.remove(), 2150);
  }
}

/* ---- Hero: drei Säulen werden eine Fläche ---- */
const bahn = $('.hero-bahn'), hero = $('.hero');
let bahnHoehe = 0;
function heroScrub() {
  if (!bahn || !hero) return;
  // 🔴 27.09.2026 (Noah: „wenn sie durchscrollt, hängt es ein bisschen sehr"): unterhalb der Bahn
  //    ändert sich nichts mehr — dort wird nicht mehr in jedem Frame an drei Video-Clip-Paths gedreht.
  if (!bahnHoehe) bahnHoehe = bahn.offsetHeight;
  if (scrollY > bahnHoehe) return;
  const weg = bahnHoehe - innerHeight;
  const p = weg > 0 ? Math.min(1, Math.max(0, scrollY / (weg * 0.82))) : 1;
  hero.style.setProperty('--p', p.toFixed(3));
}

/* ---- Pause-Knopf für laufende Videos ---- */
$$('.pause').forEach(k => {
  k.addEventListener('click', () => {
    const vids = $$('video', k.closest('.hero, .hero-klein') || document);
    const aus = k.classList.toggle('aus');
    vids.forEach(v => aus ? v.pause() : v.play().catch(() => {}));
    k.setAttribute('aria-label', aus ? 'Video abspielen' : 'Video anhalten');
  });
});

/* ---- Reveal (erst einhängen, wenn es in die Nähe kommt) ---- */
const io = new IntersectionObserver(es => {
  es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('dran');
    $$('.nr[data-zahl]', e.target).forEach(zaehlen);
    if (e.target.matches('.nr[data-zahl]')) zaehlen(e.target);
    io.unobserve(e.target);
  });
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
$$('.reveal:not(.auf), .fall, .zahlenreihe, .balken, .system-saeulen, .zelle').forEach(el => io.observe(el));
// 🔴 Ein Element mit flächenlosem clip-path meldet dem IntersectionObserver in Chromium Ratio 0 — nie
//    „dran". Deshalb wird für .reveal.auf der ELTERNBLOCK beobachtet und das Kind freigegeben.
const ioAuf = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; $$('.reveal.auf', e.target).forEach(k => k.classList.add('dran')); ioAuf.unobserve(e.target); }), { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
$$('.reveal.auf').forEach(el => ioAuf.observe(el.parentElement));
setTimeout(() => $$('.reveal:not(.dran)').forEach(el => { const r = el.getBoundingClientRect(); if (r.top < innerHeight) el.classList.add('dran'); }), 1800);

/* ---- Zähler ---- */
function zaehlen(el) {
  if (el.dataset.fertig) return; el.dataset.fertig = '1';
  const ziel = parseFloat(el.dataset.zahl), vor = el.dataset.vor || '', nach = el.dataset.nach || '';
  const dez = (String(el.dataset.zahl).split('.')[1] || '').length;
  const fmt = n => vor + n.toLocaleString('de-DE', { minimumFractionDigits: dez, maximumFractionDigits: dez }) + nach;
  if (ruhig) { el.textContent = fmt(ziel); return; }
  const t0 = performance.now(), dauer = 1300;
  const tick = t => {
    const k = Math.min(1, (t - t0) / dauer), e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmt(ziel * e);
    if (k < 1) requestAnimationFrame(tick); else el.textContent = fmt(ziel);
  };
  requestAnimationFrame(tick);
}

/* ---- Der Aufbau: sechs Säulen wachsen mit dem Weg des Blocks durchs Fenster ---- */
const aufbau = $('.aufbau'), skyline = $('.skyline');
function aufbauScrub() {
  if (!aufbau || !skyline) return;
  const r = skyline.getBoundingClientRect(), h = innerHeight;
  const p = Math.min(1, Math.max(0, (h * 0.92 - r.top) / (h * 0.72)));
  aufbau.style.setProperty('--p', p.toFixed(3));
}

/* ---- Statement: wortweise Füllung, gemessen am Textelement ---- */
const statement = $('.statement'), statementH2 = statement && $('h2', statement);
let statementWorte = [];
function worteTeilen(knoten) {
  [...knoten.childNodes].forEach(n => {
    if (n.nodeType === 3) {
      if (!n.textContent.trim()) return;
      const frag = document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach(t => {
        if (!t) return;
        if (/^\s+$/.test(t)) frag.appendChild(document.createTextNode(t));
        else { const i = document.createElement('i'); i.className = 'w'; i.textContent = t; frag.appendChild(i); }
      });
      n.replaceWith(frag);
    } else if (n.nodeType === 1 && n.tagName !== 'I' && n.tagName !== 'SVG') worteTeilen(n);
  });
}
function statementScrub() {
  if (!statementH2 || !statementWorte.length) return;
  const h = innerHeight, r = statementH2.getBoundingClientRect();
  const p = Math.min(1, Math.max(0, (h * 0.78 - r.top) / (h * 0.46)));
  statement.style.setProperty('--p', p.toFixed(3));
  const n = statementWorte.length;
  statementWorte.forEach((w, i) => w.classList.toggle('an', (i + 1) / n <= p + 0.02));
}
if (statementH2) { statementH2.setAttribute('data-fuell', ''); worteTeilen(statementH2); statementWorte = $$('i', statementH2); }

/* ---- Vorher/Nachher-Wischer ---- */
const wischer = $('.wischer');
if (wischer) {
  const vor = $('.vorher img', wischer), nach = $('.nachher img', wischer);
  const setX = x => wischer.style.setProperty('--x', Math.min(96, Math.max(4, x)).toFixed(1));
  let greift = false;
  const ausEvent = e => ((e.clientX - wischer.getBoundingClientRect().left) / wischer.offsetWidth) * 100;
  wischer.addEventListener('pointerdown', e => { greift = true; wischer.classList.add('greift'); wischer.setPointerCapture(e.pointerId); setX(ausEvent(e)); });
  wischer.addEventListener('pointermove', e => { if (greift) setX(ausEvent(e)); });
  const los = () => { greift = false; wischer.classList.remove('greift'); };
  wischer.addEventListener('pointerup', los); wischer.addEventListener('pointercancel', los);
  wischer.addEventListener('keydown', e => { const x = parseFloat(getComputedStyle(wischer).getPropertyValue('--x')) || 50; if (e.key === 'ArrowLeft') setX(x - 4); if (e.key === 'ArrowRight') setX(x + 4); });
  // Hover scrollt durch die Seite (beide Seiten gleich weit, bezogen auf die eigene Bildhöhe)
  function rollen(an) {
    [vor, nach].forEach(img => {
      const box = img.closest('.seite'); if (!img.naturalHeight) return;
      const skala = box.clientWidth / img.naturalWidth; // vorher-Bild ist auf volle Breite gerechnet
      const breite = img.classList.contains('v') ? wischer.clientWidth : box.clientWidth;
      const bildH = img.naturalHeight * (breite / img.naturalWidth);
      const weg = Math.max(0, bildH - wischer.clientHeight);
      img.style.setProperty('--sy', an ? weg.toFixed(0) : '0');
      img.style.transitionDuration = an ? Math.max(4, weg / 140).toFixed(1) + 's' : '.9s';
    });
  }
  wischer.addEventListener('pointerenter', () => rollen(true));
  wischer.addEventListener('pointerleave', () => rollen(false));
  // Projektwahl
  const knoepfe = $$('.projektwahl button');
  const titel = $('.wischer .titel');
  knoepfe.forEach(b => b.addEventListener('click', () => {
    knoepfe.forEach(k => k.classList.remove('aktiv')); b.classList.add('aktiv');
    const d = b.dataset;
    vor.src = d.vorher; nach.src = d.nachher; vor.alt = d.name + ' — alte Website'; nach.alt = d.name + ' — neue Website';
    vor.style.setProperty('--sy', '0'); nach.style.setProperty('--sy', '0');
    if (titel) { $('b', titel).textContent = d.name; $('small', titel).textContent = d.gewerk; const a = $('a', titel); if (a) { if (d.live) { a.href = d.live; a.hidden = false; } else a.hidden = true; } }
    setX(50);
  }));
}

/* ---- Frag Google selbst: Suchbegriff tippt sich, Treffer erscheinen ---- */
const suche = $('.suche');
if (suche) {
  const daten = JSON.parse(suche.dataset.treffer || '[]');
  const tipp = $('.tipp', suche), liste = $('.treffer', suche), chips = $$('.begriffe button', suche);
  let i = 0, timer = null, tippTimer = null;
  function zeige(k, vonHand) {
    i = k; chips.forEach((c, j) => c.classList.toggle('aktiv', j === k));
    const d = daten[k]; if (!d) return;
    clearTimeout(tippTimer); liste.innerHTML = ''; tipp.textContent = '';
    let z = 0;
    const tippen = () => {
      tipp.textContent = d.begriff.slice(0, ++z);
      if (z < d.begriff.length) tippTimer = setTimeout(tippen, ruhig ? 0 : 55);
      else setTimeout(() => {
        d.treffer.forEach((t, n) => {
          const el = document.createElement('div'); el.className = 't' + (n === 0 ? ' top' : '');
          el.innerHTML = `<span class="platz">${t.platz}</span><div><b>${t.titel}</b>${t.domain ? `<small>${t.domain}</small>` : ""}</div>` + (t.logo ? `<span class="t-logo${t.hell ? ' dunkel' : ''}"><img src="${t.logo}" alt=""></span>` : '<span></span>');
          liste.appendChild(el); setTimeout(() => el.classList.add('da'), 60 + n * 140);
        });
      }, 350);
    };
    tippen();
    clearTimeout(timer);
    if (!vonHand && !ruhig) timer = setTimeout(() => zeige((i + 1) % daten.length, false), 5200);
  }
  chips.forEach((c, k) => c.addEventListener('click', () => zeige(k, true)));
  const ioS = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { zeige(0, false); ioS.disconnect(); } }, { threshold: 0.3 });
  ioS.observe(suche);
}

/* ---- Videos nur abspielen, wenn sie im Bild sind ---- */
const ioV = new IntersectionObserver(es => es.forEach(e => {
  const v = e.target;
  if (e.isIntersecting) { if (!v.getAttribute('src') && v.dataset.src) v.src = (innerWidth < 760 && v.dataset.srcMobil) || v.dataset.src; v.play().catch(() => {}); }
  else v.pause();
}), { rootMargin: '120px 0px' });
/* 🔴 JEDES Video, nicht nur die mit data-lazy. Noah, 26.09.2026: "auf einmal läuft das video
   senftleben direkt? hä" — die Fallstudie auf der Startseite lief beim Laden los, während man
   noch im Hero stand, und 16 Referenz-Aufnahmen liefen daneben mit. autoplay bleibt als Rückfall
   ohne JS; im Browser entscheidet allein, ob das Video im Bild ist. */
$$('video').forEach(v => { if (v.dataset.hand !== undefined) return; if (!v.closest('.hero')) { try { v.pause(); } catch (e) {} } ioV.observe(v); });
$$('.ton').forEach(k => k.addEventListener('click', () => {
  const v = $('video', k.parentElement); if (!v) return;
  v.muted = !v.muted; k.classList.toggle('an', !v.muted);
  k.setAttribute('aria-label', v.muted ? 'Ton einschalten' : 'Ton ausschalten');
}));

/* ---- Formular (Attrappe) ---- */
$$('.formular').forEach(f => f.addEventListener('submit', e => { e.preventDefault(); const b = $('.btn', f); if (b) { b.textContent = 'Danke, wir melden uns.'; b.classList.add('btn-tinte'); } }));

/* ---- Bauzeitplan: Fortschritt aus dem Weg der Tafel durchs Fenster ---- */
const bauplan = $('.bauplan'), tafel = $('.plan-tafel');
function bauplanScrub() {
  if (!bauplan || !tafel) return;
  const r = tafel.getBoundingClientRect(), h = innerHeight;
  const p = Math.min(1, Math.max(0, (h * 0.9 - r.top) / (h * 0.75)));
  bauplan.style.setProperty('--p', p.toFixed(3));
}

/* ---- Postfach-Feed: Einträge laufen nacheinander ein (Ankunft löst Eintrag aus) ---- */
$$('.postfach').forEach(pf => {
  const li = $$('.pf-liste li', pf), z = $('.pf-zaehler', pf), leer = $('.pf-leer', pf);
  li.forEach(l => { const d = l.dataset; const ini = d.ort.slice(0, 2).toUpperCase();
    l.innerHTML = `<span class="av">${ini}</span><span><b>${d.was}</b><small>Aus ${d.ort} · gerade eben</small><span class="chips"><span>${d.a}</span><span>${d.b}</span></span></span>`; });
  let i = 0, laeuft = false;
  function naechster() {
    if (i >= li.length) { i = 0; li.forEach(l => l.classList.remove('da', 'neu')); if (leer) leer.hidden = false; setTimeout(naechster, ruhig ? 0 : 1800); return; }
    const l = li[i]; if (leer) leer.hidden = true;
    pf.querySelector('.pf-liste').prepend(l); l.classList.add('da', 'neu'); li.forEach(o => { if (o !== l) o.classList.remove('neu'); });
    i++; if (z) z.textContent = i + ' neu';
    setTimeout(naechster, ruhig ? 0 : 2600);
  }
  const ioP = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting) && !laeuft) { laeuft = true; naechster(); ioP.disconnect(); } }, { threshold: 0.3 });
  if (ruhig) { li.forEach(l => l.classList.add('da')); if (z) z.textContent = li.length + ' neu'; if (leer) leer.hidden = true; } else ioP.observe(pf);
});

/* ---- Ein Scroll-Lauf für alles ---- */
let geplant = false, netzZuletzt = 0;
function netz() {
  // Sicherheitsnetz: was im Bild steht und trotzdem nicht freigegeben wurde, wird freigegeben.
  // 🔴 Nur alle 500 ms — vorher lief in JEDEM Scroll-Frame ein querySelectorAll plus ein
  //    getBoundingClientRect je Element (erzwungenes Layout, sichtbares Ruckeln, 27.09.2026).
  const t = performance.now(); if (t - netzZuletzt < 500) return; netzZuletzt = t;
  $$('.reveal:not(.dran)').forEach(el => { const r = el.getBoundingClientRect(); if (r.top < innerHeight * 0.92 && r.bottom > 0) el.classList.add('dran'); });
}
function alles() { geplant = false; kopfStand(); heroScrub(); aufbauScrub(); statementScrub(); bauplanScrub(); netz(); }
addEventListener('scroll', () => { if (!geplant) { geplant = true; requestAnimationFrame(alles); } }, { passive: true });
addEventListener('resize', () => { bahnHoehe = 0; alles(); });
alles();
/* ---- Hero-Säulen, die durch mehrere Betriebe blenden (Über uns, Kontakt) ---- */
$$('.hero-klein .wechsel').forEach((saeule, nr) => {
  const bilder = $$('img', saeule);
  if (bilder.length < 2) return;
  let i = 0;
  const weiter = () => {
    // Runde 15: nie derselbe Betrieb in zwei Säulen zugleich (data-g)
    const belegt = new Set($$('.hero-klein .wechsel img.an').filter(b => !saeule.contains(b)).map(b => b.dataset.g));
    let n = i;
    for (let s = 1; s <= bilder.length; s++) { const k = (i + s) % bilder.length; if (!belegt.has(bilder[k].dataset.g)) { n = k; break; } }
    if (n === i) return;
    bilder[i].classList.remove('an'); i = n; bilder[i].classList.add('an');
  };
  // versetzt starten, damit die drei Säulen nie gleichzeitig wechseln
  setTimeout(() => { weiter(); setInterval(weiter, 5200); }, 1600 * nr + 2200);
});

/* ---- Kalender: die Tage füllen sich am SCROLL-Fortschritt, nicht auf einen Schlag ---- */
/*  Noah, 23.09.2026: „ich will, dass wenn man dann durchscrollt, es sich dann füllen soll."  */
$$('[data-kalender]').forEach(tafel => {
  const treffer = $$('.kal-raster i.an', tafel);
  const zahl = $('.kal-nr', tafel);
  if (!treffer.length || !zahl) return;
  let letzte = -1;
  const mal = () => {
    const r = tafel.getBoundingClientRect(), h = window.innerHeight;
    // 0 sobald die Tafel unten ins Bild kommt, 1 wenn ihre Mitte die Bildmitte passiert hat
    const p = Math.max(0, Math.min(1, (h * 0.92 - r.top) / (h * 0.52 + r.height * 0.5)));
    const k = Math.round(p * treffer.length);
    if (k === letzte) return;
    letzte = k;
    treffer.forEach((el, n) => el.classList.toggle('voll', n < k));
    zahl.textContent = k;
  };
  const los = () => { mal(); };
  addEventListener('scroll', los, { passive: true });
  addEventListener('resize', los);
  mal();
});


/* ---- Problem-Leiter: die Wege werden nacheinander durchgestrichen (Prinzip SHK v3, gelobt 25.09.) ---- */
$$('.wege-raster').forEach(r => {
  const wege = $$('.weg', r), ende = r.nextElementSibling && r.nextElementSibling.classList.contains('wege-ende') ? r.nextElementSibling : null;
  const los = () => { wege.forEach((w, i) => setTimeout(() => w.classList.add('gestempelt'), ruhig ? 0 : 350 + i * 420)); if (ende) setTimeout(() => ende.classList.add('fertig'), ruhig ? 0 : 350 + wege.length * 420 + 200); };
  const ioW = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { los(); ioW.disconnect(); } }, { threshold: 0.35 });
  ioW.observe(r);
});

/* ---- Ergebnis-Karten: Video startet erst auf Klick, mit Ton und Regler.
   🔴 Noah, 27.09.: "Da läuft immer noch automatisch das Video, obwohl ich das nicht wollte." ---- */
$$('.erg .play').forEach(k => k.addEventListener('click', () => {
  const karte = k.closest('.erg'), v = $('video', karte); if (!v) return;
  $$('.erg.laeuft video').forEach(o => { if (o !== v) { o.pause(); o.closest('.erg').classList.remove('laeuft'); } });
  karte.classList.add('laeuft'); v.controls = true; v.muted = false; v.play().catch(() => {});
}));


/* ---- Referenz-Kacheln: Drüberfahren scrollt die Kundenseite sanft runter ----
   🔴 Noah, 27.09.2026: „Wenn jemand dann mit der Maus drüberfährt, soll die Seite etwas smooth
   runterscrollen, aber es reicht, wenn der Home Screen lädt". Im Ruhezustand läuft die Hero-
   Schleife (Video). Erst beim ersten Drüberfahren lädt das Seitenbild (~150 KB), blendet über den
   Hero und fährt mit fester Geschwindigkeit nach unten; beim Verlassen fährt es zurück und die
   Schleife ist wieder zu sehen. Nur Maus — auf dem Handy bleibt es beim laufenden Hero. */
// 🔴 Runde 9 (27.09.2026): „sollte sie relativ gleich anfangen zu scrollen … nicht erst dann lange brauchen"
//    → keine Verzögerung, Anlauf ohne Kriechphase, etwas schneller; Seitenbilder liegen schon bereit (unten).
const TEMPO = 95; // Pixel je Sekunde in Anzeigegröße
$$('.schirm, .lb-schirm').forEach(schirm => {
  const bild = $('.seite-bild', schirm); if (!bild) return;
  const karte = schirm.closest('.projekt, .lb-k') || schirm;
  let lauf = null, drin = false;
  const stand = () => { const m = new DOMMatrix(getComputedStyle(bild).transform); return m.m42 || 0; };
  const runter = () => {
    if (!drin || !bild.complete || !bild.naturalHeight) return;
    const weg = bild.offsetHeight - schirm.clientHeight; if (weg <= 8) return;
    const von = stand(); lauf && lauf.cancel();
    schirm.classList.add('scrollt');
    lauf = bild.animate([{ transform: `translateY(${von}px)` }, { transform: `translateY(${-weg}px)` }],
      { duration: Math.max(1200, ((weg + von) / TEMPO) * 1000), delay: 0, easing: 'cubic-bezier(.25,.1,.25,1)', fill: 'forwards' });
  };
  karte.addEventListener('pointerenter', e => {
    if (e.pointerType !== 'mouse' || ruhig) return;
    drin = true;
    if (!bild.getAttribute('src')) { bild.src = bild.dataset.src; bild.addEventListener('load', runter, { once: true }); }
    else runter();
  });
  karte.addEventListener('pointerleave', () => {
    drin = false; if (!lauf) return;
    const von = stand(); lauf.cancel();
    schirm.classList.remove('scrollt');
    lauf = bild.animate([{ transform: `translateY(${von}px)` }, { transform: 'translateY(0)' }],
      { duration: 400, easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'forwards' });
  });
});

/* Seitenbilder vorladen, sobald eine Kachel nahe am Bild ist — nur mit Maus (auf dem Handy gibt es kein
   Drüberfahren) und erst im Leerlauf, damit der Seitenaufbau nichts davon merkt. */
if (matchMedia('(hover:hover) and (pointer:fine)').matches && !ruhig) {
  const vorlad = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; vorlad.unobserve(e.target);
    const b = $('.seite-bild', e.target); if (!b || b.getAttribute('src')) return;
    (window.requestIdleCallback || setTimeout)(() => { if (!b.getAttribute('src')) b.src = b.dataset.src; });
  }), { rootMargin: '300px 0px' });
  $$('.schirm, .lb-schirm').forEach(el => vorlad.observe(el));
}

/* ---- KI-Hinweis links unten (Startseite) ----
   🔴 Noah, 27.09.2026 (Runde 10): „kann noch schlichter sein, den unteren satz brauchts garnicht und ne kamera
   muss da auch nicht sein … während des scrollens kurz aufploppen und dann automatisch nach 5 sekunden
   wieder zugehen". Ein Satz, einmal je Sitzung, nach knapp einem Bildschirm Scrollen, 5 s sichtbar. */
/* Zeit auf der Seite — über alle Unterseiten einer Sitzung gezählt (Runde 14: bei Noah kam der Hinweis nie, weil der
   Zähler auf jeder Unterseite neu bei null anfing und ein alter Merker aus Runde 11 ihn für die ganze Sitzung sperrte). */
const hmZeit = (() => { let s0 = Date.now(); try { const v = +sessionStorage.getItem('hm-start'); if (v) s0 = v; else sessionStorage.setItem('hm-start', String(s0)); } catch (e) {} return () => (Date.now() - s0) / 1000; })();
const hmNach = (sek, fn) => setTimeout(fn, Math.max(0, sek - hmZeit()) * 1000);
window.hmNach = hmNach;
/* ---- KI-Hinweis als WhatsApp-Nachricht (Runde 15, 28.09.2026) ----
   🔴 Noah: „als kleines Typchen … nicht in den ersten 5 Sekunden, sondern nach 30, 40 Sekunden … wie es wäre, wenn man
   so eine WhatsApp-Nachricht bekommen würde." → nach 35 s auf der Seite (seitenübergreifend gezählt): Karte gleitet
   unten links herein, erst „tippt …", dann der Satz. Bleibt 12 s, × schließt. Einmal je Sitzung (neuer Schlüssel). */
const kt = $('.ki-toast');
if (kt) {
  let gesehen = false; try { gesehen = sessionStorage.getItem('hm-ki15') === '1'; } catch (e) {}
  if (gesehen) kt.remove();
  else {
    const cookieImWeg = () => { const c = $('.cookie-hinweis.da'); return c && !c.hidden && innerWidth < 760; };
    const weg = () => { kt.classList.remove('da'); setTimeout(() => kt.remove(), 450); };
    const zeigen = () => {
      if (cookieImWeg() || document.querySelector('.wa-chat.da')) { setTimeout(zeigen, 4000); return; }
      try { sessionStorage.setItem('hm-ki15', '1'); } catch (e) {}
      const zu = $('.kt-zu', kt), blase = $('.kt-blase', kt); if (zu && blase && zu.parentElement !== blase) blase.appendChild(zu);
      kt.hidden = false; void kt.offsetWidth; kt.classList.add('da');
      setTimeout(() => kt.classList.add('geschrieben'), ruhig ? 0 : 1300);
      $('.kt-zu', kt).addEventListener('click', weg, { once: true });
      setTimeout(weg, 13500);
    };
    hmNach(35, zeigen);
  }
}

/* ---- Zahlen-Bühne (Runde 10): der Scroll treibt drei Szenen, die Zahl zählt mit dem Scroll ---- */
const zb = $('.zahlen-buehne');
if (zb) {
  const felder = $$('.zs-feld i', zb), sterne = $$('.zs-sterne svg', zb), nr = $$('.zs-nr', zb);
  const klemm = x => Math.max(0, Math.min(1, x));
  let zuletzt = '';
  const male = () => {
    // Runde 15: der Fortschritt beginnt, wenn die Bühne 60 % hoch im Bild steht — beim Andocken steht schon „66"
    const r = zb.getBoundingClientRect(), vorlauf = innerHeight * .6, weg = r.height - innerHeight + vorlauf;
    const p = ruhig ? 1 : klemm((vorlauf - r.top) / (weg || 1));
    const s = Math.min(2.999, p * 3), szene = Math.floor(s);
    const a = klemm(s / 0.7), b = klemm((s - 1) / 0.7), c = klemm((s - 2) / 0.7);
    const n66 = Math.round(66 * a), n35 = Math.round(35 * b), n5 = Math.round(5 * c * 10) / 10;
    const schluessel = szene + '|' + n66 + '|' + n35 + '|' + n5;
    if (schluessel === zuletzt) return; zuletzt = schluessel;
    zb.dataset.szene = szene;
    felder.forEach((f, i) => { f.classList.toggle('an', i < n66); f.classList.toggle('eins', i < n35); });
    sterne.forEach((st, i) => st.classList.toggle('an', i < Math.round(n5)));
    if (!ruhig) { nr[0].textContent = n66; nr[1].textContent = n35; nr[2].textContent = (Math.max(n5, 0)).toFixed(1).replace('.', ','); }
  };
  addEventListener('scroll', () => requestAnimationFrame(male), { passive: true });
  addEventListener('resize', male); male();
}

/* ---- „Erkennst du dich wieder?" (Runde 10, Prinzip SHK v3): fünf Lagen, alle 6 s weiter, solange im Bild; Klick hält an ---- */
const lb = $('.lg-buehne');
if (lb) {
  const tabs = $$('.lg-tab', lb), pan = $$('.lg-panel', lb), TAKT = (lb.classList.contains('pb-buehne') ? 7500 : 6000) * (matchMedia('(max-width: 760px)').matches ? 1.6 : 1); // Handy: Heute und Mit uns nacheinander, also mehr Zeit je Moment
  // Runde 15: Uhren in den Szenen zählen bei jedem Zeigen neu hoch (Heute ab 0,5 s lang, Mit uns kurz)
  const zaehle = p => $$('[data-bis]', p).forEach(b => { const bis = +b.dataset.bis, mit = !!b.closest('.mit'), start = mit ? 1250 : 500, dauer = mit ? 450 : 2600;
    if (ruhig) { b.textContent = bis.toFixed(1).replace('.', ','); return; }
    b.textContent = '0,0'; const t0 = performance.now() + start; cancelAnimationFrame(b._r);
    const lauf = t => { const q = Math.max(0, Math.min(1, (t - t0) / dauer)), e = mit ? 1 - Math.pow(1 - q, 3) : q; b.textContent = (bis * e).toFixed(1).replace('.', ','); if (q < 1) b._r = requestAnimationFrame(lauf); };
    b._r = requestAnimationFrame(lauf); });
  let i = 0, timer = null, steht = ruhig;
  lb.style.setProperty('--takt', TAKT / 1000 + 's');
  const zeig = (k, fokus) => {
    i = (k + tabs.length) % tabs.length;
    tabs.forEach((t, n) => { const an = n === i; t.classList.toggle('an', an); t.setAttribute('aria-selected', an ? 'true' : 'false'); t.tabIndex = an ? 0 : -1;
      const l = $('.lauf', t); if (l && an) { l.style.animation = 'none'; void l.offsetWidth; l.style.animation = ''; } });
    pan.forEach((p, n) => { const an = n === i; p.hidden = !an; p.classList.remove('an'); if (an) { void p.offsetWidth; p.classList.add('an'); zaehle(p); } });
    if (fokus) tabs[i].focus();
    if (innerWidth < 1000 && !lb.classList.contains('lgm')) tabs[i].scrollIntoView({ block: 'nearest', inline: 'center', behavior: ruhig ? 'auto' : 'smooth' });
  };
  const lauf = () => { clearInterval(timer); if (!steht) timer = setInterval(() => zeig(i + 1), TAKT); };
  const halt = () => { steht = true; lb.classList.add('steht'); clearInterval(timer); };
  tabs.forEach((t, n) => t.addEventListener('click', () => { halt(); zeig(n); }));
  lb.addEventListener('keydown', e => { if (!e.target.classList.contains('lg-tab')) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); halt(); zeig(i + 1, true); }
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); halt(); zeig(i - 1, true); } });
  if (ruhig) lb.classList.add('steht');
  new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { zeig(i); lauf(); } else clearInterval(timer); }), { threshold: .35 }).observe(lb);
}

/* ---- Anfrage in drei Schritten (Runde 11): Name → Telefon oder Mail → Thema → abschicken ---- */
$$('form.sf-form').forEach(f => {
  const schritte = $$('.sf-schritt', f), nr = $('.sf-nr', f), balken = $('.sf-balken i', f), zurueck = $('.sf-zurueck', f);
  let n = 0;
  const zeig = k => {
    n = Math.max(0, Math.min(schritte.length - 1, k));
    schritte.forEach((s, i) => { s.hidden = i !== n; s.classList.toggle('an', i === n); });
    nr.textContent = n + 1; balken.style.transform = `scaleX(${(n + 1) / schritte.length})`;
    zurueck.hidden = n === 0;
    const feld = $('input:not([type=radio])', schritte[n]); if (feld) feld.focus({ preventScroll: true });
  };
  // Schritt 2: Telefonnummer und/oder E-Mail — mindestens eins davon, und zwar wirklich eine Nummer oder Adresse
  // (Noah, Runde 12: sonst tippt jemand wörtlich „Telefon" ins Feld).
  const telOk = v => (v.replace(/\D/g, '').length >= 6) && /^[+()\d\s\/.-]+$/.test(v.trim());
  const mailOk = v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());
  const gueltig = () => {
    const tel = $('input[name=telefon]', schritte[n]), mail = $('input[name=email]', schritte[n]);
    if (tel && mail) {
      const t = tel.value.trim(), m = mail.value.trim();
      const tOk = !t || telOk(t), mOk = !m || mailOk(m), eins = (t && telOk(t)) || (m && mailOk(m));
      tel.classList.toggle('fehlt', !tOk || (!eins && !m)); mail.classList.toggle('fehlt', !mOk || (!eins && !t));
      const ok = eins && tOk && mOk; $('.sf-fehler', schritte[n]).hidden = ok;
      if (!ok) (!tOk ? tel : !mOk ? mail : tel).focus();
      return ok;
    }
    const feld = $('input:not([type=radio])', schritte[n]);
    if (!feld) return true; const ok = feld.value.trim().length > 1; feld.classList.toggle('fehlt', !ok); if (!ok) feld.focus(); return ok; };
  $$('.sf-weiter', f).forEach(b => b.addEventListener('click', () => { if (gueltig()) zeig(n + 1); }));
  $$('.sf-schritt input:not([type=radio])', f).forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); if (gueltig()) zeig(n + 1); } }));
  zurueck.addEventListener('click', () => zeig(n - 1));
  // Runde 18: die Anfrage geht wirklich raus (Web3Forms → info@), vorher war das eine Attrappe
  f.addEventListener('submit', async e => {
    e.preventDefault();
    if (!$('input[name=thema]:checked', f)) { $('.sf-wahl', f).classList.add('fehlt'); return; }
    const knopf = $('.sf-senden', f); knopf.disabled = true;
    const fd = new FormData(f); fd.append('Seite', location.pathname);
    try { const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd }); if (!r.ok) throw 0; }
    catch (x) { knopf.disabled = false; const fe = $('.sf-schritt.an .sf-fehler', f) || document.createElement('p'); fe.className = 'sf-fehler'; fe.textContent = 'Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990'; fe.hidden = false; knopf.before(fe); return; }
    document.dispatchEvent(new CustomEvent('hwm:lead', { detail: { formular: 'anfrage' } }));
    schritte.forEach(s => s.hidden = true); $('.sf-fertig', f).hidden = false; zurueck.hidden = true;
    $('.sf-kopf', f).hidden = true; $('.sf-balken', f).hidden = true;
  });
  $$('input[name=thema]', f).forEach(r => r.addEventListener('change', () => $('.sf-wahl', f).classList.remove('fehlt')));
  zeig(0);
});
})();

/* ---- Collage (Runde 13, wie SHK): alle 1,4 s tauscht ein Feld, nur solange im Bild.
   Runde 14: nie zwei Bilder desselben Betriebs gleichzeitig (data-g), der Film bleibt stehen. ---- */
(() => {
  const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.collage').forEach(col => {
    if (ruhig) return;
    let pool = []; try { pool = JSON.parse(col.dataset.pool); } catch (e) {}
    const felder = [...col.querySelectorAll('img')]; let timer = null;
    // 🔴 Runde 15, Noah: „alle möglichen Shooting-Bilder … von allen möglichen Kunden, immer unterschiedlich … alles random
    //    durcheinander". Beim Laden wird die Startbelegung zufällig gezogen (je Betrieb höchstens ein Bild), danach tauscht
    //    alle 1,2 s ein zufälliges Feld gegen ein zufälliges Bild, das gerade nicht zu sehen ist und von keinem sichtbaren Betrieb stammt.
    const zufall = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
    const start = [], gruppen = new Set();
    for (const e of zufall(pool.slice())) { if (start.length >= felder.length) break; if (!gruppen.has(e[1])) { gruppen.add(e[1]); start.push(e); } }
    felder.forEach((f, i) => { if (start[i]) { f.dataset.k = JSON.stringify(start[i][2] || []); f.src = start[i][0]; f.dataset.g = start[i][1]; } });
    const tausch = () => {
      if (!pool.length) return;
      const sichtbar = felder.filter(f => f.offsetParent !== null); if (!sichtbar.length) return;
      const f = sichtbar[Math.floor(Math.random() * sichtbar.length)];
      const belegt = new Set(sichtbar.filter(x => x !== f).map(x => x.dataset.g)), zu_sehen = new Set(sichtbar.map(x => x.getAttribute('src')));
      const moeglich = pool.filter(e => !belegt.has(e[1]) && !zu_sehen.has(e[0]));
      if (!moeglich.length) return;
      const wahl = moeglich[Math.floor(Math.random() * moeglich.length)];
      const bild = new Image(); bild.src = wahl[0];
      bild.onload = () => { f.classList.add('raus'); setTimeout(() => { f.dataset.k = JSON.stringify(wahl[2] || []); f.src = bild.src; f.dataset.g = wahl[1]; f.classList.remove('raus'); }, 350); };
    };
    new IntersectionObserver(es => es.forEach(e => { clearInterval(timer); if (e.isIntersecting) timer = setInterval(tausch, 1200); }), { threshold: .2 }).observe(col);
  });
})();

/* ---- WhatsApp (Runde 13 + 15): Marke unten rechts nach 55 s; ein Klick öffnet ein kleines Chatfenster mit Textzeile
   und Senden-Knopf wie in WhatsApp — erst Senden öffnet WhatsApp mit dem Text. 🔴 Noah, 28.09.2026: „nicht direkt auf
   WhatsApp komplett weiterleiten, sondern da soll direkt auch unten so ein kleiner Chat … eine Textzeile … so dass es
   richtig clean ist." Ohne JavaScript bleibt der Link ein normaler WhatsApp-Link. ---- */
(() => {
  const wa = document.querySelector('.wa-marke'), chat = document.querySelector('.wa-chat'); if (!wa || !chat) return;
  const NR = '491795947911';
  const feld = chat.querySelector('input'), verlauf = chat.querySelector('.wa-verlauf');
  let zu = false; try { zu = sessionStorage.getItem('hm-wa') === '1'; } catch (e) {}
  const oeffne = () => { chat.hidden = false; void chat.offsetWidth; chat.classList.add('da'); wa.classList.remove('da'); setTimeout(() => feld.focus({ preventScroll: true }), 250); };
  const schliesse = () => { chat.classList.remove('da'); setTimeout(() => { chat.hidden = true; }, 300); };
  wa.querySelector('.wa-auf').addEventListener('click', e => { e.preventDefault(); oeffne(); });
  chat.querySelector('.wa-schliessen').addEventListener('click', schliesse);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && chat.classList.contains('da')) schliesse(); });
  document.addEventListener('click', e => { const t = e.target.closest('[data-whatsapp]'); if (t) { e.preventDefault(); oeffne(); } });
  chat.querySelector('.wa-form').addEventListener('submit', e => {
    e.preventDefault(); const text = feld.value.trim(); if (!text) { feld.focus(); feld.classList.add('leer'); setTimeout(() => feld.classList.remove('leer'), 600); return; }
    const b = document.createElement('div'); b.className = 'wa-blase aus'; b.textContent = text;
    const z = document.createElement('small'); z.textContent = 'Wird in WhatsApp geöffnet ✓✓'; b.appendChild(z); verlauf.appendChild(b); verlauf.scrollTop = verlauf.scrollHeight;
    window.open('https://wa.me/' + NR + '?text=' + encodeURIComponent(text), '_blank', 'noopener'); feld.value = '';
  });
  if (zu) { wa.remove(); return; }
  const cookieImWeg = () => { const c = document.querySelector('.cookie-hinweis.da'); return c && !c.hidden; };
  const zeigen = () => { if (cookieImWeg() || chat.classList.contains('da')) { setTimeout(zeigen, 4000); return; } wa.classList.add('da'); };
  (window.hmNach || ((s, f) => setTimeout(f, s * 1000)))(55, zeigen);
  wa.querySelector('.wa-zu').addEventListener('click', () => { wa.classList.remove('da'); try { sessionStorage.setItem('hm-wa', '1'); } catch (e) {} setTimeout(() => wa.remove(), 400); });
})();

/* ---- Websites: Aufbau einer Seite (Runde 16) — ein Leuchtfeld fährt von Stelle zu Stelle, die Liste läuft mit.
   Im Bild läuft es von selbst (3,2 s je Stelle); Hover, Fokus oder Tipp auf eine Zeile hält es dort an. ---- */
(() => {
  const ab = document.querySelector('.aufbau'); if (!ab) return;
  const spot = ab.querySelector('.ab-spot'), tag = ab.querySelector('.ab-tag'), li = [...ab.querySelectorAll('.ab-liste li')];
  if (!spot || !li.length) return;
  let i = 0, timer = 0, halt = false;
  const setze = n => { i = n; const [x, y, w, h] = li[n].dataset.r.split(',');
    spot.style.setProperty('--x', x + '%'); spot.style.setProperty('--y', y + '%'); spot.style.setProperty('--w', w + '%'); spot.style.setProperty('--h', h + '%');
    const z = ab.querySelector('.ab-zoom'); if (z) {
      // Zoom so, dass die Stelle GANZ im Bild bleibt: Mittelpunkt o je Achse aus lo ≤ o ≤ hi (Rand 4–6 %, nie über die Bildkante hinaus)
      const achse = (a, b, s, rv, rh) => { if (s <= 1.001) return (a + b) / 2; const lo = Math.max(0, (b * s - 1 + rh) / (s - 1)), hi = Math.min(1, (a * s - rv) / (s - 1)); return lo > hi ? null : Math.min(hi, Math.max(lo, (a + b) / 2)); };
      let sc = Math.max(1, Math.min(1.7, 62 / w, 62 / h)), ox, oy;
      for (; sc > 1; sc -= .05) { ox = achse(x / 100, (+x + +w) / 100, sc, .10, .04); oy = achse(y / 100, (+y + +h) / 100, sc, .015, .03); if (ox !== null && oy !== null) break; }
      if (sc <= 1) { sc = 1; ox = .5; oy = .5; }
      z.style.setProperty('--s', sc.toFixed(2)); z.style.setProperty('--ox', (ox * 100).toFixed(1) + '%'); z.style.setProperty('--oy', (oy * 100).toFixed(1) + '%'); }
    tag.textContent = n + 1; li.forEach((l, k) => { l.classList.toggle('an', k === n); if (k === n) { const lauf = l.querySelector('.ab-lauf'); if (lauf) { lauf.style.animation = 'none'; void lauf.offsetWidth; lauf.style.animation = ''; } } }); };
  const lauf = () => { clearInterval(timer); ab.classList.toggle('laeuft', !halt); if (!halt && !matchMedia('(prefers-reduced-motion: reduce)').matches) timer = setInterval(() => setze((i + 1) % li.length), 3200); };
  li.forEach((l, n) => { const an = () => { halt = true; setze(n); lauf(); };
    l.addEventListener('mouseenter', an); l.addEventListener('focus', an); l.addEventListener('click', an); });
  ab.querySelector('.ab-liste').addEventListener('mouseleave', () => { halt = false; lauf(); });
  new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { ab.classList.add('sichtbar'); setze(i); lauf(); } else { clearInterval(timer); } }), { threshold: .3 }).observe(ab);
})();

/* ---- Köpfe nie abschneiden (Runde 15, 28.09.2026) ----
   🔴 Noah: „Köpfe dürfen nirgends abgeschnitten sein. Das generell regeln." Jedes Bild/Poster trägt seine Kopf-Rechtecke
   (data-k, normiert). Für object-fit:cover wird je Achse der Ausschnitt gesucht, in dem möglichst viele Köpfe GANZ drin
   sind und keiner angeschnitten — nah an der gestalteten Vorgabe. Läuft beim Laden, beim Sichtbarwerden und bei Größenänderung. */
(() => {
  // oben = Anteil des Elements, den ein schräges Dach (clip-path der Hero-Säulen) oben wegschneidet
  const achse = (koepfe, frei, p0, oben = 0) => {
    if ((frei >= .995 && !oben) || !koepfe.length) return p0;
    let best = p0, bestS = -1e9;
    for (let i = 0; i <= 100; i++) {
      const p = i / 100, a = p * (1 - frei) + frei * oben, b = p * (1 - frei) + frei; let s = 0;
      for (const [x, w] of koepfe) { const drin = x >= a - .003 && x + w <= b + .003, schnitt = Math.min(x + w, b) - Math.max(x, a);
        if (drin) s += 10; else if (schnitt > w * .02) s -= 8; }
      s -= Math.abs(p - p0) * 1.5;
      if (s > bestS + 1e-9) { bestS = s; best = p; }
    }
    return best;
  };
  const prozent = v => { if (!v) return .5; if (v.endsWith('%')) return parseFloat(v) / 100; return { left: 0, top: 0, right: 1, bottom: 1, center: .5 }[v] ?? .5; };
  const setze = el => {
    let k; try { k = JSON.parse(el.dataset.k || '[]'); } catch (e) { return; }
    if (!k.length) return;
    const st = getComputedStyle(el); if (st.objectFit !== 'cover' || st.display === 'none') return;
    const nw = el.naturalWidth || el.videoWidth, nh = el.naturalHeight || el.videoHeight; if (!nw || !nh) return;
    const r = el.getBoundingClientRect(); if (r.width < 20 || r.height < 20) return;
    if (!el.dataset.pos0) el.dataset.pos0 = st.objectPosition;
    const [v0x, v0y] = el.dataset.pos0.split(' ');
    const s = Math.max(r.width / nw, r.height / nh), wv = r.width / (nw * s), hv = r.height / (nh * s);
    let oben = 0; const dach = el.closest('[class*="saeulen"] > div, .saeulen-k > div');
    if (dach) { const m = getComputedStyle(dach).clipPath.match(/polygon\(\s*[\d.]+%?\s+([\d.]+)%\s*,\s*[\d.]+%?\s+([\d.]+)%/); if (m) oben = Math.max(+m[1], +m[2]) / 100; }
    const px = achse(k.map(q => [q[0], q[2]]), wv, prozent(v0x)), py = achse(k.map(q => [q[1], q[3]]), hv, prozent(v0y), oben);
    el.style.objectPosition = `${(px * 100).toFixed(1)}% ${(py * 100).toFixed(1)}%`;
  };
  window.hmKopf = setze;
  const alle = () => document.querySelectorAll('img[data-k], video[data-k]');
  const bereit = el => { if (el.tagName === 'IMG') { if (el.complete) setze(el); el.addEventListener('load', () => setze(el)); } else { if (el.readyState >= 1) setze(el); el.addEventListener('loadedmetadata', () => setze(el)); } };
  alle().forEach(bereit);
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) setze(e.target); }), { rootMargin: '200px' });
  alle().forEach(el => io.observe(el));
  let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => alle().forEach(setze), 150); });
  // Bilder, die ihre Quelle später wechseln (Collage), bringen ihre Köpfe über data-k mit
  new MutationObserver(ms => ms.forEach(m => { if (m.attributeName === 'src' && m.target.dataset.k) { m.target.removeAttribute('data-pos0'); m.target.style.objectPosition = ''; if (m.target.complete) setze(m.target); } }))
    .observe(document.body, { subtree: true, attributes: true, attributeFilter: ['src'] });
})();

/* ---- Über uns: Zeitstrahl 2019–2026 (Runde 16) — die Bühne klebt, vertikales Scrollen fährt die Spur waagerecht
   von 2019 bis 2026, die Linie füllt sich, jede Station leuchtet auf, sobald die Linie sie erreicht. Unter 901 px: Liste. ---- */
(() => {
  const b = document.querySelector('.zs-buehne'); if (!b) return;
  const spur = b.querySelector('.zs-spur'), ol = b.querySelector('.zeitstrahl'), st = [...b.querySelectorAll('.zs-station')];
  let weg = 0;
  const mass = () => {
    const bild = st[0] && st[0].querySelector('.zs-bild'); if (bild) spur.style.setProperty('--zs-bild-h', bild.offsetHeight + 'px');
    weg = matchMedia('(min-width: 901px)').matches ? Math.max(0, ol.scrollWidth - spur.clientWidth + 2 * parseFloat(getComputedStyle(spur).paddingLeft || 0)) : 0;
    b.style.setProperty('--zs-weg', Math.round(weg * 1.1) + 'px'); lauf();
  };
  const lauf = () => {
    let p;
    if (weg > 0) { const r = b.getBoundingClientRect(), gesamt = b.offsetHeight - innerHeight; p = Math.min(1, Math.max(0, -r.top / Math.max(1, gesamt)));
      ol.style.transform = `translate3d(${-p * weg}px,0,0)`; }
    else { ol.style.transform = ''; }
    const sr = spur.getBoundingClientRect(), linie = spur.querySelector('.zs-linie');
    if (weg > 0) {
      // Linie füllt sich bis zur Station, die gerade in der Mitte des Bildschirms steht; alles links davon ist „da"
      const mitte = innerWidth * .62; let fuell = 0;
      st.forEach(s => { const r = s.getBoundingClientRect(); const da = r.left < mitte; s.classList.toggle('da', da); if (da) fuell = Math.max(fuell, r.left + 8 - sr.left); });
      if (linie) linie.style.setProperty('--zs-p', Math.min(1, fuell / Math.max(1, sr.width)).toFixed(3));
      if (p >= .995) { st.forEach(s => s.classList.add('da')); if (linie) linie.style.setProperty('--zs-p', 1); }
    } else {
      st.forEach(s => { const r = s.getBoundingClientRect(); if (r.top < innerHeight * .85) s.classList.add('da'); });
    }
  };
  addEventListener('scroll', () => requestAnimationFrame(lauf), { passive: true });
  addEventListener('resize', mass); addEventListener('load', mass); mass();
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) st.forEach(s => s.classList.add('da'));
})();

/* ---- Potenzial-Rechner (Runde 17, 28.09.2026) — von der SHK-Seite übernommen: eine Frage je Schritt, dann PLZ, kurzer
   Umkreis-Radar, Betrieb, Kontakt, abschicken (Web3Forms → info@). Öffnet über [data-rechner] und a[href="#rechner-auf"]. ---- */
const rechnerStarten = (dlg) => {
  const inline = !dlg.matches('dialog');
  const $ = (s, r = dlg) => r.querySelector(s), $$ = (s, r = dlg) => [...r.querySelectorAll(s)];
  const form = $('.rd-form'), schritte = $$('.rd-schritt'), balken = $('.rd-balken i'), zurueck = $('.rd-zurueck');
  const d = {}; let akt = 1; const MAX = 9; let uhr = 0; let beruehrt = false;
  const eur = n => Math.round(n).toLocaleString('de-DE') + ' €';
  const spur = (name, extra) => { try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name, rechner: inline ? 'seite' : 'popup' }, extra || {})); } catch (e) {} };
  // 🔴 Noah, 29.09.2026: „das muss noch ein bisschen smoother sein" — beim Schrittwechsel sprang das Fenster in der Höhe
  //    (height:fit-content) und zentrierte sich ruckartig neu. Jetzt gleitet die Höhe vom alten zum neuen Maß.
  const ruhigM = matchMedia('(prefers-reduced-motion: reduce)');
  let hoeheAnim = null;
  const zeig = n => {
    const h0 = dlg.getBoundingClientRect().height;
    akt = n; schritte.forEach(s => { const an = +s.dataset.schritt === n; s.hidden = !an; s.classList.toggle('an', an); });
    balken.style.transform = `scaleX(${Math.min(n, MAX) / MAX})`;
    zurueck.hidden = n === 1 || n === 7 || n === 10;
    const b = d.ziel === 'Kunden';
    $$('[data-text-a]').forEach(el => el.textContent = b ? el.dataset.textB : el.dataset.textA);
    $$('[data-fuer]').forEach(el => el.hidden = el.dataset.fuer !== (d.ziel || 'Mitarbeiter'));
    if (n === 5) { const sum = $('[data-summe]'), ziel = (+d.anzahl || 1) * (+d.wert || 3000), t0 = performance.now();
      const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
      const lauf = t => { const p = ruhig ? 1 : Math.min(1, (t - t0) / 900); sum.textContent = eur(ziel * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(lauf); };
      requestAnimationFrame(lauf); const bl = $('[data-beleg]'); bl.textContent = b ? bl.dataset.belegB : bl.dataset.belegA; }
    const h1 = dlg.getBoundingClientRect().height;
    if (h0 > 0 && Math.abs(h1 - h0) > 2 && !ruhigM.matches && dlg.animate) {
      if (hoeheAnim) hoeheAnim.cancel();
      dlg.style.overflow = 'hidden';
      hoeheAnim = dlg.animate([{ height: h0 + 'px' }, { height: h1 + 'px' }], { duration: 380, easing: 'cubic-bezier(.22,.8,.24,1)' });
      hoeheAnim.onfinish = hoeheAnim.oncancel = () => { dlg.style.overflow = ''; hoeheAnim = null; };
    }
    // Auf der Seite nie von selbst ins Feld springen (sonst scrollt die Seite beim Laden weg)
    const f = $('.rd-schritt.an input'); if (f && (beruehrt || !inline)) setTimeout(() => f.focus({ preventScroll: inline }), 60);
    if (beruehrt || !inline) spur('rechner_schritt', { schritt: n });
  };
  if (inline) { zeig(1); dlg.addEventListener('pointerdown', () => { beruehrt = true; }, { once: true }); dlg.addEventListener('keydown', () => { beruehrt = true; }, { once: true }); }
  else {
    const oeffne = () => { if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', ''); document.documentElement.classList.add('rd-offen'); beruehrt = true; zeig(1); spur('rechner_offen'); };
    // Schließen mit derselben Bewegung rückwärts statt schlagartig weg
    const zu = () => { const ende = () => { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); document.documentElement.classList.remove('rd-offen'); };
      if (ruhigM.matches || !dlg.animate) return ende();
      dlg.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(12px) scale(.98)' }], { duration: 220, easing: 'cubic-bezier(.4,0,1,1)' }).onfinish = ende; };
    document.addEventListener('click', e => { const t = e.target.closest('[data-rechner], a[href="#rechner-auf"]'); if (!t) return;
      // Steht der Rechner auf dieser Seite offen da, dorthin scrollen statt das Fenster zu öffnen
      const block = document.querySelector('.rd-inline'); e.preventDefault();
      if (block && t.dataset.rechner !== 'popup') { block.scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }
      oeffne(); });
    $('.rd-zu').addEventListener('click', zu);
    dlg.addEventListener('click', e => { if (e.target === dlg) zu(); });
    dlg.addEventListener('close', () => document.documentElement.classList.remove('rd-offen'));
  }
  form.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.tagName === 'INPUT' && akt < 9) { e.preventDefault(); const w = $('.rd-schritt.an [data-weiter]'); if (w) w.click(); } });
  zurueck.addEventListener('click', () => zeig(akt === 8 ? 6 : Math.max(1, akt - 1)));
  $$('.rd-wahl button').forEach(b => b.addEventListener('click', () => {
    beruehrt = true; d[b.dataset.feld] = b.dataset.wert;
    $$(`.rd-wahl button[data-feld="${b.dataset.feld}"]`).forEach(x => x.classList.toggle('an', x === b));
    setTimeout(() => zeig(akt + 1), 220);
  }));
  const radar = () => {
    const r = $('[data-radar]'), ok = $('.rd-radar-ok', r), t = $('[data-radar-text]', r);
    const ort = form.elements.ort.value.trim(), plz = form.elements.plz.value.trim();
    clearTimeout(uhr); r.classList.remove('fertig'); ok.hidden = true; t.hidden = false; t.textContent = `Umkreis ${plz} ${ort} wird vorgemerkt …`;
    uhr = setTimeout(() => { r.classList.add('fertig'); t.hidden = true; ok.hidden = false; $('[data-radar-titel]', r).textContent = `${ort} ist vorgemerkt.`; const k = $('button', ok); if (k) k.focus({ preventScroll: inline }); spur('rechner_radar', { plz }); }, matchMedia('(prefers-reduced-motion: reduce)').matches ? 300 : 1400);
  };
  $$('[data-weiter]').forEach(b => b.addEventListener('click', () => {
    let leer = null;
    $$('.rd-schritt.an input[required]').forEach(f => { const falsch = !f.value.trim() || (f.name === 'plz' && !/^[0-9]{4,5}$/.test(f.value.trim())); f.classList.toggle('fehlt', falsch); if (falsch && !leer) leer = f; });
    const h = $('.rd-schritt.an [data-fehler-ort]'); if (h) h.hidden = !leer;
    if (leer) { leer.focus(); return; }
    zeig(akt + 1); if (akt === 7) radar();
  }));
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const name = form.elements.name.value.trim(), tel = form.elements.telefon.value.trim(), fehler = $('[data-fehler-kontakt]');
    if (!name || !tel) { fehler.hidden = false; return; } fehler.hidden = true;
    const fd = new FormData(form);
    fd.append('Ziel', d.ziel || ''); fd.append('Stelle / Auftrag', d.stelle || ''); fd.append('Anzahl je Monat', d.anzahl || ''); fd.append('Wert je Auftrag', d.wert ? eur(+d.wert) : ''); fd.append('Seite', location.pathname);
    const knopf = $('button[type=submit]'); knopf.disabled = true;
    try { const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd }); if (!r.ok) throw 0; } catch (x) { knopf.disabled = false; fehler.textContent = 'Das hat nicht geklappt. Ruf gern direkt an: +49 8194 7174990'; fehler.hidden = false; return; }
    const cal = $('[data-cal]'); if (d.ziel === 'Kunden') cal.href = cal.dataset.calB;
    spur('rechner_abgeschickt', { ziel: d.ziel }); document.dispatchEvent(new CustomEvent('hwm:lead', { detail: { formular: 'rechner', ziel: d.ziel || '' } })); zeig(10);
  });
};
document.querySelectorAll('.rd').forEach(rechnerStarten);

/* ---- Ratgeber: Selbsttest-Zähler + Lesebalken (29.09.2026) ---- */
(() => {
  document.querySelectorAll('[data-test]').forEach(t => {
    const z = t.querySelector('[data-test-zahl]');
    t.addEventListener('change', () => { z.textContent = t.querySelectorAll('input:checked').length; });
  });
  const art = document.querySelector('.rg-text'); if (!art) return;
  const b = document.createElement('div'); b.className = 'rg-lesebalken'; b.setAttribute('aria-hidden', 'true'); document.body.appendChild(b);
  let lauf = false;
  const f = () => { lauf = false; const r = art.getBoundingClientRect(); const p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight))); b.style.transform = `scaleX(${p.toFixed(3)})`; };
  addEventListener('scroll', () => { if (!lauf) { lauf = true; requestAnimationFrame(f); } }, { passive: true }); f();
})();

/* ═══════ HANDY-FASSUNG (03.10.2026): eigene Bühnen fürs Telefon — nur bis 760 px, nie am Desktop ═══════
   Noah: „Mobil kann man doch eh eigentlich ziemlich viel nice mit Animation machen." Ein Takt (rAF), eine
   Fortschritts-Rechnung je Bühne, Bewegung nur über transform/opacity. Ohne Skript oder mit reduzierter
   Bewegung bleibt die gestapelte Fassung stehen. */
(() => {
  const handy = matchMedia('(max-width: 760px)');
  if (!handy.matches) return;
  const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const klemm = x => Math.max(0, Math.min(1, x));
  const sanft = x => 1 - Math.pow(1 - x, 3);
  const neuStarten = el => { el.style.display = 'none'; void el.offsetWidth; el.style.display = ''; };
  const takt = [];
  let geplant = false;
  const lauf = () => { geplant = false; takt.forEach(f => f()); };
  addEventListener('scroll', () => { if (!geplant) { geplant = true; requestAnimationFrame(lauf); } }, { passive: true });
  addEventListener('resize', () => requestAnimationFrame(lauf));

  /* ── Fünf Momente: Symbol-Leiste, Titel darunter, Heute → Mit uns wischt im selben Rahmen; Wischen mit dem Daumen ── */
  $$('.lg-buehne').forEach(lb => {
    const tabs = $$('.lg-tab', lb), pan = $$('.lg-panel', lb), panels = $('.lg-panels', lb);
    if (!tabs.length || !panels) return;
    lb.classList.add('lgm');
    const pb = lb.classList.contains('pb-buehne');
    const FLIP = pb ? 5000 : 4000;
    const etikett = (k, fall) => { const e = $(`.lg-seite.${k} .lg-etikett`, lb); return e ? e.textContent.replace(/^[✕✓]/, '').trim() : fall; };
    const titel = document.createElement('div'); titel.className = 'lgm-titel'; titel.setAttribute('aria-hidden', 'true');
    titel.innerHTML = `<small>Moment <span>1</span> von ${tabs.length}</small><b></b>`;
    $('.lg-tabs', lb).after(titel);
    const sch = document.createElement('div'); sch.className = 'lgm-schalter'; sch.dataset.mit = '0';
    sch.setAttribute('role', 'group'); sch.setAttribute('aria-label', 'Vergleich umschalten');
    sch.innerHTML = `<i class="lgm-daumen" aria-hidden="true"></i><button type="button" aria-pressed="true"><i aria-hidden="true">✕</i>${etikett('heute', 'Heute')}</button><button type="button" aria-pressed="false"><i aria-hidden="true">✓</i>${etikett('mit', 'Mit uns')}</button>`;
    panels.before(sch);
    const [bH, bM] = $$('button', sch);
    let uhr = null, aktiv = null, wunsch = null;
    const zaehle = seite => $$('[data-bis]', seite).forEach(b => {
      const bis = +b.dataset.bis; cancelAnimationFrame(b._r);
      if (ruhig) { b.textContent = bis.toFixed(1).replace('.', ','); return; }
      b.textContent = '0,0'; const t0 = performance.now() + 650;
      const f = t => { const q = klemm((t - t0) / 500); b.textContent = (bis * sanft(q)).toFixed(1).replace('.', ','); if (q < 1) b._r = requestAnimationFrame(f); };
      b._r = requestAnimationFrame(f);
    });
    const setze = (p, mit) => {
      clearTimeout(uhr);
      p.classList.toggle('mit-an', mit);
      sch.dataset.mit = mit ? '1' : '0'; bH.setAttribute('aria-pressed', mit ? 'false' : 'true'); bM.setAttribute('aria-pressed', mit ? 'true' : 'false');
      const s = $(mit ? '.lg-seite.mit' : '.lg-seite.heute', p);
      if (s) { neuStarten(s); if (mit) zaehle(s); }
    };
    const zeigen = p => {
      aktiv = p; const k = pan.indexOf(p);
      const t = tabs[k]; $('span', titel).textContent = k + 1; $('b', titel).textContent = t ? $('b', t).textContent.replace(/­/g, '') : '';
      titel.classList.remove('neu'); void titel.offsetWidth; titel.classList.add('neu');
      if (wunsch !== null) { const w = wunsch; wunsch = null; setze(p, w); return; }
      p.classList.remove('mit-an'); sch.dataset.mit = '0'; bH.setAttribute('aria-pressed', 'true'); bM.setAttribute('aria-pressed', 'false');
      clearTimeout(uhr); if (!ruhig) uhr = setTimeout(() => setze(p, true), FLIP);  // reduzierte Bewegung: Umschalten nur per Tipp
    };
    // nur auf das NEUE Einschalten eines Moments hören (alt ohne „an", jetzt mit) — sonst schaukelt sich der Beobachter selbst auf
    const hatAn = c => /(^|\s)an(\s|$)/.test(c || '');
    new MutationObserver(ms => ms.forEach(m => { const p = m.target; if (pan.includes(p) && !hatAn(m.oldValue) && hatAn(p.className) && !p.hidden) zeigen(p); }))
      .observe(panels, { subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['class'] });
    const aktuell = () => pan.indexOf(aktiv || pan.find(p => !p.hidden) || pan[0]);
    // Schalter und Wischen halten den automatischen Wechsel an (wie ein Tipp auf einen Reiter)
    const manuell = mit => { wunsch = mit; tabs[aktuell()].click(); };
    bH.addEventListener('click', () => manuell(false));
    bM.addEventListener('click', () => manuell(true));
    let x0 = null, y0 = 0;
    panels.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    panels.addEventListener('touchend', e => {
      if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
      if (Math.abs(dx) < 45 || Math.abs(dx) < Math.abs(dy) * 1.3) return;
      const mit = aktiv && aktiv.classList.contains('mit-an'), k = aktuell();
      if (dx < 0) { if (!mit) manuell(true); else { wunsch = false; tabs[(k + 1) % tabs.length].click(); } }
      else { if (mit) manuell(false); else { wunsch = true; tabs[(k - 1 + tabs.length) % tabs.length].click(); } }
    }, { passive: true });
    // gleiche Höhe für alle fünf Momente — die Seite springt beim Wechsel nicht
    const messen = () => {
      lb.style.removeProperty('--lgm-h'); let h = 0;
      pan.forEach(p => { const war = p.hidden; p.hidden = false; h = Math.max(h, p.offsetHeight); p.hidden = war; });
      if (h) lb.style.setProperty('--lgm-h', Math.ceil(h) + 'px');
    };
    messen(); addEventListener('load', messen); if (document.fonts) document.fonts.ready.then(messen);
    let bx = innerWidth; addEventListener('resize', () => { if (innerWidth !== bx) { bx = innerWidth; messen(); } });
    const erst = pan.find(p => p.classList.contains('an') && !p.hidden); if (erst) zeigen(erst);
  });

  /* ── Drei Säulen: gepinnte Bühne, die Säulen wachsen nacheinander aus dem Boden — am Ende steht das Logo ── */
  const sae = $('.system-sek .system-saeulen');
  if (sae && !ruhig) {
    const hubs = $$('.ss-hub', sae);
    if (hubs.length === 3) {
      sae.classList.add('ssm'); sae.closest('.sek')?.classList.add('ssm-sek');
      const klebt = document.createElement('div'); klebt.className = 'ssm-klebt';
      const reihe = document.createElement('div'); reihe.className = 'ssm-saeulen'; reihe.setAttribute('aria-hidden', 'true');
      const texte = document.createElement('div'); texte.className = 'ssm-texte';
      const karten = hubs.map(h => { reihe.appendChild(h); const t = document.createElement('div'); t.className = 'ssm-text';
        $$('.ss-in > *', h).forEach(k => t.appendChild(k.cloneNode(true))); texte.appendChild(t); return t; });
      klebt.append(reihe, texte); sae.prepend(klebt);
      const ss = hubs.map(h => $('.ss', h));
      let zuletzt = '';
      const male = () => {
        const r = sae.getBoundingClientRect(), H = innerHeight;
        if (r.bottom < -H || r.top > H * 2) return;
        const vor = H * .45, weg = Math.max(1, r.height - H + vor * .4);
        const s = klemm((vor - r.top) / weg) * 3;
        const g = [0, 1, 2].map(i => sanft(klemm((s - i * .92) / .7)));
        const an = Math.min(2, Math.max(0, Math.floor(s * 1.0 - .05)));
        const key = g.map(x => x.toFixed(3)).join() + an;
        if (key === zuletzt) return; zuletzt = key;
        ss.forEach((e, i) => { e.style.transform = `translate3d(0,${((1 - g[i]) * 101).toFixed(2)}%,0)`; });
        hubs.forEach((h, i) => h.classList.toggle('an', i === an));
        karten.forEach((k, i) => { const ja = i === an; k.classList.toggle('an', ja); k.inert = !ja; ja ? k.removeAttribute('aria-hidden') : k.setAttribute('aria-hidden', 'true'); });
      };
      takt.push(male); male();
    }
  }

  /* ── Kartenstapel: Fallstudien (Start) und „Was du bekommst" (Unterseiten) — die obere Karte tritt zurück,
        wenn die nächste darüber gleitet ── */
  if (!ruhig && innerHeight >= 640) [['.erg-sek .ergebnisse', '.erg'], ['.bento-sek .bento', '.zelle']].forEach(([cs, ks]) => $$(cs).forEach(box => {
    const k = $$(ks, box).filter(c => c.parentElement === box);
    if (k.length < 2) return;
    box.classList.add('stapelm'); box.closest('.sek')?.classList.add('stapelm-sek');
    const male = () => {
      const br = box.getBoundingClientRect(); if (br.bottom < 0 || br.top > innerHeight) return;
      k.forEach((c, i) => {
        const n = k[i + 1]; if (!n) return;
        const a = c.getBoundingClientRect(), b = n.getBoundingClientRect();
        const q = klemm(1 - (b.top - a.top) / Math.max(1, a.height));
        c.style.scale = (1 - .07 * q).toFixed(4);
        c.style.opacity = (1 - .35 * q).toFixed(3);
      });
    };
    takt.push(male); male();
  }));

  /* ── Treppe „So läuft es ab": Zeitstrahl, dessen Linie mit dem Scrollen wächst ── */
  if (!ruhig) $$('.treppe').forEach(tr => {
    const st = $$('.stufe', tr); if (st.length < 2) return;
    tr.classList.add('trpm');
    const linie = document.createElement('i'); linie.className = 'trpm-linie'; linie.setAttribute('aria-hidden', 'true'); tr.prepend(linie);
    let zuletzt = -1;
    const male = () => {
      const r = tr.getBoundingClientRect(), H = innerHeight; if (r.bottom < 0 || r.top > H) return;
      // voll, wenn die Treppe ganz im Bild ist oder ihr Ende die Bildmitte erreicht (Scroll-Scrub endet im Sichtfeld)
      const p = klemm((H * .78 - r.top) / Math.max(1, r.height - H * .28));
      if (Math.abs(p - zuletzt) < .002) return; zuletzt = p;
      linie.style.transform = `scaleY(${p.toFixed(4)})`;
      const y = r.top + 22 + (r.height - 44) * p;
      st.forEach(s => { const sr = s.getBoundingClientRect(); s.classList.toggle('an', sr.top + 30 <= y); });
    };
    takt.push(male); male();
  });
  lauf();
})();
