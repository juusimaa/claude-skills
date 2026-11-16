# Oulu

## Skriptit

Täytetään tehtävässä 5.

## Lähteet

Kaikki luetaan tavallisella HTTP:llä (`curl -sL -A "Mozilla/5.0 ..."` tai Pythonin `urllib`). Tarkistettu 16.11.2026.

### 1. Kaupungin tapahtumapalvelu, näyttelyt: **skripti**

`https://tapahtumat.munoulu.fi/api/search/internal-content-fetch?lang=fi&country=FI&mode=event`

- Palvelun sivu (`/fi-FI`) on AngularJS-sovellus, jonka HTML ei sisällä tapahtumia. `categoriesByKey`-taulussa on vain neljä yleiskategoriaa (Ilmainen, Esteetön, Virtuaali, Kaikukorttikohde), eikä `hm_nayttelyt` ole tapahtumien kategoria (se kuuluu Lähellä.fi-vapaaehtoistoimintaan). Älä käytä niitä.
- Sivun käyttämä taustarajapinta (`urlRootBackend` = `https://tapahtumat.munoulu.fi/api`) on selaimen verkkoliikenteestä ja bundlen koodista katsottu, ei dokumentoitu. Ilman avainta ja evästeitä palauttaa JSON `{"pages": [...]}`: kaikki tulevat ja käynnissä olevat tapahtumat kerralla (16.11. noin 364 kpl, 1,7 Mt). Suodatinparametrit (`q`, `categories`, `start`, `end`) eivät rajaa luotettavasti (`categories=hm_nayttelyt` ja päivämäärät eivät tehneet mitään), joten hae kaikki ja suodata itse.
- **Näyttelyiden suodatus:** `"Exhibitions" in page["globalContentCategories"]` (noin 60 kpl 16.11.). Kategoria on tekoälyn tai tuojan antama ja epätarkka: mukana on myös kierroksia, elokuvia, festivaaleja ja valotapahtumia, ja osa oikeista näyttelyistä puuttuu (esim. "Taidetta muualla"). Lisäsuodatus nimellä on tarpeen (ks. Sudenkuopat).
- Kentät:
  - `name`, `descriptionShort`, `descriptionLong` (HTML)
  - `defaultStartDate`, `defaultEndDate`: näyttelyn koko jakso, **UTC**-aikaleimana (`2026-11-12T22:00:00.000Z` = pe 13.11. Suomen aikaa). Muunna `Europe/Helsinki`-aikaan ennen päivän poimimista.
  - `event.dates[]`: yksittäiset päivät (`start`, `end`, `isCancelled`). Pitkillä näyttelyillä ne ovat joko tyhjiä (`[]`), yksi koko jakson pituinen rivi tai käyntikerrat.
  - `locations[0].address`: paikka ja osoite yhtenä merkkijonona, esim. "Kulttuuritalo Valve, Hallituskatu 7, 90100 Oulu". Voi olla tyhjä.
  - `hasPrice` (bool): tosi tarkoittaa, että tapahtumalla on hinta, mutta summaa ei ole kentässä. Ilmainen: `categories` sisältää id:n `6170601b7a45476ff366cb18` ("Ilmainen") tai kuvauksessa lukee "vapaa pääsy".
  - `openingHours`: lähes aina tyhjä. Aukioloajat ovat vain kuvaustekstissä, jos sielläkään.
  - `links`: tyhjä. Linkki: `https://tapahtumat.munoulu.fi/fi-FI/page/<_id>`.
  - `sourceName`: `Mun Oulu tapahtumakalenteri`, `Oulu2026 tapahtumakalenteri` (kulttuuripääkaupunkiohjelma tulee tätä kautta), `lippu.fi`, `tiketti`, `ticketmaster.mfx.FI`, `netticket`.
  - `event.isCancelled`, `event.urlPurchaseTicket`
- Esimerkki: `Josefina Nelimarkka: Arctic Clouds`, 13.11.2026–24.1.2027, Kulttuuritalo Valve, Hallituskatu 7, linkki `.../fi-FI/page/6a3a20d47520bd723d98fa22`.
- Muita esimerkkejä: `Tiibetin pyhiä kuvia - Thangka-näyttely` 1.–29.11.2026 (Hallituskatu 33); `Björk & Fotografiska Tallinn: PLAY` 13.11.–31.12.2026 (lippu.fi, Kauppurienkatu 10, ostolinkki `event.urlPurchaseTicket`).
- Tarkistus:

