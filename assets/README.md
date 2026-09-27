# Images: candidate sources and licences

Images are not part of the dataset. The website hosts the crests and shirt photos it shows
(`public/assets/` in Behind-the-Jersey/website), and records point at them by path
(`clubs/*.json` → `crest`, `kits/*.json` → `photos`).

`wikimedia-assets.csv` lists candidate images from Wikipedia and Wikimedia Commons for every club,
with the file page and licence of each, for attribution:

| column | meaning |
| --- | --- |
| `club` | club id |
| `asset` | `crest`, `kit-home`, `kit-away` or `kit-third` |
| `wikimedia_file` | the `File:` title, needed for attribution |
| `direct_url` | where to download it |
| `license` | the licence stated on the file page |
| `wikipedia_page` | the page it was read from |

**Crests** (331): the website uses these. 212 of them are non-free (fair use): they are the
clubs' own marks. Keep the `wikimedia_file` for attribution; don't treat them as openly licensed.

**Kit images** (`kit-*` rows): Wikipedia's kit *templates*, the body pattern only, with no sleeves
and no sponsor logos. They can't show what's on a shirt, so the website doesn't use them. Club
pages need real product photos (720×800 on white) with logo positions, and those need permission
from their owners before going public.

Regenerate the list with `python3 assets/build_assets.py` (Wikipedia API, no key needed).
