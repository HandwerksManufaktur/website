#!/usr/bin/env python3
"""Handy-Prüfer für handwerksmanufaktur.digital.

Läuft jede Seite am Handy durch (Chromium + WebKit, is_mobile, has_touch), scrollt einmal komplett durch
(Lazy-Inhalte, Reveal-Animationen), schließt den Cookie-Hinweis mit „Nein" und misst:

  ueberlauf     Seite breiter als der Bildschirm (scrollWidth > innerWidth)
  abgeschnitten Text in overflow:hidden/clip/ellipsis, dessen Inhalt größer ist als das Feld;
                Eingabefelder, deren Inhalt breiter ist als das Feld
  klein         Text unter 13 px (Hausregel)
  tippziel      a/button kleiner als 44 px (Links im Fließtext ausgenommen, WCAG 2.5.8)
  bahn          waagerechte Wischbahn, die vor dem Bildschirmrand endet (Karte wird mitten im Bild abgeschnitten)
  rand          Elemente, die über den Bildschirmrand ragen (außer in horizontal scrollenden Bahnen
                oder von einem Eltern-Element mit overflow:hidden sauber abgeschnitten)
  ueberlappung  Text, der auf anderem Text liegt

Aufruf (Server im Repo starten: python3 -m http.server 8830 --bind 127.0.0.1):
  .venv/bin/python werkzeug/mobil_pruefen.py --basis http://127.0.0.1:8870 [--seiten / /kontakt/]
        [--engines chromium,webkit] [--groessen 390x844,375x667] [--json aus.json] [--bilder ordner]

--bilder legt je Seite (390 px, Chromium) Bildschirmhöhen-Abschnitte ab, zum Ansehen.
Exit-Code 1, wenn es Funde gibt.
"""
import argparse, json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
INTERN = {'alt', 'neu', 'neu-neu', 'test', 'konzept', 'praesentation', 'onboarding', 'cf-worker', 'node_modules',
          'potenzialanalyse', 'static', 'assets', 'images', 'fonts', 'werkzeug'}

def alle_seiten():
    seiten = set()
    sm = REPO / 'sitemap.xml'
    if sm.exists():
        for loc in re.findall(r'<loc>([^<]+)</loc>', sm.read_text()):
            seiten.add(re.sub(r'^https?://[^/]+', '', loc) or '/')
    for f in REPO.glob('**/index.html'):
        teile = f.relative_to(REPO).parts[:-1]
        if any(t in INTERN or t.startswith('archiv-') or t.startswith('.') for t in teile):
            continue
        seiten.add('/' + '/'.join(teile) + ('/' if teile else ''))
    return sorted(s for s in seiten if not any(s.strip('/').split('/')[0] == i for i in INTERN))

