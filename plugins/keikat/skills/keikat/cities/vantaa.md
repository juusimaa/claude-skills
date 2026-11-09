# Vantaa

## Skriptit

`tiketti.py --city Vantaa` ja `linkedevents.py --city Vantaa` rinnakkain. Linked Events tuottaa Vantaalta vähän, lähinnä kirkkojen ja kirjastojen konsertteja; testissä 3 tapahtumaa kuukaudessa, hinta puuttuu usein. Tiketin etusivulla on Vantaalle nyt noin 29 tapahtumaa, joten kattavuus on kohtalainen. Täydennä Martinuksen, Myyrmäen ja Tikkurilan paikoilla.

## Songkick

Vantaalla on oma metroalue: https://www.songkick.com/metro-areas/33583-finland-vantaa/this-month sekä muut kuukaudet muodossa `.../december-2026`. Marraskuun listassa oli vain kolme keikkaa (Rekolan Kino, Myyrmäki Stadion, Myyrmäki Halli). Songkick palauttaa curlille 406, mutta WebFetch lukee sen. Helsingin metroalueella (28825) ei näkynyt Vantaan paikkoja.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Kulttuuritalo Martinus (Myyrmäki) | https://kulttuuritalomartinus.vantaa.fi/fi | Lippu.fi | etusivulla vain osa ohjelmasta, ei hintoja; konsertit, teatteri, elokuvat, tanssi ja lastentapahtumat sekaisin |
| Rekolan Kino (Rekola) | https://www.rekolankino.fi/tapahtumat-kinolla | ei tiedossa | konserttisali, jossa myös elokuvia; listan sisältöä ei luettu; keikat näkyvät myös Songkickissa |
| Lobby Myyrmäki | https://lobbymyyrmaki.fi/keikat/ | https://lobbymyyrmaki.fi/liput/ | keikkoja ja klubi-iltoja (esim. Roll FM Special, After Midnight Sauna Club); hintaa ei etusivulla; mukana myös stand-upia |
| Old Story (Tikkurila) | https://www.oldstory.fi/rokkia | ei lippuja | viikoittain livemusiikkia, vapaa pääsy; ohjelma Facebookissa |
| Vantaan Energia Areena (Myyrmäki) | haku | ei tiedossa | omaa tapahtumasivua ei löytynyt; urheilua ja satunnaisia isoja tapahtumia |
| Myyrmäki Halli ja Myyrmäki Stadion | haku | ei tiedossa | isot keikat Songkickissa; paikka (Halli vai Stadion) voi olla lähteissä ristiriitainen; ei omaa sivua, `myyrmakihalli.fi` ei vastaa |
| Tikkurilan Teatteri / Kulttuuritehdas Vernissa | https://tikkurilanteatteri.fi/esitykset/ | oma | teatteri, ei konsertteja; ei keikkapaikka |

Tikkurila-salia, Kulttuuritalo Lumoa ja Vantaan Energia Areenan omaa ohjelmasivua ei löytynyt. Lumon kirjasto näkyy Linked Eventsissä, mutta se on kirjasto. Pyhän Laurin kirkko (Tikkurila) järjestää konsertteja (esim. 15.11. ja 5.12.).

## Lipunmyynti

Lippu.fi (Martinus, isot keikat), Ticketmaster, Tiketti (Tiketin ~29 tapahtumaa). Lobbyn liput: lobbymyyrmaki.fi/liput/.

## Kaupungin kalenterit

- https://tapahtumat.vantaa.fi/fi-FI: kaupungin kalenteri, lataus tilapäisesti estetty tilitiedotteella eikä HTML:ssä näy tapahtumia (JavaScript). Musiikkisuodatin: https://tapahtumat.vantaa.fi/fi-FI/topic/5cbf089897e55c2ebb856c39?mode=event&count=9 ("Musiikki, keikat ja klubit"), sisältöä ei saatu luettua.
- https://www.vantaa.fi/fi/ajankohtaista/tapahtumat: lähinnä tapahtumauutisia, varsinainen kalenteri on tapahtumat.vantaa.fi.
- https://visit.vantaa.fi/fi: etusivu vastaa, tapahtumalinkki ohjautuu vantaa.fi:n sivulle.
- Linked Events: katso `linkedevents.py --city Vantaa`.

## Paikallismedia

Vantaan Sanomat: https://www.vantaansanomat.fi/aihe/Konsertit sekä viikon menovinkit ("Mitä tehdä Vantaalla"). Sivu oli luettavissa ilman maksumuuria, mutta viikoittaisen listan julkaisutahti ei ole selvä.

## Sudenkuopat

- Vantaan Energia Areena ja Myyrmäki Halli ovat eri paikkoja, ja Songkickin "Energia Areena" ilman kaupunkia on Oulun areena.
- Tikkurilan Teatteri on teatteri, ja `vernissa.fi` on kuopiolainen remonttiyritys. Kulttuuritehdas Vernissan oma sivu ei vastannut.
- Vantaan kaupungin kalenterin sisältö latautuu JavaScriptillä, joten käytä hakua.
- Vauhti kiihtyy -festivaali (Stratovarius, Poets of the Fall ym.) on kesäfestivaali, ei marraskuun keikka.
- Myyrmäen keikoista eri lähteet voivat kertoa eri paikan (Myyrmäki Stadion tai Myyrmäki Halli), joten tarkista paikka.
