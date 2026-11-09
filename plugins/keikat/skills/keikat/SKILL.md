---
name: keikat
description: Hakee lähiaikojen musiikkikeikat (isot ja pienet, myös baarikeikat) valitusta suomalaisesta kaupungista useista lähteistä ja listaa ne taulukkona päivämäärän, artistin, paikan, lippujen hinnan ja loppuunmyynti-tilan kanssa. Tuetut kaupungit: Helsinki, Espoo, Vantaa, Tampere, Turku, Oulu, Jyväskylä, Kuopio, Lahti, Pori, Kouvola, Joensuu, Lappeenranta, Hämeenlinna, Vaasa, Seinäjoki ja Rovaniemi (oletus Oulu, vaihdettavissa komennolla /keikat asetukset). Käytä kun käyttäjä kysyy "mitä keikkoja Tampereella", "keikat Helsingissä tällä viikolla/kuussa", "onko Turussa keikkaa X:llä" tai kutsuu /keikat.
argument-hint: "[kaupunki] [1kk–12kk] | asetukset [kaupunki] [1kk–12kk]"
---

# Keikat

Tuota ajantasainen, yhdistetty lista yhden kaupungin musiikkikeikoista. Vastaa suomeksi.

## Oletusasetukset

Käyttäjä voi tallentaa oman oletuskaupungin ja -aikavälin, joita pelkkä `/keikat` käyttää. Asetukset ovat tiedostossa `~/.config/keikat/asetukset.json`, ja niitä luetaan ja kirjoitetaan vain skriptillä:

```bash
python3 -I <tämän skillin kansio>/scripts/asetukset.py                                  # voimassa olevat oletukset (JSON)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --kaupunki Tampere --kuukaudet 3  # tallenna (kumpikin valinnainen)
python3 -I <tämän skillin kansio>/scripts/asetukset.py --nollaa                         # takaisin oletuksiin (Oulu, 1 kk)
```

**Jos argumentti alkaa sanalla `asetukset`** (myös `asetus`, `oletus`, `oletukset`), älä hae keikkoja. Toimi näin:
- `asetukset Tampere 3kk` tai `asetukset 6kk`: tallenna annetut arvot. Anna kaupunki perusmuodossa (`Tampereella` → `--kaupunki Tampere`) ja aikaväli lukuna 1–12. Vain annetut arvot muuttuvat.
- `asetukset` ilman muuta: näytä nykyiset oletukset ja kerro yhdellä rivillä, miten ne vaihdetaan.
- `asetukset nollaa`: aja `--nollaa`.
- Kerro lopuksi yhdellä rivillä skriptin tulostamat oletukset, esim. "Oletus nyt: Tampere, 3 kk. Pelkkä /keikat käyttää näitä." Jos skripti palauttaa virheen (tuntematon kaupunki), kerro se ja luettele tuetut kaupungit.

Myös vapaa pyyntö kuten "aseta oletuskaupungiksi Turku" tallentaa asetuksen samalla skriptillä.

## Parametrit (kaikki valinnaisia)

Aja ensin `asetukset.py` ilman valintoja ja käytä sen tulostamaa `kaupunki` ja `kuukaudet` oletuksina. Jos skripti ei toimi, oletus on Oulu ja 1 kk.

Komennon argumentti on: `$ARGUMENTS`. Siinä voi olla kaupunki, aikaväli tai molemmat missä järjestyksessä tahansa (esim. `Tampere 3kk`, `3kk Tampere`, `Helsingissä`). Argumentin arvot ohittavat tallennetut oletukset vain tällä kertaa. Poimi parametrit myös vapaasta pyynnöstä, muuten käytä oletuksia:

