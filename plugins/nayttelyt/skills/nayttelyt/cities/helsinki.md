# Helsinki

## Skriptit

```bash
python3 -I <skillin kansio>/scripts/nayttelyt_helsinki.py --from YYYY-MM-DD --to YYYY-MM-DD
```

Skripti lukee lähteet 1–2: Linked Eventsin näyttelyt (`yso:p5121`, `division=helsinki`) ja museot.fin näyttelykalenterin (Uusimaa, kunta Helsinki), ja palauttaa noin 100 riviä viikossa (103 viikolla 16.–22.11.2026), ja ajo kestää noin 20 s.
Se pudottaa yhden päivän tapahtumat, päivittäiset alitapahtumat (`super_event`), haarakirjastot, asukas- ja yhteisötalot sekä verkkonäyttelyt, ja yhdistää kahdesta lähteestä tulevat kaksoisrivit. Oodi ja kaupungin kulttuurikeskukset säilyvät. Lähde 3 (taidegalleriat) ja puuttuvat tiedot haetaan haulla.

## Lähteet

Kaikki luetaan tavallisella HTTP:llä (`curl -sL -A "nayttelyt-skill/1.1"` tai Pythonin `urllib`). Tarkistettu 16.11.2026.

### 1. Linked Events, näyttelyt: **skripti**

`https://api.hel.fi/linkedevents/v1/event/?keyword=yso:p5121&division=helsinki&start=<alku>&end=<loppu>&include=location&page_size=100` (seuraa `meta.next`).

- `yso:p5121` = "näyttelyt". Ilman `division=helsinki`-rajausta mukaan tulee Espoon kirjastoja (ks. Sudenkuopat).
- Kentät: `name.fi`, `start_time` ja `end_time` (**UTC**, muunna `Europe/Helsinki`-aikaan), `location.name.fi`, `info_url.fi`, `offers[0].is_free` ja `price`, `super_event_type`.
- Linkki: `info_url.fi`, jos tyhjä niin `https://tapahtumat.hel.fi/fi/events/<id>`.
- Aukioloaikoja ei ole. Ne tulevat museoilta museot.fistä (lähde 2) ja gallerioilta lähteestä 3.
- Paikkasääntö: ks. Sudenkuopat.

### 2. museot.fi, näyttelykalenteri: **skripti**

`https://museot.fi/nayttelykalenteri/index.php?maakunta_id=1&nayttelyhaku=1&kaikki=1` (tavallista HTML:ää, kaikki tulokset yhdellä sivulla).

- Kaupunkisuodatinta ei ole: haetaan maakunta Uusimaa ja pidetään kortit, joissa on `<span class="kunta">Helsinki</span>`. Loppupäivätön näyttely on pysyvä.
- Museon sivulta `https://museot.fi/museohaku/index.php?museo_id=<id>` otetaan aukioloajat ja pääsymaksut (kerran per museo).
- **TLS:** museot.fi lähettää vain oman varmenteensa (Telia RSA DV CA v4), joten curl ja Python hylkäävät sen. Skillin mukana tulee välivarmenne `certs/telia-rsa-dv-ca-v4.pem`: `curl --cacert <skillin kansio>/certs/telia-rsa-dv-ca-v4.pem` tai Pythonissa `ssl.create_default_context(cafile=...)`. Älä koskaan käytä `-k` tai `verify=False`.
- Tarkistus:

```bash
curl -sL --cacert <skillin kansio>/certs/telia-rsa-dv-ca-v4.pem -A "nayttelyt-skill/1.1" "https://museot.fi/nayttelykalenteri/index.php?maakunta_id=1&nayttelyhaku=1&kaikki=1" | grep -c 'nayttely_id='
```

### 3. Taidegalleriat, stadissa.fi-lista: **haku**

`https://www.stadissa.fi/paikat/4134/art-galleries-in-helsinki-taidegalleriat-helsingissa`: taulukko galleriasta (osoite, verkkosivu, puhelin). Ei näyttelyitä eikä päivämääriä.

Ohje vaiheeseen 3: tarkista **yhdellä** koottu web-fetch -kutsulla vain ne galleriat, joita skripti ei palauttanut (lähde 1 toi 16.11. ainakin Helsinki Contemporary, Galerie Forsblom, Galerie Anhava, Forum Box ja Galleria Huuto). Hae kunkin etusivulta nykyinen näyttely ja päivämäärät. Aukioloajat alla ovat omilta sivuilta 16.11.2026; hinta kirjataan vain, jos galleria sanoo sen itse. Muuten `–`.

