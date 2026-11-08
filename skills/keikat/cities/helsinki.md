# Helsinki

## Skriptit

`tiketti.py --city Helsinki` ja `linkedevents.py --city Helsinki` rinnakkain. Linked Events tuottaa paljon kirjastojen, kirkkojen ja seniorikeskusten ilmaiskonsertteja ja jonkin verran klubikeikkoja (Tavastia, Musiikkitalo), mutta hinta puuttuu usein; testissä noin 158 tapahtumaa kuukaudessa. Tiketin etusivulla on Helsingille noin 316 tapahtumaa, joten kattavuus on hyvä, mutta mukana on myös muuta kuin musiikkia. Isojen areenoiden ja Musiikkitalon keikat myydään pääosin muualla (Lippu.fi, Ticketmaster, omat sivut), joten täydennä niistä hakua ja paikkojen omia sivuja käyttäen.

## Songkick

https://www.songkick.com/metro-areas/28825-finland-helsinki/this-month sekä muut kuukaudet muodossa `.../december-2026`. Helsingin metroalueella on myös Espoon paikkoja (esim. Espoo Metro Areena, Pub Olarin Ossi, Nousuvesi), joten rajaa Helsinkiin paikan nimen mukaan. Vantaalla on oma metroalue. Songkick palauttaa curlille 406, mutta WebFetch lukee sen.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Tavastia | https://tavastiaklubi.fi/ | oma (tavastiaklubi.fi) | hinta tekstinä ("Liput 38,50 € / 40 €"), `Loppuunmyyty` näkyy; mukana levymessut |
| Semifinal | https://tavastiaklubi.fi/semifinal/ | oma (Tavastian sivut) | Tavastian pikkuklubi; hinta tekstinä, myös kerhoiltoja ja `Loppuunvarattu` |
| On the Rocks | https://www.rocks.fi/tapahtumat | Tiketti | hinta tekstinä (`alk.`); mukana klubi-iltoja (disko, Britpop) ja ilmaisia keikkoja |
| Ääniwalli | https://aaniwalli.fi/ | Ticketmaster, Tiketti, Biletti ym. | ei hintoja listassa, vain `Osta liput` -linkki, peruttu merkitty `[PERUTTU]`; myös klubi-iltoja ja festivaaleja |
| G Livelab | https://glivelab.fi/ | oma, `Purchase tickets!` | ei hintoja listassa, `Sold out` näkyy; vain musiikkia |
| Bar Loose | https://barloose.com/live | Tiketti | hinta tekstinä (esim. 10 €, `Vapaa pääsy!`); paljon DJ-iltoja ja karaokea |
| Kuudes Linja | https://www.kuudeslinja.com/ | Tiketti, Eventual, Tickettailor | hinta tekstinä (ennakko / ovelta, lisäksi 3,90 € turvamaksu); myös klubi-iltoja |
| Korjaamo | https://korjaamo.fi/tapahtumat/ | Lippu.fi | hinta tekstinä; mukana komediaa ja elokuvia |
| Storyville | https://storyville.fi/events/ | Tiketti | hinta tekstinä; jazzia, tribuutteja ja ilmaisia jameja; yksityistilaisuuksia ei listassa |
| Kulttuuritalo | https://kulttuuritalo.fi/tapahtumat/ | oma | `Liput alkaen` tekstinä; mukana stand-up ja teatteri |
| Musiikkitalo | https://musiikkitalo.fi/konsertit-ja-tapahtumat | oma | ei hintoja listassa (hinta tapahtumasivulla); paljon klassista, Sibelius-Akatemian oppilas- ja maisterikonsertteja ja muuta ohjelmaa |
| Finlandia-talo | https://www.finlandiatalo.fi/tapahtumat/ | Lippu.fi / Ticketmaster (ei vahvistettu) | ei hintoja; paljon muuta (näyttelyt, brunssit, markkinat, stand-up) |
| Savoy-teatteri | https://www.savoyteatteri.fi/fi/tapahtumat/tapahtumahaku | oma | ei hintoja listassa, `Sold out` näkyy; kategoria kertoo (Musiikki, Teatteri, Kirjallisuus) |
| Kaapelitehdas (Merikaapelihalli ym.) | https://www.kaapelitehdas.fi/tapahtumat/ | vaihtelee | sisältö latautuu JavaScriptillä (ei lue); käytä Songkickia ja hakua; paljon näyttelyitä ja tanssia |
| Veikkaus Arena (ent. Hartwall Arena) | https://www.veikkausarena.fi/all-events | oma | isot keikat; ei hintoja listassa; mukana jääkiekkoa |
| Helsingin Jäähalli (myös Black Box) | https://helsinginjaahalli.fi/events | oma | ei hintoja; konsertit ja HIFK-pelit sekaisin; Black Box -salia ei mainita sivulla, hae sitä Songkickista |
| Olympiastadion | https://www.stadion.fi/fi/tapahtumat/tapahtumat | vaihtelee | ei hintoja; Club Stadion -keikat ja urheilutapahtumat sekaisin |
| Malmitalo | https://www.malmitalo.fi/fi/tapahtumat/tapahtumahaku | oma | ei hintoja; kategoria näkyy; paljon elokuvia ja näyttelyitä |
| Stoa | https://www.stoa.fi/fi/tapahtumat/tapahtumahaku | oma | ei hintoja; lähinnä tanssia, sirkusta ja näyttelyitä, musiikkia vähän |
| Tiivistämö (Suvilahti) | https://tiivistamo.fi/ | vaihtelee | etusivulla ei tapahtumia; keikat löytyvät Songkickista ja Linked Eventsistä |

