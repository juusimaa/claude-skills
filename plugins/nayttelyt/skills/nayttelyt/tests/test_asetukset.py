import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "asetukset.py"


class AsetuksetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.config = root
        self.cities = root / "cities"
        self.cities.mkdir()
        (self.cities / "oulu.md").write_text("# Oulu\n", encoding="utf-8")
        self.env = dict(os.environ, XDG_CONFIG_HOME=str(root), NAYTTELYT_CITIES_DIR=str(self.cities))

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), *args],
            env=self.env, capture_output=True, text=True, encoding="utf-8",
        )

    def test_defaults(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["kaupunki"], "Oulu")
        self.assertEqual(out["aikavali"], "viikko")
        self.assertEqual(out["lähde"], "oletus")

    def test_save_months_then_week(self):
        r = self.run_script("--aikavali", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["aikavali"], 3)
        self.assertTrue((self.config / "nayttelyt" / "asetukset.json").exists())

        r = self.run_script("--aikavali", "viikko")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["aikavali"], "viikko")

    def test_bad_value(self):
        r = self.run_script("--aikavali", "13")
        self.assertNotEqual(r.returncode, 0)

    def test_unknown_city(self):
        r = self.run_script("--kaupunki", "Tampere")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Oulu", r.stderr)

    def test_helsinki_supported(self):
        real_cities = pathlib.Path(__file__).resolve().parent.parent / "cities"
        config = tempfile.TemporaryDirectory()
        self.addCleanup(config.cleanup)
        env = dict(os.environ, XDG_CONFIG_HOME=config.name, NAYTTELYT_CITIES_DIR=str(real_cities))
        r = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--kaupunki", "Helsinki"],
            env=env, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["kaupunki"], "Helsinki")


if __name__ == "__main__":
    unittest.main()
