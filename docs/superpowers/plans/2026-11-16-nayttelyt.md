# /nayttelyt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The plan can also be run with `/orchestrate`. The tasks have clear file boundaries, and their dependencies are listed under "Order".

**Goal:** Add a `nayttelyt` plugin. Its `/nayttelyt` skill lists the exhibitions open in Oulu during a time window (default: this week), with tags for new, closing soon and permanent. The list is shown as a terminal table and as a filterable web page.

**Architecture:** This is a copy of keikat's layout. An Oulu script fetches exhibitions and filters them to the time window. `sivu.py` adds the tags, sorts the rows, prints the markdown table and fills the HTML template. `SKILL.md` tells Claude how to run the scripts, fill gaps with web search, and publish the page.

**Tech Stack:** Python 3 standard library only, with plain HTTP and no browser. The page is a single HTML template with inline CSS and JS. Tests use `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-16-nayttelyt-design.md`

## Global Constraints

- Command, plugin and folder names are `nayttelyt` (ASCII). Nothing under `plugins/keikat/` changes.
- Scripts use only the standard library and are run with `python3 -I`. Under `-I`, a script cannot import a sibling module, so every script is self-contained. Tests load the scripts with `importlib`.
- `SKILL.md`, `cities/oulu.md`, script messages and page text are in Finnish. README and the marketplace entry are in English.
- License Apache-2.0, author "Jouni Uusimaa", like `plugins/keikat/.claude-plugin/plugin.json`.
- An unknown value is `–`, never guessed. A failing source prints a message to stderr, and the script still exits 0 with the other sources' rows.
- Settings go in `$XDG_CONFIG_HOME/nayttelyt/asetukset.json` (default `~/.config/nayttelyt/`).

## Shared data shape (all tasks)

One exhibition is a dict like this:

```json
{"name": "Valon kerrokset", "venue": "Oulun taidemuseo", "start": "2026-11-20", "end": "2027-03-01",
 "permanent": false, "hours": "ti–su 10–17", "price": "10 € / alennus 7 €", "url": "https://…",
 "note": "", "source": "tapahtumat.munoulu.fi"}
```

- `start` and `end` are ISO dates or `""`.
- A permanent row has `permanent: true`, empty `start` and `end`, and a name like `Pohjois-Pohjanmaan museo – pysyvät näyttelyt`.
- `hours`, `price` and `note` are free text. `price` is `Ilmainen` for free entry and `–` when unknown.

The page JSON, which is the input to `sivu.py`, looks like this:

```json
{"title": "Näyttelyt Oulussa", "range": "16.–22.11.2026", "generated": "2026-11-16",
 "from": "2026-11-16", "to": "2026-11-22", "exhibitions": [ ... ], "notes": ["…"],
 "sources": [{"name": "…", "url": "…"}]}
```

## Order

Task 1 (sources) → Task 3 (Oulu script). Tasks 2 and 4 are independent of everything and can run in parallel with Task 1. Task 5 needs Tasks 1–4. Task 6 comes last.

## Review Focus

1. **An exhibition that started earlier and has no announced end** (`start` in the past, `end` empty) must be listed. It must not be tagged Pysyvä, and its date shows as `20.11.–`. Tested in Task 3 (overlap) and Task 4 (tags and date text).
2. **A one-off event at a museum** (a guided tour, a workshop, a talk) comes from the events service with a single date. It must be dropped. Tested in Task 3 (`is_exhibition`).
3. **A future window** such as "joulukuussa": the Uusi tag is measured from the window's start, not from today. Tested in Task 4.
4. **The same exhibition from two sources** with differences in case, accents or spacing, e.g. `Valon Kerrokset` vs `valon kerrokset`, at the same venue: the rows are merged into one, and the merged row keeps the non-empty `hours`, `price` and `url`. Tested in Task 3 (`merge`).
5. **A date range across the new year**, e.g. 20.11.–1.3.2027: it overlaps the window correctly and is shown with the end year. Tested in Task 3 (overlap) and Task 4 (date text).

---

### Task 1: Find out how to read Oulu's exhibition sources

