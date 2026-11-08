---
name: keikat
description: Hakee lähiaikojen musiikkikeikat Oulusta (isot ja pienet, myös baarikeikat) useista lähteistä ja listaa ne taulukkona päivämäärän, artistin, paikan, lippujen hinnan ja loppuunmyynti-tilan kanssa. Käytä kun käyttäjä kysyy "mitä keikkoja Oulussa", "keikat Oulussa tällä viikolla/kuussa", "onko Oulussa keikkaa X:llä" tai kutsuu /keikat.
argument-hint: "[1kk–12kk]"
---

# Keikat Oulussa

Tuota ajantasainen, yhdistetty lista Oulun musiikkikeikoista. Vastaa suomeksi.

## Parametrit (kaikki valinnaisia)

Poimi käyttäjän pyynnöstä, muuten käytä oletuksia:

- **Aikaväli**: oletus 1 kuukausi tästä päivästä eteenpäin. Komennon argumentti on: `$ARGUMENTS`
  - Muoto `Nkk` (myös `N kk`, `N kuukautta`, pelkkä luku `N`), jossa N on 1–12: hae N kalenterikuukautta tästä päivästä eteenpäin. Esim. 8.11. ja `3kk` → 8.11.–8.2.
  - Jos N on yli 12, käytä 12 ja kerro siitä yhdellä lauseella. Jos argumentti on tyhjä, käytä 1 kuukautta.
  - Vapaa aikaväli kuten "tällä viikolla" tai "joulukuussa" tulkitaan sellaisenaan, ja skripteille annetaan `--days`, joka kattaa välin loppuun asti.
  - Pitkillä väleillä lista harvenee loppua kohti, koska pienet paikat julkaisevat ohjelmansa vain muutaman viikon päähän. Mainitse tämä yhdellä lauseella, kun väli on yli 3 kk.
- **Genre / artisti**: suodata, jos käyttäjä mainitsee.
- **Maksimihinta**: suodata, jos käyttäjä mainitsee. Ilmaiset keikat (0 €) kuuluvat aina mukaan.
- **Piilota loppuunmyydyt**: oletuksena näytä ne, merkitse selvästi.

## Vaiheet

Kaikki vaiheet toimivat ilman selainta: skriptit käyttävät tavallista HTTP-hakua, ja muut lähteet luetaan WebSearchilla tai web-fetch-agentilla. Älä käytä selain-MCP:tä.

### 1. Skriptit (luotettavimmat, aja aina ensin ja rinnakkain)

```bash
python3 -I <tämän skillin kansio>/scripts/tiketti_oulu.py --months N --table
python3 -I <tämän skillin kansio>/scripts/paikat_oulu.py --months N --table
```

`N` on aikavälin kuukausimäärä (1–12). Vapaalle aikavälille käytä `--months`-valinnan tilalla `--days`. Ilman `--table` tuloste on JSON.

**tiketti_oulu.py** lukee Tiketin etusivun upotetun tapahtumadatan. Se palauttaa päivän, artistin, paikan, ovien ajan, tilan (`saatavilla` / `vähissä` / `loppuunmyyty` / `peruttu`) ja linkin, kun linkki löytyy.
- Etusivulla on vain osa Tiketin tapahtumista, joten lista ei ole täydellinen.
- **Hintaa ei ole datassa**, ja tapahtumasivun hinnat latautuvat JavaScriptillä. Katso vaihe 3.
- Älä arvaile Tiketin sisäisiä JSON-osoitteita (esim. api.tiketti.fi). Lue vain julkisia sivuja.

**paikat_oulu.py** lukee hintoineen näiden paikkojen omat ohjelmasivut:
- **Tarkastamo** (Torinranta): hinta on sivun tekstinä (esim. "34,90€ | VIP 44,90€"). Ovelta peritään lisäksi palvelumaksu 4 €, ja ovilippu on 5 € ennakkoa kalliimpi. Kategoriaa ei ole, joten jätä pois muut kuin musiikkitapahtumat itse (esim. taikashow).
- **Tullisali** (Tyrnäväntie 16): kentässä `category` on sivun kategoria. Ota mukaan vain `Musiikki`. Hinta on alin hinta, joten merkitse se muodossa `alk. 33 €`. Ostolinkki (Ticketmaster) on kentässä `tickets_url`.
- **Tuba**: hinta on muodossa "Liput ennakkoon 20 €, ovelta 24 €". Linkki vie yleensä Tiketin tapahtumaan, joten **tästä saa hinnat Tuban Tiketti-keikoille**. Jätä pois brunssit, visat ja muut kuin keikat.
- **Oulu Sinfonia** (oulusinfonia.fi/kaikki-konsertit): Madetojan salin, Ouluhallin, Ravintola Preludin ja muiden paikkojen konsertit. Skripti hakee hinnan konsertin omalta sivulta (esim. "42 € perushinta / 32 € eläkeläinen / 22 € opiskelija…"). Taulukkoon riittää perushinta, esim. `42 € (alennus 22–32 €)`. Kategoria `Vapaa pääsy` tarkoittaa ilmaista. Monipäiväisillä on kenttä `end` ja `time_info` kertoo näytösten määrän. Lista ulottuu yleensä vain muutaman kuukauden päähän.

