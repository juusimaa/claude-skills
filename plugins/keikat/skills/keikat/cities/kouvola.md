# Kouvola

## Skriptit

Vain `tiketti.py --city Kouvola`. Tiketin etusivulla on Kouvolasta vain noin 3 tapahtumaa (osa kirjattu Kuusankoskelle, ja skripti hakee ne mukaan automaattisesti), joten Tiketti kattaa vain murto-osan keikoista.

## Songkick

Kouvolalla on oma metroalue: https://www.songkick.com/metro-areas/53701-finland-kouvola/this-month sekä muut kuukaudet muodossa `.../december-2026`. Kattavuus on heikko: sivulla oli vain kaksi tulevaa keikkaa (Haitaritehdas Areena, Kouvola-talo), eikä House of Rockin ja Pation ohjelmaa näkynyt. Käytä Songkickia vain täydennyksenä. Sivu vastaa WebFetchille, mutta curl saa 406.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| House of Rock (Asemakatu 1) | https://houseofrockbar.fi/tapahtumat/ | Seat4.Me | lista tekstinä (päivä, kellonaika), hinta vasta tapahtumasivulla ("Ennakkoon 16 € + toimitusmaksu, ovelta 20 €"); sama lista myös etusivulla; mukana myös ilmaisia PKMO-keskiviikkoklubeja |
| Pato Klubi ja Pato Areena (Taideruukki, Kuusankoski) | https://www.patoklubi.fi/tapahtumat | vaihtelee | sivun tapahtumalista ei näy automaattiselle haulle (JavaScript), käytä hakua; visitkouvola.fi:ssä on tapahtumasivuja hinnoin (esim. 30–38 €) |
| Kuusankoskitalo (Kuusaasali, Voikkaasali) | https://www.kouvolantapahtumatalot.fi/etusivu/talojen-tapahtumat/ | Lippu.fi, Ticketmaster, Tiketti | kalenteri latautuu JavaScriptillä (lista tyhjä HTML:ssä), käytä hakua; sama kalenteri kattaa Kouvolatalon |
| Kouvolatalo (Simelius-sali, Honkasali) | https://www.kouvolantapahtumatalot.fi/etusivu/talojen-tapahtumat/ | Lippu.fi, Ticketmaster, Tiketti | kuten yllä; Songkickissä "Kouvola-talo" |
| Kymi Sinfonietta | https://kymisinfonietta.fi/konsertit/ | Lippu.fi | lista tekstinä, hinta usein rivillä (esim. "30/25/15 €"); suurin osa konserteista on Kotkassa, ota vain Kouvolan paikat (Kuusankoskitalo, Kouvolatalo, Kouvolan kaupungintalo, Pato Areena, Kouvolan Teatteri) |
| Kouvolan Teatteri (KT-Klubi) | https://kouvolanteatteri.fi/kalenteri/ | teatterin oma | pääosin teatteria; musiikkia vain satunnaisesti, hintaa ei listassa |
| Haitaritehdas Areena | haku | vaihtelee | löytyy Songkickistä (esim. Lasten hautausmaa 13.11.2026); omaa sivua ei tarkistettu |

## Lipunmyynti

Lippu.fi / Ticketmaster (kaupungin talot ja Kymi Sinfonietta), Seat4.Me (House of Rock), Tiketti. Fienta ja Eventim: Ei tiedossa. Kaupungin talojen lippusivu: https://www.kouvolantapahtumatalot.fi/etusivu/talojen-tapahtumat/lipunmyynti/

## Kaupungin kalenterit

- visitkouvola.fi/tapahtumat/: tapahtumalista ei näy HTML:ssä (latautuu JavaScriptillä Kymenlaakso NYT -palvelusta). Yksittäiset tapahtumasivut (`visitkouvola.fi/?p=...`) löytyvät hakukoneella ja sisältävät hinnan.
- kouvola.fi/vapaa-aika/tapahtumat/: kaupungin sivu, ei keikkalistaa.
- kymenlaaksonyt.fi ja kymenlaakso.menoinfo.fi: JavaScript-sovellus, palautti virhesivun, ei käytettävissä.
- kouvolantapahtumatalot.fi: kalenteri JavaScriptillä.

## Paikallismedia

Kouvolan Sanomat: https://www.kouvolansanomat.fi/aihe/Konsertit vastaa ja listaa konserttiuutisia, mutta ei viikon keikkalistaa. Menoinfo (kymenlaakso.menoinfo.fi) ei toimi automaattisesti.

## Sudenkuopat

- Kuusankoski, Valkeala, Elimäki, Jaala ja Anjalankoski kuuluvat Kouvolaan. Keikat voivat olla näillä nimillä (esim. Kuusankoskitalo, Pato Klubi).
- Kotka, Hamina ja Kymin kirkko, Kyminlinna sekä Kotkan Konserttitalo ovat Kotkassa. Kymi Sinfoniettan kalenterissa on paljon Kotkan konsertteja, joten tarkista paikka.
- pato.fi on Tervakosken Pato -urheiluseura; Pato Klubin osoite on patoklubi.fi. patoklubi.fi/events antaa virheen "Incorrect Order Link".
- kuusankoskitalo.fi ja kouvolatalo.fi ohjaavat osoitteeseen kouvolantapahtumatalot.fi. kouvola-talo.fi ei vastaa.
- Pato Klubin Songkick-sivulla ei ole tulevia keikkoja, vaikka klubilla on niitä: Songkick ei kata Kouvolaa hyvin.
