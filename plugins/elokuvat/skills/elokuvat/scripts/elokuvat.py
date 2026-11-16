#!/usr/bin/env python3
"""Hakee kaupungin elokuvanäytökset: näytösajat elokuviin.com-sivulta (sivun __NEXT_DATA__-JSON)
sekä ensi-illat ja ikärajat nytleffaan.fi-sivulta, yhdistää ne ja tulostaa koko viikon JSON:na.

Käyttö:
    python3 -I elokuvat.py --city Oulu [--table]
Ikkuna on tänään – tämän viikon sunnuntai (Europe/Helsinki). Lähde, joka ei vastaa, raportoidaan
stderriin ja `sources`-kenttään (ok: false); skripti päättyy silti koodiin 0.
Tuntematon kaupunki (elokuviin.com 404): viesti stderriin ja paluukoodi 2.
Näytösaikoja ei koskaan arvata.
"""
import argparse
import html as htmllib
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
FI = ZoneInfo("Europe/Helsinki")
WEEKEND_WARNING = "Viikonlopun näytöksiä on vielä vähän: teatterit julkaisevat ne yleensä viikon loppupuolella."
WD = "ma ti ke to pe la su".split()


class CityNotFound(Exception):
    pass


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def slug(city: str) -> str:
    return urllib.parse.quote(city.strip().lower().replace(" ", "-"))