- **Kaupunki**: oletus asetuksista (tehdasasetus Oulu). Tunnista nimi myös taivutettuna ja pienellä kirjoitettuna ("tampereella", "Seinäjoella", "jyvaskyla"). Jos kaupunki ei ole alla olevassa taulukossa, kerro yhdellä lauseella, ettei sitä tueta, luettele tuetut kaupungit ja lopeta. Älä hae oletuskaupungin keikkoja tilalle.
- **Aikaväli**: oletus asetuksista (tehdasasetus 1 kuukausi) tästä päivästä eteenpäin.
  - Muoto `Nkk` (myös `N kk`, `N kuukautta`, pelkkä luku `N`), jossa N on 1–12: hae N kalenterikuukautta tästä päivästä eteenpäin. Esim. 8.11. ja `3kk` → 8.11.–8.2.
  - Jos N on yli 12, käytä 12 ja kerro siitä yhdellä lauseella.
  - Vapaa aikaväli kuten "tällä viikolla" tai "joulukuussa" tulkitaan sellaisenaan, ja skripteille annetaan `--days`, joka kattaa välin loppuun asti.
  - Pitkillä väleillä lista harvenee loppua kohti, koska pienet paikat julkaisevat ohjelmansa vain muutaman viikon päähän. Mainitse tämä yhdellä lauseella, kun väli on yli 3 kk.
- **Genre / artisti**: suodata, jos käyttäjä mainitsee.
- **Maksimihinta**: suodata, jos käyttäjä mainitsee. Ilmaiset keikat (0 €) kuuluvat aina mukaan.
- **Piilota loppuunmyydyt**: oletuksena näytä ne, merkitse selvästi.

## Tuetut kaupungit

| Kaupunki | Otsikossa | `--city` | Kaupungin tiedosto |
|---|---|---|---|
| Helsinki | Helsingissä | Helsinki | [cities/helsinki.md](cities/helsinki.md) |
| Espoo | Espoossa | Espoo | [cities/espoo.md](cities/espoo.md) |
| Vantaa | Vantaalla | Vantaa | [cities/vantaa.md](cities/vantaa.md) |
| Tampere | Tampereella | Tampere | [cities/tampere.md](cities/tampere.md) |
| Turku | Turussa | Turku | [cities/turku.md](cities/turku.md) |
| Oulu | Oulussa | Oulu | [cities/oulu.md](cities/oulu.md) |
| Jyväskylä | Jyväskylässä | Jyväskylä | [cities/jyvaskyla.md](cities/jyvaskyla.md) |
| Kuopio | Kuopiossa | Kuopio | [cities/kuopio.md](cities/kuopio.md) |
| Lahti | Lahdessa | Lahti | [cities/lahti.md](cities/lahti.md) |
| Pori | Porissa | Pori | [cities/pori.md](cities/pori.md) |
| Kouvola | Kouvolassa | Kouvola | [cities/kouvola.md](cities/kouvola.md) |
| Joensuu | Joensuussa | Joensuu | [cities/joensuu.md](cities/joensuu.md) |
| Lappeenranta | Lappeenrannassa | Lappeenranta | [cities/lappeenranta.md](cities/lappeenranta.md) |
| Hämeenlinna | Hämeenlinnassa | Hämeenlinna | [cities/hameenlinna.md](cities/hameenlinna.md) |
| Vaasa | Vaasassa | Vaasa | [cities/vaasa.md](cities/vaasa.md) |
| Seinäjoki | Seinäjoella | Seinäjoki | [cities/seinajoki.md](cities/seinajoki.md) |
| Rovaniemi | Rovaniemellä | Rovaniemi | [cities/rovaniemi.md](cities/rovaniemi.md) |

Lue valitun kaupungin tiedosto ennen vaihetta 1. Siinä ovat kaupungin skriptit, Songkick-osoite, keikkapaikat, lipunmyyjät, kalenterit, paikallismedia ja sudenkuopat. Hae vain valitun kaupungin keikat. Naapurikuntien keikat jätetään pois, ellei kaupungin tiedosto toisin sano.

## Vaiheet

Kaikki vaiheet toimivat ilman selainta: skriptit käyttävät tavallista HTTP-hakua, ja muut lähteet luetaan WebSearchilla tai web-fetch-agentilla. Älä käytä selain-MCP:tä.

### 1. Skriptit (luotettavimmat, aja aina ensin ja rinnakkain)

```bash
python3 -I <tämän skillin kansio>/scripts/tiketti.py --city <Kaupunki> --months N --table
python3 -I <tämän skillin kansio>/scripts/ticketmaster.py --city <Kaupunki> --months N --table
```

Nämä kaksi ajetaan kaikissa kaupungeissa. Ticketmasterilla on kaupunkisivu vain Helsingille, Espoolle, Tampereelle, Turulle, Oululle, Kuopiolle, Lahdelle, Porille ja Seinäjoelle. Muissa `ticketmaster.py` palauttaa tyhjän listan, mikä ei ole virhe. Hae niiden Lippu.fi-tapahtumat vaiheessa 2.

