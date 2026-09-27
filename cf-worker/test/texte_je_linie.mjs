// Prüft: bei Recruiting + Leadgen bekommt jeder Performance-Task nur seine eigenen Texte.
// Aufruf: node test/texte_je_linie.mjs  (bündelt src/clickup.js vorher mit esbuild)
import { execSync } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const dir = mkdtempSync(join(tmpdir(), 'cu-'));
const out = join(dir, 'cu.mjs');
execSync(`npx esbuild src/clickup.js --bundle --format=esm --outfile=${out} --log-level=warning`, { cwd: new URL('..', import.meta.url).pathname });
const { buildDescription } = await import(out);
const fd = {'Warum entscheiden sich Kunden für euch?':'USP','Was macht euch als Arbeitgeber besonders?':'AG','Betriebsvorteile':'V','Einsatzgebiet / Radius':'E','Dienstleistung / Produkt':'D','Durchschnittlicher Auftragswert':'A','Einzugsgebiet / Radius':'Z','Erfolgsziel nach der Laufzeit':'Ziel','Wer kontaktiert Leads?':'W','Wunschtermin Videodreh':'Dreh'};
const r = buildDescription(fd,'x','Recruiting'), l = buildDescription(fd,'x','Leadgen'), a = buildDescription(fd,'x');
const hat = (t,k) => t.includes('**'+k+':**');
const proben = [
  ['Recruiting hat Arbeitgeber-Text', hat(r,'Was macht euch als Arbeitgeber besonders?')],
  ['Recruiting ohne Auftragswert', !hat(r,'Durchschnittlicher Auftragswert')],
  ['Recruiting ohne Erfolgsziel', !hat(r,'Erfolgsziel nach der Laufzeit')],
  ['Recruiting hat gemeinsame Texte', hat(r,'Warum entscheiden sich Kunden für euch?') && hat(r,'Wunschtermin Videodreh')],
  ['Leadgen hat Auftragswert', hat(l,'Durchschnittlicher Auftragswert')],
  ['Leadgen ohne Arbeitgeber-Text', !hat(l,'Was macht euch als Arbeitgeber besonders?')],
  ['Leadgen ohne Betriebsvorteile', !hat(l,'Betriebsvorteile')],
  ['Leadgen hat gemeinsame Texte', hat(l,'Warum entscheiden sich Kunden für euch?') && hat(l,'Wunschtermin Videodreh')],
  ['Ohne Linie (Kundendatenbank) alles', hat(a,'Betriebsvorteile') && hat(a,'Durchschnittlicher Auftragswert')],
];
let ok = true;
for (const [n, v] of proben) { console.log(v ? '✅' : '🔴', n); ok = ok && v; }
process.exit(ok ? 0 : 1);