def fold(s: str) -> str:
    """Yhdistämisavain: pienet kirjaimet, ei diakriitteja, vain kirjaimet ja numerot."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalnum() and not unicodedata.combining(c))


def local(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(FI).strftime("%Y-%m-%dT%H:%M")


def parse_elokuviin(page: str) -> dict:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    if not m:
        raise ValueError("__NEXT_DATA__ puuttuu")
    d = json.loads(m.group(1))["props"]["pageProps"]
    # screeningCinemas can lack a cinema that `cinemas` has
    cinemas = {c["id"]: c["name"] for c in d.get("cinemas") or []}
    cinemas.update({k: v["name"] for k, v in (d.get("screeningCinemas") or {}).items()})
    movies = d.get("movies") or {}
    screenings, used = [], []
    for s in d.get("screenings") or []:
        mv = movies.get(s["movieId"])
        if not mv:
            continue
        f = s.get("festival")
        note = f.get("name", "") if isinstance(f, dict) else ("Ulkoilma" if s.get("outdoor") else "")
        screenings.append({"start": local(s["startsAt"]), "film": s["movieId"],
                           "cinema": cinemas.get(s.get("cinemaId"), ""), "auditorium": s.get("auditorium") or "",
                           "url": s.get("bookingLink") or "", "note": note})
        if s["movieId"] not in used:
            used.append(s["movieId"])
    films = []
    for i in used:
        mv = movies[i]
        title = mv.get("titleFI") or mv.get("title") or ""
        films.append({"id": i, "title": title, "original": mv.get("title") or title, "runtime": mv.get("runtime"),
                      "genres": [g["name"] for g in mv.get("genres") or []],
                      "url": "https://elokuviin.com/elokuvat/" + mv["slug"] if mv.get("slug") else ""})
    city = d.get("cityObject") or {}
    return {"city": city.get("name", ""), "inessive": city.get("nameInesive", ""),
            "screenings": screenings, "films": films}


def parse_nytleffaan(page: str) -> list:
    out = []
    for card in page.split("<div class='movie-card paikkakunta-page-movie-card'>")[1:]:
        t = re.search(r"<h3>(.*?)</h3>", card, re.S)
        if not t:
            continue
        age = re.search(r"data/icons/([^./']+)\.png", card)
        dt = re.search(r"movie-card-premiere-date'>(\d+)\.(\d+)\.(\d{4})<", card)
        href = re.search(r"class='movie-card-movie-link' href='([^']*)'", card)
        out.append({"title": htmllib.unescape(t.group(1)).strip(),
                    "premiere": f"{dt.group(3)}-{int(dt.group(2)):02d}-{int(dt.group(1)):02d}" if dt else "",
                    "age": age.group(1) if age else "", "url": href.group(1) if href else ""})
    return out


def is_new(premiere: str, today: date, to: date) -> bool:
    return bool(premiere) and today - timedelta(days=7) <= date.fromisoformat(premiere) <= to


def join(films: list, nyt: list, today: date, to: date) -> list:
    by = {}
    for n in nyt:
        by.setdefault(fold(n["title"]), n)
    out = []
    for f in films:
        n = by.get(fold(f["title"]), {})
        p = n.get("premiere", "")
        out.append({**f, "premiere": p, "age": n.get("age", ""), "tags": ["Uusi"] if is_new(p, today, to) else []})
    return out


def weekend_warning(screenings: list, today: date, to: date) -> bool:
    days = [today + timedelta(days=i) for i in range((to - today).days + 1)]
    count = {}
    for s in screenings:
        count[s["start"][:10]] = count.get(s["start"][:10], 0) + 1
    early = [count.get(d.isoformat(), 0) for d in days if d.weekday() < 4]
    wknd = [count.get(d.isoformat(), 0) for d in days if d.weekday() >= 4]
    return bool(early and wknd) and sum(wknd) / len(wknd) < sum(early) / len(early) / 2


def build(city: str, now: datetime, fetch=fetch) -> dict:
    today = now.date()
    to = today + timedelta(days=6 - today.weekday())
    src = [{"name": "elokuviin.com", "url": "https://elokuviin.com/" + slug(city), "ok": True},
           {"name": "nytleffaan.fi", "url": f"https://nytleffaan.fi/paikkakunta/{slug(city)}/", "ok": True}]
    warnings, el, nyt = [], None, []
    try:
        el = parse_elokuviin(fetch(src[0]["url"]))
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            raise CityNotFound(city)
        el = None
    except Exception:
        el = None
    if el is None:
        src[0]["ok"] = False
        warnings.append("elokuviin.com ei vastannut: näytösajat puuttuvat.")
        print(warnings[-1], file=sys.stderr)
    try:
        nyt = parse_nytleffaan(fetch(src[1]["url"]))
    except Exception:
        src[1]["ok"] = False
        warnings.append("nytleffaan.fi ei vastannut: ensi-illat ja ikärajat puuttuvat.")
        print(warnings[-1], file=sys.stderr)
    if el is None:
        films = [{"id": f"n{i}", "title": n["title"], "original": n["title"], "runtime": None, "genres": [],
                  "url": n["url"]} for i, n in enumerate(n for n in nyt if n["premiere"] <= to.isoformat())]
        films = join(films, nyt, today, to)
        screenings, name, inessive = [], city.strip().capitalize(), ""
    else:
        lo, hi = today.isoformat(), to.isoformat()
        screenings = sorted((s for s in el["screenings"] if lo <= s["start"][:10] <= hi),
                            key=lambda s: (s["start"], s["cinema"]))
        ids = {s["film"] for s in screenings}
        films = join([f for f in el["films"] if f["id"] in ids], nyt, today, to)
        name, inessive = el["city"] or city.strip().capitalize(), el["inessive"]
        if weekend_warning(screenings, today, to):
            warnings.append(WEEKEND_WARNING)
    return {"city": name, "title": "Elokuvat " + (inessive or name), "generated": now.strftime("%Y-%m-%dT%H:%M"),
            "from": today.isoformat(), "to": to.isoformat(), "screenings": screenings, "films": films,
            "sources": src, "warnings": warnings}


def table(data: dict) -> str:
    films = {f["id"]: f for f in data["films"]}
    rows = []
    for s in data["screenings"]:
        d = datetime.fromisoformat(s["start"])
        rows.append(f'{WD[d.weekday()]} {d.day}.{d.month}. {d:%H.%M}  {films[s["film"]]["title"]}  {s["cinema"]}')
    return "\n".join(rows) or "Ei näytöksiä."


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args(argv)
    try:
        data = build(a.city, datetime.now(FI), fetch=fetch)
    except CityNotFound:
        print(f"elokuviin.com ei tunne kaupunkia '{a.city}'.", file=sys.stderr)
        return 2
    print(table(data) if a.table else json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
