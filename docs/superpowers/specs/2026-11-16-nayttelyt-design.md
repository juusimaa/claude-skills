# `/nayttelyt` — exhibitions in Finnish cities

Date: 2026-11-16. Status: waiting for approval.

## Intent

A sibling of `/keikat`. The user wants a quick view of which exhibitions are open in a city
right now, and especially what is **new this week**. The default answer is "what's open this
week". A longer window can be given the same way as in keikat. The result is a terminal table
and a filterable web page, like keikat.

## Goals

- `/nayttelyt` lists every exhibition that is open on at least one day of the current week
  (Monday–Sunday, the week of today).
- Same arguments as keikat: a city anywhere in the command (inflected forms too), `Nkk` (1–12
  months from today), or a free-form window ("joulukuussa", meaning "in December"), plus an
  `asetukset` (settings) subcommand that saves the default city and window.
- Same 17 cities as keikat. **First iteration: Oulu only.** For the other cities, say in one
  sentence that they are not supported yet, list the supported ones, and stop. That is the
  same thing keikat does for an unknown city.
- Every row has: name, venue, date range, opening hours, entry fee and a link.
- Tags:
  - **Uusi** (new): the exhibition opens during the first 7 days of the window. With the default
    window, that is this week (see Time window).
  - **Päättyy pian** (closing soon): it closes within 7 days of today.
  - **Pysyvä** (permanent): a permanent collection or exhibition, with no end date.
- The web page has filters: text search, venue, "free only", "new only".
- Scope: art, photography, design, crafts, history, science and museum exhibitions, both
  temporary and permanent, in museums, galleries, libraries and other spaces.

## Non-goals

- Films, live music, theatre and other performances. One-off events at a museum (guided tours,
  workshops, talks) are left out too. The unit is an exhibition, not an event.
- Cities other than Oulu in this iteration. They are added one per change later, each with its
  own `cities/<city>.md`.
- Ticket availability or "sold out" (not relevant to exhibitions).
- Reviews and recommendations.

## Anti-goals

- Made-up opening hours or fees. An unknown value is written as `–`.
- A list where one museum's events calendar shows up as dozens of rows (guided tours, kids'
  workshops). That would bury the exhibitions.
- Breaking or changing keikat. This plugin does not touch `plugins/keikat/`.

## Constraints

- Skill names must be lowercase ASCII, so the command is `/nayttelyt` (not `/näyttelyt`).
  Folders use `nayttelyt` too.
- Plugins are installed one by one and cannot read each other's files. Anything reused from
  keikat is copied.
- Scripts use only the Python 3 standard library and plain HTTP (no browser), run with
  `python3 -I`, like keikat.
- `SKILL.md` and user-facing output are in Finnish, like keikat. README and the marketplace
  entry are in English.
- License Apache-2.0, like the rest of the repository.

## Approaches considered

- **A. Separate `nayttelyt` plugin, modelled on keikat (chosen).** Its own SKILL.md, city
  file, settings script, page script and template. It copies about 150 lines from keikat. Users
  can install it on its own, and its defaults are stored apart from keikat's.
- B. A second skill inside the keikat plugin. No copied code, but the plugin name "keikat"
  (gigs) would no longer fit, a rename would break existing installs, and the two skills would
  still need separate defaults.
- C. SKILL.md only, everything found with web search on each run. Fastest to build, but slow
  and inconsistent at run time. Opening hours and fees would differ from run to run, which is
  why keikat moved to scripts.

The user picked A.

## Design (decided)

### Layout

```
plugins/nayttelyt/
├── .claude-plugin/plugin.json
└── skills/nayttelyt/
    ├── SKILL.md
    ├── cities/oulu.md            # Oulu sources, venues and pitfalls
    ├── scripts/
    │   ├── asetukset.py          # copy of keikat's, config dir ~/.config/nayttelyt/, factory default Oulu + this week
    │   ├── nayttelyt_oulu.py     # Oulu sources -> JSON / --table
    │   └── sivu.py               # JSON -> HTML from the template
    └── templates/nayttelyt.html
```

The plugin is added to `.claude-plugin/marketplace.json` and documented in `README.md`
(plugin table, usage, sources, structure).

### Time window

- The default is the current week, Monday to Sunday. It is stored in settings as
  `"viikko"` (week), alongside keikat's `1`–`12` months. `asetukset 3kk` changes the default
  to 3 months, and `asetukset viikko` changes it back.
