# claude-skills

My own plugins and skills for [Claude Code](https://claude.com/claude-code): a coding helper, and skills for Finnish services and places. The repository is also a Claude Code plugin marketplace.

## Plugins

| Plugin | Description | Version | License |
|---|---|---|---|
| [orchestrate](plugins/orchestrate/commands/orchestrate.md) | `/orchestrate`: the session model plans a task, and Haiku and Sonnet workers implement the subtasks in parallel. | [1.1.0](plugins/orchestrate/CHANGELOG.md) | Apache-2.0 |
| [keikat](plugins/keikat/skills/keikat/SKILL.md) | `/keikat`: music gigs in Finland's 17 largest cities, as one list with prices and ticket status, in the terminal and as a filterable web page. | [1.0.0](plugins/keikat/CHANGELOG.md) | Apache-2.0 |
| [nayttelyt](plugins/nayttelyt/skills/nayttelyt/SKILL.md) | `/nayttelyt`: exhibitions (art, photography, design, museums) open in a city this week or a chosen period, with hours, prices and tags, in the terminal and as a web page. Oulu and Helsinki for now. | [1.1.0](plugins/nayttelyt/CHANGELOG.md) | Apache-2.0 |
| [elokuvat](plugins/elokuvat/skills/elokuvat/SKILL.md) | `/elokuvat`: cinema showtimes (Finnkino and independent cinemas) in a Finnish city tonight, tomorrow or this week, with booking links, in the terminal and as a filterable web page. | [1.0.0](plugins/elokuvat/CHANGELOG.md) | Apache-2.0 |

## Installation

Add the marketplace and install the plugins you want:

```
/plugin marketplace add juusimaa/claude-skills
/plugin install orchestrate@claude-skills
/plugin install keikat@claude-skills
/plugin install nayttelyt@claude-skills
/plugin install elokuvat@claude-skills
```

Then run `/reload-plugins`.

## orchestrate

```
/orchestrate add a notifications toggle to the settings screen and write tests for it
```

The orchestrator (the session model) reads the code, shows a plan as a table (subtask, worker, files) and waits for your approval. Independent subtasks then run in parallel, and the orchestrator reviews the results, runs the tests and summarizes. Each worker runs in its own git worktree, and its changes reach your folder only after the orchestrator has reviewed them. Shared groundwork is committed first so workers can see it, and your folder must otherwise have no uncommitted changes (the orchestrator asks if it does). Workers never commit or push. If a worker fails, it is re-briefed once, and after that the orchestrator does the subtask itself.

The workers are `haiku-worker` (Haiku, low effort: mechanical changes) and `sonnet-worker` (Sonnet, medium effort: well-scoped tasks that need some judgment). When installed with the plugin they are listed as `orchestrate:haiku-worker` and `orchestrate:sonnet-worker`. If you have your own workers with the same names, the plugin's workers are preferred.

The optional progress bar needs the [savvy-progress](https://github.com/johnnyvizz/claude-kit/tree/main/plugins/savvy-progress) plugin. Without it the command works the same and leaves the bar out. For the bar, Haiku tasks are labelled `light` and Sonnet tasks `medium`; the label is only a cosmetic name for a planned row.

## keikat

The command's arguments are in Finnish (`3kk` is 3 months, `joulukuussa` is "in December").

```
/keikat          # default city and period (factory default Oulu, 1 month)
/keikat 3kk      # 1–12 months
/keikat joulukuussa
/keikat Tampere  # gigs in Tampere
/keikat Helsinki 3kk
/keikat joulukuussa Turussa

/keikat asetukset Tampere 3kk   # save defaults for plain /keikat
/keikat asetukset               # show the current defaults
/keikat asetukset nollaa        # back to the factory defaults
```

The city can be anywhere in the command. Without a city and period the saved defaults are used, and values given in the command override them for that run only. Defaults are saved in `~/.config/keikat/asetukset.json` (or `$XDG_CONFIG_HOME/keikat/`), not in the skill's folder.

Supported cities: Helsinki, Espoo, Vantaa, Tampere, Turku, Oulu, Jyväskylä, Kuopio, Lahti, Pori, Kouvola, Joensuu, Lappeenranta, Hämeenlinna, Vaasa, Seinäjoki and Rovaniemi.

The skill collects gigs from several sources, merges duplicates and leaves out anything that is not a music event. The result is a table in the terminal and a web page (a claude.ai artifact) with search by artist, venue and date, a venue filter, a price limit and a toggle to hide sold-out gigs.

Sources:

| Source | How | Prices |
|---|---|---|
| Tiketti | script (`tiketti.py`, all cities) | no, status yes |
| Ticketmaster / Lippu.fi | script (`ticketmaster.py`, the 9 cities that have a city page on Ticketmaster) | no, status yes |
| Meteli.net, Bandsintown, Resident Advisor | Claude reads them from the web | no |
| Tarkastamo, Tullisali, Tuba | script (`paikat_oulu.py`, Oulu only) | yes |
| Oulu Sinfonia | script (`paikat_oulu.py`, Oulu only) | yes |
| Oulun musiikkikeskus (Madetoja Hall, Pohjankartano Hall, etc.) | script (`paikat_oulu.py`, Oulu only) | no |
| Tullikamari (Pakkahuone, Klubi), Tavara-asema, Telakka, Vastavirta | script (`paikat_tampere.py`, Tampere only) | yes |
| Lutakko (Jelmu), Musta Kynnys | script (`paikat_jyvaskyla.py`, Jyväskylä only) | yes |
| Linked Events (the Helsinki region's open events API) | script (`linkedevents.py`, Helsinki, Espoo, Vantaa) | partly |
| Songkick, venues, ticket sellers, city calendars | the city's file `cities/<city>.md`, read with a web search | varies |

The skill works without a browser. The scripts use plain HTTP requests, and the page is built from a ready-made template (`templates/keikat.html`) by the script `sivu.py`.

### Installation without the marketplace

Clone the repository and link the skill into Claude's skills folder:

```bash
git clone https://github.com/juusimaa/claude-skills.git
ln -s "$PWD/claude-skills/plugins/keikat/skills/keikat" ~/.claude/skills/keikat
```

The scripts need only the Python 3 standard library. You can also run them directly:

```bash
python3 plugins/keikat/skills/keikat/scripts/paikat_oulu.py --months 3 --table   # Oulu only
python3 plugins/keikat/skills/keikat/scripts/paikat_tampere.py --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/paikat_jyvaskyla.py --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/linkedevents.py --city Helsinki --months 1 --table
python3 plugins/keikat/skills/keikat/scripts/tiketti.py --city Tampere --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/ticketmaster.py --city Tampere --months 3 --table
```

`asetukset.py` shows and saves the defaults (`--kaupunki`, `--kuukaudet`, `--nollaa`). The `paikat_<city>.py` scripts read the venues of one city. `tiketti.py`, `ticketmaster.py` and `linkedevents.py` take the city with `--city`.

## nayttelyt

The command's arguments are in Finnish (`viikko` is the week, `3kk` is 3 months, `joulukuussa` is "in December").

```
/nayttelyt             # default city and period (factory default Oulu, this week)
/nayttelyt 3kk         # 1–12 months from today
/nayttelyt joulukuussa
/nayttelyt Oulu viikko
/nayttelyt Helsinki    # another supported city

/nayttelyt asetukset Oulu 3kk   # save defaults for plain /nayttelyt
/nayttelyt asetukset            # show the current defaults
/nayttelyt asetukset nollaa     # back to the factory defaults
```

Defaults are saved in `~/.config/nayttelyt/asetukset.json` (or `$XDG_CONFIG_HOME/nayttelyt/`). Oulu and Helsinki are supported for now; the other cities of keikat are coming.

The skill lists the exhibitions that are open in the period, temporary and permanent, with opening hours and prices. Films and live music are left out, and so are one-off events such as guided tours and workshops. Tags:

- **Uusi** (new): opens during the first 7 days of the period.
- **Päättyy pian** (ending soon): ends within 7 days from today.
- **Pysyvä** (permanent): a permanent exhibition.

The result is a table in the terminal and a web page (a claude.ai artifact).

Sources:

| Source | How |
|---|---|
| Oulu events service (exhibitions) | script (`nayttelyt_oulu.py`) |
| Oulun taidemuseo | script (`nayttelyt_oulu.py`) |
| Kulttuuritalo Valve galleries | script (`nayttelyt_oulu.py`) |
| Venue pages (Tiima, Kotilo, libraries, galleries) | the city's file `cities/oulu.md`, read with a web search |

### Installation without the marketplace

```bash
ln -s "$PWD/claude-skills/plugins/nayttelyt/skills/nayttelyt" ~/.claude/skills/nayttelyt
```

The scripts need only the Python 3 standard library. You can also run them directly:

```bash
python3 plugins/nayttelyt/skills/nayttelyt/scripts/nayttelyt_oulu.py --from 2026-11-16 --to 2026-11-22 --table
python3 plugins/nayttelyt/skills/nayttelyt/scripts/asetukset.py --kaupunki Oulu --aikavali 3
```

`asetukset.py` shows and saves the defaults (`--kaupunki`, `--aikavali`, `--nollaa`). `sivu.py` builds the web page from a JSON file.

## elokuvat

The command's arguments are in Finnish (`tänään` is today, `huomenna` tomorrow, `viikko` the week).

```
/elokuvat                  # default city and window (factory default Oulu, tonight)
/elokuvat Helsinki viikko  # one row per film, today to Sunday
/elokuvat huomenna
/elokuvat jyväskylässä

/elokuvat asetukset Tampere viikko   # save defaults for plain /elokuvat
/elokuvat asetukset                  # show the current defaults
/elokuvat asetukset nollaa           # back to the factory defaults
```

Defaults are saved in `~/.config/elokuvat/asetukset.json` (or `$XDG_CONFIG_HOME/elokuvat/`). Any city that elokuviin.com has a page for works (about 160, including all of keikat's cities).

"Tonight" lists today's screenings that have not started yet, by time, with cinema, auditorium, running time, age rating and a booking link. "This week" has one row per film with its showtimes by cinema and day. Films that premiered in the last 7 days or premiere this week are tagged **Uusi** (new). The web page always holds the whole week, with day buttons and filters. Prices and seat availability are not available.

Sources:

| Source | What | How |
|---|---|---|
| [elokuviin.com](https://elokuviin.com) | showtimes for Finnkino and other cinemas | script (`elokuvat.py`), reads the public city page |
| [nytleffaan.fi](https://nytleffaan.fi) | Finnish premiere dates and age ratings | script (`elokuvat.py`) |

Finnkino's own XML feed answers scripts with a bot check, so it is not used.

### Installation without the marketplace

```bash
ln -s "$PWD/claude-skills/plugins/elokuvat/skills/elokuvat" ~/.claude/skills/elokuvat
```

The scripts need only the Python 3 standard library (3.9+ for `zoneinfo`). You can also run them directly:

```bash
python3 plugins/elokuvat/skills/elokuvat/scripts/elokuvat.py --city Oulu > oulu.json
python3 plugins/elokuvat/skills/elokuvat/scripts/sivu.py oulu.json oulu.html --tanaan
```

`asetukset.py` shows and saves the defaults (`--kaupunki`, `--aikavali`, `--nollaa`).

## Structure

```
.claude-plugin/marketplace.json     # lists the plugins
plugins/
├── orchestrate/
│   ├── .claude-plugin/plugin.json
│   ├── commands/orchestrate.md     # /orchestrate
│   └── agents/                     # haiku-worker, sonnet-worker
├── keikat/
│   ├── .claude-plugin/plugin.json
│   └── skills/keikat/
│       ├── SKILL.md                # instructions for Claude
│       ├── cities/                 # per-city sources
│       ├── scripts/                # data fetching and page building
│       └── templates/              # web page template
├── nayttelyt/
│   ├── .claude-plugin/plugin.json
│   └── skills/nayttelyt/
│       ├── SKILL.md                # instructions for Claude
│       ├── cities/                 # per-city sources
│       ├── scripts/                # data fetching and page building
│       └── templates/              # web page template
└── elokuvat/
    ├── .claude-plugin/plugin.json
    └── skills/elokuvat/
        ├── SKILL.md                # instructions for Claude
        ├── scripts/                # data fetching and page building
        └── templates/              # web page template
```

Each plugin lives in its own folder `plugins/<name>/` and is listed in `.claude-plugin/marketplace.json`. A skill's folder has a `SKILL.md` at its root.

## Notes

The scripts read public event pages, and the pages' structure may change. If a source stops working, the script says so and the other sources keep working. The data for Oulun musiikkikeskus comes from the city's events service calendar embed, which is not a documented API.

## License

The whole repository is under the [Apache-2.0](LICENSE) license. You may use, modify and share the plugins, including commercially, under the license's terms. The copyright notice is in [NOTICE](NOTICE).

Versions before this change (the earlier commits of the `keikat` plugin) were released under PolyForm Noncommercial 1.0.0.

Copyright © 2026 Jouni Uusimaa
