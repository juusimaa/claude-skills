#!/usr/bin/env python3
"""Lukee ja tallentaa /elokuvat-komennon oletukset: kaupunki ja aikaväli.

Aikaväli on "tanaan", "huomenna" tai "viikko". Kaupunki tallennetaan sellaisenaan
(välilyönnit poistettu, ensimmäinen kirjain isoksi), koska listaa kaupungeista ei ole.
Asetukset ovat käyttäjän kotihakemistossa ($XDG_CONFIG_HOME/elokuvat/asetukset.json,
oletuksena ~/.config/elokuvat/asetukset.json), eivät skillin kansiossa, joka on git-repo.

Käyttö:
    python3 -I asetukset.py                                   # tulosta voimassa olevat oletukset (JSON)
    python3 -I asetukset.py --kaupunki Jyväskylä --aikavali viikko  # tallenna (kumpikin valinnainen)
    python3 -I asetukset.py --aikavali tanaan                 # palaa tämän illan aikaväliin
    python3 -I asetukset.py --nollaa                          # poista asetukset, palaa oletuksiin
"""
import argparse
import json
import os
import pathlib
import sys

DEFAULTS = {"kaupunki": "Oulu", "aikavali": "tanaan"}
AIKAVALIT = ("tanaan", "huomenna", "viikko")


def aikavali(s: str) -> str:
    """Hyväksyy vain "tanaan", "huomenna" tai "viikko"."""
    if s in AIKAVALIT:
        return s
    raise argparse.ArgumentTypeError(f"aikaväli on 'tanaan', 'huomenna' tai 'viikko', ei {s!r}")


def kaupunki(s: str) -> str:
    """Poistaa ympäröivät välilyönnit ja muuttaa ensimmäisen kirjaimen isoksi."""
    s = s.strip()
    if not s:
        raise argparse.ArgumentTypeError("kaupunki ei voi olla tyhjä")
    return s[:1].upper() + s[1:]


def config_path() -> pathlib.Path:
    base = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
    return pathlib.Path(base) / "elokuvat" / "asetukset.json"


def load() -> dict:
    p = config_path()
    try:
        saved = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(saved, dict):
            raise ValueError("JSON-objekti puuttuu")
    except FileNotFoundError:
        saved = {}
    except (OSError, ValueError) as exc:
        print(f"asetustiedosto {p} on rikki, käytetään oletuksia: {exc}", file=sys.stderr)
        saved = {}
    out = dict(DEFAULTS, lähde="oletus")
    k = saved.get("kaupunki")
    if isinstance(k, str) and k.strip():
        out["kaupunki"], out["lähde"] = kaupunki(k), str(p)
    av = saved.get("aikavali")
    if av in AIKAVALIT:
        out["aikavali"], out["lähde"] = av, str(p)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaupunki", type=kaupunki, help="oletuskaupunki, esim. Oulu tai Jyväskylä")
    ap.add_argument("--aikavali", type=aikavali, metavar="tanaan|huomenna|viikko", help="oletusaikaväli")
    ap.add_argument("--nollaa", action="store_true", help="poista tallennetut asetukset")
    a = ap.parse_args(argv)
    p = config_path()

    if a.nollaa:
        p.unlink(missing_ok=True)
    elif a.kaupunki is not None or a.aikavali is not None:
        saved = {k: v for k, v in load().items() if k in DEFAULTS}
        if a.kaupunki is not None:
            saved["kaupunki"] = a.kaupunki
        if a.aikavali is not None:
            saved["aikavali"] = a.aikavali
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    json.dump(load(), sys.stdout, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
