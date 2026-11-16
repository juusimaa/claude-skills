# nayttelyt 1.1.0: Helsinki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/nayttelyt Helsinki` lists Helsinki's open exhibitions (museums from museot.fi, galleries from Linked Events) like Oulu does.

**Architecture:** Helpers shared by the city scripts move from `nayttelyt_oulu.py` to a new `scripts/yhteiset.py`. A new `scripts/nayttelyt_helsinki.py` has pure parse functions (tested against fixtures) and thin fetch readers. museot.fi is read over TLS with a bundled intermediate certificate. `cities/helsinki.md` and `SKILL.md` give the agent the sources and the gallery checklist.

**Tech Stack:** Python 3 stdlib only (`urllib`, `ssl`, `re`, `json`, `unittest`). No new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-16-nayttelyt-helsinki-design.md`

All paths below are relative to `plugins/nayttelyt/skills/nayttelyt/` unless they start with `plugins/`, `docs/` or `README.md`. Run tests from that folder: `python3 -m unittest discover -s tests`.

**Baseline:** before any change, `test_sivu.py` has 2 failing tests (`test_date_text`, `test_md_table`). They are unrelated to this work and `sivu.py` is not changed. "Tests pass" below means: no new failures beyond these two.

## Global Constraints

- Scripts run as `python3 -I <script>`. `-I` removes the script's folder from `sys.path`, so a script that imports `yhteiset` must first do `sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))`.
- User-Agent for every request: `nayttelyt-skill/1.1 (+https://github.com/juusimaa/claude-skills)`.
- TLS verification is never turned off. museot.fi uses a context that also trusts `certs/telia-rsa-dv-ca-v4.pem`.
- Unknown hours or price are `–`. Free entry is `Ilmainen`.
- Output rows have exactly the Oulu fields: `name, venue, start, end, permanent, hours, price, url, note, source`.
- Tests use no live network.
- Version `1.1.0`.

## Review Focus

1. **A source is down or its TLS fails:** the other source's rows still print, and stderr names the failed reader. → test in Task 3 (`test_reader_failure_is_reported`).
2. **Linked Events has more than 100 results:** every page is followed (`meta.next`); 136 this week. → test in Task 3 (`test_fetch_follows_next`).
3. **A daily sub-event of an exhibition:** it doesn't appear as a separate one-day row, and its super event (full range) stays. → test in Task 2 (`test_sub_events_dropped`).
4. **An exhibition started before the window:** it stays if it is still open (half of this week's results started earlier). → covered by the shared `overlaps` test plus Task 2's `test_started_before_window_kept`.
5. **The same exhibition in both sources under different venue names** ("Helsingin taidemuseo HAM" / "HAM Helsingin taidemuseo"): one row, with museot.fi hours. → test in Task 3 (`test_merge_across_sources`).

---

### Task 1: Shared helpers module and honest User-Agent

**Files:**
- Create: `scripts/yhteiset.py`
- Modify: `scripts/nayttelyt_oulu.py` (remove the moved helpers, import them)
- Test: `tests/test_yhteiset.py`; existing `tests/test_oulu.py` must still pass unchanged

**Interfaces:**
- Produces, in `yhteiset.py`:
  - `UA: str` (the value in Global Constraints), `FI = ZoneInfo("Europe/Helsinki")`
  - `fetch(url: str, context: ssl.SSLContext | None = None) -> str`
  - `text(fragment: str) -> str`, `fold(s: str) -> str`, `this_week(today: date) -> tuple[date, date]`
  - `overlaps(e: dict, frm: date, to: date) -> bool`, `merge(rows: list[dict]) -> list[dict]`
  - `helsinki_day(ts: str) -> str`, `table(rows: list[dict]) -> str`
  - `run(readers: list, keep, argv=None) -> int`: the current Oulu `main` generalised. Parses `--from/--to/--table`, calls each `reader(frm, to)`, prints `f"{reader.__name__}: {ex}"` to stderr on exception, keeps rows where `r["permanent"] or keep(r)` and `overlaps(...)`, merges, sorts by `(permanent, start, name)`, prints table or JSON.
- Oulu readers change signature from `(today)` to `(frm, to)`; Oulu's `main` becomes `return run(READERS, lambda r: is_exhibition(r["name"], r["start"], r["end"]), argv)`. `is_exhibition`, `row`, `venue_of`, `cap` and the Oulu constants stay in the Oulu script.

- [ ] **Step 1: Write `tests/test_yhteiset.py`** (load the module with `importlib` like `test_oulu.py`):
  - `test_fetch_sends_honest_ua`: patch `yhteiset.urllib.request.urlopen` with a fake that records the `Request`; assert `req.get_header("User-agent") == yhteiset.UA` and `"nayttelyt-skill/1.1" in yhteiset.UA`.
  - `test_fetch_passes_context`: same fake; `fetch(url, context=ctx)` passes `context=ctx` to `urlopen`.
  - `test_run_reports_failing_reader`: readers `[ok, broken]` where `broken` raises `RuntimeError("boom")`; capture stdout/stderr; assert stderr contains `"broken: boom"` and stdout JSON has `ok`'s row.
- [ ] **Step 2: Run** `python3 -m unittest tests.test_yhteiset -v` → FAIL (module missing).
- [ ] **Step 3: Create `yhteiset.py`** by moving the helpers out of `nayttelyt_oulu.py` (bodies unchanged except `fetch` gains `context` and uses the new `UA`, and `run` as above). In the Oulu script add the `sys.path` line and `from yhteiset import ...`; update its readers and `main`.
- [ ] **Step 4: Run** all tests → `test_yhteiset` and `test_oulu` pass (`oulu.this_week`, `oulu.overlaps`, `oulu.merge` still resolve through the import); only the 2 baseline `test_sivu` failures remain.
- [ ] **Step 5: Live check Oulu still answers with the new UA:** `python3 -I scripts/nayttelyt_oulu.py --table` → rows from the event service, art museum and Valve, no stderr lines. If a source now refuses the honest UA, stop and report it (don't switch back to the browser string silently).
- [ ] **Step 6: Commit** `nayttelyt: shared helpers module, honest User-Agent`.

### Task 2: Helsinki parsers (pure functions)

**Files:**
- Create: `scripts/nayttelyt_helsinki.py` (parsers only in this task)
- Create: `tests/fixtures/linkedevents_helsinki.json`, `tests/fixtures/museot_uusimaa.html`, `tests/fixtures/museot_nayttely.html`, `tests/fixtures/museot_museo.html`
- Test: `tests/test_helsinki.py`

**Interfaces:**
- Consumes: `yhteiset.text`, `yhteiset.fold`, `yhteiset.helsinki_day`.
- Produces, in `nayttelyt_helsinki.py`:
  - `parse_linkedevents(events: list[dict]) -> list[dict]` → rows (`source="Linked Events"`)
  - `parse_museot_list(html: str) -> list[dict]` → rows for cards whose `<span class="kunta">` is `Helsinki` (`source="museot.fi"`)
  - `museum_id(detail_html: str) -> str | None` → id from `<p class="paikka"><a href="/museohaku/index.php?museo_id=N">` (the first link in `class="h_info_paikka_pva"`, not the sidebar ones)
  - `parse_museum_page(html: str) -> tuple[str, str]` → `(hours, price)`
  - `canon_venue(name: str) -> str` (alias map below)
  - `DROP_VENUE: re.Pattern`, `ALIASES: dict[str, str]`

Fixtures: build them from live responses once (save a trimmed copy), keeping these cases: a gallery exhibition with `info_url`; one without `info_url`; a one-day family event; a super event plus two of its daily sub-events (e.g. "Mari Paikkari: Before Us", `super_event` set on the subs); a branch-library show (e.g. "Kallion kirjasto"); an Oodi show; a "Stadin yhteisötalo ..." show; a `Helsingin taidemuseo HAM` exhibition; an `is_free: true` offer. museot list: a Helsinki card with an end date, a Helsinki card with an open end (`28.11.2026 &#8211; ` form), a Vantaa card, a `Verkkonäyttely:` card. Museum page: the Suomen valokuvataiteen museo page (hours table + `16/6/0 €`).

Values the spec and live data pin:
- Linked Events: drop events with `super_event` set (daily sub-events); drop when `fold(name)` matches Oulu's `NOISE` words or start day == end day (Helsinki time); drop venues matching `DROP_VENUE = re.compile(r"kirjasto|yhteisotalo|asukast|seniorikeskus|palvelukeskus|perhetalo|jaahalli|musiikkiopisto", re.I)` on the folded venue name, **except** `Keskustakirjasto Oodi`. Cultural centres (Stoa, Malmitalo, Caisa, Kanneltalo, Annantalo, Maunula-talo, Vuotalo, Savoy) contain none of these words and are kept.
- Linked Events fields: `name.fi`; venue `location.name.fi`; `start`/`end` via `helsinki_day`; `url` = `info_url.fi` or `https://tapahtumat.hel.fi/fi/events/<id>` (checked: returns 200); price `Ilmainen` if any `offers[].is_free`, else `offers[0].price.fi` if present, else `–`.
- museot.fi card: `<a ... href="/nayttelykalenteri/index.php?nayttely_id=N">`, name in `<h2>`, venue = text of `<p class="paikka">` before the comma, city in `<span class="kunta">`, dates in `<p class="ajankohta">` as `d.m.yyyy &#8211; d.m.yyyy`. Open end → `permanent=True, end=""`. Drop names starting `Verkkonäyttely`. `url` = `https://museot.fi/nayttelykalenteri/index.php?nayttely_id=N`.
- Hours from `<table class="aukioloajat">` rows (`Ma`…`Su`, `Suljettu` or `11:00-19:00`): group consecutive days with the same value, lowercase days, drop `:00`, en dash: `ma suljettu, ti–pe 11–19, la–su 11–18`. Price: the first `<p>` after `Pääsymaksut` (HTML-escaped as `P&auml;&auml;symaksut`) containing `€`, through `text()`; `–` if none.
- `ALIASES` (folded Linked Events name → museot.fi name): `helsingin taidemuseo ham` → `HAM Helsingin taidemuseo`; `luonnontieteellinen museo` → `LUOMUS Luonnontieteellinen museo`; `kaisaniemen kasvitieteellinen puutarha` → `LUOMUS Kaisaniemen kasvitieteellinen puutarha`. Add others found in the fixtures where both sources name the same place differently.

- [ ] **Step 1: Bundle the certificate and save the fixtures.**
  `curl -sS http://cps.trust.telia.com/teliarsadvcav4.cer | openssl x509 -inform DER -out certs/telia-rsa-dv-ca-v4.pem`
  Check: `openssl x509 -in certs/telia-rsa-dv-ca-v4.pem -noout -subject` → `CN = Telia RSA DV CA v4`.
  Save Linked Events with `curl`, museot.fi pages with `curl --cacert certs/telia-rsa-dv-ca-v4.pem` (if curl still fails, combine the system bundle and the PEM into one scratch file for `--cacert`). Trim each to the cases above.
- [ ] **Step 2: Write `tests/test_helsinki.py`:**
  - `test_gallery_row`: the gallery event → one row, `venue` as given, `start`/`end` in Helsinki dates, `url == info_url.fi`.
  - `test_url_fallback`: event without `info_url` → `url == "https://tapahtumat.hel.fi/fi/events/<id>"`.
  - `test_one_day_dropped`, `test_sub_events_dropped` (super event kept, its subs gone), `test_started_before_window_kept` (start before 2026-11-16, end after → present).
  - `test_venue_rule`: Kallion kirjasto and Stadin yhteisötalo rows gone; Oodi row kept.
  - `test_free_price`: `is_free` → `"Ilmainen"`.
  - `test_ham_alias`: HAM event's venue == `"HAM Helsingin taidemuseo"`.
  - `test_museot_list`: only Helsinki cards; open-end card has `permanent is True` and `end == ""`; dated card has ISO `start`/`end`; Verkkonäyttely gone.
  - `test_museum_id`: the detail fixture → `"21132"`.
  - `test_museum_page`: → `("ma suljettu, ti–pe 11–19, la–su 11–18", "16/6/0 €")`.
- [ ] **Step 3: Run** `python3 -m unittest tests.test_helsinki -v` → FAIL.
- [ ] **Step 4: Implement the parsers** in `nayttelyt_helsinki.py` (with the `sys.path` line and imports from `yhteiset`; import `NOISE` from the Oulu script or move it to `yhteiset`, builder's choice).
- [ ] **Step 5: Run** → PASS.
- [ ] **Step 6: Commit** `nayttelyt: Helsinki parsers for Linked Events and museot.fi`.

### Task 3: Helsinki readers, museot.fi TLS, CLI

**Files:**
- Commit: `certs/telia-rsa-dv-ca-v4.pem` (created in Task 2)
- Modify: `scripts/nayttelyt_helsinki.py`
- Test: `tests/test_helsinki.py`

**Interfaces:**
- Consumes: Task 1 `fetch`, `run`, `merge`; Task 2 parsers.
- Produces: CLI `python3 -I scripts/nayttelyt_helsinki.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--table]`, same output shape as Oulu. Functions `linkedevents(frm, to)`, `museot(frm, to)`, `pysyvat(frm, to)`, `museot_context() -> ssl.SSLContext`, `READERS = [museot, linkedevents, pysyvat]` (museot first so its hours win in `merge`).

- [ ] **Step 1:** (The certificate was bundled in Task 2 Step 1; commit it with this task.)
- [ ] **Step 2: Check robots.txt and terms.** robots.txt was checked 16.11. in a browser: HTTP 200, empty body (nothing disallowed). Read the museot.fi terms page (footer link) once; if it forbids automated reading, stop and report before continuing.
- [ ] **Step 3: Write tests:**
  - `test_museot_context_trusts_bundle`: `museot_context()` returns an `SSLContext` with `verify_mode == ssl.CERT_REQUIRED` and `check_hostname is True`, and `get_ca_certs()` contains a cert whose subject has `Telia RSA DV CA v4`.
  - `test_fetch_follows_next`: patch `fetch` to return page 1 with `meta.next` and page 2 without; `linkedevents(...)` reads both pages.
  - `test_reader_failure_is_reported`: patch `museot` to raise `ssl.SSLError`; run with patched readers; stderr names `museot`, stdout still has the Linked Events rows.
  - `test_merge_across_sources`: a museot row and a Linked Events row for the same HAM exhibition (names differ only in case) → one row, `hours` from museot.
- [ ] **Step 4: Run** → FAIL.
- [ ] **Step 5: Implement:**
  - `museot_context()`: `ssl.create_default_context()` then `load_verify_locations(cafile=<skill>/certs/telia-rsa-dv-ca-v4.pem)`.
  - `linkedevents(frm, to)`: URL `https://api.hel.fi/linkedevents/v1/event/?keyword=yso:p5121&division=helsinki&start=<frm>&end=<to>&include=location&page_size=100`; follow `meta.next` up to 20 pages; `parse_linkedevents`.
  - `museot(frm, to)`: list URL `https://museot.fi/nayttelykalenteri/index.php?maakunta_id=1&nayttelyhaku=1&kaikki=1` (Uusimaa = 1, checked); `parse_museot_list`; then, **once per distinct venue**, fetch one of its exhibition pages → `museum_id` → `https://museot.fi/museohaku/index.php?museo_id=<id>` → `parse_museum_page`; fill `hours`/`price` on that venue's rows. About 28 venues, so about 56 extra requests; run them sequentially. A failed museum page leaves `–` for that venue only.
  - `pysyvat(frm, to)`: empty list for now; the builder adds handwritten rows only for major permanent collections that museot.fi doesn't list (check Ateneum, Kiasma, Kansallismuseo, Design Museum against a live run first).
  - `main` = `run(READERS, keep, argv)` where `keep` is the Task 2 filters already applied in the parsers (so `keep = lambda r: True`).
- [ ] **Step 6: Run** tests → PASS.
- [ ] **Step 7: Live check:** `python3 -I scripts/nayttelyt_helsinki.py --table` → museums with hours (e.g. Suomen valokuvataiteen museo `ma suljettu, ti–pe 11–19, …`) and galleries (Helsinki Contemporary, Galerie Forsblom, Galleria Huuto …), no Espoo libraries, no one-day events, no stderr lines. Note the row count for the city file.
- [ ] **Step 8: Commit** `nayttelyt: Helsinki script with museot.fi and Linked Events`.

### Task 4: City file, skill text, version 1.1.0

**Files:**
- Create: `cities/helsinki.md`
- Modify: `SKILL.md`, `plugins/nayttelyt/.claude-plugin/plugin.json`, `plugins/nayttelyt/CHANGELOG.md`, `README.md` (repo root), `.claude-plugin/marketplace.json` (repo root, only if it names cities)
- Test: `tests/test_asetukset.py` (existing; add one case)

- [ ] **Step 1: Test:** in `test_asetukset.py` add `test_helsinki_supported`: with the real cities folder, `--kaupunki Helsinki` saves and prints `"kaupunki": "Helsinki"`. Run → FAIL (no `cities/helsinki.md` yet).
- [ ] **Step 2: Write `cities/helsinki.md`** in the same structure as `cities/oulu.md` (title line `# Helsinki`): Skriptit; Lähteet (1 Linked Events **skripti**, 2 museot.fi **skripti** incl. the TLS note and the per-venue museum pages, 3 the stadissa.fi gallery list **haku**: all 20 galleries with address and website, to be checked in one batched web-fetch call only when Linked Events didn't return them); Pysyvät näyttelyt (whatever `pysyvat` adds); Sudenkuopat (UTC times, sub-events, venue rule incl. the Oodi exception and the kept cultural centres, Espoo results without `division`, alias names, museot.fi certificate). Written in Finnish, like oulu.md. Date-stamp facts "Tarkistettu 16.11.2026".
- [ ] **Step 3: Run** the test → PASS.
- [ ] **Step 4: Update `SKILL.md`:** description and "Tuetut kaupungit" table add Helsinki (`Helsingissä`, `cities/helsinki.md`); the "Kaupunki" bullet lists Oulu and Helsinki as supported and removes Helsinki from the "ei vielä tuettu" list (15 cities remain); step 2 runs `scripts/nayttelyt_<kaupunki>.py` (the script named in the city file) instead of only the Oulu one; step 6's artifact example stays per-city.
- [ ] **Step 5: Version:** `plugin.json` `"version": "1.1.0"`; `CHANGELOG.md` new top entry `## 1.1.0 – 2026-11-16` (Helsinki added: museums from museot.fi, galleries from Linked Events; scripts identify themselves as nayttelyt-skill); README row version `1.1.0` and "Oulu for now" → "Oulu and Helsinki for now"; README usage example `/nayttelyt Helsinki`.
- [ ] **Step 6: Run** all tests → only the 2 baseline failures.
- [ ] **Step 7: Commit** `nayttelyt 1.1.0: Helsinki`.
