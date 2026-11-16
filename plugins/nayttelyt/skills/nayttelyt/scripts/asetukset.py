#!/usr/bin/env python3
"""Lukee ja tallentaa /nayttelyt-komennon oletukset: kaupunki ja aikaväli.

Aikaväli on "viikko" (tämä viikko) tai kuukausimäärä 1-12 (tulevat N kuukautta).
Asetukset ovat käyttäjän kotihakemistossa ($XDG_CONFIG_HOME/nayttelyt/asetukset.json,
oletuksena ~/.config/nayttelyt/asetukset.json), eivät skillin kansiossa, joka on git-repo.
Tuetut kaupungit luetaan cities/*.md-tiedostojen otsikoista ("# Oulu").

Käyttö:
    python3 -I asetukset.py                                   # tulosta voimassa olevat oletukset (JSON)
    python3 -I asetukset.py --kaupunki Oulu --aikavali 3      # tallenna (kumpikin valinnainen)
    python3 -I asetukset.py --aikavali viikko                 # palaa viikkoaikaväliin
    python3 -I asetukset.py --nollaa                          # poista asetukset, palaa oletuksiin
"""
import argparse
import json
import os
import pathlib
import sys
import unicodedata

# shortcut: NAYTTELYT_CITIES_DIR is a test-only override, default is the skill's cities dir
CITIES_DIR = pathlib.Path(os.environ.get("NAYTTELYT_CITIES_DIR") or pathlib.Path(__file__).resolve().parent.parent / "cities")
DEFAULTS = {"kaupunki": "Oulu", "aikavali": "viikko"}


def aikavali(s: str) -> str | int:
    """Hyväksyy "viikko" tai kuukausimäärän 1-12."""
    if s == "viikko":
        return s
    if s.isdigit() and 1 <= int(s) <= 12:
        return int(s)
    raise argparse.ArgumentTypeError(f"aikaväli on 'viikko' tai 1-12 kuukautta, ei {s!r}")


def config_path() -> pathlib.Path:
    base = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
    return pathlib.Path(base) / "nayttelyt" / "asetukset.json"


def fold(s: str) -> str:
    """Vertailuavain: pienet kirjaimet ilman ääkkösten pisteitä ("Jyväskylä" -> "jyvaskyla")."""
    return "".join(c for c in unicodedata.normalize("NFD", s.strip().lower()) if not unicodedata.combining(c))


def cities() -> dict:
    out = {}
    for f in sorted(CITIES_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        first = f.read_text(encoding="utf-8").split("\n", 1)[0]
        if first.startswith("# "):
            name = first[2:].strip()
            out[fold(name)] = name
    return out


def load() -> dict:
    p = config_path()
    try:
        saved = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        saved = {}
    except (OSError, ValueError) as exc:
        print(f"asetustiedosto {p} on rikki, käytetään oletuksia: {exc}", file=sys.stderr)
        saved = {}
    known = cities()
    out = dict(DEFAULTS, lähde="oletus")
    if fold(str(saved.get("kaupunki", ""))) in known:
        out["kaupunki"], out["lähde"] = known[fold(saved["kaupunki"])], str(p)
    av = saved.get("aikavali")
    if av == "viikko" or (isinstance(av, int) and not isinstance(av, bool) and 1 <= av <= 12):
        out["aikavali"], out["lähde"] = av, str(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaupunki", help="oletuskaupunki perusmuodossa, esim. Oulu")
    ap.add_argument("--aikavali", type=aikavali, metavar="viikko|1-12", help="oletusaikaväli: viikko tai kuukausia 1-12")
    ap.add_argument("--nollaa", action="store_true", help="poista tallennetut asetukset")
    a = ap.parse_args()
    p = config_path()

    if a.nollaa:
        p.unlink(missing_ok=True)
    elif a.kaupunki is not None or a.aikavali is not None:
        known = cities()
        saved = {k: v for k, v in load().items() if k in DEFAULTS}
        if a.kaupunki is not None:
            if fold(a.kaupunki) not in known:
                print(f"kaupunkia {a.kaupunki!r} ei tueta. Tuetut: {', '.join(sorted(known.values()))}", file=sys.stderr)
                return 2
            saved["kaupunki"] = known[fold(a.kaupunki)]
        if a.aikavali is not None:
            saved["aikavali"] = a.aikavali
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    json.dump(load(), sys.stdout, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
