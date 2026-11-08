# Jyväskylä

## Skriptit

`tiketti.py --city Jyväskylä` ja `paikat_jyvaskyla.py` rinnakkain. Tiketin etusivulla on noin 21 tapahtumaa (Poppari, Taulumäen kirkko, Tapahtumakeskus Helmi ja Villa Rana, jossa on myös stand-upia), mutta Lutakko, Paviljonki ja useimmat klubit puuttuvat, joten omat ohjelmasivut ovat tärkeämpiä.

```bash
python3 -I <skillin kansio>/scripts/paikat_jyvaskyla.py --months N --table
```

`paikat_jyvaskyla.py` lukee hintoineen kaksi omaa ohjelmasivua:
- **Lutakko** (`--only lutakko`, jelmu.net): hinta on alin–ylin tekstinä (esim. "25,00€ – 33,00€"); merkitse se muodossa `25–33 €`. `status` on `loppuunmyyty`, kun sivulla lukee "Loppuunmyyty!". Kenttä `venue` on sivun oma paikka: Jelmun listalla on Lutakon lisäksi Musta Kynnyksen keikkoja. Skripti poistaa niiden kaksoiskappaleet `mustakynnys`-lähteestä saman linkin perusteella ja pitää Jelmun rivin. `time_info` sisältää ovet, alkamisajan (jos sellainen on) ja ikärajan. Päivässä ei ole vuotta, joten skripti arvaa sen. Esiintyjät ovat pilkulla eroteltuna. DJ-illat ovat musiikkia ja ne pidetään mukana.
- **Musta Kynnys** (`--only mustakynnys`, mustakynnys.com): hinta on tekstinä "Ennakkoliput: 16/15€, Liput ovelta: 20€" (ennakkohinta/alennettu ja ovihinta). Tuntematon ovihinta ("?€") jätetään pois. `time_info` on "showtime 22.00". Linkki vie Jelmun lippukauppaan. Sivulla ei ole vuotta, joten skripti arvaa sen (yli kaksi kuukautta mennyt päivä tarkoittaa ensi vuotta). Sivulla on vain muutama seuraava keikka (bändi- ja DJ-iltoja), mutta kaikki kuuluvat mukaan.

## Songkick

https://www.songkick.com/metro-areas/56206-finland-jyvaskyla/this-month sekä muut kuukaudet muodossa `.../december-2026`. Kattavuus on heikko: this-month-sivulla oli vain kuusi keikkaa, kun Lutakon omalla sivulla on yli 40. Paviljonki näkyy kahtena paikkana (Paviljonki Areena ja Jyväskylän Paviljonki), joten sama tapahtuma voi tulla kahdesti.

## Keikkapaikat

| Paikka | Ohjelmasivu | Lipunmyynti | Huomiot |
|---|---|---|---|
| Tanssisali Lutakko | https://www.jelmu.net/ | Jelmu.net | skripti; hinta näkyy tekstinä (esim. "25,00€ – 33,00€", alin–ylin), "Loppuunmyyty!" tekstinä; yli 40 tulevaa keikkaa, vain musiikkia (myös DJ-iltoja). lutakko.fi näyttää vain viisi seuraavaa |
| Paviljonki | https://www.paviljonki.fi/tapahtumat-liput/ | Lippu.fi | hintaa ei näy sivulla, vain "Osta liput" -painike; mukana messuja, teatteria, stand-upia ja showta, joten suodata sivun kategorialla Konsertit; Jyväskylä Sinfonian konsertteja myös |
| Jyväskylä Sinfonia | https://www.jyvaskylasinfonia.fi/konsertit | Lippu.fi, jyvaskylasinfonia.lippu.fi, Jyväskylä-piste (Asemakatu 7) | hintaa ei sivulla; konserttipaikat vaihtelevat; lista kattaa vain muutaman viikon |
| Musta Kynnys | https://mustakynnys.com/ | Jelmu.net | skripti; ennakko- ja ovihinta tekstinä (esim. "16/15€" ja ovelta 20 €); vain bändi- ja DJ-iltoja; päivämäärissä ei vuotta |
| Poppari | ei omaa sivua tarkistettu (ravintolapoppari.fi, varmennevirhe) | Tiketti | keikat löytyvät Tiketistä; mm. jazzia ja tribuuttikeikkoja |
| Club Escape | https://escapejkl.fi/tapahtumat/ | ei tiedossa | hintoja ei näy; "ESC Live" -keikkojen seassa klubi-iltoja ja bileitä; päivämäärissä ei vuotta |
| London | https://londonjkl.fi/tapahtumat/ | Lippu.fi | hinta joskus tekstinä, usein ei; sivulla enimmäkseen DJ-/diskoiltoja ja coverbändejä, erota keikat niistä; ei vuotta |
| Ylä-Ruth | https://yla-ruth.fi/ | ei tiedossa | etusivulla vain kolme seuraavaa esiintyjää ilman hintoja; ei ohjelmasivua |
| Ilokivi | https://soihtu.fi/ilokivi/ | ei tiedossa | sivulla ei ole ohjelmaa, joten käytä hakua; mukana opiskelijatapahtumia ja muuta kuin musiikkia |
| RockNeck | haku (Songkick-sivu) | ei tiedossa | metalli- ja rock-klubi, Asemakatu 7; omaa sivua ei löytynyt |

Isot yksittäiset keikat (Jyväskylä-areena, Lutakonaukio, Laajavuori) näkyvät Songkickissa ja Tiketissä.

## Lipunmyynti

Lippu.fi / Ticketmaster (Paviljonki, Sinfonia, London), Jelmu.net (Lutakko, Musta Kynnys; oma lippukauppa), Liveto (yritystapahtumat, ei keikkoja). Hakulause: "<artisti> Jyväskylä liput".

## Kaupungin kalenterit

- https://kalenteri.jyvaskyla.fi/ (Keski-Suomen tapahtumakalenteri): Next.js-sovellus, tapahtumat näkyvät palvelinpuolella HTML:ssä, mutta suodattimet (esim. Musiikki) toimivat selaimessa. Sisältö on enimmäkseen ilmaisia ja perhetapahtumia, hintoja ei ole. Data on lisensoitu CC BY 4.0. Kattaa koko Keski-Suomen.
- https://visitjyvaskyla.fi/en/nightlife-in-jyvaskyla/: paikkaluettelo, ei tapahtumia.

## Paikallismedia

- Keskisuomalainen: https://www.ksml.fi/aihe/Konsertit listaa arvioita ja uutisia, mutta viikon menovinkkejä ei löytynyt. keskisuomalainen.fi ohjaa osoitteeseen ksml.fi.
- Jylkkäri (https://jylkkari.fi): ylioppilaslehti, ei säännöllistä menovinkki- tai keikkalistausta.

## Sudenkuopat

- Naapurikunnat eivät kuulu Jyväskylään: Laukaa (Hirviareena, Raskas Joulu), Muurame, Jämsä, Saarijärvi. kalenteri.jyvaskyla.fi näyttää ne kaikki.
- Songkickissä sama Paviljonki-tapahtuma on usein kahtena rivinä (Paviljonki Areena ja Jyväskylän Paviljonki).
- ravintolapoppari.fi ei aukea (varmennevirhe); Popparin keikat haetaan Tiketistä.
- Vanhentuneet sivut: londonjkl.fi ja yla-ruth.fi sisältävät vanhoja julkaisuja (Ylä-Ruthin sivulla vielä koronahuomautus), joten tarkista päivämäärät.
- Kesän festivaalit (Suomipop, Yläkaupungin yö, Jyrock) eivät näy marraskuussa.
