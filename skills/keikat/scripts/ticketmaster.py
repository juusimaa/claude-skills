#!/usr/bin/env python3
"""Hakee Ticketmaster.fi:n (sama lipunmyynti kuin Lippu.fi) kaupunkisivulta yhden kaupungin tapahtumat.

Jokaisella tuetulla kaupungilla on sivu https://www.ticketmaster.fi/discover/<slug>. Sivun HTML:ssä on
schema.org-Event-oliot (ld+json) sekä Next.js:n __NEXT_DATA__, josta löytyy tapahtuman pääkategoria
(musiikki, urheilu, taide ja teatteri, muut) ja lipputilanne. Sivutus on ?page=N (alkaa nollasta).
Datassa EI ole hintoja, joten "price" on tyhjä, ellei ld+json sattuisi kertomaan hintaa.
Kaupungille, jolla ei ole discover-sivua (esim. Vantaa), ei saada tapahtumia: asiasta kerrotaan stderrissä.

Ei-musiikkitapahtumat (urheilu, messut, työpajat, pysäköinti jne.) suodatetaan pois, ellei anneta --all.
Tuloste on JSON (oletus) tai taulukko (--table).

Käyttö:
    python3 -I ticketmaster.py --city Tampere [--days 60 | --months 1-12] [--table] [--all]
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request

BASE = "https://www.ticketmaster.fi"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
WEEKDAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
MAX_PAGES = 15
# Kaupunkisivun osoite. Vain nämä yhdeksän kaupunkia ovat ticketmaster.fi:n discover-sivuina
# (tarkistettu sivulta /discover/cities); muille discover/<slug> antaa 404.
SLUGS = {
    "Helsinki": "helsinki", "Espoo": "espoo", "Tampere": "tampere", "Turku": "turku", "Oulu": "oulu",
    "Kuopio": "kuopio", "Lahti": "lahti", "Pori": "pori", "Seinäjoki": "seinajoki",
}
CITIES = ["Helsinki", "Espoo", "Vantaa", "Tampere", "Turku", "Oulu", "Jyväskylä", "Kuopio", "Lahti", "Pori",
          "Kouvola", "Joensuu", "Lappeenranta", "Hämeenlinna", "Vaasa", "Seinäjoki", "Rovaniemi"]

# Ticketmasterin vakiomuotoiset pääkategoriat (majorCategory.id).
CATEGORIES = {
    "KZFzniwnSyZfZ7v7nJ": "musiikki",
    "KZFzniwnSyZfZ7v7nE": "urheilu",
    "KZFzniwnSyZfZ7v7na": "taide ja teatteri",
    "KZFzniwnSyZfZ7v7n1": "muut",
    "KZFzniwnSyZfZ7v7nn": "elokuva",
}
# Suodatus: urheilu ja elokuva pudotetaan datan oman kategorian perusteella. Musiikki jää aina.
# Kategoriat "taide ja teatteri" ja "muut" ovat sekalaisia (mukana on konsertteja, esim. kuoro- ja
# klassisen musiikin illat sekä kategoriattomat), joten niistä pudotetaan vain nimen avainsanalla.
# Epäselvä jää mukaan: väärin pudotettu keikka on pahempi kuin mukana oleva messu.
DROP_CATEGORIES = {"urheilu", "elokuva"}
NON_MUSIC = re.compile(
    r"messu|työpaja|workshop|kädentaidot|raksa\b|motorshow|comic con|christmas market|"
    r"jääkiekko|\bliiga\b|salibandy|koripallo|lentopallo|jalkapallo|futsal|turnaus|"
    r"stand[ -]?up|komedia|naur[au]|voimistelu|voimistelij|improvisaatio|teatteri|näytelmä|sirkus|baletti|ballet|joutsenlampi|"
    r"pähkinänsärkijä|disney on ice|pikkiriikki|elokuv|kilpailu|näyttely|luento|kurssi|opastettu|"
    r"pysäköinti|parkki|\bvip-?paketti|lahjakortti",
    re.I,
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def add_months(d: dt.date, n: int) -> dt.date:
    """Sama päivä n kuukautta myöhemmin; lyhyemmässä kuussa kuun viimeinen päivä."""
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
    return min(d.replace(year=y, month=m, day=1) + dt.timedelta(days=d.day - 1), nxt - dt.timedelta(days=1))


def parse_page(html: str):
    """Palauttaa sivun (Event-oliot ld+json:sta, tapahtuman id -> redux-data __NEXT_DATA__:sta)."""
    events = []
    # Script-tagissa on attribuutteja (id, data-nscript) ennen type-attribuuttia.
    for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        for o in data if isinstance(data, list) else [data]:
            if isinstance(o, dict) and o.get("@type") == "Event":
                events.append(o)
    extra = {}
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            queries = json.loads(m.group(1))["props"]["pageProps"]["initialReduxState"]["api"]["queries"]
            for key, q in queries.items():
                if key.startswith("cityEvents"):
                    for e in (q.get("data") or {}).get("events", []):
                        extra[e.get("url")] = e  # kumppanitapahtumilla id on "PARTNER", joten avain on url
        except (ValueError, KeyError, TypeError, AttributeError):
            pass  # kategoria- ja tilatieto puuttuu, ld+json riittää
    return events, extra


def locality(o: dict) -> str:
    """Tapahtumapaikan kaupunki: osoitteen addressLocality, muuten description-tekstin viimeinen ', Kaupunki'."""
    loc = o.get("location") or {}
    addr = loc.get("address") or {}
    city = addr.get("addressLocality") if isinstance(addr, dict) else ""
    if city:
        return city.strip()
    m = re.search(r",\s*([^,|]+)$", o.get("description") or "")
    return m.group(1).strip() if m else ""


def clean_venue(name: str) -> str:
    """'KALEVAN KIRKKO' -> 'Kalevan kirkko'; vokaalittomat lyhenteet (MTK) jäävät isoiksi."""
    name = (name or "").strip()
    if not name.isupper():
        return name
    words = []
    for w in name.split():
        if not re.search(r"[AEIOUYÄÖ]", w):
            words.append(w)
        else:
            words.append(w.lower())
    out = " ".join(words)
    return out[:1].upper() + out[1:]


def price_text(o: dict) -> str:
    offers = o.get("offers") or {}
    for off in offers if isinstance(offers, list) else [offers]:
        for key in ("lowPrice", "price"):
            try:
                v = float(str(off.get(key)).replace(",", "."))
            except (TypeError, ValueError):
                continue
            return f"alk. {v:.2f}".replace(".", ",") + " €"
    return ""


def status_text(o: dict, x: dict) -> str:
    offers = o.get("offers") or {}
    avail = " ".join(str(off.get("availability", "")) for off in (offers if isinstance(offers, list) else [offers]))
    if "EventCancelled" in str(o.get("eventStatus", "")) or x.get("cancelled"):
        return "peruttu"
    if "SoldOut" in avail or x.get("soldOut"):
        return "loppuunmyyty"
    if "LimitedAvailability" in avail or x.get("limitedAvailability"):
        return "vähissä"
    return "saatavilla"


def is_music(name: str, category: str) -> bool:
    """Datan oma kategoria ensin; sekalaisista kategorioista (ja kategoriattomista) vain avainsanat pudottavat."""
    if category == "musiikki":
        return True
    if category in DROP_CATEGORIES:
        return False
    return not NON_MUSIC.search(name)


# Järjestäjä kirjoittaa loppuunmyynnin tai peruutuksen joskus nimeen: "DISKO … / LOPPUUNMYYTY".
NAME_STATUS = re.compile(r"\s*[/|(\-–]*\s*\b(loppuunmyyty|sold\s*out|peruttu|cancelled)\b\s*\)?\s*", re.I)


def build(o: dict, x: dict):
    start = str(o.get("startDate") or "")
    try:
        d = dt.date.fromisoformat(start[:10])
    except ValueError:
        return None
    tm = re.match(r"\d{4}-\d\d-\d\dT(\d\d):(\d\d)", start)
    time_info = f"klo {int(tm.group(1))}.{tm.group(2)}" if tm and (tm.group(1), tm.group(2)) != ("00", "00") else ""
    cat_id = (x.get("majorCategory") or {}).get("id", "")
    name, status = (o.get("name") or "").strip(), status_text(o, x)
    m = NAME_STATUS.search(name)
    if m:
        status = "peruttu" if m.group(1).lower() in ("peruttu", "cancelled") else "loppuunmyyty"
        name = NAME_STATUS.sub(" ", name).strip()
    return {
        "date": d.isoformat(),
        "weekday": WEEKDAYS[d.weekday()],
        "artist": name,
        "venue": clean_venue((o.get("location") or {}).get("name", "")),
        "price": price_text(o),
        "status": status,
        "category": CATEGORIES.get(cat_id, ""),
        "time_info": time_info,
        "url": re.sub(r"\?position=\d+$", "", o.get("url") or ""),  # kumppanilinkeissä on listapaikka
        "source": "ticketmaster.fi",
    }


def collect(city: str, today: dt.date, limit: dt.date, keep_all: bool):
    slug = SLUGS[city]
    seen, out = set(), []
    for page in range(MAX_PAGES):
        url = f"{BASE}/discover/{slug}" + (f"?page={page}" if page else "")
        events, extra = parse_page(fetch(url))
        new = [o for o in events if o.get("url") not in seen]
        if not new:
            break  # tyhjä sivu tai ei uutta
        dates = []
        for o in new:
            seen.add(o.get("url"))
            e = build(o, extra.get(o.get("url"), {}))
            if not e:
                continue
            dates.append(e["date"])
            # Discover-sivulla voi olla lähikuntien tapahtumia.
            if locality(o).casefold() != city.casefold():
                continue
            if not (today.isoformat() <= e["date"] <= limit.isoformat()):
                continue
            if not keep_all and not is_music(e["artist"], e["category"]):
                continue
            out.append(e)
        # Tapahtumat tulevat päivämääräjärjestyksessä: kun koko sivu on aikavälin jälkeen, loppu on myös.
        if dates and min(dates) > limit.isoformat():
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True, choices=CITIES)
    span = ap.add_mutually_exclusive_group()
    span.add_argument("--days", type=int, default=60, help="kuinka monta päivää eteenpäin")
    span.add_argument("--months", type=int, choices=range(1, 13), metavar="1-12",
                      help="kuinka monta kalenterikuukautta eteenpäin (ohittaa --days)")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--all", action="store_true", help="älä suodata ei-musiikkitapahtumia pois")
    a = ap.parse_args()

    today = dt.date.today()
    limit = add_months(today, a.months) if a.months else today + dt.timedelta(days=a.days)
    out = []
    if a.city not in SLUGS:
        print(f"{a.city}: ticketmaster.fi:ssä ei ole kaupunkisivua, ei tapahtumia", file=sys.stderr)
    else:
        try:
            out = collect(a.city, today, limit, a.all)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            print(f"{a.city}: haku epäonnistui: {exc}", file=sys.stderr)
            out = []
        if not out:
            print(f"{a.city}: ei tapahtumia aikavälillä {today} - {limit}", file=sys.stderr)
    out.sort(key=lambda x: (x["date"], x["time_info"], x["venue"], x["artist"]))

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
