// ============================================================
// Onboarding-Eingang — Formular → Rohsatz in der eigenen D1 (seit 10.11.2026)
// ------------------------------------------------------------
// Noah, 10.11.2026: „Es darf nicht mehr mit ClickUp oder Sonstigem gehen, das ist verboten.“
// Früher legte dieser Worker Kundendatenbank- und Projekt-Tasks bei einem Fremddienst an (clickup.js, entfernt).
// Jetzt: JEDE Formular-Abgabe wird als Rohsatz in der D1 `onboarding-eingang` (Binding EINGANG_DB,
// Tabelle onboarding_eingang, Schema ../schema.sql) gespeichert — Muster cold-mail-signale: der Worker
// hält nur roh fest, der Mac-Abholer system/scripts/onboarding_eingang.py (CEO-GPT) macht daraus Kunde
// + Projekt(e) + Schritte in der Informationsgrundlage (grundlage_schreiben.kunde_anlegen/projekt_anlegen).
//
// Neben den Rohdaten (form_data im Wortlaut) steht `abgeleitet`: Stammdaten und je Projekt Linie, Name,
// Typ und Beschreibung — genau die Regeln, die vorher die Tasks befüllten (Texte je Linie getrennt,
// Stellen als Text, Leistungen als Text, nie als Schritte).
// ============================================================

export const EINGANG_SCHEMA = `CREATE TABLE IF NOT EXISTS onboarding_eingang (
  id TEXT PRIMARY KEY,
  eingegangen_am TEXT NOT NULL,
  firma TEXT NOT NULL,
  service_type TEXT NOT NULL,
  drive_link TEXT,
  root_folder_id TEXT,
  leistungen TEXT,
  form_data TEXT NOT NULL,
  missing TEXT,
  abgeleitet TEXT NOT NULL,
  client_v INTEGER
)`;

// Sucht ein Form-Feld unter mehreren möglichen Keys (Fuzzy-Matching)
// Formular-Keys von Unterfeldern kommen eingerückt an ("  Link zur alten Website"),
// deshalb wird jeder Key auch getrimmt gesucht — sonst greift stillschweigend der Fallback.
function pick(formData, ...keys) {
  for (const k of keys) {
    const v = formData[k];
    if (v !== undefined && v !== null && v !== '') return v;
    for (const realKey of Object.keys(formData)) {
      if (realKey.trim() === k) {
        const rv = formData[realKey];
        if (rv !== undefined && rv !== null && rv !== '') return rv;
      }
    }
  }
  return null;
}

// URL-Felder: nur echte Adressen übernehmen — z.B. das "Ja" aus einem Ja/Nein-Toggle ist keine Website.
function asUrl(raw) {
  if (!raw) return null;
  const v = String(raw).trim();
  if (!/^https?:\/\/\S+\.\S+/i.test(v)) {
    if (/^(www\.|[\w-]+\.[a-z]{2,})/i.test(v) && !/\s/.test(v)) return 'https://' + v.replace(/^\/+/, '');
    return null;
  }
  return v;
}

// Long-Text-Antworten in eine Description packen
// Stellen aus den Section-Markern lesen ("── STELLE 1 ──" gefolgt von den Feldern).
// Bewusst NICHT über feste Feldnamen: Das Formular sendet die Stellen-Felder eingerückt
// und ohne "Stelle N - "-Präfix ("  Gehaltsspanne brutto"), Mehrfach-Stellen zusätzlich
// mit "(2)"-Suffix. Über die Sections bleibt das unabhängig von den Feldnamen korrekt.
function extractStellen(formData) {
  const stellen = [];
  let current = null;
  for (const [rawKey, value] of Object.entries(formData)) {
    const sec = /^──\s*(.+?)\s*──$/.exec(rawKey);
    if (sec) {
      if (current && Object.keys(current).length) stellen.push(current);
      current = /^STELLE\b/i.test(sec[1]) ? {} : null;
      continue;
    }
    // Bei mehreren Stellen hängt das Formular " (2)", " (3)" … an doppelte Feldnamen
    // — für die Anzeige wieder abstreifen, sonst heißt es "Stellenbezeichnung (2)".
    if (current && value) current[rawKey.trim().replace(/\s*\(\d+\)$/, '')] = value;
  }
  if (current && Object.keys(current).length) stellen.push(current);
  return stellen;
}

