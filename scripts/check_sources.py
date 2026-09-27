"""Check the sources cited in data/: that each link works, that it isn't a made-up address, and that
its quote is on the page. On a pull request only the records it changes are checked.

    python3 scripts/check_sources.py --base origin/main      # records changed since origin/main
    python3 scripts/check_sources.py --all                   # every record (slow)
    python3 scripts/check_sources.py --base origin/main --report review/sources.md   # a table for reviewers

Errors (the check fails):
  - the page is gone: 404, 410, or the domain doesn't exist;
  - it looks made up: the site sends it to its own homepage;
  - its quote isn't on the page, although the page's text loaded.
Warnings: the site blocks scripts or didn't answer; the site answers a made-up address with exactly
the same page (so a script can't tell whether this one exists); the quote can't be checked by a script
(a PDF without text, a page that needs a browser). A reviewer opens those by hand.
"""
import argparse
import concurrent.futures
import gzip
import html
import io
import os
import random
import re
import ssl
import string
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zlib

from common import ROOT, read_json

ap = argparse.ArgumentParser()
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--base', help='git ref to diff against, e.g. origin/main')
g.add_argument('--all', action='store_true')
ap.add_argument('--root', default=ROOT, help='the checkout to check (default: this one)')
ap.add_argument('--report', help='also write a Markdown table of every source to this file')
args = ap.parse_args()
root = os.path.abspath(args.root)

if args.all:
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(root, 'data')) for f in fs if f.endswith('.json')]
else:
    out = subprocess.run(['git', '-C', root, 'diff', '--name-only', '--no-renames', '--diff-filter=AM', f'{args.base}...HEAD',
                          '--', 'data'], capture_output=True, text=True, check=True).stdout.split()
    files = [os.path.join(root, f) for f in out if f.endswith('.json')]


# ------------------------------------------------------------------ what to check
def sources_in(o, path, found):
    """Every source object ({name, url, ...}) with where it sits in the record."""
    if isinstance(o, dict):
        if 'name' in o and 'url' in o and isinstance(o.get('url'), (str, type(None))):
            found.append((path, o))
        if o.get('type') in ('contact-form', 'website') and isinstance(o.get('value'), str):
            found.append((f'{path} ({o["type"]})', {'name': o['type'], 'url': o['value']}))
        for k, v in o.items():
            sources_in(v, f'{path}.{k}' if path else k, found)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            sources_in(v, f'{path}[{i}]', found)
    return found


items = []  # (record, path, source)
for f in sorted(files):
    rec = os.path.relpath(f, root)[:-5]
    for path, s in sources_in(read_json(f), '', []):
        if s.get('url'):
            items.append((rec, path, s))

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 '
      '(Behind-the-Jersey source check; https://github.com/Behind-the-Jersey/data)')
CTX = ssl.create_default_context()