Aja samaan aikaan kaupungin tiedoston osiossa **Skriptit** mainitut skriptit, jos niitä on:

| Kaupunki | Skripti | Lähteet |
|---|---|---|
| Oulu | `paikat_oulu.py --months N --table` | Tarkastamo, Tullisali, Tuba, Oulu Sinfonia, musiikkikeskus |
| Tampere | `paikat_tampere.py --months N --table` | Tullikamari (Pakkahuone, Klubi), Tavara-asema, Telakka, Vastavirta |
| Jyväskylä | `paikat_jyvaskyla.py --months N --table` | Lutakko (Jelmu), Musta Kynnys |
| Helsinki, Espoo, Vantaa | `linkedevents.py --city <Kaupunki> --months N --table` | kaupunkien avoin tapahtumarajapinta |

Paikkaskriptit palauttavat hinnan ja tilan, joten niiden rivit täydentävät samojen keikkojen Tiketti-rivejä. Kaikilla skripteillä on samat valinnat (`--days`/`--months`, `--table`) ja samat JSON-kentät kuin `paikat_oulu.py`:llä.

`<Kaupunki>` on kohdan Tuetut kaupungit taulukon `--city`-sarakkeen arvo ääkkösineen. `N` on aikavälin kuukausimäärä (1–12). Vapaalle aikavälille käytä `--months`-valinnan tilalla `--days`. Ilman `--table` tuloste on JSON.

**tiketti.py** lukee Tiketin etusivun upotetun tapahtumadatan. Se palauttaa päivän, artistin, paikan, ovien ajan, tilan (`saatavilla` / `vähissä` / `loppuunmyyty` / `peruttu`) ja linkin, kun linkki löytyy. Kaupunkiin luetaan myös siihen liitettyjen entisten kuntien tapahtumat (esim. Kouvolaan Kuusankoski).
- Etusivulla on vain osa Tiketin tapahtumista, joten lista ei ole täydellinen.
- **Hintaa ei ole datassa**, ja tapahtumasivun hinnat latautuvat JavaScriptillä. Katso vaihe 3.
- Älä arvaile Tiketin sisäisiä JSON-osoitteita (esim. api.tiketti.fi). Lue vain julkisia sivuja.

**ticketmaster.py** lukee Ticketmasterin (sama myynti kuin Lippu.fi) kaupunkisivun `ticketmaster.fi/discover/<kaupunki>` upotetun tapahtumadatan. Siellä ovat isojen areenoiden, konserttitalojen ja kirkkokonserttien liput, joita Tiketissä ei ole. Hintaa ei ole datassa, mutta tila on (`saatavilla` / `vähissä` / `loppuunmyyty` / `peruttu`). Skripti pudottaa urheilun Ticketmasterin oman kategorian perusteella ja selvät ei-musiikkitapahtumat nimen perusteella (messut, työpajat, stand-up, teatteri). Mukaan jää silti teatteria ja stand-upia, joiden nimestä lajia ei näe, joten suodata vaiheen 4 mukaan. Sama tapahtuma voi tulla useana rivinä (VIP- ja aitiolippuvariantit), joten yhdistä ne. `--all` näyttää kaiken.

Jos skripti kertoo stderrissä, että lähde epäonnistui tai palautti nollan tapahtumaa, mainitse se lopuksi, ja lue sivu tarvittaessa web-fetch-agentilla.

### 2. Täydennä muilla lähteillä

Käy läpi kaupungin tiedoston lähteet. Aja ne rinnakkain WebSearchilla ja web-fetch-agentilla. Anna agentille kaikki osoitteet yhdellä kertaa ja pyydä tiivis lista (päivä, artisti, paikka, hinta, tila, osoite). Hae aina haetulle aikavälille, ja mainitse hakulauseessa kaupunki, kuukausi ja vuosi.

