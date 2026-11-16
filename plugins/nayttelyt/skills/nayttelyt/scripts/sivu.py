#!/usr/bin/env python3
"""Tekee näyttelylistasta HTML-sivun (Artifact-työkalulle) ja tulostaa markdown-taulukon.

Syöte on JSON-tiedosto:
    {"title": "Näyttelyt Oulussa", "range": "16.–22.11.2026", "generated": "2026-11-16",
     "from": "2026-11-16", "to": "2026-11-22",
     "exhibitions": [{"name": "…", "venue": "…", "start": "2026-11-20", "end": "2027-03-01",
                      "permanent": false, "hours": "", "price": "", "url": "", "note": "", "source": ""}],
     "notes": ["…"], "sources": [{"name": "…", "url": "…"}]}
Pakollisia ovat name ja venue; start ja end ovat tyhjiä tai muotoa 2026-11-20.

Käyttö:
    python3 -I sivu.py nayttelyt.json nayttelyt.html
"""
import html
import json
import pathlib
import re
import sys
from datetime import date, timedelta

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "nayttelyt.html"
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def tags(e: dict, frm: date, today: date) -> list:
    out = []
    if e.get("start") and frm <= date.fromisoformat(e["start"]) <= frm + timedelta(days=6):
        out.append("Uusi")
    if e.get("end") and today <= date.fromisoformat(e["end"]) <= today + timedelta(days=7):
        out.append("Päättyy pian")
    if e.get("permanent"):
        out.append("Pysyvä")
    return out


def sort_key(e: dict) -> tuple:
    t = e.get("tags") or []
    rank = 3 if e.get("permanent") else 0 if "Uusi" in t else 1 if "Päättyy pian" in t else 2
    return (rank, e.get("start") or "", e.get("name") or "")


def date_text(e: dict, today: date) -> str:
    if e.get("permanent"):
        return "Pysyvä"

    def f(iso):
        d = date.fromisoformat(iso)
        return f"{d.day}.{d.month}." + (str(d.year) if d.year != today.year else "")

    if not e.get("start") and not e.get("end"):
        return "–"
    return f"{f(e['start']) if e.get('start') else ''}–{f(e['end']) if e.get('end') else ''}"


def md_table(data: dict) -> str:
    today = date.fromisoformat(data["generated"])
    cell = lambda s: (s or "–").replace("|", "\\|").replace("\n", " ")
    lines = [f"{data.get('title', '')} {data.get('range', '')}".strip(), "",
             "| Tagit | Näyttely | Paikka | Ajalla | Aukioloajat | Hinta | Linkki |", "|---|---|---|---|---|---|---|"]
    for e in data.get("exhibitions") or []:
        link = f"[Linkki]({e['url']})" if e.get("url") else "–"
        lines.append("| " + " | ".join([cell(", ".join(e.get("tags") or [])), cell(e["name"]), cell(e["venue"]),
                                        cell(date_text(e, today)), cell(e.get("hours")), cell(e.get("price")), link]) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    data = json.loads(pathlib.Path(argv[0]).read_text(encoding="utf-8"))
    rows = data.get("exhibitions") or []
    missing = [i for i, e in enumerate(rows) if not all(e.get(k) for k in ("name", "venue"))]
    if missing:
        print(f"näyttelystä puuttuu name tai venue: indeksit {missing}", file=sys.stderr)
        return 1
    bad = [i for i, e in enumerate(rows) if any(e.get(k) and not ISO.fullmatch(e[k]) for k in ("start", "end"))]
    if bad:
        print(f"start tai end ei ole muotoa 2026-11-20: indeksit {bad}", file=sys.stderr)
        return 1
    frm, today = date.fromisoformat(data["from"]), date.fromisoformat(data["generated"])
    for e in rows:
        e["tags"] = tags(e, frm, today)
    data["exhibitions"] = rows = sorted(rows, key=sort_key)
    for e in rows:
        e["dates"] = date_text(e, today)
    # "</" katkaisisi script-elementin, joten se escapetaan JSONin sisällä.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(data.get("title") or "Näyttelyt")).replace("__DATA__", payload)
    pathlib.Path(argv[1]).write_text(page, encoding="utf-8")
    print(md_table(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
