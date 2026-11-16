import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from datetime import date, datetime

P = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "sivu.py"
spec = importlib.util.spec_from_file_location("sivu", P)
sivu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sivu)


def scr(start, film="f1", cinema="Finnkino Plaza", **k):
    return {"start": start, "film": film, "cinema": cinema, "auditorium": "Sali 1", "url": "", "note": "", **k}


def film(id, title, **k):
    return {"id": id, "title": title, "original": title, "runtime": 100, "genres": ["Draama"],
            "premiere": "", "age": "12", "url": "https://elokuviin.com/elokuvat/x", "tags": [], **k}


def data(**k):
    return {"city": "Oulu", "title": "Elokuvat Oulussa", "generated": "2026-11-16T17:40",
            "from": "2026-11-16", "to": "2026-11-22",
            "screenings": [], "films": [film("f1", "Lapin sota")], "sources": [], "warnings": [], **k}


class T(unittest.TestCase):
    def test_short_cinema(self):
        self.assertEqual(sivu.short_cinema("Finnkino Plaza"), "Plaza")
        self.assertEqual(sivu.short_cinema("Elokuvateatteri Star"), "Star")
        self.assertEqual(sivu.short_cinema("Oulun Elokuvakeskus R.y."), "Oulun Elokuvakeskus R.y.")

    def test_day_rows_cutoff(self):
        d = data(screenings=[scr("2026-11-16T22:45"), scr("2026-11-16T21:00"), scr("2026-11-17T10:00")])
        rows = sivu.day_rows(d, date(2026, 11, 16), datetime(2026, 11, 16, 22, 30))
        self.assertEqual([r["start"] for r in rows], ["2026-11-16T22:45"])
        rows = sivu.day_rows(d, date(2026, 11, 16), None)
        self.assertEqual([r["start"][11:] for r in rows], ["21:00", "22:45"])

    def test_md_day_columns_and_empty(self):
        d = data(films=[film("f1", "Lapin sota", tags=["Uusi"], runtime=158),
                        film("f2", "A|B", runtime=None, age="", url="")],
                 screenings=[scr("2026-11-16T19:40", url="https://x/l"),
                             scr("2026-11-16T18:00", film="f2")])
        rows = sivu.day_rows(d, date(2026, 11, 16), None)
        out = sivu.md_day(d, rows, "Elokuvat Oulussa tänään 16.11.2026").split("\n")
        self.assertEqual(out[0], "Elokuvat Oulussa tänään 16.11.2026")
        self.assertEqual(out[2], "| Klo | Elokuva | Teatteri | Sali | Kesto | Ikäraja | Liput |")
        self.assertEqual(out[4], "| 18.00 | A\\|B | Plaza | Sali 1 | – | – | – |")
        self.assertEqual(out[5], "| 19.40 | Lapin sota (Uusi) | Plaza | Sali 1 | 158 min | 12 | [Liput](https://x/l) |")
        self.assertTrue(sivu.md_day(d, [], "X tänään 1.1.2026").endswith("\nEi enää näytöksiä tänään."))
        self.assertTrue(sivu.md_day(d, [], "X huomenna 1.1.2026").endswith("\nEi näytöksiä."))
        self.assertIn("| Klo |", sivu.md_day(d, [], "X tänään 1.1.2026"))

    def test_md_week_screenings_text(self):
        d = data(screenings=[scr("2026-11-16T19:40"), scr("2026-11-16T17:15"), scr("2026-11-17T20:45"),
                             scr("2026-11-18T18:30", cinema="Elokuvateatteri Star")])
        out = sivu.md_week(d, "H").split("\n")
        self.assertEqual(out[2], "| Tagit | Elokuva | Kesto | Lajityyppi | Näytökset | Liput |")
        self.assertIn("| Plaza: ma 17.15 19.40, ti 20.45 · Star: ke 18.30 |", out[4])

    def test_md_week_order_and_empty(self):
        d = data(films=[film("a", "Aaa"), film("b", "Bbb"), film("c", "Ccc", tags=["Uusi"]), film("z", "Zzz")],
                 screenings=[scr("2026-11-16T10:00", film="a"), scr("2026-11-16T11:00", film="b"),
                             scr("2026-11-16T12:00", film="b"), scr("2026-11-16T13:00", film="c")])
        rows = sivu.md_week(d, "H").split("\n")[4:]
        self.assertEqual([r.split(" | ")[1] for r in rows], ["Ccc", "Bbb", "Aaa"])
        d["screenings"] = []
        rows = sivu.md_week(d, "H").split("\n")[4:]
        self.assertEqual(len(rows), 4)
        self.assertIn("| – |", rows[0])

    def test_headings(self):
        self.assertEqual(sivu.week_range(date(2026, 11, 16), date(2026, 11, 22)), "16.–22.11.2026")
        self.assertEqual(sivu.week_range(date(2026, 11, 30), date(2026, 12, 6)), "30.11.–6.12.2026")
        self.assertEqual(sivu.week_range(date(2026, 12, 28), date(2027, 1, 3)), "28.12.2026–3.1.2027")
        with tempfile.TemporaryDirectory() as t:
            t = pathlib.Path(t)
            (t / "tpl").write_text("<title>__TITLE__</title><script>__DATA__</script>")
            (t / "in.json").write_text(json.dumps(data()))
            sivu.TEMPLATE = t / "tpl"
            for flag, want in (("--tanaan", "Elokuvat Oulussa tänään 16.11.2026"),
                               ("--huomenna", "Elokuvat Oulussa huomenna 17.11.2026"),
                               ("--viikko", "Elokuvat Oulussa 16.–22.11.2026")):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(sivu.main([str(t / "in.json"), str(t / "o.html"), flag]), 0)
                self.assertEqual(buf.getvalue().split("\n")[0], want)

    def run_main(self, d):
        with tempfile.TemporaryDirectory() as t:
            t = pathlib.Path(t)
            (t / "tpl").write_text("<title>__TITLE__</title><script>__DATA__</script>")
            (t / "in.json").write_text(json.dumps(d))
            sivu.TEMPLATE = t / "tpl"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = sivu.main([str(t / "in.json"), str(t / "o.html")])
            page = (t / "o.html").read_text() if (t / "o.html").exists() else ""
        return rc, page

    def test_validation(self):
        bad = [scr("2026-11-16T19:40", cinema=""), scr("2026-11-16T19:40", film=""),
               {"film": "f1", "cinema": "X"}, scr("2026-11-16 19:40"), scr("2026-11-16T19:40", film="nope")]
        for s in bad:
            self.assertEqual(self.run_main(data(screenings=[s]))[0], 1, s)

    def test_page_written(self):
        d = data(films=[film("f1", "</script><b>")], screenings=[scr("2026-11-16T19:40")])
        rc, page = self.run_main(d)
        self.assertEqual(rc, 0)
        self.assertNotIn("__DATA__", page)
        self.assertNotIn("__TITLE__", page)
        self.assertIn("<\\/script><b>", page)
        self.assertEqual(page.count("</script>"), 1)


if __name__ == "__main__":
    unittest.main()
