# `/nayttelyt` 1.1.0: Helsinki

Date: 2026-11-16. Status: waiting for approval (builder check done).

## Intent

`/nayttelyt` 1.0.0 supports only Oulu. Other cities are added **one at a time**, each with its
own researched sources, because a shared museums-only source would miss most of what a city
has. Helsinki goes first. It has many private galleries, and they matter as much as the museums.

## Goals

- `/nayttelyt Helsinki` (inflected forms too: "Helsingissä") works like Oulu: a terminal table and
  a web page with exhibitions open in the window, with hours and prices where known, tagged
  Uusi / Päättyy pian / Pysyvä.
- Covers museums (from museot.fi) **and** galleries (from Linked Events), including the
  galleries on the stadissa.fi list.
- Version 1.1.0 of the plugin.

## Non-goals

- Other cities (Espoo, Tampere, ...). Each one gets its own round later.
- Scraping individual gallery websites.
- Public art, outdoor works, online-only exhibitions.
- Changes to the page template or `sivu.py`.

## Anti-goals

- Turning off TLS certificate checking to read museot.fi.
- Espoo/Vantaa library shows or one-day events (tours, workshops, family days) in the Helsinki list.
- Made-up opening hours or prices. Unknown is `–`.

## Approaches

1. **Linked Events + museot.fi as scripts, stadissa.fi gallery list as a checklist** (chosen).
   Both script sources are structured and fetched over plain HTTP. Linked Events already powers
   keikat in Helsinki. The stadissa list goes into `cities/helsinki.md` as the gallery checklist
   with websites; web search fills only the gaps. Same shape as Oulu.
2. museot.fi + a scraper per gallery website (20 sites). Dropped: 20 different layouts that
   break one by one.
3. museot.fi as script, galleries by web search on every run. Dropped: slow and gives
   different results each run.

## Sources (checked 2026-11-16)

### 1. Linked Events: **script**

