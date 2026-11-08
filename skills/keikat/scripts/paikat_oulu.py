#!/usr/bin/env python3
"""Hakee Oulun keikkapaikkojen omat ohjelmasivut (Tarkastamo, Tullisali, Tuba) tavallisella HTTP-haulla.

Kaikilla kolmella sivulla ohjelma ja hinnat ovat valmiina HTML:ssä, joten selainta ei tarvita.
Tuloste on JSON (oletus) tai taulukko (--table), samoilla kentillä kuin tiketti_oulu.py
sekä lisäksi "price" ja "category". Sivu, joka ei vastaa, raportoidaan stderriin ja ohitetaan.

Käyttö:
    python3 -I paikat_oulu.py [--days 30] [--only tarkastamo,tullisali,tuba] [--table]
"""
import argparse
import datetime as dt
import html as htmllib
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
WEEKDAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
MONTHS = {
    "TAMMIKUU": 1, "HELMIKUU": 2, "MAALISKUU": 3, "HUHTIKUU": 4, "TOUKOKUU": 5, "KESÄKUU": 6,
    "HEINÄKUU": 7, "ELOKUU": 8, "SYYSKUU": 9, "LOKAKUU": 10, "MARRASKUU": 11, "JOULUKUU": 12,
}
SOLD_OUT = re.compile(r"sold\s*out|loppuunmyyty", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def text(fragment: str) -> str:
    """HTML-pätkä siistiksi tekstiksi (myös tavutusmerkit pois)."""
    s = re.sub(r"<br\s*/?>", " ", fragment)
    s = htmllib.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xad", "")
    return re.sub(r"\s+", " ", s).strip(" ,")


def guess_year(day: int, month: int, today: dt.date) -> int:
    # Sivu ei kerro vuotta: yli kaksi kuukautta mennyt päivä tarkoittaa ensi vuotta.
    d = dt.date(today.year, month, day)
    return today.year + 1 if (today - d).days > 60 else today.year


def event(date, artist, venue, price, url, category="", time_info="", source=""):
    return {
        "date": date.isoformat(),
        "weekday": WEEKDAYS[date.weekday()],
        "artist": artist,
        "venue": venue,
        "price": price,
        "status": "loppuunmyyty" if SOLD_OUT.search(price or "") else "saatavilla",
        "category": category,
        "time_info": time_info,
        "url": url,
        "source": source,
    }


def tarkastamo(today):
    page = fetch("https://tarkastamo-oulu.fi/tapahtumat/")
    i = page.find("events-list__list")
    page = page[i:] if i >= 0 else page
    year, month = today.year, today.month
    # Kuukausiotsikot ("MARRASKUU 2026") ja tapahtumarivit tulevat sivulla järjestyksessä.
    token = re.compile(
        r'events-list__month-header">\s*([A-ZÄÖ]+)\s+(\d{4})'
        r'|<div class="events-list__row">(.*?)<span class="events-list__row-action">',
        re.S,
    )
    for m in token.finditer(page):
        if m.group(1):
            month, year = MONTHS.get(m.group(1), month), int(m.group(2))
            continue
        row = m.group(3)
        d = re.search(r'row-date">\s*(\d{1,2})\.(\d{1,2})\.', row)
        a = re.search(r'row-title">\s*<a href="([^"]+)">(.*?)</a>', row, re.S)
        p = re.search(r'row-prices">(.*?)</span>', row, re.S)
        if not (d and a):
            continue
        yield event(dt.date(year, int(d.group(2)), int(d.group(1))), text(a.group(2)), "Tarkastamo",
                    text(p.group(1)) if p else "", a.group(1), source="tarkastamo-oulu.fi")


def tullisali(today):
    page = fetch("https://www.tullisali.fi/tapahtumat/")
    for item in page.split('<div class="event-list-item">')[1:]:
        d = re.search(r"<h3>\w+ (\d{1,2})\.(\d{1,2})\.<span class=\"year\"><span>(\d{4})", item)
        a = re.search(r'<h3><a href="([^"]+)">(.*?)</a></h3>', item, re.S)
        if not (d and a):
            continue
        cat = re.search(r'<ul class="event-category">(.*?)</ul>', item, re.S)
        price = re.search(r'<span class="price">(.*?)</span>', item, re.S)
        doors = re.search(r'Ovet</span>(klo [\d:.]+)', item)
        tickets = re.search(r'href="([^"]+)"[^>]*class="btn tickets"', item)
        e = event(dt.date(int(d.group(3)), int(d.group(2)), int(d.group(1))), text(a.group(2)), "Tullisali",
                  text(price.group(1)) if price else "", a.group(1),
                  category=text(cat.group(1)) if cat else "",
                  time_info=f"Ovet {doors.group(1)}" if doors else "", source="tullisali.fi")
        e["tickets_url"] = tickets.group(1) if tickets else ""
        e["status"] = "loppuunmyyty" if SOLD_OUT.search(text(item)) else e["status"]
        yield e


def tuba(today):
    page = fetch("https://www.tuba.fi/tapahtumat")
    # Ohjelma on tekstikappaleina: <strong>Lauantaina 14.11.</strong> klo 20.00 <strong>Artisti,</strong> <a>…</a><br>Hinta
    para = re.compile(
        r"<p[^>]*>\s*<strong>\s*\w+\s+(\d{1,2})\.(\d{1,2})\.?\s*</strong>(.*?)</p>", re.S)
    for m in para.finditer(page):
        rest = m.group(3)
        name = re.search(r"<strong>(.*?)</strong>", rest, re.S)
        if not name:
            continue
        link = re.search(r'<a href="([^"]+)"', rest)
        url = link.group(1) if link else ""
        if url.startswith("/"):
            url = "https://www.tuba.fi" + url
        tm = re.search(r"klo\s*([\d.:–-]+)", text(rest))
        after = rest.split("<br", 1)[1] if "<br" in rest else ""
        price = text(re.sub(r"^[^>]*>", "", after))
        yield event(dt.date(guess_year(int(m.group(1)), int(m.group(2)), today), int(m.group(2)), int(m.group(1))),
                    text(name.group(1)), "Tuba", price, url,
                    time_info=f"klo {tm.group(1)}" if tm else "", source="tuba.fi")


SOURCES = {"tarkastamo": tarkastamo, "tullisali": tullisali, "tuba": tuba}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60, help="kuinka monta päivää eteenpäin")
    ap.add_argument("--only", default=",".join(SOURCES), help="pilkuin eroteltu lista lähteistä")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()

    today = dt.date.today()
    limit = today + dt.timedelta(days=a.days)
    out = []
    for name in a.only.split(","):
        try:
            events = list(SOURCES[name.strip()](today))
        except Exception as exc:  # yksi rikkinäinen sivu ei saa kaataa muita
            print(f"{name}: haku epäonnistui: {exc}", file=sys.stderr)
            continue
        if not events:
            print(f"{name}: ei tapahtumia, sivun rakenne on ehkä muuttunut", file=sys.stderr)
        out += [e for e in events if today.isoformat() <= e["date"] <= limit.isoformat()]
    out.sort(key=lambda x: (x["date"], x["venue"], x["artist"]))

    if a.table:
        for r in out:
            cat = f' [{r["category"]}]' if r["category"] else ""
            # Hintateksteissä on itsessään pystyviivoja ("79,90€ | VIP 99,90€"), jotka sotkisivat sarakkeet.
            price = (r["price"] or "–").replace(" | ", " / ")
            print(f'{r["date"]} {r["weekday"]:2} | {r["artist"].replace(" | ", " / ")}{cat} | {r["venue"]} | {price} | '
                  f'{r["status"]} | {r["time_info"]} | {r["url"]}')
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
