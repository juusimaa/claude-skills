import contextlib
import importlib.util
import io
import json
import pathlib
import ssl
import sys
import unittest
from unittest import mock

D = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(D))
spec = importlib.util.spec_from_file_location("yhteiset", D / "yhteiset.py")
y = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y)


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class T(unittest.TestCase):
    def _fetch(self, **kw):
        seen = {}

        def fake(req, timeout=None, context=None):
            seen["req"], seen["context"] = req, context
            return FakeResp(b"ok")

        with mock.patch.object(y.urllib.request, "urlopen", fake):
            self.assertEqual(y.fetch("https://example.test/", **kw), "ok")
        return seen

    def test_fetch_sends_honest_ua(self):
        seen = self._fetch()
        self.assertEqual(seen["req"].get_header("User-agent"), y.UA)
        self.assertIn("nayttelyt-skill/1.1", y.UA)

    def test_fetch_passes_context(self):
        ctx = ssl.create_default_context()
        self.assertIs(self._fetch(context=ctx)["context"], ctx)

    def test_run_reports_failing_reader(self):
        def ok(frm, to):
            return [{"name": "A", "venue": "V", "start": "2026-11-17", "end": "2026-11-30", "permanent": False,
                     "hours": "–", "price": "–", "url": "", "note": "", "source": ""}]

        def broken(frm, to):
            raise RuntimeError("boom")

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            y.run([ok, broken], lambda r: True, ["--from", "2026-11-16", "--to", "2026-11-22"])
        self.assertIn("broken: boom", err.getvalue())
        self.assertEqual([r["name"] for r in json.loads(out.getvalue())], ["A"])

    @staticmethod
    def _r(n, v="Museo X", src="museot.fi", s="2026-10-01", e="2027-01-31", perm=False, **kw):
        return {"name": n, "venue": v, "source": src, "start": s, "end": e, "permanent": perm,
                "hours": "–", "url": "", **kw}

    def test_merge_variant_titles(self):
        r = self._r
        m = y.merge([r("Aalto Design – Hyvinvoinnin muodot", hours="ti–su 11–18"),
                     r("Aalto Design - Hyvinvoinnin muodot", src="Linked Events", url="https://a")])
        self.assertEqual(len(m), 1)
        self.assertEqual((m[0]["hours"], m[0]["url"]), ("ti–su 11–18", "https://a"))

    def test_merge_contained_name_across_sources(self):
        r = self._r
        m = y.merge([r("Luova Tuho", hours="ti 12–16"), r("Luova Tuho – Johan Eichhorn", src="Linked Events", url="https://b"),
                     r("Luova Tuho", v="Toinen paikka")])
        self.assertEqual(len(m), 2)
        self.assertEqual((m[0]["hours"], m[0]["url"]), ("ti 12–16", "https://b"))

    def test_merge_does_not_swallow_siblings(self):
        r = self._r
        m = y.merge([r("Luova Tuho"), r("Luova Tuho – A", src="Linked Events"), r("Luova Tuho – B", src="Linked Events")])
        self.assertEqual([x["name"] for x in m], ["Luova Tuho", "Luova Tuho – B"])
        # Saman lähteen sisältyvät nimet eivät yhdisty lainkaan.
        self.assertEqual(len(y.merge([r("Syyssalonki"), r("Syyssalonki 2026")])), 2)

    def test_merge_needs_overlapping_dates(self):
        r = self._r
        m = y.merge([r("Syyssalonki", s="2025-09-01", e="2025-10-01"),
                     r("Syyssalonki", src="Linked Events", s="2026-09-01", e="2026-10-01")])
        self.assertEqual(len(m), 2)

    def test_merge_permanent_with_dated(self):
        r = self._r
        m = y.merge([r("Kokoelmanäyttely Ajan kysymys", s="2023-04-14", e="", perm=True, hours="ti 10–18"),
                     r("Ajan kysymys", src="Linked Events", s="2023-04-14", e="2026-12-31", url="https://c")])
        self.assertEqual(len(m), 1)
        self.assertEqual((m[0]["permanent"], m[0]["end"], m[0]["url"]), (True, "", "https://c"))

    def test_merge_keeps_short_distinct_names(self):
        r = self._r
        self.assertEqual(len(y.merge([r("Uni"), r("Unikuvia ja muuta", src="Linked Events")])), 2)

    def test_overlaps_permanent_not_yet_open(self):
        from datetime import date
        frm, to = date(2026, 11, 16), date(2026, 11, 22)
        self.assertFalse(y.overlaps({"start": "2026-11-28", "end": "", "permanent": True}, frm, to))
        self.assertTrue(y.overlaps({"start": "2022-09-21", "end": "", "permanent": True}, frm, to))
        self.assertTrue(y.overlaps({"start": "", "end": "", "permanent": True}, frm, to))

if __name__ == "__main__":
    unittest.main()
