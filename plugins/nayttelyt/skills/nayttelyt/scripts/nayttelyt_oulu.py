#!/usr/bin/env python3
"""Hakee Oulun näyttelyt: kaupungin tapahtumapalvelu, Oulun taidemuseo ja Kulttuuritalo Valve
sekä pysyvät näyttelyt (Tiima, taidemuseo) vakioriveinä. Lähteet: cities/oulu.md.

Käyttö:
    python3 -I nayttelyt_oulu.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--table]
Oletus: tänään – tämän viikon sunnuntai. Tuloste on JSON-lista tai taulukko (--table).
Lähde, joka ei vastaa, raportoidaan stderriin ja ohitetaan.
"""
import argparse
import html as htmllib
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
FI = ZoneInfo("Europe/Helsinki")
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


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def text(fragment: str) -> str:
    """HTML-pätkä siistiksi tekstiksi."""
    s = re.sub(r"<br\s*/?>", " ", fragment)
    s = htmllib.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xad", "")
    return re.sub(r"\s+", " ", s).strip(" ,")


def fold(s: str) -> str:
    """Vertailuavain: pienet kirjaimet ilman ääkkösten pisteitä ("Jyväskylä" -> "jyvaskyla")."""
    return "".join(c for c in unicodedata.normalize("NFD", s.strip().lower()) if not unicodedata.combining(c))


def this_week(today: date) -> tuple[date, date]:
    return today, today + timedelta(days=6 - today.weekday())


def overlaps(e: dict, frm: date, to: date) -> bool:
    if e.get("permanent"):
        return True
    s = date.fromisoformat(e["start"]) if e.get("start") else date.min
    t = date.fromisoformat(e["end"]) if e.get("end") else date.max
    return s <= to and t >= frm


def is_exhibition(name: str, start: str, end: str) -> bool:
    return start != end and not NOISE.search(name)


def merge(rows: list[dict]) -> list[dict]:
    out: dict = {}
    for r in rows:
        k = (fold(r["name"]), fold(r["venue"]))
        if k not in out:
            out[k] = dict(r)
            continue
        for f, v in r.items():
            if out[k].get(f) in ("", "–", None) and v not in ("", "–", None):
                out[k][f] = v
    return list(out.values())


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


def helsinki_day(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(FI).date().isoformat()


def tapahtumapalvelu(today: date) -> list[dict]:
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


def taidemuseo(today: date) -> list[dict]:
    out = []
    pat = r'class="item-date[^>]*>([^<]*)</span>.*?<h2>(.*?)</h2>.*?href="([^"]+)"'
    for d, name, url in re.findall(pat, fetch(MUSEO_URL), re.S):
        m = re.findall(r"(\d+)\.(\d+)\.(\d{4})", d)
        if len(m) != 2:
            continue
        s, e = (date(int(y), int(mo), int(dd)).isoformat() for dd, mo, y in m)
        out.append(row(text(name), MUSEO, s, e, url=url, source="ouluntaidemuseo.fi"))
    return out


def valve(today: date) -> list[dict]:
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


def pysyvat(today: date) -> list[dict]:
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


def table(rows: list[dict]) -> str:
    head = ["Näyttely", "Paikka", "Ajalla", "Aukioloajat", "Hinta"]
    body = [[r["name"], r["venue"], "Pysyvä" if r["permanent"] else f'{r["start"] or "–"} – {r["end"] or "–"}',
             r["hours"] or "–", r["price"] or "–"] for r in rows]
    w = [max(len(x[i]) for x in [head] + body) for i in range(len(head))]
    return "\n".join("  ".join(c.ljust(w[i]) for i, c in enumerate(x)).rstrip() for x in [head] + body)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args(argv)
    today = datetime.now(FI).date()
    frm = date.fromisoformat(a.frm) if a.frm else this_week(today)[0]
    to = date.fromisoformat(a.to) if a.to else this_week(today)[1]
    rows = []
    for rd in READERS:
        try:
            rows += rd(today)
        except Exception as ex:
            print(f"{rd.__name__}: {ex}", file=sys.stderr)
    rows = merge([r for r in rows if (r["permanent"] or is_exhibition(r["name"], r["start"], r["end"])) and overlaps(r, frm, to)])
    rows.sort(key=lambda r: (r["permanent"], r["start"], r["name"]))
    print(table(rows) if a.table else json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
