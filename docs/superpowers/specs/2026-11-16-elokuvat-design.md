# `/elokuvat` — cinema showtimes in Finnish cities

Date: 2026-11-16. Status: waiting for approval.

## Intent

A sibling of `/nayttelyt` and `/keikat`. The user has two questions: **"what's on tonight?"**
(picking a showing now) and **"what's on in cinemas this week?"** (an overview). Finnkino is a
must: without its showtimes the skill is useless. The result is a terminal table and a
filterable web page, like nayttelyt.

## Goals

- `/elokuvat` answers "what's on tonight" in the chosen city: every screening today that has
  not started yet, sorted by time, with cinema, auditorium and a booking link.
- `/elokuvat viikko` answers "what's on this week": one row per film, with its showtimes
  grouped by cinema and day, from today to Sunday.
- **All cities in the first draft.** Any city that elokuviin.com has a page for (about 160,
  including all 17 keikat cities) is supported. No per-city files.
- Finnkino, independent cinemas (e.g. Star and Oulun Elokuvakeskus in Oulu) and other chains
  all come from the same source.
- A **Uusi** (new) tag for films whose Finnish premiere falls within the last 7 days or later
  in the window.
- The same `asetukset` (settings) subcommand as nayttelyt: saves the default city and window.

## Non-goals

- Ticket prices and seat availability. Neither source has them, and Finnkino's own pages
  can't be read by a script.
- Windows longer than this week. elokuviin.com lists only today to Sunday, so `Nkk` and
  "joulukuussa" are not supported. A request for those gets one sentence saying so.
- Upcoming premieres beyond this week ("tulossa"), reviews and recommendations.
- Streaming.

## Anti-goals

- Getting around Finnkino's bot protection. Finnkino's XML feed (`finnkino.fi/xml/`) answers
  scripts with a Cloudflare challenge (403). It is not used, and no script tries other routes
  to it.
- Reading elokuviin.com's `/api/`, which its robots.txt disallows. Only the public city pages
  are read.
- Made-up showtimes. A source that fails is named. Its gap is never filled with guessed times.
- Changing keikat or nayttelyt.

## Constraints

- Same as nayttelyt: lowercase ASCII skill name (`elokuvat`), its own plugin, code copied rather
  than shared between plugins, Python 3 standard library only, plain HTTP with no browser,
  `python3 -I`. Finnish SKILL.md and output, English README and marketplace entry, Apache-2.0.
- Both sources are privately run websites, not official feeds. Their markup can change at any
  time. Tests run against saved copies of the pages, so a break shows up as a failed run with
  the source named, not as wrong data.

## Sources (verified 2026-11-16)

1. **elokuviin.com/<city>** (main source, showtimes). A Next.js page whose `__NEXT_DATA__`
   script holds JSON under `props.pageProps`:
   - `screenings[]`: `startsAt` (UTC ISO, e.g. `2026-11-22T18:00:00.000Z`), `movieId`,
     `cinemaId`, `auditorium`, `bookingLink` (for Finnkino a direct
     `finnkino.fi/liput/valitse-paikat/?showtimeId=…` link), `festival`, `outdoor`.
   - `movies{id: …}`: `titleFI`, `title` (original), `runtime` (min, may be null), `genres[].name`,
     `year`, `director`, `imdbRating`, `slug`.
   - `screeningCinemas{id: …}`: `name`, `website`.
   - `cityObject`: `name`, `nameInesive` (e.g. `Oulussa`, used in the title).
   Oulu today: 3 cinemas, 31 films, 139 screenings from Monday to Sunday. Slugs are the city
   name in lowercase; names with ä/ö redirect (308) from the ASCII form, so following redirects
   is enough. An unknown city should give a 404.
   Known quirk: Friday–Sunday have far fewer screenings than Monday–Thursday (5–6 against ~30
   a day), because cinemas publish the weekend late. The output says so.
