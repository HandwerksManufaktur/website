/* Pilot „roter Faden“ (start-neu/roter_faden.py): die Bronze-Linie läuft von der ersten bis zur letzten Kapitelmarke.
   Ihre Spitze steht immer bei 62 % der Fensterhöhe; was darüber liegt, ist gezeichnet, jede Marke darüber leuchtet.
   Ohne JS oder mit reduzierter Bewegung steht die Linie fertig da. */
(() => {
  const strecke = document.querySelector('.rf-strecke');
  if (!strecke) return;
  const spur = strecke.querySelector('.rf-spur');
  const marken = [...strecke.querySelectorAll('.rf-marke')];
  if (!spur || marken.length < 2) return;
  const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let oben = 0, laenge = 1, lagen = [], streckeOben = 0, dran = false;

  function messen() {
    const r = strecke.getBoundingClientRect();
    streckeOben = r.top + scrollY;
    const punkte = marken.map(m => {
      const b = m.getBoundingClientRect();
      return { x: b.left + b.width / 2 - r.left, y: b.top + b.height / 2 - r.top };
    });
    oben = punkte[0].y;
    laenge = Math.max(1, punkte[punkte.length - 1].y - oben);
    lagen = punkte.map(p => p.y - oben);
    strecke.style.setProperty('--rf-x', punkte[0].x + 'px');
    spur.style.top = oben + 'px';
    spur.style.height = laenge + 'px';
    zeichnen();
  }

  function zeichnen() {
    dran = false;
    const spitze = ruhig ? laenge : scrollY + innerHeight * 0.62 - streckeOben - oben;
    const p = Math.max(0, Math.min(1, spitze / laenge));
    spur.style.setProperty('--rf-p', p.toFixed(4));
    spur.style.setProperty('--rf-y', (p * laenge).toFixed(1) + 'px');
    spur.style.setProperty('--rf-o', p > 0 && p < 1 ? '1' : '0');
    marken.forEach((m, i) => m.classList.toggle('erreicht', spitze >= lagen[i] - 1));
  }

  const anstossen = () => { if (!dran) { dran = true; requestAnimationFrame(zeichnen); } };
  addEventListener('scroll', anstossen, { passive: true });
  addEventListener('resize', () => requestAnimationFrame(messen));
  // Bilder, Schrift und die Stimmen-Bahn ändern Höhen nach dem Laden: neu messen, sobald die Strecke wächst oder schrumpft
  if ('ResizeObserver' in window) new ResizeObserver(() => requestAnimationFrame(messen)).observe(strecke);
  addEventListener('load', messen);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(messen);
  messen();
})();
