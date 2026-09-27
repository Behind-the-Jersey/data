# AGENTS.md

Rules for AI agents working in this repository. OpenCode, Codex, Cursor and similar tools load this file automatically; Claude Code loads it through `CLAUDE.md`. They apply to every task, however small, and whoever runs you.

## Every change goes through a pull request

**Never push to `main`. Never merge, approve or close a pull request.** A maintainer reviews and merges. This holds even when your token could do it: don't use admin rights, `gh pr merge`, `--admin`, `--force` or a direct push, and don't commit on `main` "just this once".

The only way to change this repository:

```bash
git fetch origin
git switch -c <kind>/<short-name> origin/main     # e.g. research/ligue-1-257, fix/arsenal-kit-source
# … edit records in data/ …
pip install jsonschema pypdf
python3 scripts/validate.py                        # must print 0 errors
python3 scripts/check_sources.py --base origin/main   # must print 0 errors
git add data && git commit -m "…"
git push -u origin HEAD
gh pr create --base main --fill                    # then complete the template
```

Before you finish, check:
- `git branch --show-current` is **not** `main`;
- `gh pr view` shows your pull request;
- the issue has a comment linking it.

**Make the hook do the remembering.** `main` is protected with *enforce admins*, so a direct push is rejected even for an admin — but failing in your own terminal beats failing at the remote. Install it once per clone (hooks are not cloned):

```bash
git config core.hooksPath scripts/hooks
```

`scripts/hooks/pre-push` refuses a push to `main` and prints the commands to use instead. For a deliberate one-off: `BTJ_ALLOW_MAIN_PUSH=1 git push origin main`.

**If you committed or pushed to `main` by mistake:** stop. Don't try to repair `main`, force-push, or revert on it. Tell the person running you, and comment on the issue, with the commit id. A maintainer fixes `main`.

## What a pull request may contain

- **Records in `data/`,** one JSON file per record, and nothing generated. `build_normalized.py`, `normalized/` and `research/` were retired, and CI rejects them.
- **Your research notes, proposed tiers and unsourced leads** go in the pull request description, not in files.
- **Don't touch `schema/`, `scripts/`, `.github/`, `agents/` or these instructions** unless the issue asks you to.
- **One issue per pull request,** linked with `Part of #<n>`, or `Closes #<n>` when it finishes the issue. Claim the issue with a comment first. Keep it reviewable: split anything over a few hundred records.

## What every record must meet

- **Every source you cite, you open.** Copy the words that support the fact into `quote`, and record `checked: {"on": "<date>", "by": "<who runs you>"}`. CI fails a pull request whose quote isn't on the page, or whose link is dead or made up.
- **Claims behind a Concern, Serious or Severe rating** need a second source from a different publisher, in `additionalSources`.
- **Never invent anything:** no facts, figures, dates, owners, URLs, quotes, emails or phone numbers. Unknown is `null`, or leave it out and say so in the pull request.
- **Don't set tiers.** Propose them in the pull request; a maintainer sets them.

## Read next

- [`agents/research.md`](agents/research.md): the full brief for research tasks.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): the record format and the source rules.
- [`METHOD.md`](METHOD.md): the evidence standard and the rating rule.
- [`agents/review.md`](agents/review.md): what the review agent checks in your pull request.
