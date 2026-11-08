# suomi-skills

Suomalaisiin palveluihin ja paikkakuntiin liittyviä skillejä [Claude Codelle](https://claude.com/claude-code).

## Skillit

| Skilli | Kuvaus |
|---|---|
| [keikat](skills/keikat/SKILL.md) | Oulun musiikkikeikat yhdeksi listaksi hintoineen ja lipputilanteineen, terminaaliin ja suodatettavalle web-sivulle. |

### keikat

```
/keikat          # kuukausi tästä päivästä
/keikat 3kk      # 1–12 kuukautta
/keikat joulukuussa
```

Skilli kokoaa keikat useasta lähteestä, yhdistää kaksoiskappaleet ja jättää pois muut kuin musiikkitapahtumat. Tulos tulee taulukkona terminaaliin ja julkaistaan web-sivuna (claude.ai-artifact), jolla on haku artistin, paikan ja päivän mukaan, paikkasuodatin, hintaraja ja loppuunmyytyjen piilotus.

Lähteet:

| Lähde | Miten | Hinnat |
|---|---|---|
| Tiketti | skripti (`tiketti_oulu.py`) | ei, tila kyllä |
| Tarkastamo, Tullisali, Tuba | skripti (`paikat_oulu.py`) | kyllä |
| Oulu Sinfonia | skripti (`paikat_oulu.py`) | kyllä |
| Oulun musiikkikeskus (Madetojan sali, Pohjankartanon sali ym.) | skripti (`paikat_oulu.py`) | ei |
| Songkick, muut lipunmyyjät, pienet paikat, kaupungin kalenterit | Claude hakee verkosta | vaihtelee |

Skilli toimii ilman selainta. Skriptit käyttävät tavallista HTTP-hakua, ja sivu tehdään valmiista pohjasta (`templates/keikat.html`) skriptillä `sivu.py`.

## Asennus

Kloonaa repo ja linkitä haluamasi skilli Clauden skill-kansioon:

```bash
git clone https://github.com/juusimaa/suomi-skills.git
ln -s "$PWD/suomi-skills/skills/keikat" ~/.claude/skills/keikat
```

Skriptit tarvitsevat vain Python 3:n standardikirjaston. Niitä voi ajaa myös suoraan:

```bash
python3 skills/keikat/scripts/paikat_oulu.py --months 3 --table
python3 skills/keikat/scripts/tiketti_oulu.py --months 3 --table
```

## Rakenne

```
skills/
└── keikat/
    ├── SKILL.md            # ohjeet Claudelle
    ├── scripts/            # tiedonhaku ja sivun teko
    └── templates/          # web-sivun pohja
```

Jokainen skilli on omassa kansiossaan `skills/<nimi>/`, ja kansion juuressa on `SKILL.md`.

## Huomioita

Skriptit lukevat julkisia tapahtumasivuja, ja sivujen rakenne voi muuttua. Jos jokin lähde lakkaa toimimasta, skripti ilmoittaa siitä ja muut lähteet toimivat edelleen. Oulun musiikkikeskuksen data tulee kaupungin tapahtumapalvelun kalenteriupotuksesta, joka ei ole dokumentoitu rajapinta.