- **Songkick** (paras kokoava lähde): kaupungin tiedoston osoite, `/this-month` sekä jokainen muu aikavälin kuukausi muodossa `.../december-2026` (kuukauden englanninkielinen nimi pienellä). Lue web-fetch-agentilla, koska suora HTTP-haku palauttaa virheen 406. Hintoja ja tilaa ei ole.
- **Keikkapaikat**: kaupungin tiedoston taulukon ohjelmasivut. Lisää paikkoja löytyy hakemalla "keikkapaikat <kaupunki>". Etsi nykyinen osoite hakukoneella, jos tiedoston osoite ei vastaa.
- **Meteli.net** (suomalainen keikkakalenteri, myös pienet klubit), **Bandsintown** ja klubi- ja DJ-illoille **Resident Advisor** (ra.co/events/fi/<kaupunki>). Kaikki palauttavat suoralle HTTP-haulle virheen 403, joten lue ne web-fetch-agentilla tai hae WebSearchilla ("meteli.net <kaupunki> keikat"). Jos sivu ei aukea agentillekaan, jätä lähde pois ja mainitse se yhteenvedossa.
- **Muut lipunmyyjät**: kaupungin tiedoston osio **Lipunmyynti**. Lippu.fi / Ticketmaster tulee jo skriptistä. Yleisesti lisäksi Eventim, Fienta ja Lippupiste.
- **Kaupungin kalenterit** ja **paikallismedia**: kaupungin tiedoston osiot.

Jos paikka tai lähde ei vastaa tai sivu on tyhjä, jätä se pois äläkä keksi tietoja.

### 3. Hinnat

Hae hinta jokaiselle keikalle, jolta se vielä puuttuu, tässä järjestyksessä:

1. Kaupungin oman skriptin tulos, jos sellainen on (katso kaupungin tiedosto).
2. Keikkapaikan ohjelmasivu, jos hinta näkyy siellä tekstinä (kaupungin tiedoston taulukko kertoo).
3. Muun lipunmyyjän sivu tai tiedote, jossa hinta on usein tekstinä (esim. "liput 25 €"). Hae WebSearchilla muodossa "<artisti> <kaupunki> <pvm> liput hinta".
4. Jos hintaa ei löydy, kirjoita `–` äläkä arvaa. Tiketin tapahtumasivulta hinta ei näy ilman selainta. Jos sisäänpääsy on ilmainen, kirjoita `Ilmainen`. Jos liput eivät ole vielä myynnissä, kirjoita `Ei vielä myynnissä`.

Isoissa kaupungeissa (Helsinki, Tampere) keikkoja voi olla satoja. Hae silloin hinnat ensin paikkojen ohjelmasivuilta, jotka kattavat monta keikkaa kerralla, ja tee keikkakohtaisia hakuja vain, jos aikaa on. Jätä loput `–`:ksi.

### 4. Yhdistä ja puhdista

- Yhdistä saman keikan kaksoiskappaleet (sama artisti, päivä ja paikka eri lähteistä). Paikan nimi voi vaihdella lähteittäin (Ticketmaster: "Kalevan kirkko", Tiketti: "Kalevan kirkko, Tampere"), joten vertaa artistia ja päivää. Pidä lähteistä se, jossa on hinta ja tila, ja listaa muut lähteet linkkeinä.
- Suodata pois muut kuin musiikkikeikat (teatteri, stand-up, urheilu, messut), ellei tapahtuma ole selvästi musiikkia (konsertti, festivaali, klubi-ilta).
- Poista menneet ja perutut tapahtumat. Jos peruttu keikka olisi kiinnostava, mainitse se erikseen lopussa.
- Poista muiden kaupunkien keikat, joita kokoavat lähteet (Songkick, lipunmyyjät) tuovat mukaan.
- Järjestä aikajärjestykseen.

### 5. Tulosta

Taulukko, otsikkona kaupunki ja haettu aikaväli (esim. `Keikat Tampereella 8.11.–8.12.2026`):

