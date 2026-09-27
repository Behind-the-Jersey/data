# Contributing

Thank you for helping. You can work by hand or with an AI agent. Either way the path is the same:

1. **Pick an [issue](https://github.com/Beyond-The-Jersey/data/issues)** (or open one: *Check a club*, *Check a sponsor*, *Report an error*) and **claim it with a comment**: that you're taking it, and what you'll do. Anyone can comment, and only maintainers can assign, so the comment is the claim.
   - An issue with a recent claim, or an assignee, is taken. Pick another one.
   - A claim with no activity for a week is free: ask on the issue, then take it over.
   - If you stop, say so on the issue.
2. **Make a branch** (or fork), and add or edit records in `data/`.
3. **Run the checks:** `pip install jsonschema pypdf && python3 scripts/validate.py`, and `python3 scripts/check_sources.py --base origin/main`.
4. **Open a pull request** using the template, linked to the issue (`Part of #<n>`, or `Closes #<n>` when it finishes the issue). Say what you added, what you couldn't source, and which tiers you propose and why.
5. **CI runs, the review agent comments, and a maintainer reviews.** Nothing is published until a maintainer approves it.

Small fixes (a wrong date, a better source) can be made directly in the GitHub editor: open the record, edit it and choose "Create a new branch and start a pull request".

**Using an agent?** Point it at [`agents/research.md`](agents/research.md). It explains the task, the format and the rules. Agents never push to `main` and never merge.

## The records

Each record is one JSON file in `data/<type>/`, named after its id: `data/sponsors/visit-rwanda.json`. The schemas in `schema/` define every field; `scripts/validate.py` enforces them.

- **Ids** are ASCII kebab-case (`atletico-de-madrid`, not `atlético-de-madrid`). Before you add a record, search `data/` for an existing one: the owner `government-of-saudi-arabia` exists, so reuse it.
- **References are ids**, never names: `clubId`, `sponsorId`, `ownerId`, `claimIds`.
- **Seasons:**
  - Season leagues use `YYYY-YY` (`2026-27`) for `season`, `periodFrom` and `periodTo`.
  - Calendar-year competitions use `YYYY`.
  - A deal's `from` is when the deal started. Use `null` if you don't know; never the season you looked it up.
- **Dates** are `YYYY`, `YYYY-MM` or `YYYY-MM-DD`.
- **Money** is the reported value with its source, `upTo: true` when the report says "up to", and `usdApprox` for the dollar figure. Unknown is `value: null`, never a guess.
- **Kits:**
  - one per club per season (or per period when nothing changed);
  - every sponsor with its `placement`, and a `source` for each;
  - `sponsorsComplete: true` only when you've checked every placement;
  - `photos` only for images the website has (see `assets/`).

## Sources

Every fact carries a `source` from the **primary document**: the club's announcement, the company's filing or annual report, the UN or NGO report, or a named press article. Open it, copy the words that support the fact, and say who checked it:

```json
"source": {
  "name": "<publisher: title of the page>",
  "date": "<YYYY-MM-DD, as shown on the page>",
  "url": "<the link you opened>",
  "quote": "<words copied exactly from the page, at most about 30>",
  "checked": { "on": "<YYYY-MM-DD, the day you opened it>", "by": "<your GitHub login>" }
}
```

- **Only checked claims are published.** A claim appears on the website once every source on it has a `quote` and `checked` (see [METHOD.md](METHOD.md), the evidence standard).
- **Two independent sources for claims behind a Concern, Serious or Severe rating.** Put the second in `additionalSources`, from a different publisher. That includes the claims that tie a sponsor to a state. Without it the rating is published as *not rated yet*.
- **The quote must be on the page, word for word.** `scripts/check_sources.py` opens every source in your pull request. It fails when a link is gone, when it looks made up (the site shows the same page for any address, or sends it to the homepage), or when the quote isn't on the page.
- **Claims say only what the source says.** Leave out what the page doesn't state, including conclusions like "no state stake" or "privately held". Your reasoning goes in the pull request.
- **Wikipedia and Wikidata are not sources.** Use them to find the primary document.
- **Never invent:** no placeholder URLs (`example.com`), no "inference" or "industry analysis" as a source, no made-up owners, quotes, emails or phone numbers. If you can't source something, leave it out and list it in your pull request.
- **Claims** (`data/claims/`) are short statements about an **owner**, in plain words. A deal is not a claim: it goes in `data/deals/` or on a kit.
- **Contacts** are only channels a club publishes for fans (the supporter liaison officer, a fan-services inbox, a contact page), each with the page it's on. Never ticket offices, shops, hospitality or named staff.

## Ratings

Read [METHOD.md](METHOD.md). In short:

- New sponsors are `tier: "unrated"`, `status: "unrated"`, and new claims are `reviewed: false`.
- State ownership alone is not a tier.
- Propose tiers in your pull request, with the claims that support them. A maintainer sets them.

## Licence

By contributing you agree that your contributions are published under [CC BY 4.0](LICENSE-DATA.md) (data) and [MIT](LICENSE) (code).