- **Oulun musiikkikeskus** (Madetojan sali, Pohjankartanon sali, Tulindbergin sali, Pikkusali): skripti lukee musiikkikeskuksen tapahtumakalenterin datan suoraan kaupungin tapahtumapalvelusta (tapahtumat.munoulu.fi). Mukana ovat kaikki tapahtumat eivätkä vain sivulla ensin näkyvät kuusi. Hintaa ja lipputilannetta ei ole, joten jätä `status` tyhjäksi ja hinta `–`, ellei sitä löydy muualta. Linkki vie tapahtumasivulle, jolla on ostolinkki. Peruttujen tapahtumien `status` on `peruttu`. Kalenterissa on paljon muutakin kuin musiikkia (stand-up, taikurit, sirkus, baletti, teatteri, seminaarit), joten suodata vaiheen 4 mukaan. Konservatorion oppilaskonsertit ovat musiikkia ja kuuluvat mukaan. Sama konsertti voi tulla myös Oulu Sinfonialta, joten yhdistä kaksoiskappaleet. Datan osoite on katsottu selaimen verkkoliikenteestä eikä se ole dokumentoitu rajapinta. Jos lähde palauttaa nollan tapahtumaa, hae Madetojan salin tapahtumat WebSearchilla.

`status` on `loppuunmyyty`, jos hintatekstissä lukee "sold out" tai "loppuunmyyty". Tarkista teksti: esim. "VIP 44,90€ (sold out)" voi tarkoittaa, että vain VIP-liput on myyty loppuun. Kerro tällainen epävarmuus alaviitteessä. Jos skripti kertoo stderrissä, että lähde epäonnistui tai palautti nollan tapahtumaa, mainitse se lopuksi, ja lue sivu tarvittaessa web-fetch-agentilla.

### 2. Täydennä muilla lähteillä

Aja nämä rinnakkain WebSearchilla ja web-fetch-agentilla. Anna agentille kaikki osoitteet yhdellä kertaa ja pyydä tiivis lista (päivä, artisti, paikka, hinta, tila, osoite). Hae aina haetulle aikavälille, ja mainitse hakulauseessa kuukausi ja vuosi.

- **Songkick** (paras kokoava lähde): https://www.songkick.com/metro-areas/28832-finland-oulu/this-month sekä jokainen muu aikavälin kuukausi muodossa `.../december-2026` (kuukauden englanninkielinen nimi pienellä). Lue web-fetch-agentilla, koska suora HTTP-haku palauttaa virheen 406. Hintoja ja tilaa ei ole.
- **Muut lipunmyyjät**: Lippu.fi / Ticketmaster (Oulun Energia Areena, Ouluhalli, Madetojan sali), Eventim, Fienta.
- **Pienet paikat ja baarit**: etsi paikkojen omat ohjelmasivut ja sosiaalinen media. Tarkista ainakin Tukikohta, 45 Special, Club Teatria, RioLive, Sauna Oulu ja Oulun Tapahtumat Oy. Lisää paikkoja löytyy hakemalla "keikkapaikat Oulu". Etsi nykyinen osoite hakukoneella äläkä oleta vanhoja osoitteita: tukikohta.org on eri järjestö, ja clubteatria.fi ja 45special.com eivät aina vastaa.
- **Kaupungin kalenterit**: visitoulu.fi/fi/tapahtumat (sisältö latautuu JavaScriptillä, joten käytä hakua), ouka.fi/oulu/tapahtumat, oulu2026.eu/program (Oulu on Euroopan kulttuuripääkaupunki 2026, mukana paljon ilmaisia keikkoja).
- **Ilmaiset ja pienet keikat**: Kaleva ja Oulun Ylioppilaslehti listaavat usein viikon keikat.

