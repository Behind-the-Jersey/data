# How a rating is made

**Ratings are illustrative until the method is final.** This is the method the data follows today; changes to it go through a pull request like any other change.

## Sponsor tiers

Each sponsor gets one tier (`sponsors/<id>.json` → `tier`). A tier above *Nothing found* says there is human-rights abuse behind the sponsor's money, so it needs two things, each a sourced claim:

1. **The link: whose money it is** (a claim with `kind: "ownership"`). The sponsor is a brand or subsidiary of the company named, and where a state or state fund is involved, its stake counts only if it
   - **controls** the sponsor: owns it, holds a majority, or holds a golden share or the right to appoint its management; or
   - holds **5% or more**, directly or through other companies: multiply the stakes along the chain (29% of a company that owns 33% is 9.6%); or
   - has **a seat on the board**: its official, or an executive of its fund.

   A smaller, passive stake doesn't count.
2. **The record: a human-rights abuse** (a claim with `kind: "record"`), either
   - **by that state:** serious abuses documented by a UN body, Human Rights Watch, Amnesty International or a court, such as killing, torture or arbitrary detention of critics, mass or unfair trials, executions, forced labour or systemic abuse of migrant workers, war crimes or persecution of minorities. Executions for drug offences count (the maintainers decided this for Singapore in September 2026). France doesn't count: findings of excessive police force and racial profiling aren't a record of this kind (decided in September 2026, for Renault). A state without such a record doesn't count, whatever its stake; or
   - **by the company itself:** forced or child labour, deaths or injuries, discrimination, or abuse of communities, **found** by a court, regulator, UN body or major human-rights NGO: a judgment or jury verdict, a guilty plea or admission, a regulator's order or decision, or a published NGO investigation. The abuse happened **in the last 20 years, or is still going on.** A settlement without a finding or an admission isn't a finding (a consent decree that says it isn't an admission of liability doesn't count; decided in October 2026, for QuikTrip), but a regulator's own finding counts even when the company then settles (decided in October 2026, for Ball Corporation). Product-liability verdicts, where a defective product injured or killed a customer, aren't a finding of this kind (decided in October 2026, for Toyota). Owning a joint venture with a military's business conglomerate counts when a UN body documents those ventures as supporting a military with a record of serious abuses (decided in October 2026, for POSCO and the Myanmar military's MEHL). Financial, bribery, sanctions, tax, consumer-protection, antitrust and climate or fossil-finance records don't count, however large the fine.

| Tier | Label on the site | What it needs |
|---|---|---|
| `severe` | Severe | A state directly tied to ongoing severe abuses (armed conflict, conflict minerals) controls or pays for the sponsor. |
| `serious` | Serious | A state or state fund with a record **controls** the sponsor. |
| `concern` | Concern | A state or state fund with a record holds **5% or more, or a board seat,** without control; or the company **itself** has a human-rights finding. |
| `none` | Nothing found | Sponsor and owner checked, with a sourced ownership claim; nothing passes the test above. |
| `unrated` | Not rated yet | Not checked yet (`status: unrated`), or checked but on hold until a person reviews it (`status: being-rated`: the owner and evidence are kept and shown). |

**The rules:**

- **State ownership alone is not a tier.** A public owner in a state without a sourced record of serious abuses (a US state university, a county tourism board, an Italian region, Swiss cantons, a German development bank, South Korea's pension fund) is not a link to abuse, whatever its stake. It's `none`.
- **Every rating above *Nothing found* has a `why`:** the short text on the website that says why it's a problem. It names the link, then the record, and is written only from the claims it cites. Those include at least one ownership claim and one record claim, record claims first (the website shows the first one's source). `scripts/validate.py` fails a sponsor without one, and the release holds its rating.
- **The record must be about someone the link reaches:** an owner in the sponsor's chain (`parentId`), or an owner named in the ownership claims it cites, and that owner's chain. Evidence about a different company that shares a shareholder doesn't count.
- **A sponsor rated *Nothing found* cites ownership claims only.** Conduct that doesn't pass the test isn't recorded: it would read as a reason on a sponsor we say is clean.
- **Claims say only what their source says.** One claim is either ownership or a record, never both. The reasoning for a tier goes in the sponsor's `note` or the pull request, never in a claim's `text`.
- **Only a maintainer sets or changes a tier.** Contributors propose tiers in their pull request, with the claims and their reasoning. The review agent checks each proposal and each tier change against these rules.

## The evidence standard

A claim is published only once someone has opened every source on it and confirmed it says what the claim says.

- **Every source carries a quote and a check.** The `quote` is words copied exactly from the page that support the claim (about 30 words at most). `checked` records who opened the page and when. CI opens every source in a pull request and fails it when the link is gone, when it looks made up (the site shows the same page for any address, or sends it to the homepage), or when the quote isn't on the page.
- **A claim that a Concern, Serious or Severe rating rests on needs two independent sources:** its `source`, and at least one in `additionalSources` from a different publisher. That covers the ownership claims (the link) as well as the record claims. Independent means a different publisher that reports it separately, not a second article repeating the first. Where there is one, one of them should be a primary document: a UN or NGO report, a court ruling, a filing.
- **Everything else needs one primary source,** with a working link and a quote.
- **Claims say only what their sources say.** A conclusion such as "no state stake" needs a source that says it, for example a shareholder register that lists the owners.

**What the release publishes:**
- Sponsors cite only checked claims.
- A rating is published as *not rated yet* when any of its claims is unchecked, when a Concern, Serious or Severe rating has no `why` citing an ownership claim and a record claim, or when a claim behind one has only one source. The release then shows `tier: "unrated"` and `status: "being-rated"`, with `hold` saying why and `heldTier` holding the rating it will get.
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
- A review agent opens every source again and checks that it supports the claim, and checks every tier set or proposed against the rules above. Its check fails when a source doesn't hold up or a tier doesn't meet them.
- A maintainer approves before anything is merged and published.
- `reviewed: true` on a claim means a person checked it against its sources. New claims start as `reviewed: false`. Checked sources (a quote plus `checked`) are what publishes a claim; `reviewed` is the extra step a person takes.
