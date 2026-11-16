---
name: nayttelyt
description: Hakee valitun suomalaisen kaupungin näyttelyt (taide, valokuva, muotoilu, museot; määräaikaiset ja pysyvät), jotka ovat auki tällä viikolla tai valitulla aikavälillä, ja listaa ne taulukkona aukioloaikojen ja hintojen kanssa. Merkitsee näyttelyt tunnisteilla Uusi, Päättyy pian ja Pysyvä ja tekee samasta listasta web-sivun. Tuettu tällä hetkellä: Oulu (muut keikat-skillin 17 kaupungista tulossa). Ei elokuvia eikä live-musiikkia. Käytä kun käyttäjä kysyy "mitä näyttelyitä Oulussa", "näyttelyt tällä viikolla", "mitä näyttelyitä on joulukuussa" tai kutsuu /nayttelyt.
argument-hint: "[kaupunki] [viikko|1kk–12kk] | asetukset [kaupunki] [viikko|1kk–12kk]"
---

# Näyttelyt

Tuota ajantasainen, yhdistetty lista yhden kaupungin näyttelyistä. Vastaa suomeksi.

## Oletusasetukset

Käyttäjä voi tallentaa oman oletuskaupungin ja -aikavälin, joita pelkkä `/nayttelyt` käyttää. Asetukset ovat tiedostossa `~/.config/nayttelyt/asetukset.json`, ja niitä luetaan ja kirjoitetaan vain skriptillä:

```bash
python3 -I <tämän skillin kansio>/scripts/asetukset.py                                    # voimassa olevat oletukset (JSON)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --kaupunki Oulu --aikavali 3       # tallenna (kumpikin valinnainen)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --aikavali viikko                  # viikko tai kuukausia 1–12
python3 -I <tämän skillin kansio>/scripts/asetukset.py --nollaa                           # takaisin oletuksiin (Oulu, viikko)
```

Skripti tulostaa JSONin `{"kaupunki", "aikavali", "lähde"}`. `aikavali` on `"viikko"` tai kuukausien määrä 1–12.

**Jos argumentti alkaa sanalla `asetukset`** (myös `asetus`, `oletus`, `oletukset`), älä hae näyttelyitä. Toimi näin:
- `asetukset Oulu 3kk` tai `asetukset viikko`: tallenna annetut arvot. Anna kaupunki perusmuodossa (`Oulussa` → `--kaupunki Oulu`) ja aikaväli sanana `viikko` tai lukuna 1–12. Vain annetut arvot muuttuvat.
- `asetukset` ilman muuta: näytä nykyiset oletukset ja kerro yhdellä rivillä, miten ne vaihdetaan.
- `asetukset nollaa`: aja `--nollaa`.
- Kerro lopuksi yhdellä rivillä skriptin tulostamat oletukset, esim. "Oletus nyt: Oulu, 3 kk. Pelkkä /nayttelyt käyttää näitä." Jos skripti palauttaa virheen (tuntematon kaupunki), kerro se ja luettele tuetut kaupungit.

Myös vapaa pyyntö kuten "aseta näyttelyiden oletusajaksi 3 kuukautta" tallentaa asetuksen samalla skriptillä.

## Parametrit (kaikki valinnaisia)

Aja ensin `asetukset.py` ilman valintoja ja käytä sen tulostamaa `kaupunki` ja `aikavali` oletuksina. Jos skripti ei toimi, oletus on Oulu ja viikko.

Komennon argumentti on: `$ARGUMENTS`. Siinä voi olla kaupunki, aikaväli tai molemmat missä järjestyksessä tahansa (esim. `Oulu 3kk`, `joulukuussa`, `Oulussa`). Argumentin arvot ohittavat tallennetut oletukset vain tällä kertaa. Poimi parametrit myös vapaasta pyynnöstä, muuten käytä oletuksia:

