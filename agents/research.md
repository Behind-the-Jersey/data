# Brief for research agents

You're helping Behind the Jersey, an open dataset of who really pays for the sponsors on sports shirts, and how much human-rights abuse sits behind the money. You'll research one issue and deliver it as a pull request that a person reviews. Anyone can run you: a maintainer, a volunteer, or a journalist's agent.

## Before you start

- **Read:**
  - [`CONTRIBUTING.md`](../CONTRIBUTING.md): the format and the source rules;
  - [`METHOD.md`](../METHOD.md): tiers and the rating rule;
  - the schemas in [`schema/`](../schema), which say what each field means.
- **Pick an open issue** labelled `club`, `league`, `sport` or `research` that nobody has claimed: no assignee, and no comment claiming it in the last week. Comment "Taking this", with what you'll do and who runs you. That comment is the claim (only maintainers can assign). If you stop before a pull request, say so on the issue.
- **Work on a branch** named after the issue, e.g. `research/ligue-1-257`. Never push to `main`, never merge, never approve.

## The task

For the clubs, league or sponsors in your issue:

1. **Clubs:** make sure each club in the current season exists in `data/clubs/`, using the official league list. Add missing ones. Set `crest: null` unless `assets/` lists an image the website has.
2. **Kits:**
   - one current home kit per club in `data/kits/`, with every sponsor and its `placement` (front, back, sleeve, shorts, patch…);
   - each sponsor gets a `source`: the club's kit launch or announcement, or a named press article;
   - set `sponsorsComplete: true` only if you checked every placement.
3. **Sponsors:**
   - one record per sponsor in `data/sponsors/`;
   - search `data/` first and reuse an existing id;
   - new sponsors are `tier: "unrated"`, `status: "unrated"`.
4. **Owners:**
   - trace each sponsor's owner up to a state or fund where there is one (`parentId`), using company filings, annual reports or the sponsor's own site;
   - each owner gets a claim that states the ownership, with its source;
   - reuse existing owners (`government-of-saudi-arabia`, `saudi-pif`, `government-of-dubai`…).
5. **Evidence:** for owners that are states or state-controlled, add claims (`data/claims/`) with sourced facts about their human-rights record. Use the UN, Amnesty International, Human Rights Watch, courts, or the named press. Reuse existing claims where they fit.
6. **Deals:**
   - organisation sponsors (league or competition partners) go in `data/deals/` with `clubId: null`, `orgName` and `leagueId`;
   - reported deal values go in the club's deal, with their source.
7. **Check:** run `python3 scripts/validate.py` and `python3 scripts/check_links.py --base origin/main`. Fix every error.
8. **Open the pull request** with the template, linked to the issue (`Part of #<n>`, or `Closes #<n>` when it finishes the issue). Include:
   - what you added or changed (counts per type);
   - the tier you propose for each sponsor, with the claims behind it and one line of reasoning. Don't set tiers yourself.
   - facts you found but couldn't source, as plain text with where you saw them;
   - anything that disagreed between sources.

## Rules you must follow

- **Never invent anything.** That means no facts, figures, dates, owners, URLs, emails or phone numbers. Unknown is `null`, or you leave it out and list it in the pull request.
- **Open every URL you cite** and make sure it says what you claim. Wikipedia and Wikidata are for finding primary documents, not for citing.
- **Claims say only what the source says.** Your reasoning goes in the pull request, never in a claim's text.
- **State ownership alone is not a tier** ([METHOD.md](../METHOD.md)).
- **Contacts:** only fan-facing channels the club publishes, with the page they're on.
- **Don't touch** `schema/`, `scripts/`, `.github/`, or records outside your issue, unless the issue asks you to.
- **Some things don't fit the data yet:** races, fights and tournaments hosted by a state (no event record yet), and sponsors on cars (no car placement). Put them in the pull request description with their sources instead of forcing them into kits.

## When you're done

Comment on the issue with a link to your pull request and a one-paragraph summary. The review agent and CI will comment on the pull request. Answer their findings with new commits on the same branch.
