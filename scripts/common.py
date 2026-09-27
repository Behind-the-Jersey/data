"""Shared helpers: load the records in data/, and the rating rule (METHOD.md).

Standard library only, so contributors and agents can run the scripts with a plain python3.
"""
import json
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
SCHEMA = os.path.join(ROOT, 'schema')

# folder in data/ -> (schema file, key field)
TYPES = {
    'sports': ('sport', 'id'),
    'leagues': ('league', 'id'),
    'clubs': ('club', 'id'),
    'owners': ('owner', 'id'),
    'claims': ('claim', 'id'),
    'sponsors': ('sponsor', 'id'),
    'kits': ('kit', 'id'),
    'deals': ('deal', 'id'),
    'changes': ('change', 'id'),
    'dropped': ('dropped', 'id'),
    'contacts': ('contact', 'clubId'),
}
# The dataset the website and other consumers read: one array per type, plus these.
BUNDLE = ['meta', 'levels', 'tiers'] + list(TYPES)


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load():
    """{type: {key: record}}, plus levels, tiers and order, and {type: {key: path}} for messages."""
    records, paths = {}, {}
    for folder, (_, key) in TYPES.items():
        records[folder], paths[folder] = {}, {}
        d = os.path.join(DATA, folder)
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not name.endswith('.json'):
                continue
            p = os.path.join(d, name)
            rec = read_json(p)
            records[folder][rec.get(key) if isinstance(rec, dict) else name[:-5]] = rec
            paths[folder][rec.get(key) if isinstance(rec, dict) else name[:-5]] = os.path.relpath(p, ROOT)
    records['levels'] = read_json(os.path.join(DATA, 'levels.json'))
    records['tiers'] = read_json(os.path.join(DATA, 'tiers.json'))
    records['order'] = read_json(os.path.join(DATA, 'order.json'))
    return records, paths


# ------------------------------------------------------------------ the rating rule (METHOD.md)

TIER_SCORE = {'unrated': None, 'none': 0, 'concern': 1, 'serious': 2, 'severe': 3}
LEVEL_ORDER = ['soaked', 'stained', 'spotted', 'clean', 'not-rated']


def kit_level(kit, tier_of):
    """A shirt's blood level from its sponsors' tiers and placements. Mirrors the website's lib/data/rating.ts."""
    if kit.get('levelOverride'):
        return kit['levelOverride']
    xs = [(p['placement'], TIER_SCORE[tier_of(p['sponsorId'])]) for p in kit['sponsors']]
    rated = [(pl, sc) for pl, sc in xs if sc is not None]
    if not rated:
        return 'not-rated'
    if any(sc == 3 and pl == 'front' for pl, sc in rated) or sum(sc >= 2 for _, sc in rated) >= 2:
        return 'soaked'
    if any(sc == 2 and pl == 'front' for pl, sc in rated) or any(sc == 3 and pl != 'front' for pl, sc in rated):
        return 'stained'
    if any(sc >= 1 for _, sc in rated):
        return 'spotted'
    return 'clean' if len(rated) == len(xs) and kit['sponsorsComplete'] else 'not-rated'


def kit_end(k):
    return k.get('periodTo') or k.get('season') or k.get('periodFrom') or ''


def current_kits(kits):
    """The latest home kit per club."""
    out = {}
    for k in kits.values():
        if k['kitType'] == 'home' and (k['clubId'] not in out or kit_end(k) >= kit_end(out[k['clubId']])):
            out[k['clubId']] = k
    return out


def owner_chain(owners, owner_id):
    out = []
    while owner_id and owner_id in owners and owner_id not in out:
        out.append(owner_id)
        owner_id = owners[owner_id].get('parentId')
    return out


# ------------------------------------------------------------------ the evidence standard (METHOD.md)

def claim_sources(claim):
    """A claim's source and its additional sources."""
    return [x for x in [claim.get('source'), *(claim.get('additionalSources') or [])] if x]


def source_checked(src):
    """Opened and confirmed: it has a link, words copied from the page, and who checked it when."""
    return bool(src and src.get('url') and src.get('quote') and src.get('checked'))