Muista paikoista: Kaikulle ei löytynyt toimivaa ohjelmasivua (kaiku.com ei vastannut), joten hae sen keikat Songkickista ja WebSearchilla. Nosturi lopetti vuonna 2020. Kulttuuriareena Gloria on olemassa, mutta sille ei tarkistettu ohjelmasivua; gloria.fi on eri asia (lehti). Apollo Live Club ja Hartwall Arenan vanha osoite eivät vastanneet.

## Lipunmyynti

Tiketti (tiketti.fi, pienet ja keskikokoiset klubit), Lippu.fi (Eventim, eventim.fi ohjautuu sinne; Korjaamo, Espoon kulttuurikeskus; sivu ei vastaa automaattiseen hakuun), Ticketmaster (ticketmaster.fi; Ääniwalli), Eventual (eventu.al, klubi-illat; 403 automaattihaulle), Fienta (fienta.com/fi), Biletti ja Tickettailor yksittäisiin keikkoihin. Tavastia, Veikkaus Arena ja Jäähalli myyvät myös omilla sivuillaan.

## Kaupungin kalenterit

- https://tapahtumat.hel.fi/fi: sisältö latautuu JavaScriptillä, joten käytä rajapintaa tai hakua.
- https://www.myhelsinki.fi/fi/nae-ja-koe/tapahtumat: palauttaa 403 curlille, WebFetchillä tapahtumat eivät lataudu (JavaScript). Käytä hakua.
- Linked Events: avoin rajapinta, katso `linkedevents.py` (avainsanat, sivutus ja pitkien tapahtumien suodatus siinä).

## Paikallismedia

HS (https://www.hs.fi/kulttuuri/), City-lehti (https://www.cityfi.com/), Ylioppilaslehti (https://ylioppilaslehti.fi/) ja Time Out Helsinki (https://www.timeout.com/fi/helsinki). Sivut vastaavat, mutta viikon keikkalistoja ei tarkistettu. hs.fi/menovinkit palauttaa 404.

## Sudenkuopat

- Nosturi on purettu (2020). Älä etsi sen keikkoja.
- siltanen.fi on hautauspalvelu, ei Kallion Siltanen. kaiku.fi on yritys, ei klubi. gloria.fi on lehti.
- Musiikkitalossa on oma `Black Box` -tila (oppilas- ja maisterikonsertit), joka on eri paikka kuin Jäähallin Black Box.
- Tavastian ja Semifinalin keikat ovat samalla sivustolla, ja Semifinalin sivulla listassa ei näy paikan nimeä.
- Savoy-, Malmitalo- ja Stoa-sivujen tapahtumalinkit ovat `#!`-osoitteita, jotka toimivat vain selaimessa.
- Veikkaus Arenan listassa ei ole päivämääriä kaikille (esim. NHL Global Series), ja jääkiekko on sekaisin.
- Songkickin Helsingin alueella on Espoon paikkoja ja `Private Event` -rivejä, jotka kannattaa jättää pois.
- Linked Events sisältää enimmäkseen ilmaisia ja kaupungin tapahtumia, ei kaikkia klubikeikkoja.
