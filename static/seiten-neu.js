/* Unterseiten-Heros, Foto & Video, Signet im Startseiten-Hintergrund (Noah, 18.11.2026). Gebaut von start-neu/bauen.py.
   Videos mit data-hand verwaltet nur dieses Skript (main.js lässt sie aus): sie laden erst, wenn sie sichtbar sind,
   und laufen nur, solange ihr Bereich im Bild ist. Unter „Bewegung reduzieren“ steht alles still und vollständig. */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sichtbar = el => !!(el && el.getClientRects().length && getComputedStyle(el).display !== 'none');
  const laden = v => { if (!v.getAttribute('src') && v.dataset.src) { v.src = v.dataset.src; } };
  const spiel = v => { if (ruhig) return; laden(v); const p = v.play(); if (p) p.catch(() => {}); };

  /* ── 1 · Unterseiten-Hero ─────────────────────────────────────────────────────────────────── */
  const hero = $('.hk-neu');
  if (hero) {
    const angehalten = () => !!$('.pause.aus', hero);
    let imBild = true;
    new IntersectionObserver(es => es.forEach(e => {
      imBild = e.isIntersecting;
      $$('video', hero).forEach(v => { if (!imBild) v.pause(); else if (v.closest('.an, .hk-tel, .hk-mobil, .hk-einzel') && sichtbar(v) && !angehalten()) spiel(v); });
    }), { threshold: 0.05 }).observe(hero);
    // Feste Filme (Telefone, Handy-Hintergrund, Einzelfilm) nach dem Laden der Seite holen
    const start = () => $$('.hk-tel video, .hk-mobil video, video.hk-mobil, .hk-einzel video', hero).forEach(v => { if (sichtbar(v)) spiel(v); });
    if (document.readyState === 'complete') start(); else addEventListener('load', () => setTimeout(start, 150), { once: true });

    // Wechsel: Film im Hintergrund (+ Browser bzw. Sucher) nacheinander, Ziffern und Etikett mitziehen
    const lagen = $$('.hk-film .hk-lage', hero);
    if (lagen.length > 1) {
      const fenster = $$('.hk-browser .bs video', hero), knoepfe = $$('.hk-reel-leiste button', hero);
      const etikett = $$('[data-hk-name]', hero), url = $('.hk-browser .bl span', hero), info = $('.hk-sucher .info', hero), tc = $('.hk-sucher .rec b', hero);
      const dauer = +hero.dataset.takt || 7000;
      let i = 0, t0 = performance.now(), wartet = false;
      const zeige = n => {
        i = (n + lagen.length) % lagen.length; t0 = performance.now();
        lagen.forEach((l, k) => l.classList.toggle('an', k === i));
        fenster.forEach((v, k) => v.classList.toggle('an', k === i));
        knoepfe.forEach((b, k) => { b.classList.toggle('an', k === i); b.setAttribute('aria-pressed', k === i); });
        const l = lagen[i];
        etikett.forEach(e => { e.textContent = l.dataset.name; });
        if (url) url.textContent = l.dataset.url || '';
        if (info) info.textContent = `${String(i + 1).padStart(2, '0')} / ${String(lagen.length).padStart(2, '0')}`;
        const v = $('video', l); if (v && imBild && !angehalten()) { v.currentTime = 0; spiel(v); }
        const f = fenster[i]; if (f && imBild && !angehalten() && sichtbar(f)) { f.currentTime = 0; spiel(f); }
        // nächsten Film schon holen, damit der Wechsel ohne schwarzes Bild kommt
        const nv = $('video', lagen[(i + 1) % lagen.length]); if (nv && !ruhig) laden(nv);
        const nf = fenster[(i + 1) % lagen.length]; if (nf && !ruhig && sichtbar(nf)) laden(nf);
      };
      knoepfe.forEach((b, k) => b.addEventListener('click', () => zeige(k)));
      const los = () => {
        zeige(0);
        if (ruhig) return;
        const tick = now => {
          if (!imBild || angehalten()) { t0 = now - ((now - t0) % dauer); }
          const z = Math.min(1, (now - t0) / dauer);
          const b = knoepfe[i]; if (b) b.style.setProperty('--z', z.toFixed(3));
          if (tc) { const s = (now - t0) / 1000 + i * (dauer / 1000); const f = Math.floor((s % 1) * 25);
            tc.textContent = `00:${String(Math.floor(s / 60)).padStart(2, '0')}:${String(Math.floor(s % 60)).padStart(2, '0')}:${String(f).padStart(2, '0')}`; }
          if (z >= 1 && imBild && !angehalten()) zeige(i + 1);
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      };
      if (document.readyState === 'complete') los(); else addEventListener('load', () => setTimeout(los, 150), { once: true });
      if (!ruhig && matchMedia('(hover:hover)').matches) {
        const br = $('.hk-browser', hero);
        if (br) hero.addEventListener('pointermove', e => { const r = hero.getBoundingClientRect();
          br.style.setProperty('--mx', ((e.clientX - r.left) / r.width - .5).toFixed(3)); br.style.setProperty('--my', ((e.clientY - r.top) / r.height - .5).toFixed(3)); });
      }
    }

    // Suche: Suchbegriff tippt sich, darunter steht der Kunde auf Platz 1
    const suche = $('.hk-suche', hero);
    if (suche) {
      const eintraege = JSON.parse(suche.dataset.eintraege || '[]'), feld = $('.sf b', suche), li = $$('li', suche);
      const name = $('li:first-child b', suche);
      let n = 0;
      const runde = async () => {
        const e = eintraege[n % eintraege.length]; n++;
        li.forEach(x => x.classList.remove('an'));
        if (ruhig) { feld.textContent = e.wort; name.textContent = e.name; li.forEach(x => x.classList.add('an')); return; }
        feld.textContent = '';
        for (const z of e.wort) { feld.textContent += z; await new Promise(r => setTimeout(r, 70 + Math.random() * 60)); }
        name.textContent = e.name;
        for (const x of li) { await new Promise(r => setTimeout(r, 260)); x.classList.add('an'); }
        await new Promise(r => setTimeout(r, 3400));
        if (!angehalten()) runde(); else setTimeout(runde, 2000);
      };
      if (eintraege.length) runde();
    }
  }

  /* ── 2 · Foto & Video: Galerie mit Filter, laufenden Filmen und Lichtkasten ─────────────────── */
  const raster = $('.fv-raster');
  if (raster) {
    const karten = $$('.fv-k', raster), knoepfe = $$('.fv-filter button');
    let filter = 'alle';
    raster.classList.add('js');
    const spalten = () => innerWidth >= 1100 ? 4 : innerWidth >= 700 ? 3 : 2;
    const legen = () => {
      const n = spalten(), gap = innerWidth >= 700 ? 14 : 10, w = raster.clientWidth, sw = (w - gap * (n - 1)) / n, hoehe = Array(n).fill(0);
      karten.forEach(k => {
        const an = filter === 'alle' || k.dataset.g.split(' ').includes(filter);
        k.classList.toggle('weg', !an);
        if (!an) return;
        const r = +k.style.getPropertyValue('--r') || 1.5, h = Math.round(sw / r);
        let s = 0; for (let j = 1; j < n; j++) if (hoehe[j] < hoehe[s] - 1) s = j;
        k.style.width = sw + 'px'; k.style.height = h + 'px';
        k.style.transform = `translate(${Math.round(s * (sw + gap))}px,${Math.round(hoehe[s])}px)`;
        hoehe[s] += h + gap;
      });
      raster.style.height = Math.max(...hoehe) - gap + 'px';
    };
    legen();
    let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(legen, 120); });
    // Karten erscheinen gestaffelt, sobald sie ins Bild kommen
    const ioK = new IntersectionObserver(es => es.forEach((e, j) => { if (!e.isIntersecting) return; ioK.unobserve(e.target);
      setTimeout(() => e.target.classList.add('da'), ruhig ? 0 : (j % 6) * 70); }), { rootMargin: '0px 0px -6% 0px' });
    karten.forEach(k => ioK.observe(k));
    knoepfe.forEach(b => b.addEventListener('click', () => {
      filter = b.dataset.f; knoepfe.forEach(x => x.setAttribute('aria-pressed', x === b));
      legen(); karten.forEach(k => { if (!k.classList.contains('weg')) k.classList.add('da'); });
      $$('video', raster).forEach(v => { if (v.closest('.weg')) v.pause(); });
    }));
    // Filme: am Rechner beim Drüberfahren, am Handy sobald sie zu zwei Dritteln im Bild sind
    const filme = $$('.fv-k.ist-film', raster);
    if (matchMedia('(hover:hover)').matches) filme.forEach(k => { const v = $('video', k);
      k.addEventListener('pointerenter', () => spiel(v)); k.addEventListener('pointerleave', () => v.pause());
      k.addEventListener('focusin', () => spiel(v)); k.addEventListener('focusout', () => v.pause()); });
    else { const ioF = new IntersectionObserver(es => es.forEach(e => { const v = $('video', e.target); e.isIntersecting ? spiel(v) : v.pause(); }), { threshold: 0.66 });
      filme.forEach(k => ioF.observe(k)); }
    // Zeiger-Blase „Ansehen“ / „Abspielen“
    const blase = $('.fv-cursor');
    if (blase && matchMedia('(hover:hover) and (pointer:fine)').matches && !ruhig) {
      raster.addEventListener('pointermove', e => { blase.style.setProperty('--x', e.clientX + 'px'); blase.style.setProperty('--y', e.clientY + 'px'); });
      karten.forEach(k => { k.addEventListener('pointerenter', () => { blase.textContent = k.classList.contains('ist-film') ? 'Abspielen' : 'Ansehen'; blase.style.setProperty('--s', 1); });
        k.addEventListener('pointerleave', () => blase.style.setProperty('--s', 0)); });
    }
    // Lichtkasten
    const lk = $('.fv-licht'), buehne = lk && $('.lk-buehne', lk);
    if (lk) {
      let pos = 0;
      const liste = () => karten.filter(k => !k.classList.contains('weg'));
      const zeige = (k, von) => {
        const l = liste(); pos = l.indexOf(k);
        const alt = $('img, video', buehne); if (alt) alt.remove();
        let m;
        if (k.classList.contains('ist-film')) { const q = $('video', k); m = document.createElement('video');
          Object.assign(m, { muted: true, loop: true, playsInline: true, autoplay: !ruhig, controls: true, poster: q.poster || q.dataset.poster || '' });
          m.src = q.dataset.gross || q.dataset.src; }
        else { const q = $('img', k); m = new Image(); m.src = q.dataset.gross; m.alt = q.alt; }
        buehne.append(m);
        $('.lk-fuss b', lk).textContent = $('figcaption b', k).textContent;
        $('.lk-fuss span', lk).textContent = $('figcaption span', k).textContent;
        $('.lk-zahl', lk).textContent = `${pos + 1} / ${l.length}`;
        if (von && !ruhig) { const r = von.getBoundingClientRect();
          requestAnimationFrame(() => { const z = m.getBoundingClientRect(); if (!z.width) return;
            m.animate([{ transform: `translate(${r.left + r.width / 2 - (z.left + z.width / 2)}px,${r.top + r.height / 2 - (z.top + z.height / 2)}px) scale(${r.width / z.width})`, opacity: .6 }, { transform: 'none', opacity: 1 }],
              { duration: 420, easing: 'cubic-bezier(.2,.7,.2,1)' }); }); }
      };
      const weiter = d => { const l = liste(); zeige(l[(pos + d + l.length) % l.length]); };
      karten.forEach(k => $('.fv-auf', k).addEventListener('click', () => { lk.showModal(); zeige(k, k); }));
      $('.lk-zu', lk).addEventListener('click', () => lk.close());
      $('.lk-vor', lk).addEventListener('click', () => weiter(1));
      $('.lk-zur', lk).addEventListener('click', () => weiter(-1));
      lk.addEventListener('keydown', e => { if (e.key === 'ArrowRight') weiter(1); if (e.key === 'ArrowLeft') weiter(-1); });
      lk.addEventListener('click', e => { if (e.target === lk || e.target === buehne) lk.close(); });
      lk.addEventListener('close', () => { const m = $('video', buehne); if (m) m.pause(); });
      let sx = null; buehne.addEventListener('pointerdown', e => { sx = e.clientX; });
      buehne.addEventListener('pointerup', e => { if (sx !== null && Math.abs(e.clientX - sx) > 50) weiter(e.clientX < sx ? 1 : -1); sx = null; });
    }
  }
  // Kontaktabzug: rote Markierungen zeichnen sich, sobald der Streifen im Bild ist; Scrollen schiebt den Streifen mit
  const streifen = $('.kb-streifen');
  if (streifen) {
    new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) streifen.classList.add('sicht'); }), { threshold: .3 }).observe(streifen);
    const spur = $('.kb-spur', streifen), anim = spur.getAnimations && spur.getAnimations()[0];
    if (anim && !ruhig) { let y = scrollY, v = 1;
      addEventListener('scroll', () => { const d = scrollY - y; y = scrollY; v = Math.max(-6, Math.min(8, 1 + d * .12)); anim.updatePlaybackRate(v); }, { passive: true });
      setInterval(() => { v += (1 - v) * .25; anim.updatePlaybackRate(v); }, 120); }
  }

  /* ── 3 · Startseite: Signet wächst mit dem Scrollen ──────────────────────────────────────── */
  const buehnen = $$('.sg-buehne');
  if (buehnen.length && !ruhig) {
    const lauf = () => {
      const vh = innerHeight;
      buehnen.forEach(b => {
        const s = b.closest('section').getBoundingClientRect();
        if (s.bottom < -100 || s.top > vh + 100) return;
        const p = Math.max(0, Math.min(1, (vh - s.top) / (vh + s.height * .45)));   // 0 = Sektion kommt unten rein
        const balken = $$('.sg-b', b);
        if (b.classList.contains('sg-wachsen')) {
          balken.forEach((g, i) => { const q = Math.max(0, Math.min(1, (p - .08 - i * .1) / .42)); const e = 1 - Math.pow(1 - q, 3);
            g.style.setProperty('--sy', (0.08 + .92 * e).toFixed(4)); g.style.setProperty('--py', ((1 - p) * (40 + i * 34)).toFixed(1)); });
          const gl = $('#sg-glanz', b); if (gl) gl.setAttribute('gradientTransform', `translate(${(-1.2 + p * 2.4).toFixed(3)} 0)`);
        } else {
          b.style.setProperty('--zug', Math.max(0, 1 - p / .5).toFixed(4));
          const f = $('.sg-fuell-rect', b); if (f) f.setAttribute('y', (91 - 95 * Math.max(0, Math.min(1, (p - .15) / .5))).toFixed(2));
          balken.forEach((g, i) => g.style.setProperty('--py', ((.5 - p) * (i - 1) * 60).toFixed(1)));
        }
      });
    };
    let warte = false;
    addEventListener('scroll', () => { if (warte) return; warte = true; requestAnimationFrame(() => { warte = false; lauf(); }); }, { passive: true });
    addEventListener('resize', lauf); lauf();
    // Zeiger-Glut über dem wachsenden Signet
    $$('.sg-wachsen').forEach(b => { const sek = b.closest('section'), lg = $('#sg-zeiger', b); if (!lg || !matchMedia('(hover:hover)').matches) return;
      sek.addEventListener('pointermove', e => { const r = b.getBoundingClientRect(); lg.setAttribute('cx', ((e.clientX - r.left) / r.width).toFixed(3)); lg.setAttribute('cy', ((e.clientY - r.top) / r.height).toFixed(3)); lg.setAttribute('r', '.55'); });
      sek.addEventListener('pointerleave', () => lg.setAttribute('r', '0')); });
  }
})();
