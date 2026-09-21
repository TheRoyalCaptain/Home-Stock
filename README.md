# Home Stock

Home Stock is een zelfgehoste voorraad- en houdbaarheidsapp voor thuis. Beheer
producten en losse bakken in je koelkast, vriezer, voorraadkast of eigen
locaties, scan barcodes met je iPhone en print bewaaretiketten rechtstreeks op
een DYMO LabelWriter.

## Belangrijkste functies

- Losse voorraadpartijen met hoeveelheid, locatie, productie- en einddatum
- Vaste locaties: **Koelkast**, **Vriezer** en **Voorraadkast**
- Zelf eigen locaties toevoegen
- Meerdere bakken in één keer invoeren met codes als `VP001-A` en `VP001-B`
- Iedere bak afzonderlijk verbruiken, verspillen, openen of verplaatsen
- Winkelbarcodes opzoeken via Open Food Facts
- Home Stock-codes, EAN, UPC, Code 128 en QR scannen
- Automatische, handmatig aanpasbare houdbaarheidsinschatting
- Optionele Gemini Free Tier-inschatting als lokale regels niet voldoen
- Verbruik, verspilling, prijzen, winkels en statistieken
- Boodschappenlijst, recepten en maaltijdplanner
- Meerdere gebruikers met activiteitshistorie
- Houdbaarheids- en minimumvoorraadmeldingen
- CSV-export en JSON-back-up
- Direct printen op een USB-aangesloten DYMO LabelWriter 400/450
- Door Gemini gemaakte, handmatig aanpasbare bereidingswijze op het label
- Installeerbare iPhone-webapp

## Installeren op Umbrel

1. Open in de Umbrel App Store het menu voor **Community App Stores**.
2. Voeg `https://github.com/TheRoyalCaptain/Home-Stock` toe.
3. Open de nieuwe sectie **Home Stock App Store**.
4. Installeer **Home Stock**.

De images worden automatisch gebouwd voor AMD64 en ARM64. De app gebruikt geen
extra Umbrel-authenticatiescherm. Home Stock opent rechtstreeks zijn eigen
beveiligde inlogpagina.

## Eerste login

- Gebruikersnaam: `admin`
- Wachtwoord: `admin`

Bij de eerste login moet het standaardwachtwoord direct worden vervangen door
een uniek wachtwoord van minimaal 12 tekens. Daarna kan een beheerder via
**Gebruikers beheren** extra accounts aanmaken.

## iPhone-webapp en barcodes scannen

Installeer Home Stock op een iPhone via:

1. Open Home Stock in Safari.
2. Tik op de deelknop.
3. Kies **Zet op beginscherm**.
4. Open Home Stock voortaan via het appicoon.

Voor continu live scannen is HTTPS en cameratoestemming nodig. Via een lokaal
HTTP-adres blijft **Foto scannen** beschikbaar. Cameraframes worden lokaal door
de Home Stock-server met ZXing verwerkt, niet naar een clouddienst gestuurd en
niet opgeslagen.

## Meerdere bakken tegelijk invoeren

Vul bij een gerecht het aantal bakken en de hoeveelheid per bak in. Home Stock
maakt voor iedere bak een eigen voorraadpartij, barcode en optioneel label. Een
artikel met code `VP001` krijgt bijvoorbeeld:

- `VP001-A`
- `VP001-B`
- `VP001-C`

Extra bakken lopen automatisch door met `-D`, `-E` enzovoort. Iedere bak kan
afzonderlijk worden verbruikt zonder de voorraad van de andere bakken te wijzigen.

## DYMO-labels

De Umbrel-app bevat een afgeschermde CUPS-printerservice voor een via USB
aangesloten DYMO LabelWriter 400 of 450. Alleen deze interne printercontainer
krijgt toegang tot `/dev/bus/usb`; de CUPS-poort wordt niet op het netwerk
gepubliceerd.

De standaard DYMO 99014-indeling gebruikt het label verticaal op 54 × 101 mm en
toont onder andere:

