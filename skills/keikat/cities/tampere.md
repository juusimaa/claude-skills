# Tampere

## Skriptit

`tiketti.py --city Tampere` ja `paikat_tampere.py` rinnakkain. Tiketin etusivulla on noin 172 tapahtumaa, joten Tampereella Tiketti kattaa suurimman osan keikoista (Tavara-asema, Tullikamari, Telakka, Vastavirta).

`paikat_tampere.py` lukee neljän paikan omat ohjelmasivut tavallisella HTTP-haulla (`--only tullikamari,tavara,telakka,vastavirta`). Tullikamarin ja Tavara-aseman rivit tuovat hinnan samoille keikoille, jotka Tiketti listaa ilman hintaa.

- `tullikamari` (tullikamari.fi/ohjelma/): koko ohjelma yhdellä sivulla ilman sivutusta, myös Pakkahuone ja Klubi (venue-kenttä). Hinta on tekstinä, esim. "alk. 20€ / Ovelta 25€" tai pelkkä "Ovelta 8€"; ilmainen on "Ilmainen"; loppuunmyyty näkyy hintana "Loppuunmyyty". `category` on Konsertti/keikka, Yökerho tai Muu julkinen tapahtuma. `time_info` sisältää ovet ja pääesiintyjän alkamisajan. Suodata pois Yökerho-rivit (DJ-illat) ja Muu julkinen tapahtuma (esim. vapaaehtoismessut); Pakkahuoneen "Tanssit"-torstait ovat kategoriassa Konsertti/keikka, joten ne pitää tunnistaa nimestä. Yhdellä rivillä (Tarja Turunen 23.2.2027) sali puuttuu sivulta, joten venue on "Tullikamari" eikä ovia ole.
- `tavara` (tavara-asema.fi/ohjelma/): sama sivupohja ja hintamuoto kuin Tullikamarilla, sali on aina "Tavara-asema". Mukana arkipäivien "Päivähypyt"-päivätanssit (ovelta 12 €), disco- ja klubi-illat sekä Orion-tyyppiset yötapahtumat; suodata nimestä. Päivässä ei ole vuotta, se luetaan linkin lopusta.
- `telakka` (telakka.eu/ohjelma/): vapaamuotoinen tekstisivu. Hinta on esim. "15 €", "Ilmainen" (Vapaa pääsy) tai "Loppuunmyyty"; linkki on Tiketin sivu, jos sellainen on, muuten ohjelmasivu. Vuotta ei kerrota, vaan se päätellään (vuosi vaihtuu omalla "2027"-rivillä). Telakan 2. kerroksen tapahtumat (runoilta, päivätanssit) ovat venue-kentässä "Telakka (2. kerros)". Mukana puheohjelmaa, jameja ja DJ-iltoja; suodata nimestä.
- `vastavirta` (vastavirta.net): etusivun tapahtumalohkot. Hinta on esim. "10 €", "15 € / 18 €" tai "Ilmainen"; jos sivulla lukee vain "Liput: €", price on tyhjä. Venue on "Vastavirta-Klubi (alakerta)" tai "Terassi Pub Yläkerta". Nimi sisältää usein bändien soittoajat suluissa. Linkki on Facebook-tapahtuma tai etusivu; ennakkolippujen osoite on kentässä `tickets_url`. Tietovisat ja DJ-illat ovat mukana, suodata nimestä.

## Songkick

https://www.songkick.com/metro-areas/28834-finland-tampere/this-month sekä muut kuukaudet muodossa `.../december-2026`.

