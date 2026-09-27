"""Build the published dataset from data/: dist/ with one JSON array per type (the format the
website reads), meta.json, and CSV files for spreadsheets. CI publishes dist/ as a GitHub release
on every merge to main; you can also run it locally.

    python3 scripts/build.py            # writes dist/
"""
import csv
import json
import os
import shutil
import subprocess
from datetime import date

from common import BUNDLE, ROOT, TYPES, claim_checked, current_kits, kit_level, load, owner_chain, published_sponsor

OUT = os.path.join(ROOT, 'dist')
R, _ = load()


def git(*a):
    try:
        return subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


# ------------------------------------------------------------------ arrays, in a stable order
def ordered(kind):
    recs = R[kind]
    if kind in ('sports', 'leagues'):
        return [recs[k] for k in R['order'][kind]]
    if kind == 'changes':
        return sorted(recs.values(), key=lambda x: (x['date'], x['id']), reverse=True)
    if kind == 'dropped':
        return sorted(recs.values(), key=lambda x: (-x['year'], x['id']))
    return [recs[k] for k in sorted(recs)]


bundle = {kind: ordered(kind) for kind in TYPES}
# What the release publishes (METHOD.md, the evidence standard): only checked claims on sponsors, and a
# rating whose evidence isn't complete as not rated yet (tier "unrated", status "being-rated", with
# "hold" saying why and "heldTier" the tier it would have). claims.json keeps every claim.
bundle['sponsors'] = [published_sponsor(s, R['claims']) for s in bundle['sponsors']]
_tier = {s['id']: s['tier'] for s in bundle['sponsors']}
_cur = current_kits(R['kits'])
for lg in bundle['leagues']:
    # League status follows what's published: none rated, some, or all.
    ids = [c['id'] for c in bundle['clubs'] if c['leagueId'] == lg['id']]
    n = sum(1 for c in ids if c in _cur and kit_level(_cur[c], lambda s: _tier.get(s, 'unrated')) != 'not-rated')
    total = lg.get('clubCount') or len(ids)
    lg['status'] = 'not-started' if n == 0 else 'complete' if n >= total else 'partial'
bundle['levels'] = R['levels']
bundle['tiers'] = R['tiers']
bundle['meta'] = {
    'schemaVersion': 1,
    'updatedAt': git('log', '-1', '--format=%cs', '--', 'data') or date.today().isoformat(),
    'generatedBy': 'Behind-the-Jersey/data scripts/build.py',
    'sourceCommit': git('rev-parse', '--short', 'HEAD'),
}

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for name in BUNDLE:
    with open(os.path.join(OUT, f'{name}.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(bundle[name], ensure_ascii=False, indent=2) + '\n')

# ------------------------------------------------------------------ CSV for spreadsheets
S, O, C = {s['id']: s for s in bundle['sponsors']}, R['owners'], R['claims']
tier_of = lambda sid: S.get(sid, {}).get('tier', 'unrated')
cur = current_kits(R['kits'])
league = lambda lid: R['leagues'][lid]['name'] if lid in R['leagues'] else ''
state_owner = lambda s: next((O[o]['name'] for o in owner_chain(O, s['ownerId']) if O[o]['type'] in ('state', 'state-fund')), '')
src = lambda s: ((s or {}).get('name', ''), (s or {}).get('date', ''), (s or {}).get('url') or '')


def write_csv(name, header, rows):
    with open(os.path.join(OUT, f'{name}.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


write_csv('clubs', ['id', 'name', 'sport', 'league', 'country', 'level', 'current_kit', 'sponsors_on_current_kit'], [
    [c['id'], c['name'], c['sportId'], league(c['leagueId']), c['country'] or '',
     kit_level(cur[c['id']], tier_of) if c['id'] in cur else 'not-rated',
     cur[c['id']]['id'] if c['id'] in cur else '',
     '; '.join(f"{S[p['sponsorId']]['name']} ({p['placement']})" for p in cur[c['id']]['sponsors']) if c['id'] in cur else '']
    for c in bundle['clubs']])
write_csv('sponsors', ['id', 'name', 'tier', 'status', 'held_tier', 'hold', 'owner', 'owner_chain', 'state_owner', 'claims',
                       'on_current_kits'], [
    [s['id'], s['name'], s['tier'], s['status'], s.get('heldTier', ''), s.get('hold', ''),
     O[s['ownerId']]['name'] if s['ownerId'] in O else '',
     ' > '.join(O[o]['name'] for o in owner_chain(O, s['ownerId'])), state_owner(s), len(s['claimIds']),
     '; '.join(R['clubs'][k['clubId']]['name'] for k in cur.values() if any(p['sponsorId'] == s['id'] for p in k['sponsors']))]
    for s in bundle['sponsors']])
write_csv('claims', ['id', 'text', 'owners', 'source_name', 'source_date', 'source_url', 'more_source_urls', 'checked',
                     'reviewed'], [
    [c['id'], c['text'], '; '.join(O[o]['name'] for o in c['ownerIds'] if o in O), *src(c['source']),
     ' '.join(x.get('url') or '' for x in c.get('additionalSources') or []), claim_checked(c), c['reviewed']]
    for c in bundle['claims']])
write_csv('kit_sponsors', ['kit', 'club', 'season', 'kit_type', 'sponsor', 'placement', 'source_name', 'source_date', 'source_url'], [
    [k['id'], R['clubs'][k['clubId']]['name'], k['season'] or '', k['kitType'], S[p['sponsorId']]['name'], p['placement'],
     *src(p.get('source'))]
    for k in bundle['kits'] for p in k['sponsors']])
write_csv('deals', ['id', 'club_or_org', 'league', 'sponsor', 'placement', 'from', 'to', 'amount', 'currency', 'unit', 'per',
                    'up_to', 'usd_approx', 'source_name', 'source_date', 'source_url'], [
    [d['id'], R['clubs'][d['clubId']]['name'] if d['clubId'] in R['clubs'] else (d['orgName'] or ''), league(d.get('leagueId')),
     S[d['sponsorId']]['name'], d['placement'], d['from'] or '', d['to'] or '',
     *((d['value'][k] if d['value'] else '') for k in ('amount', 'currency', 'unit', 'per', 'upTo', 'usdApprox')),
     *src(d['source'])]
    for d in bundle['deals']])

# One download with everything (built next to dist/, then moved in, so it doesn't include itself).
zip_path = shutil.make_archive(os.path.join(ROOT, 'behind-the-jersey-data'), 'zip', OUT)
shutil.move(zip_path, os.path.join(OUT, os.path.basename(zip_path)))
print(f"dist/: {', '.join(f'{k} {len(v)}' for k, v in bundle.items() if isinstance(v, list))}; "
      f"meta {bundle['meta']['updatedAt']} {bundle['meta']['sourceCommit']}")
