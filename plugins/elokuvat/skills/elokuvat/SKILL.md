---
name: elokuvat
description: Hakee suomalaisen kaupungin elokuvateatterien näytökset (Finnkino ja muut teatterit) tälle illalle, huomiselle tai koko tälle viikolle ja listaa ne taulukkona näytösaikojen, salien, ikärajojen ja lippulinkkien kanssa. Merkitsee uudet ensi-illat ja tekee samasta listasta suodatettavan web-sivun. Lähteet elokuviin.com ja nytleffaan.fi; kaikki elokuviin.comin kaupungit tuettu. Käytä kun käyttäjä kysyy "mitä leffoja tänään", "mitä elokuvia Oulussa tänä iltana", "elokuvat tällä viikolla" tai kutsuu /elokuvat.
argument-hint: "[kaupunki] [tänään|huomenna|viikko] | asetukset [kaupunki] [tänään|huomenna|viikko]"
---

# Elokuvat

Tuota ajantasainen lista yhden kaupungin elokuvateatterien näytöksistä. Vastaa suomeksi.

## Oletusasetukset

Käyttäjä voi tallentaa oman oletuskaupungin ja -aikavälin, joita pelkkä `/elokuvat` käyttää. Asetukset ovat tiedostossa `~/.config/elokuvat/asetukset.json`, ja niitä luetaan ja kirjoitetaan vain skriptillä:

```bash
python3 -I <tämän skillin kansio>/scripts/asetukset.py                                       # voimassa olevat oletukset (JSON)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --kaupunki Oulu --aikavali viikko     # tallenna (kumpikin valinnainen)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --aikavali tanaan                     # tanaan, huomenna tai viikko
python3 -I <tämän skillin kansio>/scripts/asetukset.py --nollaa                              # takaisin oletuksiin (Oulu, tänään)
```

Skripti tulostaa JSONin `{"kaupunki", "aikavali", "lähde"}`.

**Jos argumentti alkaa sanalla `asetukset`** (myös `asetus`, `oletus`, `oletukset`), älä hae näytöksiä. Toimi näin:
- `asetukset Tampere viikko`: tallenna annetut arvot. Anna kaupunki perusmuodossa (`Tampereella` → `--kaupunki Tampere`) ja aikaväli sanana `tanaan`, `huomenna` tai `viikko`. Vain annetut arvot muuttuvat.
- `asetukset` ilman muuta: näytä nykyiset oletukset ja kerro yhdellä rivillä, miten ne vaihdetaan.
- `asetukset nollaa`: aja `--nollaa`.
- Kerro lopuksi yhdellä rivillä skriptin tulostamat oletukset, esim. "Oletus nyt: Tampere, koko viikko. Pelkkä /elokuvat käyttää näitä."

Kaupunkia ei tarkisteta tallennettaessa. Se tarkistuu, kun näytöksiä haetaan.

## Parametrit (kaikki valinnaisia)

Aja ensin `asetukset.py` ilman valintoja ja käytä sen tulostamaa `kaupunki` ja `aikavali` oletuksina. Jos skripti ei toimi, oletus on Oulu ja tänään.

Komennon argumentti on: `$ARGUMENTS`. Siinä voi olla kaupunki, aikaväli tai molemmat missä järjestyksessä tahansa. Argumentin arvot ohittavat tallennetut oletukset vain tällä kertaa. Poimi parametrit myös vapaasta pyynnöstä:

- **Kaupunki**: tunnista nimi myös taivutettuna ja pienellä ("oulussa", "Jyväskylässä", "Helsingissä"), ja anna se skriptille perusmuodossa (`Oulu`, `Jyväskylä`, `Helsinki`). Mikä tahansa kaupunki, jolle elokuviin.comissa on sivu, toimii.
- **Aikaväli**:
  - `tänään`, "tänä iltana", "nyt", oletus `tanaan` → `--tanaan` (tämän päivän näytökset, jotka eivät ole vielä alkaneet).
  - `huomenna` → `--huomenna`. Sunnuntaina huominen ei ole vielä listalla: sano se yhdellä lauseella ja näytä `--tanaan`.
  - `viikko`, "tällä viikolla", "koko viikko" → `--viikko` (tästä päivästä sunnuntaihin, yksi rivi per elokuva).
  - Kaikki pidempi tai myöhempi ("3kk", "joulukuussa", "ensi viikolla"): sano yhdellä lauseella, että näytösajat ovat saatavilla vain tälle viikolle, ja näytä `--viikko`.

