#!/usr/bin/env python3
"""Hakee Oulun näyttelyt: kaupungin tapahtumapalvelu, Oulun taidemuseo ja Kulttuuritalo Valve
sekä pysyvät näyttelyt (Tiima, taidemuseo) vakioriveinä. Lähteet: cities/oulu.md.

Käyttö:
    python3 -I nayttelyt_oulu.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--table]
Oletus: tänään – tämän viikon sunnuntai. Tuloste on JSON-lista tai taulukko (--table).
Lähde, joka ei vastaa, raportoidaan stderriin ja ohitetaan.
"""
import json
import pathlib
import re
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # -I jättää skriptin kansion pois
from yhteiset import fetch, fold, helsinki_day, merge, overlaps, run, text, this_week  # noqa: E402,F401
EVENTS = "https://tapahtumat.munoulu.fi/api/search/internal-content-fetch?lang=fi&country=FI&mode=event"
PAGE = "https://tapahtumat.munoulu.fi/fi-FI/page/"
WIDGET = ("https://tapahtumat.munoulu.fi/widget/67b6f7af04b40b760fdd944c?currentLocation="
          "https%3A%2F%2Fwww.kulttuurivalve.fi%2Ftervetuloa-vierailulle%2Fnayttelyt-valveella%2F&nolog=true")
MUSEO_URL = "https://ouluntaidemuseo.fi/nayttelyt/"
FREE_ID = "6170601b7a45476ff366cb18"
VALVE_CLOSES = "2027-04-30"  # peruskorjaus alkaa 1.5.2027
NOISE = re.compile(
    r"esittely|työpaja|opastus|opastettu|kierros|luento|esitelmä|kurssi|elokuva|festivaali|tapaaminen"
    r"|verkkonäyttely|lumo|palaveri|julkistus|juhlist", re.I)

# Aukioloajat ja hinnat, tarkistettu 2026-11-16 (cities/oulu.md, Pysyvät näyttelyt).
MUSEO = "Oulun taidemuseo"
MUSEO_HOURS = "ti–to 9–18, pe 11–19, la–su 11–18, ma suljettu"
MUSEO_PRICE = "12 € / alennus 9 €"
TIIMA = "Tiima (Tietomaa, Oulun museo, Lasten museo)"
TIIMA_HOURS = "ma–pe 11–19, la–su 10–18"
TIIMA_PRICE = "22 € / alennus 14 €"
VALVE = "Kulttuuritalo Valve"
VALVE_HOURS = "ma–pe 9–21, la–su 10–21"
VENUE_INFO = {MUSEO: (MUSEO_HOURS, MUSEO_PRICE), TIIMA: (TIIMA_HOURS, TIIMA_PRICE), VALVE: (VALVE_HOURS, "Ilmainen")}


def is_exhibition(name: str, start: str, end: str) -> bool:
    return start != end and not NOISE.search(name)


def row(name, venue, start="", end="", permanent=False, hours="", price="–", url="", note="", source=""):
    h, p = VENUE_INFO.get(venue, ("", "–"))
    return {"name": name, "venue": venue, "start": start, "end": end, "permanent": permanent,
            "hours": hours or h or "–", "price": price if price != "–" else p, "url": url, "note": note, "source": source}


def venue_of(addr: str) -> str:
    a = fold(addr)
    if "valve" in a or "hallituskatu 7" in a:
        return VALVE
    if "taidemuseo" in a or "kasarmintie 9" in a:  # Kasarmintie 11 is a different venue (Rapumaja)
        return MUSEO
    if any(k in a for k in ("tiima", "tietomaa", "nahkatehtaankatu", "oulun museo")):
        return TIIMA
    parts = [s.strip() for s in addr.split(",") if s.strip()]
    # "Näyttely, Kauppurienkatu 10 …": the first part is a generic word, so use the street.
    if len(parts) > 1 and fold(parts[0]) in ("nayttely", "galleria", "nayttelytila"):
        parts = parts[1:]
    return parts[0] if parts else "–"


def cap(r: dict) -> dict:
    if r["venue"] == VALVE and (not r["end"] or r["end"] > VALVE_CLOSES):
        r["end"] = VALVE_CLOSES
    return r


