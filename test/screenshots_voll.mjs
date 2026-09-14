/* Prueft die Referenz-Screenshots im Showcase auf LOECHER.
   Anlass (Noah, 14.09.2026): "wenn ich auf die erste Referenz drueber scroll, dann
   erscheint mir da die alte" — nachher-wohner.jpg war am 28.07. aufgenommen worden,
   OHNE dass die Reveal-Animationen der Kundenseite ausgeloest hatten. 22 % der
   Bildhoehe waren eine durchgehend weisse Flaeche; beim Hover scrollt das Bild durch,
   und genau diese Luecke sieht man.
   Lauf:  node test/screenshots_voll.mjs            (Server auf 8811 muss laufen)
          node test/screenshots_voll.mjs --selbsttest
   Der Selbsttest baut ein Loch ein und prueft, ob es gefunden wird. */
import { chromium } from '/Users/noahs/Documents/CEO-GPT/system/apps/audit/node_modules/playwright/index.mjs';
import { readdirSync } from 'node:fs';

const BASIS = process.env.BASIS || 'http://localhost:8811';
const ORDNER = new URL('../assets/work/', import.meta.url).pathname;
const GRENZE = 0.12;           // hoechstens 12 % der Hoehe am Stueck fast weiss

const messen = async (page, url, kunstLoch = 0) => page.evaluate(async ([u, loch]) => {
  const bild = new Image(); bild.crossOrigin = 'anonymous'; bild.src = u;
  await bild.decode();
  const c = document.createElement('canvas');
  c.width = 60; c.height = Math.min(bild.naturalHeight, 4000);
  const g = c.getContext('2d');
  g.drawImage(bild, 0, 0, c.width, c.height);
  if (loch) { g.fillStyle = '#fff'; g.fillRect(0, 100, c.width, Math.round(c.height * loch)); }
  const d = g.getImageData(0, 0, c.width, c.height).data;
  let lauf = 0, best = 0;
  for (let y = 0; y < c.height; y++) {
    let summe = 0;
    for (let x = 0; x < c.width; x++) { const i = (y * c.width + x) * 4; summe += (d[i] + d[i+1] + d[i+2]) / 3; }
    if (summe / c.width > 247) { lauf++; best = Math.max(best, lauf); } else lauf = 0;
  }
  return { hoehe: bild.naturalHeight, anteil: best / c.height };
}, [url, kunstLoch]);

const b = await chromium.launch();
const p = await b.newPage();
await p.goto(BASIS + '/', { waitUntil: 'domcontentloaded' });
const bilder = readdirSync(ORDNER).filter(f => /^nachher-.*\.(jpg|png)$/.test(f));
const selbsttest = process.argv.includes('--selbsttest');
let schlecht = [];

for (const f of bilder) {
  const { hoehe, anteil } = await messen(p, `${BASIS}/assets/work/${f}`);
  if (anteil > GRENZE) schlecht.push(`${f} — ${Math.round(anteil*100)} % weisse Strecke am Stueck (Hoehe ${hoehe})`);
}
if (selbsttest) {
  const { anteil } = await messen(p, `${BASIS}/assets/work/${bilder[0]}`, 0.3);
  console.log('Selbsttest — eingebautes Loch gefunden:', anteil > GRENZE ? '✅' : '❌ NICHT GEFUNDEN');
  await b.close();
  process.exit(anteil > GRENZE ? 0 : 1);
}
await b.close();
if (schlecht.length) {
  console.error('🔴 Screenshots mit Loch (Reveals waren beim Aufnehmen nicht ausgeloest):');
  schlecht.forEach(s => console.error('   ' + s));
  process.exit(1);
}
console.log(`✅ ${bilder.length} Referenz-Screenshots ohne Loch (keine weisse Strecke ueber ${GRENZE*100} % der Hoehe).`);