function buildStellenText(formData) {
  const stellen = extractStellen(formData);
  if (!stellen.length) return '';
  return stellen.map((felder, i) => {
    const bez = felder['Stellenbezeichnung'] || `Stelle ${i + 1}`;
    const zeilen = Object.entries(felder)
      .filter(([k]) => k !== 'Stellenbezeichnung')
      .map(([k, v]) => `\n${k}: ${v}`);
    return `\n\n**🎯 Stelle ${i + 1}: ${bez}**${zeilen.join('')}`;
  }).join('');
}

// Welche Texte nur zu EINER Performance-Linie gehören. Bei Recruiting + Leadgen bekommt jeder
// Projekt nur seine eigenen (Noah, 27.09.2026: „trenn die Texte je Projekt“ — vorher standen die
// Arbeitgeber-Vorteile auch im Leadgen-Projekt und die Auftragswerte im Recruiting-Projekt).
// Kunde und Website-Projekt bekommen weiter alles (linie leer).
const NUR_RECRUITING = new Set([
  'Was macht euch als Arbeitgeber besonders?', 'Betriebsvorteile', 'Einsatzgebiet / Radius',
]);
const NUR_LEADGEN = new Set([
  'Dienstleistung / Produkt', 'Durchschnittlicher Auftragswert', 'Einzugsgebiet / Radius',
  'Aktuelle Auslastung Badsanierung / Monat', 'Aktuelle Auslastung Wärmepumpen / Monat',
  'Erfolgsziel nach der Laufzeit', 'Wer kontaktiert Leads?',
]);
export function gehoertZuLinie(key, linie) {
  if (linie === 'Recruiting') return !NUR_LEADGEN.has(key);
  if (linie === 'Leadgen')    return !NUR_RECRUITING.has(key);
  return true;
}

export function buildDescription(formData, driveLink, linie) {
  const longTextKeys = [
    'Was macht ihr genau? (2–3 Sätze)',
    'Was macht ihr genau?',
    'Was macht euch besonders?',
    'Konkurrenten mit guter Website?',
    'Noch etwas das wir wissen sollten?',
    'Warum entscheiden sich Kunden für euch?',
    'Was macht euch als Arbeitgeber besonders?',
    'Erfolgsziel nach der Laufzeit',
    'Betriebsvorteile',
    'Einsatzgebiet / Radius',
    'Personen vor der Kamera',
    'Bevorzugtes Datum & Uhrzeit für Videodreh',
    'Wunschtermin Videodreh',
    'Abgebildete Personen (Einwilligung)',
    'Unterschriebene Einwilligungen hochgeladen',
    'Öffnungszeiten',
    'Aktuelle Auslastung Badsanierung / Monat',
    'Aktuelle Auslastung Wärmepumpen / Monat',
    'Durchschnittlicher Auftragswert',
    'Einzugsgebiet / Radius',
    'Wer kontaktiert Leads?',
    'Dienstleistung / Produkt',
    'Wann und was wurde gemacht?',
  ];
  const parts = [];
  for (const k of longTextKeys) {
    if (!gehoertZuLinie(k, linie)) continue;
    const v = formData[k];
    if (v) parts.push(`**${k}:**\n${v}`);
  }
  if (driveLink) parts.push(`---\n📁 [Drive-Ordner](${driveLink})`);
  return parts.join('\n\n');
}

// Leistungen + Stichpunkte als Textblock für die Projekt-Beschreibung (statt je eine Unteraufgabe).
export function leistungenAlsText(leistungen, formData) {
  if (!Array.isArray(leistungen)) return '';
  const zeilen = [];
  for (const l of leistungen) {
    if (!l) continue;
    const st = pick(formData, `${l} - Stichpunkte`, `Stichpunkte ${l}`) || '';
    zeilen.push(`**${l}**` + (st ? `\n${st}` : ''));
  }
  return zeilen.length ? `\n\n---\n**Leistungen:**\n\n${zeilen.join('\n\n')}` : '';
}

// Telefon einheitlich international (+49…), wie in der Kundenakte der Grundlage.
function normalizePhone(raw) {
  if (!raw) return null;
  let p = String(raw).replace(/[\s\/\-().]/g, '');
  if (p.startsWith('00')) p = '+' + p.slice(2);
  else if (p.startsWith('0')) p = '+49' + p.slice(1);
  return p;
}