| Pvm | Artisti | Paikka | Hinta | Tila | Linkki |
|---|---|---|---|---|---|
| la 14.11. | Jemina | Tuba | 28 € | saatavilla | [Linkki](https://www.tiketti.fi/…) |

Säännöt:
- Linkki-sarakkeessa on aina markdown-linkki `[Linkki](osoite)`, ei pelkkää osoitetta eikä lähteen nimeä. Käytä täyttä `https://`-osoitetta, jotta linkki aukeaa selaimeen. Jos tapahtumalla ei ole omaa sivua, linkitä paikan tai lähteen ohjelmasivulle. Jos osoitetta ei ole lainkaan, kirjoita `–`.
- Päivämäärä muodossa `la 14.11.` (viikonpäivä, päivä.kuukausi.), vuosi vain jos se ei ole kuluva vuosi.
- Hinta muodossa `28 €` tai väli `25–35 €` (alin–ylin, ennakko). Jos lähde kertoo vain alimman hinnan, kirjoita `alk. 28 €`. Mainitse erikseen jos hinta on ovelta.
- Tila: `saatavilla`, `vähissä`, `loppuunmyyty` (lihavoi), `ei vielä myynnissä`, `ilmainen`. Käytä sanaa `vähissä`, vain kun lähde sen kertoo (Tiketin tiedoista alle 15 % vapaana).
- Taulukon jälkeen **yksi rivi**: montako keikkaa löytyi ja mitkä lähteet tuottivat tuloksia. Jos jokin lähde ei toiminut, sano se.
- Älä lisää arvosteluja tai suosituksia, ellei käyttäjä pyydä. Voit tarjota suodatusta (genre, hinta) seuraavaksi.

### 6. Julkaise web-sivuna

Tee samasta listasta web-sivu, jolla on suodattimet (haku, paikka, hintaraja, loppuunmyytyjen piilotus) ja klikattavat Linkki-painikkeet. Sivun ulkoasu on valmiina tiedostossa `templates/keikat.html`, joten älä suunnittele sivua itse.

1. Kirjoita lista JSON-tiedostoksi scratchpad-kansioon, nimeksi `keikat-<kaupunki>.json` (pienellä, ilman ääkkösiä, esim. `keikat-seinajoki.json`). Muoto on kuvattu skriptin `scripts/sivu.py` alussa:
   - `title`: `Keikat <Otsikossa>` kaupunkitaulukon mukaan, esim. `Keikat Tampereella`.
   - `range`: haettu aikaväli, esim. `8.11.–8.12.2026`. `generated`: tämä päivä.
   - `events`: samat keikat kuin taulukossa. `date` muodossa `2026-11-14`, monipäiväisille lisäksi `end`. `price` ja `status` samoin kuin taulukossa, `url` täytenä osoitteena tai tyhjä. Alaviitteen sisältö (esim. epävarma loppuunmyynti) kenttään `note`.
   - `notes`: taulukon jälkeinen yhteenvetorivi ja maininta siitä, että lista ei ole täydellinen.
   - `sources`: lähteet, jotka tuottivat tuloksia, muodossa `{"name", "url"}`.
2. Aja `python3 -I <tämän skillin kansio>/scripts/sivu.py <keikat-kaupunki.json> <keikat-kaupunki.html>`. Molemmat tiedostot tulevat scratchpad-kansioon.
3. Julkaise HTML Artifact-työkalulla. Jokaisella kaupungilla on oma pysyvä linkkinsä:
   - Jos tässä keskustelussa on jo julkaistu saman kaupungin keikkasivu, julkaise sama tiedostopolku uudelleen.
   - Muuten hae käyttäjän artifactit (`action: "list"`). Jos sieltä löytyy saman kaupungin keikkasivu (otsikko esim. `Keikat Tampereella`), lue se (`action: "read"`) ja julkaise uusi versio sen `url`:iin. Älä päivitä toisen kaupungin sivua.
   - Muuten julkaise uutena: `icon: "music"`, `description` esim. "Tampereen musiikkikeikat 8.11.–8.12.2026 hintoineen ja suodattimineen."
4. Anna linkki taulukon ja yhteenvetorivin jälkeen yhdellä rivillä. Jos julkaisu ei onnistu, kerro se ja jätä terminaalin taulukko vastaukseksi.

## Totuudenmukaisuus

- Kerro puuttuvat tiedot puuttuviksi. Parempi `–` kuin keksitty hinta.
- Lista ei ole koskaan täydellinen, koska pienet baarikeikat ilmoitetaan usein vain sosiaalisessa mediassa. Mainitse tämä kerran lyhyesti, kun lista on valmis.
- Lähteiden sivut muuttuvat. Jos `tiketti.py` palauttaa tyhjän listan tai virheen, jatka muilla lähteillä ja kerro, että Tiketin haku ei toiminut. Pienissä kaupungeissa Tiketissä voi olla vain muutama tapahtuma, mikä ei ole virhe.
