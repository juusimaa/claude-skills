#!/usr/bin/env python3
"""Tekee elokuvalistasta HTML-sivun (Artifact-työkalulle) ja tulostaa markdown-taulukon.

Syöte on koko viikon JSON-tiedosto:
    {"city": "Oulu", "title": "Elokuvat Oulussa", "generated": "2026-11-16T17:40",
     "from": "2026-11-16", "to": "2026-11-22",
     "screenings": [{"start": "2026-11-16T19:40", "film": "f1", "cinema": "Finnkino Plaza",
                     "auditorium": "Sali 1", "url": "", "note": ""}],
     "films": [{"id": "f1", "title": "…", "original": "…", "runtime": 158, "genres": ["Draama"],
                "premiere": "2026-10-23", "age": "12", "url": "", "tags": ["Uusi"]}],
     "sources": [{"name": "…", "url": "…", "ok": true}], "warnings": []}
Näytöksen pakolliset kentät ovat start (2026-11-16T19:40), film (films-listan id) ja cinema.
Sivulle menee aina koko JSON; ikkuna valitsee vain tulostettavan taulukon.

Käyttö:
    python3 -I sivu.py elokuvat.json elokuvat.html [--tanaan | --huomenna | --viikko]
"""
import html
import json
import pathlib
import re
import sys
from datetime import date, datetime, timedelta

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "elokuvat.html"
START = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
WD = ["ma", "ti", "ke", "to", "pe", "la", "su"]


def short_cinema(name: str) -> str:
    for p in ("Finnkino ", "Elokuvateatteri "):
        if name.startswith(p):
            return name[len(p):]
    return name


def cell(s) -> str:
    return (str(s) if s else "–").replace("|", "\\|").replace("\n", " ")


def clock(start: str) -> str:
    return start[11:16].replace(":", ".")


def dmy(d: date) -> str:
    return f"{d.day}.{d.month}.{d.year}"


def day_rows(data: dict, day: date, after: datetime | None) -> list:
    lo = after.isoformat(timespec="minutes") if after else ""
    rows = [s for s in data.get("screenings") or []
            if s["start"][:10] == day.isoformat() and s["start"] >= lo]
    return sorted(rows, key=lambda s: s["start"])


def md_day(data: dict, rows: list, heading: str) -> str:
    films = {f["id"]: f for f in data.get("films") or []}
    lines = [heading, "", "| Klo | Elokuva | Teatteri | Sali | Kesto | Ikäraja | Liput |", "|---|---|---|---|---|---|---|"]
    for s in rows:
        f = films[s["film"]]
        title = f["title"] + (" (Uusi)" if "Uusi" in (f.get("tags") or []) else "")
        lines.append("| " + " | ".join([
            clock(s["start"]), cell(title), cell(short_cinema(s["cinema"])), cell(s.get("auditorium")),
            f"{f['runtime']} min" if f.get("runtime") else "–", cell(f.get("age")),
            f"[Liput]({s['url']})" if s.get("url") else "–"]) + " |")
    if not rows:
        lines.append("Ei enää näytöksiä tänään." if "tänään" in heading else "Ei näytöksiä.")
    return "\n".join(lines)


def screenings_text(rows: list) -> str:
    cinemas = {}  # järjestys: ensimmäisen näytöksen mukaan
    for s in sorted(rows, key=lambda s: s["start"]):
        days = cinemas.setdefault(short_cinema(s["cinema"]), {})
        days.setdefault(s["start"][:10], []).append(clock(s["start"]))
    return " · ".join(
        f"{c}: " + ", ".join(f"{WD[date.fromisoformat(d).weekday()]} {' '.join(t)}" for d, t in days.items())
        for c, days in cinemas.items())


def md_week(data: dict, heading: str) -> str:
    by_film = {}
    for s in data.get("screenings") or []:
        by_film.setdefault(s["film"], []).append(s)
    films = [f for f in data.get("films") or [] if f["id"] in by_film or not by_film]
    films.sort(key=lambda f: ("Uusi" not in (f.get("tags") or []), -len(by_film.get(f["id"], [])), f["title"]))
    lines = [heading, "", "| Tagit | Elokuva | Kesto | Lajityyppi | Näytökset | Liput |", "|---|---|---|---|---|---|"]
    for f in films:
        lines.append("| " + " | ".join([
            cell(", ".join(f.get("tags") or [])), cell(f["title"]),
            f"{f['runtime']} min" if f.get("runtime") else "–", cell(", ".join(f.get("genres") or [])),
            cell(screenings_text(by_film.get(f["id"], []))),
            f"[Liput]({f['url']})" if f.get("url") else "–"]) + " |")
    return "\n".join(lines)


def week_range(a: date, b: date) -> str:
    if a.year != b.year:
        return f"{dmy(a)}–{dmy(b)}"
    if a.month != b.month:
        return f"{a.day}.{a.month}.–{b.day}.{b.month}.{b.year}"
    return f"{a.day}.–{b.day}.{b.month}.{b.year}"


def validate(data: dict) -> str:
    ids = {f.get("id") for f in data.get("films") or []}
    for i, s in enumerate(data.get("screenings") or []):
        if not all(s.get(k) for k in ("start", "film", "cinema")):
            return f"näytöksestä {i} puuttuu start, film tai cinema"
        if not START.fullmatch(s["start"]):
            return f"näytöksen {i} start ei ole muotoa 2026-11-16T19:40"
        if s["film"] not in ids:
            return f"näytöksen {i} film '{s['film']}' puuttuu films-listasta"
    return ""


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2 or len(flags) > 1 or any(f not in ("--tanaan", "--huomenna", "--viikko") for f in flags):
        print(__doc__, file=sys.stderr)
        return 2
    window = flags[0] if flags else "--tanaan"
    data = json.loads(pathlib.Path(args[0]).read_text(encoding="utf-8"))
    err = validate(data)
    if err:
        print(err, file=sys.stderr)
        return 1
    title = data.get("title") or "Elokuvat"
    gen = datetime.fromisoformat(data["generated"])
    if window == "--viikko":
        table = md_week(data, f"{title} {week_range(date.fromisoformat(data['from']), date.fromisoformat(data['to']))}")
    elif window == "--huomenna":
        day = gen.date() + timedelta(days=1)
        table = md_day(data, day_rows(data, day, None), f"{title} huomenna {dmy(day)}")
    else:
        table = md_day(data, day_rows(data, gen.date(), gen), f"{title} tänään {dmy(gen.date())}")
    # "</" katkaisisi script-elementin, joten se escapetaan JSONin sisällä.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(title)).replace("__DATA__", payload)
    pathlib.Path(args[1]).write_text(page, encoding="utf-8")
    print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
