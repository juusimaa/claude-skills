# Lahti

## Skriptit

Vain `tiketti.py --city Lahti`. Tiketin etusivulla on Lahdesta vain noin 12 tapahtumaa, joten se kattaa kaupungin keikoista pienen osan. Sibeliustalon, Möysän ja Torven ohjelma on haettava erikseen alla olevista osoitteista.

## Songkick

https://www.songkick.com/metro-areas/28830-finland-lahti/this-month sekä muut kuukaudet muodossa `.../december-2026`. Metroalue on Lahden seutu: listalla oli yksi Heinolan keikka (Iloinen Kulkija), joten jätä pois muut paikkakunnat kuin Lahti. Kattavuus on hyvä isoissa paikoissa (Sibeliustalo, Finlandia-klubi, Torvi, Lahti Halli), mutta Möysän Musaklubi puuttuu tai on vajaa. Sivu vastaa WebFetchille, mutta curl saa 406.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Sibeliustalo (Pääsali, Metsähalli) ja Finlandia-klubi | https://www.sibeliustalo.fi/tapahtumakalenteri/ | Ticketmaster.fi, Lippu.fi | hinta näkyy tapahtumasivulla tekstinä, ei kalenterilistassa; mukana show- ja lastentapahtumia, lounaita ja Yle-tapahtumia, joten suodata |
| Sinfonia Lahti | https://sinfonialahti.fi/konsertit/ | Lippu.fi | lista tekstinä ilman hintoja (hinta konsertin omalla sivulla); konsertit myös Sibeliustalon ulkopuolella (esim. Verkatehdas Hämeenlinnassa, kaupungintalon sisäpiha) |
| Möysän Musaklubi (Mössö) | https://moysa.fi/tapahtumat/ | Lippu.fi | päivät ja artistit tekstinä, hintaa ei listassa; sivulla myös pikkujoulu- ja festivaalilinkkejä |
| Ravintola Torvi ja Tirra (Loviisankatu 8) | https://ravintolatorvi.fi/tapahtumat/ | Lippu.fi | hinta tekstinä ("ennakkoon 14 €, ovelta 17 €"); sivulla myös karaokea ja klubi-iltoja |
| Lahti Halli | haku | Lippu.fi / Ticketmaster | iso areena (esim. Stratovarius ja Klamydia 4.12.2026); omaa sivua ei löytynyt. Isku Areena on nykyisin Wemasto Areena (Wikipedian mukaan), mutta ei varmistettu, onko se sama paikka |
| Lahden Konserttitalo | https://lahdenkonserttitalo.fi/tapahtumat/ | ulkopuolinen myyjä (linkki sivulla) | vain muutama tapahtuma kerrallaan, hinta tekstinä (esim. 39–65 €); Konservatorion konsertit ovat Concis-sivuilla |
| Teatteri Vanha Juko, JukoKlubi (Rautatienkatu 13) | https://teatterivanhajuko.fi/kalenteri/ | Lippu.fi tai teatterin oma | kalenterissa teatteria, komediaa ja musiikkia; ota vain `JukoKlubi`-rivit; hintaa ei listassa. WebFetch saa 403, curl toimii |
| Lahti Jazz Club (Teerenpeli, Vapaudenkatu 20) | https://www.lahtijazz.fi/tapahtumat | – | klubi joka kuun toinen tiistai, ohjelma on kuvana tai alasivulla, ei tekstilistaa |
| Opiston Kunkku, Ristinkirkko, Niemen Satama (Headland-festivaali) | haku | vaihtelee | löytyvät Songkickistä; omia sivuja ei tarkistettu |

## Lipunmyynti

Lippu.fi / Ticketmaster (Sibeliustalo, Sinfonia Lahti, Möysä, Torvi, Lahti Halli) on tärkein. Ticketmaster.fi myy samoja Sibeliustalon lippuja. Tiketti on harvinaisempi. Fienta ja Eventim: Ei tiedossa.

## Kaupungin kalenterit

- visitlahti.fi/etusivu/tapahtumat/musiikkia/: matkailun musiikkisivu, teksti näkyy suoraan HTML:ssä, mutta se on lähinnä paikkaesittely ja suppea tapahtumalista. Yleinen tapahtumasivu https://visitlahti.fi/etusivu/tapahtumat/ vastaa, mutta HTML:ssä ei näkynyt tapahtumalistaa (todennäköisesti JavaScript).
- lahti.fi/vapaa-aika/tapahtumat/: kaupungin omat juhlat (itsenäisyyspäivä, ympäristöviikko), ei keikkakalenteri. Tapahtumat.lahti.fi ei vastannut.
- Menoinfo (hame.menoinfo.fi): ESS ja Hämeen Sanomat käyttävät sitä, mutta sivu palautti virheen ja on JavaScript-sovellus, ei käytettävissä.

## Paikallismedia

Etelä-Suomen Sanomat (ess.fi) vastaa, mutta menovinkkien omaa osoitetta ei löytynyt (/menoinfo ja /aihe/Menoinfo antavat 404). Menoinfo ei toimi automaattisesti. Käytä hakua "ess.fi keikat Lahti".

## Sudenkuopat

- Hollola, Heinola ja Orimattila eivät kuulu Lahteen. Songkickin Lahden metroalueella on Heinolan keikkoja.
- lahtihalli.fi ja tirra.fi eivät vastaa (ei toimivaa osoitetta). `lahdenhalli.fi` on kauppahalli, ei areena.
- Sibeliustalon tapahtumakalenterissa on paljon muuta kuin musiikkia (show, lounaat, Yle-tapahtumat) ja samoja keikkoja useita näytöksiä.
- Sibeliustalon ja Finlandia-klubin keikat näkyvät Songkickissä usein yhdellä rivillä "Sibeliustalo, Finlandia Klubi".
- finlandiaklubi.fi ohjaa Sibeliustalon sivulle; /keikat antaa 404.
- Sinfonia Lahden konsertteja on myös Hämeenlinnassa (Verkatehdas), jolloin ne kuuluvat Hämeenlinnaan.
- Möysä järjestää myös Helsingin pikkujouluja ("Pikkujoulu Mössö Helsinki") ja festareita, jotka eivät ole Lahdessa.
