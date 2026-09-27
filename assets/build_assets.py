#!/usr/bin/env python3
"""DEFINITIVE asset sourcing. Handles API continuation so every page's full
image list and infobox image are actually retrieved (the earlier runs silently
used a truncated slice)."""
import os, json, urllib.request, urllib.parse, time, re, csv, difflib
from collections import Counter

UA = 'LegionBot/1.0 (https://github.com/Behind-the-Jersey; okinent@protonmail.com)'
EN = 'https://en.wikipedia.org/w/api.php'
COMMONS = 'https://commons.wikimedia.org/w/api.php'

GENERIC = re.compile(r'commons-logo|disambig|wikimedia|^file:wiki|flag of|symbol|'
                     r'ambox|question_book|edit-clear|padlock|portal|nuvola|crystal|'
                     r'folder|puzzle|commons\.svg|wikidata|wikisource|wikiquote|'
                     r'wikinews|wiktionary|free-content|wikivoyage|featured|'
                     r'cscr-|speaker|semi-protection|padlock', re.I)
GOOD = re.compile(r'logo|crest|badge|wordmark|arms', re.I)
BAD = re.compile(r'kit body|stadium|jersey|shirt|squad|crowd|match|signature|'
                 r'panorama|team photo|map of|location|panorama', re.I)
NEUTRAL = {'logo', 'crest', 'badge', 'wordmark', 'arms', 'svg', 'png', 'fc', 'f.c.', 'cf',
           'sc', 's.c.', 'ac', 'a.c.', 'afc', 'the', 'of', 'and', 'football', 'club',
           'sport', 'sports', 'team', 'national', 'cap', 'primary', 'main', 'official', 'file'}
YEAR = re.compile(r'\b(1[89]\d\d|20[0-2]\d)\b')
STOP = {'f.c.', 'fc', 'cf', 'sc', 'ac', 'afc', 'the', 'team', 'club', 'sport', 'sports'}

PATTERNS = [('non-?free|fair ?use|fairuse', 'Non-free (fair use)'),
            ('cc[- ]?zero|cc0', 'CC0'),
            ('cc[- ]?by[- ]?sa|cc[- ]?sa', 'CC BY-SA'),
            ('cc[- ]?by\\b', 'CC BY'),
            ('gfdl', 'GFDL'),
            ('pd[-_]|public domain', 'Public domain'),
            ('attribution', 'Attribution')]

UMLAUT = [('oe', 'ö'), ('ue', 'ü'), ('ae', 'ä'), ('ss', 'ß')]