This is research, not TDD. The deliverable is a file, and Task 3 is built from it.

**Files:**
- Create: `plugins/nayttelyt/skills/nayttelyt/cities/oulu.md`

**Interfaces:**
- Produces: `cities/oulu.md`. Line 1 is exactly `# Oulu`, because `asetukset.py` reads the city name from it. Then these sections:
  - `## Skriptit`: an empty placeholder that Task 5 fills.
  - `## Lähteet`: for each source, the URL and how to read it over plain HTTP: the endpoint, the category id or query, and the fields available (name, dates, hours, fee, link). Mark each source as **skripti** (Task 3 reads it) or **haku** (web search in SKILL.md).
  - `## Pysyvät näyttelyt`: per venue, its permanent exhibitions page, opening hours page and fee page.
  - `## Sudenkuopat`: pitfalls, including any venue that is closed now.

- [ ] **Step 1: Events service.** Look at tapahtumat.munoulu.fi. Find how the "Näyttelyt" exhibitions category can be read without a browser: for example a search or topic URL with a category filter, or a widget JSON like the one in `plugins/keikat/skills/keikat/scripts/paikat_oulu.py:181` (`MUSIIKKIKESKUS_WIDGET`). The page `https://tapahtumat.munoulu.fi/fi-FI` embeds a category table (`categoriesByKey`, `lahellaFiLabels` with `hm_nayttelyt`). Write down the working URL and an example item with its fields.
  - Check: `curl -sL -A "Mozilla/5.0" "<url>"` returns at least one exhibition with a name and a date range.
- [ ] **Step 2: Venues.** For each venue, check whether its exhibition page is plain HTML (`curl` shows the exhibition names): Oulun taidemuseo, Pohjois-Pohjanmaan museo, Tietomaa, Galleria Harmaja, the Valve galleries / Taidekeskus Kulttuurivalimo, the main library's exhibition spaces, and Oulu2026 (oulu2026.eu/program). For each, record the URL, whether it is readable, and where hours and fees are shown.
- [ ] **Step 3: Write `cities/oulu.md`** from what Steps 1 and 2 found. If the events service can't be read, say so and make the readable venue pages the scripted sources. Any source that fails gets the label **haku**.
- [ ] **Step 4: Commit**

```bash
git add plugins/nayttelyt/skills/nayttelyt/cities/oulu.md
git commit -m "nayttelyt: Oulu sources"
```

### Task 2: Plugin scaffold and settings script

**Files:**
- Create: `plugins/nayttelyt/.claude-plugin/plugin.json`
- Create: `plugins/nayttelyt/skills/nayttelyt/scripts/asetukset.py`
- Test: `plugins/nayttelyt/skills/nayttelyt/tests/test_asetukset.py`
- Modify: `.claude-plugin/marketplace.json`. Add a `nayttelyt` entry, and add `/nayttelyt` to the top-level description.

**Interfaces:**
- Consumes: `cities/*.md` (line 1 `# <City>`). Use a temporary `cities` dir in tests.
- Produces: the CLI `asetukset.py [--kaupunki X] [--aikavali viikko|1-12] [--nollaa]`. It prints JSON `{"kaupunki": "Oulu", "aikavali": "viikko", "lähde": "oletus"}`. `aikavali` is the string `"viikko"` or an int 1–12.

- [ ] **Step 1: Write the failing tests.** Run the script with `subprocess`, with `XDG_CONFIG_HOME` set to a temp dir:
  - `test_defaults`: no args → `kaupunki == "Oulu"`, `aikavali == "viikko"`, `lähde == "oletus"`.
  - `test_save_months_then_week`: `--aikavali 3` → `aikavali == 3`; then `--aikavali viikko` → `"viikko"`. The file is in `<tmp>/nayttelyt/asetukset.json`.
  - `test_bad_value`: `--aikavali 13` → non-zero exit code.
  - `test_unknown_city`: `--kaupunki Tampere` → exit 2, and stderr contains `Oulu`. Only Oulu exists in this iteration.