Metroalue on kattava vain isoille keikoille (etusivulla noin 36 tapahtumaa, 13.11.2026 alkaen), joten sitä ei kannata pitää ainoana lähteenä. Alueella on myös naapurikuntien paikkoja, esim. Ylöjärvi ja Laukon kartano (Vesilahti). Rajaa pois paikat, jotka eivät ole Tampereella.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Tavara-asema | https://tavara-asema.fi/ohjelma/ | Tiketti | hintaa ei ole sivulla, vain "Liput"-linkki; muuta kuin musiikkia on vähän (kirpputori, pakohuone); skripti |
| Pakkahuone (Tullikamari) | https://tullikamari.fi/tapahtumat/ | Tiketti | sama sivu kattaa Pakkahuoneen ja Klubin; hinta näkyy tekstinä (esim. "alk. 20 €", "ovelta 25 €"); sivulla myös tansseja ja vapaaehtoismessut; skripti |
| Klubi (Tullikamari) | https://tullikamari.fi/tapahtumat/ | Tiketti | pienempi sali, sama ohjelmasivu kuin Pakkahuoneella; loppuunmyynti merkitty "Sold out"; skripti |
| Nokia Arena | https://www.nokiaarena.fi/tapahtumat | Lippu.fi | iso osa on urheilua (Tappara, salibandy, taitoluistelu), suodata; hintaa ei näy |
| Tampere-talo | https://www.tampere-talo.fi/tapahtumat/ | ei tiedossa | ohjelma latautuu JavaScriptillä, käytä hakua; mukana ooppera, baletti ja komiikka |
| Tampere Filharmonia (Tampere-talo) | https://www.tamperefilharmonia.fi/konsertit/ | oma (Liput ja hinnat -sivu) | hintaa ei ole listassa; konsertit pääosin Tampere-talossa |
| G Livelab Tampere | https://glivelab.fi/tampere/ | oma | pääosin keikkoja; hintaa ei näy, ostolinkki "Osta liput" tai "loppuunmyyty" |
| Telakka | https://www.telakka.eu/ohjelma/ | Tiketti | hinta tekstinä tai "Vapaa pääsy"; mukana puheohjelmaa, runoilta, tanssit, jamit; skripti |
| Vastavirta-klubi | https://vastavirta.net/ | Tiketti | hinta tekstinä, moni ilta ilmainen; mukana tietovisat ja DJ-illat (Terassi Pub Yläkerta); skripti |
| Bar Kotelo | https://barkotelo.fi/keikat/ | ovelta / Liveto | hinta tekstinä ("liput: 10 €"), ovelta lisäksi eteispalvelumaksu 3 € |
| Hakametsän jäähalli | haku | ei tiedossa | isoja keikkoja, esim. Stratovarius 20.11.2026; urheilua suodatettava |
| Olympia-kortteli | https://olympiakortteli.fi/keikat/ | Lippu.fi | SULJETTU 30.9.2026 alkaen, älä listaa keikkoja |
| Bar Ihku, Katubaari Axu, Muovitehdas, Varjobaari, Pub Armo, Maanalainen, Ttt-klubi | haku | vaihtelee | pieniä klubeja ja baareja, jotka näkyvät Songkickissä; omia ohjelmasivuja ei löytynyt toimivina |
| Ratinanniemi | haku | vaihtelee | kesän festivaalit (Blockfest 21.8.2027) |
| Tampereen Tuomiokirkko, Kalevan kirkko | haku | vaihtelee | kirkkokonsertit |

Muita: Tampere Jazz Happening (loka–marraskuun vaihde) ja Tampereen Musiikkijuhlat https://tamperemusicfestivals.fi/.

## Lipunmyynti

Lippu.fi / Ticketmaster (Nokia Arena, Olympia-kortteli), Tiketti (Tavara-asema, Tullikamari, Telakka, Vastavirta), Liveto (Bar Kotelo). Hae tarvittaessa hakulauseella "<artisti> Tampere liput".

## Kaupungin kalenterit

- https://tapahtumat.tampere.fi/fi-FI on Tampereen virallinen tapahtumakalenteri (myös visittampere.fi/en/events/ ohjaa sinne). Sisältö latautuu JavaScriptillä (AngularJS), eikä WebFetch saanut siitä luettavaa sisältöä, joten käytä hakua.
- tampere.fi/ajankohtaista on uutissivu, ei tapahtumakalenteri.

## Paikallismedia

- Aamulehti: menovinkit eivät auenneet WebFetchillä, käytä WebSearchia (esim. "Aamulehti viikon menot Tampere").
- Tamperelainen: keikka-arviot https://www.tamperelainen.fi/aihe/Keikka-arviot, ei menokalenteria.
- Aviisi (Tampereen ylioppilaslehti): https://www.aviisi.fi/category/menot/ (sisältöä ei tarkistettu).

## Sudenkuopat

- Olympia-kortteli suljettiin 30.9.2026, mutta Songkickissä ja lipunmyyntisivuilla voi yhä näkyä sen keikkoja (Songkickissä kaksi paikkaa: Olympia-Kortteli ja Olympia Tampere). Tarkista, että keikka ei ole peruttu.
- pakkahuone.fi ei vastaa (ei osoitetta) ja klubi.net ei avaudu (varmenne vanhentunut). Käytä tullikamari.fi (tullikamari.net ohjaa sinne).
- poikkeus.fi on jyväskyläläinen mainostoimisto, ei tamperelainen klubi. kehraamo.fi on tamperelainen joogastudio.
- yo-talo.fi: Tampereen ylioppilastalo on ollut suljettuna yleisöltä kesästä 2024.
- barihku.fi on yleinen Ihku-ketjun sivu, jossa ei ole Tampereen ohjelmaa; katubaariaxu.fi ja muovitehdas.fi eivät ole keikkapaikkojen sivuja.
- jerunpiilopaikka.fi (Pub Jerun Piilopaikka, Hämeenkatu 10) näytti vanhentuneita tapahtumia (huhti–toukokuu 2026) eikä keikkoja.
- Naapurikunnat (Nokia, Ylöjärvi, Lempäälä, Kangasala, Pirkkala, Vesilahti) eivät kuulu Tampereeseen.
