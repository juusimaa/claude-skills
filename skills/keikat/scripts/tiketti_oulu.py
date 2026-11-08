#!/usr/bin/env python3
"""Hakee Tiketin etusivun upotetusta tapahtumadatasta tietyn kaupungin (oletus Oulu) tapahtumat.

Tuloste on JSON (oletus) tai taulukko (--table). Data sisältää päivän, paikan, loppuunmyynti-
tilan ja vapaiden lippujen määrän, mutta EI hintoja: hinnat haetaan tapahtumasivulta erikseen.

Käyttö:
    python3 -I tiketti_oulu.py [--city Oulu] [--days 60] [--table]
"""
import argparse
import datetime as dt
import http.cookiejar
import json
import re
import sys
import urllib.request

BASE = "https://www.tiketti.fi"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(url: str) -> str:
    # Tiketin jonotuspalvelu (queue-it) ohjaa pyynnön edestakaisin evästeen kanssa; cookiejar hoitaa sen.
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA), ("Accept-Language", "fi")]
    with opener.open(url, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def objects_for_city(html: str, city: str):
    """Poimii kaikki JSON-oliot, joissa location_city on annettu kaupunki."""
    needle = f'"location_city":"{city}"'
    seen = set()
    pos = 0
    while True:
        i = html.find(needle, pos)
        if i < 0:
            return
        pos = i + len(needle)
        depth, s = 0, i
        while s > 0:
            c = html[s]
            if c == "}":
                depth += 1
            elif c == "{":
                if depth == 0:
                    break
                depth -= 1
            s -= 1
        depth, e = 0, i
        while e < len(html):
            c = html[e]
            if c == "{":
                depth += 1
            elif c == "}":
                if depth == 0:
                    break
                depth -= 1
            e += 1
        try:
            obj = json.loads(html[s : e + 1])
        except ValueError:
            continue
        if obj.get("eventID") and obj["eventID"] not in seen:
            seen.add(obj["eventID"])
            yield obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default="Oulu")
    ap.add_argument("--days", type=int, default=60, help="kuinka monta päivää eteenpäin")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()

    html = fetch(BASE + "/")
    slugs = {}
    for m in re.finditer(r'href="(/[a-z0-9-]+-lippuja/(\d+))', html):
        slugs[m.group(2)] = BASE + m.group(1)

    today = dt.date.today()
    limit = today + dt.timedelta(days=a.days)
    out = []
    for o in objects_for_city(html, a.city):
        try:
            d = dt.date.fromisoformat(o["start_date"])
        except (KeyError, ValueError):
            continue
        if d < today or d > limit:
            continue
        total, free = int(o.get("tickets_total") or 0), int(o.get("tickets_free") or 0)
        if o.get("cancelled") == "1":
            status = "peruttu"
        elif o.get("sold_out") == "1" or (total and free == 0):
            status = "loppuunmyyty"
        elif total and free / total < 0.15:
            status = "vähissä"
        else:
            status = "saatavilla"
        out.append(
            {
                "date": o["start_date"],
                "weekday": o.get("start_weekday", ""),
                "artist": o.get("name", ""),
                "venue": o.get("location_name", ""),
                "status": status,
                "tickets_free": free if total else None,
                "tickets_total": total or None,
                "time_info": o.get("timeinfo", ""),
                "age": o.get("ageinfo", ""),
                "url": slugs.get(o["eventID"], ""),
                "source": "tiketti.fi",
            }
        )
    out.sort(key=lambda x: (x["date"], x["artist"]))

    if a.table:
        for r in out:
            print(f'{r["date"]} {r["weekday"]:2} | {r["artist"]} | {r["venue"]} | {r["status"]} | {r["time_info"]} | {r["url"]}')
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