- [ ] **Step 2: Run them, expect FAIL.** Run: `python3 -m unittest discover -s plugins/nayttelyt/skills/nayttelyt/tests -v`
- [ ] **Step 3: Implement.** Copy `plugins/keikat/skills/keikat/scripts/asetukset.py` and change it:
  - config dir `nayttelyt`
  - `DEFAULTS = {"kaupunki": "Oulu", "aikavali": "viikko"}`
  - replace `--kuukaudet` with `--aikavali`, parsed by a function `aikavali(s: str) -> str | int`. It accepts `viikko` or `1`–`12` and otherwise raises `argparse.ArgumentTypeError`.
  - `load()` accepts a saved `"viikko"` or an int 1–12.
  - The docstring is in Finnish.
  - Write `plugin.json` like keikat's, with keywords `["näyttelyt", "taide", "museot", "suomi"]`.
- [ ] **Step 4: Run the tests, expect PASS.**
- [ ] **Step 5: Commit** `nayttelyt: plugin scaffold and settings`.

### Task 3: Oulu script `nayttelyt_oulu.py`

**Files:**
- Create: `plugins/nayttelyt/skills/nayttelyt/scripts/nayttelyt_oulu.py`
- Test: `plugins/nayttelyt/skills/nayttelyt/tests/test_oulu.py`

**Interfaces:**
- Consumes: the sources and fields in `cities/oulu.md` (Task 1).
- Produces:
  - CLI: `nayttelyt_oulu.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--table]`. The defaults are today and this Sunday. The output is a JSON list of exhibition dicts (see the shared shape) or a plain text table.
  - Pure functions, which the tests use:
    - `this_week(today: date) -> tuple[date, date]`: today and the Sunday of this week
    - `overlaps(e: dict, frm: date, to: date) -> bool`
    - `is_exhibition(name: str, start: str, end: str) -> bool`
    - `merge(rows: list[dict]) -> list[dict]`
    - `fold(s: str) -> str`: copy it from keikat's `asetukset.py`

- [ ] **Step 1: Write the failing tests** (in `test_oulu.py`):
  - `test_this_week`: `this_week(date(2026,11,19))` → `(date(2026,11,19), date(2026,11,22))`. `this_week(date(2026,11,22))` → `(date(2026,11,22), date(2026,11,22))`.
  - `test_overlap`: the window is 16.11.–22.11.2026.
    - `{start:"2026-10-01", end:"2026-11-21"}` → True
    - `{start:"2026-10-01", end:"2026-11-15"}` → False
    - `{start:"2026-11-23", end:""}` → False
    - `{start:"2026-09-01", end:""}` → True. This is Review Focus 1.
    - `{start:"2026-11-20", end:"2027-03-01"}` → True. This is Review Focus 5.
    - `{permanent: True, start:"", end:""}` → True.
  - `test_is_exhibition`:
    - a one-day item, e.g. `("Opastettu kierros", "2026-11-18", "2026-11-18")` → False. This is Review Focus 2.
    - `("Valon kerrokset", "2026-11-20", "2027-03-01")` → True.
    - a multi-day item whose name contains `työpaja`, `opastus` or `kierros` → False.
  - `test_merge`: two rows, `Valon Kerrokset`/`Oulun taidemuseo` with `price:"–"`, and `valon kerrokset`/`Oulun Taidemuseo` with `price:"10 €"` and `hours:"ti–su 10–17"`. The result is 1 row with `price == "10 €"` and those hours. This is Review Focus 4.
- [ ] **Step 2: Run them, expect FAIL.** Run: `python3 -m unittest discover -s plugins/nayttelyt/skills/nayttelyt/tests -v`
- [ ] **Step 3: Implement the pure functions.**
  - `overlaps`: a permanent row is always True. An empty `start` counts as `date.min`, and an empty `end` as `date.max`.
  - `is_exhibition`:
    - a single-day item is False
    - a name matching `työpaja|opastus|opastettu|kierros|luento|esitelmä|kurssi` (case-insensitive) is False
    - everything else is True
  - `merge`: the key is `(fold(name), fold(venue))`. The first row wins, and each empty or `–` field is filled from later rows.
