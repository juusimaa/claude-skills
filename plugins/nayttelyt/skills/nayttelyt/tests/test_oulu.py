import importlib.util
import pathlib
import unittest
from datetime import date

P = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "nayttelyt_oulu.py"
spec = importlib.util.spec_from_file_location("nayttelyt_oulu", P)
oulu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oulu)

FRM, TO = date(2026, 11, 16), date(2026, 11, 22)


class T(unittest.TestCase):
    def test_this_week(self):
        self.assertEqual(oulu.this_week(date(2026, 11, 19)), (date(2026, 11, 19), date(2026, 11, 22)))
        self.assertEqual(oulu.this_week(date(2026, 11, 22)), (date(2026, 11, 22), date(2026, 11, 22)))

    def test_overlap(self):
        o = lambda s, e, **k: oulu.overlaps({"start": s, "end": e, **k}, FRM, TO)
        self.assertTrue(o("2026-10-01", "2026-11-21"))
        self.assertFalse(o("2026-10-01", "2026-11-15"))
        self.assertFalse(o("2026-11-23", ""))
        self.assertTrue(o("2026-09-01", ""))
        self.assertTrue(o("2026-11-20", "2027-03-01"))
        self.assertTrue(o("", "", permanent=True))

    def test_is_exhibition(self):
        for name, s, e, want in [
            ("Opastettu kierros", "2026-11-18", "2026-11-18", False),
            ("Valon kerrokset", "2026-11-20", "2027-03-01", True),
            ("Piirustustyöpaja", "2026-11-18", "2026-11-25", False),
            ("Opastus näyttelyyn", "2026-11-18", "2026-11-25", False),
            ("Kuraattorikierros", "2026-11-18", "2026-11-25", False),
            ("Näyttelyesittely: Sopeutuminen", "2026-10-21", "2027-02-10", False),
            ("Verkkonäyttely: Koulutie", "2025-01-01", "2029-01-01", False),
        ]:
            self.assertEqual(oulu.is_exhibition(name, s, e), want, name)

    def test_merge(self):
        a = {"name": "Valon Kerrokset", "venue": "Oulun taidemuseo", "price": "–", "hours": "", "url": ""}
        b = {"name": "valon kerrokset", "venue": "Oulun Taidemuseo", "price": "10 €", "hours": "ti–su 10–17", "url": "https://x"}
        m = oulu.merge([a, b])
        self.assertEqual(len(m), 1)
        self.assertEqual((m[0]["price"], m[0]["hours"], m[0]["url"]), ("10 €", "ti–su 10–17", "https://x"))


if __name__ == "__main__":
    unittest.main()
