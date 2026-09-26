# Subagent brief: research one target for Behind the Jersey

You are researching ONE target for Behind the Jersey, a site that shows who really
pays for the sponsors on sports jerseys and events, and rates how much human-rights
abuse sits behind them. Your output is ONE research file that the orchestrator
merges into the data. You are one of 9 parallel subagents: write only your own file;
never touch shared builders or `normalized/`.

## Paths (this machine; not /tmp)

- website (schemas, seed, targets, validator): `/Users/michael/git/HRF/behind-the-jersey`
- data repo (read existing data here): `/Users/michael/git/HRF/data`
- write your file to: `/Users/michael/git/HRF/data/research/<TARGET_ID>.json`
- python with `jsonschema`: `/var/folders/xx/8zf5sz1d24n0cxtgsk956cvr0000gn/T/opencode/btj-venv/bin/python`
- today is 24 Sep 2026; current season is 2026-27. Season competitions use `2026-27`
  in `season`, `periodFrom`, `periodTo`; bare `2026` only for calendar-year
  competitions (cycling tours, tennis tours, F1).

## Read first

1. Your target entry `"id": "<TARGET_ID>"` in
   `/Users/michael/git/HRF/behind-the-jersey/docs/coverage/targets.json`: read
   `entities`, `shape`, `sponsorPlacements`, `teamListSource`, `dataNotes` and every
   `leads` entry. Then read the GitHub issue in its `issue` field and its comments:
   `gh issue view <n> -R Beyond-The-Jersey/data --comments`
2. The data contract: JSON Schemas in
   `/Users/michael/git/HRF/behind-the-jersey/data/schema/*.schema.json` and examples
   in `/Users/michael/git/HRF/behind-the-jersey/data/seed/`.
3. What already exists: `/Users/michael/git/HRF/data/normalized/*.json`. Reuse
   existing ids for clubs, sponsors and owners (e.g. `saudi-pif`,
   `government-of-saudi-arabia`, `government-of-dubai`, `qatar-airways`); search
   before creating a new id.

## Do

1. **Entities.** The league/competition entry (with `clubCount`), and the sport if
   the sport code is new (`status: "not-mapped"`). Every club or team for the current
   season from the official list: ASCII kebab-case `id`, `name`, `shortName`, `code`,
   `sportId`, `leagueId`, `country`, `crest: null`, `aliases`.
2. **Sponsors on the shirt.** One kit per club or team for the current season, listing
   every sponsor with its `placement` (front, back, sleeve, shorts) and a `source`
   `{name, date, url}` from the club's kit launch or announcement, or a named press
   article. `sponsorsComplete: true` only when you have checked every placement.
3. **Organisation deals.** Sponsors of the league or competition itself as deals with
   `clubId: null`, `orgName`, `leagueId` and `placement: "league-partner"`, each
   with a source.
4. **Owners.** For each sponsor, the owner chain up to a state or a fund where there
   is one (`parentId`), from company filings, annual reports or the sponsor's own site.
5. **Claims.** For state-linked owners only: sourced statements about the owner's
   human-rights record, each with the primary source's URL and `reviewed: false`.
   Reuse existing claims where they fit.
6. **Proposed tiers.** New sponsors stay `tier: "unrated"`. For each sponsor you think
   deserves a tier, add a `proposedRatings` entry:
   `{sponsorId, tier, ownerId, claimIds, reasoning}`. A person decides.
7. **Write** everything to your single file in the format below.
8. **Report back** to the orchestrator: counts, the sponsors you propose to rate and
   why, anything you couldn't source, and anything that disagreed between sources.

## Format (exact top-level keys; omit empty arrays or leave them empty)

```json
{
  "target": "<TARGET_ID>",
  "issue": "<issue url>",
  "sports":   [ /* only if the sport code is new */ ],
  "leagues":  [ /* leagues.json entries */ ],
  "clubs":    [ /* clubs.json entries */ ],
  "owners":   [ /* owners.json entries, parentId up to the state or fund */ ],
  "sponsors": [ /* sponsors.json entries, tier "unrated" */ ],
  "kits":     [ /* kits.json entries, every sponsor with placement and source */ ],
  "deals":    [ /* deals.json entries; org deals use clubId null, orgName, leagueId, placement "league-partner" */ ],
  "claims":   [ /* claims.json entries, source with url, reviewed false */ ],
  "proposedRatings": [ { "sponsorId": "…", "tier": "serious", "ownerId": "…", "claimIds": ["…"], "reasoning": "…" } ],
  "unsourced": [ "facts found but not sourced yet, as plain text" ]
}
```

Every entry must match the matching schema.

## Validate before finishing (must print OK)

```
/var/folders/xx/8zf5sz1d24n0cxtgsk956cvr0000gn/T/opencode/btj-venv/bin/python - <<'PY'
import json, jsonschema, os
base = "/Users/michael/git/HRF/behind-the-jersey/data/schema"
d = json.load(open("/Users/michael/git/HRF/data/research/<TARGET_ID>.json")); n = 0
for k in ["sports","leagues","clubs","owners","sponsors","kits","deals","claims"]:
    s = json.load(open(os.path.join(base, k + ".schema.json")))["items"]
    for e in d.get(k) or []:
        try: jsonschema.validate(e, s)
        except Exception as ex: n += 1; print("FAIL", k, e.get("id"), ex.message)
print("OK" if not n else "%d errors" % n)
PY
```

## Don't

- Invent nothing: no facts, figures, dates, URLs, owners or contact details. Unknown
  is `null` with a note, or goes in `unsourced` as plain text.
- Never cite Wikipedia or Wikidata as a source; use them only to find the primary
  document. Open every URL you cite.
- Don't edit `normalized/`, `pipeline_data.py`, `research_additions.json` or any
  builder, and don't commit or comment on issues.
- Don't set a tier or `reviewed: true`, and don't write club levels.
- Shapes `event-host` (races, fights, tournaments) and `car-livery` (sponsors on
  cars) don't fit the schema yet. Record those facts in `unsourced` with their
  sources; don't force them into kits.
