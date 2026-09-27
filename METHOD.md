# How a rating is made

**Ratings are illustrative until the method is final.** This is the method the data follows today; changes to it go through a pull request like any other change.

## Sponsor tiers

Each sponsor gets one tier (`sponsors/<id>.json` → `tier`). The tier rests on sourced claims about its owners.

| Tier | Label on the site | What it needs |
|---|---|---|
| `severe` | Severe | Paid for by a state directly tied to ongoing severe abuses (armed conflict, conflict minerals), with a sourced claim of those abuses. |
| `serious` | Serious | Owned by a state or state fund **with documented serious abuses**: a sourced claim of those abuses by a state in the sponsor's owner chain. |
| `concern` | Concern | A lesser link: a minority stake held by a state or state fund with a poor record, or a sustained, documented conduct record. |
| `none` | Nothing found | Sponsor and owner checked, with a sourced ownership claim; no link to serious abuses. |
| `unrated` | Not rated yet | Not checked yet (`status: unrated`), or checked but on hold until a person reviews it (`status: being-rated`: the owner and evidence are kept and shown). |

**The rules:**

- **State ownership alone is not a tier.** A public owner in a state with no sourced record of serious abuses (a US state university, a county tourism board, an Italian region, Swiss cantons) is not `serious`. It's `none`, or `unrated` with `status: being-rated` until someone decides.
- **Every `serious` or `severe` sponsor has a `why`.** That's a short text for the website, written only from the claims it cites. Those claims must be about an owner in the sponsor's chain. `scripts/validate.py` flags a serious or severe sponsor without one.
- **Claims say only what their source says.** The reasoning for a tier goes in the sponsor's `note` or the pull request, never in a claim's `text`.
- **A claim is about the owner it names,** and a sponsor cites it only if that owner is in its chain. Evidence about a different company that shares a shareholder doesn't count.
- **Only a maintainer sets or changes a tier.** Contributors propose tiers in their pull request, with the claims and their reasoning.

## The evidence standard

A claim is published only once someone has opened every source on it and confirmed it says what the claim says.

- **Every source carries a quote and a check.** The `quote` is words copied exactly from the page that support the claim (about 30 words at most). `checked` records who opened the page and when. CI opens every source in a pull request and fails it when the link is gone, when it looks made up (the site shows the same page for any address, or sends it to the homepage), or when the quote isn't on the page.
- **A claim that a Concern, Serious or Severe rating rests on needs two independent sources:** its `source`, and at least one in `additionalSources` from a different publisher. That covers the ownership claims that tie a sponsor to a state as well as the claims about abuses. Independent means a different publisher that reports it separately, not a second article repeating the first. Where there is one, one of them should be a primary document: a UN or NGO report, a court ruling, a filing.
- **Everything else needs one primary source,** with a working link and a quote.
- **Claims say only what their sources say.** A conclusion such as "no state stake" needs a source that says it, for example a shareholder register that lists the owners.

**What the release publishes:**
- Sponsors cite only checked claims.
- A rating is published as *not rated yet* when any of its claims is unchecked, or when a claim behind a Concern, Serious or Severe rating has only one source. The release then shows `tier: "unrated"` and `status: "being-rated"`, with `hold` saying why and `heldTier` holding the rating it will get.
- `scripts/validate.py` lists every held rating as a warning.
- `claims.json` in the release still has every claim, with all its sources.

## Club blood level

A club's level comes from the sponsors on its current home kit, their tiers and where they sit on the shirt. Front counts most. The same rule runs in `scripts/common.py` (`kit_level`) and on the website (`lib/data/rating.ts`).

| Level | When |
|---|---|
| **Soaked** | a `severe` sponsor on the front, or two sponsors rated `serious` or worse |
| **Stained** | a `serious` sponsor on the front, or a `severe` one elsewhere |
| **Spotted** | any sponsor rated `concern` or worse |
| **Clean** | every sponsor rated `none`, and the kit's sponsor list is complete (`sponsorsComplete: true`) |
| **Not rated yet** | none of the above |

A kit can override its level (`levelOverride`) only for a documented exception.

## Review

- Every change arrives as a pull request.
- CI checks the schema, references and this method, and opens every source in the changed records (links, made-up addresses, quotes).
- A review agent opens every source again and checks that it supports the claim. Its check fails when a source doesn't hold up.
- A maintainer approves before anything is merged and published.
- `reviewed: true` on a claim means a person checked it against its sources. New claims start as `reviewed: false`. Checked sources (a quote plus `checked`) are what publishes a claim; `reviewed` is the extra step a person takes.
