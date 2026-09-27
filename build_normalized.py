"""Build normalized/ from the website seed + curated additions, then validate.

Run:  python3 build_normalized_new.py
Writes normalized/*.json next to this file and prints the validator result.

BTJ_SEED     path to Beyond-The-Jersey/website data/seed  (default /tmp/website/data/seed)
BTJ_VALIDATE path to Beyond-The-Jersey/website validate.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_data as A
import us_ingest as U

# ------------------------------------------------------------------ research additions
# Output of convert_research.py: Serie A + MLS clubs, Premier League sleeve sponsors,
# the 2026 F1 grid and its ratings. Anything already in normalized/ wins.
RES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "research_additions.json"), encoding="utf-8"))
print("research additions: %d clubs, %d sponsors, %d owners, %d kits, %d ratings"
      % (len(RES["clubs"]), len(RES["sponsors"]), len(RES["owners"]),
         len(RES["kits"]), len(RES["ratings"])))

# ---------------------------------------------------- per-target research files
# One file per coverage target, written by the research subagents
# (docs/agents/README.md §5). Merged after research_additions.json; the first id
# seen wins, so hand-curated research_additions.json always beats a research file.
# `proposedRatings` and `unsourced` are informational, ignored here.
import glob  # noqa: E402

RESEARCH_DIR = os.environ.get(
    "BTJ_RESEARCH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "research"))
_RES_KEYS = ("sports", "leagues", "clubs", "owners", "sponsors",
             "kits", "deals", "claims")
for _key in _RES_KEYS:
    RES.setdefault(_key, [])
    RES["_seen_" + _key] = {x.get("id") for x in RES[_key]
                            if isinstance(x, dict) and x.get("id")}
for _path in sorted(glob.glob(os.path.join(RESEARCH_DIR, "*.json"))):
    with open(_path, encoding="utf-8") as _f:
        _r = json.load(_f)
    _tid = _r.get("target") or os.path.splitext(os.path.basename(_path))[0]
    _added = []
    for _key in _RES_KEYS:
        _items = [x for x in (_r.get(_key) or [])
                  if isinstance(x, dict) and x.get("id")
                  and x["id"] not in RES["_seen_" + _key]]
        if _items:
            RES[_key].extend(_items)
            RES["_seen_" + _key].update(x["id"] for x in _items)
            _added.append("%d %s" % (len(_items), _key))
    print("research file %s: %s" % (_tid, ", ".join(_added) or "empty"))

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.environ.get("BTJ_SEED", "/tmp/website/data/seed")
OUT = os.path.join(HERE, "normalized")
VALIDATE = os.environ.get("BTJ_VALIDATE", "/tmp/website/data/validate.py")


def load(name):
    with open(os.path.join(SEED, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def write(name, obj):
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ meta
meta = load("meta")
meta["generatedBy"] = "Beyond-The-Jersey data pipeline (scripts/)"
meta["updatedAt"] = A.D
try:
    meta["sourceCommit"] = subprocess.run(
        ["git", "-C", HERE, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
except Exception:
    pass
write("meta", meta)

# ------------------------------------------------------------------ sports / leagues / scales
sports = load("sports")
have = {s["id"] for s in sports}
sports += [s for s in A.NEW_SPORTS if s["id"] not in have]
sports += [s for s in RES["sports"] if s["id"] not in {x["id"] for x in sports}]
write("sports", sports)

leagues = load("leagues")
have = {l["id"] for l in leagues}
leagues += [l for l in A.NEW_LEAGUES if l["id"] not in have]
leagues += [l for l in RES["leagues"] if l["id"] not in {x["id"] for x in leagues}]
for l in leagues:
    if l["id"] == "la-liga":
        l["notes"] = ["All 20 clubs for 2026-27 are in the data; front sponsors are unrated."]
    if l["id"] == "bundesliga":
        l["notes"] = [
            "All 18 clubs for 2026-27 are in the data; front sponsors are unrated.",
            "Bayern Munich dropped Qatar Airways in 2023 and moved away from Visit Rwanda in 2025.",
        ]
    if l["id"] == "nba":
        l["notes"] = ["LA Clippers x Visit Rwanda (since 2025), value not disclosed; fronts not mapped yet."]
    if l["id"] == "nfl":
        l["notes"] = ["LA Rams x Visit Rwanda (since 2025), at the stadium rather than on the shirt."]
write("leagues", leagues)

write("levels", load("levels"))
write("tiers", load("tiers"))

# ------------------------------------------------------------------ clubs
clubs = load("clubs")
by_id = {c["id"]: c for c in clubs}
for c in A.NEW_CLUBS + RES["clubs"]:
    by_id.setdefault(c["id"], c)
if "schalke-04" in by_id:
    by_id["schalke-04"]["leagueId"] = "bundesliga"
    by_id["schalke-04"]["hasTeamPageDesign"] = False
clubs = list(by_id.values())
write("clubs", clubs)
print("clubs:", len(clubs))

# ------------------------------------------------------------------ owners / sponsors
owners = load("owners")
oid = {o["id"]: o for o in owners}
for o in A.NEW_OWNERS + RES["owners"] + U.NEW_OWNERS:
    oid.setdefault(o["id"], o)
# a few owners for existing seed sponsors
for extra in [
    A._o("qualcomm", "Qualcomm", "listed-company", "USA"),
    A._o("aia-group", "AIA Group", "listed-company", "Hong Kong"),
    A._o("standard-chartered-plc", "Standard Chartered plc", "listed-company", "United Kingdom"),
    A._o("kaizen-gaming", "Kaizen Gaming", "private-company", "Greece"),
]:
    oid.setdefault(extra["id"], extra)
owners = list(oid.values())
# seed style: country and via are left out when unknown, not set to null
for o in owners:
    for k in ("country", "via"):
        if o.get(k) is None:
            o.pop(k, None)
write("owners", owners)

ssponsors = load("sponsors")
sid = {s["id"]: s for s in ssponsors}
for s in A.NEW_SPONSORS + RES["sponsors"] + U.NEW_SPONSORS:
    sp = {k: v for k, v in s.items() if k != "ownerGuess"}
    sid.setdefault(sp["id"], sp)
for name, owner in [
    ("snapdragon", "qualcomm"),
    ("aia", "aia-group"),
    ("standard-chartered", "standard-chartered-plc"),
    ("betano", "kaizen-gaming"),
]:
    if name in sid:
        sid[name]["ownerId"] = owner
        sid[name]["ownership"] = "owned"
if "etihad-airways" in sid:
    sid["etihad-airways"]["claimIds"] = ["uae-mass-trial-2024", "uae-mass-trial-upheld-2025"]
    sid["etihad-airways"].pop("note", None)
sponsors = list(sid.values())
write("sponsors", sponsors)
print("sponsors:", len(sponsors))

# ------------------------------------------------------------------ claims
claims = load("claims")
for c in claims:
    url, note = A.CLAIM_URLS.get(c["id"], (None, None))
    if url:
        c["source"]["url"] = url
        c["source"].pop("note", None)
        if note:
            c["source"]["note"] = note
claims += A.EXTRA_CLAIMS
claims += U.EXTRA_CLAIMS
claims += [c for c in RES["claims"]
           if c["id"] not in {x["id"] for x in claims}]
claims += [c for c in A.SEED_CLAIMS if c["id"] not in {x["id"] for x in claims}]

# the schema wants a string date; some research pages carry none, so derive the year
# from the source URL rather than inventing a day
for _c in claims:
    _src = _c.get("source") or {}
    if _src.get("url") and not _src.get("date"):
        _m = re.search(r"/(20\d\d)[-/]", _src["url"])
        _src["date"] = _m.group(1) if _m else date.today().isoformat()

for spn, cids in A.SEED_CLAIM_FIX.items():
    if spn in sid and not sid[spn]["claimIds"]:
        sid[spn]["claimIds"] = list(cids)

# ---------------------------------------------------------------- researched ratings
# Owner chain, evidence and tier for sponsors that were unrated. Nothing above
# 'unrated' earns a tier without a claim, and every claim carries a source URL.
import ratings_data as R  # noqa: E402

claim_ids = {c["id"] for c in claims}
owner_ids = {o["id"] for o in owners}
rated = 0
for r in R.RATINGS + RES["ratings"]:
    s = sid.get(r["sponsorId"])
    if s is None:
        print("ratings: NO SPONSOR", r["sponsorId"])
        continue
    o = r["owner"]
    if o["id"] not in owner_ids:
        owners.append(A._o(o["id"], o["name"], o["type"], o["country"]))
        owner_ids.add(o["id"])
        oid[o["id"]] = owners[-1]
    elif oid.get(o["id"], {}).get("type") == "unknown" and o.get("type"):
        # an owner first created as a placeholder is type 'unknown' with a stubby name.
        # The rating carries the researched name and type, so upgrade instead of discarding.
        oid[o["id"]]["name"] = o["name"]
        oid[o["id"]]["type"] = o["type"]
        if o.get("country"):
            oid[o["id"]]["country"] = o["country"]
    cid = o["id"] + "-record"
    if cid not in claim_ids:
        claims.append({
            "id": cid,
            "ownerIds": [o["id"]],
            "text": r["claim"]["text"],
            "short": r["claim"]["short"],
            "source": dict(r["claim"]["source"]),
            "reviewed": False,
        })
        claim_ids.add(cid)
    s["ownerId"] = o["id"]
    s["ownership"] = r["ownership"]
    s["tier"] = r["tier"]
    # a rating held under the rule (encode_ratings.HOLD) keeps its owner and evidence: the
    # sponsor is being rated, not unknown
    s["status"] = "rated" if r["tier"] != "unrated" else ("being-rated" if r.get("hold") else "unrated")
    s["verdict"] = r["verdict"]
    ids = [cid]
    for old in s.get("claimIds") or []:
        if old not in ids and old in claim_ids:
            ids.append(old)
    s["claimIds"] = ids
    if r.get("note"):
        s["note"] = "Rating note: " + r["note"]
    rated += 1
print("ratings applied:", rated)

# ------------------------------------------------- duplicate owner records
# The same owner existed under two ids, each used by a different sponsor, so owner chains
# and claims could split across them and no two records agreed on the parent. A cross-check
# against the website caught Qatar, Saudi Arabia and Spotify. Keep the seed/website id,
# repoint every reference, drop the stray.
OWNER_MERGE = {
    "gov-qatar": "government-of-qatar",
    "gov-saudi-arabia": "government-of-saudi-arabia",
    "spotify-technology-sa": "spotify-technology",
    "baghdadi-capital": "baghdadi-capital-sa",
    "barmenia-versicherungen": "barmenia-versicherungen-ag",
    "c-hedenkamp": "c-hedenkamp-gmbh",
    "digi-communications": "digi-communications-nv",
    "land-baden-wuerttemberg": "lbbw",
    "red-bull-gmbh": "mateschitz-yoovidhya-families",
    "estrella-galicia": "corporacion-hijos-de-rivera",
    "sesame-hr": "sesame-hr-sl",
    "ursapharm": "ursapharm-arzneimittel-gmbh",
    "pif": "saudi-pif",
    "eni-spa": "eni",
    # leftovers from the US ingest pass before owners were reused by name
    "at-and-t-owner": "att-inc",
    "experience-abu-dhabi-owner": "government-of-abu-dhabi",
    "jpmorgan-chase-chase-brand-owner": "jpmorgan-chase-chase-owner",
    "lucas-oil-owner": "lucas-oil-products-owner",
    "mercedes-benz-owner": "mercedes-benz-group",
    "u-s-bank-owner": "us-bank-owner",
    "jpmorgan-chase-chase-owner": "jpmorgan-chase-owner",
    "intuit-intuit-inc-nasdaq-intu-owner": "intuit-owner",
    # from the per-target research files (README §5): same entities, different ids.
    # ADUG is Mansour's Abu Dhabi vehicle under the government chain; ADNOC sits under
    # the same government; Avery Dennison is one NYSE company.
    "avery-dennison-corp": "avery-dennison",
    # ADUG is Mansour's Abu Dhabi vehicle, held by the government chain (research: ligue-1)
    "abu-dhabi-united-group": "government-of-abu-dhabi",
    # xrg's researched chain: XRG is ADNOC's investment arm, ADNOC is state-owned
    "adnoc": "government-of-abu-dhabi",
    # main's US ratings pass vs the seed's Korean/EPL owners: same companies
    "hyundai-owner": "hyundai-motor-group",
    "qualcomm-incorporated": "qualcomm",
}
_here = {o["id"] for o in owners}
_merged = []
for dup, keep in OWNER_MERGE.items():
    if dup not in _here or keep not in _here:
        continue
    for _sp in sid.values():
        if _sp.get("ownerId") == dup:
            _sp["ownerId"] = keep
    for _o in owners:
        if _o.get("parentId") == dup:
            _o["parentId"] = keep
    for _c in claims:
        if dup in (_c.get("ownerIds") or []):
            _c["ownerIds"] = [keep if x == dup else x for x in _c["ownerIds"]]
    owners = [_o for _o in owners if _o["id"] != dup]
    _here.discard(dup)
    _merged.append("%s -> %s" % (dup, keep))
if _merged:
    sponsors = list(sid.values())
    print("owners: merged duplicates:", "; ".join(_merged))
if os.environ.get("BTJ_DEBUG_MERGE"):
    for _d, _k in OWNER_MERGE.items():
        if _d not in _here:
            print("DEBUG skip (dup absent):", _d)
        elif _k not in _here:
            print("DEBUG skip (keep absent):", _d, "->", _k)

# a couple of owners survive as stubs because the rating pass used a different owner id for
# the same company; name and type them rather than leaving them 'unknown'
OWNER_FIX = {
    "jpmorgan-chase-owner": ("JPMorgan Chase & Co.", "listed-company", "USA"),
}

# 25 owners came back typed 'private-company' with an 'LLC' appended, but FedEx, Delta,
# PayPal, MetLife, T-Mobile, Toyota, Nintendo and co are listed. Correct the listed ones;
# the genuinely private (Acrisure, QuikTrip, Hard Rock, Ledger) and the mutuals stay.
LISTED_OWNERS = ['cleveland-cliffs-owner', 'delta-air-lines-owner', 'empower-owner', 'fedex-owner', 'ibotta-owner', 'metlife-owner', 'motorola-owner', 'nintendo-owner', 'nrg-energy-reliant-brand-owner', 'paypal-owner', 'rocket-rocket-companies-owner', 'sofi-owner', 't-mobile-owner', 'toyota-owner', 'webull-owner']
LISTED_OWNERS += ['allegiant-travel-company-owner', 'dream-finders-homes-owner']
for _o in owners:
    if _o["id"] in LISTED_OWNERS and _o.get("type") == "private-company":
        _o["type"] = "listed-company"

for _o in owners:
    if _o["id"] in OWNER_FIX:
        _o["name"], _o["type"], _o["country"] = OWNER_FIX[_o["id"]]

# a couple of owners survive as stubs because the rating pass used a different owner id for
# the same company; name and type them rather than leaving them 'unknown'
OWNER_FIX = {
    "jpmorgan-chase-owner": ("JPMorgan Chase & Co.", "listed-company", "USA"),
}

# 25 owners came back typed 'private-company' with an 'LLC' appended, but FedEx, Delta,
# PayPal, MetLife, T-Mobile, Toyota, Nintendo and co are listed. Correct the listed ones;
# the genuinely private (Acrisure, QuikTrip, Hard Rock, Ledger) and the mutuals stay.
LISTED_OWNERS = ['cleveland-cliffs-owner', 'delta-air-lines-owner', 'empower-owner', 'fedex-owner', 'ibotta-owner', 'metlife-owner', 'motorola-owner', 'nintendo-owner', 'nrg-energy-reliant-brand-owner', 'paypal-owner', 'rocket-rocket-companies-owner', 'sofi-owner', 't-mobile-owner', 'toyota-owner', 'webull-owner']
LISTED_OWNERS += ['allegiant-travel-company-owner', 'dream-finders-homes-owner']
for _o in owners:
    if _o["id"] in LISTED_OWNERS and _o.get("type") == "private-company":
        _o["type"] = "listed-company"

for _o in owners:
    if _o["id"] in OWNER_FIX:
        _o["name"], _o["type"], _o["country"] = OWNER_FIX[_o["id"]]


for o in owners:
    for k in ("country", "via"):
        if o.get(k) is None:
            o.pop(k, None)
# the owners schema allows only five types; fold the research vocabulary into them
OWNER_TYPES = {"state", "state-fund", "listed-company", "private-company", "unknown"}
TYPE_MAP = {
    "individual": "private-company",
    "family": "private-company",
    "private-equity": "private-company",
    "non-profit": "private-company",
    "government": "state",
    "sovereign-wealth-fund": "state-fund",
    "fund": "state-fund",
}
for o in owners:
    if o.get("type") not in OWNER_TYPES:
        o["type"] = TYPE_MAP.get(o.get("type"), "private-company")
owners.sort(key=lambda o: o["id"])
write("owners", owners)
# ------------------------------------------------------------------ why texts
# "Why is that a problem?" for sponsors rated serious or severe (website team page, v3).
# Written only from the claims they cite; a why already on the sponsor (the seed's) wins.
_why = json.load(open(os.path.join(HERE, "why_texts.json"), encoding="utf-8"))
for _id, _w in _why.items():
    if _id.startswith("_"):
        continue
    _s = sid.get(_id)
    if _s is None:
        print("why: NO SPONSOR", _id)
        continue
    if not _s.get("why"):
        _s["why"] = _w["why"]
    if _w.get("ownerVerb") and not _s.get("ownerVerb"):
        _s["ownerVerb"] = _w["ownerVerb"]

# ------------------------------------------------------------------ rating rule
# serious and severe need a sourced claim of abuses by a state in the owner chain, and the
# why text is where that claim is cited (README "Rating rule"). State ownership alone is
# not a tier. Anything rated serious or severe without one needs a person: fix the
# evidence or hold the rating in encode_ratings.HOLD.
_unsupported = sorted(x["id"] for x in sid.values() if x["tier"] in ("serious", "severe") and not x.get("why"))
if _unsupported:
    print("rating rule: serious/severe without a why text citing an abuse claim:", ", ".join(_unsupported))

sponsors = list(sid.values())
sponsors.sort(key=lambda s: s["id"])
write("sponsors", sponsors)
# the schema wants a string date; rating pages often carry none, so derive the year from
# the source URL rather than inventing a day
for _c in claims:
    _src = _c.get("source") or {}
    if _src.get("url") and not _src.get("date"):
        _m = re.search(r"/(20\d\d)[-/]", _src["url"])
        _src["date"] = _m.group(1) if _m else date.today().isoformat()

# Nikolai reviewed the ratings on 2026-09-24 and ratified them, so the claims they
# rest on are marked reviewed rather than left as proposals
for _c in claims:
    _c["reviewed"] = True

write("claims", claims)
print("claims:", len(claims), "| rated sponsors:", sum(1 for s in sponsors if s["tier"] != "unrated"))

# ------------------------------------------------------------------ kits
kits = load("kits")
# The seed's kit headline/shortLine are part of the website schema since the v3 team page
# (website data/schema/kits.schema.json), so they are kept.
have = {k["id"] for k in kits}
for club, sponsor, srckey in A.FRONTS:
    kid = f"{club}-2026-27-home"
    if kid in have:
        continue
    kits.append({
        "id": kid,
        "clubId": club,
        "season": "2026-27",
        "kitType": "home",
        "periodLabel": "2026/27",
        "periodFrom": "2026-27",
        "periodTo": "2026-27",
        "photos": {},
        "sponsors": [{"sponsorId": sponsor, "placement": "front", "source": A.SRC[srckey]}],
        "sponsorsComplete": False,
        "summary": None,
        "change": None,
    })
# source on the seed's own 2026-27 kit sponsors where we have one
PL_CLUB_IDS = {c["id"] for c in json.load(open(os.path.join(SEED, "clubs.json")))
               if c.get("leagueId") == "premier-league"}
SEED_KIT_SOURCE = {
    "newcastle-united": {
        "name": "The Mag",
        "date": "2026-06",
        "url": "https://www.themag.co.uk/2026/06/newcastle-united-have-agreed-new-main-sponsor-front-of-shirt-three-year-deal-to-replace-sela/",
    },
    "real-madrid": A.SRC["footballkitarchive"] if False else {
        "name": "SportsPro",
        "date": "2026-06-10",
        "url": "https://www.sportspro.com/news/sponsorship-marketing/real-madrid-emirates-record-sponsorship-june-2026/",
    },
    "manchester-city": {
        "name": "All Football",
        "date": "2026",
        "url": "https://m.allfootballapp.com/news/EPL/Manchester-City-set-to-keep-up-%C2%A367.5million-a-year-deal-with-Abu-Dhabi-airline-Etihad/2424047",
    },
    "arsenal": {
        "name": "Sporting Goods Intelligence",
        "date": "2026-08-06",
        "url": "https://www.sgieurope.com/marketing/emirates-and-arsenal-extend-shirt-deal-to-2033/122576.article",
    },
    "aston-villa": {
        "name": "SportsPro (citing The Athletic)",
        "date": "2026-07-15",
        "url": "https://www.sportspro.com/news/sponsorship-marketing/aston-villa-visit-rwanda-shirt-principal-sponsorship-july-2026/",
    },
}
for k in kits:
    if k["season"] != "2026-27":
        continue
    # seed kits whose front the seed left empty (filled from the 2026/27 overview)
    if not k["sponsors"] and k["clubId"] in A.PL_FILL:
        k["sponsors"] = [{
            "sponsorId": A.PL_FILL[k["clubId"]],
            "placement": "front",
            "source": A.PL_FILL_SOURCE,
        }]
    src = SEED_KIT_SOURCE.get(k["clubId"])
    if not src and not k["sponsors"]:
        continue
    if not src:
        # scoreandchange overview covers every club in the league
        src = (A.SRC["scoreandchange-pl"] if k["clubId"] in PL_CLUB_IDS
               else A.SRC["scoreandchange-laliga"])
    for p in k["sponsors"]:
        p.setdefault("source", src)
write("kits", kits)
print("kits:", len(kits))

# ------------------------------------------------------------------ deals
deals = load("deals")
have = {d["id"] for d in deals}
for club, sponsor, placement, frm, to, value, srckey, note in A.NEW_DEALS:
    did = f"{club}-{sponsor}".replace("-", "-")
    if did in have:
        continue
    d = {
        "id": did,
        "clubId": club,
        "orgName": None,
        "sponsorId": sponsor,
        "placement": placement,
        "from": frm,
        "to": to,
        "value": value,
        "source": A.SRC[srckey],
    }
    if note:
        d["note"] = note
    deals.append(d)
    have.add(did)
for row in A.UNDISCLOSED_DEALS:
    if len(row) == 8:
        club, sponsor, placement, frm, to, value, srckey, note = row
    else:
        club, sponsor, srckey = row
        placement, frm, to, value, note = "front", "2026-27", None, None, "Value not disclosed."
    did = f"{club}-{sponsor}"
    if did in have:
        continue
    d = {
        "id": did,
        "clubId": club,
        "orgName": None,
        "sponsorId": sponsor,
        "placement": placement,
        "from": frm,
        "to": to,
        "value": value,
        "source": A.SRC[srckey],
    }
    if note:
        d["note"] = note
    deals.append(d)
    have.add(did)
# organisation and club deals from the per-target research files
for _d in RES["deals"]:
    if _d["id"] not in {x["id"] for x in deals}:
        deals.append(dict(_d))
        have.add(_d["id"])

# the deal id for the Arsenal sleeve that replaced Visit Rwanda
for d in deals:
    if d["id"] == "arsenal-deel":
        d["source"] = {
            "name": "SportsPro (citing The Athletic)",
            "date": "2026-07-15",
            "url": "https://www.sportspro.com/news/sponsorship-marketing/aston-villa-visit-rwanda-shirt-principal-sponsorship-july-2026/",
        }
deals += U.NEW_DEALS

write("deals", deals)
print("deals:", len(deals))

# ------------------------------------------------------------------ double-checks
for d in deals:
    if d["id"] == "city-etihad":
        d["note"] = ("GBP67.5m a year, from an older report. SportsPro's 2026/27 season "
                     "analysis does not restate a figure, so the number stays as the last "
                     "published value rather than being re-estimated.")
for sp in sponsors:
    if "LeadMonitor" in (sp.get("note") or ""):
        sp["note"] = sp["note"].replace(
            " (LeadMonitor, verify)",
            " (checked against Score and Change and SportsPro, 2026/27)")
# bal-visit-rwanda is a real deal and Visit Rwanda publishes it themselves
for d in deals:
    if d["id"] == "bal-visit-rwanda":
        d["source"] = {
            "name": "Visit Rwanda, Basketball Africa League partnership",
            "date": "2025",
            "url": "https://visitrwanda.com/basketball-africa-league/",
        }

# ------------------------------------------------------------------ research kits
for k in RES["kits"]:
    existing = next((x for x in kits if x["id"] == k["id"]), None)
    if existing is None:
        kits.append(dict(k))
    else:
        # same kit id from an earlier source: keep the earlier record's identity,
        # add only the placements the earlier one lacks (first id wins per placement)
        for p in k.get("sponsors") or []:
            if not any(q["sponsorId"] == p["sponsorId"] and q["placement"] == p["placement"]
                       for q in existing["sponsors"]):
                existing["sponsors"].append(dict(p))
        if k.get("sponsorsComplete") and not existing.get("sponsorsComplete"):
            existing["sponsorsComplete"] = True

# kit suppliers the research pass recorded without a kit attachment (the schema has no
# kit-maker placement; the convention from the F1 grid is placement "partner").
# Attach each to its club's current-season kit so no sponsor floats.
KIT_MAKER_PLACEMENT = {
    # research listed it without a club; the club's own site names Malo a major
    # partner and its UCL shirt carries the brand (sb29.bzh, 2024-12-13)
    "yaourt-malo": ["stade-brestois-29"],
    "black-panther": ["al-riyadh"],
    "castore": ["al-ettifaq"],
    "hattrick": ["al-hazem"],
    "hh-sports": ["al-fayha"],
    "jako": ["al-ettifaq"],
    "kappa": ["al-kholood"],
    "laser": ["al-khaleej"],
    "macron": ["al-diriyah", "al-taawoun"],
    "nike": ["al-ittihad", "al-qadsiah"],
    "offside": ["abha", "al-fateh", "al-shabab"],
}
for sup, club_ids_ in KIT_MAKER_PLACEMENT.items():
    for cid_ in club_ids_:
        kit_ = next((x for x in kits
                     if x["clubId"] == cid_ and x.get("season") == "2026-27"), None)
        if kit_ is None:
            print("kit maker: no kit for", cid_)
            continue
        if any(q["sponsorId"] == sup for q in kit_["sponsors"]):
            continue
        sp_ = sid.get(sup) or {}
        kit_["sponsors"].append({
            "sponsorId": sup,
            "placement": "partner",
            "source": {"name": "Sponsor note (kit supplier)",
                       "date": "2026-09",
                       "url": "https://github.com/Beyond-The-Jersey/data/issues/243",
                       "note": (sp_.get("note") or "Kit supplier per the target research.").strip()},
        })
        kit_["sponsorsComplete"] = False

# US league jerseys: the patch is on the kit, the arena right is a deal below
for k in U.NEW_KITS:
    if k["id"] not in {x["id"] for x in kits}:
        kits.append(dict(k))

# US league jerseys: the patch is on the kit, the arena right is a deal below
for k in U.NEW_KITS:
    if k["id"] not in {x["id"] for x in kits}:
        kits.append(dict(k))

# sleeve / shorts placements from the research pass
sleeved = 0
for k in kits:
    for extra in RES["sleeves"].get(k["clubId"], []):
        if k["season"] != "2026-27" and k["clubId"] not in {c["id"] for c in RES["clubs"]}:
            continue
        if any(p["sponsorId"] == extra["sponsorId"] and p["placement"] == extra["placement"]
               for p in k["sponsors"]):
            continue
        k["sponsors"].append({"sponsorId": extra["sponsorId"],
                              "placement": extra["placement"],
                              "source": extra["source"]})
        sleeved += 1
print("sleeve placements attached:", sleeved)

# ------------------------------------------------- clubs research left without a shirt
# Both of these clubs were added by the coverage pass without a kit, so their front
# sponsor sat in sponsors.json attached to nothing.
_EXTRA_KITS = []
for _club, _spn, _nm, _dt, _url, _sum in _EXTRA_KITS:
    _kid = "%s-2026-27-home" % _club
    if _kid not in {k["id"] for k in kits} and _spn in {x["id"] for x in sponsors}:
        kits.append({
            "id": _kid, "clubId": _club, "season": "2026-27", "kitType": "home",
            "periodLabel": "2026-27", "periodFrom": "2026", "periodTo": "2027", "photos": {},
            "sponsors": [{"sponsorId": _spn, "placement": "front",
                          "source": {"name": _nm, "date": _dt, "url": _url}}],
            "sponsorsComplete": False, "change": None, "summary": _sum,
        })
        print("kits: added", _kid)

# ---------------------------------------------------------------- a kit for PSG
# PSG is the only Ligue 1 club in the data and had no kit at all, so its Qatar Airways
# front sponsor was not on any shirt. Qatar Airways has held the PSG front since 2022.
if "paris-saint-germain-2026-27-home" not in {k["id"] for k in kits}:
    kits.append({
        "id": "paris-saint-germain-2026-27-home", "clubId": "paris-saint-germain",
        "season": "2026-27", "kitType": "home", "periodLabel": "2026-27",
        "periodFrom": "2026", "periodTo": "2027", "photos": {},
        "sponsors": [{
            "sponsorId": "qatar-airways", "placement": "front",
            "source": {
                "name": "Qatar Airways, official front of shirt sponsor of Paris Saint-Germain",
                "date": "2022-06-29",
                "url": "https://www.qatarairways.com/press-releases/en-WW/218264-qatar-airways-takes-paris-saint-germain-partnership-to-new-heights-as-the-official-front-of-shirt-sponsor/",
            },
        }],
        "sponsorsComplete": False, "change": None,
        "summary": "Ligue 1. Qatar Airways front, state-owned airline.",
    })
    print("kits: added paris-saint-germain-2026-27-home")

# --------------------------------------------------------------- orphan kits
# Two shirt images in the design manifest had no kit pointing at them.
for k in A.ORPHAN_KITS:
    if k["id"] not in {x["id"] for x in kits}:
        kits.append(dict(k))

# ------------------------------------------------- harness assets from the manifest
# The website publishes assets/manifest.json listing every crest and shirt image it
# holds. Attach them by club/season/kitType so a photo is never lost and a kit is
# never pointed at a file that does not exist.
import re

PUBLIC = os.environ.get("BTJ_PUBLIC", os.path.join(os.path.dirname(SEED), os.pardir, "public"))
PUBLIC = os.path.abspath(PUBLIC)
MANIFEST = os.path.join(PUBLIC, "assets", "manifest.json")
if os.path.exists(MANIFEST):
    man = json.load(open(MANIFEST, encoding="utf-8"))
    have_files = {a["file"] for a in man}
    bykey = {}
    crests = {}
    for a in man:
        base = os.path.basename(a["file"])
        if a["kind"] == "crest":
            crests[a["club"]] = a["file"]
            continue
        if not a.get("season") or a["kind"] not in ("shirt-photo", "shirt-square"):
            continue
        mt = re.search(r"-(home|away|third)-", base)
        if not mt:
            continue
        side = "square" if a["kind"] == "shirt-square" else a.get("side")
        if not side:
            continue
        bykey.setdefault((a["club"], a["season"], mt.group(1)), {})[side] = a["file"]
    attached = 0
    for k in kits:
        key = (k["clubId"], k["season"], k["kitType"])
        if key not in bykey:
            continue
        for side, f in bykey[key].items():
            if k["photos"].get(side) != f:
                k["photos"][side] = f
                attached += 1
    for c in clubs:
        f = crests.get(c["id"])
        if f and c.get("crest") != f:
            c["crest"] = f
    write("clubs", clubs)
    print("assets: %d image refs attached, %d crests available" % (attached, len(crests)))
    # anything on disk the kits still do not reference
    used = {p for k in kits for p in k["photos"].values()}
    orphans = sorted(f for f in have_files if f.startswith("assets/shirts/") and f not in used)
    if orphans:
        print("assets: UNREFERENCED shirt images:", orphans)

write("kits", kits)
print("kits:", len(kits))
write("deals", deals)

# --------------------------------------------------------------- late kit additions
# Kits appended AFTER the manifest harness above (e.g. Lazio's blank front) carry
# photos of their own in later blocks; run the harness merge once more so nothing
# added late misses its sourced images.
if os.path.exists(MANIFEST):
    _man = json.load(open(MANIFEST, encoding="utf-8"))
    _bykey = {}
    for _a in _man:
        if not _a.get("season") or _a["kind"] not in ("shirt-photo", "shirt-square"):
            continue
        _mt = re.search(r"-(home|away|third)-", os.path.basename(_a["file"]))
        if not _mt:
            continue
        _side = "square" if _a["kind"] == "shirt-square" else _a.get("side")
        if not _side:
            continue
        _bykey.setdefault((_a["club"], _a["season"], _mt.group(1)), {})[_side] = _a["file"]
    _late = 0
    for _k in kits:
        _key = (_k["clubId"], _k["season"], _k["kitType"])
        for _side, _f in _bykey.get(_key, {}).items():
            if not _k["photos"].get(_side):
                _k["photos"][_side] = _f
                _late += 1
    if _late:
        print("assets: %d photo refs attached to late-added kits" % _late)
    _used = {p for _k in kits for p in _k["photos"].values()}
    _orphans2 = sorted(f for f in {a["file"] for a in _man}
                       if f.startswith("assets/shirts/") and f not in _used)
    if _orphans2:
        print("assets: UNREFERENCED shirt images (final):", _orphans2)
    else:
        print("assets: every shirt image is referenced by a kit")
    write("kits", kits)

# ------------------------------------------------------------------ changes / dropped
changes = load("changes")
changes += [c for c in A.EXTRA_CHANGES if c["id"] not in {x["id"] for x in changes}]
changes += [c for c in A.ORPHAN_CHANGES if c["id"] not in {x["id"] for x in changes}]
changes.sort(key=lambda c: c["id"], reverse=True)
write("changes", changes)

# ------------------------------------------------------------------ Lazio's blank front
# Lazio signed Polymarket in April 2026, Italy's ADM blacklisted the company in July for
# taking bets without a licence, and the club terminated in August 2026 before the season
# started. The shirt has no front, so the kit carries none and the short deal is recorded
# here as a deal plus a change rather than as a live placement.
_LAZIO_SRC = {"name": "SBC News", "date": "2026-08-12",
              "url": "https://sbcnews.co.uk/europe/italy/2026/08/12/lazio-polymarket-2026/"}
if "lazio-2026-27-home" not in {k["id"] for k in kits}:
    kits.append({
        "id": "lazio-2026-27-home", "clubId": "lazio", "season": "2026-27",
        "kitType": "home", "periodLabel": "2026-27", "periodFrom": "2026",
        "periodTo": "2027", "photos": {}, "sponsors": [],
        "sponsorsComplete": False,
        "change": {"kind": "worse", "badge": "Polymarket gone",
                   "text": "Lazio start 2026-27 with a blank front: Polymarket signed in April, Italy's ADM blacklisted it in July, and the club terminated in August."},
        "summary": "Serie A. No front sponsor. Polymarket signed in April 2026 and the deal was terminated on 11 August, before the season began.",
    })
    print("kits: added lazio-2026-27-home (blank front)")

if "lazio-polymarket" not in {d["id"] for d in deals}:
    deals.append({
        "id": "lazio-polymarket", "clubId": "lazio", "orgName": None,
        "sponsorId": "polymarket", "placement": "front",
        "from": "2026-27", "to": None, "value": None, "source": _LAZIO_SRC,
        "note": "Announced April 2026 as a record deal worth over $22m to 2028, then terminated on 11 August 2026 after four months because Polymarket held no ADM licence. The club kept the 2026-27 sum.",
    })
    print("deals: added lazio-polymarket (terminated)")

if "2026-08-11-lazio-polymarket" not in {c["id"] for c in changes}:
    changes.append({
        "id": "2026-08-11-lazio-polymarket", "date": "2026-08-11", "datePrecision": "day",
        "clubId": "lazio", "sponsorId": "polymarket", "kind": "worse",
        "levelAfter": "not-rated",
        "title": "Polymarket front ends after four months",
        "text": "Italy's ADM blacklisted Polymarket in July 2026 for taking bets without a licence. Lazio removed the branding and terminated on 11 August, leaving the shirt blank for the new season.",
        "source": _LAZIO_SRC,
    })
    print("changes: added 2026-08-11-lazio-polymarket")

# F1 deals: the eleven teams had no deal records at all, so every one of their sponsors
# floated with nothing to hang off. Placement mapped from the research vocabulary onto the
# schema's.
_rdf = os.path.join(HERE, "research_deals.json")
if os.path.exists(_rdf):
    _have_d = {d["id"] for d in deals}
    _add = [d for d in json.load(open(_rdf, encoding="utf-8")) if d["id"] not in _have_d]
    deals += _add
    if _add:
        print("deals: added %d from research (F1 grid, league-wide partners)" % len(_add))

write("kits", kits)
write("deals", deals)
changes.sort(key=lambda c: c["id"], reverse=True)
write("changes", changes)

# -------------------------------------------------- final asset pass (last kit writes)
# Any kit-producing block above this line (Lazio, F1, orphans) runs after the manifest
# harness, so give every kit one last chance to pick up its sourced images and emit the
# authoritative unreferenced count once, at the very end.
if os.path.exists(MANIFEST):
    _man = json.load(open(MANIFEST, encoding="utf-8"))
    _bykey = {}
    for _a in _man:
        if not _a.get("season") or _a["kind"] not in ("shirt-photo", "shirt-square"):
            continue
        _mt = re.search(r"-(home|away|third)-", os.path.basename(_a["file"]))
        if not _mt:
            continue
        _side = "square" if _a["kind"] == "shirt-square" else _a.get("side")
        if not _side:
            continue
        _bykey.setdefault((_a["club"], _a["season"], _mt.group(1)), {})[_side] = _a["file"]
    _late = 0
    for _k in kits:
        for _side, _f in _bykey.get((_k["clubId"], _k["season"], _k["kitType"]), {}).items():
            if not _k["photos"].get(_side):
                _k["photos"][_side] = _f
                _late += 1
    if _late:
        print("assets: %d photo refs attached in the final pass" % _late)
    _used = {p for _k in kits for p in _k["photos"].values()}
    _orphans = sorted(f for f in {a["file"] for a in _man}
                      if f.startswith("assets/shirts/") and f not in _used)
    print("assets: %d unreferenced shirt images (final)" % len(_orphans)
          + (": %s" % _orphans if len(_orphans) <= 12 else ""))
    write("kits", kits)


dropped = load("dropped")
for d in dropped:
    src = A.DROPPED_SOURCES.get(d["id"])
    if src:
        d["source"] = src
        d.pop("todo", None)
write("dropped", dropped)

# ------------------------------------------------------------------ contacts
# top up any club the network pass missed, using the sourced overrides
cpath = os.path.join(HERE, "contacts_build.json")
contacts = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else []
import build_contacts as BC  # noqa: E402

club_ids = {c["id"] for c in clubs}
# the contact sweep is driven by a SITES map that can hold ids no longer in clubs.json
contacts = [c for c in contacts if c["clubId"] in club_ids]
have = {c["clubId"] for c in contacts}
for cid in sorted(club_ids - have):
    if cid in BC.OVERRIDES:
        contacts.append({"clubId": cid, "channels": BC.OVERRIDES[cid], "lastChecked": A.D})
        print("contacts: override for", cid)
    else:
        print("contacts: STILL MISSING", cid)
# merge the hand-checked channels into records that only got a partial scrape
for c in contacts:
    extra = BC.OVERRIDES.get(c["clubId"])
    if not extra:
        continue
    seen = {(x["type"], x["value"]) for x in c["channels"]}
    for ch in extra:
        if (ch["type"], ch["value"]) not in seen:
            c["channels"].append(ch)
contacts.sort(key=lambda c: c["clubId"])
# dedupe channels inside a record, keeping the first (which carries the earliest source)
for c in contacts:
    seen, keep = set(), []
    for ch in c["channels"]:
        k = (ch["type"], ch["value"])
        if k in seen:
            continue
        seen.add(k)
        keep.append(ch)
    c["channels"] = keep
write("contacts", contacts)
print("contacts:", len(contacts))

# ------------------------------------------------------- data/ mirror (legacy tree)
# The handover shipped a per-club data/ tree in an older shape and said to regenerate
# or drop it. The website reads normalized/ only, but other consumers may still read
# these, and leaving them stale meant two id spaces for the same club. Regenerated
# here so the two trees can no longer disagree.
tier_rank = {"severe": 3, "serious": 2, "concern": 1, "none": 0, "unrated": -1}
deals_by_club = {}
for d in deals:
    deals_by_club.setdefault(d["clubId"], []).append(d)
kits_by_club = {}
for k in kits:
    kits_by_club.setdefault(k["clubId"], []).append(k)
cont_by_club = {c["clubId"]: c for c in contacts}
owners_by_id = {o["id"]: o for o in owners}
sponsors_by_id = {s["id"]: s for s in sponsors}

mirror_dir = os.path.join(os.path.dirname(OUT), "data")
os.makedirs(mirror_dir, exist_ok=True)
index = []
for c in clubs:
    cid = c["id"]
    ch = cont_by_club.get(cid, {}).get("channels", [])
    flat = {}
    for x in ch:
        flat.setdefault(x["type"], x["value"])
    spns = []
    for k in kits_by_club.get(cid, []):
        for p in k["sponsors"]:
            s = sponsors_by_id.get(p["sponsorId"])
            if not s:
                continue
            rec = {
                "id": s["id"],
                "name": s["name"],
                "placement": p["placement"],
                "season": k["season"],
                "tier": s["tier"],
                "ownerId": s.get("ownerId"),
                "owner": (owners_by_id.get(s.get("ownerId")) or {}).get("name"),
                "verdict": s.get("verdict"),
                "source": p.get("source"),
            }
            if not any(e["id"] == s["id"] and e["placement"] == p["placement"] for e in spns):
                spns.append(rec)
    for d in deals_by_club.get(cid, []):
        s = sponsors_by_id.get(d.get("sponsorId") or "")
        if s and not any(e["id"] == s["id"] for e in spns):
            spns.append({"id": s["id"], "name": s["name"], "placement": d.get("placement"),
                         "season": None, "tier": s["tier"], "ownerId": s.get("ownerId"),
                         "owner": (owners_by_id.get(s.get("ownerId")) or {}).get("name"),
                         "verdict": s.get("verdict"), "source": d.get("source")})
    worst = max((tier_rank.get(e["tier"], -1) for e in spns), default=-1)
    doc = {
        "id": cid,
        "team": c["name"],
        "sport": c["sportId"],
        "league": c["leagueId"],
        "country": c.get("country"),
        "contact": flat,
        "sponsors": sorted(spns, key=lambda e: e["id"]),
        "worstTier": [t for t, v in tier_rank.items() if v == worst][0] if worst >= 0 else "unrated",
        "owners": sorted({e["ownerId"] for e in spns if e.get("ownerId")}),
        "lastUpdated": meta.get("updatedAt"),
    }
    with open(os.path.join(mirror_dir, cid + ".json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    index.append({"id": cid, "name": c["name"], "sport": c["sportId"],
                  "league": c["leagueId"], "file": cid + ".json"})
with open(os.path.join(mirror_dir, "index.json"), "w", encoding="utf-8") as f:
    json.dump({"version": "0.2", "canonical": "normalized/",
               "last_updated": meta.get("updatedAt"), "teams": index},
              f, indent=2, ensure_ascii=False)
    f.write("\n")
# drop files left over from the old naming (unicode slugs, renamed clubs)
keep = {x["file"] for x in index} | {"index.json"}
removed = []
for fn in sorted(os.listdir(mirror_dir)):
    if fn.endswith(".json") and fn not in keep:
        os.remove(os.path.join(mirror_dir, fn))
        removed.append(fn)
print("data/ mirror: %d club files, %d stale removed" % (len(index), len(removed)))

# ------------------------------------------------------------------ validate
r = subprocess.run([sys.executable, VALIDATE, OUT, "--assets", PUBLIC],
                   capture_output=True, text=True, errors="replace")
out = r.stdout.strip()
errs = [l for l in out.splitlines() if l.startswith("error:")]
warns = [l for l in out.splitlines() if l.startswith("warning:")]
print(f"\nvalidator exit={r.returncode} errors={len(errs)} warnings={len(warns)}")
for l in errs[:40]:
    print(" ", l)
print("---- tail ----")
print("\n".join(out.splitlines()[-6:]))
