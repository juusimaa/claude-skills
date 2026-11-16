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


if __name__ == "__main__":
    unittest.main()