// Stammdaten + Projekte aus einer Abgabe ableiten (reine Funktion, ohne Netz — testbar)
export function eingangAbleiten({ firmaName, serviceType, formData = {}, driveLink = '', leistungen = [] }) {
  const isWebdesign = serviceType === 'webdesign';
  const strasse = pick(formData, 'Straße + Hausnummer', 'Straße');
  const plz     = pick(formData, 'PLZ');
  const ort     = pick(formData, 'Ort');
  const stammdaten = {
    ansprechpartner: pick(formData, 'Ansprechpartner (Name + Position)', 'Ansprechpartner'),
    inhaber:         pick(formData, 'Inhaber / Geschäftsführer', 'Inhaber/Geschäftsführer', 'Geschäftsführer'),
    adresse:         [strasse, [plz, ort].filter(Boolean).join(' ')].filter(Boolean).join(', ') || null,
    plz, ort,
    email:           pick(formData, 'E-Mail', 'Email'),
    telefon:         normalizePhone(pick(formData, 'Telefon')),
    ust_id:          pick(formData, 'UID / USt-ID', 'UID', 'USt-ID'),
    website_alt:     asUrl(pick(formData, 'Link zur alten Website', 'Website')),
    facebook:        asUrl(pick(formData, 'FB: Link zur Seite', 'Facebook Seite Link', 'Link Facebook', 'Facebook')),
    instagram:       asUrl(pick(formData, 'IG: Link', 'Instagram Handle', 'Handle Instagram', 'Instagram')),
    kunde_typ:       isWebdesign ? 'Webdesign' : 'Performance',
  };
  const projekte = [];
  if (isWebdesign) {
    const projekttyp = pick(formData, 'Projekttyp', 'Onepager oder Multipager');
    const typ = projekttyp && /multi/i.test(projekttyp) ? 'Multipager' : 'Onepager';
    projekte.push({
      linie: 'Webdesign', typ, name: `${firmaName} - ${typ}`,
      beschreibung: buildDescription(formData, driveLink) + leistungenAlsText(leistungen, formData),
    });
  } else {
    // Gebuchte Leistung(en) — je Linie ein eigenes Projekt (eine kann auslaufen, die andere weiterlaufen).
    // Nichts erkannt → Leadgen, damit nie ein Kunde ohne Projekt dasteht.
    const auswahl = (pick(formData, 'Gebuchte Leistung(en)', 'Gebuchte Leistungen',
                          'Service-Auswahl', 'Recruiting / Neukundengewinnung') || '').toLowerCase();
    const linien = [];
    if (/recruiting|mitarbeitergewinnung/.test(auswahl)) linien.push('Recruiting');
    if (/neukundengewinnung|leadgen|lead-gen/.test(auswahl) || !linien.length) linien.push('Leadgen');
    const stellenText = buildStellenText(formData);
    for (const linie of linien) {
      projekte.push({
        linie, typ: null, name: `${firmaName} - ${linie}`,
        beschreibung: buildDescription(formData, driveLink, linie) + (linie === 'Recruiting' ? stellenText : ''),
      });
    }
  }
  return { stammdaten, projekte, beschreibung_kunde: buildDescription(formData, driveLink) };
}

// Rohsatz speichern. Wirft bei D1-Fehlern — der Aufrufer loggt, die Abgabe selbst (Drive + Doc + Mail) bleibt gültig.
export async function eingangSpeichern(env, { firmaName, serviceType, formData = {}, driveLink = '', leistungen = [],
                                              missing = [], rootId = null, clientV = 0 }) {
  if (!env.EINGANG_DB) throw new Error('EINGANG_DB-Binding fehlt (wrangler.toml)');
  await env.EINGANG_DB.prepare(EINGANG_SCHEMA).run();
  const id = crypto.randomUUID();
  const abgeleitet = eingangAbleiten({ firmaName, serviceType, formData, driveLink, leistungen });
  await env.EINGANG_DB.prepare(
    `INSERT INTO onboarding_eingang (id, eingegangen_am, firma, service_type, drive_link, root_folder_id, leistungen,
       form_data, missing, abgeleitet, client_v) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).bind(id, new Date().toISOString(), firmaName, serviceType, driveLink || null, rootId,
         JSON.stringify(leistungen || []), JSON.stringify(formData || {}), JSON.stringify(missing || []),
         JSON.stringify(abgeleitet), Number(clientV) || 0).run();
  return { id, projekte: abgeleitet.projekte.map(p => p.name) };
}