```bash
python3 -I -c "
import json,urllib.request as u
r=u.Request('https://tapahtumat.munoulu.fi/api/search/internal-content-fetch?lang=fi&country=FI&mode=event',headers={'User-Agent':'Mozilla/5.0'})
d=json.load(u.urlopen(r,timeout=30))['pages']
for p in d:
    if 'Exhibitions' in p.get('globalContentCategories',[]): print(p['name'],p['defaultStartDate'][:10],p['defaultEndDate'][:10])"
```

### 2. Oulun taidemuseo, näyttelylista: **skripti**

`https://ouluntaidemuseo.fi/nayttelyt/` (tavallista HTML:ää, WordPress).

- Jokaisesta näyttelystä on kortti: päivämäärävälin `<span class="item-date ...">30.10.2026–28.3.2027 </span>`, nimi `<h2>…</h2>` ja linkki `href="https://ouluntaidemuseo.fi/nayttely/<slug>/"`. Poimi nämä regexillä (`class="item-date[^>]*>([^<]*)</span>.*?<h2>(.*?)</h2>.*?href="([^"]+)"`).
- 16.11. palautuu: `Ajasta irrallaan` 30.10.2026–28.3.2027 ja `Sopeutuminen` 16.10.2026–14.2.2027 (molemmat Oulun taidemuseo, Kasarmintie 9). Näyttelyn omalla sivulla on lisätietoa, mutta aukioloajat ja hinnat ovat yhteisellä sivulla (ks. Pysyvät näyttelyt).
- Samalla sivulla on myös `Taidetta muualla` -kiertonäyttely (`Hanna Kaisa Vainio: Paikan henki`, 1.8.2026–31.7.2027), pysyvä Galleria Oskari Jauhiainen ja verkkonäyttelyt. Ne eivät noudata samaa korttirakennetta ja jäävät regexin ulkopuolelle: Oskari Jauhiainen on pysyvä rivi, verkkonäyttelyt jätetään pois (ei fyysisiä).
- `https://ouluntaidemuseo.fi/nayttelyt-taidemuseolla/` näyttää saman listan.

```bash
curl -sL -A "Mozilla/5.0" https://ouluntaidemuseo.fi/nayttelyt/ | grep -o 'item-date[^<]*\|<h2>[^<]*'
```

### 3. Kulttuuritalo Valven näyttelyt (Valvegalleria, Photo North, Sarjakuvagalleria!, Kamari): **skripti**

`https://tapahtumat.munoulu.fi/widget/67b6f7af04b40b760fdd944c?currentLocation=https%3A%2F%2Fwww.kulttuurivalve.fi%2Ftervetuloa-vierailulle%2Fnayttelyt-valveella%2F&nolog=true`

- Sama widget-JSON kuin keikat-pluginin Musiikkikeskuksessa (`paikat_oulu.py`, `musiikkikeskus`). Ilman `currentLocation`-parametria palvelin vastaa virheellä 500, joten parametri on pakollinen.
- Vastauksen kenttä `html` sisältää kortit: pilko kohdasta `<div class="bubster-page`. Nimi: `class="bubster-name"[^>]*>(.*?)</a>`, aika: `class="bubster-time">(.*?)</div>` (esim. `la 5.9.2026 - su 20.12.2026`), paikka: `class="bubster-location">`, sivun id: `bubster-page-<id>` (linkki `https://tapahtumat.munoulu.fi/fi-FI/page/<id>`). Ei hintaa eikä aukioloaikoja.
- 16.11. palautuu 5 riviä: `Hertta Kiiski: Bloomrotmilk` ja `Lyy Raitala: Pesintä` (5.9.–20.12.2026, Photo North), `Angel 90s, from crying to flying - taidenäyttely` (13.10.–22.11.2026), `Josefina Nelimarkka: Arctic Clouds` (13.11.2026–24.1.2027) ja yksi yksittäinen tapahtuma (`Valveen Lumo-valofestivaali: DJ MALSSON`, `klo 18:00 - 20:00`), joka pitää pudottaa.
- Widgetin osoite on katsottu Valven sivun lähdekoodista (`widget-loader/<id>`), ei dokumentoitu.
- Valven aukioloajat ja ilmainen pääsy: ks. Pysyvät näyttelyt.

