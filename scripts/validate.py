"""Check every record in data/: the JSON Schemas in schema/, references between records, the
rating rule (METHOD.md) and the data rules (CONTRIBUTING.md). CI runs this on every pull request.

    pip install jsonschema
    python3 scripts/validate.py            # all records
    python3 scripts/validate.py --strict   # warnings fail too

Exit code 1 on errors. Warnings are printed and don't fail (unless --strict).
"""
import argparse
import os
import re
import sys

import jsonschema

from common import (DATA, PLACEHOLDER_TEXT, PLACEHOLDER_URL, SCHEMA, SEASON, TYPES, YEAR, claim_sources, current_kits,
                    kit_level, load, owner_chain, publisher, rating_hold, rating_owners, read_json, why_problem)

ap = argparse.ArgumentParser()
ap.add_argument('--strict', action='store_true', help='fail on warnings too')
args = ap.parse_args()

errors, warnings = [], []
err = lambda where, msg: errors.append(f'{where}: {msg}')
warn = lambda where, msg: warnings.append(f'{where}: {msg}')

R, P = load()

# ------------------------------------------------------------------ schemas and file names
for folder, (schema_name, key) in TYPES.items():
    validator = jsonschema.Draft202012Validator(read_json(os.path.join(SCHEMA, f'{schema_name}.schema.json')))
    for k, rec in R[folder].items():
        where = P[folder][k]
        for e in validator.iter_errors(rec):
            err(where, f"{'/'.join(map(str, e.path)) or '(record)'}: {e.message[:200]}")
        if os.path.basename(where) != f'{k}.json':
            err(where, f'file name must be {k}.json (the record\'s {key})')
for name in ['levels', 'tiers']:
    for e in jsonschema.Draft202012Validator(read_json(os.path.join(SCHEMA, f'{name}.schema.json'))).iter_errors(R[name]):
        err(f'data/{name}.json', e.message[:200])
for kind in ['sports', 'leagues']:
    listed = R['order'].get(kind, [])
    for k in R[kind]:
        if k not in listed:
            err('data/order.json', f'{kind}: "{k}" is missing (add it where it should appear on the site)')
    for k in listed:
        if k not in R[kind]:
            err('data/order.json', f'{kind}: "{k}" has no record in data/{kind}/')

# The old pipeline was replaced by data/ in the 2026-09-25 migration (docs/migration-2026-09-25.md).
for old in ('build_normalized.py', 'normalized', 'research'):
    if os.path.exists(os.path.join(os.path.dirname(DATA), old)):
        err(old, 'the old builder and its output were replaced by one file per record in data/ '
                 '(docs/migration-2026-09-25.md): edit data/ instead, and put research notes in the pull request')

if errors:  # references assume valid records
    print('\n'.join('error: ' + e for e in errors))
    sys.exit(1)

# ------------------------------------------------------------------ references
ids = {t: set(R[t]) for t in TYPES}
where_of = lambda t, k: P[t][k]


def ref(t, k, target, v):
    if v and v not in ids[target]:
        err(where_of(t, k), f'unknown {target[:-1] if target != "dropped" else target} "{v}"')


for k, x in R['leagues'].items():
    ref('leagues', k, 'sports', x['sportId'])
    n = sum(1 for c in R['clubs'].values() if c['leagueId'] == k)
    if x.get('clubCount') is not None and n > x['clubCount']:
        err(where_of('leagues', k), f'{n} clubs point here but clubCount is {x["clubCount"]}')
for k, x in R['clubs'].items():
    ref('clubs', k, 'sports', x['sportId'])
    ref('clubs', k, 'leagues', x['leagueId'])
for k, x in R['owners'].items():
    ref('owners', k, 'owners', x['parentId'])
    if x['parentId'] and k in owner_chain(R['owners'], x['parentId']):
        err(where_of('owners', k), 'owner chain loops back to itself')
for k, x in R['claims'].items():
    for o in x['ownerIds']:
        ref('claims', k, 'owners', o)
for k, x in R['sponsors'].items():
    ref('sponsors', k, 'owners', x['ownerId'])
    for c in x['claimIds']:
        ref('sponsors', k, 'claims', c)
for k, x in R['kits'].items():
    ref('kits', k, 'clubs', x['clubId'])
    for p in x['sponsors']:
        ref('kits', k, 'sponsors', p['sponsorId'])
