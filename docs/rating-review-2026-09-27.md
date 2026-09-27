# Rating review, 27 September 2026

Until now a sponsor could be rated Concern for any state money in its owner chain, or for any fine or settlement. LA Rams showed the problem: their practice-jersey sponsor Hyundai was Concern because South Korea's pension fund holds 7.8% of Hyundai Motor, and the page gave no reason, since Concern needed no explanation.

The maintainers set a stricter rule ([METHOD.md](../METHOD.md), "Sponsor tiers"). A rating above *Nothing found* now needs **the link** (an ownership claim: a state with a record controls the sponsor, or holds 5% or more, or a board seat) and **the record** (a record claim: that state's documented serious abuses, or a human-rights finding against the company itself for abuse in the last 20 years), and a `why` that says both. Every claim now has a `kind`: `ownership` or `record`. Decided along the way: Singapore's executions for drug offences count as a record; stakes multiply along the chain; the 20 years run from when the abuse happened.

Every rating above *Nothing found* (56) was checked again, with a second 3M record that was *Nothing found*. Research agents (Claude) opened every new source, copied the words that support each claim, and recorded the check as `checked.by: "rating-review-2026-09-27"`; `scripts/check_sources.py` found every quote on its page where a script can read it. No person has reviewed the new claims yet, so they keep `reviewed: false`.

| | |
|---|---:|
| Ratings checked: every one above Nothing found (56), and a second 3M record | 57 |
| … now Nothing found | 25 |
| … tier changed otherwise | 3 |
| … same tier, link or record now sourced, why added or rewritten | 29 |
| New claims | 57 |
| Claims removed (replaced, or conduct that isn't a human-rights finding) | 37 |
| Clubs whose level changes | 17 |

## Ratings

| Sponsor | Before | After | Why | On the shirts of |
|---|---|---|---|---|
| `aeroflot` | Severe | **Severe** | The Russian state owns about 74% of Aeroflot. Russia has been at war with Ukraine since its full-scale invasion in February 2022, and after Western countries im |  |
| `gazprom` | Severe | **Severe** | the Russian state controls Gazprom; Russia is at war with Ukraine. |  |
| `visit-rwanda` | Severe | **Severe** | Visit Rwanda is the tourism brand of the Rwanda Development Board, a Rwandan government institution. UN experts say 3,000–4,000 Rwandan troops are fighting alon | Aston Villa, Atlético de Madrid, LA Clippers |
| `aramco` | Serious | **Serious** | Aramco is controlled by the Saudi state: the government holds about 81.5% directly and its fund PIF a further 16%. Saudi Arabia carried out a record 345 executi | Aston Martin Aramco F1 Team |
| `emirates` | Serious | **Serious** | Emirates is wholly owned by the Investment Corporation of Dubai, a Dubai government entity. Dubai is part of the United Arab Emirates, where in July 2024 a cour | AC Milan, Arsenal, Olympique Lyonnais, Real Madrid, UAE Team Emirates XRG |
| `etihad-airways` | Serious | **Serious** | Etihad moved from the Abu Dhabi government to ADQ (2022) and into L'IMAD Holding (2026), both Abu Dhabi state funds. | ES Troyes AC, Manchester City, New York City FC |
| `experience-abu-dhabi` | Serious | **Serious** | Experience Abu Dhabi is a tourism brand of the Abu Dhabi government, part of the United Arab Emirates. In 2024, a UAE court gave 43 people, including human righ | New York Knicks |
| `maaden` | Serious | **Serious** | Ma’aden is about 67% owned by PIF, Saudi Arabia’s sovereign wealth fund. Saudi Arabia carried out a record 345 executions in 2024, and US intelligence assessed  | Aston Martin Aramco F1 Team |
| `petronas` | Serious | **Serious** | Petronas is wholly owned by the Malaysian state. Malaysia uses broad laws against its critics and holds refugees and migrants in indefinite detention, and UN ex | Mercedes-AMG PETRONAS F1 Team |
| `qatar-airways` | Serious | **Serious** | Qatar Airways is wholly owned by the Government of Qatar. In the years before the 2022 World Cup, migrant workers in Qatar faced widespread abuses, including un | BWT Alpine F1 Team, Paris Saint-Germain |
| `qatar-airways-global` | Serious | **Serious** | why text added. |  |
| `riyadh-air` | Serious | **Serious** | Riyadh Air is wholly owned by Saudi Arabia’s state fund, PIF, which the crown prince chairs. Saudi Arabia carried out a record 345 executions in 2024, and US in | Atlético de Madrid |
| `sela` | Serious | **Serious** | Saudi Arabia’s state fund, PIF, owns 94% of Sela. Saudi Arabia carried out a record 345 executions in 2024, and US intelligence assessed that the crown prince a |  |
| `turkish-airlines` | Serious | **Serious** | the state's wealth fund owns 49.12% and a Treasury golden share carries privileged voting rights over board nominations (control). |  |
| `valvoline` | Serious | **Serious** | why text added. | Aston Martin Aramco F1 Team |
| `visit-qatar` | Serious | **Serious** | Visit Qatar was set up by Qatar Tourism, the Qatari state’s tourism body, to market the country. Amnesty International and Human Rights Watch report that migran | Audi Revolut F1 Team |
| `visit-saudi` | Serious | **Serious** | Visit Saudi is the flagship platform of the Saudi Tourism Authority, a Saudi government body. Human Rights Watch and Amnesty International report widespread lab |  |
| `3m` | Concern | **Concern** | 3M Company (listed; largest holders Vanguard 8.89%, BlackRock 7.60%, JPMorgan 7.60%, State Street 5.10%) - US federal juries found for service members in 10 of 16 Combat Arms earplug bellwether trials (2021-2022) over hearing damage; no qualifying PFAS finding of harm to people yet. |  |
| `boeing` | Concern | **Concern** | The Boeing Company (listed; largest holders Vanguard 9.0%, FMR 7.0%, BlackRock 6.8%) - Boeing admitted in 2021 that its pilots deceived the FAA about the 737 MAX, and a US federal judge found in 2022 that without that conspiracy the 346 people killed in two crashes would not have died. | BWT Alpine F1 Team |
| `bp` | Concern | **Concern** | BP p.l.c. (listed; largest holder BlackRock, no state at 5%+) - in 2013 a US court accepted BP Exploration and Production's guilty plea to 11 counts of felony manslaughter for the 11 men killed on the Deepwater Horizon rig in 2010. | Audi Revolut F1 Team |
| `castrol` | Concern | **Concern** | Castrol is BP's lubricants brand (BP p.l.c., listed, largest holder BlackRock); same BP record as the bp entry: the 2013 guilty plea to 11 counts of felony manslaughter over the Deepwater Horizon deaths. Pending sale of 65% to Stonepeak not completed yet. | Audi Revolut F1 Team |
| `citigroup` | Concern | **Concern** | Citigroup Inc. (listed; largest holders Vanguard and BlackRock, no state) - a 2023 CFPB consent order found Citibank had a pattern or practice of discriminating against credit card applicants based on Armenian national origin (2015-2021); order ended early in October 2025. |  |
| `cognizant` | Concern | **Concern** | Cognizant (listed; 5% holders BlackRock and State Street, no state) - an October 2024 federal jury found a pattern or practice of intentional discrimination against non-South Asian and non-Indian employees; the verdict stands (post-trial motions denied Oct 2025, disparate-impact finding Dec 2025, case in phase two). | Aston Martin Aramco F1 Team |
| `g42` | Serious | **Concern** | was serious. Mubadala holds an undisclosed minority stake and its CEO sits on the board (board-seat test); the controlling shareholder on record is Royal Group, Sheikh Tahnoon's private holding, not the state. | Mercedes-AMG PETRONAS F1 Team, UAE Team Emirates XRG |
| `lenovo` | Concern | **Concern** | CAS Holdings (wholly state-owned) holds 29.04% of Legend, which holds 32.95% of Lenovo: about 9.5% through the chain. |  |
| `motorola-mobility` | Concern | **Concern** | owned by Lenovo; the Chinese state holds about 9.5% of Lenovo through CAS Holdings and Legend. | Chicago Bulls |
| `noon` | Concern | **Concern** | PIF owns 50% (a joint venture, not control). | Newcastle United |
| `nouryon` | Concern | **Concern** | GIC is a named joint owner (share not published, no board seat); maintainers decided in September 2026 that Singapore's executions for drug offences count as a record. | Visa Cash App Racing Bulls F1 Team |
| `s-3m` | Nothing found | **Concern** | 3M Company (listed; largest holders Vanguard 8.89%, BlackRock 7.60%, JPMorgan 7.60%, State Street 5.10%) - US federal juries found for service members in 10 of 16 Combat Arms earplug bellwether trials (2021-2022) over hearing damage; no qualifying PFAS finding of harm to people yet. | Cadillac Formula 1 Team |
| `shell` | Concern | **Concern** | Shell plc (listed; largest holder BlackRock 8.1%, no state) - Shell's then Nigerian subsidiary SPDC admitted liability in the English High Court for two 2008 oil spills at Bodo in the Niger Delta and paid £55 million in 2015. | Scuderia Ferrari HP |
| `standard-chartered` | Concern | **Concern** | Temasek (wholly owned by the Singapore government) holds 17-18%; Singapore counts as a state with a record (maintainers, September 2026). The sanctions record in the old claim is not a human-rights finding. | Liverpool |
| `uniqlo` | Concern | **not rated yet** | on hold for a maintainer. In 2021 US customs held Uniqlo shirts under its order against XPCC cotton and ruled Uniqlo had not shown they were made without forced labour; the rulings were later taken off CBP's site. A failure to disprove, not a finding. |  |
| `adidas` | Concern | **Nothing found** | was concern. The Xinjiang cotton tests were journalism, not a finding of forced labour against adidas (METHOD.md). | Mercedes-AMG PETRONAS F1 Team |
| `adidas-a` | Concern | **Nothing found** | was concern. The Xinjiang cotton tests were journalism, not a finding of forced labour against adidas (METHOD.md). | Audi Revolut F1 Team |
| `bank-of-america` | Concern | **Nothing found** | was concern; the 2016 finding concerns hiring in 1993, more than 20 years ago; fossil finance and mortgage settlements are not human-rights findings. | Portland Timbers |
| `barclays` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). | Atlassian Williams F1 Team |
| `capital-one` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). |  |
| `deutsche-telekom` | Concern | **Nothing found** | was concern. State ownership alone is not a tier: Germany has no record of serious abuses. | Bayern Munich |
| `dhl` | Concern | **Nothing found** | was concern. State ownership alone is not a tier: Germany has no record of serious abuses. |  |
| `gree` | Concern | **Nothing found** | was concern. The Zhuhai state sold control in 2019-2020 and holds 3.46%, under 5%, with no board seat. | Al-Taawoun, Real Betis |
| `herbalife` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). | LA Galaxy |
| `hyundai` | Concern | **Nothing found** | was concern. South Korea's pension fund holds 7.8%, but no claim ties South Korea to serious abuses. | Los Angeles Rams |
| `ifs` | Concern | **Nothing found** | was concern. ADIA is a minority shareholder of undisclosed size with no board seat; if a stake of 5% or more is published, it becomes concern. | Cadillac Formula 1 Team |
| `intuit` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). |  |
| `jeep` | Concern | **Nothing found** | was concern. France has no record of serious abuses, so Bpifrance's stake is not a link. | Juventus FC |
| `jpmorgan-chase` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). |  |
| `kia-america` | Concern | **Nothing found** | was concern with no stated reason; no state stake that counts. |  |
| `kroger` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). | Cincinnati Reds, Tennessee Titans |
| `lbbw` | Concern | **Nothing found** | was concern. State ownership alone is not a tier: a German state has no record of serious abuses. | VfB Stuttgart |
| `mobil-1` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). | Oracle Red Bull Racing |
| `mobil-1-rb` | Concern | **Nothing found** | was concern; its record (fines, settlements, financing) is not a human-rights finding (METHOD.md). | Visa Cash App Racing Bulls F1 Team |
| `nissan` | Concern | **Nothing found** | was concern. France has no record of serious abuses. |  |
| `okx` | Concern | **Nothing found** | was concern; its anti-money-laundering guilty plea is not a human-rights finding. | Manchester City, McLaren Mastercard F1 Team |
| `plenitude` | Concern | **Nothing found** | was concern. Italy has no record of serious abuses. | Racing Santander |
| `pnc-bank` | Concern | **Nothing found** | was concern; the 2013 fair-lending settlement is not a finding (the CFPB says so), and concerns 2002-2008. |  |
| `sabor-a-malaga` | Concern | **Nothing found** | was concern. State ownership alone is not a tier: a Spanish provincial council has no record of serious abuses. | Malaga CF |
| `uralkali` | Concern | **Nothing found** | was concern. No state holds 5% or more, and no human-rights finding against the company. |  |