- [ ] **Step 4: Run the tests, expect PASS.**
- [ ] **Step 5: Implement the source readers.** Write one function per **skripti** source in `cities/oulu.md`, each `def <source>(today: date) -> list[dict]`. Follow the `fetch()`/`text()` helpers in `paikat_oulu.py`; copy them, don't import them. Add one row per venue for permanent exhibitions, using the hours and fees from the venue page.
  - `main()` runs each reader inside `try/except Exception`. On a failure it prints `<lähde>: <virhe>` to stderr. It then keeps the rows that pass `is_exhibition` (permanent rows skip that check) and `overlaps`, runs them through `merge`, and prints the result.
- [ ] **Step 6: Live check.** Run: `python3 -I plugins/nayttelyt/skills/nayttelyt/scripts/nayttelyt_oulu.py --table`
  - Expected: at least one temporary exhibition and at least one permanent row, with no one-off tours or workshops. Any source failures are reported on stderr.
- [ ] **Step 7: Commit** `nayttelyt: Oulu exhibition script`.

### Task 4: Page script `sivu.py` and template

**Files:**
- Create: `plugins/nayttelyt/skills/nayttelyt/scripts/sivu.py`
- Create: `plugins/nayttelyt/skills/nayttelyt/templates/nayttelyt.html`
- Test: `plugins/nayttelyt/skills/nayttelyt/tests/test_sivu.py`

**Interfaces:**
- Consumes: the page JSON (see the shared shape).
- Produces:
  - CLI: `sivu.py <in.json> <out.html>`. It writes the HTML and prints the markdown table to stdout. On invalid input it exits 1 and names the bad rows.
  - Pure functions:
    - `tags(e: dict, frm: date, today: date) -> list[str]`: tags in this order: `Uusi`, `Päättyy pian`, `Pysyvä`
    - `sort_key(e: dict) -> tuple`
    - `date_text(e: dict, today: date) -> str`
    - `md_table(data: dict) -> str`
  - Each exhibition in the page JSON gets a `tags` list before it goes into the template.

- [ ] **Step 1: Write the failing tests:**
  - `test_tags`: `frm = date(2026,11,16)`, `today = date(2026,11,16)`.
    - `start 2026-11-20` → `["Uusi"]`
    - `start 2026-11-23` → `[]`
    - `end 2026-11-21` → `["Päättyy pian"]`
    - `end 2026-11-30` → `[]`
    - `permanent` → `["Pysyvä"]`
  - `test_tags_future_window`: `frm = date(2026,12,1)`, `today = date(2026,11,16)`, `start 2026-12-03` → contains `"Uusi"`. This is Review Focus 3.
  - `test_sort`: with the rows [plain started 1.10., permanent, closing soon, new], sorting by `sort_key` gives [new, closing soon, plain, permanent].
  - `test_date_text`: `today = 2026-11-16`.
    - `20.11.2026–1.3.2027` → `"20.11.–1.3.2027"`
    - `1.10.–` with an empty end → `"1.10.–"`. This is Review Focus 1.
    - a permanent row → `"Pysyvä"`
    - `1.10.–21.11.2026` → `"1.10.–21.11."`
  - `test_md_table`: the header line equals `| Tagit | Näyttely | Paikka | Ajalla | Aukioloajat | Hinta | Linkki |`. A row with `url` contains `[Linkki](https://`. A row with an empty `url` has `–` in the last column.
  - `test_validation`: a row without `venue`, or with `start: "20.11.2026"`, makes `main()` return 1.
- [ ] **Step 2: Run them, expect FAIL.**
- [ ] **Step 3: Implement.** Start from `plugins/keikat/skills/keikat/scripts/sivu.py`, which already has the validation, the `</` escaping and the template filling.
  - Uusi: `frm <= start <= frm + 6 days`.
  - Päättyy pian: `today <= end <= today + 7 days`.
  - `sort_key`: rank 0 for Uusi, 1 for Päättyy pian, 2 for the rest, 3 for permanent; then `start`; then `name`.
  - `date_text`: the year is shown only when it is not the year of `today`.
