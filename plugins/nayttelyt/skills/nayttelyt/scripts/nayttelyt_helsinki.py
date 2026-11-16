#!/usr/bin/env python3
"""Hakee Helsingin näyttelyt: museot museot.fi-näyttelykalenterista (aukioloajat ja hinnat museon sivulta)
ja galleriat sekä muut Linked Events -rajapinnasta. Lähteet: cities/helsinki.md.

Käyttö:
    python3 -I nayttelyt_helsinki.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--table]
Oletus: tänään – tämän viikon sunnuntai. Tuloste on JSON-lista tai taulukko (--table).
Lähde, joka ei vastaa, raportoidaan stderriin ja ohitetaan.
"""
import json
import pathlib
import re
import ssl
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # -I jättää skriptin kansion pois
from yhteiset import fetch, fold, helsinki_day, overlaps, run, text  # noqa: E402
from nayttelyt_oulu import NOISE  # noqa: E402

CERT = pathlib.Path(__file__).resolve().parent.parent / "certs" / "telia-rsa-dv-ca-v4.pem"
LINKED = ("https://api.hel.fi/linkedevents/v1/event/?keyword=yso:p5121&division=helsinki"
          "&start={}&end={}&include=location&page_size=100")
MUSEOT = "https://museot.fi"
MUSEOT_LIST = MUSEOT + "/nayttelykalenteri/index.php?maakunta_id=1&nayttelyhaku=1&kaikki=1"  # 1 = Uusimaa
DROP_VENUE = re.compile(r"kirjasto|yhteisotalo|asukast|seniorikeskus|palvelukeskus|perhetalo|musiikkiopisto|^internet$", re.I)
# Toistuvat ohjelmat, joita Linked Events kutsuu näyttelyiksi (Kiasma, Arkkitehtuuri- ja designmuseo, Suomenlinna).
PROGRAMME = re.compile(r"ilmaispäivä|ilmaisilta|treffiperjantai|museorasti", re.I)
OODI = "keskustakirjasto oodi"
# Linked Eventsin paikan nimi (foldattu) -> museot.fi:n nimi, jotta merge yhdistää rivit.
ALIASES = {
    "helsingin taidemuseo ham": "HAM Helsingin taidemuseo",
    "luonnontieteellinen museo": "LUOMUS Luonnontieteellinen museo",
    "kaisaniemen kasvitieteellinen puutarha": "LUOMUS Kaisaniemen kasvitieteellinen puutarha",
    "median museo ja arkisto merkki": "Merkki",
    "tiedemuseo liekin observatorio": "Tiedemuseo Liekki, Observatorio",
}


def row(name, venue, start="", end="", permanent=False, hours="–", price="–", url="", note="", source=""):
    return {"name": name, "venue": venue, "start": start, "end": end, "permanent": permanent,
            "hours": hours, "price": price, "url": url, "note": note, "source": source}


def canon_venue(name: str) -> str:
    return ALIASES.get(fold(name), name)


def parse_linkedevents(events: list[dict]) -> list[dict]:
    out = []
    for e in events:
        name = (e["name"].get("fi") or next(iter(e["name"].values()), "")).strip()
        venue = ((e.get("location") or {}).get("name") or {}).get("fi", "").strip()
        if e.get("super_event") or not e.get("start_time") or NOISE.search(name) or PROGRAMME.search(name):
            continue  # päiväkohtaiset alitapahtumat ja opastukset pois, kattotapahtuma jää
        fv = fold(venue)
        if DROP_VENUE.search(fv) and OODI not in fv:
            continue
        start = helsinki_day(e["start_time"])
        end = helsinki_day(e["end_time"]) if e.get("end_time") else start
        if start == end:
            continue
        offers = e.get("offers") or []
        price = "Ilmainen" if any(o.get("is_free") for o in offers) else \
            ((offers[0].get("price") or {}).get("fi") if offers else "") or "–"
        if price.startswith("http"):  # hintakenttään on joskus laitettu lippukauppa
            price = "–"
        url = (e.get("info_url") or {}).get("fi") or "https://tapahtumat.hel.fi/fi/events/" + e["id"]
        out.append(row(name, canon_venue(venue), start, end, price=price, url=url, source="Linked Events"))
    return out