## Clubs whose level changes

| Club | Before | After |
|---|---|---|
| Al-Taawoun | Spotted | not rated yet |
| Atlassian Williams F1 Team | Spotted | not rated yet |
| Bayern Munich | Spotted | not rated yet |
| Cincinnati Reds | Spotted | Clean |
| Juventus FC | Spotted | not rated yet |
| LA Galaxy | Spotted | not rated yet |
| Los Angeles Rams | Spotted | Clean |
| Malaga CF | Spotted | not rated yet |
| McLaren Mastercard F1 Team | Spotted | not rated yet |
| Mercedes-AMG PETRONAS F1 Team | Soaked | Stained |
| Oracle Red Bull Racing | Spotted | not rated yet |
| Portland Timbers | Spotted | not rated yet |
| Racing Santander | Spotted | not rated yet |
| Real Betis | Spotted | not rated yet |
| Tennessee Titans | Spotted | Clean |
| UAE Team Emirates XRG | Soaked | Stained |
| VfB Stuttgart | Spotted | not rated yet |

## Claims removed

Replaced by a clean claim of one kind, or about conduct that the rule doesn't count (fines, settlements, sanctions, financing, climate). They stay in the git history.

`3m-company-record`, `adidas-ag-record`, `bahrain-hrw-record`, `bank-of-america-mortgage-settlement-2014`, `bank-of-america-record`, `barclays-record`, `belgium-hrw-record`, `boeing-record`, `bp-plc-record`, `capital-one-cfpb-add-on-products-2012`, `citigroup-citi-owner-record`, `cognizant-record`, `cote-divoire-hrw-record`, `dr-congo-hrw-record`, `exxon-mobil-corporation-record`, `exxon-valdez-oil-spill`, `france-hrw-record`, `gov-qatar-record`, `government-of-saudi-arabia-record`, `gree-group-zhuhai-sasac-record`, `herbalife-ltd-record`, `ifs-ab-record`, `intuit-intuit-inc-nasdaq-intu-owner-record`, `jpmorgan-chase-fossil-finance-2025`, `kazakhstan-hrw-record`, `kroger-owner-record`, `lenovo-china-record`, `lenovo-group-ltd-record`, `mubadala-record`, `nouryon-board-2026`, `okx-group-record`, `pnc-national-city-fair-lending-2013`, `shell-nigeria-oil-spills-hague-2021`, `shell-plc-record`, `standard-chartered-plc-record`, `turkiye-wealth-fund-record`, `uniqlo-owner-record`

