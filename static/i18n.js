/* Home Stock browser translations. Dutch is the canonical source language. */
(function () {
  'use strict';

  const supported = ['nl', 'en', 'de'];
  const localeMap = {nl: 'nl-NL', en: 'en-GB', de: 'de-DE'};
  const names = {nl: 'Nederlands', en: 'English', de: 'Deutsch'};
  const pairs = {
    'Je slimme thuisvoorraad': ['Your smart home inventory', 'Dein smarter Haushaltsvorrat'],
    'Thuisvoorraad': ['Home inventory', 'Haushaltsvorrat'],
    'Beheren': ['Manage', 'Verwalten'], 'Hoofdnavigatie': ['Main navigation', 'Hauptnavigation'],
    'Overzicht': ['Dashboard', 'Übersicht'], 'Voorraad': ['Inventory', 'Vorrat'],
    'Boodschappen': ['Shopping', 'Einkäufe'], 'Recepten': ['Recipes', 'Rezepte'],
    'Maaltijdplanner': ['Meal planner', 'Essensplaner'], 'Statistieken': ['Statistics', 'Statistiken'],
    'Labels': ['Labels', 'Etiketten'], 'Geschiedenis': ['History', 'Verlauf'],
    'Instellingen': ['Settings', 'Einstellungen'], 'Actief profiel': ['Active profile', 'Aktives Profil'],
    'Wachtwoord': ['Password', 'Passwort'], 'Gebruikers': ['Users', 'Benutzer'],
    'Uitloggen': ['Log out', 'Abmelden'], 'Taal': ['Language', 'Sprache'],
    'Je huishouden in één oogopslag.': ['Your household at a glance.', 'Dein Haushalt auf einen Blick.'],
    'Producten, partijen en houdbaarheid per locatie.': ['Products, batches and shelf life by location.', 'Produkte, Chargen und Haltbarkeit nach Lagerort.'],
    'Automatisch en handmatig samengesteld.': ['Compiled automatically and manually.', 'Automatisch und manuell zusammengestellt.'],
    'Kook op basis van wat je al hebt.': ['Cook with what you already have.', 'Koche mit dem, was du bereits hast.'],
    'Plan vooruit en vul ontbrekende voorraad aan.': ['Plan ahead and replenish missing stock.', 'Plane voraus und ergänze fehlende Vorräte.'],
    'Verbruik, uitgaven en verspilling.': ['Consumption, spending and waste.', 'Verbrauch, Ausgaben und Verschwendung.'],
    'Voorbeelden, wachtrij en DYMO-afdrukken.': ['Previews, queue and DYMO printing.', 'Vorschau, Warteschlange und DYMO-Druck.'],
    'Alle voorraadmutaties per profiel.': ['All inventory changes by profile.', 'Alle Bestandsänderungen pro Profil.'],
    'Locaties, profielen, Gemini en labels.': ['Locations, profiles, Gemini and labels.', 'Lagerorte, Profile, Gemini und Etiketten.'],
    'Kleurmodus wisselen': ['Toggle colour mode', 'Farbmodus wechseln'],
    'Barcode scannen': ['Scan barcode', 'Barcode scannen'], 'Meldingen': ['Notifications', 'Benachrichtigungen'],
    'Product toevoegen': ['Add product', 'Produkt hinzufügen'], 'Vandaag': ['Today', 'Heute'],
    'Alles op voorraad, zonder giswerk.': ['Know exactly what you have in stock.', 'Genau wissen, was vorrätig ist.'],
    'Bekijk wat bijna op is, gebruik eerst wat verloopt en leg nieuwe bakken direct met een label in.': ['See what is running low, use items nearing expiry first and label new containers immediately.', 'Sieh, was knapp wird, verbrauche bald ablaufende Produkte zuerst und etikettiere neue Behälter sofort.'],
    'Code scannen': ['Scan code', 'Code scannen'], 'Producten': ['Products', 'Produkte'],
    'Totale voorraad': ['Total inventory', 'Gesamtbestand'], 'Binnen 7 dagen': ['Within 7 days', 'Innerhalb von 7 Tagen'],
    'Bijna op': ['Running low', 'Fast aufgebraucht'], 'Aandacht nodig': ['Needs attention', 'Handlungsbedarf'],
    'Oudste partijen en lage voorraad': ['Oldest batches and low stock', 'Älteste Chargen und niedriger Bestand'],
    'Recente activiteit': ['Recent activity', 'Letzte Aktivitäten'], 'Wie deed wat': ['Who did what', 'Wer hat was gemacht'],
    'Zoek op naam, code, barcode of locatie': ['Search by name, code, barcode or location', 'Nach Name, Code, Barcode oder Lagerort suchen'],
    'Alle locaties': ['All locations', 'Alle Lagerorte'], 'Alle soorten': ['All types', 'Alle Arten'],
    'Zelfgemaakt': ['Homemade', 'Selbstgemacht'], 'Winkelproduct': ['Store product', 'Ladenprodukt'],
    'Iedere houdbaarheid': ['Any shelf life', 'Jede Haltbarkeit'], 'Over datum': ['Expired', 'Abgelaufen'],
    'Zonder datum': ['Without date', 'Ohne Datum'], 'Eerst opmaken': ['Use first', 'Zuerst verbrauchen'],
    'Naam A–Z': ['Name A–Z', 'Name A–Z'], 'Laagste voorraad': ['Lowest stock', 'Niedrigster Bestand'],
    'Hoogste voorraad': ['Highest stock', 'Höchster Bestand'], 'Gearchiveerd': ['Archived', 'Archiviert'],
    'Verlopen opruimen': ['Clear expired', 'Abgelaufenes entfernen'],
    'Boodschappenlijst': ['Shopping list', 'Einkaufsliste'],
    'Minimumvoorraad wordt automatisch aangevuld': ['Minimum stock is added automatically', 'Mindestbestand wird automatisch ergänzt'],
    'Afgevinkt wissen': ['Clear checked', 'Erledigte löschen'], 'Handmatig toevoegen': ['Add manually', 'Manuell hinzufügen'],
    'Product': ['Product', 'Produkt'], 'Aantal': ['Quantity', 'Anzahl'], 'Eenheid': ['Unit', 'Einheit'],
    'Toevoegen': ['Add', 'Hinzufügen'], 'Recepten controleren automatisch je voorraad.': ['Recipes automatically check your inventory.', 'Rezepte prüfen automatisch deinen Vorrat.'],
    'Recept': ['Recipe', 'Rezept'], 'Plan maaltijden en zet ontbrekende ingrediënten op de lijst.': ['Plan meals and add missing ingredients to the list.', 'Plane Mahlzeiten und setze fehlende Zutaten auf die Liste.'],
    'Maaltijd plannen': ['Plan meal', 'Mahlzeit planen'], 'Laatste 30 dagen': ['Last 30 days', 'Letzte 30 Tage'],
    '90 dagen': ['90 days', '90 Tage'], '1 jaar': ['1 year', '1 Jahr'], 'Uitgegeven': ['Spent', 'Ausgegeben'],
    'Verbruikt': ['Consumed', 'Verbraucht'], 'Verspild': ['Wasted', 'Verschwendet'],
    'Waarde verspilling': ['Waste value', 'Wert der Verschwendung'], 'Uitgaven per winkel': ['Spending by store', 'Ausgaben pro Geschäft'],
    'Meest verspild': ['Most wasted', 'Am meisten verschwendet'], 'Bekijk, groepeer en druk labels af.': ['View, group and print labels.', 'Etiketten ansehen, gruppieren und drucken.'],
    'Print wachtrij': ['Print queue', 'Warteschlange drucken'], 'Activiteitshistorie': ['Activity history', 'Aktivitätsverlauf'],
    'Alle veranderingen chronologisch bij elkaar; recente voorraadacties kun je terugdraaien.': ['All changes in chronological order; recent inventory actions can be undone.', 'Alle Änderungen chronologisch; aktuelle Bestandsaktionen können rückgängig gemacht werden.'],
    'Meer laden': ['Load more', 'Mehr laden'],
    'Gebruikt voor houdbaarheidsinschattingen en korte bereidingswijzen op labels.': ['Used for shelf-life estimates and short preparation instructions on labels.', 'Für Haltbarkeitsschätzungen und kurze Zubereitungshinweise auf Etiketten.'],
    'Gemini API-key': ['Gemini API key', 'Gemini-API-Schlüssel'], 'Bestaande key wordt niet getoond': ['Existing key is not shown', 'Vorhandener Schlüssel wird nicht angezeigt'],
    'Opslaan': ['Save', 'Speichern'], 'Locaties': ['Locations', 'Lagerorte'], 'Nieuwe locatie': ['New location', 'Neuer Lagerort'],
    'Profielen': ['Profiles', 'Profile'], 'Naam': ['Name', 'Name'], 'Labels en meldingen': ['Labels and notifications', 'Etiketten und Benachrichtigungen'],
    'Standaard label': ['Default label', 'Standardetikett'], 'Compact': ['Compact', 'Kompakt'],
    'Standaard afdrukmethode': ['Default print method', 'Standarddruckmethode'],
    'Direct via USB-printer op de server': ['Direct via USB printer on the server', 'Direkt über USB-Drucker am Server'],
    'Afdrukvenster van de browser': ['Browser print dialog', 'Druckdialog des Browsers'],
    'Standaard USB-printer': ['Default USB printer', 'Standard-USB-Drucker'], 'Automatisch kiezen': ['Select automatically', 'Automatisch auswählen'],
    'Printerstatus wordt opgehaald…': ['Retrieving printer status…', 'Druckerstatus wird abgerufen…'],
    'Printers opnieuw zoeken': ['Search for printers again', 'Drucker erneut suchen'], 'Testlabel direct printen': ['Print test label now', 'Testetikett direkt drucken'],
    'Dagelijkse houdbaarheidsmeldingen inschakelen': ['Enable daily expiry notifications', 'Tägliche Haltbarkeitsmeldungen aktivieren'],
    'Dagelijkse controletijd': ['Daily check time', 'Tägliche Prüfzeit'], 'Waarschuwen vóór houdbaarheid': ['Warn before expiry', 'Vor Ablauf warnen'],
    'Houdbaarheidssjablonen': ['Shelf-life templates', 'Haltbarkeitsvorlagen'], 'Beheer vaste regels voor producten en locaties.': ['Manage fixed rules for products and locations.', 'Feste Regeln für Produkte und Lagerorte verwalten.'],
    'Regel': ['Rule', 'Regel'], 'Gegevens': ['Data', 'Daten'], 'JSON-back-up': ['JSON backup', 'JSON-Sicherung'],
    'iPhone-webapp': ['iPhone web app', 'iPhone-Web-App'], 'Open Home Stock in Safari en zet de app op je beginscherm.': ['Open Home Stock in Safari and add it to your Home Screen.', 'Öffne Home Stock in Safari und füge es zum Home-Bildschirm hinzu.'],
    'Installatie-uitleg': ['Installation instructions', 'Installationsanleitung'], 'Account': ['Account', 'Konto'],
    'Ingelogd als': ['Signed in as', 'Angemeldet als'], 'Wachtwoord wijzigen': ['Change password', 'Passwort ändern'],
    'Scan een barcode of vul het product in.': ['Scan a barcode or enter the product.', 'Scanne einen Barcode oder gib das Produkt ein.'],
    'Barcode scannen of typen': ['Scan or enter barcode', 'Barcode scannen oder eingeben'], 'Opzoeken': ['Look up', 'Suchen'],
    'Soort': ['Type', 'Art'], 'Zelfgemaakt / bak eten': ['Homemade / food container', 'Selbstgemacht / Essensbehälter'],
    'Inhoud of ingrediënten': ['Contents or ingredients', 'Inhalt oder Zutaten'],
    'Bijvoorbeeld: pasta, vegetarisch gehakt, tomaat en kaas': ['For example: pasta, vegetarian mince, tomato and cheese', 'Zum Beispiel: Nudeln, vegetarisches Hack, Tomate und Käse'],
    'Merk': ['Brand', 'Marke'], 'Categorie': ['Category', 'Kategorie'], 'Kies of typ zelf': ['Choose or enter your own', 'Auswählen oder selbst eingeben'],
    'Aantal bakken / verpakkingen': ['Number of containers / packages', 'Anzahl Behälter / Packungen'],
    'Hoeveelheid per bak / verpakking': ['Quantity per container / package', 'Menge pro Behälter / Packung'],
    'Gewicht per bak (gram)': ['Weight per container (grams)', 'Gewicht pro Behälter (Gramm)'], 'Bijvoorbeeld 500': ['For example 500', 'Zum Beispiel 500'],
    'Eenheid per bak': ['Unit per container', 'Einheit pro Behälter'], 'Minimumvoorraad': ['Minimum stock', 'Mindestbestand'],
    'Locatie': ['Location', 'Lagerort'], 'Winkel': ['Store', 'Geschäft'], 'Prijs per eenheid': ['Price per unit', 'Preis pro Einheit'],
    'Ingelegd of gekocht op': ['Stored or purchased on', 'Eingelagert oder gekauft am'], 'Bereid op': ['Prepared on', 'Zubereitet am'],
    'Houdbaar tot / einddatum': ['Use by / expiry date', 'Haltbar bis / Ablaufdatum'],
    'Bereidingswijze voor op het label': ['Preparation instructions for the label', 'Zubereitungshinweise für das Etikett'],
    'Bijvoorbeeld: Magnetron: 4–5 min op 700 W, halverwege omscheppen': ['For example: Microwave: 4–5 min at 700 W, stir halfway through', 'Zum Beispiel: Mikrowelle: 4–5 Min. bei 700 W, nach der Hälfte umrühren'],
    'Bereidingswijze met Gemini maken': ['Generate instructions with Gemini', 'Zubereitung mit Gemini erstellen'],
    'Gebruikt naam, ingrediënten én gewicht per bak; je kunt de tekst daarna aanpassen.': ['Uses the name, ingredients and weight per container; you can edit the text afterwards.', 'Verwendet Name, Zutaten und Gewicht pro Behälter; der Text kann danach bearbeitet werden.'],
    'Houdbaarheid bepalen': ['Determine shelf life', 'Haltbarkeit bestimmen'], 'Lokale regels worden eerst gebruikt.': ['Local rules are used first.', 'Lokale Regeln werden zuerst verwendet.'],
    'Deze aangepaste houdbaarheid onthouden voor dit product en deze locatie': ['Remember this custom shelf life for this product and location', 'Diese angepasste Haltbarkeit für dieses Produkt und diesen Lagerort merken'],
    'Voor iedere bak een eigen label maken': ['Create a separate label for each container', 'Für jeden Behälter ein eigenes Etikett erstellen'],
    'Exemplaren per bak': ['Copies per container', 'Exemplare pro Behälter'], 'Notities': ['Notes', 'Notizen'],
    'Annuleren': ['Cancel', 'Abbrechen'], 'Product opslaan': ['Save product', 'Produkt speichern'],
    'Labelvoorbeeld': ['Label preview', 'Etikettenvorschau'], 'Controleer het label voordat je print.': ['Check the label before printing.', 'Prüfe das Etikett vor dem Drucken.'],
    'INHOUD': ['CONTENTS', 'INHALT'], 'BEREIDINGSWIJZE': ['PREPARATION', 'ZUBEREITUNG'], 'BEREID': ['PREPARED', 'ZUBEREITET'],
    'EINDDATUM': ['EXPIRY DATE', 'ABLAUFDATUM'], 'Niet printen': ['Do not print', 'Nicht drucken'],
    'In wachtrij': ['Add to queue', 'In Warteschlange'], 'Via browser printen': ['Print via browser', 'Über Browser drucken'],
    'Alle labels printen': ['Print all labels', 'Alle Etiketten drucken'], 'Direct printen': ['Print now', 'Direkt drucken'],
    'Recept toevoegen': ['Add recipe', 'Rezept hinzufügen'], 'Bewaar ingrediënten en een duidelijke bereidingswijze.': ['Save ingredients and clear preparation instructions.', 'Speichere Zutaten und eine klare Zubereitung.'],
    'Emoji': ['Emoji', 'Emoji'], 'Porties': ['Servings', 'Portionen'], 'Bereidingstijd': ['Preparation time', 'Zubereitungszeit'],
    'Ingrediënten': ['Ingredients', 'Zutaten'], 'Ingrediënt': ['Ingredient', 'Zutat'], 'Bereiding': ['Preparation', 'Zubereitung'],
    'Datum': ['Date', 'Datum'], 'Moment': ['Meal', 'Mahlzeit'], 'ontbijt': ['breakfast', 'Frühstück'], 'lunch': ['lunch', 'Mittagessen'],
    'avondeten': ['dinner', 'Abendessen'], 'Notitie': ['Note', 'Notiz'], 'Bijvoorbeeld: Simon eet mee': ['For example: Simon is joining us', 'Zum Beispiel: Simon isst mit'],
    'Ontbrekende ingrediënten direct op de boodschappenlijst zetten': ['Add missing ingredients directly to the shopping list', 'Fehlende Zutaten direkt auf die Einkaufsliste setzen'],
    'Plannen': ['Plan', 'Planen'], 'Richt de camera op een winkelbarcode of Home Stock-label.': ['Point the camera at a retail barcode or Home Stock label.', 'Richte die Kamera auf einen Produktbarcode oder ein Home-Stock-Etikett.'],
    'Zoeken / toevoegen': ['Search / add', 'Suchen / hinzufügen'], 'Direct verbruiken': ['Consume directly', 'Direkt verbrauchen'],
    'Foto scannen': ['Scan photo', 'Foto scannen'], 'Of typ de barcode': ['Or enter the barcode', 'Oder Barcode eingeben'],
    'Gebruiken': ['Use', 'Verwenden'], 'Alles gelezen': ['Mark all as read', 'Alle als gelesen markieren'],
    'VEILIG · ZELFGEHOST': ['SECURE · SELF-HOSTED', 'SICHER · SELBST GEHOSTET'],
    'Weet wat je hebt.': ['Know what you have.', 'Wisse, was du hast.'], 'Gebruik wat eerst op moet.': ['Use what expires first.', 'Verbrauche, was zuerst abläuft.'],
    'Voorraad, houdbaarheid en DYMO-labels in één rustige omgeving.': ['Inventory, shelf life and DYMO labels in one calm environment.', 'Vorrat, Haltbarkeit und DYMO-Etiketten in einer übersichtlichen Umgebung.'],
    'Eigen beveiligde login': ['Secure built-in login', 'Eigene sichere Anmeldung'], 'Je gegevens blijven op je server': ['Your data stays on your server', 'Deine Daten bleiben auf deinem Server'],
    'Ontworpen voor mobiel': ['Designed for mobile', 'Für Mobilgeräte entwickelt'], 'Inloggen': ['Sign in', 'Anmelden'],
    'Terug naar inloggen': ['Back to sign in', 'Zurück zur Anmeldung'], 'Log in om je voorraad te bekijken en te beheren.': ['Sign in to view and manage your inventory.', 'Melde dich an, um deinen Vorrat anzusehen und zu verwalten.'],
    'Je gebruikt nog het standaardwachtwoord. Kies eerst een eigen wachtwoord om verder te gaan.': ['You are still using the default password. Choose your own password before continuing.', 'Du verwendest noch das Standardpasswort. Lege zuerst ein eigenes Passwort fest.'],
    'Gebruikersnaam': ['Username', 'Benutzername'], 'Huidig wachtwoord': ['Current password', 'Aktuelles Passwort'],
    'Nieuw wachtwoord': ['New password', 'Neues Passwort'], 'Herhaal nieuw wachtwoord': ['Repeat new password', 'Neues Passwort wiederholen'],
    'Gebruik minimaal 12 tekens, bijvoorbeeld een lange, unieke wachtzin.': ['Use at least 12 characters, such as a long, unique passphrase.', 'Verwende mindestens 12 Zeichen, zum Beispiel eine lange, einzigartige Passphrase.'],
    'Wachtwoord opslaan': ['Save password', 'Passwort speichern'], 'Terug naar voorraad': ['Back to inventory', 'Zurück zum Vorrat'],
    'BEHEER': ['ADMINISTRATION', 'VERWALTUNG'], 'Gebruikers beheren': ['Manage users', 'Benutzer verwalten'],
    'Accounts en toegangsrechten voor Home Stock.': ['Accounts and access rights for Home Stock.', 'Konten und Zugriffsrechte für Home Stock.'],
    'Terug naar Home Stock': ['Back to Home Stock', 'Zurück zu Home Stock'], 'Accounts': ['Accounts', 'Konten'],
    'Tijdelijk wachtwoord ingesteld. De gebruiker moet dit na de volgende login wijzigen.': ['Temporary password set. The user must change it after the next sign-in.', 'Temporäres Passwort festgelegt. Der Benutzer muss es nach der nächsten Anmeldung ändern.'],
    'Beheerder': ['Administrator', 'Administrator'], 'Gebruiker': ['User', 'Benutzer'], 'Uitgeschakeld': ['Disabled', 'Deaktiviert'],
    'Wachtwoordwijziging vereist': ['Password change required', 'Passwortänderung erforderlich'], 'Actief': ['Active', 'Aktiv'],
    'Uitschakelen': ['Disable', 'Deaktivieren'], 'Inschakelen': ['Enable', 'Aktivieren'],
    'Tijdelijk wachtwoord instellen': ['Set temporary password', 'Temporäres Passwort festlegen'],
    'Nieuw tijdelijk wachtwoord': ['New temporary password', 'Neues temporäres Passwort'], 'Instellen en sessies uitloggen': ['Set and sign out sessions', 'Festlegen und Sitzungen abmelden'],
    'Gebruiker toevoegen': ['Add user', 'Benutzer hinzufügen'], 'Beide rollen kunnen de gezamenlijke voorraad beheren. Alleen beheerders kunnen accounts aanmaken en systeeminstellingen wijzigen.': ['Both roles can manage the shared inventory. Only administrators can create accounts and change system settings.', 'Beide Rollen können den gemeinsamen Vorrat verwalten. Nur Administratoren können Konten erstellen und Systemeinstellungen ändern.'],
    'Account aangemaakt. Deel het tijdelijke wachtwoord persoonlijk met de gebruiker.': ['Account created. Share the temporary password with the user in person.', 'Konto erstellt. Teile dem Benutzer das temporäre Passwort persönlich mit.'],
    'Tijdelijk wachtwoord': ['Temporary password', 'Temporäres Passwort'], 'Rol': ['Role', 'Rolle'],
    'De gebruiker moet bij de eerste login een eigen wachtwoord kiezen.': ['The user must choose their own password at first sign-in.', 'Der Benutzer muss bei der ersten Anmeldung ein eigenes Passwort wählen.'],
    'Account aanmaken': ['Create account', 'Konto erstellen'],
    'Geen datum': ['No date', 'Kein Datum'], 'Geen locatie': ['No location', 'Kein Lagerort'], 'Geen categorie': ['No category', 'Keine Kategorie'],
    'Onbekend': ['Unknown', 'Unbekannt'], 'ONBEKEND': ['UNKNOWN', 'UNBEKANNT'], 'ONBEKENDE LOCATIE': ['UNKNOWN LOCATION', 'UNBEKANNTER LAGERORT'],
    'Niet ingesteld': ['Not set', 'Nicht festgelegt'], 'Sluiten': ['Close', 'Schließen'], 'Details': ['Details', 'Details'],
    'Actie': ['Action', 'Aktion'], 'Klaar': ['Done', 'Fertig'], 'Archiveren': ['Archive', 'Archivieren'],
    'Partij': ['Batch', 'Charge'], 'Partijen en bakken': ['Batches and containers', 'Chargen und Behälter'],
    'Inhoud:': ['Contents:', 'Inhalt:'], 'Bereidingswijze:': ['Preparation:', 'Zubereitung:'],
    'Hoeveelheid': ['Quantity', 'Menge'], 'Gewicht (gram)': ['Weight (grams)', 'Gewicht (Gramm)'],
    'Ingelegd / gekocht': ['Stored / purchased', 'Eingelagert / gekauft'], 'Geproduceerd / bereid': ['Produced / prepared', 'Produziert / zubereitet'],
    'Houdbaar tot': ['Use by', 'Haltbar bis'], 'Verbruiken': ['Consume', 'Verbrauchen'], 'Verspilling registreren': ['Register waste', 'Verschwendung erfassen'],
    'Als geopend markeren': ['Mark as opened', 'Als geöffnet markieren'], 'Verplaatsen': ['Move', 'Verschieben'], 'Aantal corrigeren': ['Correct quantity', 'Menge korrigieren'],
    'Nieuwe locatie': ['New location', 'Neuer Lagerort'], 'Notitie (optioneel)': ['Note (optional)', 'Notiz (optional)'],
    'Alles ziet er goed uit.': ['Everything looks good.', 'Alles sieht gut aus.'], 'Nog geen activiteit.': ['No activity yet.', 'Noch keine Aktivität.'],
    'Geen producten gevonden.': ['No products found.', 'Keine Produkte gefunden.'], 'Geen voorraadpartijen.': ['No inventory batches.', 'Keine Bestandschargen.'],
    'Je lijst is leeg.': ['Your list is empty.', 'Deine Liste ist leer.'], 'Voeg je eerste recept toe.': ['Add your first recipe.', 'Füge dein erstes Rezept hinzu.'],
    'Nog niets gepland.': ['Nothing planned yet.', 'Noch nichts geplant.'], 'Nog geen prijsgegevens.': ['No price data yet.', 'Noch keine Preisdaten.'],
    'Nog niets verspild — mooi zo.': ['Nothing wasted yet — great.', 'Noch nichts verschwendet — sehr gut.'],
    'Nog geen labels.': ['No labels yet.', 'Noch keine Etiketten.'], 'Nog geen geschiedenis.': ['No history yet.', 'Noch kein Verlauf.'],
    'Geen meldingen.': ['No notifications.', 'Keine Benachrichtigungen.'], 'Ongedaan maken': ['Undo', 'Rückgängig machen'],
    'Teruggedraaid': ['Undone', 'Rückgängig gemacht'], 'Vaste locatie': ['Fixed location', 'Fester Lagerort'], 'Eigen locatie': ['Custom location', 'Eigener Lagerort'],
    'Huisgenoot': ['Household member', 'Haushaltsmitglied'], 'Koelkast': ['Fridge', 'Kühlschrank'], 'Vriezer': ['Freezer', 'Gefrierschrank'],
    'Voorraadkast': ['Pantry', 'Vorratsschrank'], 'Algemene regel': ['General rule', 'Allgemeine Regel'],
    'Herstellen': ['Restore', 'Wiederherstellen'], 'Bewerken': ['Edit', 'Bearbeiten'], 'Verwijder': ['Delete', 'Löschen'],
    'Productnaam of patroon': ['Product name or pattern', 'Produktname oder Muster'], 'Bijvoorbeeld lasagne': ['For example lasagne', 'Zum Beispiel Lasagne'],
    'Bijvoorbeeld avondeten': ['For example dinner', 'Zum Beispiel Abendessen'], 'Houdbaar in dagen': ['Shelf life in days', 'Haltbar in Tagen'],
    'Na openen in dagen (optioneel)': ['Days after opening (optional)', 'Tage nach dem Öffnen (optional)'],
    'Camera starten…': ['Starting camera…', 'Kamera wird gestartet…'], 'Richt de code binnen het kader.': ['Position the code inside the frame.', 'Richte den Code im Rahmen aus.'],
    'Foto wordt gescand…': ['Scanning photo…', 'Foto wird gescannt…'], 'Zoeken…': ['Searching…', 'Suche…'],
    'Niet gevonden': ['Not found', 'Nicht gefunden'], 'Bezig met bepalen…': ['Determining…', 'Wird bestimmt…'],
    'Gemini maakt een korte bereidingswijze…': ['Gemini is generating short preparation instructions…', 'Gemini erstellt eine kurze Zubereitungsanweisung…'],
    'Laag': ['Low', 'Niedrig'], 'Datum': ['Date', 'Datum'], 'automatisch': ['automatic', 'automatisch'],
    'Bekijken / bewerken': ['View / edit', 'Ansehen / bearbeiten'], 'Naar lijst': ['Add to list', 'Zur Liste'],
    'Open': ['Open', 'Öffnen'], 'ingekocht': ['purchased', 'eingekauft'], 'verbruikt': ['consumed', 'verbraucht'],
    'verspild': ['wasted', 'verschwendet'], 'gecorrigeerd': ['corrected', 'korrigiert'], 'verplaatst': ['moved', 'verschoben'],
    'geopend': ['opened', 'geöffnet'], 'bijgewerkt': ['updated', 'aktualisiert'], 'geïmporteerd': ['imported', 'importiert'],
    'Bereid': ['Prepared', 'Zubereitet'], 'Ingelegd': ['Stored', 'Eingelagert'], 'GEPRODUCEERD': ['PRODUCED', 'PRODUZIERT'],
    'INGELEGD': ['STORED', 'EINGELAGERT'], 'INGELEGD DOOR': ['STORED BY', 'EINGELAGERT VON'],
    'PRODUCTINFORMATIE': ['PRODUCT INFORMATION', 'PRODUKTINFORMATIONEN'], 'PARTIJ': ['BATCH', 'CHARGE'],
    'HOME STOCK · BEWAARETIKET': ['HOME STOCK · STORAGE LABEL', 'HOME STOCK · LAGERETIKET'],
    'porties': ['servings', 'Portionen'],
    'Er ging iets mis': ['Something went wrong', 'Etwas ist schiefgelaufen'],
    'Log opnieuw in om verder te gaan.': ['Sign in again to continue.', 'Melde dich erneut an, um fortzufahren.'],
    'Wijzig eerst je standaardwachtwoord.': ['Change your default password first.', 'Ändere zuerst dein Standardpasswort.'],
    'Alleen beheerders mogen dit aanpassen.': ['Only administrators may change this.', 'Nur Administratoren dürfen dies ändern.'],
    'Sessie verlopen of ongeldig. Vernieuw de pagina en probeer opnieuw.': ['Session expired or invalid. Refresh the page and try again.', 'Sitzung abgelaufen oder ungültig. Aktualisiere die Seite und versuche es erneut.'],
    'Te veel pogingen. Probeer het over 15 minuten opnieuw.': ['Too many attempts. Try again in 15 minutes.', 'Zu viele Versuche. Versuche es in 15 Minuten erneut.'],
    'Gebruikersnaam of wachtwoord klopt niet.': ['Incorrect username or password.', 'Benutzername oder Passwort ist falsch.'],
    'Je huidige wachtwoord klopt niet.': ['Your current password is incorrect.', 'Dein aktuelles Passwort ist falsch.'],
    'Kies een nieuw wachtwoord van 12 tot 256 tekens.': ['Choose a new password of 12 to 256 characters.', 'Wähle ein neues Passwort mit 12 bis 256 Zeichen.'],
    'De nieuwe wachtwoorden komen niet overeen.': ['The new passwords do not match.', 'Die neuen Passwörter stimmen nicht überein.'],
    'Kies een ander wachtwoord dan je huidige.': ['Choose a password different from your current one.', 'Wähle ein anderes Passwort als dein aktuelles.'],
    'Account niet gevonden.': ['Account not found.', 'Konto nicht gefunden.'],
    'Je kunt je eigen account niet uitschakelen.': ['You cannot disable your own account.', 'Du kannst dein eigenes Konto nicht deaktivieren.'],
    'Er moet minimaal één actieve beheerder blijven.': ['At least one active administrator must remain.', 'Mindestens ein aktiver Administrator muss verbleiben.'],
    'Gebruik een tijdelijk wachtwoord van 12 tot 256 tekens.': ['Use a temporary password of 12 to 256 characters.', 'Verwende ein temporäres Passwort mit 12 bis 256 Zeichen.'],
    'Naam is verplicht': ['Name is required', 'Name ist erforderlich'], 'Product niet gevonden': ['Product not found', 'Produkt nicht gefunden'],
    'Locatie niet gevonden': ['Location not found', 'Lagerort nicht gefunden'], 'Partij niet gevonden': ['Batch not found', 'Charge nicht gefunden'],
    'Recept niet gevonden': ['Recipe not found', 'Rezept nicht gefunden'], 'Label niet gevonden': ['Label not found', 'Etikett nicht gefunden'],
    'Geen wijzigingen': ['No changes', 'Keine Änderungen'], 'Ongeldig producttype': ['Invalid product type', 'Ungültiger Produkttyp'],
    'Onbekende actie': ['Unknown action', 'Unbekannte Aktion'], 'Geen camerabeeld ontvangen': ['No camera image received', 'Kein Kamerabild empfangen'],
    'Het camerabeeld kon niet worden gelezen': ['The camera image could not be read', 'Das Kamerabild konnte nicht gelesen werden'],
    'Geen beschikbare voorraad voor deze code': ['No available inventory for this code', 'Kein verfügbarer Bestand für diesen Code'],
    'Vul eerst de naam van het gerecht of product in': ['Enter the dish or product name first', 'Gib zuerst den Namen des Gerichts oder Produkts ein'],
    'Vul eerst de inhoud of ingrediënten in': ['Enter the contents or ingredients first', 'Gib zuerst Inhalt oder Zutaten ein'],
    'Configureer eerst je Gemini API-key bij Instellingen': ['Configure your Gemini API key in Settings first', 'Konfiguriere zuerst deinen Gemini-API-Schlüssel in den Einstellungen'],
    'Houdbaarheidsregel niet gevonden': ['Shelf-life rule not found', 'Haltbarkeitsregel nicht gefunden'],
    'Voor deze combinatie bestaat al een regel': ['A rule already exists for this combination', 'Für diese Kombination existiert bereits eine Regel'],
    'Deze locatie bestaat al': ['This location already exists', 'Dieser Lagerort existiert bereits'],
    'Vaste locaties kunnen niet worden verwijderd': ['Fixed locations cannot be deleted', 'Feste Lagerorte können nicht gelöscht werden'],
    'Verplaats eerst de aanwezige voorraad': ['Move the existing inventory first', 'Verschiebe zuerst den vorhandenen Bestand'],
    'Deze activiteit is al teruggedraaid': ['This activity has already been undone', 'Diese Aktivität wurde bereits rückgängig gemacht'],
    'Deze activiteit kan niet worden teruggedraaid': ['This activity cannot be undone', 'Diese Aktivität kann nicht rückgängig gemacht werden'],
    'Draai eerst de nieuwere activiteit van deze partij terug': ['Undo the newer activity for this batch first', 'Mache zuerst die neuere Aktivität dieser Charge rückgängig'],
    'Deze naam bestaat al': ['This name already exists', 'Dieser Name existiert bereits'],
    'De printerservice gaf een fout': ['The printer service returned an error', 'Der Druckerdienst hat einen Fehler gemeldet'],
    'De USB-printerservice is niet bereikbaar': ['The USB printer service is unavailable', 'Der USB-Druckerdienst ist nicht erreichbar'],
    'Geen ondersteunde DYMO via USB gevonden': ['No supported DYMO found via USB', 'Kein unterstützter DYMO über USB gefunden'],
    'Home Stock · Inloggen': ['Home Stock · Sign in', 'Home Stock · Anmeldung'],
    'Home Stock · Gebruikers': ['Home Stock · Users', 'Home Stock · Benutzer']
    ,'Gearchiveerde producten': ['Archived products', 'Archivierte Produkte']
    ,'Deze producten zijn uit de actieve voorraadlijst gehaald, maar hun historie is bewaard.': ['These products were removed from the active inventory, but their history was retained.', 'Diese Produkte wurden aus dem aktiven Bestand entfernt, ihr Verlauf bleibt jedoch erhalten.']
    ,'Terugzetten': ['Restore', 'Wiederherstellen']
    ,'Geen gearchiveerde producten.': ['No archived products.', 'Keine archivierten Produkte.']
    ,'Product teruggezet in de voorraadlijst': ['Product restored to the inventory', 'Produkt wieder in den Bestand aufgenommen']
    ,'Verlopen voorraad opruimen': ['Clear expired inventory', 'Abgelaufenen Bestand entfernen']
    ,'Alle partijen waarvan de einddatum verstreken is worden als verspild geregistreerd. Je kunt iedere actie daarna via Geschiedenis terugdraaien.': ['All batches past their expiry date will be registered as waste. You can undo each action later through History.', 'Alle Chargen mit überschrittenem Ablaufdatum werden als Verschwendung erfasst. Jede Aktion kann später im Verlauf rückgängig gemacht werden.']
    ,'Dit raakt alleen voorraad die daadwerkelijk over de ingestelde einddatum is.': ['This only affects inventory that is actually past its set expiry date.', 'Dies betrifft nur Bestände, deren festgelegtes Ablaufdatum tatsächlich überschritten ist.']
    ,'Geen verlopen voorraad gevonden': ['No expired inventory found', 'Kein abgelaufener Bestand gefunden']
    ,'Partijgegevens bewerken': ['Edit batch details', 'Chargendaten bearbeiten']
    ,'Partijgegevens bijgewerkt': ['Batch details updated', 'Chargendaten aktualisiert']
    ,'Product archiveren': ['Archive product', 'Produkt archivieren']
    ,'Je kunt het product later via Gearchiveerd terugzetten.': ['You can restore the product later from Archived.', 'Du kannst das Produkt später unter Archiviert wiederherstellen.']
    ,'Product veilig gearchiveerd': ['Product archived safely', 'Produkt sicher archiviert']
    ,'Voorraad aanpassen': ['Adjust inventory', 'Bestand anpassen']
    ,'Product uit de voorraadlijst halen als de totale voorraad 0 wordt': ['Remove product from the inventory when total stock reaches 0', 'Produkt aus dem Bestand entfernen, wenn der Gesamtbestand 0 erreicht']
    ,'Bijvoorbeeld: gebruikt voor avondeten': ['For example: used for dinner', 'Zum Beispiel: fürs Abendessen verwendet']
    ,'Voorraad bijgewerkt': ['Inventory updated', 'Bestand aktualisiert']
    ,'Laatste voorraad verbruikt · product uit de lijst gehaald': ['Last stock consumed · product removed from the list', 'Letzten Bestand verbraucht · Produkt aus der Liste entfernt']
    ,'Bakken of verpakkingen toevoegen': ['Add containers or packages', 'Behälter oder Packungen hinzufügen']
    ,'iedere bak krijgt een eigen code': ['each container receives its own code', 'jeder Behälter erhält einen eigenen Code']
    ,'Productiedatum (optioneel)': ['Production date (optional)', 'Produktionsdatum (optional)']
    ,'Product bewerken': ['Edit product', 'Produkt bearbeiten']
    ,'Product bijgewerkt': ['Product updated', 'Produkt aktualisiert']
    ,'Vul een barcode in': ['Enter a barcode', 'Gib einen Barcode ein']
    ,'Vul eerst een productnaam in': ['Enter a product name first', 'Gib zuerst einen Produktnamen ein']
    ,'Vul eerst de naam in': ['Enter the name first', 'Gib zuerst den Namen ein']
    ,'Vul eerst de ingrediënten in': ['Enter the ingredients first', 'Gib zuerst die Zutaten ein']
    ,'Met Gemini gemaakt · controleer en pas zo nodig aan': ['Generated with Gemini · check and edit if needed', 'Mit Gemini erstellt · prüfen und bei Bedarf anpassen']
    ,'Ontbrekende ingrediënten toegevoegd': ['Missing ingredients added', 'Fehlende Zutaten hinzugefügt']
    ,'Recept bekijken en bewerken': ['View and edit recipe', 'Rezept ansehen und bearbeiten']
    ,'Recept bijgewerkt': ['Recipe updated', 'Rezept aktualisiert']
    ,'Recept opgeslagen': ['Recipe saved', 'Rezept gespeichert']
    ,'Recept verwijderen': ['Delete recipe', 'Rezept löschen']
    ,'Het recept en de planning ervan worden verwijderd.': ['The recipe and its planned meals will be deleted.', 'Das Rezept und seine geplanten Mahlzeiten werden gelöscht.']
    ,'Recept verwijderd': ['Recipe deleted', 'Rezept gelöscht']
    ,'Maak eerst een recept': ['Create a recipe first', 'Erstelle zuerst ein Rezept']
    ,'Maaltijd gepland': ['Meal planned', 'Mahlzeit geplant']
    ,'Nog geen houdbaarheidssjablonen.': ['No shelf-life templates yet.', 'Noch keine Haltbarkeitsvorlagen.']
    ,'Deze regel wordt gebruikt vóórdat Gemini wordt geraadpleegd.': ['This rule is used before consulting Gemini.', 'Diese Regel wird verwendet, bevor Gemini befragt wird.']
    ,'Houdbaarheidsregel bewerken': ['Edit shelf-life rule', 'Haltbarkeitsregel bearbeiten']
    ,'Houdbaarheidsregel bijgewerkt': ['Shelf-life rule updated', 'Haltbarkeitsregel aktualisiert']
    ,'Houdbaarheidsregel verborgen of verwijderd': ['Shelf-life rule hidden or deleted', 'Haltbarkeitsregel ausgeblendet oder gelöscht']
    ,'Standaardregel hersteld': ['Default rule restored', 'Standardregel wiederhergestellt']
    ,'Houdbaarheidssjabloon toevoegen': ['Add shelf-life template', 'Haltbarkeitsvorlage hinzufügen']
    ,'Home Stock gebruikt deze regel voortaan automatisch.': ['Home Stock will use this rule automatically from now on.', 'Home Stock verwendet diese Regel ab jetzt automatisch.']
    ,'Houdbaarheidssjabloon toegevoegd': ['Shelf-life template added', 'Haltbarkeitsvorlage hinzugefügt']
    ,'Zoeken naar een DYMO LabelWriter 400/450…': ['Searching for a DYMO LabelWriter 400/450…', 'Suche nach einem DYMO LabelWriter 400/450…']
    ,'Locatie toegevoegd': ['Location added', 'Lagerort hinzugefügt']
    ,'Profiel toegevoegd': ['Profile added', 'Profil hinzugefügt']
    ,'Gemini-instellingen opgeslagen': ['Gemini settings saved', 'Gemini-Einstellungen gespeichert']
    ,'Instellingen opgeslagen': ['Settings saved', 'Einstellungen gespeichert']
    ,'Scan een voorraadlabel of productbarcode om direct te verbruiken.': ['Scan an inventory label or product barcode to consume it directly.', 'Scanne ein Bestandsetikett oder einen Produktbarcode, um es direkt zu verbrauchen.']
    ,'Scan om een product te zoeken of toe te voegen.': ['Scan to find or add a product.', 'Scanne, um ein Produkt zu suchen oder hinzuzufügen.']
    ,'Afbeelding kon niet worden gescand': ['Image could not be scanned', 'Bild konnte nicht gescannt werden']
    ,'Live camera vereist HTTPS. Gebruik Foto scannen of voer de code handmatig in.': ['Live camera requires HTTPS. Use Scan photo or enter the code manually.', 'Die Live-Kamera benötigt HTTPS. Verwende Foto scannen oder gib den Code manuell ein.']
    ,'iPhone-camera actief · richt de code binnen het kader.': ['iPhone camera active · position the code inside the frame.', 'iPhone-Kamera aktiv · richte den Code im Rahmen aus.']
    ,'Camera actief · serverherkenning wordt gebruikt.': ['Camera active · server recognition is being used.', 'Kamera aktiv · Servererkennung wird verwendet.']
    ,'Geen cameratoegang. Sta camera toe in Safari of gebruik Foto scannen.': ['No camera access. Allow the camera in Safari or use Scan photo.', 'Kein Kamerazugriff. Erlaube die Kamera in Safari oder verwende Foto scannen.']
    ,'Geen barcode gevonden. Probeer dichterbij en met voldoende licht.': ['No barcode found. Try closer and with sufficient light.', 'Kein Barcode gefunden. Versuche es näher und mit ausreichend Licht.']
    ,'Home Stock draait al als webapp': ['Home Stock is already running as a web app', 'Home Stock läuft bereits als Web-App']
    ,'Home Stock op je iPhone': ['Home Stock on your iPhone', 'Home Stock auf deinem iPhone']
    ,'Installeren via Safari': ['Install via Safari', 'Über Safari installieren']
    ,'Begrepen': ['Got it', 'Verstanden']
    ,'Open deze pagina in Safari.': ['Open this page in Safari.', 'Öffne diese Seite in Safari.']
    ,'Zet op beginscherm': ['Add to Home Screen', 'Zum Home-Bildschirm']
    ,'Voeg toe': ['Add', 'Hinzufügen']
    ,'Tik onderin op de deelknop (vierkant met pijl omhoog).': ['Tap the Share button at the bottom (square with upward arrow).', 'Tippe unten auf die Teilen-Taste (Quadrat mit Pfeil nach oben).']
    ,'Kies Zet op beginscherm en daarna Voeg toe.': ['Choose Add to Home Screen and then Add.', 'Wähle Zum Home-Bildschirm und anschließend Hinzufügen.']
    ,'Open Home Stock voortaan via het nieuwe app-icoon.': ['From now on, open Home Stock using the new app icon.', 'Öffne Home Stock künftig über das neue App-Symbol.']
    ,'Voor live scannen moet de app via HTTPS worden geopend en moet cameratoegang zijn toegestaan.': ['For live scanning, the app must be opened over HTTPS and camera access must be allowed.', 'Für Live-Scans muss die App über HTTPS geöffnet und der Kamerazugriff erlaubt sein.']
    ,'Home Stock draait als geïnstalleerde webapp.': ['Home Stock is running as an installed web app.', 'Home Stock läuft als installierte Web-App.']
    ,'Donkere modus ingeschakeld': ['Dark mode enabled', 'Dunkler Modus aktiviert']
    ,'Lichte modus ingeschakeld': ['Light mode enabled', 'Heller Modus aktiviert']
    ,'Dit label printen': ['Print this label', 'Dieses Etikett drucken']
    ,'Label overgeslagen': ['Label skipped', 'Etikett übersprungen']
    ,'Label in wachtrij': ['Label added to queue', 'Etikett in Warteschlange']
    ,'Wachtrij is leeg': ['The queue is empty', 'Die Warteschlange ist leer']
    ,'Voorraadactie teruggedraaid': ['Inventory action undone', 'Bestandsaktion rückgängig gemacht']
    ,'Toegevoegd': ['Added', 'Hinzugefügt'], 'Verwijderen': ['Delete', 'Löschen']
    ,'preview': ['preview', 'Vorschau'], 'queued': ['queued', 'Warteschlange'], 'printed': ['printed', 'gedruckt'], 'skipped': ['skipped', 'übersprungen']
    ,'ARTIKEL': ['ITEM', 'ARTIKEL'], 'BAK': ['CONTAINER', 'BEHÄLTER']
    ,'stuks': ['pcs', 'Stück'], 'groente': ['vegetables', 'Gemüse'], 'fruit': ['fruit', 'Obst'], 'zuivel': ['dairy', 'Milchprodukte']
    ,'vlees': ['meat', 'Fleisch'], 'vis': ['fish', 'Fisch'], 'eieren': ['eggs', 'Eier'], 'bakkerij': ['bakery', 'Backwaren']
    ,'sauzen en kruiden': ['sauces and herbs', 'Soßen und Gewürze'], 'dranken': ['drinks', 'Getränke'], 'restjes': ['leftovers', 'Reste'], 'overig': ['other', 'Sonstiges']
  };

  const translations = {en: {}, de: {}};
  Object.entries(pairs).forEach(([source, values]) => {
    translations.en[source] = values[0]; translations.de[source] = values[1];
  });

  function detect() {
    const saved = localStorage.getItem('homeStockLanguage');
    if (supported.includes(saved)) return saved;
    const browser = (navigator.language || 'nl').slice(0, 2).toLowerCase();
    return supported.includes(browser) ? browser : 'nl';
  }
  let language = detect();

  const patterns = {
    en: [
      [/^(\d+) d\. over datum$/, '$1 d. expired'], [/^Nog (\d+) dagen$/, '$1 days left'],
      [/^(\d+) producten · ([\d.,]+) voorraad(?: · (\d+) verlopen)?$/, (_, a, b, c) => `${a} products · ${b} in stock${c ? ` · ${c} expired` : ''}`],
      [/^(\d+) porties · (\d+) min\.$/, '$1 servings · $2 min.'], [/^(\d+) ingrediënten$/, '$1 ingredients'],
      [/^(\d+) verspild$/, '$1 wasted'], [/^(\d+) dagen$/, '$1 days'], [/^geopend (\d+)$/, 'opened $1'],
      [/^(.*) · geproduceerd (.*)$/, '$1 · produced $2'], [/^(.*) · geopend (.*)$/, '$1 · opened $2'],
      [/^Alle (\d+) labels printen$/, 'Print all $1 labels'], [/^(\d+) printer\(s\) gevonden en klaar voor direct printen$/, '$1 printer(s) found and ready for direct printing'],
      [/^(.*) is over datum$/, '$1 has expired'], [/^(.*) is bijna over datum$/, '$1 is nearing expiry'], [/^Partij (.*)$/, 'Batch $1'], [/^(.*) bijna op$/, '$1 is running low'], [/^Nog ([\d.,]+) (.*)$/, '$1 $2 left'],
      [/^(\d+) verlopen partij\(en\) opgeruimd$/, '$1 expired batch(es) cleared'], [/^(\d+) bakken toegevoegd$/, '$1 containers added'], [/^(\d+) bak toegevoegd$/, '$1 container added'], [/^(.*) eenheid direct verbruikt · terugdraaien kan via Geschiedenis$/, '$1 unit consumed directly · can be undone through History']
    ],
    de: [
      [/^(\d+) d\. over datum$/, '$1 T. abgelaufen'], [/^Nog (\d+) dagen$/, 'Noch $1 Tage'],
      [/^(\d+) producten · ([\d.,]+) voorraad(?: · (\d+) verlopen)?$/, (_, a, b, c) => `${a} Produkte · ${b} auf Lager${c ? ` · ${c} abgelaufen` : ''}`],
      [/^(\d+) porties · (\d+) min\.$/, '$1 Portionen · $2 Min.'], [/^(\d+) ingrediënten$/, '$1 Zutaten'],
      [/^(\d+) verspild$/, '$1 verschwendet'], [/^(\d+) dagen$/, '$1 Tage'], [/^geopend (\d+)$/, 'geöffnet $1'],
      [/^(.*) · geproduceerd (.*)$/, '$1 · produziert $2'], [/^(.*) · geopend (.*)$/, '$1 · geöffnet $2'],
      [/^Alle (\d+) labels printen$/, 'Alle $1 Etiketten drucken'], [/^(\d+) printer\(s\) gevonden en klaar voor direct printen$/, '$1 Drucker gefunden und für Direktdruck bereit'],
      [/^(.*) is over datum$/, '$1 ist abgelaufen'], [/^(.*) is bijna over datum$/, '$1 läuft bald ab'], [/^Partij (.*)$/, 'Charge $1'], [/^(.*) bijna op$/, '$1 ist fast aufgebraucht'], [/^Nog ([\d.,]+) (.*)$/, 'Noch $1 $2'],
      [/^(\d+) verlopen partij\(en\) opgeruimd$/, '$1 abgelaufene Charge(n) entfernt'], [/^(\d+) bakken toegevoegd$/, '$1 Behälter hinzugefügt'], [/^(\d+) bak toegevoegd$/, '$1 Behälter hinzugefügt'], [/^(.*) eenheid direct verbruikt · terugdraaien kan via Geschiedenis$/, '$1 Einheit direkt verbraucht · kann im Verlauf rückgängig gemacht werden']
    ]
  };

  const fragments = {
    en: [[' dagen · ', ' days · '], [' dagen', ' days'], [' porties', ' servings'], [' ingrediënten', ' ingredients'], [' voorraad', ' in stock'], [' verlopen', ' expired'], [' automatisch', ' automatic'], [' geproduceerd ', ' produced '], [' geopend ', ' opened '], [' stuks', ' pcs'], [' · Koelkast', ' · Fridge'], [' · Vriezer', ' · Freezer'], [' · Voorraadkast', ' · Pantry'], ['INGELEGD DOOR ', 'STORED BY '], ['ARTIKEL ', 'ITEM '], [' · BAK ', ' · CONTAINER '], [' verdwijnt uit de actieve voorraad. Alle partijen, labels en geschiedenis blijven bewaard.', ' will be removed from active inventory. All batches, labels and history will be retained.'], [' · iedere bak krijgt een eigen code', ' · each container receives its own code'], [' labels naar de DYMO gestuurd', ' labels sent to the DYMO'], ['Label verzonden naar ', 'Label sent to ']],
    de: [[' dagen · ', ' Tage · '], [' dagen', ' Tage'], [' porties', ' Portionen'], [' ingrediënten', ' Zutaten'], [' voorraad', ' Bestand'], [' verlopen', ' abgelaufen'], [' automatisch', ' automatisch'], [' geproduceerd ', ' produziert '], [' geopend ', ' geöffnet '], [' stuks', ' Stück'], [' · Koelkast', ' · Kühlschrank'], [' · Vriezer', ' · Gefrierschrank'], [' · Voorraadkast', ' · Vorratsschrank'], ['INGELEGD DOOR ', 'EINGELAGERT VON '], ['ARTIKEL ', 'ARTIKEL '], [' · BAK ', ' · BEHÄLTER '], [' verdwijnt uit de actieve voorraad. Alle partijen, labels en geschiedenis blijven bewaard.', ' wird aus dem aktiven Bestand entfernt. Alle Chargen, Etiketten und der Verlauf bleiben erhalten.'], [' · iedere bak krijgt een eigen code', ' · jeder Behälter erhält einen eigenen Code'], [' labels naar de DYMO gestuurd', ' Etiketten an den DYMO gesendet'], ['Label verzonden naar ', 'Etikett gesendet an ']]
  };

  function t(value) {
    if (language === 'nl' || value == null) return String(value ?? '');
    const source = String(value);
    const decorated = source.match(/^([✓✨📷⌗＋←]\s*)(.+)$/u);
    if (decorated) return decorated[1] + t(decorated[2]);
    const direct = translations[language][source];
    if (direct) return direct;
    for (const [pattern, replacement] of patterns[language]) {
      if (pattern.test(source)) return source.replace(pattern, replacement);
    }
    let result = source;
    for (const [from, to] of fragments[language]) result = result.replace(from, to);
    return result;
  }

  function translateTextNode(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return;
    const original = node.nodeValue;
    const leading = original.match(/^\s*/)[0], trailing = original.match(/\s*$/)[0];
    const translated = t(original.trim());
    if (translated !== original.trim()) node.nodeValue = leading + translated + trailing;
  }
  function translateElement(element) {
    if (!(element instanceof Element) || ['SCRIPT', 'STYLE'].includes(element.tagName)) return;
    for (const attribute of ['placeholder', 'title', 'aria-label']) {
      if (element.hasAttribute(attribute)) element.setAttribute(attribute, t(element.getAttribute(attribute)));
    }
    for (const child of element.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) translateTextNode(child);
      else if (child.nodeType === Node.ELEMENT_NODE) translateElement(child);
    }
  }
  function syncSelectors() {
    document.querySelectorAll('[data-language-select]').forEach(select => { select.value = language; });
  }
  function setLanguage(next) {
    if (!supported.includes(next)) return;
    localStorage.setItem('homeStockLanguage', next);
    document.cookie = `home_stock_language=${next}; Path=/; Max-Age=31536000; SameSite=Lax`;
    location.reload();
  }
  function init() {
    document.documentElement.lang = language;
    document.cookie = `home_stock_language=${language}; Path=/; Max-Age=31536000; SameSite=Lax`;
    translateElement(document.body);
    document.title = t(document.title);
    document.querySelectorAll('#category-options option').forEach(option => { option.label = t(option.value); });
    document.querySelectorAll('input[name="unit"]').forEach(input => { if (input.value === 'stuks') input.value = t('stuks'); });
    syncSelectors();
    document.querySelectorAll('[data-language-select]').forEach(select => {
      select.onchange = () => setLanguage(select.value);
      select.setAttribute('aria-label', t('Taal'));
    });
    new MutationObserver(records => {
      for (const record of records) {
        if (record.type === 'characterData') translateTextNode(record.target);
        for (const node of record.addedNodes) {
          if (node.nodeType === Node.TEXT_NODE) translateTextNode(node);
          else if (node.nodeType === Node.ELEMENT_NODE) translateElement(node);
        }
      }
    }).observe(document.body, {subtree: true, childList: true, characterData: true});
  }

  window.I18N = {t, locale: () => localeMap[language], language: () => language, names, setLanguage};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
