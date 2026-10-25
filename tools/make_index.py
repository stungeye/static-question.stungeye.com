#!/usr/bin/env python3
"""Build site/index.html (the list of S5 decks) from lessons.usv.

Usage: python3 -I tools/make_index.py lessons.usv site/index.html
lessons.usv columns (\\x1f-separated): course, id, title, author, company, created, updated.
Three sections (owner, 2026-10-25): community talks, work talks, course modules (grouped by course name).
Decks with no course are placed by id in COMMUNITY / WORK, or in a course by COURSE_OF. Courses in HIDDEN aren't listed
(their decks are still served at /s5/show/<id>). Community talks are newest first (by updated date); a course in ORDER
uses that order; everything else is in id order, as on the app's /lessons page.
"""
import sys
from html import escape
from itertools import groupby

COMMUNITY = {34, 37, 39, 51, 52, 64}     # meetups and events (WinnipegRb, BSides Winnipeg, Sound + Code = Jam, paper talks)
WORK = {38, 55}                          # internal presentations for coworkers
COURSE_OF = {43: "Intro to Programming Logic"}   # course material with no course in the app
HIDDEN = {"Game Dev Drafts", "XML & Mobile Computing"}
ORDER = {"Intro to Programming Logic": [19, 21, 22, 25, 49, 26, 27, 28, 42, 43, 44, 29]}   # owner, 2026-10-25

rows = [l.rstrip("\n").split("\x1f") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
community, work, courses = [], [], []
for course, lid, title, _author, _company, _created, updated in rows:
    deck = (int(lid), title, updated)
    if course.strip():
        if course not in HIDDEN:
            courses.append((course, deck))
    elif deck[0] in COMMUNITY:
        community.append(deck)
    elif deck[0] in WORK:
        work.append(deck)
    elif deck[0] in COURSE_OF:
        courses.append((COURSE_OF[deck[0]], deck))
    else:
        sys.exit(f"deck {lid} ({title}) has no course and no section")


def deck_list(decks, order=None):
    decks = sorted(decks)
    if order:
        assert sorted(order) == [d[0] for d in decks], (order, decks)
        decks.sort(key=lambda d: order.index(d[0]))
    items = [f'<li><a href="/s5/show/{lid}">{escape(title)}</a> <span class="date">{updated[:4]}</span></li>'
             for lid, title, updated in decks]
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


courses.sort(key=lambda c: c[0])   # by course name
community.sort(key=lambda d: d[2], reverse=True)   # newest first
parts = ["<h2>Community talks</h2>\n<p>Presented at local meetups and events.</p>", deck_list(community, [d[0] for d in community]),
         "<h2>Work talks</h2>\n<p>Internal presentations for coworkers.</p>", deck_list(work),
         "<h2>Course modules</h2>\n<p>Notes and slides for courses taught in the Business Information Technology (BIT) "
         "program at Red River College.</p>"]
for course, group in groupby(courses, key=lambda c: c[0]):
    parts += [f"<h3>{escape(course)}</h3>", deck_list((d for _, d in group), ORDER.get(course))]

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Slide Decks · question.stungeye.com</title>
<style>
  body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 48rem; margin: 2rem auto; padding: 0 1rem; color: #222; background: #fff; }}
  h2 {{ margin-top: 2rem; border-bottom: 1px solid #ddd; }}
  h2 + p {{ margin-top: -.25rem; color: #555; }}
  ul {{ padding-left: 1.2rem; }}
  li {{ margin: .2rem 0; }}
  .date {{ color: #777; font-size: .85rem; margin-left: .3rem; }}
  kbd {{ font: .85rem ui-monospace, monospace; border: 1px solid #bbb; border-radius: 3px; padding: 0 .3rem; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #161616; }} a {{ color: #8ab4f8; }}
    h2 {{ border-color: #333; }} h2 + p, .date {{ color: #aaa; }} kbd {{ border-color: #555; }}
  }}
</style>
</head>
<body>
<h1>Slide Decks From 2008 to 2022</h1>
<p>Course modules and event talks written by Kyle Geske for work and community events.</p>
<p>Decks open as a single scrolling page. Press <kbd>t</kbd> with a deck open to toggle slide view, then use the arrow keys to move between slides.</p>
{chr(10).join(parts)}
</body>
</html>
"""
open(sys.argv[2], "w", encoding="utf-8").write(page)
print(f"{len(community)} community, {len(work)} work, {len(courses)} course decks; {len(rows) - len(community) - len(work) - len(courses)} hidden")
