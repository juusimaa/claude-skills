"""Kaupunkiskriptien yhteiset apufunktiot (nayttelyt_oulu.py, nayttelyt_helsinki.py).

Kaupunkiskripti ajetaan `python3 -I`, joka jättää skriptin kansion pois sys.pathista, joten
skripti lisää kansionsa itse ennen `import yhteiset`.
"""
import argparse
import html as htmllib
import json
import re
import ssl
import sys
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

UA = "nayttelyt-skill/1.1 (+https://github.com/juusimaa/claude-skills)"
FI = ZoneInfo("Europe/Helsinki")


def fetch(url: str, context: ssl.SSLContext | None = None) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fi"})
    with urllib.request.urlopen(req, timeout=30, context=context) as r:
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


def helsinki_day(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(FI).date().isoformat()


def table(rows: list[dict]) -> str:
    head = ["Näyttely", "Paikka", "Ajalla", "Aukioloajat", "Hinta"]
    body = [[r["name"], r["venue"], "Pysyvä" if r["permanent"] else f'{r["start"] or "–"} – {r["end"] or "–"}',
             r["hours"] or "–", r["price"] or "–"] for r in rows]
    w = [max(len(x[i]) for x in [head] + body) for i in range(len(head))]
    return "\n".join("  ".join(c.ljust(w[i]) for i, c in enumerate(x)).rstrip() for x in [head] + body)


def run(readers: list, keep, argv=None) -> int:
    """Kaupunkiskriptin main: lukee lähteet (reader(frm, to)), suodattaa, yhdistää ja tulostaa."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args(argv)
    week = this_week(datetime.now(FI).date())
    frm = date.fromisoformat(a.frm) if a.frm else week[0]
    to = date.fromisoformat(a.to) if a.to else week[1]
    rows = []
    for rd in readers:
        try:
            rows += rd(frm, to)
        except Exception as ex:
            print(f"{rd.__name__}: {ex}", file=sys.stderr)
    rows = merge([r for r in rows if (r["permanent"] or keep(r)) and overlaps(r, frm, to)])
    rows.sort(key=lambda r: (r["permanent"], r["start"], r["name"]))
    print(table(rows) if a.table else json.dumps(rows, ensure_ascii=False, indent=2))
    return 0