- *(Builder's call.)* The window is a pair of dates, and nothing in it is earlier than today.
  The default runs from today to Sunday, but the title still shows the whole week
  (Monday–Sunday), so a show that closed on Tuesday is not listed on Thursday. `Nkk` runs from
  today to today + N months. A free-form window such as "joulukuussa" means its own dates
  (1.–31.12.). The scripts take `--from YYYY-MM-DD --to YYYY-MM-DD` and default to today
  through this Sunday. The skill converts `Nkk` and free-form windows into those dates.
- An exhibition is included if its date range overlaps the window. Permanent exhibitions are
  always included.
- *(Builder's call.)* "Open" here means not known to be closed. A venue that is closed for a
  renovation or a season is noted in `cities/oulu.md` and skipped. Daily opening hours are
  shown as text and are not used to filter.
- *(Builder's call.)* **Uusi** marks an exhibition that opens during the first 7 days of the
  window. With the default window that means this week. With "joulukuussa" it means the first
  week of December.
- *(Builder's call.)* A temporary exhibition that has no end date announced is not permanent.
  `end` is left empty and the date shows as `20.11.–`. **Pysyvä** is used only when the source
  says the exhibition is permanent.

### Data per exhibition (script JSON and page JSON)

`name`, `venue`, `start` (ISO date or empty for permanent), `end` (ISO date or empty),
`permanent` (bool), `hours` (text, e.g. `ti–su 10–17`), `price` (text, e.g. `10 € / alennus 7 €`,
`Ilmainen`, `–`), `url`, `note` (e.g. free-entry days), `source`. Tags are computed from
`start`/`end`/`permanent` and the generation date by the page and by the skill, not stored
by sources.

### Oulu sources

1. **Oulu's events service** (tapahtumat.munoulu.fi). keikat's `paikat_oulu.py` already reads
   it through a widget JSON endpoint. The service has an exhibitions category ("Näyttelyt"),
   but it has **not yet been verified** where that category sits in the data, or whether the
   items include opening hours and fees. **Verifying this is the first step of the plan.** If
   the category can't be read reliably, the script reads the venues' own pages instead.
2. **Venue pages** for the main exhibition venues, read by the script where the page is plain
   HTML. Candidates: Oulun taidemuseo (art museum), Pohjois-Pohjanmaan museo (regional
   museum), Tietomaa (science centre), Galleria Harmaja, Taidekeskus Kulttuurivalimo/Valve
   galleries, Oulun kaupunginkirjasto (library) exhibition spaces, and the Oulu2026 (European
   Capital of Culture) programme. The builder confirms which have readable pages.
3. **Web search** for the rest, guided by `cities/oulu.md` (smaller galleries, the
   university, and Oulu2026 venues that load content with JavaScript).

Permanent exhibitions and their opening hours and fees usually come from the venue page, not
the events calendar. **Each venue gets one permanent row** (user's decision), e.g.
`Pohjois-Pohjanmaan museo – pysyvät näyttelyt`, even if the venue has several permanent displays.
The row's `note` can name the displays briefly. Library exhibitions count only when they are in
a dedicated exhibition space. Small displays in branch libraries are left out.

### Output

- Terminal table, titled e.g. `Näyttelyt Oulussa 16.–22.11.2026`:
  `| Tagit | Näyttely | Paikka | Ajalla | Aukioloajat | Hinta | Linkki |`
  (tags, exhibition, venue, dates, opening hours, fee, link). Dates are written as
  `20.11.–1.3.2027`; a permanent exhibition shows `Pysyvä`. Links use `[Linkki](https://…)`.
  After the table comes one summary line: the number of exhibitions, which sources returned
  results, and which failed.
- Web page: `sivu.py` fills `templates/nayttelyt.html`. Each card shows the tag badges, name,
  venue, date range, opening hours, fee and a link button. Filters are search, venue, free
  only and new only. Ordering: new first, then closing soon, then the rest by start date, and
  permanent last. Publish the page as an Artifact following keikat's rule: one stable page per
  city (reuse an existing `Näyttelyt <Otsikossa>` artifact, where "Otsikossa" is the city name
  in inessive case), icon `"image"`.

### Truthfulness (copied from keikat in spirit)

Unknown values are `–`. The list is never complete, and it says so once. Failed sources are
named. Past exhibitions and one-off events are removed. Duplicates across sources are merged by
name + venue.

## Left to the builder

- How exactly to read the events service's exhibitions (endpoint, category id, parsing). This
  is the plan's first step.
- Which Oulu venues get a scripted reader and which are left to web search, based on what is
  readable over plain HTTP.
- Whether the template is a modified copy of `keikat.html` or written fresh. It must work at
  phone width and in light and dark modes, like keikat's.
- The heuristic for telling exhibitions apart from one-off events in mixed sources.
- Wording of SKILL.md, the README section and the marketplace description.
