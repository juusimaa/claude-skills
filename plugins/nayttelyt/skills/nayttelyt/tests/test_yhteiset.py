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

    def test_merge_variant_titles(self):
        r = lambda n, v, h="–", u="": {"name": n, "venue": v, "permanent": False, "hours": h, "url": u}
        m = y.merge([r("Aalto Design – Hyvinvoinnin muodot", "Designmuseo", h="ti–su 11–18"),
                     r("Aalto Design - Hyvinvoinnin muodot", "Designmuseo", u="https://a"),
                     r("Luova Tuho – Johan Eichhornin valokuvasarja", "Museo X", h="ti 12–16"),
                     r("Luova Tuho", "Museo X", u="https://b"),
                     r("Luova Tuho", "Toinen paikka"),
                     r("Kevät", "Museo X")])
        self.assertEqual(len(m), 4)
        self.assertEqual((m[0]["hours"], m[0]["url"]), ("ti–su 11–18", "https://a"))
        self.assertEqual((m[1]["hours"], m[1]["url"]), ("ti 12–16", "https://b"))

    def test_merge_keeps_short_distinct_names(self):
        r = lambda n: {"name": n, "venue": "V", "permanent": False}
        self.assertEqual(len(y.merge([r("Uni"), r("Unikuvia ja muuta")])), 2)


if __name__ == "__main__":
    unittest.main()
