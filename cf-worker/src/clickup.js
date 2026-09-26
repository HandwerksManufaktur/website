// Gerüst (Subtasks + Checklisten) liegt in pipeline_geruest.json — dieselbe Datei liest
// system/scripts/onboarding_geruest.py und trägt nach, was hier im 30-s-Nachlauf abbricht.
import GERUEST from "./pipeline_geruest.json";
// ============================================================
// ClickUp Integration — Onboarding Form → ClickUp Tasks
// ------------------------------------------------------------
// Bei Form-Submit:
//   • Webdesign-Onboarding → Task in Kundendatenbank + Task in Website Projekte (verlinkt)
//   • SHK-Onboarding       → Task in Kundendatenbank + Task in Performance Projekte (verlinkt)
//
// Non-blocking. ClickUp-Fehler killt den Drive-Flow nicht.
// ============================================================

const CLICKUP_API = 'https://api.clickup.com/api/v2';

// === Listen-IDs ===
const LISTS = {
  kdb:         '901523378981', // 👥 Kundendatenbank (FULFILLMENT Space — neu nach Rebuild)
  pipeline:    '901523338959', // ⚡ Performance Projekte (FULFILLMENT Space)
  webdesign:   '901515004215', // 🌐 Website Projekte (FULFILLMENT Space)
};

// === Custom Field IDs ===
const FIELDS = {
  // Kundendatenbank
  kdb: {
    ansprechpartner:  'af58b50f-ccdb-4f17-aef9-3108ed521c42',
    inhaber:          '4dac64f3-2adb-4965-9804-68f0d810eee2',
    firmenadresse:    '11ac7353-b083-48df-8a05-39b3a755a8c0',
    telefon:          '40d86cc8-bb12-4efe-8ab7-f5dedd4ff352',
    email:            '7a4de0a6-4919-49f2-a471-45b2f5bcedcd',
    uid:              '83474451-1136-4db3-89be-9bad372c58c1',
    website:          '575fce4e-409e-4cf6-b758-9fe828372bb6',
    drive:            'e0f84371-a112-46c0-bd6b-2eb22b60a3b1',
    kundeSeit:        'e7959a32-f1f0-4bdb-9405-b105db7fb115',
    kundeTyp:         '04cc689d-8be7-478c-8c46-5ca3649914d8',
    onboardingDatum:  '84fea7d6-8ee8-4a52-9b83-ff4321b2d3ce',
  },
  // Performance Projekte
  // Stand 08/2026 gegen die Liste abgeglichen. "verknuepft" und "serviceTyp" gab es
  // nicht mehr (Rebuild) — die Verknüpfung läuft über die Relationship, die Linie über
  // das Label "Paket". Tote IDs kosten Zeit: der Create läuft sonst in den Fallback und
  // setzt jedes Feld einzeln nach.
  pipeline: {
    paket:           'e26428d8-6c95-4cb3-ae64-60da41e0e53b',
    eingangsdatum:   '843cfc33-6b8f-42fb-a467-ce1d7873f9fe',
    drive:           'e0f84371-a112-46c0-bd6b-2eb22b60a3b1',
    facebook:        '1a704120-1820-4d05-b2b7-bc6e9944e715',
    instagram:       '1608f876-6f0b-49e5-9088-65401c9c86b0',
    ansprechpartner: 'af58b50f-ccdb-4f17-aef9-3108ed521c42',
    email:           '7a4de0a6-4919-49f2-a471-45b2f5bcedcd',
    telefon:         '40d86cc8-bb12-4efe-8ab7-f5dedd4ff352',
    firmenadresse:   '11ac7353-b083-48df-8a05-39b3a755a8c0',
  },
  // Website Projekte
  webdesign: {
    briefingLink:    '84f15ecb-1633-428a-9e6d-b033524a1bcb',
    driveProjekt:    'ceec73c4-95fc-4676-95a7-287048304f1e',
    projekttyp:      '3f9ec2e7-376f-4584-bd0b-1b92727a2fb6',
    hostingAlt:      '439e369b-0012-4863-b3a4-e417c7363629',
    artTexte:        'ec4a66f2-67dd-4308-b8ba-c4611486b1b9',
    statusLogo:      'f57f55d0-df4f-4efd-b300-d27a6ae740dd',
    statusFotos:     '2311c233-23d1-4c0b-890f-cf002cdcb30d',
    statusInhalte:   '762b9e24-96da-4941-a63f-a339c8493503',
  },
};