2. **nytleffaan.fi/paikkakunta/<city>/** (premiere dates and fallback film list). Plain HTML.
   Each film is a `.movie-card` with `<h3>` title (Finnish), `.movie-card-premiere-date`
   (`30.10.2026`), an age rating icon (`data/icons/7.png` → `7`) and a link
   (`/elokuva/<slug>/<city>`). No showtimes. City slugs work in ASCII (`jyvaskyla`) and with
   ä/ö. Not every elokuviin city may have a page here; a missing one is a warning, not an error. It also lists films that premiere later (e.g.
   27.11.), which are dropped unless they premiere within the window.

## Approaches considered

- **A. elokuviin.com for showtimes, nytleffaan.fi for premiere dates and age ratings
  (chosen).** One script reads both and joins them by Finnish title. nytleffaan also acts as a
  fallback film list (without times) if elokuviin breaks. It costs one small extra parser.
- B. elokuviin.com only. The smallest version, but there would be no premiere dates (so no
  Uusi tag) and nothing to fall back on.
- C. Finnkino's XML feed plus cinemas' own pages. Ruled out: the feed is behind Cloudflare's
  bot check for scripts.

The user picked A.

## Design (decided)

### Layout

```
plugins/elokuvat/
├── .claude-plugin/plugin.json
└── skills/elokuvat/
    ├── SKILL.md
    ├── scripts/
    │   ├── asetukset.py   # copy of nayttelyt's, ~/.config/elokuvat/, default Oulu + tänään
    │   ├── elokuvat.py    # city -> JSON (or --table) from both sources
    │   └── sivu.py        # JSON -> HTML from the template + markdown table
    ├── templates/elokuvat.html
    └── tests/             # unittest against saved pages, like nayttelyt's
```

Added to `.claude-plugin/marketplace.json` and `README.md`.

### Arguments and settings

- City anywhere in the argument, inflected forms too ("oulussa" → Oulu, "Jyväskylässä" →
  Jyväskylä). *(My call.)* The skill turns it into the base form. The script makes the slug
  (lowercase, spaces → `-`) and lets the redirect handle ä/ö. A 404 means "elokuviin.com has no
  page for this city": say so in one sentence and stop.
- Window: `tänään` ("tonight", the default) or `viikko` (today to Sunday). Words like "tänä
  iltana", "nyt" and "huomenna" are understood; "huomenna" (tomorrow) is a one-day window.
  *(My call: the factory default is `tänään`, since "tonight" is the more urgent question.)*
- `asetukset Oulu viikko` saves defaults, as in nayttelyt. *(My call.)* `asetukset.py` stops
  checking the city against `cities/*.md` (there are none). It stores the base form it is
  given, and the city is checked when the fetch runs.

### Script

*(My call, after the builder check.)* The script has no window flag: `elokuvat.py --city Oulu
[--table]` always prints the **whole week** (today to Sunday), because one fetch gives it and the
page needs all of it. The window only changes the terminal table: `sivu.py in.json out.html
--tanaan | --huomenna | --viikko` writes the same full-week page every time and prints the
markdown table for the chosen window. The skill runs the script once.

The JSON:

```
{"city": "Oulu", "title": "Elokuvat Oulussa", "generated": "2026-11-16T17:40",
 "screenings": [{"start": "2026-11-16T19:40", "film": "Lapin sota", "cinema": "Finnkino Plaza",
                 "auditorium": "Sali 1", "url": "https://www.finnkino.fi/liput/…"}],
 "films": [{"title": "Lapin sota", "original": "…", "runtime": 158, "genres": ["Draama", "Sota"],
            "premiere": "2026-10-23", "age": "12", "url": "…", "tags": ["Uusi"]}],
 "sources": [{"name": "elokuviin.com", "url": "…", "ok": true}, …],
 "warnings": ["…"]}
```

- Times are converted from UTC to Europe/Helsinki (`zoneinfo`).
- "Tonight" = today's screenings that start at or after the current time.
- Each source is fetched separately. A failed source becomes a warning on stderr and
  `ok: false`, and the run continues. If elokuviin fails, `screenings` is empty and `films`
  comes from nytleffaan, and the output says showtimes are missing.
- `titleFI` is sometimes null (2 of 31 films in Oulu, 23 of 81 in Helsinki); fall back to
  `title`.
- Versions: elokuviin.com has one movie per film. Checked in Oulu and Helsinki: no dubbed,
  3D or language variants appear as separate movies, and screenings carry no language field.
  So one row per movie, with no title normalising beyond the join key.
- Join by folded Finnish title (lowercase, no diacritics, punctuation removed). A film without
  a match keeps empty `premiere` and `age`.
- **Uusi**: premiere within the 7 days before today, or on any day in the window.

### Output

- Tonight, titled e.g. `Elokuvat Oulussa tänään 16.11.2026`:
  `| Klo | Elokuva | Teatteri | Sali | Kesto | Ikäraja | Liput |`, sorted by time. A film's
  title carries `(Uusi)` when tagged.
- Week, titled e.g. `Elokuvat Oulussa 16.–22.11.2026`:
  `| Tagit | Elokuva | Kesto | Lajityyppi | Näytökset | Liput |`, one row per film. Näytökset is
  compact, e.g. `Plaza: ma 17.15 19.40, ti 20.45 · Star: ke 18.30`. Ordering: Uusi first, then
  by number of screenings.
- One summary line afterwards: the number of films and screenings, which sources worked, and
  the weekend note when it applies.
- Web page: `sivu.py` fills `templates/elokuvat.html`. *(My call.)* The page always holds the
  whole week (one fetch gives it), with day chips (Tänään selected by default, ma–su), a cinema
  filter, text search and "Uusi only". A screening's time links to its booking page.
  *(My call.)* The page is a snapshot, so its script compares each screening with the
  viewer's own clock when the page opens: screenings already started are dimmed, not hidden.
  The Tänään chip means the viewer's today, so opening Tuesday's page on Wednesday selects
  Wednesday. One stable
  Artifact per city (`Elokuvat <Oulussa>`), icon `"film"`, as in nayttelyt.

## Left to the builder

- The exact HTML of the page template (start from a copy of nayttelyt's; it must work at phone
  width and in light and dark modes).
- Short cinema names in the week table (e.g. "Finnkino Plaza" → "Plaza").
- Handling festival and outdoor screenings (`festival`, `outdoor`): show them, with the
  festival name in a note.
- Wording of SKILL.md, README and marketplace text.