def parse_museot_list(html: str) -> list[dict]:
    out = []
    for nid, card in re.findall(r'<a class="normaali" href="[^"]*nayttely_id=(\d+)"[^>]*>(.*?)</a>', html, re.S):
        m = re.search(r'<h2>(.*?)</h2>.*?<p class="paikka">(.*?)<span class="kunta">(.*?)</span>.*?'
                      r'<p class="ajankohta">(.*?)</p>', card, re.S)
        if not m or text(m.group(3)) != "Helsinki":
            continue
        name, venue = text(m.group(1)), text(m.group(2))
        if name.lower().startswith("verkkonäyttely"):
            continue
        d = re.findall(r"(\d+)\.(\d+)\.(\d{4})", m.group(4))
        if not d:
            continue
        iso = [date(int(y), int(mo), int(dd)).isoformat() for dd, mo, y in d]
        permanent = len(iso) == 1 and "&#8211;" in m.group(4)  # "28.11.2026 – ": ei loppupäivää
        out.append(row(name, venue, iso[0], "" if permanent else iso[-1], permanent=permanent,
                       url=f"{MUSEOT}/nayttelykalenteri/index.php?nayttely_id={nid}", source="museot.fi"))
    return out


def museum_id(detail_html: str) -> str | None:
    m = re.search(r'class="h_info_paikka_pva"><p class="paikka"><a href="/museohaku/index.php\?museo_id=(\d+)"', detail_html)
    return m.group(1) if m else None


def parse_museum_page(html: str) -> tuple[str, str]:
    groups: list[list] = []  # [ensimmäinen päivä, viimeinen päivä, arvo]
    t = re.search(r'<table class="aukioloajat">(.*?)</table>', html, re.S)
    for day, val in re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", t.group(1) if t else "", re.S):
        day = text(day).lower()
        val = re.sub(r":00\b", "", text(val).lower()).replace("-", "–")
        if groups and groups[-1][2] == val:
            groups[-1][1] = day
        else:
            groups.append([day, day, val])
    hours = ", ".join(f"{a if a == b else a + '–' + b} {v}" for a, b, v in groups) or "–"
    price = "–"
    h = re.search(r"P&auml;&auml;symaksut</h2>(.*)", html, re.S)
    for p in re.findall(r"<p>(.*?)</p>", h.group(1) if h else "", re.S):
        if "€" in p:
            price = re.sub(r",\s*Museokortti.*$", "", text(p)) or "–"
            break
    return hours, price


def museot_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cafile=str(CERT))  # museot.fi ei lähetä välivarmennetta
    return ctx


def linkedevents(frm: date, to: date) -> list[dict]:
    url, events = LINKED.format(frm, to), []
    for _ in range(20):
        page = json.loads(fetch(url))
        events += page["data"]
        url = (page.get("meta") or {}).get("next")
        if not url:
            break
    return parse_linkedevents(events)


def museot(frm: date, to: date) -> list[dict]:
    ctx = museot_context()
    # Vain ikkunassa auki olevien museoiden sivut haetaan.
    rows = [r for r in parse_museot_list(fetch(MUSEOT_LIST, ctx)) if overlaps(r, frm, to)]
    info: dict = {}
    for r in rows:
        if r["venue"] not in info:
            try:
                mid = museum_id(fetch(r["url"], ctx))
                info[r["venue"]] = parse_museum_page(fetch(f"{MUSEOT}/museohaku/index.php?museo_id={mid}", ctx)) if mid else ("–", "–")
            except Exception as ex:  # yksi museo ei kaada muita
                print(f"museot: {r['venue']}: {ex}", file=sys.stderr)
                info[r["venue"]] = ("–", "–")
        r["hours"], r["price"] = info[r["venue"]]
    return rows


def pysyvat(frm: date, to: date) -> list[dict]:
    return []


READERS = [museot, linkedevents, pysyvat]  # museot ensin: sen aukioloajat voittavat mergessä


def main(argv=None) -> int:
    return run(READERS, lambda r: True, argv)


if __name__ == "__main__":
    sys.exit(main())
