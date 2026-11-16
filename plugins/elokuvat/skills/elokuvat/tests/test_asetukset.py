import contextlib
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "asetukset.py"
spec = importlib.util.spec_from_file_location("asetukset", SCRIPT)
asetukset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asetukset)


class AsetuksetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.file = self.root / "elokuvat" / "asetukset.json"
        patcher = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = asetukset.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_defaults(self):
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["kaupunki"], "Oulu")
        self.assertEqual(data["aikavali"], "tanaan")
        self.assertEqual(data["lähde"], "oletus")

    def test_save_and_load(self):
        code, out, err = self.run_main("--kaupunki", "Jyväskylä", "--aikavali", "viikko")
        self.assertEqual(code, 0, err)
        self.assertEqual(
            json.loads(self.file.read_text(encoding="utf-8")),
            {"kaupunki": "Jyväskylä", "aikavali": "viikko"},
        )
        data = json.loads(out)
        self.assertEqual(data["kaupunki"], "Jyväskylä")
        self.assertEqual(data["aikavali"], "viikko")
        self.assertEqual(data["lähde"], str(self.file))

    def test_any_city_accepted(self):
        code, out, err = self.run_main("--kaupunki", "Kemijärvi")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["kaupunki"], "Kemijärvi")

    def test_city_is_stripped_and_first_letter_capitalised(self):
        code, out, err = self.run_main("--kaupunki", "  jyväskylä ")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["kaupunki"], "Jyväskylä")

    def test_bad_window(self):
        with self.assertRaises(SystemExit) as cm:
            with contextlib.redirect_stderr(io.StringIO()):
                self.run_main("--aikavali", "3")
        self.assertEqual(cm.exception.code, 2)
        self.assertFalse(self.file.exists())

    def test_reset(self):
        self.run_main("--kaupunki", "Turku")
        self.assertTrue(self.file.exists())
        code, out, _ = self.run_main("--nollaa")
        self.assertEqual(code, 0)
        self.assertFalse(self.file.exists())
        self.assertEqual(json.loads(out)["kaupunki"], "Oulu")

    def test_broken_file(self):
        self.file.parent.mkdir(parents=True)
        self.file.write_text("{ei ole json", encoding="utf-8")
        code, out, err = self.run_main()
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["kaupunki"], "Oulu")
        self.assertEqual(data["aikavali"], "tanaan")
        self.assertIn("rikki", err)


if __name__ == "__main__":
    unittest.main()