def fetch(url):
    """(status, final URL, content type, body). Status is an int, or the name of the error."""
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/pdf,*/*;q=0.8',
                                               'Accept-Language': 'en', 'Accept-Encoding': 'gzip, deflate'})
    try:
        r = urllib.request.urlopen(req, timeout=25, context=CTX)
        body = r.read(8_000_000)
        enc = r.headers.get('Content-Encoding', '')
        body = gzip.decompress(body) if enc == 'gzip' else zlib.decompress(body) if enc == 'deflate' else body
        return r.status, r.geturl(), r.headers.get('Content-Type', ''), body
    except urllib.error.HTTPError as e:
        return e.code, url, '', b''
    except urllib.error.URLError as e:
        reason = str(e.reason)
        return ('no-such-host' if 'not known' in reason or 'nodename' in reason or 'getaddrinfo' in reason
                else type(e.reason).__name__), url, '', b''
    except Exception as e:  # timeouts, TLS errors, broken compression
        return type(e).__name__, url, '', b''


def page_text(ctype, body):
    """The readable text of a page or PDF, or None if a script can't get it."""
    if body[:4] == b'PK\x03\x04' or any(t in ctype for t in ('spreadsheet', 'excel', 'msword', 'officedocument', 'zip', 'image/')):
        return None  # a spreadsheet, document or image: a person checks the quote
    if 'pdf' in ctype or body[:5] == b'%PDF-':
        try:
            from pypdf import PdfReader
            return ' '.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(body)).pages)
        except Exception:
            return None
    t = body.decode('utf-8', 'ignore')
    t = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    return html.unescape(t)


def title_of(ctype, body):
    if 'pdf' in ctype:
        return '(PDF)'
    t = body[:300_000].decode('utf-8', 'ignore')
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', t, re.I) or \
        re.search(r'<title[^>]*>(.*?)</title>', t, re.I | re.S)
    return html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()[:160] if m else ''


FOLD = str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '\u00a0': ' ', '\u2009': ' '})


def norm(t):
    return re.sub(r'\s+', ' ', t.translate(FOLD)).strip().lower()


def loose(t):
    return re.sub(r'[^0-9a-z]+', '', norm(t))


# ------------------------------------------------------------------ fetch every page, and probe each site once
urls = sorted({s['url'] for _, _, s in items})
pages = {}
with concurrent.futures.ThreadPoolExecutor(16) as ex:
    for u, (st, final, ctype, body) in zip(urls, ex.map(fetch, urls)):
        ok = isinstance(st, int) and st < 400
        pages[u] = {'status': st, 'final': final, 'type': ctype, 'title': title_of(ctype, body) if ok else '',
                    'text': page_text(ctype, body) if ok else None}


def probe(site):
    junk = ''.join(random.choices(string.ascii_lowercase, k=14))
    st, final, ctype, body = fetch(f'{site}/{junk}-no-such-page/')
    ok = isinstance(st, int) and st < 400
    return site, (st, final, norm(page_text(ctype, body) or '') if ok else None)


def site_of(u):
    p = urllib.parse.urlsplit(u)
    return f'{p.scheme}://{p.netloc}'


sites = sorted({site_of(u) for u in urls if isinstance(pages[u]['status'], int) and pages[u]['status'] < 400
                and urllib.parse.urlsplit(u).path.strip('/')})
with concurrent.futures.ThreadPoolExecutor(16) as ex:
    made_up = dict(ex.map(probe, sites))


def verdict(src):
    """('error' | 'warning' | 'ok', message, quote found: True/False/None)."""
    u = src['url']
    p = pages[u]
    st = p['status']
    if st in (404, 410) or st == 'no-such-host':
        return 'error', f'gone ({st})', None
    if not isinstance(st, int):
        return 'warning', f'no answer ({st}): open it in a browser', None
    if st in (401, 403, 429, 451, 999):
        return 'warning', f'the site blocks scripts ({st}): open it in a browser', None
    if st >= 400:
        return 'warning', f'server error ({st})', None
    src_url = urllib.parse.urlsplit(u)
    src_path = src_url.path.strip('/')
    fin = urllib.parse.urlsplit(p['final'])
    same_site = (fin.hostname or '').removeprefix('www.') == (src_url.hostname or '').removeprefix('www.')
    if src_path and same_site and not fin.path.strip('/') and not fin.query:
        return 'error', f'redirects to the site\'s homepage ({p["final"]}): the page may not exist', None
    probe_st, probe_final, probe_text = made_up.get(site_of(u), (None, '', None))
    text_norm = norm(p['text']) if p['text'] else None
    if src_path and isinstance(probe_st, int) and probe_st < 400 and (
            urllib.parse.urlsplit(probe_final).path == fin.path or (probe_text and probe_text == text_norm)):
        return 'warning', ('the site answers a made-up address with exactly this page, so a script can\'t tell '
                           'whether it exists: open it in a browser'), None
    q = src.get('quote')
    if not q:
        return 'ok', '', None
    text = p['text']
    if not text or len(norm(text)) < 1500:
        return 'warning', 'the quote can\'t be checked by script (a PDF without text, or a page that needs a browser)', None
    if norm(q) in norm(text) or loose(q) in loose(text):
        return 'ok', '', True
    return 'error', 'the quote is not on the page', False


errors, warnings, rows = [], [], []
for rec, path, src in items:
    level, msg, found = verdict(src)
    line = f'{src["url"]}: {msg} (in {rec}, {path})'
    if level == 'error':
        errors.append(line)
    elif level == 'warning':
        warnings.append(line)
    p = pages[src['url']]
    rows.append((rec, path, src, p, level, msg, found))

for w in warnings:
    print('warning:', w)
for e in errors:
    print('error:', e)
print(f'{len(items)} sources ({len(urls)} links) checked in {len(files)} files: {len(errors)} errors, '
      f'{len(warnings)} to open by hand.')

if args.report:
    cell = lambda x: str(x or '').replace('|', '\\|').replace('\n', ' ')
    mark = {True: 'found', False: '**not found**', None: '–'}
    lines = ['# Sources in this pull request', '',
             f'{len(items)} sources, {len(errors)} errors, {len(warnings)} to open by hand. '
             'Written by scripts/check_sources.py; the review agent checks every row.', '',
             '| Record | Where | Source | Link | Answer | Page title | Quote on page | Check |', '|---|---|---|---|---|---|---|---|']
    for rec, path, src, p, level, msg, found in rows:
        final = p['final'] if p['final'] != src['url'] else ''
        lines.append('| ' + ' | '.join(cell(x) for x in [
            rec, path, f'{src.get("name")} ({src.get("date") or "no date"})', src['url'] + (f' → {final}' if final else ''),
            p['status'], p['title'], mark[found], {'ok': 'ok', 'warning': f'⚠️ {msg}', 'error': f'❌ {msg}'}[level]]) + ' |')
    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    with open(args.report, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')

sys.exit(1 if errors else 0)