## Vaiheet

Kaikki toimii ilman selainta tavallisella HTTP-haulla. Skriptit ovat ainoat lähteet: älä täydennä WebSearchilla äläkä hae finnkino.fi-sivuja (ne estävät skriptit).

### 1. Asetukset

Aja `asetukset.py` ja päätä kaupunki ja aikaväli.

### 2. Hae näytökset

```bash
python3 -I <tämän skillin kansio>/scripts/elokuvat.py --city <Kaupunki> > <scratchpad>/elokuvat-<kaupunki>.json
```

Tiedoston nimessä kaupunki pienellä ja ilman ääkkösiä, esim. `elokuvat-jyvaskyla.json`. Skripti hakee aina koko viikon (tästä päivästä sunnuntaihin).

- Paluuarvo 2: elokuviin.comissa ei ole sivua kaupungille. Sano se yhdellä lauseella ja lopeta. Älä hae oletuskaupunkia tilalle.
- Stderrin rivit kertovat epäonnistuneista lähteistä. Ne näkyvät myös JSONin `warnings`-listassa.

### 3. Taulukko ja sivu

```bash
python3 -I <tämän skillin kansio>/scripts/sivu.py <scratchpad>/elokuvat-<kaupunki>.json <scratchpad>/elokuvat-<kaupunki>.html --tanaan
```

Lipuksi `--tanaan`, `--huomenna` tai `--viikko` aikavälin mukaan. Skripti tulostaa markdown-taulukon otsikkoineen: tulosta se sellaisenaan vastaukseksi. HTML-sivu sisältää aina koko viikon.

Taulukon jälkeen **yksi rivi**: montako elokuvaa ja näytöstä löytyi, mitkä lähteet epäonnistuivat (`sources` jossa `ok: false`) ja jokainen `warnings`-rivi sellaisenaan. Älä lisää arvosteluja tai suosituksia, ellei käyttäjä pyydä.

### 4. Julkaise web-sivuna

Vaiheen 3 HTML on valmis sivu (ulkoasu tiedostossa `templates/elokuvat.html`), joten älä suunnittele sivua itse. Julkaise se Artifact-työkalulla. Jokaisella kaupungilla on oma pysyvä linkkinsä:
- Jos tässä keskustelussa on jo julkaistu saman kaupungin elokuvasivu, julkaise sama tiedostopolku uudelleen.
- Muuten hae käyttäjän artifactit (`action: "list"`). Jos sieltä löytyy saman kaupungin sivu (otsikko esim. `Elokuvat Oulussa`), lue se (`action: "read"`) ja julkaise uusi versio sen `url`:iin. Älä päivitä toisen kaupungin sivua.
- Muuten julkaise uutena: `icon: "film"`, `description` esim. "Oulun elokuvateatterien näytökset 16.–22.11.2026."

Anna linkki yhteenvetorivin jälkeen yhdellä rivillä. Jos julkaisu ei onnistu, kerro se ja jätä terminaalin taulukko vastaukseksi.

## Totuudenmukaisuus

- Älä koskaan keksi näytösaikoja, saleja tai ikärajoja. Puuttuva tieto on `–`.
- Lista kattaa sen, mitä elokuviin.com listaa. Viikonlopun näytökset julkaistaan usein vasta viikon loppupuolella: jos skripti varoittaa siitä, kerro se.
- Lähteet ovat yksityisiä sivustoja, joiden rakenne voi muuttua. Jos elokuviin.com ei vastaa, kerro, että näytösajat puuttuvat ja lista on vain nytleffaan.fi:n elokuvaluettelo.
