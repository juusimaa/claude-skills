#!/usr/bin/env python3
"""Hakee Jyväskylän keikkapaikkojen omat ohjelmasivut (Tanssisali Lutakko, Musta Kynnys) tavallisella HTTP-haulla.

Molemmilla sivulla ohjelma ja hinnat ovat valmiina HTML:ssä, joten selainta ei tarvita.
Tuloste on JSON (oletus) tai taulukko (--table), samoilla kentillä kuin tiketti.py
sekä lisäksi "price" ja "category". Sivu, joka ei vastaa, raportoidaan stderriin ja ohitetaan.

Käyttö:
    python3 -I paikat_jyvaskyla.py [--days 30 | --months 1-12] [--only lutakko,mustakynnys] [--table]
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
SOLD_OUT = re.compile(r"sold\s*out|loppuunmyyty!?", re.I)


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


def lutakko(today):
    # Jelmun etusivu listaa kaikki tulevat keikat WooCommerce-tuotteina (<li class="product ...">).
    # Päivässä ei ole vuotta. Paikka voi olla muukin kuin Lutakko (esim. "Musta kynnys").
    page = fetch("https://www.jelmu.net/")
    for item in page.split('<li class="product ')[1:]:
        item = item.split("</li>")[0]
        d = re.search(r'<span class="date">\s*(\d{1,2})\.(\d{1,2})\.', item)
        a = re.search(r'<a href="([^"]+)" class="woocommerce-LoopProduct-link', item)
        names = re.search(r'<h2 class="woocommerce-loop-product__title">(.*?)</h2>(.*?)<span class="location">', item, re.S)
        if not (d and a and names):
            continue
        # Tavallisesti jokainen esiintyjä on omassa <span>-elementissään h2:ssa, alkamisaika joskus nimen
        # perässä: "Semmarit (21:00)". Festivaaleilla h2 on pelkkä tapahtuman nimi ja esiintyjälista on h3:ssa.
        artists, start = [], ""
        spans = re.findall(r"<span>(.*?)</span>", names.group(1), re.S)
        extra = re.findall(r"<span>(.*?)</span>", names.group(2), re.S)
        if not spans:
            spans = extra or [text(names.group(1))]
        for s in spans:
            s = text(s)
            t = re.search(r"\s*\((\d{1,2}[:.]\d{2})\)$", s)
            if t:
                start, s = min(start or t.group(1), t.group(1)), s[:t.start()]  # useita aikoja: aikaisin
            if s:
                artists.append(s)
        place = re.search(r'class="location">(.*?)</span>', item, re.S)
        doors = re.search(r'class="doors">(.*?)</span>', item, re.S)
        age = re.search(r'class="age">(.*?)</span>', item, re.S)
        price = re.search(r'<span class="price">(.*?)</div>', item, re.S)
        # Hinta: näkyvä osa ilman ruudunlukijan toistoa ("Hintaluokka: ...").
        ptxt = re.sub(r'<span class="screen-reader-text">.*?</span>', "", price.group(1) if price else "", flags=re.S)
        ptxt = text(ptxt)
        month, day = int(d.group(2)), int(d.group(1))
        times = [x for x in (text(doors.group(1)) if doors else "", f"alkaa {start}" if start else "",
                             text(age.group(1)) if age else "") if x]
        e = event(dt.date(guess_year(day, month, today), month, day), ", ".join(artists),
                  text(place.group(1)) if place and text(place.group(1)) else "Lutakko", ptxt,
                  a.group(1), time_info=", ".join(times),
                  source="jelmu.net")
        if SOLD_OUT.search(text(item)):
            e["status"] = "loppuunmyyty"
        elif re.search(r"ilmainen|vapaa pääsy", ptxt, re.I) or re.fullmatch(r"0(?:[,.]0+)?\s*€", ptxt):
            e["price"], e["status"] = "Ilmainen", "ilmainen"
        yield e


def mustakynnys(today):
    # Ohjelma on peräkkäisinä <div id="keikka">-lohkoina: päivä, nimi + showtime, ennakkohinta ja ovihinta.
    page = fetch("https://mustakynnys.com/")
    for block in page.split('<div id="keikka">')[1:]:
        d = re.search(r'<div id="pvm">[^<]*?(\d{1,2})\.(\d{1,2})\.</div>', block)
        name = re.search(r"<strong>(.*?)</strong>", block, re.S)
        if not (d and name):
            continue
        # Linkin lainausmerkit puuttuvat joskus (href=https://...), joten ne ovat valinnaisia.
        link = re.search(r'<a href="?(https?://[^"\s>]+)', block)
        adv = re.search(r"<a [^>]*>(.*?)</a>", block, re.S)
        door = re.search(r'<div id="lipunhinta">(.*?)</div>', block, re.S)
        show = re.search(r"</strong>\s*Showtime:\s*([^<]+)", block)
        adv_t = re.sub(r"\s*www\.jelmu\.net$", "", text(adv.group(1))) if adv else ""
        door_t = text(door.group(1)) if door else ""
        # Tuntematon ovihinta on "Liput ovelta: ?€", joka jätetään pois.
        parts = [adv_t] if adv_t else []
        if door_t and "?" not in door_t:
            parts.append(door_t)
        price = ", ".join(parts)
        month, day = int(d.group(2)), int(d.group(1))
        show_t = show.group(1).strip() if show else ""
        e = event(dt.date(guess_year(day, month, today), month, day), text(name.group(1)), "Musta Kynnys",
                  price, link.group(1) if link else "https://mustakynnys.com/",
                  time_info=f"showtime {show_t}" if show_t else "", source="mustakynnys.com")
        if SOLD_OUT.search(text(block)):
            e["status"] = "loppuunmyyty"
        elif re.search(r"ilmainen|vapaa pääsy", price, re.I):
            e["price"], e["status"] = "Ilmainen", "ilmainen"
        yield e


SOURCES = {"lutakko": lutakko, "mustakynnys": mustakynnys}


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
    # Jelmu listaa myös Musta Kynnyksen keikat samalla linkillä; pidä Jelmun rivi (ovet ja ikäraja mukana).
    jelmu_urls = {e["url"] for e in out if e["source"] == "jelmu.net" and e["url"]}
    out = [e for e in out if e["source"] == "jelmu.net" or e["url"] not in jelmu_urls]
    for e in out:
        if e["venue"].lower() == "musta kynnys":
            e["venue"] = "Musta Kynnys"
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