```bash
curl -sL -A "Mozilla/5.0" "https://tapahtumat.munoulu.fi/widget/67b6f7af04b40b760fdd944c?currentLocation=https%3A%2F%2Fwww.kulttuurivalve.fi%2Ftervetuloa-vierailulle%2Fnayttelyt-valveella%2F&nolog=true" | python3 -I -c "import sys,json;print(len(json.load(sys.stdin)['html']))"
```

### 4. Tiima (Tietomaa, Oulun museo, Lasten museo, VISIO): **haku** (pysyvät rivit kirjoitetaan skriptiin)

- `https://tietomaa.fi/` ja `https://oulun-museo.fi/` ovat tavallista HTML:ää (curl toimii), mutta sivuilla ei ole päivämääriä: näyttelyt ovat esittelysivuja ilman alkua ja loppua. Aukioloajat ja hinnat ovat etusivun tekstissä ja `https://tietomaa.fi/info/`-sivulla (ks. Pysyvät näyttelyt).
- Tapahtumapalvelun kautta (lähde 1) tulevat samat näyttelyt (`Eläinten jäljillä`, `Aurora Revelare`, `Metallikausi`, `Polkuja kaupungissa`, `Masiina`) jaksolla 8.10.2026 – 2028…2040. Pitkä loppupäivä on pysyvyyden merkki, ei oikea päättymispäivä.
- Skripti ei tarvitse näitä erikseen, jos Tiima on listattu pysyvissä riveissä.

### 5. Oulu2026-ohjelma: **haku** (katettu lähteellä 1)

- `https://oulu2026.eu/program/` on kulttuuripääkaupunkivuoden avajaisfestivaalin staattinen ohjelmasivu (tammikuun 2026 sisältöä), ei ajantasainen näyttelylista. WordPress-rajapinta `wp-json/` on olemassa, mutta ohjelmalle ei löytynyt avointa päätepistettä.
- Oulu2026-tapahtumat näkyvät tapahtumapalvelussa (`sourceName` = `Oulu2026 tapahtumakalenteri`), joten lähde 1 kattaa ne (esim. `Josefina Nelimarkka: Arctic Clouds`, `Ystävän talo`, `Climate Clock`). Kalenteri: `https://oulu2026.eu/tapahtumat`.
- Täydentävä haku: WebSearch "Oulu2026 näyttely <kuukausi>", jos käyttäjä kysyy erikseen.

### 6. Muut: **haku**

- Kotilo (`https://www.ouka.fi/lastenkulttuurikotilo/nayttelyt`, myös `lastenkulttuurikotilo.fi`): HTML toimii, näyttelyt `Ystävän talo` ja `Sen pituinen se` ilman päivämääriä sivulla. Päivämäärät tulevat lähteestä 1 (29.9.2026–10.4.2027).
- Kirjastot: `https://www.ouka.fi/kirjaston-tapahtumat-ja-nayttelyt` on kuvaus eikä lista. Keskustakirjasto Saaren näyttelyt tulevat vain tapahtumapalvelusta (lähde 1, osoite sisältää "Saari").
- Galleria Harmaja ja Taidekeskus Kulttuurivälimö: ks. Sudenkuopat. Kumpaakaan ei löytynyt toimivalla verkkosivulla.
- Oulun Taiteilijaseuran Oulun kuvataiteen talo (Galleria 5, Pimento, Arttila; `https://artoulu.fi` vastaa 200, ohjelmaa ei tutkittu) ja yksityiset galleriat (Galleria TASO, Pikigalleria, Neliö-Galleria, Art Gallery Finland): näkyvät osittain lähteessä 1.

## Pysyvät näyttelyt

Arvo `–` tarkoittaa, ettei sitä löytynyt. Tiedot tarkistettu 16.11.2026.

### Oulun taidemuseo (Kasarmintie 9)