MESSEN = r"""
(nurSichtbar) => {
  // nurSichtbar: nur Elemente prüfen, die gerade (senkrecht) im Bildschirm liegen — so wird jede Sticky-Bühne in dem
  // Zustand gemessen, in dem man sie beim Scrollen wirklich sieht.
  const W = innerWidth, H = innerHeight, funde = [];
  const cs = e => getComputedStyle(e);
  const name = e => {
    let s = e.tagName.toLowerCase();
    if (e.id) s += '#' + e.id;
    if (e.classList.length) s += '.' + [...e.classList].slice(0, 3).join('.');
    const p = e.parentElement; if (p && p !== document.body) {
      let q = p.tagName.toLowerCase(); if (p.classList.length) q += '.' + [...p.classList].slice(0, 2).join('.');
      s = q + ' > ' + s;
    }
    return s;
  };
  const text = e => (e.innerText || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 60);
  const imBild = r => !nurSichtbar || (r.bottom > 0 && r.top < H);
  const cache = new Map();
  const sichtbar = e => {
    if (cache.has(e)) return cache.get(e);
    let ok = true;
    const r = e.getBoundingClientRect();
    if (r.width <= 2 || r.height <= 2) ok = false;
    else if (e.checkVisibility && !e.checkVisibility({contentVisibilityAuto: true, opacityProperty: true, visibilityProperty: true})) ok = false;
    else if (e.closest('details:not([open])') && !e.closest('summary')) ok = false;
    else {
      const s = cs(e);
      if (s.visibility !== 'visible') ok = false;
      let op = 1;
      if (ok) for (let a = e; a && a !== document.documentElement; a = a.parentElement) {
        const sa = cs(a); op *= parseFloat(sa.opacity);
        if (sa.display === 'none' || op < .1 || a.hidden) { ok = false; break; }
        if (sa.clip && sa.clip !== 'auto' || (sa.clipPath && /inset\(50%|circle\(0/.test(sa.clipPath))) { ok = false; break; }
      }
      if (ok) for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) {
        const sa = cs(a);
        if (/(hidden|clip|auto|scroll)/.test(sa.overflowX + sa.overflowY)) {
          const ra = a.getBoundingClientRect();
          if (r.right <= ra.left + 1 || r.left >= ra.right - 1 || r.bottom <= ra.top + 1 || r.top >= ra.bottom - 1) { ok = false; break; }
        }
      }
    }
    cache.set(e, ok); return ok;
  };
  const eigenerText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
  const textRects = e => {
    const rs = [];
    for (const n of e.childNodes) if (n.nodeType === 3 && n.textContent.trim()) {
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) if (r.width > 2 && r.height > 2) rs.push(r);
    }
    return rs;
  };
  const inScrollBahn = e => {
    for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) {
      const s = cs(a); if (/(auto|scroll)/.test(s.overflowX)) return a;
    }
    return null;
  };
  const geclippt = e => {
    for (let a = e.parentElement; a && a !== document.documentElement; a = a.parentElement) {
      const s = cs(a);
      if (/(hidden|clip)/.test(s.overflowX)) { const ra = a.getBoundingClientRect(); if (ra.left >= -1 && ra.right <= W + 1) return true; }
    }
    return false;
  };
  const fest = e => { for (let a = e; a && a !== document.body; a = a.parentElement) if (cs(a).position === 'fixed') return true; return false; };
  const NICHT = new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','BR','SOURCE','TRACK','META','LINK','svg','path','circle','line','rect','g','polyline','polygon','defs','use','text','tspan','ellipse','mask','clipPath','linearGradient','stop','radialGradient','pattern','image','foreignObject','symbol']);
  const alle = [...document.body.querySelectorAll('*')].filter(e => !NICHT.has(e.tagName) && !e.closest('svg') && imBild(e.getBoundingClientRect()));

  const sw = document.documentElement.scrollWidth;
  if (sw > W + 1) funde.push({art: 'ueberlauf', wo: 'html', info: `scrollWidth ${sw} > ${W}`, text: ''});

  const textEl = alle.filter(e => eigenerText(e) && sichtbar(e));

  // abgeschnitten (eigenes overflow): Ellipsis, oder eigene Textzeilen ragen über den Rand des eigenen Kastens
  for (const e of textEl) {
    const s = cs(e);
    const hx = /(hidden|clip)/.test(s.overflowX), hy = /(hidden|clip)/.test(s.overflowY);
    const lc = s.webkitLineClamp && s.webkitLineClamp !== 'none' && s.webkitLineClamp !== '0';
    let grund = '';
    if (s.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1) grund = 'Ellipsis ' + e.scrollWidth + '>' + e.clientWidth;
    else if (lc && e.scrollHeight > e.clientHeight + 1) grund = 'line-clamp';
    else if (hx || hy) {
      const r = e.getBoundingClientRect();
      const L = r.left + e.clientLeft, T = r.top + e.clientTop, R = L + e.clientWidth, B = T + e.clientHeight;
      for (const q of textRects(e)) {
        if (hx && (q.right > R + 1 || q.left < L - 1)) { grund = 'Zeile ragt seitlich raus'; break; }
        if (hy && (q.bottom > B + 1 || q.top < T - 1)) { grund = 'Zeile ragt unten/oben raus'; break; }
      }
    }
    if (grund) funde.push({art: 'abgeschnitten', wo: name(e), info: grund, text: text(e)});
  }
  // Text ragt teilweise aus einem overflow:hidden-Vorfahren (Schnitt am Bildschirmrand = Laufband/Bahn, erlaubt)
  for (const e of textEl) {
    let hit = null;
    for (const r of textRects(e)) {
      for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) {
        const s = cs(a);
        const hx = /(hidden|clip)/.test(s.overflowX), hy = /(hidden|clip)/.test(s.overflowY);
        if (!hx && !hy) continue;
        const ra = a.getBoundingClientRect();
        const drin = r.right > ra.left + 2 && r.left < ra.right - 2 && r.bottom > ra.top + 2 && r.top < ra.bottom - 2;
        const linksCut = hx && r.left < ra.left - 1 && ra.left > 1, rechtsCut = hx && r.right > ra.right + 1 && ra.right < W - 1;
        const vCut = hy && (r.top < ra.top - 1 || r.bottom > ra.bottom + 1);
        if (drin && (linksCut || rechtsCut || vCut)) hit = a;
        break;
      }
      if (hit) break;
    }
    if (hit) funde.push({art: 'abgeschnitten', wo: name(e), info: 'ragt aus ' + name(hit), text: text(e)});
  }
  for (const e of alle.filter(x => x.matches('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=range]),textarea'))) {
    if (!sichtbar(e)) continue;
    if (e.tagName === 'INPUT' && e.value && e.scrollWidth > e.clientWidth + 1) funde.push({art: 'abgeschnitten', wo: name(e), info: 'Eingabe breiter als Feld', text: e.value.slice(0, 60)});
    const fs = parseFloat(cs(e).fontSize); if (fs < 16) funde.push({art: 'klein', wo: name(e), info: 'Eingabefeld ' + fs + 'px (iOS zoomt unter 16 px)', text: e.placeholder || ''});
  }

  // klein
  for (const e of textEl) {
    const fs = parseFloat(cs(e).fontSize);
    if (fs < 12.95) funde.push({art: 'klein', wo: name(e), info: fs.toFixed(1) + 'px', text: text(e)});
  }

  // Tippziele (Pseudo-Elemente, die die Fläche vergrößern, zählen mit)
  const px = v => parseFloat(v) || 0;
  for (const e of alle.filter(x => x.matches('a[href],button,[role=button],summary,label[for]'))) {
    if (!sichtbar(e) || e.closest('[inert]') || cs(e).pointerEvents === 'none') continue;
    const r = e.getBoundingClientRect();
    let w = r.width, h = r.height;
    for (const ps of ['::before', '::after']) {
      const p = getComputedStyle(e, ps);
      if (p.content && p.content !== 'none' && p.position === 'absolute' && p.pointerEvents !== 'none') {
        w = Math.max(w, r.width - Math.min(0, px(p.left)) - Math.min(0, px(p.right)));
        h = Math.max(h, r.height - Math.min(0, px(p.top)) - Math.min(0, px(p.bottom)));
      }
    }
    if (w >= 43.5 && h >= 43.5) continue;
    // Beschriftung (label for=…) über einem Feld, das selbst groß genug ist: das Feld ist das Tippziel, nicht die Überschrift
    if (e.tagName === 'LABEL') { const z = document.getElementById(e.htmlFor); if (z && z.getBoundingClientRect().height >= 43.5) continue; }
    const s = cs(e);
    if (e.tagName === 'A' && s.display === 'inline') {
      const p = e.parentElement; const pt = (p.innerText || '').trim().length, et = (e.innerText || '').trim().length;
      if (pt > et + 10) continue;   // Link im Fließtext (WCAG 2.5.8, Ausnahme „inline")
    }
    funde.push({art: 'tippziel', wo: name(e), info: `${Math.round(w)}×${Math.round(h)}`, text: text(e) || e.getAttribute('aria-label') || ''});
  }

  // Wischbahnen, die vor dem Bildschirmrand enden: die nächste Karte wird mitten im Bild hart abgeschnitten
  for (const e of alle) {
    const s = cs(e);
    if (!/(auto|scroll)/.test(s.overflowX) || e.scrollWidth <= e.clientWidth + 1 || !sichtbar(e)) continue;
    const r = e.getBoundingClientRect();
    if (r.width > W * .6 && (r.right < W - 2 || r.left > 2)) funde.push({art: 'bahn', wo: name(e), info: `Wischbahn endet vor dem Rand: ${Math.round(r.left)}–${Math.round(r.right)} (W ${W})`, text: text(e).slice(0, 40)});
  }

  // über den Rand
  const randFunde = [];
  for (const e of alle) {
    const r = e.getBoundingClientRect();
    if (!(r.right > W + 1 || r.left < -1)) continue;
    if (!sichtbar(e) || inScrollBahn(e) || geclippt(e)) continue;
    randFunde.push(e);
  }
  for (const e of randFunde) if (!randFunde.some(o => o !== e && o.contains(e))) {
    const r = e.getBoundingClientRect();
    funde.push({art: 'rand', wo: name(e), info: `left ${Math.round(r.left)} right ${Math.round(r.right)} (W ${W})`, text: text(e)});
  }

  // Text auf Text — nur, was man wirklich sieht: liegt eine deckende Fläche dazwischen, zählt es nicht
  const deckend = el => { const s = cs(el); const m = s.backgroundColor.match(/rgba?\(([^)]+)\)/); const al = m ? (m[1].split(',')[3] === undefined ? 1 : parseFloat(m[1].split(',')[3])) : 0;
    return al > .85 || ['IMG', 'VIDEO', 'CANVAS', 'PICTURE'].includes(el.tagName) || (s.backgroundImage !== 'none' && !/gradient/.test(s.backgroundImage)); };
  const boxen = [];
  for (const e of textEl) if (!fest(e)) for (const r of textRects(e)) if (r.bottom > 0 && r.top < H) boxen.push({e, r});
  const ueb = new Set();
  for (let i = 0; i < boxen.length; i++) for (let j = i + 1; j < boxen.length; j++) {
    const a = boxen[i], b = boxen[j]; if (a.e === b.e || a.e.contains(b.e) || b.e.contains(a.e)) continue;
    const x0 = Math.max(a.r.left, b.r.left), x1 = Math.min(a.r.right, b.r.right), y0 = Math.max(a.r.top, b.r.top), y1 = Math.min(a.r.bottom, b.r.bottom);
    if (!(x1 - x0 > 4 && y1 - y0 > Math.min(a.r.height, b.r.height) * .35)) continue;
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    if (cx < 0 || cx > W || cy < 0 || cy > H) continue;
    const stapel = document.elementsFromPoint(cx, cy);
    const ia = stapel.findIndex(el => el === a.e || a.e.contains(el)), ib = stapel.findIndex(el => el === b.e || b.e.contains(el));
    if (ia >= 0 && ib >= 0) {
      const [o, u] = ia < ib ? [ia, ib] : [ib, ia]; const oben = stapel[o];
      if (stapel.slice(o, u).some(el => !el.contains(stapel[u]) && deckend(el))) continue;
    } else if (ia >= 0 || ib >= 0) {
      // einer ist nicht trefferbar (pointer-events:none) — verdeckt? wenn über dem anderen eine deckende Fläche liegt, zählt es nicht
      const k = Math.max(ia, ib); const andere = ia >= 0 ? b.e : a.e;
      if (stapel.slice(0, k + 1).some(el => deckend(el) && !el.contains(andere) && !andere.contains(el))) {} 
    }
    const k = name(a.e) + ' | ' + name(b.e); if (ueb.has(k)) continue; ueb.add(k);
    funde.push({art: 'ueberlappung', wo: k, info: `${Math.round(x1 - x0)}×${Math.round(y1 - y0)} @y${Math.round(cy + scrollY)}`, text: text(a.e) + ' | ' + text(b.e)});
  }
  return funde;
}
"""