| Galleria | Osoite | Verkkosivu | Aukioloajat | Hinta |
|---|---|---|---|---|
| Galleria Ama (AMA Gallery) | Rikhardinkatu 1 | `ama.gallery` (`ama.fi` ohjaa sinne) | ti–pe 11–17, la–su 12–16 | – |
| Galleria Heino | Erottajankatu 9, sisäpiha | `galleriaheino.fi` (`.com` ohjaa) | – | – |
| Helsinki Contemporary | Bulevardi 10 | `helsinkicontemporary.com` | ke–pe 12–18, la–su 12–16 | – |
| Galerie Anhava | Fredrikinkatu 43 | `anhava.com` | ti–pe 11–17, la–su 12–16 | – |
| Galleria Art Kaarisilta | Sanomatalo 1. krs, Elielinaukio 2 | `artkaarisilta.fi` | **toiminta päättynyt 19.6.2025** | – |
| G 12 Helsinki | Annankatu 16 | `galleria12.fi` | ti–to 12–17, pe–su 12–16 (vaihtoviikot kiinni: 18.–19.11., 9.–10.12., 23.12.–6.1.) | – |
| Galleria Bronda | Annankatu 16 | `bronda.fi` | ti–pe 11–17, la–su 12–16 | – |
| Galleria Duetto | Kalevankatu 15 | `galleriat.net/duetto` antaa 404 | – | – |
| Gallery Halmetoja | Kalevankatu 16 | `galleryhalmetoja.com` (stadissa antaa saman) | ti–pe 11–18, la–su 12–16, ma kiinni | – |
| Galerie Forsblom | Lönnrotinkatu 5 (sisäänkäynti Yrjönkatu 22) | `galerieforsblom.com` | ti–pe 11–18, la–su 12–16, ma kiinni / sopimuksen mukaan; 6.12. kiinni | ilmainen (sivun mukaan galleriaan ei ole pääsymaksua) |
| Galleria Pirkko-Liisa Topelius | Hietalahdenranta 17 | `galleriatopelius.com`: yleisesittely, ei aikoja eikä näyttelyitä, vain puhelin 044 010 1167 | – | – |
| Forum Box | Ruoholahdenranta 3 A | `forumbox.fi` | ti–su 12–17, ma kiinni | – |
| Galleria Katariina | Rikhardinkatu 1 | `helsingintaiteilijaseura.fi` | ti–pe 11–17, la–su 12–16 (HTS: 8.11., 6.12., 24.–27.12., 31.12.–3.1. ja 6.1. kiinni) | – |
| OHO Gallery | Pursimiehenkatu 29 A, 4. krs | `ohogallery.com` | ti–pe 13–16 tai sopimuksen mukaan | – |
| Taidesalonki – Konstsalongen | Bulevardi 3 B, 4. krs | `taidesalonki.com`: ohjaus `www.`-osoitteeseen jää silmukkaan, sivu ei aukea | – | – |
| Artegrafica | Museokatu 3 | `artegrafica.com` ohjaa tyhjälle `/lander`-sivulle (pysäköity) | – | – |
| Galeria Oksasenkatu 11 | Oksasenkatu 11 | `oksasenkatu11.fi` | näyttelykohtaisesti: nyt pe–su 14–18 | – |
| Galleria Huuto | Panimokatu 1, 2. krs | `galleriahuuto.fi` | ti–su 12–18 | – |
| Galleria 68 | Hämeentie 68 | `galleria68.com` | ke–to 12–18, pe–su 12–16, ma–ti kiinni | – |

- Stadissa-listalla on 19 riviä (ei 20), ja siinä on vanhentuneita osoitteita: Artegrafica, Duetto, Taidesalonki ja Art Kaarisilta eivät toimi. Älä listaa niitä, ellei haku löydä ajantasaista näyttelyä.
- Samalla Annankadun osoitteella (Annankatu 16) on kaksi galleriaa (G 12 ja Bronda), ja Rikhardinkatu 1:ssä Ama ja Katariina.

## Pysyvät näyttelyt

Isojen museoiden aukioloajat ja hinnat tulevat skriptin kautta museot.fistä (lähde 2); arvo `–` tarkoittaa, ettei sitä löytynyt. Tiedot tarkistettu 16.11.2026. Museoiden omat sivut täydentävät, jos museot.fi ei anna aikoja.