// === Option-IDs für Dropdowns/Labels ===
const OPTS = {
  kundeTyp: {
    Webdesign:   '1106b36d-0403-4eae-b3b5-f8cd9b654c66',
    Performance: '8e159d32-b1f2-452a-a85f-bb0fa3deefb6',
    Hybrid:      '09f02faa-cb10-4db1-92a7-c0e66a7e057d',
  },
  produkt: {
    Webdesign:       '3a2bc3fc-3486-4978-bcc9-1a61386fe97a', // neu nach Rebuild
    Performance:     '292af171-d780-461f-b7cf-75252dc61e99',
    Recruiting:      'd1924e4f-d3e8-4468-b800-e3aa8a68a2cf',
    Wartungsvertrag: '16a60de6-c2bb-456b-9083-ea96b39daac4',
  },
  // Label-Feld "Paket" in Performance Projekte
  paket: {
    Leadgen:    '262c19ba-843e-4517-ade5-0191ebfc66cc', // Lead Generation
    Recruiting: '904ab9a2-b387-45c7-9c8f-094892534ea7',
  },
  projekttyp: {
    Onepager:   '21f42b6d-622e-4d39-95a3-c5e936f74c5d',
    Multipager: '01f92ebb-94ec-4d76-b5c5-d41ac6f1dd17',
  },
  artTexte: {
    'Neu erstellen, Basis Briefing':     'f765eb19-7f76-447c-917b-f1915061b5fb',
    'Neu erstellen, Basis alte Website': 'd66dda02-b03b-4de1-9523-1942a97b40bf',
    'Kunde liefert Texte':               '3cdd5cca-c368-4a6e-a417-fd81628c737a',
  },
  statusLogo: {
    Vorhanden: 'f94ea169-0374-4fa8-9454-84742e97e5a3',
    Fehlt:     '41a12204-7ba3-4876-b810-5ecbd609374a',
  },
  statusFotos: {
    'Vollständig vorhanden': 'd7d22af8-5e60-44c2-8e7b-eceddd7e56b7',
    'Teilweise vorhanden':   '0064e714-0306-493a-99a7-a7a46b8aab02',
    'Fehlt':                 'c22af1d2-5bf0-40fd-a60b-4b19ed6c923d',
  },
  statusInhalte: {
    'Vollständig vorhanden': '7d90a6a9-3888-4e0c-a6bf-caa0c2114386',
    'Teilweise vorhanden':   'c5bd9ad6-67ea-4bf6-b661-f82d4f47a65b',
    'Fehlt':                 'f588163c-00a4-4788-af14-4b6164b43857',
  },
};

const TASK_TYPE_LEAD    = 1002;
const TASK_TYPE_PROJECT = 1003;

const NOAH_USER_ID = 188597937;

// === Subtask-Vorlage Performance Projekte ===
// dueToday: Due Date = Tag des Onboarding-Eingangs
const PIPELINE_SUBTASKS = GERUEST.subtasks;

// === Checklisten-Vorlage Performance Projekte ===
const PIPELINE_CHECKLISTS = GERUEST.checklisten;

// ============================================================
// Helpers
// ============================================================

