# Hämeenlinna

## Skriptit

Vain `tiketti.py --city Hämeenlinna`. Tiketin etusivulla on Hämeenlinnasta noin 28 tapahtumaa, pääosin Suistoklubin keikkoja, joten Tiketti kattaa klubikeikat hyvin mutta ei Verkatehtaan isoja konsertteja (ne myydään Lippu.fi:ssä).

## Songkick

Hämeenlinnalla on oma metroalue: https://www.songkick.com/metro-areas/60196-finland-hameenlinna/2026 (kuukausittain `.../december-2026`; `this-month` ei tarkistettu). Kattavuus on heikko: sivulla oli vain kaksi tulevaa keikkaa (Suisto, Verkatehdas), vaikka Suistossa on yli 20. Käytä vain täydennyksenä. Sivu vastaa WebFetchille, mutta curl saa 406.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Suistoklubi (Viipurintie 4) | https://www.suisto.fi/ | Tiketti, joitain Lippu.fi | koko ohjelma tekstinä etusivulla (päivä, kellonaika, "Osta liput"-linkki, "LOPPUUNMYYTY" tekstinä); hintaa ei listassa, se on Tiketin sivulla; Suiston Musavisa-torstait ovat ilmaisia visailuiltoja eivätkä keikkoja |
| Verkatehdas (Vanaja-sali, Lasipiha, Werkki) | https://www.verkatehdas.fi/tapahtumat/ | Lippu.fi | lista latautuu JavaScriptillä (HTML:ssä ei tapahtumia), mutta etusivulla on osa tapahtumista ja tapahtumasivut (esim. `/tapahtumat/j-karjalainen-juhlakevat-2027/`) näyttävät hinnan tekstinä ("Peruslippu 49,90 €"); mukana teatteria, stand-upia, tanssia ja pikkujouluja |
| Hämeenlinnan Teatteri | https://www.hmlteatteri.fi/ | Lippu.fi | esitykset Verkatehtaalla; musikaaleja, vain osa musiikkia |
| Albertin Kellari (Ravintola Piparkakkutalo) | https://ravintolapiparkakkutalo.fi/albertin-kellari/ | – | musiikkipubi, viikoittain livemusiikkia, vapaa pääsy; kuukausilista tekstinä (Pe/La klo 21.30), hintaa ei |
| Tuuloksen Kapakanmäki (Tuulos) | https://www.kapakanmaki.fi/ | vaihtelee | tanssilava Tuuloksessa (kuuluu Hämeenlinnaan); tapahtumalista latautuu JavaScriptillä, käytä hakua |

Muita Songkickissä näkyviä paikkoja, joille ei löytynyt omaa ohjelmasivua: Aulanko Areena, Kaima, Linnanpuisto (Mellakka-festivaali), Sibeliuksen Syntymäkoti (Hauhon musiikkijuhlat). Bar Skogster (barskogster.fi) on baari ilman ohjelmasivua.

## Lipunmyynti

Tiketti (Suistoklubi), Lippu.fi (Verkatehdas, Hämeenlinnan Teatteri). Verkatehtaan lipunmyynti: https://www.verkatehdas.fi/lipunmyynti/. Fienta ja Eventim: Ei tiedossa.

## Kaupungin kalenterit

- hameenlinna.fi/vapaa-aika-ja-matkailu/tapahtumat/: kaupungin sivu, tapahtumat latautuvat JavaScriptillä (sivulla näkyy mallipohjan {{ }}-tekstiä), ei käytettävissä automaattisesti.
- visithameenlinna.fi ohjaa hameenlinna.fi:n Visit Hämeenlinna -sivulle, jossa ei ole tapahtumalistaa. visithame.fi (Visit Häme) on matkailun sivusto ilman keikkakalenteria.
- Menoinfo (hame.menoinfo.fi): palautti virhesivun, JavaScript-sovellus, ei käytettävissä.

## Paikallismedia

Hämeen Sanomat (hameensanomat.fi) vastaa; aihesivu https://www.hameensanomat.fi/aihe/Muusikot_bändit toimii, mutta viikon keikkalistaa ei löytynyt. Menoinfo ei toimi automaattisesti.

## Sudenkuopat

- Hattula, Janakkala ja Hauho: Hauho kuuluu Hämeenlinnaan (Hauhon musiikkijuhlat), Hattula ja Janakkala eivät. Tuulos kuuluu Hämeenlinnaan.
- Hämeenlinnan kaupunginorkesteri on lakkautettu. Sinfonia Lahti esiintyy Verkatehtaalla, ja ne ovat Sinfonia Lahden konsertteja.
- verkatehdas.fi/tapahtumakalenteri/ antaa 404, oikea osoite on /tapahtumat/.
- Suistoklubin vanha osoite suistoklubi.fi antaa 404, käytä suisto.fi.
- Suistossa on torstaisin Musavisa, joka ei ole keikka; samoja keikkoja voi olla sekä Tiketissä että Suiston omalla sivulla.
- Hämeenlinnan Teatterin ja Verkatehtaan listalla on paljon muuta kuin musiikkia (musikaalit, stand-up).
