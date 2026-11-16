import importlib.util
import io
import json
import pathlib
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime
from unittest import mock

P = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "elokuvat.py"
spec = importlib.util.spec_from_file_location("elokuvat", P)
el = importlib.util.module_from_spec(spec)
spec.loader.exec_module(el)

NOW = datetime(2026, 11, 16, 17, 40, tzinfo=el.FI)
TODAY, SUNDAY = date(2026, 11, 16), date(2026, 11, 22)
WARN_DOWN = "elokuviin.com ei vastannut: näytösajat puuttuvat."


def next_page(props):
    return '<html><script id="__NEXT_DATA__" type="application/json">%s</script></html>' % json.dumps(
        {"props": {"pageProps": props}})


def nyt_card(title, d, age, href):
    return (f"<div class='movie-card paikkakunta-page-movie-card'><h3>{title}</h3>"
            f"<img src='https://nytleffaan.fi/data/icons/{age}.png'><div class='movie-card-description'>x</div>"
            f"<span class='movie-card-premiere-date'>{d}</span><a class='movie-card-movie-link' href='{href}'> Osta </a></div>")


def props(screenings, movies=None, cinemas=None):
    return {"screenings": screenings,
            "movies": movies or {"m1": {"titleFI": "Lapin sota", "title": "Lapland War", "runtime": 158,
                                        "genres": [{"name": "Draama"}], "slug": "lapin-sota"}},
            "screeningCinemas": cinemas or {"c1": {"name": "Finnkino Plaza"}},
            "cityObject": {"name": "Oulu", "nameInesive": "Oulussa"}}


def scr(starts, **k):
    return {"startsAt": starts, "movieId": "m1", "cinemaId": "c1", "auditorium": "", "bookingLink": "",
            "festival": None, "outdoor": False, **k}


NYT = nyt_card("Lapin sota", "30.10.2026", "12", "https://nytleffaan.fi/a") + \
    nyt_card("Tuleva", "27.11.2026", "S", "https://nytleffaan.fi/b")


def fake(elo, nyt=NYT):
    def f(url):
        if "elokuviin.com" in url:
            if isinstance(elo, Exception):
                raise elo
            return elo
        return nyt
    return f