- **Kaupunki**: oletus asetuksista (tehdasasetus Oulu). Tunnista nimi myös taivutettuna ja pienellä kirjoitettuna ("oulussa"). Tällä hetkellä tuettu on vain Oulu. Muista keikat-skillin 16 kaupungista (Helsinki, Espoo, Vantaa, Tampere, Turku, Jyväskylä, Kuopio, Lahti, Pori, Kouvola, Joensuu, Lappeenranta, Hämeenlinna, Vaasa, Seinäjoki, Rovaniemi) sano yhdellä lauseella "ei vielä tuettu", kerro että tuettu on vain Oulu, ja lopeta. Sama pätee tuntemattomaan kaupunkiin. Älä hae oletuskaupungin näyttelyitä tilalle.
- **Aikaväli**: oletus asetuksista (tehdasasetus viikko). Muunna se päivämääriksi `--from` ja `--to` (muoto `YYYY-MM-DD`). Tämä päivä on `generated`.
  - Oletus / `viikko` / "tällä viikolla": `--from` tänään, `--to` tämän viikon sunnuntai. Sivun `range` näyttää silti koko viikon ma–su, esim. `16.–22.11.2026`.
  - `Nkk` (myös `N kk`, `N kuukautta`, pelkkä luku `N`), N 1–12: `--from` tänään, `--to` tänään + N kuukautta. Jos N on yli 12, käytä 12 ja kerro siitä yhdellä lauseella.
  - Vapaa aikaväli tulkitaan sellaisenaan: "joulukuussa" on kuukauden omat päivät (1.–31.12.), "ensi viikolla" on seuraava ma–su. Tällöin `range` on sama väli, esim. `1.–31.12.2026`.

## Tuetut kaupungit

| Kaupunki | Otsikossa | Kaupungin tiedosto |
|---|---|---|
| Oulu | Oulussa | [cities/oulu.md](cities/oulu.md) |

Muut keikat-skillin 17 kaupungista tulevat myöhemmin. Lue valitun kaupungin tiedosto ennen vaihetta 2. Siinä ovat kaupungin skriptit, lähteet (merkitty **skripti** tai **haku**), pysyvät näyttelyt aukioloaikoineen ja hintoineen sekä sudenkuopat.

## Vaiheet

Kaikki vaiheet toimivat ilman selainta: skriptit käyttävät tavallista HTTP-hakua, ja muut lähteet luetaan WebSearchilla tai web-fetch-agentilla. Älä käytä selain-MCP:tä.

### 1. Asetukset

Aja `asetukset.py` ja päätä kaupunki ja aikaväli (ks. Parametrit).

### 2. Skriptit (luotettavimmat)

```bash
python3 -I <tämän skillin kansio>/scripts/nayttelyt_oulu.py --from YYYY-MM-DD --to YYYY-MM-DD
```

Tuloste on JSON-lista näyttelyistä. Valinnat: `--from`, `--to` ja `--table` (tekstitaulukko JSONin sijaan). Skripti lukee tapahtumapalvelun, Oulun taidemuseon ja Valven näyttelyt sekä kaupungin pysyvät rivit. Jos skripti kertoo stderrissä, että lähde epäonnistui tai palautti nollan riviä, mainitse se lopuksi ja täydennä vaiheessa 3.

### 3. Täydennä haulla

Käy läpi kaupungin tiedoston **haku**-lähteet ja täytä puuttuvat aukioloajat, hinnat ja linkit WebSearchilla tai web-fetch-agentilla. Aja haut rinnakkain, anna agentille kaikki osoitteet yhdellä kertaa ja mainitse hakulauseessa kaupunki, kuukausi ja vuosi. Älä koskaan keksi aukioloaikoja tai hintoja: jos tietoa ei löydy, kirjoita `–`. Ilmainen pääsy on `Ilmainen`. Jos lähde ei vastaa tai sivu on tyhjä, jätä se pois.

### 4. Yhdistä ja puhdista

- Yhdistä kaksoiskappaleet (sama nimi ja paikka eri lähteistä). Pidä rivi, jossa on aukioloajat, hinta ja linkki.
- Pudota kertatapahtumat: kierrokset, työpajat, luennot, taiteilijatapaamiset, elokuvat, konsertit ja festivaalitapahtumat. Mukaan vain varsinaiset näyttelyt.
- Pudota haarakirjastojen pienet vitriininäyttelyt (ks. kaupungin sudenkuopat).
- Yksi pysyvä rivi per paikka (esim. Tiiman pysyvät näyttelyt yhtenä rivinä, jos kaupungin tiedosto niin ohjaa).
- Älä laske tunnisteita (Uusi, Päättyy pian, Pysyvä) itse: `sivu.py` laskee ne.

