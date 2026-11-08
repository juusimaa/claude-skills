# Espoo

## Skriptit

Vain `tiketti.py --city Espoo`. Tiketin etusivulla on Espoolle nyt vain noin 8 tapahtumaa, joten kattavuus on heikko ja loput pitää hakea paikkojen omilta sivuilta ja Songkickista.

## Songkick

Espoolla ei löytynyt omaa metroaluetta. Espoon keikat ovat Helsingin metroalueella: https://www.songkick.com/metro-areas/28825-finland-helsinki/this-month sekä muut kuukaudet muodossa `.../december-2026`. Erota Espoon keikat paikan nimen mukaan: Espoo Metro Areena, Pub Olarin Ossi, Olarin Panimo, Nousuvesi, Sellosali, Tapiolasali, Louhisali, Kannusali, Hybridiarena Hype, Vermo Areena ja Vermon Tapahtumapuisto (kaksi viimeistä näkyivät hakutuloksissa, ei tarkistettu). Songkick palauttaa curlille 406, mutta WebFetch lukee sen. Marraskuun alueen listassa Espoon paikkoja oli vain Pub Olarin Ossi ja Nousuvesi.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Espoon kulttuurikeskus (Tapiolasali, Louhisali) | https://www.espoo.fi/fi/espoon-kulttuurikeskus/espoon-kulttuurikeskuksen-tapahtumat | Lippu.fi, Ticketmaster, kassa (Kulttuuriaukio 2) | lista latautuu JavaScriptillä, käytä hakua; Tapiolasali on konserttisali, Louhisali teatteripainotteinen |
| Sellosali (Leppävaara) | https://www.espoo.fi/fi/sellosali | espoo.fi/fi/sellosalin-lipunmyynti | tapahtumat näkyvät HTML:ssä, ei hintoja, `LOPPUUNMYYTY` otsikossa; mukana lastenkonsertteja |
| Kannusali (Tapiola) | https://www.espoo.fi/fi/kannusali | espoo.fi/fi/kannusali/kannusalin-lipunmyynti | tapahtumat HTML:ssä, ei hintoja; mukana elokuvia, stand-upia ja päivätansseja |
| Hybridiarena Hype | https://hypeareena.fi/fi/tapahtumat/tulevat-tapahtumat | Ticketmaster | tapahtumalista ei latautunut, hae Linked Eventsistä (Hype Live -keikat 59,90 €) tai haulla; mukana stand-upia ja urheilua |
| Espoo Metro Areena | https://www.metroareena.fi/tapahtumat/ | Ticketmaster | tapahtumat HTML:ssä, ei hintoja; lähes kaikki jääkiekkoa ja koripalloa, konsertteja harvoin |
| Olarin Panimo (Konepaja Taproom) | https://olarinpanimo.fi/tapahtumat/ | oma | ei hintoja; panimo, musiikkia vain satunnaisesti |
| Pub Olarin Ossi, Nousuvesi | haku | ei tiedossa | pieniä baarikeikkoja (Olarin Ossi lähinnä metallia), omia ohjelmasivuja ei löytynyt; käytä Songkickia |

Tapiolasalin ja Louhisalin ohjelmaa ei saatu luettua suoraan, joten hae niiden keikat WebSearchilla ("Tapiolasali konsertit <kuukausi> <vuosi>") ja Songkickista.

## Lipunmyynti

Lippu.fi ja Ticketmaster (Kulttuurikeskus, Metro Areena, Hype), kaupungin omat salit myös espoo.fi:n lipunmyyntisivuilla. Tiketissä on vähän Espoon tapahtumia.

## Kaupungin kalenterit

- https://www.espoo.fi/fi/tapahtumat-espoossa: kaupungin kalenteri, sisältö latautuu JavaScriptillä (HTML:ssä ei tapahtumia). Yksittäisten tapahtumien osoite on muotoa `https://www.espoo.fi/fi/tapahtumat/espooevents:<id>`.
- https://www.visitespoo.fi/: etusivu vastaa, tapahtumasivun osoitetta ei löytynyt (`/fi/tapahtumat` palauttaa 404).
- Linked Events: https://api.hel.fi/linkedevents/v1/event/?start=<alku>&end=<loppu>&keyword=yso:p11185&division=espoo&sort=start_time&include=location&page_size=50. Kattavuus on heikko: marraskuussa 2026 vain kolme tulosta, ja kulttuurikeskuksen tapahtumat puuttuvat. `starts_after` ei toimi (400).

## Paikallismedia

Länsiväylä (https://www.lansivayla.fi/, myös Espoo-aihesivu `/aihe/Espoo`). Sivulta ei löytynyt keikka- tai menovinkkiosiota. HS:n Espoo-sivu https://www.hs.fi/kaupunki/espoo/ vastaa, sisältöä ei tarkistettu.

## Sudenkuopat

- Espoon omilla kalentereilla ja kulttuurikeskuksen sivulla lista latautuu JavaScriptillä, joten käytä hakua.
- Metro Areenan ohjelma on lähes kokonaan urheilua, ja Hypen ohjelmassa on stand-upia.
- Espoon Songkick-keikat sekoittuvat Helsingin alueeseen, joten rajaa paikan nimellä.
- Marraskuun 2026 alueella Espoossa on vain kourallinen keikkoja, joten pelkkä tyhjä tulos ei tarkoita virhettä.
- Osa Songkickin Espoon paikoista on pienbaareja ilman omaa sivua, ja ohjelmatieto voi olla vanhaa.
