/* ═══════════════════════════════════════════════════════════════
   HandwerksManufaktur · /neu-neu/ · Bewegung
   Kein GSAP, kein Webflow: sticky + eine rAF-Schleife.
   Alles ist additiv — fällt das Skript aus, bleibt die Seite lesbar.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var sanft = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var handy = function () { return innerWidth <= 680; };
  var $ = function (s, w) { return (w || document).querySelector(s); };
  var $$ = function (s, w) { return Array.prototype.slice.call((w || document).querySelectorAll(s)); };
  var klemm = function (v, a, b) { return v < a ? a : v > b ? b : v; };

  /* ── Intro ──────────────────────────────────────────────── */
  (function () {
    var intro = $('#intro');
    if (!intro) return;
    if (sanft || sessionStorage.getItem('nn-intro')) { intro.remove(); return; }
    // Pfadlängen messen, damit sich jeder Körper sauber zeichnet
    $$('.k', intro).forEach(function (p) {
      try { p.style.setProperty('--len', Math.ceil(p.getTotalLength()) + ''); } catch (e) {}
    });
    document.body.style.overflow = 'hidden';
    setTimeout(function () {
      intro.classList.add('fort');
      document.body.style.overflow = '';
      sessionStorage.setItem('nn-intro', '1');
      setTimeout(function () { intro.remove(); }, 900);
    }, 1450);
  })();

  /* ── Navigation + Burger ────────────────────────────────── */
  var nav = $('#nav');
  var burger = $('#burger');
  var menu = $('#mobilmenu');

  function menuZu() {
    if (!menu || menu.hidden) return;
    menu.hidden = true;
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Menü öffnen');
    document.body.style.overflow = '';
  }
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var auf = menu.hidden;
      menu.hidden = !auf;
      burger.setAttribute('aria-expanded', auf ? 'true' : 'false');
      burger.setAttribute('aria-label', auf ? 'Menü schließen' : 'Menü öffnen');
      document.body.style.overflow = auf ? 'hidden' : '';
    });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', menuZu); });
    addEventListener('keydown', function (e) { if (e.key === 'Escape') menuZu(); });
    addEventListener('resize', function () { if (innerWidth > 900) menuZu(); });
  }

  /* ── Reveals (additiv) ──────────────────────────────────── */
  (function () {
    var ziele = $$('.rv').concat($$('h1.display, h2.display'));
    if (!('IntersectionObserver' in window) || sanft) {
      ziele.forEach(function (e) { e.classList.add('sichtbar'); });
      return;
    }
    var beobachter = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('sichtbar'); beobachter.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    ziele.forEach(function (e) { beobachter.observe(e); });
    // Bento-Karten melden ihre eigene Sichtbarkeit (Balken-Animation)
    $$('.bk').forEach(function (e) { beobachter.observe(e); });
  })();

  /* ── Marquee: Tempo aus der echten Spurbreite ───────────── */
  (function () {
    $$('.marq').forEach(function (m) {
      var spur = $('.marq-spur', m);
      if (!spur) return;
      // Inhalt verdoppeln, damit die Schleife nahtlos läuft
      spur.innerHTML += spur.innerHTML;
      var tempo = parseFloat(m.dataset.tempo || '60');
      function setzen() {
        var breite = spur.scrollWidth / 2;
        spur.style.setProperty('--dauer', Math.max(18, breite / tempo) + 's');
      }
      setzen();
      addEventListener('resize', setzen);
      if (document.readyState !== 'complete') addEventListener('load', setzen);
    });
  })();

  /* ── Zahlen zählen hoch ─────────────────────────────────── */
  (function () {
    var zellen = $$('[data-zaehl]');
    if (!zellen.length) return;
    if (sanft || !('IntersectionObserver' in window)) {
      zellen.forEach(function (z) { z.textContent = z.dataset.zaehl + (z.dataset.suffix || ''); });
      return;
    }
    var b = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        b.unobserve(e.target);
        var el = e.target, ziel = parseFloat(el.dataset.zaehl), suf = el.dataset.suffix || '';
        var start = performance.now(), dauer = 1100;
        (function lauf(t) {
          var p = klemm((t - start) / dauer, 0, 1);
          var e2 = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(ziel * e2) + suf;
          if (p < 1) requestAnimationFrame(lauf);
        })(start);
      });
    }, { threshold: 0.4 });
    zellen.forEach(function (z) { b.observe(z); });
  })();

  /* ── Vorher / Nachher: 1:1 am Zeiger ────────────────────── */
  (function () {
    var vn = $('#vn');
    if (!vn) return;
    var bild = $('.vn-bild', vn), griff = $('.vn-griff', vn);
    var vorher = $('.vn-vorher', vn), nachher = $('.vn-nachher', vn);
    var p = 50;

    function setzen(neu) {
      p = klemm(neu, 0, 100);
      bild.style.setProperty('--p', p + '%');
      griff.setAttribute('aria-valuenow', Math.round(p));
    }
    function ausZeiger(x) {
      var r = bild.getBoundingClientRect();
      setzen(((x - r.left) / r.width) * 100);
    }

    bild.addEventListener('pointerdown', function (e) {
      bild.setPointerCapture(e.pointerId);
      bild.dataset.zieht = '1';
      ausZeiger(e.clientX);
    });
    bild.addEventListener('pointermove', function (e) {
      if (bild.dataset.zieht === '1') { e.preventDefault(); ausZeiger(e.clientX); }
    });
    ['pointerup', 'pointercancel'].forEach(function (t) {
      bild.addEventListener(t, function () { bild.dataset.zieht = '0'; });
    });
    griff.addEventListener('keydown', function (e) {
      var s = e.shiftKey ? 10 : 4;
      if (e.key === 'ArrowLeft') { setzen(p - s); e.preventDefault(); }
      if (e.key === 'ArrowRight') { setzen(p + s); e.preventDefault(); }
      if (e.key === 'Home') { setzen(0); e.preventDefault(); }
      if (e.key === 'End') { setzen(100); e.preventDefault(); }
    });

    $$('.vn-wahl button', vn).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('.vn-wahl button', vn).forEach(function (o) { o.setAttribute('aria-selected', 'false'); });
        b.setAttribute('aria-selected', 'true');
        vorher.src = b.dataset.v;
        nachher.src = b.dataset.n;
        vorher.alt = b.dataset.name + ', alte Website';
        nachher.alt = b.dataset.name + ', neue Website';
        setzen(50);
      });
    });

    addEventListener('resize', function () { setzen(p); });
    if (document.readyState !== 'complete') addEventListener('load', function () { setzen(50); });
    setzen(50);
  })();

  /* ── Videos erst im Blick laden und starten ─────────────── */
  (function () {
    var videos = $$('video[data-lazy]');
    if (!videos.length) return;
    if (!('IntersectionObserver' in window)) {
      videos.forEach(function (v) { v.src = v.dataset.lazy; });
      return;
    }
    var b = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          if (!v.src) { v.src = v.dataset.lazy; v.load(); }
          if (!sanft) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
        } else if (!v.paused) { v.pause(); }
      });
    }, { rootMargin: '200px 0px', threshold: 0.15 });
    videos.forEach(function (v) { b.observe(v); });
  })();

  /* ── Formular ───────────────────────────────────────────── */
  (function () {
    var form = $('#ktForm'), meldung = $('#ktMeldung');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var knopf = $('button[type=submit]', form);
      knopf.disabled = true;
      meldung.textContent = 'Wird gesendet …';
      fetch('https://api.web3forms.com/submit', { method: 'POST', body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.success) {
            form.reset();
            meldung.textContent = 'Danke. Wir melden uns innerhalb von 24 Stunden.';
          } else { throw new Error('abgelehnt'); }
        })
        .catch(function () {
          meldung.textContent = 'Hat nicht geklappt. Ruf kurz an: +49 8194 7174990';
        })
        .then(function () { knopf.disabled = false; });
    });
  })();

  /* ═══════════ Eine rAF-Schleife für alles Scrollgebundene ═══════════ */
  var hz = $('#hz'), hzSpur = $('#hzSpur'), hzLeiste = $('#hzLeiste');
  var ab = $('#ab'), abStufen = $$('#abStufen li'), abFuell = $('#abFuell'), abProzent = $('#abProzent');
  var fortSeg = $$('#fortschritt i');
  var navZiele = $$('.nav-ziele a');
  var abschnitte = navZiele.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  var laueft = false;

  function rechnen() {
    laueft = false;
    var y = scrollY || pageYOffset;
    var vh = innerHeight;

    /* Nav verdichten */
    if (nav) nav.classList.toggle('tief', y > 40);

    /* Fortschritt über drei Segmente */
    if (fortSeg.length === 3) {
      var doc = document.documentElement.scrollHeight - vh;
      var g = doc > 0 ? klemm(y / doc, 0, 1) : 0;
      for (var i = 0; i < 3; i++) {
        fortSeg[i].style.setProperty('--f', klemm(g * 3 - i, 0, 1) + '');
      }
    }

    /* Aktiver Menüpunkt */
    for (var n = abschnitte.length - 1; n >= 0; n--) {
      var s = abschnitte[n];
      if (s && s.getBoundingClientRect().top <= vh * 0.35) {
        navZiele.forEach(function (a) { a.classList.remove('aktiv'); });
        navZiele[n].classList.add('aktiv');
        break;
      }
    }

    /* Arbeiten: horizontal */
    if (hz && hzSpur && !handy() && !sanft) {
      var r = hz.getBoundingClientRect();
      var weg = hz.offsetHeight - vh;
      var p = weg > 0 ? klemm(-r.top / weg, 0, 1) : 0;
      var rand = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--rand')) || 40;
      var strecke = Math.max(0, hzSpur.scrollWidth - innerWidth + rand * 2);
      hzSpur.style.transform = 'translate3d(' + (-p * strecke).toFixed(1) + 'px,0,0)';
      if (hzLeiste) hzLeiste.style.setProperty('--w', (4 + p * 96).toFixed(1) + '%');
    }

    /* Ablauf: vier Stufen */
    if (ab && abStufen.length && !handy() && !sanft) {
      var r2 = ab.getBoundingClientRect();
      var weg2 = ab.offsetHeight - vh;
      var p2 = weg2 > 0 ? klemm(-r2.top / weg2, 0, 1) : 0;
      var anzahl = abStufen.length;
      var aktiv = Math.min(anzahl - 1, Math.floor(p2 * anzahl * 0.999));
      abStufen.forEach(function (li, idx) { li.classList.toggle('an', idx <= aktiv); });
      if (abFuell) abFuell.style.setProperty('--h', (p2 * 100).toFixed(1) + '%');
      if (abProzent) abProzent.textContent = Math.round(klemm(p2 * 1.04, 0, 1) * 100);
    }
  }

  function anstossen() { if (!laueft) { laueft = true; requestAnimationFrame(rechnen); } }
  addEventListener('scroll', anstossen, { passive: true });
  addEventListener('resize', anstossen);
  addEventListener('load', anstossen);
  rechnen();

  /* ── Sanftes Scrollen (Zusatz, nicht Voraussetzung) ─────── */
  if (!sanft) {
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/lenis@1.1.18/dist/lenis.min.js';
    s.onload = function () {
      if (!window.Lenis) return;
      var lenis = new window.Lenis({ duration: 1.05, smoothWheel: true, touchMultiplier: 1.6 });
      function tick(t) { lenis.raf(t); requestAnimationFrame(tick); }
      requestAnimationFrame(tick);
      lenis.on('scroll', anstossen);
      // Ankerlinks über Lenis führen, damit das Gefühl gleich bleibt
      $$('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
          var id = a.getAttribute('href');
          if (id.length < 2) return;
          var ziel = document.querySelector(id);
          if (!ziel) return;
          e.preventDefault();
          menuZu();
          lenis.scrollTo(ziel, { offset: -parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--navh')) || -68 });
        });
      });
    };
    s.onerror = function () { /* ohne Lenis scrollt die Seite nativ — alles funktioniert */ };
    document.head.appendChild(s);
  }
})();