GOOGLE = r"""
() => {
  // „Frag Google einfach selbst": jeden Suchbegriff ins Feld setzen und prüfen, ob er ganz zu sehen ist
  const su = document.querySelector('.suche[data-treffer]'); if (!su) return [];
  const t = su.querySelector('.tipp'), f = su.querySelector('.suchfeld'); if (!t || !f) return [];
  let d = []; try { d = JSON.parse(su.dataset.treffer); } catch (e) { return []; }
  const alt = t.textContent, funde = [];
  for (const x of d) {
    t.textContent = x.begriff;
    const rg = document.createRange(); rg.selectNodeContents(t);
    const fr = f.getBoundingClientRect(), tr = t.getBoundingClientRect();
    const raus = [...rg.getClientRects()].some(q => q.right > Math.min(fr.right, tr.right) + 1 || q.left < fr.left - 1 || q.bottom > fr.bottom + 1);
    if (raus || t.scrollWidth > t.clientWidth + 1) funde.push({art: 'abgeschnitten', wo: 'google .suchfeld .tipp', info: 'Suchbegriff passt nicht ins Feld', text: x.begriff});
  }
  t.textContent = alt;
  return funde;
}
"""

def cookie_weg(page):
    try:
        b = page.locator('.cookie-nein')
        if b.count() and b.first.is_visible():
            b.first.click(timeout=2000)
            page.wait_for_timeout(300)
    except Exception:
        pass

