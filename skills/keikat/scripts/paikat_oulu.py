#!/usr/bin/env python3
"""Hakee Oulun keikkapaikkojen omat ohjelmasivut (Tarkastamo, Tullisali, Tuba) tavallisella HTTP-haulla.

Kaikilla kolmella sivulla ohjelma ja hinnat ovat valmiina HTML:ssä, joten selainta ei tarvita.
Tuloste on JSON (oletus) tai taulukko (--table), samoilla kentillä kuin tiketti_oulu.py
sekä lisäksi "price" ja "category". Sivu, joka ei vastaa, raportoidaan stderriin ja ohitetaan.

Käyttö:
    python3 -I paikat_oulu.py [--days 30 | --months 1-12] [--only tarkastamo,tullisali,tuba] [--table]
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


def sinfonia(today):
    # Oulun musiikkikeskuksen oma kalenteri on JavaScript-upotus, mutta Oulu Sinfonian
    # konserttilista on tavallista HTML:ää. Hinnat ovat vain konserttien omilla sivuilla.
    page = fetch("https://oulusinfonia.fi/kaikki-konsertit/")
    for flyer in page.split('<div class="col-6 flyer-frame')[1:]:
        cat = re.search(r'<div class="kategoria">(.*?)</div>', flyer, re.S)
        cat = text(cat.group(1)) if cat else ""
        single = re.search(r'class="paivamaara">.*?<span>(\d{1,2})\.(\d{1,2})\.(\d{4})</span>', flyer, re.S)
        span = re.search(r'(\d{1,2})\.(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.(\d{4})', text(flyer))
        if single:
            start, end = dt.date(int(single.group(3)), int(single.group(2)), int(single.group(1))), None
        elif span:
            y = int(span.group(5))
            end = dt.date(y, int(span.group(4)), int(span.group(3)))
            sm = int(span.group(2))
            start = dt.date(y - 1 if sm > end.month else y, sm, int(span.group(1)))
        else:
            continue
        title = re.search(r"<h3>(.*?)</h3>", flyer, re.S)
        if not title:
            continue
        who = re.search(r"<!-- Esiintyjät -->\s*<p>(.*?)</p>", flyer, re.S)
        place = re.search(r'class="konserttipaikka">(.*?)</p>', flyer, re.S)
        tm = re.search(r'class="kellonaika">.*?([\d.]+)\s*</p>', flyer, re.S)
        shows = re.search(r"(\d+) näytöstä", text(flyer))
        link = re.search(r'class="liput-link[^"]*" href="([^"]+)"', flyer)
        artist = text(title.group(1)) + (f" ({text(who.group(1))})" if who and text(who.group(1)) else "")
        e = event(start, artist, text(place.group(1)) if place else "", "", link.group(1) if link else "",
                  category=cat, time_info=f"klo {tm.group(1)}" if tm else (f"{shows.group(1)} näytöstä" if shows else ""),
                  source="oulusinfonia.fi")
        e["end"] = end.isoformat() if end else ""
        if cat.lower() == "vapaa pääsy":
            e["price"], e["status"] = "Ilmainen", "ilmainen"
        yield e


def sinfonia_prices(events, limit):
    """Hakee hinnan konserttisivulta vain aikavälin konserteille (ensimmäinen €-rivi)."""
    for e in events:
        if e["source"] != "oulusinfonia.fi" or e["price"] or not e["url"] or e["date"] > limit.isoformat():
            continue
        try:
            body = re.sub(r"(?s)<(script|style).*?</\1>", "", fetch(e["url"]))
        except Exception:
            continue
        lines = [text(l) for l in re.split(r"<(?:/p|br\s*/?|/h\d|/li)>", body)]
        price = next((l for l in lines if "€" in l and len(l) < 200 and not l.lower().startswith("erikseen")), "")
        e["price"] = re.sub(r"^Liput\s+", "", price)
        if re.search(r"vapaa pääsy|ilmainen sisäänpääsy", e["price"], re.I):
            e["status"] = "ilmainen"


SOURCES = {"tarkastamo": tarkastamo, "tullisali": tullisali, "tuba": tuba, "sinfonia": sinfonia}


def add_months(d: dt.date, n: int) -> dt.date:
    """Sama päivä n kuukautta myöhemmin; lyhyemmässä kuussa kuun viimeinen päivä."""
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return min(d.replace(year=y, month=m, day=1) + dt.timedelta(days=d.day - 1), nxt - dt.timedelta(days=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    span = ap.add_mutually_exclusive_group()
    span.add_argument("--days", type=int, default=60, help="kuinka monta päivää eteenpäin")
    span.add_argument("--months", type=int, choices=range(1, 13), metavar="1-12",
                      help="kuinka monta kalenterikuukautta eteenpäin (ohittaa --days)")
    ap.add_argument("--only", default=",".join(SOURCES), help="pilkuin eroteltu lista lähteistä")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()

    today = dt.date.today()
    limit = add_months(today, a.months) if a.months else today + dt.timedelta(days=a.days)
    out = []
    for name in a.only.split(","):
        try:
            events = list(SOURCES[name.strip()](today))
        except Exception as exc:  # yksi rikkinäinen sivu ei saa kaataa muita
            print(f"{name}: haku epäonnistui: {exc}", file=sys.stderr)
            continue
        if not events:
            print(f"{name}: ei tapahtumia, sivun rakenne on ehkä muuttunut", file=sys.stderr)
        # Monipäiväinen tapahtuma kuuluu mukaan, jos se on vielä käynnissä.
        out += [e for e in events if today.isoformat() <= (e.get("end") or e["date"]) and e["date"] <= limit.isoformat()]
    sinfonia_prices(out, limit)
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