### 5. Kirjoita JSON ja tulosta taulukko

Kirjoita lista JSON-tiedostoksi scratchpad-kansioon nimeksi `nayttelyt-<kaupunki>.json` (pienellä, ilman ääkkösiä, esim. `nayttelyt-oulu.json`). Muoto on kuvattu skriptin `scripts/sivu.py` alussa:
- `title`: `Näyttelyt <Otsikossa>`, esim. `Näyttelyt Oulussa`.
- `range`: haettu aikaväli, esim. `16.–22.11.2026` (oletusviikolla koko viikko ma–su). `generated`: tämä päivä (`YYYY-MM-DD`).
- `from`, `to`: haun alku ja loppu (`YYYY-MM-DD`). `from` on ikkunan alku, ja Uusi-tunniste lasketaan siitä, ei tästä päivästä.
- `exhibitions`: `name` ja `venue` ovat pakollisia. Lisäksi `start`, `end` (tyhjä tai `2026-11-20`), `permanent`, `hours`, `price`, `url`, `note`, `source`.
- `notes`: taulukon jälkeinen yhteenvetorivi ja maininta siitä, että lista ei ole täydellinen.
- `sources`: lähteet, jotka tuottivat tuloksia, muodossa `{"name", "url"}`.

Aja `python3 -I <tämän skillin kansio>/scripts/sivu.py <nayttelyt-kaupunki.json> <nayttelyt-kaupunki.html>`. Molemmat tiedostot tulevat scratchpad-kansioon. Skripti tulostaa markdown-taulukon: tulosta se sellaisenaan vastaukseksi otsikon (esim. `Näyttelyt Oulussa 16.–22.11.2026`) alle.

Taulukon jälkeen **yksi rivi**: montako näyttelyä löytyi, mitkä lähteet tuottivat tuloksia, mitkä epäonnistuivat, ja että lista ei ole koskaan täydellinen. Älä lisää arvosteluja tai suosituksia, ellei käyttäjä pyydä.

### 6. Julkaise web-sivuna

Vaiheen 5 HTML on valmis sivu (ulkoasu tiedostossa `templates/nayttelyt.html`), joten älä suunnittele sivua itse. Julkaise se Artifact-työkalulla. Jokaisella kaupungilla on oma pysyvä linkkinsä:
- Jos tässä keskustelussa on jo julkaistu saman kaupungin näyttelysivu, julkaise sama tiedostopolku uudelleen.
- Muuten hae käyttäjän artifactit (`action: "list"`). Jos sieltä löytyy saman kaupungin näyttelysivu (otsikko `Näyttelyt Oulussa`), lue se (`action: "read"`) ja julkaise uusi versio sen `url`:iin. Älä päivitä toisen kaupungin sivua.
- Muuten julkaise uutena: `icon: "image"`, `description` esim. "Oulun näyttelyt 16.–22.11.2026 aukioloaikoineen ja hintoineen."

Anna linkki taulukon ja yhteenvetorivin jälkeen yhdellä rivillä. Jos julkaisu ei onnistu, kerro se ja jätä terminaalin taulukko vastaukseksi.

## Totuudenmukaisuus

- Kerro puuttuvat tiedot puuttuviksi. Parempi `–` kuin keksitty aukioloaika tai hinta.
- Lista ei ole koskaan täydellinen, koska pienet galleriat ja kirjastot ilmoittavat näyttelynsä usein vain omilla sivuillaan tai sosiaalisessa mediassa. Mainitse tämä kerran lyhyesti.
- Lähteiden sivut ja tapahtumapalvelun rajapinta muuttuvat. Jos skripti palauttaa tyhjän listan tai virheen, jatka haulla ja kerro, että kyseinen lähde ei toiminut.