for k, x in R['deals'].items():
    ref('deals', k, 'clubs', x['clubId'])
    ref('deals', k, 'sponsors', x['sponsorId'])
    ref('deals', k, 'leagues', x.get('leagueId'))
for t in ['changes', 'dropped']:
    for k, x in R[t].items():
        ref(t, k, 'clubs', x.get('clubId'))
        ref(t, k, 'sponsors', x.get('sponsorId'))
for k, x in R['contacts'].items():
    ref('contacts', k, 'clubs', x['clubId'])

# ------------------------------------------------------------------ the rating rule
owners, claims = R['owners'], R['claims']
for k, s in R['sponsors'].items():
    w = where_of('sponsors', k)
    if s['tier'] != 'unrated' and s['status'] != 'rated':
        err(w, f'tier "{s["tier"]}" needs status "rated"')
    if s['tier'] == 'unrated' and s['status'] == 'rated':
        err(w, 'status "rated" needs a tier other than "unrated"')
    if s['tier'] != 'unrated' and not s['claimIds']:
        err(w, f'tier "{s["tier"]}" needs at least one claim (for "none": the sourced ownership record)')
    if s['tier'] != 'unrated' and not s['ownerId']:
        err(w, f'tier "{s["tier"]}" needs an owner')
    reach = set(rating_owners(s, owners, claims))
    kinds = [claims[c].get('kind') for c in s['claimIds'] if c in claims]
    if s['tier'] != 'unrated' and 'ownership' not in kinds:
        err(w, f'tier "{s["tier"]}" needs an ownership claim: whose money it is (METHOD.md)')
    if s['tier'] == 'none' and 'record' in kinds:
        err(w, 'rated "none" but cites a record claim: a record that passes METHOD.md is a rating, and one that '
               'doesn\'t isn\'t cited')
    for c in s['claimIds']:
        if c in claims and claims[c].get('kind') == 'record' and not reach & set(claims[c]['ownerIds']):
            err(w, f'cites record claim "{c}", which is about an owner the link doesn\'t reach (not in the owner '
                   'chain, nor named in its ownership claims)')
    why = s.get('why')
    if why:
        for c in why['claimIds']:
            if c not in claims:
                err(w, f'why cites unknown claim "{c}"')
            elif c not in s['claimIds']:
                err(w, f'why cites claim "{c}", which the sponsor doesn\'t list in claimIds (the page lists its evidence)')
            elif not reach & set(claims[c]['ownerIds']):
                err(w, f'why cites claim "{c}", which is about an owner outside this sponsor\'s chain')
        if why['status'] != 'reviewed':
            warn(w, 'why text is a draft (status: draft)')
    problem = why_problem(s, claims)
    if problem:
        err(w, f'rated "{s["tier"]}": {problem}. METHOD.md: every rating above "none" names whose money it is and '
               'the human-rights record behind it. Fix the evidence or set the tier back.')
    hold = rating_hold(s, claims)
    if hold and not problem:
        warn(w, f'rated "{s["tier"]}" but published as not rated yet until the evidence is complete ({hold})')

# ------------------------------------------------------------------ sources and formats
DATE = re.compile(r'^\d{4}(-\d{2}(-\d{2})?)?$')


def source(where, s, required=False, what='source'):
    if not s:
        (err if required else warn)(where, f'no {what} yet')
        return
    url, name = s.get('url'), s.get('name') or ''
    if url and PLACEHOLDER_URL.match(url):
        err(where, f'{what} URL is a placeholder: {url}')
    if url and not re.match(r'^https?://', url):
        err(where, f'{what} URL must start with http(s)://: {url}')
    if re.match(r'(inference|assumption|estimated? by|guess)', name, re.I):
        err(where, f'{what} "{name}" is not a source: cite the document the fact comes from')
    if not url:
        warn(where, f'{what} "{name}" has no URL yet')
    if s.get('date') and not DATE.match(s['date']):
        warn(where, f'{what} date "{s["date"]}" should be YYYY, YYYY-MM or YYYY-MM-DD')
    if s.get('checked') and not (url and s.get('quote')):
        err(where, f'{what} "{name}" is marked checked but has no {"URL" if not url else "quote"}: '
                   'checked means someone opened the link and copied the words that support the fact')
    if s.get('quote') and not s.get('checked'):
        warn(where, f'{what} "{name}" has a quote but no "checked" (who opened the page, and when)')