`https://api.hel.fi/linkedevents/v1/event/?keyword=yso:p5121&division=helsinki&start=<from>&end=<to>&include=location&page_size=100`
(follow `meta.next`; keikat's `linkedevents.py` `fetch_events` does exactly this).

- `yso:p5121` = "näyttelyt". Without `division`, 154 events for 16.–22.11.; with
  `division=helsinki` 136. The unfiltered result includes Espoo libraries (Sello, Tapiola,
  Entresse), so the filter is required.
- Seen venues: Mimosa Galleria, Oodi, Suomenlinna-museo, Galleria GAo ShAn, TakeMeHome-Galleria,
  Helsinki Contemporary, Galleria Huuto, Galerie Forsblom, HAM, Hippolyte, Forum Box, MUU,
  Teatterimuseo, Lastentarhamuseo, community houses.
- Fields: `name.fi`, `start_time`/`end_time` (UTC, convert to Europe/Helsinki like Oulu),
  `location.name.fi`, `info_url.fi` (exhibition page, e.g. muu.fi), `offers[0].is_free` / `price`,
  `super_event_type` (recurring/umbrella events; some exhibitions appear as super events, e.g.
  "Mari Paikkari: Before Us").
- About 40 of 136 are one-day events (family days, workshops): drop with the same rule as Oulu
  (start day == end day, plus the name noise filter).
- **Venue rule (decided):** keep Oodi and the city cultural centres with gallery spaces (Stoa,
  Malmitalo, Caisa, Kanneltalo, Annantalo, and similar such as Vuotalo and
  Savoy). Drop branch libraries and residents' / community houses (e.g. "Stadin
  yhteisötalo ..."). Same idea as Oulu, where only the central library stays. The builder keeps
  an explicit allow list of cultural centres and drops other venues whose name contains
  `kirjasto` (except Oodi) or `yhteisötalo` / `asukastalo`.
- Link fallback when `info_url` is empty: `https://tapahtumat.hel.fi/fi/events/<id>`
  (builder: confirm the URL form).

### 2. museot.fi exhibition calendar: **script**

`https://museot.fi/nayttelykalenteri/index.php?maakunta_id=<Uusimaa id>&nayttelyhaku=1&kaikki=1`

- Static HTML (no JS needed). Region filter `maakunta_id` (Pirkanmaa = 6; Uusimaa id: read from
  the `<select id="maakunta_id">`). `kaikki=1` returns all results on one page. There is no
  working city filter in the URL; keep cards whose city is `Helsinki`.
- Card: `a[href*="nayttely_id="]` with type, name, short text, `Museum, City`, and
  `d.m.yyyy – d.m.yyyy` (open end = long-running, treat as permanent).
- Museum page `/museohaku/index.php?museo_id=<id>` (linked from the exhibition page) has
  "Pääsymaksut" and "Aukioloajat" per weekday. Use it for hours and price per museum, fetched
  once per museum.
- **TLS:** museot.fi sends only its leaf certificate (issuer Telia RSA DV CA v4), so curl and
  Python reject it. Fix: commit the intermediate as a PEM file in the skill
  (`http://cps.trust.telia.com/teliarsadvcav4.cer`, DER, convert once), and load it into an
  `ssl.create_default_context()` with `load_verify_locations`. Verification stays on.
- Repeats exist (same exhibition listed under two venue names, e.g. Tiima / Tietomaa in Oulu),
  and online exhibitions (`Verkkonäyttely`) must be dropped.
- robots.txt and terms of use were **not** checked (TLS blocked it). Builder: check both once
  the TLS fix works; if scraping is disallowed, stop and report.

### 3. stadissa.fi gallery list: **city file only**

`https://www.stadissa.fi/paikat/4134/art-galleries-in-helsinki-taidegalleriat-helsingissa`
lists 20 galleries (name, address, website), no exhibitions or dates. It goes into
`cities/helsinki.md` as the gallery checklist. In step 3 (search), galleries on this list that
Linked Events did not return are looked up on their own websites, every run, in **one** batched
web-fetch agent call (same pattern as Oulu's **haku** sources). Only the gaps are fetched, which
keeps runs short; this differs from approach 3, where every gallery came from search. (My call.)

## Identification

The new script names itself honestly, like elokuvat since bb1c0db:
`User-Agent: nayttelyt-skill/1.1 (+https://github.com/juusimaa/claude-skills)`. If `fetch` is
moved to a shared helper, Oulu gets the same header (no behaviour change expected; the builder
confirms Oulu's sources still answer). (My call.)

## Design

- New `scripts/nayttelyt_helsinki.py`, same CLI and output as `nayttelyt_oulu.py`
  (`--from`, `--to`, `--table`, JSON rows with the same fields). Readers: `linkedevents`,
  `museot`, `pysyvat` (permanent rows written by hand, e.g. Ateneum/Kiasma/Kansallismuseo
  if museot.fi lacks them; builder decides after seeing the data).
- Shared helpers (`fetch`, `text`, `fold`, `overlaps`, `merge`, `row` ...) are currently inside
  `nayttelyt_oulu.py`. Builder's call: import them from the Oulu module or move them to a
  small shared module; don't copy them.
- Merge rows from both sources by folded name + venue (as Oulu), preferring the row with hours,
  price and link. Venue names differ between sources (e.g. "Helsingin taidemuseo HAM" vs "HAM"),
  so a small alias map is likely needed.
- New `cities/helsinki.md` in the Oulu format: script, sources, permanent exhibitions with
  hours and prices, the gallery checklist, pitfalls. `asetukset.py` picks up the city from the
  file title automatically.
- `SKILL.md`: Helsinki in the supported-cities table and description; step 2 runs the city's
  script (generic, not Oulu-only); remove Helsinki from the "not yet" list.
- Tests: `tests/test_helsinki.py` with fixture-based checks of the parsing and filters
  (Espoo dropped, one-day dropped, open end = permanent, merge across sources). No live
  network in tests.
- Version: `plugin.json` 1.1.0, `CHANGELOG.md` entry, README version column and "Oulu for now"
  text, marketplace description if it names cities.

## Left to the builder

- The exact Uusimaa `maakunta_id`, museot.fi card regex, and the museum-page parsing.
- Whether super events and their sub-events duplicate each other in Linked Events, and how to
  keep one row.
- The venue alias map and the handwritten permanent rows.
- Helper sharing between the city scripts.
