# Oulu

## Skriptit

Ajetaan rinnakkain `tiketti.py`:n kanssa:

```bash
python3 -I <skillin kansio>/scripts/paikat_oulu.py --months N --table
```

`paikat_oulu.py` lukee hintoineen näiden paikkojen omat ohjelmasivut:
- **Tarkastamo** (Torinranta): hinta on sivun tekstinä (esim. "34,90€ | VIP 44,90€"). Ovelta peritään lisäksi palvelumaksu 4 €, ja ovilippu on 5 € ennakkoa kalliimpi. Kategoriaa ei ole, joten jätä pois muut kuin musiikkitapahtumat itse (esim. taikashow).
- **Tullisali** (Tyrnäväntie 16): kentässä `category` on sivun kategoria. Ota mukaan vain `Musiikki`. Hinta on alin hinta, joten merkitse se muodossa `alk. 33 €`. Ostolinkki (Ticketmaster) on kentässä `tickets_url`.
- **Tuba**: hinta on muodossa "Liput ennakkoon 20 €, ovelta 24 €". Linkki vie yleensä Tiketin tapahtumaan, joten **tästä saa hinnat Tuban Tiketti-keikoille**. Jätä pois brunssit, visat ja muut kuin keikat.
- **Oulu Sinfonia** (oulusinfonia.fi/kaikki-konsertit): Madetojan salin, Ouluhallin, Ravintola Preludin ja muiden paikkojen konsertit. Skripti hakee hinnan konsertin omalta sivulta (esim. "42 € perushinta / 32 € eläkeläinen / 22 € opiskelija…"). Taulukkoon riittää perushinta, esim. `42 € (alennus 22–32 €)`. Kategoria `Vapaa pääsy` tarkoittaa ilmaista. Monipäiväisillä on kenttä `end` ja `time_info` kertoo näytösten määrän. Lista ulottuu yleensä vain muutaman kuukauden päähän.
- **Oulun musiikkikeskus** (Madetojan sali, Pohjankartanon sali, Tulindbergin sali, Pikkusali): skripti lukee musiikkikeskuksen tapahtumakalenterin datan suoraan kaupungin tapahtumapalvelusta (tapahtumat.munoulu.fi). Mukana ovat kaikki tapahtumat eivätkä vain sivulla ensin näkyvät kuusi. Hintaa ja lipputilannetta ei ole, joten jätä `status` tyhjäksi ja hinta `–`, ellei sitä löydy muualta. Linkki vie tapahtumasivulle, jolla on ostolinkki. Peruttujen tapahtumien `status` on `peruttu`. Kalenterissa on paljon muutakin kuin musiikkia (stand-up, taikurit, sirkus, baletti, teatteri, seminaarit), joten suodata. Konservatorion oppilaskonsertit ovat musiikkia ja kuuluvat mukaan. Sama konsertti voi tulla myös Oulu Sinfonialta, joten yhdistä kaksoiskappaleet. Datan osoite on katsottu selaimen verkkoliikenteestä eikä se ole dokumentoitu rajapinta. Jos lähde palauttaa nollan tapahtumaa, hae Madetojan salin tapahtumat WebSearchilla.

`status` on `loppuunmyyty`, jos hintatekstissä lukee "sold out" tai "loppuunmyyty". Tarkista teksti: esim. "VIP 44,90€ (sold out)" voi tarkoittaa, että vain VIP-liput on myyty loppuun. Kerro tällainen epävarmuus alaviitteessä.

Hintojen järjestys vaiheessa 3: ensin `paikat_oulu.py`:n tulos. Saman keikan Tuba-rivillä on myös Tiketti-keikan hinta.

## Songkick

https://www.songkick.com/metro-areas/28832-finland-oulu/this-month sekä muut kuukaudet muodossa `.../december-2026`.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Tarkastamo, Tullisali, Tuba | skripti | Tiketti, Ticketmaster | hinnat skriptistä |
| Madetojan sali ja muut musiikkikeskuksen salit | skripti | Lippu.fi / Ticketmaster | ei hintoja |
| Oulun Energia Areena, Ouluhalli | haku | Lippu.fi / Ticketmaster | isot keikat |
| Tukikohta, 45 Special, Club Teatria, RioLive, Sauna Oulu | haku | vaihtelee | etsi nykyinen osoite hakukoneella |

Lisää paikkoja löytyy hakemalla "keikkapaikat Oulu". Myös Oulun Tapahtumat Oy järjestää keikkoja.

## Lipunmyynti

Lippu.fi / Ticketmaster (Oulun Energia Areena, Ouluhalli, Madetojan sali), Eventim, Fienta.

## Kaupungin kalenterit

- visitoulu.fi/fi/tapahtumat: sisältö latautuu JavaScriptillä, joten käytä hakua.
- ouka.fi/oulu/tapahtumat
- oulu2026.eu/program: Oulu on Euroopan kulttuuripääkaupunki 2026, ja ohjelmassa on paljon ilmaisia keikkoja.

## Paikallismedia

Kaleva ja Oulun Ylioppilaslehti listaavat usein viikon keikat.

## Sudenkuopat

- tukikohta.org on eri järjestö kuin oululainen Tukikohta.
- clubteatria.fi ja 45special.com eivät aina vastaa.
- Raahe ja Kempele näkyvät Tiketissä omina kaupunkeinaan, eivätkä ne kuulu Ouluun.
