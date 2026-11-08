#!/usr/bin/env python3
"""Tekee yhdistetystä keikkalistasta HTML-sivun, jonka voi julkaista Artifact-työkalulla.

Syöte on JSON-tiedosto:
    {
      "title": "Keikat Oulussa",
      "range": "8.11.–8.12.2026",
      "generated": "8.11.2026",
      "events": [
        {"date": "2026-11-14", "artist": "Jemina", "venue": "Tuba", "price": "20 € (ovelta 24 €)",
         "status": "saatavilla", "url": "https://…", "time": "klo 20", "end": "", "note": ""}
      ],
      "notes": ["Lista ei ole täydellinen …"],
      "sources": [{"name": "Tiketti", "url": "https://www.tiketti.fi/"}]
    }
Tapahtumista pakollisia ovat date, artist ja venue. Sivu järjestää ne päivän mukaan.

Käyttö:
    python3 -I sivu.py keikat.json keikat.html
"""
import html
import json
import pathlib
import re
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "keikat.html"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    events = data.get("events") or []
    missing = [i for i, e in enumerate(events) if not all(e.get(k) for k in ("date", "artist", "venue"))]
    if missing:
        print(f"tapahtumista puuttuu date, artist tai venue: indeksit {missing}", file=sys.stderr)
        return 1
    iso = re.compile(r"\d{4}-\d{2}-\d{2}")
    bad = [i for i, e in enumerate(events)
           if not iso.fullmatch(e["date"]) or (e.get("end") and not iso.fullmatch(e["end"]))]
    if bad:
        print(f"date tai end ei ole muotoa 2026-11-14: indeksit {bad}", file=sys.stderr)
        return 1
    data["events"] = sorted(events, key=lambda e: (e["date"], e["venue"], e["artist"]))
    # "</" katkaisisi script-elementin, joten se escapetaan JSONin sisällä.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(data.get("title") or "Keikat")).replace("__DATA__", payload)
    pathlib.Path(sys.argv[2]).write_text(page, encoding="utf-8")
    print(f"{len(events)} keikkaa -> {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