## For the maintainers

- **Uniqlo** is on hold (not rated yet): in 2021 US customs held Uniqlo shirts under its order against Xinjiang's XPCC and ruled Uniqlo hadn't shown they were made without forced labour, then took the rulings off its site. Is a failure to disprove a finding?
- **G42** went from Serious to Concern: Mubadala's stake is undisclosed, but its CEO sits on the board. The controlling shareholder on record is Royal Group, Sheikh Tahnoon's private holding. Treating his control as the state's would make it Serious.
- **noon** stays Concern: PIF owns 50% as a joint venture, which is joint control, not control.
- **Nouryon** is Concern: GIC is one of its two named joint owners. Its share isn't published and it has no board seat; this review reads joint ownership by two owners as meeting the 5% test. If a published share shows less, it becomes Nothing found.
- **IFS** is Nothing found: ADIA is a minority shareholder of undisclosed size with no board seat. A published stake of 5% or more would make it Concern.
- **Castrol:** bp agreed to sell 65% to Stonepeak, backed by CPP Investments, expected to close by the end of 2026. Re-rate it then.
- **Boeing:** the fraud charge was dismissed in November 2025 under a non-prosecution agreement; the 2021 admission and the 2022 court finding stand.
- **Not rated yet, but the rule now reaches them:** Mercedes-Benz's shareholders include BAIC, a Chinese state company (9.98%), and the Kuwait Investment Authority (5.33%) (`mercedes-benz-group-record`).
- **Why texts are drafts:** every `why` written or changed here has `status: "draft"` until a person reads it.