def api(ep, params, retries=5):
    params = dict(params); params['format'] = 'json'; params['formatversion'] = '2'
    for a in range(retries):
        try:
            qs = urllib.parse.urlencode(params, safe='')
            req = urllib.request.Request(ep + '?' + qs, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(1.2 * (a + 1)); continue
            return {'_error': str(e.code)}
        except Exception:
            time.sleep(1.2 * (a + 1))
    return {'_error': 'maxretries'}


def api_all(ep, params):
    """Query with full continuation handling. Returns merged pages dict."""
    params = dict(params)
    pages = {}
    guard = 0
    while True:
        guard += 1
        if guard > 40:
            break
        d = api(ep, params)
        if '_error' in d:
            break
        for p in d.get('query', {}).get('pages', []):
            t = norm(p['title'])
            if p.get('missing'):
                pages.setdefault(t, p)
                continue
            cur = pages.setdefault(t, {'title': p['title'], 'images': []})
            for k, v in p.items():
                if k == 'images':
                    cur['images'] = cur.get('images', []) + v
                elif k in ('pageimage', 'original', 'pageid'):
                    if v:
                        cur[k] = v
            if 'missing' in p:
                cur.pop('missing', None)
        cont = d.get('continue')
        if not cont:
            break
        params.update(cont)
        time.sleep(0.05)
    return pages


def chunk(s, n):
    for i in range(0, len(s), n):
        yield s[i:i + n]


def norm(t):
    return t.replace('_', ' ').strip()


def toks(s):
    return [w for w in re.split(r'[\s\-–._"()\[\]]+', s.lower()) if w]


def name_words(name):
    return [w for w in toks(name) if len(w) > 3 and w not in STOP and w not in NEUTRAL]


def affinity(filename, clubname):
    nw = name_words(clubname)
    if not nw:
        return 0.0
    f = filename.lower()
    return sum(1 for w in nw if w in f) / len(nw)


def score(filename, clubname):
    f = filename.lower()
    s = 0.0
    if GENERIC.search(f):
        s += 40
    if BAD.search(f):
        s += 12
    if GOOD.search(f):
        s -= 8
    s -= affinity(filename, clubname) * 14
    extra = [t for t in toks(filename.rsplit('.', 1)[0]) if t not in NEUTRAL and t not in STOP]
    s += len(extra) * 3.5
    if YEAR.search(f):
        s += 7
    if f.endswith('.svg'):
        s -= 3
    elif f.endswith('.jpg'):
        s += 3
    return s


def looks_like_crest(fn, club):
    f = fn.lower()
    if GENERIC.search(f) or BAD.search(f):
        return False
    return bool(GOOD.search(f)) or affinity(fn, club) >= 1.0


def pick_crest(page, club):
    pi = page.get('pageimage')
    if pi and looks_like_crest(pi, club):
        return 'File:' + norm(pi)
    cands = [(score(i['title'], club), i['title']) for i in page.get('images', [])
             if i['title'].lower().endswith(('.svg', '.png'))]
    if cands:
        cands.sort()
        return cands[0][1]
    return 'File:' + norm(pi) if pi else None


def kit_rank(title):
    t = title.lower()
    if '2627' in t or '2026' in t:
        s = 0
    elif '2526' in t or '2025' in t:
        s = 20
    else:
        s = 60
    m = re.search(r'(h|a|t)\.(png|jpg)$', t)
    s += {'h': 0, 'a': 1, 't': 2}.get(m.group(1) if m else 'h', 3)
    return s


def kit_type(title):
    m = re.search(r'(h|a|t)\.(png|jpg|jpeg)$', title.lower())
    return {'h': 'kit-home', 'a': 'kit-away', 't': 'kit-third'}.get(m.group(1) if m else 'h', 'kit-home')


def candidates(club):
    n, s = club['name'], club['sportId']
    c = []

    def add(x):
        x = (x or '').strip()
        if x and x not in c:
            c.append(x)

    if s == 'soccer':
        for suf in [' F.C.', ' FC', ' CF', ' S.C.', ' SC', ' AFC', ' AC', ' SV', ' (football club)']:
            add(n + suf)
        add(n)
        alt = n
        for a, b in UMLAUT:
            alt = alt.replace(a, b)
        if alt != n:
            for suf in [' F.C.', ' FC', ' (football club)', '']:
                add(alt + suf)
    elif s == 'basketball':
        add(n); add(n + ' (basketball)'); add(n + ' (NBA)')
    elif s == 'american-football':
        add(n); add(n + ' (American football)'); add(n + ' (NFL)')
    elif s == 'baseball':
        add(n); add(n + ' (baseball)'); add(n + ' (MLB)')
    elif s == 'motorsport':
        short = re.sub(r'\b(F1 Team|Formula 1 Team|F1)\b', '', n).strip()
        add(short); add(n)
        parts = short.split()
        if len(parts) > 1:
            add(' '.join(parts[1:]))
    elif s == 'cycling':
        add(n); add(n.replace('-', '–')); add(n + ' (cycling team)')
    else:
        add(n)
    return c


def detect(txt):
    low = txt.lower()
    if low.startswith('#redirect'):
        return None
    for pat, name in PATTERNS:
        if re.search(pat, low):
            return name
    return 'Unknown'


def fetch_licences(files, urls):
    by_host = {}
    for f in files:
        h = COMMONS if '/wikipedia/commons/' in urls.get(f, '') else EN
        by_host.setdefault(h, set()).add(f)
    out = {}
    for h, fs in by_host.items():
        for batch in chunk(sorted(fs), 40):
            d = api(h, {'action': 'query', 'titles': '|'.join(batch), 'redirects': '1',
                        'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main'})
            redir = {norm(x['from']): norm(x['to']) for x in d.get('query', {}).get('redirects', [])}
            for p in d.get('query', {}).get('pages', []):
                try:
                    v = detect(p['revisions'][0]['slots']['main']['content'])
                except Exception:
                    continue
                if v:
                    out[norm(p['title'])] = ('Commons: ' if h == COMMONS else '') + v
            for frm, to in redir.items():
                if to in out:
                    out[frm] = out[to]
            time.sleep(0.12)
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    clubs_dir = os.path.join(here, '..', 'data', 'clubs')
    clubs = [json.load(open(os.path.join(clubs_dir, f))) for f in sorted(os.listdir(clubs_dir)) if f.endswith('.json')]
    print(f'clubs: {len(clubs)}')

    cand_map, cand_prio = {}, {}
    for club in clubs:
        for i, t in enumerate(candidates(club)):
            if t not in cand_map:
                cand_map[t] = club['id']; cand_prio[t] = i
    titles = list(cand_map)
    print(f'candidate titles: {len(titles)}')

    pages = {}
    for bi, batch in enumerate(chunk(titles, 30)):
        got = api_all(EN, {'action': 'query', 'titles': '|'.join(batch),
                           'prop': 'images|pageimages', 'imlimit': 'max',
                           'piprop': 'original|name', 'pilicense': 'any', 'pilimit': 'max',
                           'redirects': '1'})
        for t, p in got.items():
            pages[t] = p
        if bi % 10 == 0:
            print(f'  batch {bi+1}: pages so far {len(pages)}')
        time.sleep(0.12)
    print(f'pages fetched: {len(pages)}')

    # map pages -> clubs
    best = {}
    for t, p in pages.items():
        cid = cand_map.get(t)
        if cid is None:
            continue
        if p.get('missing'):
            continue
        kits = [i['title'] for i in p.get('images', [])
                if 'kit body' in i['title'].lower() and i['title'].lower().endswith(('.png', '.jpg'))]
        prio = cand_prio.get(t, 99)
        sc = (0 if kits and kit_rank(min(kits, key=kit_rank)) < 20 else 5) + prio
        if cid not in best or sc < best[cid][0]:
            best[cid] = (sc, t, p)
    print(f'clubs matched: {len(best)}')

    rows = []
    for club in clubs:
        cid = club['id']
        if cid not in best:
            continue
        _, title, p = best[cid]
        f = pick_crest(p, club['name'])
        if f:
            rows.append({'club': cid, 'asset': 'crest', 'wikimedia_file': f,
                         'direct_url': 'TBD', 'license': 'check', 'wikipedia_page': p['title']})
        kits = [i['title'] for i in p.get('images', [])
                if 'kit body' in i['title'].lower() and i['title'].lower().endswith(('.png', '.jpg'))]
        kits.sort(key=kit_rank)
        seen = set()
        for k in kits[:8]:
            kt = kit_type(k)
            if kt in seen:
                continue
            seen.add(kt)
            rows.append({'club': cid, 'asset': kt, 'wikimedia_file': k,
                         'direct_url': 'TBD', 'license': 'check', 'wikipedia_page': p['title']})
    print(f'rows: {len(rows)}')

    # resolve urls
    files = sorted({r['wikimedia_file'] for r in rows})
    url_of = {}
    for batch in chunk(files, 40):
        d = api(EN, {'action': 'query', 'titles': '|'.join(batch), 'prop': 'imageinfo', 'iiprop': 'url'})
        for p in d.get('query', {}).get('pages', []):
            ii = p.get('imageinfo') or []
            if ii:
                url_of[norm(p['title'])] = ii[0]['url']
        time.sleep(0.12)
    # crests already may carry original from pageimages
    for r in rows:
        r['direct_url'] = url_of.get(norm(r['wikimedia_file']), '')
    rows = [r for r in rows if r['direct_url']]
    print(f'rows with url: {len(rows)}')

    urls = {r['wikimedia_file']: r['direct_url'] for r in rows}
    lic = fetch_licences(sorted(urls), urls)
    for r in rows:
        r['license'] = lic.get(norm(r['wikimedia_file']), 'Unknown')

    rows.sort(key=lambda r: (r['club'], r['asset']))
    with open(os.path.join(here, 'wikimedia-assets.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['club', 'asset', 'wikimedia_file', 'direct_url', 'license', 'wikipedia_page'])
        w.writeheader(); w.writerows(rows)

    print('\nassets:', dict(Counter(r['asset'] for r in rows)))
    print('licences:', dict(Counter(r['license'] for r in rows)))
    print('clubs:', len({r['club'] for r in rows}), '/', len(clubs))
    gen = [r for r in rows if r['asset'] == 'crest' and GENERIC.search(r['wikimedia_file'])]
    print('generic crests:', len(gen), [r['wikimedia_file'] for r in gen[:5]])
    badu = [r for r in rows if 'Unknown' in r['license']]
    print('unknown licences:', len(badu))


if __name__ == '__main__':
    main()