- Näyttelyt: `https://ouluntaidemuseo.fi/nayttelyt/`. Perusnäyttelyä museolla ei ole, vaan vaihtuvat näyttelyt (ks. lähde 2). Kokoelmanäyttelyt: `https://ouluntaidemuseo.fi/kokoelmanayttelyt/` (ei kiinteää jaksoa).
- Aukioloajat ja hinnat: `https://ouluntaidemuseo.fi/aukioloajat-ja-paasymaksut/`.
- Aukioloajat 17.10.–23.12.2026: ti–to 9–18, pe 11–19, la–su 11–18. 29.–30.12. ti–to 11–18. Suljettu maanantaisin, 6.12. ja 24.–27.12. Poikkeukset: 19.11. 9–16, 20.–22.11. 11–16, 1.12. 9–17, 4.12. 11–17, 31.12. 11–16.
- Hinta 2026: aikuinen 12 €, opiskelija / työtön / eläkeläinen 9 €, alle 18-vuotiaat vapaa pääsy. Museokortti ja Kaikukortti käyvät. Ilmaispäivä 8.11. (Isänpäivä). Kahvila Kaari ja museokauppa Ainoa ovat vapaa pääsy.
- Galleria Oskari Jauhiainen (Syke-talo, Kirjastokuja 1, Kiiminki): **pysyvä** perusnäyttely, yli 20 veistosta, `https://ouluntaidemuseo.fi/nayttely/galleria-oskari-jauhiainen/`. Avoinna Kiimingin kirjaston aukioloaikoina (kirjaston ajat: –), pääsy maksuton.

### Tiima: Tietomaa, Oulun museo, Lasten museo (Nahkatehtaankatu 6, Myllytulli)

- Tietomaa ja Oulun museo toimivat nyt yhdessä Tiimassa. Vanhaa Tietomaan taloa ei käytetä.
- Sivut: `https://tietomaa.fi/` (näyttelyt: `/nayttelyt/masiina/`, `/nayttelyt/aurora-revelare/`, `/nayttelyt/elainten-jaljilla/`, `/nayttelyt/varkkaamo/`), `https://oulun-museo.fi/` (Oulu: Tarinani, Rikoksetta rangaistut, Lasten museo – Polkuja kaupungissa, Seikkailutehdas, Metallikausi), `https://www.tiima-oulu.fi/`.
- Aukioloajat (tietomaa.fi/info/, oulun-museo.fi, tiima-oulu.fi): ma–pe 11–19, la–su 10–18. Lipunmyynti päättyy 30 min ennen sulkemista. 5.11. 12–19 (poikkeus, mennyt).
- Hinnat (`https://tietomaa.fi/info/`): aikuinen 22 €, alennusryhmät 14 €, lapsi 6–17 v 14 €, perhe 58 €, iltalippu (kaksi viimeistä tuntia) 12 €. Museokortti käy. Yksi lippu käy koko Tiimaan. Lapsille on oma pääsymaksuton museo (Lasten museo, uutinen 13.10.2026).
- Pysyvät rivit: Masiina, Aurora Revelare, Eläinten jäljillä, Värkkäämö (oppimisympäristö), Oulu: Tarinani, Rikoksetta rangaistut, Polkuja kaupungissa, Seikkailutehdas, Metallikausi (avautui 2026, ei päättymispäivää). Tarkkoja avautumispäiviä: –.

### Kulttuuritalo Valve (Hallituskatu 7)

- Näyttelyt: `https://www.kulttuurivalve.fi/tervetuloa-vierailulle/nayttelyt-valveella/` (lähde 3). Galleriat: Valvegalleria, Photo North, Sarjakuvagalleria!, aulagalleria, ravintola Valveen Paljetin näyttelytila ja 2. kerroksen Pop up -galleria Kamari (avattu 4/2026).
- Aukioloajat (`https://www.kulttuurivalve.fi/tervetuloa-vierailulle/aukioloajat/`): ma–pe 9–21, la–su 10–21. Suljettu 6.12.2026, 23.12.2026–1.1.2027, 6.1.2027 ja 26.–29.3.2027.
- Hinta: näyttelyihin vapaa pääsy (Liput ja maksutavat -sivulla `…/liput-ja-maksutavat/` on vain tapahtumalippuja).
- Pysyviä näyttelyitä ei ole.
- **Sulkeutuu:** talo on avoinna 30.4.2027 asti ja suljetaan peruskorjaukseen 1.5.2027 alkaen (kesä 2027 – joulu 2029).