def tapahtumapalvelu(frm: date, to: date) -> list[dict]:
    out = []
    for p in json.loads(fetch(EVENTS))["pages"]:
        cats = p.get("globalContentCategories") or []
        if "Exhibitions" not in cats or (p.get("event") or {}).get("isCancelled"):
            continue
        # The Exhibitions category also holds film screenings, guided tours and online-only works.
        if set(cats) & {"Movies / Cinema", "Excursions, guided tours", "Virtual"}:
            continue
        if not p.get("defaultStartDate") or not p.get("defaultEndDate"):
            continue
        addr = ((p.get("locations") or [{}])[0] or {}).get("address", "") or ""
        venue = venue_of(addr)
        if "kirjasto" in fold(addr) and "saari" not in fold(addr):
            continue  # haarakirjastojen vitriinit pois
        start, end = helsinki_day(p["defaultStartDate"]), helsinki_day(p["defaultEndDate"])
        if venue == TIIMA and end >= "2028":
            continue  # pysyvä, kattaa Tiiman pysyvä rivi
        free = FREE_ID in (p.get("categories") or []) or "vapaa pääsy" in (p.get("descriptionShort") or "").lower()
        out.append(cap(row(p["name"].strip(), venue or "–", start, end, price="Ilmainen" if free else "–",
                           url=PAGE + p["_id"], source="tapahtumat.munoulu.fi")))
    return out


def taidemuseo(frm: date, to: date) -> list[dict]:
    out = []
    pat = r'class="item-date[^>]*>([^<]*)</span>.*?<h2>(.*?)</h2>.*?href="([^"]+)"'
    for d, name, url in re.findall(pat, fetch(MUSEO_URL), re.S):
        m = re.findall(r"(\d+)\.(\d+)\.(\d{4})", d)
        if len(m) != 2:
            continue
        s, e = (date(int(y), int(mo), int(dd)).isoformat() for dd, mo, y in m)
        out.append(row(text(name), MUSEO, s, e, url=url, source="ouluntaidemuseo.fi"))
    return out


def valve(frm: date, to: date) -> list[dict]:
    out = []
    for card in json.loads(fetch(WIDGET))["html"].split('<div class="bubster-page')[1:]:
        g = lambda c: re.search(r'class="%s"[^>]*>(.*?)</(?:a|div)>' % c, card, re.S)
        n, t, loc, pid = g("bubster-name"), g("bubster-time"), g("bubster-location"), re.search(r'bubster-page-(\w+)', card)
        d = re.findall(r"(\d+)\.(\d+)\.(\d{4})", t.group(1)) if t else []
        if not (n and pid and len(d) == 2):
            continue  # yksittäinen tapahtuma pois
        s, e = (date(int(y), int(mo), int(dd)).isoformat() for dd, mo, y in d)
        place = text(loc.group(1)) if loc else ""
        gallery = place.split(",")[0]
        out.append(cap(row(text(n.group(1)), VALVE, s, e, url=PAGE + pid.group(1),
                           note="" if gallery == VALVE else gallery, source="tapahtumat.munoulu.fi (Valve)")))
    return out


def pysyvat(frm: date, to: date) -> list[dict]:
    return [
        row("Oulun taidemuseo – pysyvät näyttelyt", MUSEO, permanent=True, url="https://ouluntaidemuseo.fi/kokoelmanayttelyt/",
            note="Kokoelmanäyttelyt, ei kiinteää jaksoa", source="ouluntaidemuseo.fi"),
        row("Galleria Oskari Jauhiainen", "Syke-talo, Kiiminki", permanent=True, hours="Kiimingin kirjaston aukioloaikoina",
            price="Ilmainen", url="https://ouluntaidemuseo.fi/nayttely/galleria-oskari-jauhiainen/", source="ouluntaidemuseo.fi"),
        row("Tiima – pysyvät näyttelyt", TIIMA, permanent=True, url="https://www.tiima-oulu.fi/",
            note="Masiina, Aurora Revelare, Eläinten jäljillä, Värkkäämö, Oulu: Tarinani, Rikoksetta rangaistut, "
                 "Polkuja kaupungissa, Seikkailutehdas, Metallikausi", source="tietomaa.fi"),
        row("Merimiehenkotimuseo – perusnäyttely", "Merimiehenkotimuseo", "2026-11-28", "2026-12-20", hours="la–su 11–17",
            price="Ilmainen", url="https://merimiehenkotimuseo.fi/", note="Avoinna vain tänä aikana", source="merimiehenkotimuseo.fi"),
    ]


READERS = [tapahtumapalvelu, taidemuseo, valve, pysyvat]


def main(argv=None) -> int:
    return run(READERS, lambda r: is_exhibition(r["name"], r["start"], r["end"]), argv)


if __name__ == "__main__":
    sys.exit(main())
