# claude-skills

My own plugins and skills for [Claude Code](https://claude.com/claude-code): a coding helper, and skills for Finnish services and places. The repository is also a Claude Code plugin marketplace.

## Plugins

| Plugin | Description | License |
|---|---|---|
| [orchestrate](plugins/orchestrate/commands/orchestrate.md) | `/orchestrate`: the session model plans a task, and Haiku and Sonnet workers implement the subtasks in parallel. | Apache-2.0 |
| [keikat](plugins/keikat/skills/keikat/SKILL.md) | `/keikat`: music gigs in Finland's 17 largest cities, as one list with prices and ticket status, in the terminal and as a filterable web page. | Apache-2.0 |

## Installation

Add the marketplace and install the plugins you want:

```
/plugin marketplace add juusimaa/claude-skills
/plugin install orchestrate@claude-skills
/plugin install keikat@claude-skills
```

Then run `/reload-plugins`.

## orchestrate

```
/orchestrate add a notifications toggle to the settings screen and write tests for it
```

The orchestrator (the session model) reads the code, shows a plan as a table (subtask, worker, files) and waits for your approval. Independent subtasks then run in parallel, and the orchestrator reviews the results, runs the tests and summarizes. Workers never commit or push. If a worker fails, it is re-briefed once, and after that the orchestrator does the subtask itself.

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

## Structure

```
.claude-plugin/marketplace.json     # lists the plugins
plugins/
├── orchestrate/
│   ├── .claude-plugin/plugin.json
│   ├── commands/orchestrate.md     # /orchestrate
│   └── agents/                     # haiku-worker, sonnet-worker
└── keikat/
    ├── .claude-plugin/plugin.json
    └── skills/keikat/
        ├── SKILL.md                # instructions for Claude
        ├── cities/                 # per-city sources
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