class T(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(el.slug("Jyväskylä"), "jyv%C3%A4skyl%C3%A4")
        self.assertEqual(el.slug("Oulu"), "oulu")

    def test_fold(self):
        self.assertEqual(el.fold("Late Lammas -elokuva: Hämäräpuuhissa"), "latelammaselokuvahamarapuuhissa")

    def test_parse_elokuviin_time_zone(self):
        r = el.parse_elokuviin(next_page(props([scr("2026-11-16T17:40:00.000Z"), scr("2026-07-01T15:00:00.000Z")])))
        self.assertEqual([s["start"] for s in r["screenings"]], ["2026-11-16T19:40", "2026-07-01T18:00"])

    def test_parse_elokuviin_title_fallback(self):
        mv = {"m1": {"titleFI": None, "title": "Wild Horse Nine", "runtime": None, "genres": [], "slug": "w"}}
        r = el.parse_elokuviin(next_page(props([scr("2026-11-16T17:40:00.000Z")], mv)))
        self.assertEqual(r["films"][0]["title"], "Wild Horse Nine")

    def test_parse_elokuviin_fields(self):
        r = el.parse_elokuviin(next_page(props([
            scr("2026-11-16T17:40:00.000Z", festival={"name": "Rakkautta & Anarkiaa"}),
            scr("2026-11-16T18:40:00.000Z", outdoor=True),
            scr("2026-11-16T19:40:00.000Z")])))
        self.assertEqual([s["note"] for s in r["screenings"]], ["Rakkautta & Anarkiaa", "Ulkoilma", ""])
        self.assertEqual(r["screenings"][0]["cinema"], "Finnkino Plaza")
        self.assertEqual(r["screenings"][0]["auditorium"], "")
        self.assertEqual(r["inessive"], "Oulussa")
        self.assertEqual(r["films"][0]["url"], "https://elokuviin.com/elokuvat/lapin-sota")
        self.assertEqual(r["films"][0]["genres"], ["Draama"])

    def test_cinema_name_from_cinemas_list(self):
        p = props([scr("2026-11-16T17:40:00.000Z", cinemaId="c9")])
        p["cinemas"] = [{"id": "c9", "name": "Muu teatteri"}]
        self.assertEqual(el.parse_elokuviin(next_page(p))["screenings"][0]["cinema"], "Muu teatteri")

    def test_parse_elokuviin_null_slug(self):
        mv = {"m1": {"titleFI": "A", "title": "A", "runtime": None, "genres": None, "slug": None}}
        r = el.parse_elokuviin(next_page(props([scr("2026-11-16T17:40:00.000Z")], mv)))
        self.assertEqual((r["films"][0]["url"], r["films"][0]["genres"]), ("", []))

    def test_parse_elokuviin_missing(self):
        with self.assertRaises(ValueError):
            el.parse_elokuviin("<html></html>")

    def test_parse_nytleffaan(self):
        r = el.parse_nytleffaan(nyt_card("Berliinin sankari", "30.10.2026", "7", "https://x/1") +
                                nyt_card("&quot;Hei&quot;", "1.11.2026", "S", "https://x/2"))
        self.assertEqual(r[0], {"title": "Berliinin sankari", "premiere": "2026-10-30", "age": "7", "url": "https://x/1"})
        self.assertEqual((r[1]["title"], r[1]["premiere"], r[1]["age"]), ('"Hei"', "2026-11-01", "S"))

    def test_is_new(self):
        n = lambda p: el.is_new(p, TODAY, SUNDAY)
        self.assertTrue(n("2026-11-09"))
        self.assertFalse(n("2026-11-08"))
        self.assertTrue(n("2026-11-19"))
        self.assertFalse(n("2026-11-27"))
        self.assertFalse(n(""))

    def test_join(self):
        films = [{"id": "a", "title": "LAPIN, sota!"}, {"id": "b", "title": "Muu"}]
        r = el.join(films, el.parse_nytleffaan(NYT), TODAY, SUNDAY)
        self.assertEqual((r[0]["premiere"], r[0]["age"], r[0]["tags"]), ("2026-10-30", "12", []))
        self.assertEqual((r[1]["premiere"], r[1]["age"], r[1]["tags"]), ("", "", []))

    def test_build_ok(self):
        page = next_page(props([scr("2026-11-16T17:40:00.000Z"), scr("2026-11-30T17:40:00.000Z")]))
        d = el.build("Oulu", NOW, fetch=fake(page))
        self.assertEqual((d["title"], d["from"], d["to"], d["generated"]),
                         ("Elokuvat Oulussa", "2026-11-16", "2026-11-22", "2026-11-16T17:40"))
        self.assertEqual(len(d["screenings"]), 1)  # the one after Sunday is dropped
        self.assertTrue(all(s["ok"] for s in d["sources"]))
        self.assertEqual(d["films"][0]["premiere"], "2026-10-30")

    def test_build_elokuviin_down(self):
        with redirect_stderr(io.StringIO()):
            d = el.build("Oulu", NOW, fetch=fake(OSError("x")))
        self.assertEqual(d["screenings"], [])
        self.assertEqual([f["title"] for f in d["films"]], ["Lapin sota"])  # 27.11. premiere left out
        self.assertEqual(d["films"][0]["id"], "n0")
        self.assertIn(WARN_DOWN, d["warnings"])
        self.assertFalse(d["sources"][0]["ok"])
        self.assertTrue(d["sources"][1]["ok"])

    def test_build_no_next_data(self):
        with redirect_stderr(io.StringIO()):
            d = el.build("Oulu", NOW, fetch=fake("<html></html>"))
        self.assertFalse(d["sources"][0]["ok"])

    def test_build_unknown_city(self):
        err = urllib.error.HTTPError("u", 404, "nf", {}, None)
        with self.assertRaises(el.CityNotFound):
            el.build("Xyz", NOW, fetch=fake(err))
        out, e = io.StringIO(), io.StringIO()
        with mock.patch.object(el, "fetch", fake(err)), redirect_stdout(out), redirect_stderr(e):
            self.assertEqual(el.main(["--city", "Xyz"]), 2)
        self.assertEqual(e.getvalue().strip(), "elokuviin.com ei tunne kaupunkia 'Xyz'.")

    def test_weekend_warning(self):
        def warns(per_day):
            ss = [scr(f"2026-11-{16 + i}T12:00:00.000Z") for i, n in enumerate(per_day) for _ in range(n)]
            return el.WEEKEND_WARNING in el.build("Oulu", NOW, fetch=fake(next_page(props(ss))))["warnings"]
        self.assertTrue(warns([30, 30, 30, 30, 5, 5, 5]))
        self.assertFalse(warns([30] * 7))


if __name__ == "__main__":
    unittest.main()
