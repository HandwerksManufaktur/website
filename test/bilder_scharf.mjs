/* Prüft zwei Regeln aus Noahs Korrektur vom 09.09.2026:
   1. Jedes Bild muss mindestens 1,5-mal so breit geliefert werden wie sein Slot.
      (Das Senftleben-Hero war 1100 px breit in einem 1132-px-Slot — unter 1:1.)
   2. Unter Kundenfotos steht kein Kundenname.
   Lauf:  node test/bilder_scharf.mjs            (Server auf 8811 muss laufen)
          node test/bilder_scharf.mjs --selbsttest
   Der Selbsttest baut den Fehler künstlich ein und prüft, ob er gefunden wird. */
import { chromium } from '/Users/noahs/Documents/CEO-GPT/system/apps/audit/node_modules/playwright/index.mjs';

const BASIS = process.env.BASIS || 'http://localhost:8811';
const SEITEN = ['/', '/neukundengewinnung/', '/mitarbeitergewinnung/'];
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
  if (selbsttest) await p.evaluate(() => {           // Fehler einbauen
    const i = document.querySelector('img'); i.style.width = (i.naturalWidth * 2) + 'px';
  });
  const funde = await p.evaluate(({ MINDEST, KUNDENQ }) => {
    const k = new RegExp(KUNDENQ, 'i'); const raus = [];
    for (const i of document.querySelectorAll('img')) {
      const br = i.getBoundingClientRect().width;
      if (br < 40 || !i.naturalWidth) continue;      // versteckt / noch nicht geladen
      const f = i.naturalWidth / br;
      if (f < MINDEST) raus.push({ art: 'unscharf', src: i.getAttribute('src'), faktor: +f.toFixed(2), slot: Math.round(br), quelle: i.naturalWidth });
    }
    for (const c of document.querySelectorAll('figcaption'))
      if (k.test(c.textContent)) raus.push({ art: 'kundenname', text: c.textContent.trim() });
    return raus;
  }, { MINDEST, KUNDENQ: KUNDEN.source });
  funde.forEach(f => {
    if (AUSNAHMEN[f.src]) { console.log('  … bewusste Ausnahme:', f.src, '—', AUSNAHMEN[f.src]); return; }
    fehler.push({ seite: s, ...f });
  });
}
await b.close();

if (selbsttest) {
  const gefunden = fehler.some(f => f.art === 'unscharf');
  console.log(gefunden ? '✅ Selbsttest: der eingebaute Fehler wird gefunden.'
                       : '❌ Selbsttest: der eingebaute Fehler blieb unentdeckt — die Prüfung taugt nichts.');
  process.exit(gefunden ? 0 : 1);
}
if (fehler.length) { console.log('❌ ' + fehler.length + ' Befund(e):'); fehler.forEach(f => console.log('  ', JSON.stringify(f))); process.exit(1); }
console.log('✅ Alle Bilder mindestens ' + MINDEST + '× so breit wie ihr Slot, keine Kundennamen unter Fotos.');