def publisher(url):
    """The site a link belongs to, to tell independent sources apart: www.hrw.org -> hrw.org."""
    host = (urllib.parse.urlsplit(url or '').hostname or '').lower()
    parts = host[4:].split('.') if host.startswith('www.') else host.split('.')
    two_part_tld = len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in {'co', 'com', 'org', 'net', 'gov', 'ac', 'or', 'ne', 'go'}
    return '.'.join(parts[-3:] if two_part_tld else parts[-2:])


def claim_checked(claim):
    """Every source on the claim is checked. Only checked claims are published."""
    xs = claim_sources(claim)
    return bool(xs) and all(source_checked(x) for x in xs)


def claim_corroborated(claim):
    """Checked, with sources from at least two different publishers."""
    return claim_checked(claim) and len({publisher(x['url']) for x in claim_sources(claim)}) >= 2


def cited_claims(sponsor):
    """The ids of every claim a sponsor cites: its claimIds, then its why's."""
    return list(dict.fromkeys(sponsor['claimIds'] + ((sponsor.get('why') or {}).get('claimIds') or [])))


def rating_owners(sponsor, owners, claims):
    """The owners a rating can rest on: the sponsor's owner chain, plus every owner named in the ownership
    claims it cites, with their chains. A record claim must be about one of them (METHOD.md: the record
    must be about someone the link reaches)."""
    out = owner_chain(owners, sponsor.get('ownerId'))
    for i in cited_claims(sponsor):
        if claims.get(i, {}).get('kind') == 'ownership':
            for o in claims[i]['ownerIds']:
                out += [x for x in owner_chain(owners, o) if x not in out]
    return out


def why_problem(sponsor, claims):
    """What a rating above "Nothing found" is missing, or None. Its why must cite the link (an ownership
    claim) and the record (a record claim) (METHOD.md)."""
    if not TIER_SCORE[sponsor['tier']]:
        return None
    why = sponsor.get('why')
    if not why:
        return 'no why text naming the link and the record'
    kinds = {claims[i].get('kind') for i in why['claimIds'] if i in claims}
    missing = [k for k in ('ownership', 'record') if k not in kinds]
    return 'the why cites no ' + ' and no '.join(f'{k} claim' for k in missing) if missing else None


def rating_hold(sponsor, claims):
    """Why a sponsor's rating can't be published yet, or None. A held rating is published as not rated yet.

    Every claim a rating rests on must be checked. Concern, Serious and Severe also need a why that cites
    the link and the record, and a second, independent source for each claim."""
    if sponsor['tier'] == 'unrated':
        return None
    ids = cited_claims(sponsor)
    unchecked = [i for i in ids if i in claims and not claim_checked(claims[i])]
    if unchecked:
        return 'evidence not checked yet: ' + ', '.join(unchecked)
    problem = why_problem(sponsor, claims)
    if problem:
        return problem
    if TIER_SCORE[sponsor['tier']]:
        single = [i for i in ids if i in claims and not claim_corroborated(claims[i])]
        if single:
            return 'needs a second, independent source: ' + ', '.join(single)
    return None


def published_sponsor(sponsor, claims):
    """The sponsor as the release publishes it: only checked claims, and a held rating as not rated yet."""
    out = dict(sponsor)
    out['claimIds'] = [i for i in sponsor['claimIds'] if i in claims and claim_checked(claims[i])]
    hold = rating_hold(sponsor, claims)
    why = sponsor.get('why')
    if why and (hold or not all(i in claims and claim_checked(claims[i]) for i in why['claimIds'])):
        del out['why']
    if hold:
        out.update(tier='unrated', status='being-rated', hold=hold, heldTier=sponsor['tier'])
    return out


SEASON = re.compile(r'^\d{4}-\d{2}$')
YEAR = re.compile(r'^\d{4}$')
PLACEHOLDER_URL = re.compile(r'^https?://(www\.)?(example\.(com|org|net)|localhost)\b', re.I)
PLACEHOLDER_TEXT = re.compile(r'X{3,}|\.\.\.|lorem ipsum', re.I)
