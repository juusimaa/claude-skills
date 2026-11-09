# claude-skills

Omia pluginejaan ja skilliään [Claude Codelle](https://claude.com/claude-code): koodausapuri ja suomalaisiin palveluihin ja paikkakuntiin liittyviä skillejä. Repo on samalla Claude Coden plugin-marketplace.

## Pluginit

| Plugin | Kuvaus | Lisenssi |
|---|---|---|
| [orchestrate](plugins/orchestrate/commands/orchestrate.md) | `/orchestrate`: istunnon malli suunnittelee tehtävän, ja Haiku- ja Sonnet-työntekijät toteuttavat osatehtävät rinnakkain. | Apache-2.0 |
| [keikat](plugins/keikat/skills/keikat/SKILL.md) | `/keikat`: Suomen 17 suurimman kaupungin musiikkikeikat yhdeksi listaksi hintoineen ja lipputilanteineen, terminaaliin ja suodatettavalle web-sivulle. | Apache-2.0 |

## Asennus

Lisää marketplace ja asenna haluamasi plugin:

```
/plugin marketplace add juusimaa/claude-skills
/plugin install orchestrate@claude-skills
/plugin install keikat@claude-skills
```

Lataa sen jälkeen `/reload-plugins`.

## orchestrate

```
/orchestrate lisää asetusnäyttöön ilmoitusten kytkin ja kirjoita siitä testit
```

Orkestroija (istunnon malli) lukee koodin, näyttää suunnitelman taulukkona (osatehtävä, työntekijä, tiedostot) ja odottaa hyväksyntääsi. Sen jälkeen riippumattomat osatehtävät ajetaan rinnakkain, ja orkestroija tarkastaa tulokset, ajaa testit ja tekee yhteenvedon. Työntekijät eivät koskaan commitoi tai pushaa. Jos työntekijä epäonnistuu, sille annetaan uusi ohje kerran, ja sen jälkeen orkestroija tekee osatehtävän itse.

Työntekijät ovat `haiku-worker` (Haiku, matala työmäärä: mekaaniset muutokset) ja `sonnet-worker` (Sonnet, keskitaso: rajatut tehtävät, jotka vaativat harkintaa). Pluginin kanssa ne näkyvät nimillä `orchestrate:haiku-worker` ja `orchestrate:sonnet-worker`. Jos sinulla on omat samannimiset työntekijät, pluginin työntekijät ovat etusijalla.

Valinnainen etenemispalkki vaatii [savvy-progress](https://github.com/johnnyvizz/claude-kit/tree/main/plugins/savvy-progress)-pluginin. Ilman sitä komento toimii samoin ja jättää palkin pois. Palkin kautta Haiku-tehtävät merkitään nimellä `light` ja Sonnet-tehtävät nimellä `medium`; merkintä on pelkkä kosmeettinen nimi suunnitellulle riville.

## keikat

```
/keikat          # oletuskaupunki ja -aikaväli (tehdasasetus Oulu, 1 kk)
/keikat 3kk      # 1–12 kuukautta
/keikat joulukuussa
/keikat Tampere  # Tampereen keikat
/keikat Helsinki 3kk
/keikat joulukuussa Turussa

/keikat asetukset Tampere 3kk   # tallenna oletukset pelkälle /keikat-komennolle
/keikat asetukset               # näytä nykyiset oletukset
/keikat asetukset nollaa        # takaisin tehdasasetuksiin
```

Kaupunki voi olla missä kohtaa komentoa tahansa. Ilman kaupunkia ja aikaväliä käytetään tallennettuja oletuksia, ja komennon omat arvot ohittavat ne vain sillä kertaa. Oletukset tallentuvat tiedostoon `~/.config/keikat/asetukset.json` (tai `$XDG_CONFIG_HOME/keikat/`), eivät skillin kansioon.

Tuetut kaupungit: Helsinki, Espoo, Vantaa, Tampere, Turku, Oulu, Jyväskylä, Kuopio, Lahti, Pori, Kouvola, Joensuu, Lappeenranta, Hämeenlinna, Vaasa, Seinäjoki ja Rovaniemi.

Skilli kokoaa keikat useasta lähteestä, yhdistää kaksoiskappaleet ja jättää pois muut kuin musiikkitapahtumat. Tulos tulee taulukkona terminaaliin ja julkaistaan web-sivuna (claude.ai-artifact), jolla on haku artistin, paikan ja päivän mukaan, paikkasuodatin, hintaraja ja loppuunmyytyjen piilotus.

Lähteet:

| Lähde | Miten | Hinnat |
|---|---|---|
| Tiketti | skripti (`tiketti.py`, kaikki kaupungit) | ei, tila kyllä |
| Ticketmaster / Lippu.fi | skripti (`ticketmaster.py`, 9 kaupunkia, joilla Ticketmasterissa on kaupunkisivu) | ei, tila kyllä |
| Meteli.net, Bandsintown, Resident Advisor | Claude lukee verkosta | ei |
| Tarkastamo, Tullisali, Tuba | skripti (`paikat_oulu.py`, vain Oulu) | kyllä |
| Oulu Sinfonia | skripti (`paikat_oulu.py`, vain Oulu) | kyllä |
| Oulun musiikkikeskus (Madetojan sali, Pohjankartanon sali ym.) | skripti (`paikat_oulu.py`, vain Oulu) | ei |
| Tullikamari (Pakkahuone, Klubi), Tavara-asema, Telakka, Vastavirta | skripti (`paikat_tampere.py`, vain Tampere) | kyllä |
| Lutakko (Jelmu), Musta Kynnys | skripti (`paikat_jyvaskyla.py`, vain Jyväskylä) | kyllä |
| Linked Events (Helsingin seudun avoin tapahtumarajapinta) | skripti (`linkedevents.py`, Helsinki, Espoo, Vantaa) | osin |
| Songkick, keikkapaikat, lipunmyyjät, kaupunkien kalenterit | kaupungin tiedosto `cities/<kaupunki>.md`, luetaan verkkohaulla | vaihtelee |

Skilli toimii ilman selainta. Skriptit käyttävät tavallista HTTP-hakua, ja sivu tehdään valmiista pohjasta (`templates/keikat.html`) skriptillä `sivu.py`.

### Asennus ilman marketplacea

Kloonaa repo ja linkitä skilli Clauden skill-kansioon:

```bash
git clone https://github.com/juusimaa/claude-skills.git
ln -s "$PWD/claude-skills/plugins/keikat/skills/keikat" ~/.claude/skills/keikat
```

Skriptit tarvitsevat vain Python 3:n standardikirjaston. Niitä voi ajaa myös suoraan:

```bash
python3 plugins/keikat/skills/keikat/scripts/paikat_oulu.py --months 3 --table   # vain Oulu
python3 plugins/keikat/skills/keikat/scripts/paikat_tampere.py --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/paikat_jyvaskyla.py --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/linkedevents.py --city Helsinki --months 1 --table
python3 plugins/keikat/skills/keikat/scripts/tiketti.py --city Tampere --months 3 --table
python3 plugins/keikat/skills/keikat/scripts/ticketmaster.py --city Tampere --months 3 --table
```

`asetukset.py` näyttää ja tallentaa oletukset (`--kaupunki`, `--kuukaudet`, `--nollaa`). `paikat_<kaupunki>.py`-skriptit lukevat yhden kaupungin keikkapaikkoja. `tiketti.py`, `ticketmaster.py` ja `linkedevents.py` ottavat kaupungin valinnalla `--city`.

## Rakenne

```
.claude-plugin/marketplace.json     # listaa pluginit
plugins/
├── orchestrate/
│   ├── .claude-plugin/plugin.json
│   ├── commands/orchestrate.md     # /orchestrate
│   └── agents/                     # haiku-worker, sonnet-worker
└── keikat/
    ├── .claude-plugin/plugin.json
    └── skills/keikat/
        ├── SKILL.md                # ohjeet Claudelle
        ├── cities/                 # kaupunkikohtaiset lähteet
        ├── scripts/                # tiedonhaku ja sivun teko
        └── templates/              # web-sivun pohja
```

Jokainen plugin on omassa kansiossaan `plugins/<nimi>/`, ja se on listattu tiedostossa `.claude-plugin/marketplace.json`. Skillin kansion juuressa on `SKILL.md`.

## Huomioita

Skriptit lukevat julkisia tapahtumasivuja, ja sivujen rakenne voi muuttua. Jos jokin lähde lakkaa toimimasta, skripti ilmoittaa siitä ja muut lähteet toimivat edelleen. Oulun musiikkikeskuksen data tulee kaupungin tapahtumapalvelun kalenteriupotuksesta, joka ei ole dokumentoitu rajapinta.

## Lisenssi

Koko repositorio on [Apache-2.0](LICENSE)-lisenssillä. Saat käyttää, muokata ja jakaa pluginit myös kaupallisesti lisenssin ehtojen mukaan. Tekijänoikeusilmoitus on tiedostossa [NOTICE](NOTICE).

Tätä muutosta edeltävät versiot (pluginin `keikat` aiemmat commitit) julkaistiin lisenssillä PolyForm Noncommercial 1.0.0.

Copyright © 2026 Jouni Uusimaa
