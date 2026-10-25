# question.stungeye.com: S5 slide decks (static archive)

This is a static copy of the 47 S5 slide decks published by the QuestionCMS Rails app at question.stungeye.com. It was taken on 2026-10-24, before the server (olddroplet) was retired. The app's source is at [stungeye/QuestionCMS-RRC](https://github.com/stungeye/QuestionCMS-RRC).

## Layout

| Path | What |
|-|-|
| `site/index.html` | List of decks in three sections: community talks, work talks and course modules (grouped by course). Generated from the app's `lessons`/`courses` tables. It replaces the admin-only `/lessons` page. The "Game Dev Drafts" (deck 63) and "XML & Mobile Computing" (deck 15) courses aren't listed; their decks are still served. |
| `site/s5/show/<id>.html` | One deck per lesson. These are the app's own page-cache files, exactly as nginx served them. |
| `site/ui/default/` | S5 engine (slides.js, CSS, images) |
| `site/stylesheets/syntax/` | Code-highlighting themes the decks reference |
| `site/system/images/` | Paperclip images used by the decks (only the sizes referenced) |
| `crawl.log.gz` | HTTP status for every fetched path |
| `tools/` | `crawl.py` (the fetcher) and `make_index.py` (the index generator) |

## Serving

Deck URLs were `/s5/show/<id>`, with no extension. Serve `site/` with "extensionless URL → `.html`" handling so old links keep working. For example, Cloudflare Workers static assets with `html_handling: auto-trailing-slash`, or nginx `try_files $uri $uri.html =404`. All asset URLs are root-relative (`/ui/…`, `/system/…`), so the decks need to be served from a domain root, not a subpath. Opening them from `file://` won't work.

Image URLs carry Rails cache-busting query strings (`?1296087850`). The files are saved without them, and static hosts ignore the query.

## How it was made

1. The deck list was taken from the app's `/lessons` index and cross-checked against the `lessons` table: 47 lessons, IDs 5–64.
2. `python3 -I tools/crawl.py tools/ids.sorted site tools/extra_paths.txt` fetched `https://question.stungeye.com/s5/show/<id>` from the origin (159.203.24.194, bypassing Cloudflare, so no injected scripts), then every same-host `src`/`href`/CSS `url()` it referenced, plus the whole `/ui/` tree.
3. Lesson 14 had no page-cache file, so this crawl rendered it for the first time.
4. `tools/make_index.py` built the index from the DB. Its sections and copy were revised on 2026-10-25 (owner): decks with no course are placed in a section (or a course) by id, community talks are newest first, "Intro to Programming Logic" has a set order, and the author and company / event columns were dropped.

## Known gaps

The original content already had these broken links (404 on the live site too):

* deck 15 (DOM and Javascript): `/images/15/205.jpg`, `/images/15/207.jpg`
* deck 37 (Internet Bots for Fun & No Profit): a relative link `ruby-lang.org`, which resolves to `/s5/show/ruby-lang.org`

External links (GitHub, Flickr, shoesrb.com, …) were left as they are, and some are probably dead.

Not included: cached pages for four deleted lessons (33, 36, 48, 56), and the junk cache files that scanner probes created (`51'+and+1=1…` etc.).

## Hosting

Served from **Cloudflare Workers static assets** (Phase B of the olddroplet migration). `wrangler.jsonc`, `.gitignore`, `site/404.html` and this section are written by `hosting.py` (`python3 -I hosting.py question.stungeye.com <preview|routed|final>`).

* **Worker:** `static-question-stungeye-com`, account `Stungeye@gmail.com's Account`.
* **Deploy:** `npx wrangler@4.148.0 deploy` from the repo root. Only `site/` is uploaded.
* **Routes:** `question.stungeye.com/*` on zone `stungeye.com`, over the existing proxied DNS record.
* **workers.dev:** https://static-question-stungeye-com.stungeye.workers.dev. Per-version preview URLs are off (`preview_urls: false`).
* **Serving:** `html_handling: auto-trailing-slash` (`/foo` serves `foo.html`, `/foo/` serves `foo/index.html`; the other forms 307 to those) and `not_found_handling: 404-page` (`site/404.html`, a minimal page added in Phase B).
* **http → https:** the `stungeye.com` zone has "Always Use HTTPS" **off** (it also serves the owner's other sites), so http isn't redirected at the edge yet; decided at cutover.
* **Redirect rules:** none.
* **Rollback:** while the old origin is up, remove `routes` from `wrangler.jsonc` and deploy (or delete the route in the dashboard); the origin serves again at once. A bad version can be rolled back with `npx wrangler@4.148.0 rollback`.

## Secret scan

The Phase A §7.2 scan was run on `site/` before publishing. Its only hit is a code sample in deck 37 that uses a constant named `DB_PASSWORD`, with no value. Other "password" strings are teaching examples (`pass123`, `gorgonzola77`, `your_postgres_pass`). The wifi password field on deck 64 is blank.