def scrolle_und_miss(page, schritt=.6):
    """Scrollt von oben nach unten und misst an jeder Stelle, was im Bildschirm steht."""
    funde = []
    h = page.evaluate('innerHeight'); y = 0; n = 0
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})'); page.wait_for_timeout(500)
    while True:
        for f in page.evaluate(MESSEN, True):
            if f not in funde: funde.append(f)
        total = page.evaluate('document.documentElement.scrollHeight')
        if y + h >= total - 2 or n > 150: break
        y += int(h * schritt); n += 1
        page.evaluate(f'window.scrollTo({{top:{y},behavior:"instant"}})')
        page.wait_for_timeout(260)
    return funde

def bilder_machen(page, ordner, slug):
    h = page.evaluate('innerHeight'); y = 0; n = 0; shots = []
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})'); page.wait_for_timeout(500)
    while True:
        p = Path(ordner) / f'{slug}_{n:02d}.png'; page.screenshot(path=str(p)); shots.append(str(p))
        total = page.evaluate('document.documentElement.scrollHeight')
        if y + h >= total - 2 or n > 80: break
        y += h; n += 1
        page.evaluate(f'window.scrollTo({{top:{y},behavior:"instant"}})'); page.wait_for_timeout(1100)
    return shots

def pruefe(page, url, bilder_dir=None, slug=''):
    page.goto(url, wait_until='load', timeout=45000)
    page.wait_for_timeout(700)
    cookie_weg(page)
    # Messen ohne Einrasten/Smooth-Scroll, sonst landet scrollTo nicht dort, wo gemessen werden soll
    page.add_style_tag(content='html,html.zs-rastet{scroll-behavior:auto!important;scroll-snap-type:none!important}')
    # einmal zügig ganz durch (Lazy-Inhalte, Reveal), dann je Bildschirm messen
    page.evaluate("""async () => { const h = innerHeight; for (let y = 0; y < document.documentElement.scrollHeight; y += h * .8) { scrollTo({top: y, behavior: 'instant'}); await new Promise(r => setTimeout(r, 90)); } }""")
    page.wait_for_timeout(400)
    cookie_weg(page)
    funde = scrolle_und_miss(page)
    funde += page.evaluate(GOOGLE)
    # Geschenk-Fenster der Stadt-/Branchenseiten: im Durchlauf unterdrückt (es läge sonst über allem), hier einzeln geprüft —
    # alle drei Zustände (Angebot, Formular, Warnung)
    if page.evaluate("!!document.querySelector('dialog.lp-geschenk')"):
        for zustand in ('.lg-auf', '.lg-form', '.lg-warnung'):
            page.evaluate(f"""() => {{ const d = document.querySelector('dialog.lp-geschenk'); if (!d.open) d.showModal(); d.classList.add('an');
                ['.lg-auf', '.lg-form', '.lg-warnung'].forEach(x => {{ const t = d.querySelector(x); if (t) t.hidden = x !== '{zustand}'; }}); d.scrollTop = 0; }}""")
            page.wait_for_timeout(500)
            for f in page.evaluate(MESSEN, True):
                if f not in funde: funde.append(f)
        page.evaluate("() => { const d = document.querySelector('dialog.lp-geschenk'); d.classList.remove('an'); d.close(); }")
    shots = bilder_machen(page, bilder_dir, slug) if bilder_dir else []
    seen, out = set(), []
    for f in funde:
        k = (f['art'], f['wo'], f.get('text', ''))
        if k in seen: continue
        seen.add(k); out.append(f)
    return out, shots

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--basis', default='http://127.0.0.1:8870')
    ap.add_argument('--seiten', nargs='*')
    ap.add_argument('--engines', default='chromium,webkit')
    ap.add_argument('--groessen', default='390x844,375x667')
    ap.add_argument('--json')
    ap.add_argument('--bilder')
    ap.add_argument('--still', action='store_true', help='nur Summen ausgeben')
    a = ap.parse_args()
    seiten = a.seiten or alle_seiten()
    groessen = [tuple(map(int, g.split('x'))) for g in a.groessen.split(',')]
    ergebnis = {}
    with sync_playwright() as p:
        for eng in a.engines.split(','):
            br = getattr(p, eng).launch()
            for (w, h) in groessen:
                ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True,
                                     device_scale_factor=2 if eng == 'webkit' else 2, locale='de-DE')
                # Geschenk-Fenster (lp.js) und WhatsApp-Marke nicht von selbst aufgehen lassen — sie werden gezielt geprüft
                ctx.add_init_script("try{localStorage.setItem('hwm-geschenk-am',String(Date.now()))}catch(e){}")
                page = ctx.new_page()
                for s in seiten:
                    slug = s.strip('/').replace('/', '_') or 'start'
                    bd = a.bilder if (a.bilder and eng == 'chromium' and w == groessen[0][0]) else None
                    if bd: os.makedirs(bd, exist_ok=True)
                    try:
                        funde, _ = pruefe(page, a.basis + s, bd, slug)
                    except Exception as ex:
                        funde = [{'art': 'fehler', 'wo': '', 'info': str(ex)[:200]}]
                    ergebnis.setdefault(s, {})[f'{eng} {w}x{h}'] = funde
                    if not a.still:
                        print(f'{eng} {w}x{h} {s}: {len(funde)}', flush=True)
                ctx.close()
            br.close()
    summe = sum(len(f) for v in ergebnis.values() for f in v.values())
    arten = {}
    for v in ergebnis.values():
        for f in v.values():
            for x in f: arten[x['art']] = arten.get(x['art'], 0) + 1
    print(f'\nFunde gesamt: {summe}  ' + ' · '.join(f'{k} {v}' for k, v in sorted(arten.items())))
    for s, v in ergebnis.items():
        n = sum(len(f) for f in v.values())
        if n:
            print(f'\n{s}  ({n})')
            uniq = {}
            for k, f in v.items():
                for x in f: uniq.setdefault((x['art'], x['wo'], x.get('info', '') if x['art'] != 'tippziel' else '', x.get('text', '')), []).append(k)
            for (art, wo, info, txt), ks in uniq.items():
                print(f'  [{art}] {wo} {info} «{txt}»  ({", ".join(ks)})')
    if a.json:
        Path(a.json).write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1))
    sys.exit(1 if summe else 0)

if __name__ == '__main__':
    main()
