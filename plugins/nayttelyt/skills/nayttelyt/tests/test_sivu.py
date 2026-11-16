import importlib.util
import json
import pathlib
import tempfile
import unittest
from datetime import date

P = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "sivu.py"
spec = importlib.util.spec_from_file_location("sivu", P)
sivu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sivu)

D = date(2026, 11, 16)


def ex(**k):
    return {"name": "N", "venue": "V", "start": "", "end": "", "permanent": False, **k}


class T(unittest.TestCase):
    def test_tags(self):
        t = lambda **k: sivu.tags(ex(**k), D, D)
        self.assertEqual(t(start="2026-11-20"), ["Uusi"])
        self.assertEqual(t(start="2026-11-23"), [])
        self.assertEqual(t(end="2026-11-21"), ["Päättyy pian"])
        self.assertEqual(t(end="2026-11-30"), [])
        self.assertEqual(t(permanent=True), ["Pysyvä"])
        self.assertEqual(t(start="2026-11-20", end="2026-11-21"), ["Uusi", "Päättyy pian"])

    def test_tags_future_window(self):
        self.assertIn("Uusi", sivu.tags(ex(start="2026-12-03"), date(2026, 12, 1), D))

    def test_sort(self):
        rows = [ex(name="plain", start="2026-10-01"), ex(name="perm", permanent=True),
                ex(name="soon", start="2026-10-01", end="2026-11-18"), ex(name="new", start="2026-11-17")]
        for r in rows:
            r["tags"] = sivu.tags(r, D, D)
        self.assertEqual([r["name"] for r in sorted(rows, key=sivu.sort_key)], ["new", "soon", "plain", "perm"])

    def test_date_text(self):
        d = lambda **k: sivu.date_text(ex(**k), D)
        self.assertEqual(d(start="2026-11-20", end="2027-03-01"), "20.11.–1.3.2027")
        self.assertEqual(d(start="2026-10-01"), "1.10.–")
        self.assertEqual(d(permanent=True), "Pysyvä")
        self.assertEqual(d(start="2026-10-01", end="2026-11-21"), "1.10.–21.11.")

    def test_md_table(self):
        data = {"title": "Näyttelyt Oulussa", "range": "16.–22.11.2026", "generated": "2026-11-16", "from": "2026-11-16",
                "exhibitions": [ex(name="A", url="https://x.fi", start="2026-11-20", tags=["Uusi"]), ex(name="B", url="")]}
        out = sivu.md_table(data)
        lines = out.splitlines()
        self.assertEqual(lines[0], "Näyttelyt Oulussa 16.–22.11.2026")
        self.assertIn("| Tagit | Näyttely | Paikka | Ajalla | Aukioloajat | Hinta | Linkki |", lines)
        self.assertIn("[Linkki](https://x.fi)", out)
        self.assertTrue(out.rstrip().endswith("| – |"))

    def test_validation(self):
        base = {"title": "T", "range": "r", "generated": "2026-11-16", "from": "2026-11-16"}
        with tempfile.TemporaryDirectory() as d:
            for bad in ({"name": "A"}, ex(name="A", start="20.11.2026")):
                i = pathlib.Path(d) / "i.json"
                i.write_text(json.dumps({**base, "exhibitions": [bad]}), encoding="utf-8")
                self.assertEqual(sivu.main([str(i), str(pathlib.Path(d) / "o.html")]), 1)
            i.write_text(json.dumps({**base, "exhibitions": [ex(name="A </script>")]}), encoding="utf-8")
            o = pathlib.Path(d) / "o.html"
            self.assertEqual(sivu.main([str(i), str(o)]), 0)
            self.assertNotIn("</script>\"", o.read_text(encoding="utf-8").split('id="data">')[1].split("</script>")[0])


if __name__ == "__main__":
    unittest.main()