async function clickup(token, path, method, body, versuch = 0) {
  const res = await fetch(CLICKUP_API + path, {
    method,
    headers: { Authorization: token, 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  // 429 = Rate Limit (ClickUp: 100 Requests/Minute). Kurz warten und erneut versuchen,
  // sonst gehen bei zwei Projekt-Tasks einzelne Subtasks/Checklist-Items verloren.
  if (res.status === 429 && versuch < 4) {
    const wartezeit = Number(res.headers.get('retry-after') || 0) * 1000 || (2 ** versuch) * 1000;
    await new Promise(r => setTimeout(r, wartezeit));
    return clickup(token, path, method, body, versuch + 1);
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`ClickUp ${method} ${path} → ${res.status}: ${text}`);
  }
  return res.json();
}

// Parallel, aber gedrosselt — volle Parallelität reißt das ClickUp-Rate-Limit,
// rein sequenziell läuft der Worker in sein Zeitlimit.
async function mitLimit(items, limit, fn) {
  const ergebnisse = [];
  for (let i = 0; i < items.length; i += limit) {
    ergebnisse.push(...await Promise.all(items.slice(i, i + limit).map(fn)));
  }
  return ergebnisse;
}

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

// URL-Felder in ClickUp lehnen alles ab, was keine URL ist (400 FIELD_010) —
// z.B. das "Ja" aus einem Ja/Nein-Toggle. Lieber leer lassen als den Field-Set killen.
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

function buildDescription(formData, driveLink) {
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
    const v = formData[k];
    if (v) parts.push(`**${k}:**\n${v}`);
  }
  if (driveLink) parts.push(`---\n📁 [Drive-Ordner](${driveLink})`);
  return parts.join('\n\n');
}

function cleanFields(arr) {
  return arr.filter(f => f.value !== null && f.value !== undefined && f.value !== '');
}

// ClickUp-Phone-Fields akzeptieren NUR internationales Format (+49…).
// Nationale Nummern ("0943…") → 400 FIELD_016 und killen sonst den ganzen Task-Create.
function normalizePhone(raw) {
  if (!raw) return null;
  let p = String(raw).replace(/[\s\/\-().]/g, '');
  if (p.startsWith('00')) p = '+' + p.slice(2);
  else if (p.startsWith('0')) p = '+49' + p.slice(1);
  return p;
}

// Task-Create, der bei ungültigen Custom-Field-Werten NICHT komplett scheitert:
// Erst Versuch mit allen Fields; bei 400 → Task ohne Fields anlegen und
// jedes Field einzeln setzen (fehlerhafte Fields werden übersprungen und geloggt).
async function createTaskSafe(token, listId, payload) {
  try {
    return await clickup(token, `/list/${listId}/task`, 'POST', payload);
  } catch (err) {
    console.error('[ClickUp] Create mit Fields fehlgeschlagen, Fallback ohne Fields:', err.message);
    const { custom_fields, ...bare } = payload;
    const task = await clickup(token, `/list/${listId}/task`, 'POST', bare);
    for (const f of custom_fields || []) {
      await clickup(token, `/task/${task.id}/field/${f.id}`, 'POST', { value: f.value })
        .catch(e => console.error(`[ClickUp] Field ${f.id} übersprungen:`, e.message));
    }
    return task;
  }
}

// Subtasks (an Noah, teils Due Date = heute) + Checklisten an einen Performance-Projekt-Task hängen
// Subtasks + Checklisten laufen parallel statt nacheinander: bei zwei Projekt-Tasks
// (Recruiting + Leadgen) sind das ~52 API-Calls — sequenziell lief der Worker in sein
// Zeitlimit und der zweite Task wurde nie fertig angelegt.
export async function addPipelineExtrasForTask(token, taskId, todayMs) {
  await addPipelineSubtasks(token, taskId, todayMs);
  await addPipelineChecklisten(token, taskId);
}

async function addPipelineSubtasks(token, taskId, todayMs) {
  await mitLimit(PIPELINE_SUBTASKS, 4, st =>
    clickup(token, `/list/${LISTS.pipeline}/task`, 'POST', {
      name: st.name,
      parent: taskId,
      assignees: [NOAH_USER_ID],
      ...(st.dueToday ? { due_date: todayMs, due_date_time: false } : {}),
    }).catch(e => console.error(`[ClickUp] Subtask "${st.name}" übersprungen:`, e.message))
  );
}

// Die Checklisten selbst SEQUENZIELL anlegen — parallel angelegte Checklisten kamen
// zwar an, ihre Items aber nicht (ClickUp verträgt gleichzeitige Checklist-Writes auf
// demselben Task nicht). Die Items innerhalb einer Checkliste dürfen parallel laufen;
// eine feste Reihenfolge gibt ClickUp dort ohnehin nicht zurück.
async function addPipelineChecklisten(token, taskId) {
  for (const cl of PIPELINE_CHECKLISTS) {
    try {
      const created = await clickup(token, `/task/${taskId}/checklist`, 'POST', { name: cl.name });
      const clId = created.checklist ? created.checklist.id : created.id;
      await mitLimit(cl.items, 4, item =>
        clickup(token, `/checklist/${clId}/checklist_item`, 'POST', { name: item })
          .catch(e => console.error(`[ClickUp] Checklist-Item "${item}" übersprungen:`, e.message))
      );
    } catch (e) {
      console.error(`[ClickUp] Checkliste "${cl.name}" übersprungen:`, e.message);
    }
  }
}

// ============================================================
// Haupt-Funktion: createClickUpTasks
// ============================================================

export async function createClickUpTasks({ token, firmaName, serviceType, formData, driveLink, leistungen, selfService }) {
  const isWebdesign = serviceType === 'webdesign';
  const isSHK       = serviceType === 'shk';

  // === Stammdaten extrahieren ===
  const ansprechpartner = pick(formData, 'Ansprechpartner (Name + Position)', 'Ansprechpartner');
  const inhaber         = pick(formData, 'Inhaber / Geschäftsführer', 'Inhaber/Geschäftsführer', 'Geschäftsführer');
  const strasse         = pick(formData, 'Straße + Hausnummer', 'Straße');
  const plz             = pick(formData, 'PLZ');
  const ort             = pick(formData, 'Ort');
  const firmenadresse   = [strasse, [plz, ort].filter(Boolean).join(' ')].filter(Boolean).join(', ');
  const email           = pick(formData, 'E-Mail', 'Email');
  const telefon         = normalizePhone(pick(formData, 'Telefon'));
  const uid             = pick(formData, 'UID / USt-ID', 'UID', 'USt-ID');
  const websiteUrl      = asUrl(pick(formData, 'Link zur alten Website', 'Website'));
  const facebook        = asUrl(pick(formData, 'FB: Link zur Seite', 'Facebook Seite Link', 'Link Facebook', 'Facebook'));
  const instagram       = asUrl(pick(formData, 'IG: Link', 'Instagram Handle', 'Handle Instagram', 'Instagram'));

  const todayMs = Date.now();
  const description = buildDescription(formData, driveLink);

  // ============================================================
  // 1. KUNDENDATENBANK-Task — IMMER (egal welches Onboarding)
  // ============================================================
  const kdbFields = cleanFields([
    { id: FIELDS.kdb.kundeTyp,         value: isWebdesign ? OPTS.kundeTyp.Webdesign : OPTS.kundeTyp.Performance },
    { id: FIELDS.kdb.firmenadresse,    value: firmenadresse },
    { id: FIELDS.kdb.inhaber,          value: inhaber },
    { id: FIELDS.kdb.ansprechpartner,  value: ansprechpartner },
    { id: FIELDS.kdb.telefon,          value: telefon },
    { id: FIELDS.kdb.email,            value: email },
    { id: FIELDS.kdb.uid,              value: uid },
    { id: FIELDS.kdb.website,          value: websiteUrl },
    { id: FIELDS.kdb.drive,            value: driveLink },
    { id: FIELDS.kdb.kundeSeit,        value: todayMs },
    { id: FIELDS.kdb.onboardingDatum,  value: todayMs },
  ]);

  const kdbTask = await createTaskSafe(token, LISTS.kdb, {
    name: firmaName,
    status: 'aktiv',
    custom_item_id: TASK_TYPE_LEAD,
    description,
    custom_fields: kdbFields,
  });

  // ============================================================
  // 2a. WEBDESIGN-FLOW → zusätzlich Task in Website Projekte
  // ============================================================
  if (isWebdesign) {
    const projekttyp = pick(formData, 'Projekttyp', 'Onepager oder Multipager');
    const projektOpt = projekttyp && /multi/i.test(projekttyp) ? OPTS.projekttyp.Multipager : OPTS.projekttyp.Onepager;
    const hatBestehendeWebsite = pick(formData, 'Bestehende Website? (Ja/Nein)', 'Bestehende Website');
    const teamfotosVorhanden = pick(formData, 'Team-Fotos vorhanden? (Ja/Nein)', 'Team-Fotos vorhanden');

    const wdFields = cleanFields([
      { id: FIELDS.webdesign.briefingLink,  value: driveLink },
      { id: FIELDS.webdesign.driveProjekt,  value: driveLink },
      { id: FIELDS.webdesign.projekttyp,    value: projektOpt },
      { id: FIELDS.webdesign.artTexte,      value: [OPTS.artTexte['Neu erstellen, Basis Briefing']] },
      { id: FIELDS.webdesign.statusLogo,    value: OPTS.statusLogo.Fehlt }, // wird upgegradet wenn Logo im Drive
      { id: FIELDS.webdesign.statusFotos,   value: teamfotosVorhanden && /ja/i.test(teamfotosVorhanden)
                                                    ? OPTS.statusFotos['Teilweise vorhanden']
                                                    : OPTS.statusFotos.Fehlt },
      { id: FIELDS.webdesign.statusInhalte, value: OPTS.statusInhalte['Teilweise vorhanden'] },
    ]);

    const wdTask = await createTaskSafe(token, LISTS.webdesign, {
      name: `${firmaName} - ${projekttyp && /multi/i.test(projekttyp) ? 'Multipager' : 'Onepager'}`,
      status: 'neuer kunde',
      custom_item_id: TASK_TYPE_PROJECT,
      description,
      custom_fields: wdFields,
    });

    // Relationship: Website Projekt ↔ Kundendatenbank
    await clickup(token, `/task/${wdTask.id}/link/${kdbTask.id}`, 'POST', null).catch(() => {});

    // Leistungen als Subtasks im Website Projekt
    if (Array.isArray(leistungen)) {
      for (const leistung of leistungen) {
        if (!leistung) continue;
        const stichpunkte = pick(formData, `${leistung} - Stichpunkte`, `Stichpunkte ${leistung}`) || '';
        await clickup(token, `/list/${LISTS.webdesign}/task`, 'POST', {
          name: leistung,
          parent: wdTask.id,
          description: stichpunkte,
        }).catch(() => {});
      }
    }

    return { kdbTaskId: kdbTask.id, webdesignTaskId: wdTask.id };
  }

  // ============================================================
  // 2b. SHK-FLOW → zusätzlich Task in Performance Projekte
  // ============================================================
  if (isSHK) {
    // Gebuchte Leistung(en) — Feldname kommt so aus dem Formular; ältere Namen als Fallback.
    const auswahl = (pick(formData, 'Gebuchte Leistung(en)', 'Gebuchte Leistungen',
                          'Service-Auswahl', 'Recruiting / Neukundengewinnung') || '').toLowerCase();
    const hatRecruiting = /recruiting|mitarbeitergewinnung/.test(auswahl);
    const hatLeadgen    = /neukundengewinnung|leadgen|lead-gen/.test(auswahl);

    // Pro gebuchter Leistung ein eigener Projekt-Task — so bleibt jede Linie einzeln
    // trackbar (eine kann auslaufen, während die andere weiterläuft).
    // Nichts erkannt → Leadgen als Fallback, damit nie ein Kunde ohne Projekt-Task dasteht.
    const linien = [];
    if (hatRecruiting) linien.push('Recruiting');
    if (hatLeadgen || !linien.length) linien.push('Leadgen');

    // Offene Stellen gehören in die Description (Infos, keine To-dos — KEINE Subtasks)
    const stellenText = buildStellenText(formData);

    // Zuerst ALLE Projekt-Tasks anlegen (wenige Calls) — erst danach die Extras.
    // So existieren die Tasks auch dann, wenn der Worker beim Nachziehen der
    // Subtasks/Checklisten abbrechen sollte.
    const pipelineTaskIds = [];
    for (const linie of linien) {
      const isRecruiting = linie === 'Recruiting';

      const ppFields = cleanFields([
        { id: FIELDS.pipeline.paket,           value: [isRecruiting ? OPTS.paket.Recruiting : OPTS.paket.Leadgen] },
        { id: FIELDS.pipeline.eingangsdatum,   value: todayMs },
        { id: FIELDS.pipeline.drive,           value: driveLink },
        { id: FIELDS.pipeline.facebook,        value: facebook },
        { id: FIELDS.pipeline.instagram,       value: instagram },
        { id: FIELDS.pipeline.ansprechpartner, value: ansprechpartner },
        { id: FIELDS.pipeline.email,           value: email },
        { id: FIELDS.pipeline.telefon,         value: telefon },
        { id: FIELDS.pipeline.firmenadresse,   value: firmenadresse },
      ]);

      const ppTask = await createTaskSafe(token, LISTS.pipeline, {
        name: `${firmaName} - ${linie}`,
        status: '🆕 Neuer Kunde',
        custom_item_id: TASK_TYPE_PROJECT,
        description: description + (isRecruiting ? stellenText : ''),
        assignees: [NOAH_USER_ID],
        custom_fields: ppFields,
      });

      // Relationship: Performance Projekt ↔ Kundendatenbank
      await clickup(token, `/task/${ppTask.id}/link/${kdbTask.id}`, 'POST', null).catch(() => {});

      pipelineTaskIds.push(ppTask.id);
    }

    // Reihenfolge nach Wichtigkeit: erst bekommen ALLE Tasks ihre Subtasks (die echten
    // Arbeitsschritte), danach die Checklisten (QA-Details). Bei zwei Projekt-Tasks ist
    // die Worker-Laufzeit knapp — so ist im Zweifel das Wichtigere zuerst vollständig.
    // Subtask/Checklisten-Gerüst pro Task. Zwei volle Gerüste (~80 API-Calls) sprengen
    // das Laufzeitlimit EINER Invocation — deshalb ruft sich der Worker pro Task über
    // das Service Binding selbst auf (/clickup-extras): jede Invocation hat ihr eigenes
    // frisches Limit. Die Aufrufe laufen parallel und werden abgewartet.
    if (selfService) {
      const results = await Promise.all(pipelineTaskIds.map(id =>
        selfService.fetch('https://self/clickup-extras', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'x-internal-auth': token },
          body: JSON.stringify({ taskId: id, todayMs }),
        }).then(r => ({ id, status: r.status }))
          .catch(e => ({ id, error: e.message }))
      ));
      console.log('[ClickUp Extras via SELF]', JSON.stringify(results));
      // Fallback: Tasks, deren Self-Request nicht mit 200 endete, inline versorgen
      for (const r of results) {
        if (r.status !== 200) {
          console.error('[ClickUp] Self-Extras fehlgeschlagen, mache inline:', JSON.stringify(r));
          await addPipelineSubtasks(token, r.id, todayMs);
          await addPipelineChecklisten(token, r.id);
        }
      }
    } else {
      // Ohne Binding (z.B. lokal): erst alle Subtasks, dann Checklisten — über die
      // Tasks hinweg parallel; der Checklist-Konflikt trat nur auf DEMSELBEN Task auf.
      await Promise.all(pipelineTaskIds.map(id => addPipelineSubtasks(token, id, todayMs)));
      await Promise.all(pipelineTaskIds.map(id => addPipelineChecklisten(token, id)));
    }

    return { kdbTaskId: kdbTask.id, pipelineTaskIds, pipelineTaskId: pipelineTaskIds[0] };
  }

  return { kdbTaskId: kdbTask.id };
}