### Pohjois-Pohjanmaan museo

- Pohjois-Pohjanmaan vastuumuseo on Oulun museo- ja tiedekeskus (`https://oulunmuseojatiedekeskus.fi/`, curl toimii). Se ylläpitää Tiimaa (Tietomaa + Oulun museo, avautui 9.10.2026), Kierikkiä, Turkansaarta, Merimiehenkotimuseota, Oulun linnan kellaria, Oulunsalon kotiseutumuseota ja Pateniemen sahan museota. Pääkohde Oulun museo = Tiima (ks. yllä). Erillistä `ppmuseo.fi`-sivua ei ole (yhteysvirhe). Muiden kohteiden aukioloajat ja hinnat: –.
- Merimiehenkotimuseo (Pikisaarentie 6), `https://merimiehenkotimuseo.fi/`: perusnäyttely. Avoinna vain kesäisin ja joulun aikaan: 28.11.–20.12.2026 la–su 11–17. Vapaa pääsy. Tapahtumapalvelussa lisäksi `Joulu Merimiehenkotimuseossa` ja `Jouluikkunat Merimiehenkotimuseossa` (27.11.2026–). Kun museo on kiinni, rivi ei kuulu listalle.

### Lastenkulttuurikeskus Kotilo (Keskustakirjasto Saari, 4. krs, Kaarlenväylä 3)

- Näyttelyt: `https://www.ouka.fi/lastenkulttuurikotilo/nayttelyt` (Ystävän talo, Sen pituinen se; molemmat 29.9.2026–10.4.2027 tapahtumapalvelun mukaan).
- Galleria avoinna: ti ja to 13–19, ke ja pe 9–15, la 10–16, su ja ma suljettu. Sivu: `https://www.ouka.fi/lastenkulttuurikotilo/aukioloajat`. Hinta: –.

### Keskustakirjasto Saari (Kaarlenväylä 3)

- Sivu: `https://www.ouka.fi/kirjastot-ja-kirjastoautot/keskustakirjasto-saari`. Aukioloajat ma–pe 8–20, la–su 10–16 (Kotilon sivun mukaan, kirjaston oma sivu ei näyttänyt aikoja tekstinä). Pääsy ilmainen.
- Pysyvää näyttelyä ei ole, vain vaihtuvia (Näyttelyvitriini, galleriatilat). Ei listasivua: käytä tapahtumapalvelua (lähde 1, osoite "Oulun keskustakirjasto Saari") ja nuoriso- tai yhteisönäyttelyt.

### Galleria Harmaja

- Verkkosivua ei löytynyt. `galleriaharmaja.fi` ohjautuu toiseen galleriaan (`galleriakajaste.fi`) ja `harmaja.fi` on ohjelmistoyritys. Aukioloajat ja hinnat: –. Älä listaa, ellei haku löydä ajantasaista näyttelyä.

### Taidekeskus Kulttuurivälimö

- `kulttuurivalimo.fi` ja `www.kulttuurivalimo.fi` eivät vastanneet (yhteysvirhe). Aukioloajat ja hinnat: –.

### Oulun kuvataiteen talo (Oulun Taiteilijaseura)

- Galleria 5, Pimento, Arttila, taidelainaamo Arto. Valven naapurissa (Valven sivun mukaan), `https://artoulu.fi`. Aukioloajat ja hinnat: –.

## Sudenkuopat

