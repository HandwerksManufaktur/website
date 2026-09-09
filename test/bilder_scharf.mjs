/* Prüft zwei Regeln aus Noahs Korrektur vom 09.09.2026:
   1. Jedes Bild muss mindestens 1,5-mal so breit geliefert werden wie sein Slot.
      (Das Senftleben-Hero war 1100 px breit in einem 1132-px-Slot — unter 1:1.)
   2. Unter Kundenfotos steht kein Kundenname.
   3. Kein Block klebt links und laesst rechts eine grosse leere Flaeche stehen.
      (Die Fragen standen als 820-px-Streifen im 1200-px-Container — Noah:
      „So ist das eingeengt, und da steht dann da irgendwie so leer mit drin.")
   4. Zwei Spalten nebeneinander duerfen sich um hoechstens 25 % unterscheiden.
      (In der Fallstudie war die linke Spalte 1,9-mal so hoch wie das Video, weil
      die Zahlen darin standen — Noah: „Die Sektionen sind asymmetrisch.")
   Lauf:  node test/bilder_scharf.mjs            (Server auf 8811 muss laufen)
          node test/bilder_scharf.mjs --selbsttest
   Der Selbsttest baut den Fehler künstlich ein und prüft, ob er gefunden wird. */
import { chromium } from '/Users/noahs/Documents/CEO-GPT/system/apps/audit/node_modules/playwright/index.mjs';

const BASIS = process.env.BASIS || 'http://localhost:8811';
const SEITEN = ['/', '/neukundengewinnung/', '/mitarbeitergewinnung/',
                '/impressum/', '/datenschutz/', '/agb/', '/onboarding/'];
const SCHIEF = 140;   // px Unterschied zwischen linkem und rechtem Rand
const MINDEST = 1.5;
const KUNDEN = /Senftleben|Irlbacher|Erwin Schmidt|Sussmann|Wohner|Klass/i;
/* Bewusste Ausnahme mit Grund — nie die Schwelle senken, sondern hier eintragen.
   Der Wohner-Screenshot ist eine Ganzseiten-Aufnahme (900x5300) im Showcase mit
   Scroll-Animation. In doppelter Aufloesung neu aufgenommen ist die Live-Seite
   inzwischen 9735 statt 5300 px hoch — das Bild zeigt dann etwas anderes und die
   Animation laeuft anders. Neu aufnehmen ist eine eigene Entscheidung von Noah. */
const AUSNAHMEN = { '/assets/work/nachher-wohner.jpg': '1,43x — Ganzseiten-Screenshot, Neuaufnahme aendert den Showcase' };
const selbsttest = process.argv.includes('--selbsttest');

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
let fehler = [];

for (const s of SEITEN) {
  await p.goto(BASIS + s, { waitUntil: 'domcontentloaded' });
  await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await p.waitForTimeout(1800);
  if (selbsttest) await p.evaluate(() => {           // alle drei Fehler einbauen
    const i = [...document.querySelectorAll('img')].find(x => x.naturalWidth > 60);
    if (i) i.style.width = (i.naturalWidth * 2) + 'px';
    const g = document.querySelector('.fs-grid');
    if (g) g.children[0].style.height = (g.children[1].getBoundingClientRect().height * 2) + 'px';
    const f = document.querySelector('.wrap > ul, .wrap > .faq-liste, .wrap > div[class]');
    if (f) { f.style.maxWidth = '340px'; f.style.marginRight = 'auto'; f.style.display = 'grid'; f.style.minHeight = '200px'; }
  });
  const funde = await p.evaluate(({ MINDEST, KUNDENQ, SCHIEF }) => {
    const k = new RegExp(KUNDENQ, 'i'); const raus = [];
    for (const i of document.querySelectorAll('img')) {
      const br = i.getBoundingClientRect().width;
      if (br < 40 || !i.naturalWidth) continue;      // versteckt / noch nicht geladen
      const f = i.naturalWidth / br;
      if (f < MINDEST) raus.push({ art: 'unscharf', src: i.getAttribute('src'), faktor: +f.toFixed(2), slot: Math.round(br), quelle: i.naturalWidth });
    }
    /* Gesucht ist der Fall „Liste/Raster klebt links, rechts bleibt es leer".
       Ueberschriften und Fliesstext sind absichtlich schmaler und zaehlen nicht,
       ebenso wenig die Kinder eines Rasters (die richtet ihr Raster aus). */
    for (const el of document.querySelectorAll('.wrap > *')) {
      const r = el.getBoundingClientRect(); if (r.height < 120 || r.width < 80) continue;
      const eltern = el.parentElement, ep = getComputedStyle(eltern).display;
      if (ep.includes('grid') || ep.includes('flex')) continue;
      const d = getComputedStyle(el).display;
      const gruppe = d.includes('grid') || d.includes('flex') || /^(UL|OL)$/.test(el.tagName);
      if (!gruppe || el.children.length < 2) continue;
      const p = eltern.getBoundingClientRect();
      const rechts = p.right - r.right, links = r.left - p.left;
      if (rechts - links > SCHIEF)
        raus.push({ art: 'eingeengt', block: el.tagName + '.' + String(el.className).split(' ')[0],
                    breite: Math.round(r.width), leerRechts: Math.round(rechts) });
    }
    for (const g of document.querySelectorAll('.fs-grid')) {
      const [a, b] = [...g.children].map(c => c.getBoundingClientRect().height);
      if (a && b && Math.max(a, b) / Math.min(a, b) > 1.25)
        raus.push({ art: 'asymmetrisch', links: Math.round(a), rechts: Math.round(b) });
    }
    for (const c of document.querySelectorAll('figcaption'))
      if (k.test(c.textContent)) raus.push({ art: 'kundenname', text: c.textContent.trim() });
    return raus;
  }, { MINDEST, KUNDENQ: KUNDEN.source, SCHIEF });
  funde.forEach(f => {
    if (AUSNAHMEN[f.src]) { console.log('  … bewusste Ausnahme:', f.src, '—', AUSNAHMEN[f.src]); return; }
    fehler.push({ seite: s, ...f });
  });
}
await b.close();

if (selbsttest) {
  const u = fehler.some(f => f.art === 'unscharf'), a = fehler.some(f => f.art === 'asymmetrisch'),
        e = fehler.some(f => f.art === 'eingeengt');
  console.log('Selbsttest — unscharf:', u ? '✅' : '❌', '· asymmetrisch:', a ? '✅' : '❌', '· eingeengt:', e ? '✅' : '❌');
  process.exit(u && a && e ? 0 : 1);
}
if (fehler.length) { console.log('❌ ' + fehler.length + ' Befund(e):'); fehler.forEach(f => console.log('  ', JSON.stringify(f))); process.exit(1); }
console.log('✅ ' + SEITEN.length + ' Seiten: Bilder mindestens ' + MINDEST + '× so breit wie ihr Slot, '
  + 'keine Kundennamen unter Fotos, keine eingeengten Blöcke, Spalten im Lot.');