Jos paikka tai lähde ei vastaa tai sivu on tyhjä, jätä se pois äläkä keksi tietoja.

### 3. Hinnat

Hae hinta jokaiselle keikalle, jolta se vielä puuttuu, tässä järjestyksessä:

1. `paikat_oulu.py`:n tulos. Saman keikan Tuba-rivillä on myös Tiketti-keikan hinta.
2. Muun lipunmyyjän sivu tai tiedote, jossa hinta on usein tekstinä (esim. "liput 25 €"). Hae WebSearchilla muodossa "<artisti> Oulu <pvm> liput hinta".
3. Paikan oma sivu web-fetch-agentilla.
4. Jos hintaa ei löydy, kirjoita `–` äläkä arvaa. Tiketin tapahtumasivulta hinta ei näy ilman selainta. Jos sisäänpääsy on ilmainen, kirjoita `Ilmainen`. Jos liput eivät ole vielä myynnissä, kirjoita `Ei vielä myynnissä`.

### 4. Yhdistä ja puhdista

- Yhdistä saman keikan kaksoiskappaleet (sama artisti, päivä ja paikka eri lähteistä). Pidä lähteistä se, jossa on hinta ja tila, ja listaa muut lähteet linkkeinä.
- Suodata pois muut kuin musiikkikeikat (teatteri, stand-up, urheilu, messut), ellei tapahtuma ole selvästi musiikkia (konsertti, festivaali, klubi-ilta).
- Poista menneet ja perutut tapahtumat. Jos peruttu keikka olisi kiinnostava, mainitse se erikseen lopussa.
- Järjestä aikajärjestykseen.

### 5. Tulosta

Taulukko, otsikkona haettu aikaväli:

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

1. Kirjoita lista JSON-tiedostoksi scratchpad-kansioon (esim. `keikat.json`). Muoto on kuvattu skriptin `scripts/sivu.py` alussa:
   - `title`: `Keikat <kaupunki>ssa`, esim. `Keikat Oulussa`.
   - `range`: haettu aikaväli, esim. `8.11.–8.12.2026`. `generated`: tämä päivä.
   - `events`: samat keikat kuin taulukossa. `date` muodossa `2026-11-14`, monipäiväisille lisäksi `end`. `price` ja `status` samoin kuin taulukossa, `url` täytenä osoitteena tai tyhjä. Alaviitteen sisältö (esim. epävarma loppuunmyynti) kenttään `note`.
   - `notes`: taulukon jälkeinen yhteenvetorivi ja maininta siitä, että lista ei ole täydellinen.
   - `sources`: lähteet, jotka tuottivat tuloksia, muodossa `{"name", "url"}`.
2. Aja `python3 -I <tämän skillin kansio>/scripts/sivu.py <keikat.json> <keikat.html>`. Molemmat tiedostot tulevat scratchpad-kansioon.
3. Julkaise HTML Artifact-työkalulla. Pidä yksi pysyvä linkki:
   - Jos tässä keskustelussa on jo julkaistu keikkasivu, julkaise sama tiedostopolku uudelleen.
   - Muuten hae käyttäjän artifactit (`action: "list"`). Jos sieltä löytyy saman kaupungin keikkasivu (esim. otsikko `Keikat Oulussa`), lue se (`action: "read"`) ja julkaise uusi versio sen `url`:iin.
   - Muuten julkaise uutena: `icon: "music"`, `description` esim. "Oulun musiikkikeikat 8.11.–8.12.2026 hintoineen ja suodattimineen."
4. Anna linkki taulukon ja yhteenvetorivin jälkeen yhdellä rivillä. Jos julkaisu ei onnistu, kerro se ja jätä terminaalin taulukko vastaukseksi.

## Totuudenmukaisuus

- Kerro puuttuvat tiedot puuttuviksi. Parempi `–` kuin keksitty hinta.
- Lista ei ole koskaan täydellinen, koska pienet baarikeikat ilmoitetaan usein vain sosiaalisessa mediassa. Mainitse tämä kerran lyhyesti, kun lista on valmis.
- Lähteiden sivut muuttuvat. Jos skripti `tiketti_oulu.py` palauttaa tyhjän listan tai virheen, jatka muilla lähteillä ja kerro, että Tiketin haku ei toiminut.
