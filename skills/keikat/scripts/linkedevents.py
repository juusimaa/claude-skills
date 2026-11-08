#!/usr/bin/env python3
"""Hakee Helsingin, Espoon tai Vantaan musiikkitapahtumat Helsingin avoimesta Linked Events -rajapinnasta.

Rajapinta (https://api.hel.fi/linkedevents/v1/) on avoin eikä tarvitse avainta. Se kattaa paljon
kirjastojen, kirkkojen ja yhteisötalojen ilmaiskonsertteja, mutta kaupallisia klubeja vähän, ja hinta
puuttuu usein. Tuloste on JSON (oletus) tai taulukko (--table), samoilla kentillä kuin paikat_oulu.py
sekä lisäksi "end" (loppupäivä, jos tapahtuma kestää yli yhden päivän).

Käyttö:
    python3 -I linkedevents.py --city Helsinki|Espoo|Vantaa [--days 60 | --months 1-12] [--table]
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

API = "https://api.hel.fi/linkedevents/v1/event/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
TZ = ZoneInfo("Europe/Helsinki")
WEEKDAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
DIVISIONS = {"Helsinki": "helsinki", "Espoo": "espoo", "Vantaa": "vantaa"}
# Musiikkiavainsanat (OR). Vertailu Helsingin marraskuulle 2026 (136 / 28 / 5 tapahtumaa):
#   yso:p11185 konsertit       kirjastojen, kirkkojen ja orkesterien konsertit, lähes pelkkää musiikkia
#   yso:p24765 musiikkikeikat  klubi- ja baarikeikat (jazz-illat, PK-Live), täydentää konsertteja
#   yso:p27962 elävä musiikki  jamit ja kirjastokeikat, vain muutama mutta puhdasta musiikkia
# Jätetty pois: yso:p1808 "musiikki" (923 tapahtumaa, enimmäkseen taaperotuokioita, yhteislauluja ja
# kuorojen harjoituksia), yso:p20421 musiikkiklubit ja helmet:11686 (0 osumaa).
KEYWORDS = "yso:p11185,yso:p24765,yso:p27962"
# Yleiset avainsanat, joita ei käytetä kategoriana, jos tarkempi (esim. jazz) löytyy.
GENERIC = {"yso:p11185", "yso:p24765", "yso:p27962", "yso:p1808"}
MUSIC_NAME = re.compile(r"musiik|jazz|rock|blues|soul|barokki|folk|metalli|kuoro|laulu|pop|klassi|reggae|punk|oopp|tango|iskelm", re.I)
MAX_PAGES = 20
# Näyttelyt ja muut pitkät käynnissä olevat tapahtumat pudotetaan pois ja alkaneet ennen tätä päivää.
MAX_ONGOING_DAYS = 14


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_events(division: str, start: dt.date, end: dt.date) -> list:
    """Hakee kaikki sivut (enintään MAX_PAGES) meta.next-linkkiä seuraten."""
    query = urllib.parse.urlencode({
        "start": start.isoformat(), "end": end.isoformat(), "keyword": KEYWORDS, "division": division,
        "sort": "start_time", "include": "location,keywords", "page_size": 100,
    }, safe=":,")
    url, events = f"{API}?{query}", []
    for _ in range(MAX_PAGES):
        data = fetch_json(url)
        events += data.get("data", [])
        url = (data.get("meta") or {}).get("next")
        if not url:
            break
    return events


def parse_time(s):
    """Rajapinnan aika (UTC tai pelkkä päivä) -> (paikallinen datetime tai date, onko kellonaikaa)."""
    if not s:
        return None, False
    if len(s) <= 10:
        return dt.date.fromisoformat(s), False
    d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d.astimezone(TZ), True


def pick(names, order=("fi", "en", "sv")) -> str:
    """Monikielisestä kentästä ensimmäinen löytyvä kieli: fi -> en -> sv."""
    if isinstance(names, dict):
        for lang in order:
            if names.get(lang):
                return " ".join(str(names[lang]).split())
    return ""


def first_url(*candidates) -> str:
    for c in candidates:
        v = pick(c) if isinstance(c, dict) else ""
        if v.startswith("https://"):
            return v
    return ""


def drop_duplicates(events: list) -> list:
    """Sarjojen päällekkäisyys: jos sarjatapahtuma (super_event_type recurring/umbrella) on tuloksessa
    ja jokin tuloksen tapahtuma viittaa siihen super_eventinä, sarja jätetään pois ja alatapahtumat
    (varsinaiset esitykset) pidetään. Sarja, jonka alatapahtumia ei ole aikavälillä, pidetään."""
    parents = {(e.get("super_event") or {}).get("@id") for e in events}
    parents.discard(None)
    return [e for e in events if not (e.get("super_event_type") in ("recurring", "umbrella") and e.get("@id") in parents)]


def convert(e: dict, today: dt.date):
    """Linked Events -tapahtuma -> tulosteen rivi; None, jos tapahtuma ei kuulu mukaan."""
    start, has_time = parse_time(e.get("start_time"))
    if start is None:
        return None
    start_day = start.date() if has_time else start
    end, end_has_time = parse_time(e.get("end_time"))
    end_day = ""
    if end is not None:
        last = end.date() if end_has_time else end
        # Aikaleima keskiyöllä tarkoittaa edellisen päivän loppua.
        if end_has_time and end.timetz().replace(tzinfo=None) == dt.time(0, 0):
            last -= dt.timedelta(days=1)
        if last > start_day:
            end_day = last
    # Alkanut jo ennen tätä päivää ja kestää yli 14 päivää: näyttely tms.
    if start_day < today and end_day and (end_day - start_day).days > MAX_ONGOING_DAYS:
        return None
    if (end_day or start_day) < today:
        return None

    offers = e.get("offers") or []
    is_free = any(o.get("is_free") for o in offers)
    price = "Ilmainen" if is_free else (pick(offers[0].get("price")) if offers else "")
    if e.get("event_status") == "EventCancelled":
        status = "peruttu"
    else:
        status = "ilmainen" if is_free else ""

    keywords = e.get("keywords") or []
    # Kategoriaksi ensimmäinen musiikkia tarkoittava avainsana (jazz, kamarimusiikki, ...); muuten
    # yleinen musiikkiavainsana. Avainsanoissa on myös epämusiikillista (osallistuminen, isänpäivä).
    ids = [k.get("@id", "").rstrip("/").split("/")[-1] for k in keywords]
    names = [pick(k.get("name")) for k, i in zip(keywords, ids) if i not in GENERIC]
    generic = [pick(k.get("name")) for k, i in zip(keywords, ids) if i in GENERIC]
    category = next((n for n in names if n and MUSIC_NAME.search(n)), next((n for n in generic if n), ""))

    url = first_url(e.get("info_url"), (offers[0].get("info_url") if offers else None))
    if not url and e.get("id"):
        url = "https://tapahtumat.hel.fi/fi/events/" + e["id"]

    venue = pick((e.get("location") or {}).get("name"), ("fi",))
    return {
        "date": start_day.isoformat(),
        "weekday": WEEKDAYS[start_day.weekday()],
        "artist": pick(e.get("name")),
        "venue": venue,
        "price": price,
        "status": status,
        "category": category,
        "time_info": f"klo {start.hour}.{start.minute:02d}" if has_time else "",
        "url": url,
        "source": "linkedevents.hel.fi",
        "end": end_day.isoformat() if end_day else "",
    }


def add_months(d: dt.date, n: int) -> dt.date:
    """Sama päivä n kuukautta myöhemmin; lyhyemmässä kuussa kuun viimeinen päivä."""
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return min(d.replace(year=y, month=m, day=1) + dt.timedelta(days=d.day - 1), nxt - dt.timedelta(days=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True, choices=list(DIVISIONS))
    span = ap.add_mutually_exclusive_group()
    span.add_argument("--days", type=int, default=60, help="kuinka monta päivää eteenpäin")
    span.add_argument("--months", type=int, choices=range(1, 13), metavar="1-12",
                      help="kuinka monta kalenterikuukautta eteenpäin (ohittaa --days)")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()

    today = dt.date.today()
    limit = add_months(today, a.months) if a.months else today + dt.timedelta(days=a.days)
    out = []
    try:
        raw = drop_duplicates(fetch_events(DIVISIONS[a.city], today, limit))
        for e in raw:
            row = convert(e, today)
            if row and row["date"] <= limit.isoformat():
                out.append(row)
    except Exception as exc:  # verkkovirhe ei saa kaataa kutsujaa
        print(f"linkedevents: haku epäonnistui: {exc}", file=sys.stderr)
        out = []
    if not out:
        print(f"linkedevents: ei tapahtumia ({a.city})", file=sys.stderr)
    out.sort(key=lambda x: (x["date"], x["time_info"], x["artist"]))

    if a.table:
        for r in out:
            cat = f' [{r["category"]}]' if r["category"] else ""
            print(f'{r["date"]} {r["weekday"]:2} | {r["artist"].replace(" | ", " / ")}{cat} | {r["venue"]} | '
                  f'{r["price"] or "–"} | {r["status"]} | {r["time_info"]} | {r["url"]}')
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
