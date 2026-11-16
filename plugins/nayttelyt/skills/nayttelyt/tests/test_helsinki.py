import contextlib
import importlib.util
import io
import json
import pathlib
import ssl
import unittest
from datetime import date
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nayttelyt_helsinki", HERE.parent / "scripts" / "nayttelyt_helsinki.py")
hki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hki)

FX = HERE / "fixtures"
EVENTS = json.loads((FX / "linkedevents_helsinki.json").read_text())
ROWS = hki.parse_linkedevents(EVENTS)
by = lambda n: [r for r in ROWS if r["name"] == n]


class Parsers(unittest.TestCase):
    def test_gallery_row(self):
        (r,) = by("Eeva Juuti: Message")
        self.assertEqual((r["venue"], r["start"], r["end"]), ("MUU Helsinki Nykytaidekeskus", "2026-11-21", "2026-12-20"))
        self.assertEqual(r["url"], "https://www.muu.fi/fi/muuspace/nayttelyt/eeva-juuti-message/")

    def test_url_fallback(self):
        (r,) = by("Pia Männikkö: Kesäyön unelma")
        self.assertEqual(r["url"], "https://tapahtumat.hel.fi/fi/events/helsinki:agquakw62q")

    def test_one_day_dropped(self):
        self.assertEqual(by("Lastentarhamuseon avoimet ovet"), [])

    def test_sub_events_dropped(self):
        self.assertEqual(len(by("Mari Paikkari: Before Us")), 1)
        self.assertEqual(by("Mari Paikkari: Before Us")[0]["end"], "2026-12-22")

    def test_started_before_window_kept(self):
        self.assertTrue(any(r["venue"] == "Galerie Forsblom" and r["start"] < "2026-11-16" for r in ROWS))

    def test_venue_rule(self):
        venues = {r["venue"] for r in ROWS}
        self.assertNotIn("Kallion kirjasto", venues)
        self.assertFalse(any("yhteisotalo" in v.lower() or "yhteisötalo" in v.lower() for v in venues))
        self.assertIn("Keskustakirjasto Oodi", venues)

    def test_free_price(self):
        self.assertEqual(by("Eeva Juuti: Message")[0]["price"], "Ilmainen")
        self.assertEqual(by("Emma Talbot: Et ole keskipiste")[0]["price"], "20/12/0")

    def test_ham_alias(self):
        self.assertEqual(by("Emma Talbot: Et ole keskipiste")[0]["venue"], "HAM Helsingin taidemuseo")

    def test_museot_list(self):
        rows = hki.parse_museot_list((FX / "museot_uusimaa.html").read_text())
        names = {r["name"]: r for r in rows}
        self.assertEqual(set(names), {"Tatenda Chidora: Jos covid olisi väri", "Seurasaaren kesämökki"})
        open_end = names["Seurasaaren kesämökki"]
        self.assertIs(open_end["permanent"], True)
        self.assertEqual(open_end["end"], "")
        dated = names["Tatenda Chidora: Jos covid olisi väri"]
        self.assertEqual((dated["start"], dated["end"], dated["venue"]), ("2026-12-04", "2027-01-31", "Suomen valokuvataiteen museo"))
        self.assertEqual(dated["url"], "https://museot.fi/nayttelykalenteri/index.php?nayttely_id=45570")

    def test_museum_id(self):
        self.assertEqual(hki.museum_id((FX / "museot_nayttely.html").read_text()), "21132")

    def test_museum_page(self):
        self.assertEqual(hki.parse_museum_page((FX / "museot_museo.html").read_text()),
                         ("ma suljettu, ti–pe 11–19, la–su 11–18", "16/6/0 €"))


class Readers(unittest.TestCase):
    def test_museot_context_trusts_bundle(self):
        ctx = hki.museot_context()
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(ctx.check_hostname)
        self.assertTrue(any("Telia RSA DV CA v4" in str(c["subject"]) for c in ctx.get_ca_certs()))

    def test_fetch_follows_next(self):
        p1 = {"data": EVENTS[:1], "meta": {"next": "https://example.test/p2"}}
        p2 = {"data": EVENTS[1:2], "meta": {"next": None}}
        with mock.patch.object(hki, "fetch", side_effect=[json.dumps(p1), json.dumps(p2)]) as f:
            rows = hki.linkedevents(date(2026, 11, 16), date(2026, 11, 22))
        self.assertEqual(f.call_count, 2)
        self.assertEqual(len(rows), 2)

    def test_reader_failure_is_reported(self):
        def museot(frm, to):
            raise ssl.SSLError("bad cert")
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(hki, "READERS", [museot, lambda f, t: ROWS]), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            hki.main(["--from", "2026-11-16", "--to", "2026-11-22"])
        self.assertIn("museot: ", err.getvalue())
        self.assertIn("Eeva Juuti: Message", out.getvalue())

    def test_merge_across_sources(self):
        (ev,) = by("Emma Talbot: Et ole keskipiste")
        mu = hki.row("EMMA TALBOT: ET OLE KESKIPISTE", "HAM Helsingin taidemuseo", "2026-10-09", "2027-04-25",
                     hours="ti–su 11–18", price="–", source="museot.fi")
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(hki, "READERS", [lambda f, t: [mu], lambda f, t: [ev]]), contextlib.redirect_stdout(out):
            hki.main(["--from", "2026-11-16", "--to", "2026-11-22"])
        merged = json.loads(out.getvalue())
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["hours"], "ti–su 11–18")


if __name__ == "__main__":
    unittest.main()