- [ ] **Step 4: Run the tests, expect PASS.**
- [ ] **Step 5: Template.** Copy `plugins/keikat/skills/keikat/templates/keikat.html` and adapt it. Keep its theming, phone layout, `__TITLE__`/`__DATA__` placeholders and search.
  - Remove the max-price, unpriced and sold-out controls.
  - Add `vain ilmaiset` (free only: `price` matches `/^\s*(ilmai|vapaa pääsy)/i`) and `vain uudet` (only rows whose `tags` include `Uusi`).
  - Cards show tag badges, name, venue, date text, hours, price, the note, and a `Linkki` button.
  - The page uses the Python-computed `tags` and order. It does not recompute them.
- [ ] **Step 6: Visual check.** Write a sample JSON with one row of each kind to the scratchpad. Run `sivu.py` and open the HTML in the browser pane. Check desktop and mobile width, light and dark modes, and that every filter works.
- [ ] **Step 7: Commit** `nayttelyt: page script and template`.

### Task 5: SKILL.md and README

**Files:**
- Create: `plugins/nayttelyt/skills/nayttelyt/SKILL.md`
- Modify: `plugins/nayttelyt/skills/nayttelyt/cities/oulu.md`. Fill in `## Skriptit`.
- Modify: `README.md`. Add a plugin table row, a `## nayttelyt` usage section, a sources table, the install line and the structure tree.

**Interfaces:**
- Consumes: the CLIs from Tasks 2–4, exactly as written in their Interfaces blocks.

- [ ] **Step 1: Write `SKILL.md`** in Finnish, modelled on keikat's `SKILL.md`. Frontmatter: `name: nayttelyt`, a description with the trigger phrases ("mitä näyttelyitä Oulussa", "näyttelyt tällä viikolla", "/nayttelyt"), and `argument-hint: "[kaupunki] [viikko|1kk–12kk] | asetukset …"`.
  - Supported cities table: Oulu only, plus one sentence that the other 16 keikat cities are coming.
  - The steps:
    1. Run `asetukset.py`.
    2. Turn the argument into `--from`/`--to`: the default runs from today to Sunday, `Nkk` runs to today + N months, and a free-form month uses its own days. With the default window, the page JSON `range` still shows the whole week, Monday–Sunday (e.g. `16.–22.11.2026`).
    3. Run `nayttelyt_oulu.py`.
    4. Fill gaps with web search from the **haku** sources in `cities/oulu.md`.
    5. Merge, and drop one-off events.
    6. Write `nayttelyt-oulu.json` and run `sivu.py`. Print its markdown table and one summary line.
    7. Publish following keikat's step 6 rule, with title `Näyttelyt Oulussa` and `icon: "image"`.
  - A truthfulness section, as in keikat.
- [ ] **Step 2: Check.** `grep -n "nayttelyt_oulu.py\|sivu.py\|asetukset.py" SKILL.md`. Every option it uses must exist in Tasks 2–4: `--from`, `--to`, `--table`, `--aikavali`, `--kaupunki`, `--nollaa`.
- [ ] **Step 3: Commit** `nayttelyt: skill instructions and README`.

### Task 6: End-to-end run

- [ ] **Step 1:** Run all tests: `python3 -m unittest discover -s plugins/nayttelyt/skills/nayttelyt/tests -v`. Expected: all pass.
- [ ] **Step 2:** Link the skill (`ln -s "$PWD/plugins/nayttelyt/skills/nayttelyt" ~/.claude/skills/nayttelyt`) and run `/nayttelyt` in a new session. Expected: a table titled `Näyttelyt Oulussa 16.–22.11.2026`, the Uusi, Päättyy pian and Pysyvä tags where they apply, and a published page link.
- [ ] **Step 3:** Run `/nayttelyt joulukuussa`. Expected: the title range is `1.–31.12.2026`, and Uusi marks exhibitions that open 1.–7.12.
- [ ] **Step 4:** Remove the symlink if the user doesn't want it kept. Fix anything that failed, re-run, and commit.