- Locatie en producttype
- Productnaam en unieke bakcode
- Scanbare barcode
- Inhoud of ingrediënten
- Korte bereidings- of opwarminstructie op basis van naam én ingrediënten
- Productie- of bereidingsdatum
- Einddatum en hoeveelheid
- Wie het product heeft ingelegd

Ga na installatie naar **Instellingen → Labels en meldingen**, kies de gevonden
DYMO als standaardprinter en gebruik **Testlabel direct printen**. Browserprinten
blijft beschikbaar als reserveoptie. De DYMO 5-serie wordt niet ondersteund.

## Beveiliging

Umbrels extra proxy-login is uitgeschakeld om een dubbele login te voorkomen.
De eigen beveiliging van Home Stock blijft volledig actief:

- Alle voorraadpagina's en API-routes vereisen een Home Stock-account
- Wachtwoorden worden opgeslagen als salted scrypt-hashes
- Server-side sessies verlopen na 12 uur
- Sessies worden ingetrokken na uitloggen of een wachtwoordwijziging
- Schrijfacties zijn beschermd met CSRF-tokens
- Inlogpogingen worden begrensd
- Gebruikers kunnen elkaars profiel niet via API-parameters overnemen
- Alleen beheerders kunnen gebruikers en systeeminstellingen aanpassen

Gebruik HTTPS wanneer Home Stock buiten het vertrouwde lokale netwerk bereikbaar
is. Stel bij TLS via een reverse proxy `HOME_STOCK_SECURE_COOKIE=1` in voor de
webcontainer.

## Versiegeschiedenis

### v0.7.0

- Gemini maakt een korte bereidings- of opwarminstructie op basis van zowel de
  productnaam als de ingrediënten
- De tekst is vóór en na het opslaan handmatig aanpasbaar
- Nieuw blok **Bereidingswijze** in het schermvoorbeeld en op de DYMO 99014
- De bereidingswijze wordt bij het product bewaard en op ieder baklabel hergebruikt

### v0.6.1

- Umbrel-proxylogin uitgeschakeld; alleen de eigen Home Stock-login is nodig
- README volledig opnieuw ingedeeld en versiegeschiedenis gecorrigeerd
- Standaard Home Stock-inloggegevens zichtbaar gemaakt in Umbrel

### v0.6.0

- Installeerbare iPhone-webapp met Apple-appicoon en mobiele navigatie
- Live iPhone-camerascanner en foto-scanfunctie
- Lokale ZXing-herkenning voor EAN, UPC, Code 128, QR en Home Stock-codes

### v0.5.0

- Meerdere bakken of verpakkingen in één keer invoeren
- Individuele achtervoegsels zoals `VP001-A`, `VP001-B` en `VP001-C`
- Iedere bak apart verbruiken en alle bijbehorende labels samen printen

### v0.4.0

- Verticaal DYMO 99014-bewaaretiket
- Vaste artikelcodes van twee letters en drie cijfers
- Inhoud, locatie, productie-/bereidingsdatum en inlegger op het label
- Aparte formulieren voor zelfgemaakt eten en winkelproducten

### v0.3.0

- Automatische USB-detectie voor DYMO LabelWriter 400/450
- Ingebouwde, afgeschermde CUPS-printerservice
- Direct printen, standaardprinter en testlabel

### v0.2.2

- Verplichte eigen login en wachtwoordwijziging bij eerste gebruik
- Gebruikersbeheer, beheerdersrechten en beveiligde sessies

### v0.2.1

- Browserpop-ups vervangen door formulieren, dropdowns en eigen invoervelden

### v0.2.0

- SQLite-database en automatische migratie
- Voorraadpartijen, vaste en eigen locaties
- Open Food Facts en Gemini-houdbaarheidsinschatting
- Prijzen, statistieken, profielen, geschiedenis en meldingen
- Recepten, maaltijdplanning, boodschappen en labelwachtrij

## Lokale ontwikkeling

```bash
docker build -t home-stock .
docker run --rm -p 8080:8080 -v home-stock-data:/data home-stock
```

Open daarna <http://localhost:8080>.

Tests uitvoeren:

```bash
python -m unittest discover -s tests
```

## Licentie

MIT