- **Ateneum**: `https://ateneum.fi/`. Suomen taiteen kokoelma on pysyvä perusnäyttely, vaihtuvat näyttelyt erikseen. Ilmaispäivät: –.
- **Kiasma**: `https://kiasma.fi/`. Kokoelmanäyttelyt ja vaihtuvat näyttelyt. Stadissan mukaan Kiasmassa on ilmaispäiviä, päivät: –.
- **Kansallismuseo**: `https://kansallismuseo.fi/`. Pysyvä Suomen historia -näyttely ja vaihtuvat näyttelyt. Ilmaispäivät: –.
- **HAM Helsingin taidemuseo**: `https://www.hamhelsinki.fi/`. Vaihtuvat näyttelyt ja kokoelma. Ilmaispäivät: –.
- **Amos Rex**: `https://amosrex.fi/`. Vaihtuvat näyttelyt, ei perusnäyttelyä. Hinnat ja aukioloajat: museot.fi tai omat sivut.
- **Design Museum / Arkkitehtuuri- ja designmuseo**: `https://www.designmuseum.fi/`. Pysyvä Designin tarina -näyttely (`–` jos museot.fi ei listaa) ja vaihtuvat näyttelyt (esim. `Aalto Design – Hyvinvoinnin muodot`, 5.6.2026–6.1.2027). Sivun mukaan ilmainen sisäänpääsy kerran kuussa, päivä: –.
- **Helsingin kaupunginmuseo**: `https://www.helsinginkaupunginmuseo.fi/`. Pysyvä Helsinki-näyttely ja vaihtuvat näyttelyt (esim. `PUNK! 50 vuotta säpinää Helsingin kaduilla`). Sivulla on ilmaispäiviä tapahtumina (esim. 27.11.2026 klo 11–17), pysyvä ilmaispäiväsääntö: –.

## Sudenkuopat

- **Linked Eventsin ajat ovat UTC:tä.** `start_time` voi olla edellisen päivän 21:00 tai 22:00 (talvi- ja kesäaika): muunna `Europe/Helsinki`-aikaan, tai alku on päivää liian aikainen.
- **Ilman `division=helsinki`-rajausta tulee Espoon kirjastoja** (Sello, Tapiola, Entresse). Rajaus on pakollinen.
- **Päivittäiset alitapahtumat kopioivat näyttelyn.** Näyttely, jolla on `super_event`, voi tulla yhtenä yhden päivän rivinä per päivä sekä yhtenä koko jakson rivinä. Pudota yhden päivän rivit ja pidä koko jakson rivi. Pudota myös nimet, joissa on `kierros`, `työpaja`, `opastus`, `luento`, `esittely`, `tapaaminen`.
- **Paikkasääntö.** Pudota haarakirjastot ja asukas- ja yhteisötalot, seniorikeskukset yms. Pidä Oodi ja kulttuurikeskukset: Stoa, Malmitalo, Caisa, Kanneltalo, Annantalo, Maunula-talo, Vuotalo, Savoy.
- **Sama paikka eri nimellä kahdessa lähteessä.** Esim. `Helsingin taidemuseo HAM` (Linked Events) ja `HAM Helsingin taidemuseo` (museot.fi), samoin LUOMUS. Yhdistä nimen ja paikan mukaan aliaslistalla, ja pidä rivi, jossa on aukioloajat, hinta ja linkki.
- **museot.fin varmenne.** Ilman mukana tulevaa välivarmennetta curl ja Python epäonnistuvat. Käytä `certs/telia-rsa-dv-ca-v4.pem`, älä koskaan `-k`.
- **museot.fissa ei ole kaupunkisuodatinta.** Skripti hakee maakunnan Uusimaa ja suodattaa kortit `<span class="kunta">Helsinki</span>`-tekstillä (Espoo, Vantaa ym. putoavat pois).
- **Verkkonäyttelyt pois.** Pudota nimet, joissa on `Verkkonäyttely`, sekä online-paikat.
- **Galleriat, joiden sivut eivät toimi:** Art Kaarisilta (päättänyt toimintansa 6/2025), Duetto (404), Taidesalonki (ohjaussilmukka), Artegrafica (pysäköity), Topelius (ei näyttelyitä sivulla). Älä keksi niille aikoja.
- **Galleriat vaihtavat näyttelyä:** G 12 on kiinni vaihtoviikkoina (18.–19.11., 9.–10.12., 23.12.–6.1.), Forsblom 23.–26.11. ja 6.12. Aukioloajat poikkeavat myös itsenäisyyspäivänä 6.12.
- **Linked Eventsin rajapinta ei takaa täydellisyyttä.** Gallerian oma sivu on tuoreempi: jos näyttely puuttuu, tarkista lähteestä 3.