- **Tapahtumapalvelun ajat ovat UTC:tä.** `defaultStartDate` voi olla edellisen päivän 22:00 tai 21:00 (kesäaika/talviaika), joten muunna Suomen aikaan, tai alku on yhtä päivää liian aikaisin.
- **Yhden päivän tai kierros-tapahtumat pois.** Kategoria `Exhibitions` sisältää paljon muuta: `Näyttelyesittely: …`, `Kuraattorikierros`, `Monikielinen näyttelykierros …`, `Taiteilijatapaaminen`, `Maanantaielokuva`, elokuvat (esim. `Klaus Härö: HETKI ENNEN VALOA`), `Lumo`-valofestivaalin tapahtumat, kirjajulkistus (`Zero Nine -kirjaa juhlistetaan …`), `Festivaalisunnuntai`, `Henkilöstöpalaveri`. Pudota yhden päivän rivit sekä nimet, joissa on `esittely`, `kierros`, `työpaja`, `opastus`, `luento`, `elokuva`, `festivaali`, `tapaaminen`.
- **Sama näyttely kahdesti.** `Minä olen tarina` tulee sekä `Mun Oulu`- että `Oulu2026`-lähteestä, ja Valven näyttelyt tulevat sekä widgetistä (lähde 3) että tapahtumapalvelusta (lähde 1). Yhdistä nimen ja paikan mukaan. Englanninkielinen versio (`Näyttelyesittely englanniksi: …`) on opastus, ei näyttely.
- **Tiiman pysyvät näyttelyt näyttävät tapahtumapalvelussa määräaikaisilta** (`8.10.2026 – 9.10.2028`, `…2030`, `…2040`). Loppu 2028 tai myöhemmin tarkoittaa käytännössä pysyvää: merkitse Pysyvä, älä näytä loppupäivää.
- **Verkkonäyttelyt** (`Verkkonäyttely: Vilho Lampi …`, `Verkkonäyttely: Koulutie`, alku 2024–2025, loppu 2028–2030) eivät ole fyysisiä näyttelyitä. Pudota nimen `Verkkonäyttely` perusteella.
- **Ulkotaide ja reitit** (`Climate Clock`, `JiiPee.art Showroom`) ovat jatkuvia ulkoteoksia ilman aukioloaikoja: ota mukaan vain, jos käyttäjä haluaa julkista taidetta.
- **Päättyvät pian.** Esim. `Uoman huomassa` päättyy 19.11.2026 ja `Minä olen tarina` 22.11.2026: sopivat Päättyy pian -merkintään.
- **Haarakirjastojen näyttelyt pois.** Haarakirjastojen (Kiimingin kirjasto jne.) vitriinit ja pienet kirjastonäyttelyt tulevat tapahtumapalvelusta (esim. `Jälkiä ympäristössä`, `Musiikin innoittama taidenäyttely`, Kiimingin kirjasto). Pudota ne (osoitteessa Kiimingin kirjasto tms.): vain Keskustakirjasto Saari otetaan mukaan. Kiimingin Galleria Oskari Jauhiainen on poikkeus, koska se on taidemuseon pysyvä näyttely.
- **Suljetut tai sulkeutuvat paikat:**
  - Kulttuuritalo Valve suljetaan peruskorjaukseen 1.5.2027 alkaen. Jos aikaväli ulottuu sen yli, merkitse Valven rivien loppu 30.4.2027.
  - Merimiehenkotimuseo on auki vain 28.11.–20.12.2026 (la–su 11–17), muuten kiinni.
  - Tietomaan vanha talo ei ole käytössä: Tietomaa on Tiimassa.
  - Galleria Harmaja ja Taidekeskus Kulttuurivälimö: ei toimivaa sivua.
- **Aukioloajat poikkeavat juhlina.** Taidemuseo on kiinni maanantaisin ja 6.12. ja 24.–27.12.; Valve 6.12. ja 23.12.–1.1.
- **Tapahtumapalvelun rajapinta ei ole julkinen eikä sille ole lupausta.** Jos `pages` on tyhjä tai pyyntö antaa virheen, kerro lähteen epäonnistumisesta ja turvaudu hakuun (taidemuseo ja Valve toimivat itsenäisesti).
- **Valven widget** vaatii `currentLocation`-parametrin (ilman sitä HTTP 500).
- **`www.valve.fi` ja `kulttuurivalimo.fi` eivät ole kulttuuritalon sivuja.** `valve.fi` ohjaa B2B-yritykseen (`valveone.com`). Oikea osoite on `www.kulttuurivalve.fi`.
- **`visitoulu.fi/fi/tapahtumat`** lataa sisällön JavaScriptillä eikä ole luettavissa curlilla.
