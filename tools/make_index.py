#!/usr/bin/env python3
"""Build site/index.html (the list of S5 decks) from lessons.usv.

Usage: python3 -I tools/make_index.py lessons.usv site/index.html
lessons.usv columns (\\x1f-separated): course, id, title, author, company, created, updated.
Grouping and order match the app's /lessons page (courses by name, lessons by id).
"""
import sys
from html import escape
from itertools import groupby

rows = [l.rstrip("\n").split("\x1f") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
parts = []
for course, lessons in groupby(rows, key=lambda r: r[0]):
    parts.append(f"<h2>{escape(course) or 'Other talks'}</h2>\n<table>\n"
                 "<tr><th>Title</th><th>Author</th><th>Company / event</th><th>Updated</th></tr>")
    for _, lid, title, author, company, _created, updated in lessons:
        parts.append(f'<tr><td><a href="/s5/show/{lid}">{escape(title)}</a></td>'
                     f"<td>{escape(author)}</td><td>{escape(company)}</td><td>{updated}</td></tr>")
    parts.append("</table>")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Slide decks · question.stungeye.com</title>
<style>
  body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 60rem; margin: 2rem auto; padding: 0 1rem; color: #222; background: #fff; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
  th, td {{ text-align: left; padding: .3rem .6rem; border-bottom: 1px solid #ddd; vertical-align: top; }}
  th {{ font-size: .85rem; color: #555; }}
  td:last-child {{ white-space: nowrap; color: #555; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #161616; }} a {{ color: #8ab4f8; }}
    th, td:last-child {{ color: #aaa; }} th, td {{ border-color: #333; }}
  }}
</style>
</head>
<body>
<h1>Slide decks</h1>
<p>S5 slide decks by Kyle Geske, published from question.stungeye.com between 2009 and 2022.
This is a static archive made in October 2026. Open a deck, then use the arrow keys to move between slides.</p>
{chr(10).join(parts)}
</body>
</html>
"""
open(sys.argv[2], "w", encoding="utf-8").write(page)
print(f"{len(rows)} decks")
