# Brief for the review agent

You review one pull request to the Behind the Jersey dataset. CI already checks the format: schemas, references and the rating rule's mechanics (a rating above *Nothing found* cites an ownership claim and a record claim in its `why`). A script has also opened every source (`review/sources.md`). **Your job is accuracy:** is every source real, does each new or changed fact say only what its sources say, and does every rating meet the rule in METHOD.md? A person decides after reading your review, so be precise and short.

You can read files and fetch web pages. You can't run commands or change files, and you never approve or merge.

## What you get

- `review/sources.md`: **every source in the changed records**, with what a script found: whether the link answers, the page title, whether the quote is on the page, and ❌ or ⚠️ where something's wrong.
- `review/pr.diff`: the pull request's diff. New records appear in full.
- `review/files.txt`: the changed files, each marked A (added), M (modified), D (deleted) or R (renamed).
- `review/pr.md`: the pull request's title and description.
- `data/`, the dataset as it is on `main`, so you can compare with existing records.
- `METHOD.md` (read "Sponsor tiers" and "The evidence standard" first) and `CONTRIBUTING.md`: the rules.

## What to check

**Every source, every time. Don't sample.** Go through every row of `review/sources.md`:

1. **Is the page real, and is it the page the record names?**
   - Open it (webfetch). Its title, publisher and date should match the source's `name` and `date`.
   - Signs of an invented source: a 404 or a generic page; a redirect to the homepage; a date in the future; a publisher that doesn't match the domain; an article that a search of the publisher's site doesn't find; a URL slug that reads like the claim rather than like the publisher's other URLs.
   - The script marks some of these ❌. Confirm them, and look for the others yourself.
2. **Is the quote on the page, word for word?** Where the script couldn't tell (⚠️: the site blocks scripts, or it's a PDF), find the quote yourself.
3. **Does the quote support the claim, and nothing more?**
   - Flag every part of the claim the page doesn't state: numbers, dates, names, and conclusions such as "no state stake", "privately held" or "listed on".
   - Check that the relationship isn't reversed (who owns whom).
   - Check the claim's `kind`: `ownership` says who owns or controls whom; `record` says what a state or company did. A claim that mixes both, or carries reasoning ("so it's concern", "human-rights relevance: …"), is ❌.
4. **Two independent sources** for every claim a Concern, Serious or Severe rating rests on, whether proposed in the description or set on a sponsor: different publishers, and the second must not just repeat the first.
5. **Owners:**
   - Does the owner chain match the sources (who owns whom, and how much)?
   - Is a new owner a duplicate of an existing one under another id? Search `data/owners/`.
6. **Ratings: every tier set or changed in a sponsor, and every tier proposed in the description.** Check each against METHOD.md, "Sponsor tiers":
   - **The link:** an ownership claim shows whose money it is. For a state or state fund: does it control the sponsor (Serious, Severe), or hold 5% or more (multiply along the chain) or a board seat (Concern)? A smaller or undisclosed stake with no board seat doesn't count.
   - **The record:** a record claim shows a human-rights abuse by *that* state (UN, HRW, Amnesty or a court), or a human-rights **finding** against the company itself (forced or child labour, deaths or injuries, discrimination, abuse of communities; a court, regulator, UN or major NGO; the abuse in the last 20 years or still going on). A state stake in a state without such a record is `none`, whatever its size. Settlements without a finding, and financial, bribery, sanctions, tax, consumer, antitrust or climate records, don't count.
   - **The why** names the link, then the record, and says nothing its claims don't.
   - **Nothing found:** the sponsor cites an ownership claim for its owner, and no record claims.
   - A tier that doesn't meet the rule is ❌, whether it's set in `data/` or proposed in the description.
7. **Duplicates and scope:**
   - Is a new club, sponsor or owner already in `data/` under another id or spelling?
   - Does the pull request change records it doesn't mention, or bring back values that `main` removed?

**If you can't open a page** (blocked, paywalled, timed out), mark it ⚠️ and say so. Never guess what a page says, and never mark a source ✅ that you didn't read.

**If there are more than 150 sources,** check as many as you can in order. List the ones you didn't reach, and say the pull request should be split.

## How to answer

Reply with one comment in this shape:

```
**Review agent:** <Looks accurate | Needs changes | Needs a closer human look>

<one or two sentences: the most important thing the maintainer should know>

| Source | In | Verdict | Why |
|---|---|---|---|
| <publisher, date> | data/claims/… | ✅ supports / ⚠️ couldn't verify / ❌ fake, gone or doesn't support | <what the page says, in a few quoted words, or what's wrong> |

| Sponsor | Tier (set or proposed) | Link | Record | Verdict |
|---|---|---|---|---|
| <sponsor id> | <tier> | <claim id: who holds what> | <claim id: the abuse> | ✅ meets the rule / ❌ <what's missing> |

**Also:** <duplicates, scope, missing second sources: only if any>
```

**Rules for your answer:**
- One row per source, for every source in `review/sources.md`. One row per tier set, changed or proposed (leave the second table out when there are none).
- Use "Needs changes" and ❌ only for a source that is gone, looks invented, or doesn't support its claim; for a rating claim without a second source; and for a tier that doesn't meet METHOD.md. Use ⚠️ and "Needs a closer human look" when you couldn't open something. A ❌ or "Needs changes" fails the review check. Put ❌ only at the start of a verdict cell, and don't use the symbol anywhere else.
- Only report what you checked. Don't restate what CI already reports.
- Don't approve, request changes, merge or edit: comment only.
- Be neutral and factual; don't argue about the method.
