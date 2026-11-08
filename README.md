# suomi-skills

Suomalaisiin palveluihin ja paikkakuntiin liittyviä skillejä [Claude Codelle](https://claude.com/claude-code).

## Skillit

| Skilli | Kuvaus |
|---|---|
| [keikat](skills/keikat/SKILL.md) | Suomen 17 suurimman kaupungin musiikkikeikat yhdeksi listaksi hintoineen ja lipputilanteineen, terminaaliin ja suodatettavalle web-sivulle. |

### keikat

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

## Asennus

Kloonaa repo ja linkitä haluamasi skilli Clauden skill-kansioon:

```bash
git clone https://github.com/juusimaa/suomi-skills.git
ln -s "$PWD/suomi-skills/skills/keikat" ~/.claude/skills/keikat
```

Skriptit tarvitsevat vain Python 3:n standardikirjaston. Niitä voi ajaa myös suoraan:

```bash
python3 skills/keikat/scripts/paikat_oulu.py --months 3 --table   # vain Oulu
python3 skills/keikat/scripts/paikat_tampere.py --months 3 --table
python3 skills/keikat/scripts/paikat_jyvaskyla.py --months 3 --table
python3 skills/keikat/scripts/linkedevents.py --city Helsinki --months 1 --table
python3 skills/keikat/scripts/tiketti.py --city Tampere --months 3 --table
python3 skills/keikat/scripts/ticketmaster.py --city Tampere --months 3 --table
```

`asetukset.py` näyttää ja tallentaa oletukset (`--kaupunki`, `--kuukaudet`, `--nollaa`). `paikat_<kaupunki>.py`-skriptit lukevat yhden kaupungin keikkapaikkoja. `tiketti.py`, `ticketmaster.py` ja `linkedevents.py` ottavat kaupungin valinnalla `--city`.

## Rakenne

```
skills/
└── keikat/
    ├── SKILL.md            # ohjeet Claudelle
    ├── cities/             # kaupunkikohtaiset lähteet
    ├── scripts/            # tiedonhaku ja sivun teko
    └── templates/          # web-sivun pohja
```

Jokainen skilli on omassa kansiossaan `skills/<nimi>/`, ja kansion juuressa on `SKILL.md`.

## Huomioita

Skriptit lukevat julkisia tapahtumasivuja, ja sivujen rakenne voi muuttua. Jos jokin lähde lakkaa toimimasta, skripti ilmoittaa siitä ja muut lähteet toimivat edelleen. Oulun musiikkikeskuksen data tulee kaupungin tapahtumapalvelun kalenteriupotuksesta, joka ei ole dokumentoitu rajapinta.
