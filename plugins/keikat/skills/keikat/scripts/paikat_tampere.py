#!/usr/bin/env python3
"""Hakee Tampereen keikkapaikkojen omat ohjelmasivut (Tullikamari, Tavara-asema, Telakka, Vastavirta) tavallisella HTTP-haulla.

Kaikilla neljällä sivulla ohjelma ja hinnat ovat valmiina HTML:ssä, joten selainta ei tarvita.
Tuloste on JSON (oletus) tai taulukko (--table), samoilla kentillä kuin paikat_oulu.py:
date, weekday, artist, venue, price, status, category, time_info, url ja source.
Sivu, joka ei vastaa, raportoidaan stderriin ja ohitetaan.

Huomioita: sivuilla on myös tansseja, päiväkonsertteja, DJ-iltoja, tietovisoja ja messuja,
joita ei ole suodatettu pois (category-kenttä auttaa Tullikamarin ja Tavara-aseman rivien kanssa).

Käyttö:
    python3 -I paikat_tampere.py [--days 30 | --months 1-12] [--only tullikamari,tavara,telakka,vastavirta] [--table]
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
SOLD_OUT = re.compile(r"sold\s*out|loppuunmyyty", re.I)
FREE = re.compile(r"vapaa pääsy|ilmainen", re.I)
CATEGORIES = {
    "konsertti-keikka": "Konsertti/keikka",
    "yokerho": "Yökerho",
    "muu-julkinen-tapahtuma": "Muu julkinen tapahtuma",
}


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


def mark_free(e):
    """Ilmaiselle tapahtumalle hinnaksi "Ilmainen" ja tilaksi "ilmainen"."""
    if e["price"] and FREE.search(e["price"]) and not re.search(r"\d", e["price"]):
        e["price"], e["status"] = "Ilmainen", "ilmainen"
    return e


def ohjelmakortit(page, default_venue, source, today):
    """Tullikamarin ja Tavara-aseman yhteinen WordPress-teema: <article class="event-feed-item ...">."""
    for art in page.split('<article id="post-')[1:]:
        art = art.split("</article>")[0]
        d = re.search(r"<time><span>\w+</span>(\d{1,2})[./](\d{1,2})[./](\d{4})?", art)
        link = re.search(r'<a href="([^"]+)" class="event-link"', art)
        if not (d and link):
            continue
        day, month, year = int(d.group(1)), int(d.group(2)), d.group(3)
        if not year:
            # Tavara-aseman päivä on muotoa 13.11.; vuosi löytyy osoitteen lopusta (…-13-11-2026/).
            y = re.search(r"-(\d{4})/?$", link.group(1))
            year = y.group(1) if y else guess_year(day, month, today)
        title = re.search(r'<h2 class="event-title">(.*?)</h2>', art, re.S)
        artists = re.findall(r'<h2 class="event-artist">(.*?)</h2>', art, re.S)
        first_time = re.search(r"<span>(\d{1,2}:\d{2})</span>", artists[0]) if artists else None
        names = ", ".join(n for n in (text(re.sub(r"<span>.*?</span>", "", a, flags=re.S)) for a in artists) if n)
        title = text(title.group(1)) if title else ""
        if title and title.lower() not in names.lower():
            names = f"{title} {names}" if title.endswith(":") else f"{title}: {names}" if names else title
        if not names:
            continue
        info = re.search(r'<ul class="event-feed-item__info">(.*?)</ul>', art, re.S)
        items = [text(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", info.group(1), re.S)] if info else []
        venue = re.search(r'class="event-venue">(.*?)</li>', art, re.S)
        venue = text(venue.group(1)) if venue and text(venue.group(1)) else default_venue
        doors = next((x for x in items if re.match(r"Ovet \d", x) and x != "Ovet 00:00"), "")
        prices = [re.sub(r"Vapaa pääsy\s*€", "Vapaa pääsy", x) for x in items
                  if "€" in x or SOLD_OUT.search(x) or FREE.search(x)]
        cat = re.search(r"event_category-([\w-]+)", art)
        cat = cat.group(1) if cat else ""
        time_info = ", ".join(x for x in (doors, f"klo {first_time.group(1)}" if first_time else "") if x)
        e = event(dt.date(int(year), month, day), names, venue, " / ".join(prices), link.group(1),
                  category=CATEGORIES.get(cat, cat), time_info=time_info, source=source)
        if re.search(r'class="event-feed-item[^"]*\bsold-out\b', art):
            e["status"] = "loppuunmyyty"
        yield mark_free(e)


def tullikamari(today):
    # Koko ohjelma (Pakkahuone ja Klubi) on yhdellä sivulla ilman sivutusta; suodatus tapahtuu selaimessa.
    yield from ohjelmakortit(fetch("https://tullikamari.fi/ohjelma/"), "Tullikamari", "tullikamari.fi", today)


def tavara(today):
    yield from ohjelmakortit(fetch("https://tavara-asema.fi/ohjelma/"), "Tavara-asema", "tavara-asema.fi", today)


def telakka(today):
    # Ohjelma on yksi vapaamuotoinen tekstisivu: kappaleessa "Pe 13.11." <br> nimi <br> "klo 21.00 Liput 15 €".
    # Vuotta ei kerrota, paitsi omalla rivillään kun vuosi vaihtuu ("2027"). Päiväämätön kappale
    # ("Telakan 2. kerros: …") on edellisen päivän oma tapahtuma.
    page = fetch("https://www.telakka.eu/ohjelma/")
    page = page.split('class="entry-content"', 1)[-1].split("</article>")[0]
    year, last, prev_month = None, None, 0
    for para in re.findall(r"(?s)<p[^>]*>(.*?)</p>", page):
        if re.fullmatch(r"\d{4}", text(para)):
            year, prev_month = int(text(para)), 0
            continue
        lines = [text(x) for x in re.split(r"<br\s*/?>", para)]
        lines = [x for x in lines if x]
        if not lines:
            continue
        d = re.match(r"\w{2} (\d{1,2})\.(\d{1,2})\.$", lines[0])
        venue = "Telakka"
        if d:
            day, month = int(d.group(1)), int(d.group(2))
            if year is None:
                year = guess_year(day, month, today)
            elif month < prev_month:
                year += 1  # kuukausi pieneni ilman vuosiriviä: vuosi vaihtui
            prev_month = month
            last = (day, month)
            lines = lines[1:]
        elif not (last and re.match(r"Telakan \d\. kerros:?$", lines[0])):
            continue
        if lines and re.match(r"Telakan \d\. kerros:?$", lines[0]):
            venue = "Telakka (" + lines[0].rstrip(":").replace("Telakan ", "") + ")"
            lines = lines[1:]
        klo = next((i for i, x in enumerate(lines) if re.match(r"klo\s*\d", x)), None)
        if klo is None or klo == 0:
            continue
        name = " ".join(lines[:klo]).rstrip(":")
        k = re.match(r"klo\s*([\d.:]+(?:\s*–\s*[\d.:]+)?)\s*(.*)", lines[klo])
        price = re.sub(r"^Liput\s+", "", k.group(2)).strip()
        if price.upper() == "LOPPUUNMYYTY":
            price = "Loppuunmyyty"
        link = re.search(r'<a href="([^"]+)"', para)
        e = event(dt.date(year, last[1], last[0]), name, venue, price,
                  link.group(1) if link else "https://www.telakka.eu/ohjelma/",
                  time_info=f"klo {k.group(1)}", source="telakka.eu")
        yield mark_free(e)


def vastavirta(today):
    # Etusivun "vv-custom-events"-lohkot: otsikko "13.11.2026 21:00 - Nimi", sitten "Tapahtumapaikka: …"
    # ja "Liput: 10 €" tai "Ilmainen sisäänpääsy". Tapahtumakohtaista sivua ei ole, joten linkkinä on
    # Facebook-tapahtuma tai sivu itse; ennakkolippujen osoite on kentässä tickets_url.
    page = fetch("https://vastavirta.net/")
    for block in page.split('<div class="vv-custom-events">')[1:]:
        block = block.split("</div>")[0]
        h = re.search(r'vv-events-heading">\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}:\d{2})\s*-\s*(.*?)</h3>', block, re.S)
        if not h:
            continue
        place = re.search(r"<p>Tapahtumapaikka:\s*(.*?)</p>", block, re.S)
        price = re.search(r"</p>\s*<p>((?:Liput|Ilmainen)[^<]*)</p>", block)
        price = text(price.group(1)) if price else ""
        price = re.sub(r"^Liput\s*:\s*", "", price)
        if re.fullmatch(r"€?", price):  # "Liput: €" = hintaa ei ole vielä ilmoitettu
            price = ""
        fb = re.search(r'href="(https://(?:www\.)?facebook\.com/[^"]+)"', block)
        tickets = re.search(r'href="(https://cluby\.com/[^"]+)"', block)
        e = event(dt.date(int(h.group(3)), int(h.group(2)), int(h.group(1))), text(h.group(5)),
                  text(place.group(1)) if place else "Vastavirta", price,
                  fb.group(1) if fb else "https://vastavirta.net/",
                  time_info=f"klo {h.group(4)}", source="vastavirta.net")
        e["tickets_url"] = tickets.group(1) if tickets else ""
        yield mark_free(e)


SOURCES = {"tullikamari": tullikamari, "tavara": tavara, "telakka": telakka, "vastavirta": vastavirta}


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
    out.sort(key=lambda x: (x["date"], x["venue"], x["artist"]))

    if a.table:
        for r in out:
            cat = f' [{r["category"]}]' if r["category"] else ""
            # Hintateksteissä on itsessään pystyviivoja, jotka sotkisivat sarakkeet.
            price = (r["price"] or "–").replace(" | ", " / ")
            print(f'{r["date"]} {r["weekday"]:2} | {r["artist"].replace(" | ", " / ")}{cat} | {r["venue"]} | {price} | '
                  f'{r["status"]} | {r["time_info"]} | {r["url"]}')
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