for k, c in claims.items():
    source(where_of('claims', k), c['source'], required=True)
    for i, extra in enumerate(c.get('additionalSources') or []):
        source(where_of('claims', k), extra, required=True, what=f'additional source {i + 1}')
        if not extra.get('url'):
            err(where_of('claims', k), f'additional source {i + 1} needs a URL')
    pubs = [publisher(x.get('url')) for x in claim_sources(c) if x.get('url')]
    if len(pubs) != len(set(pubs)):
        warn(where_of('claims', k), 'two of its sources are from the same publisher, so they don\'t count as independent')
    if PLACEHOLDER_TEXT.search(c['text']):
        err(where_of('claims', k), 'claim text contains a placeholder')
cited = {c for s in R['sponsors'].values() for c in s['claimIds']} | {
    c for s in R['sponsors'].values() if s.get('why') for c in s['why']['claimIds']}
for k in claims:
    if k not in cited:
        warn(where_of('claims', k), 'no sponsor cites this claim')
for k, x in R['deals'].items():
    if x['value']:
        source(where_of('deals', k), x['source'], required=True)
    for f in ('from', 'to'):
        v = x.get(f)
        if v and not (SEASON.match(v) or YEAR.match(v)):
            err(where_of('deals', k), f'{f} "{v}" must be YYYY-YY or YYYY')
for k, x in R['kits'].items():
    w = where_of('kits', k)
    for p in x['sponsors']:
        if p.get('source'):
            source(w, p['source'], what=f'source for {p["sponsorId"]}')
        if p.get('hotspot') and not p.get('side'):
            err(w, f'sponsor "{p["sponsorId"]}" has a hotspot but no side')
        h = p.get('hotspot')
        if h and not all(0 <= h[a] <= 1 for a in 'xywh'):
            err(w, f'hotspot for "{p["sponsorId"]}" must use fractions between 0 and 1')
    # A kit's period is written like its season: seasons for a season kit (both ends set: the website sorts on them),
    # years for a calendar-year kit. A launch month such as 2026-05 is not a season.
    if SEASON.match(x.get('season') or ''):
        for f in ('season', 'periodFrom', 'periodTo'):
            v = x.get(f)
            if not (isinstance(v, str) and SEASON.match(v) and int(v[5:]) == (int(v[:4]) + 1) % 100):
                err(w, f'{f} {v!r} must be one season, e.g. 2026-27 (a kit worn for several seasons says so in periodFrom/periodTo)')
    elif re.match(r'^\d{4}$', x.get('season') or ''):
        for f in ('periodFrom', 'periodTo'):
            if x.get(f) is not None and not re.match(r'^\d{4}$', x[f]):
                err(w, f'{f} "{x[f]}" must be a year like the kit\'s season ({x["season"]})')
    if x.get('periodFrom') and x.get('periodTo') and x['periodFrom'] > x['periodTo']:
        err(w, 'periodFrom is after periodTo')
for t in ['changes', 'dropped']:
    for k, x in R[t].items():
        source(where_of(t, k), x.get('source'))
EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
for k, c in R['contacts'].items():
    for ch in c['channels']:
        if PLACEHOLDER_TEXT.search(ch['value']) or PLACEHOLDER_URL.match(ch['value']):
            err(where_of('contacts', k), f'placeholder value "{ch["value"]}"')
        if ch['type'] == 'email' and not EMAIL.match(ch['value']):
            err(where_of('contacts', k), f'not a valid email address "{ch["value"]}"')

# ------------------------------------------------------------------ league status
tier_of = lambda sid: R['sponsors'].get(sid, {}).get('tier', 'unrated')
cur = current_kits(R['kits'])
for k, lg in R['leagues'].items():
    clubs = [c for c in R['clubs'] if R['clubs'][c]['leagueId'] == k]
    n = sum(1 for c in clubs if c in cur and kit_level(cur[c], tier_of) != 'not-rated')
    total = lg.get('clubCount') or len(clubs)
    want = 'not-started' if n == 0 else 'complete' if n >= total else 'partial'
    if lg['status'] != want:
        warn(where_of('leagues', k), f'status "{lg["status"]}" but {n} of {total} clubs are rated: "{want}"')

for w in warnings:
    print('warning:', w)
for e in errors:
    print('error:', e)
n = sum(len(R[t]) for t in TYPES)
print(f'{len(errors)} errors, {len(warnings)} warnings in {n} records.')
sys.exit(1 if errors or (args.strict and warnings) else 0)
