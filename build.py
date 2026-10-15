#!/usr/bin/env python3
"""
build.py - generates the static pages of www.stimec.eu from one template.

Version: 1.5.0
Changelog:
  1.5.0 (2026-10-15) Added "Arrival and house rules" card (2nd floor, self
                     check-in, parking, no pets, smoking on balcony only).
  1.4.0 (2026-10-15) Automatic dark mode (follows device setting).
  1.3.0 (2026-10-15) Booking rating moved from the hero photo to the
                     highlights strip (readable score box).
  1.2.0 (2026-10-15) Brighter favicon (favicon.svg/.ico, apple-touch-icon);
                     Booking rating 9.1, no longer a link; removed
                     "book on Booking.com" link and Booking contact tile.
  1.1.0 (2026-10-15) Gallery reduced to 9 photos (no second bedroom shot,
                     coast, harbour, beach); new gallery heading text.
  1.0.0 (2026-10-15) First version. Builds / (sl), /en/, /de/, /it/,
                     gallery.html (redirect), sitemap.xml and robots.txt.

How to use:
  Edit texts in TEXT below (or PRICES / CONTACT), then run:  python3 build.py
  Commit the generated HTML files. No other tools needed.
"""
import json
import os
from datetime import date

SITE = "https://www.stimec.eu"
LANGS = ["sl", "en", "de", "it"]          # first one is served at /
GA_ID = "G-PX3ZXTV3Y9"
FORMSPREE = "https://formspree.io/f/mqarrvjw"
BOOKING_URL = "https://www.booking.com/hotel/si/apartma-stimec-izola.html"
FACEBOOK = "https://www.facebook.com/ApartmaIzola"
INSTAGRAM = "https://www.instagram.com/apartma_stimec_izola"
MAPS_LINK = "https://maps.app.goo.gl/E7dw93RXaq41dxHK6"
PHONE = "+38668937322"
PHONE_SHOW = "+386 68 937 322"
EMAIL = "stimec@gmail.com"
ADDRESS = "Senčna ulica 8, 6310 Izola"
GEO = (45.528154, 13.650045)
RATING = "9.1"

PRICES = {"high": 140, "mid": 115, "low": 90, "cleaning": 40,
          "taxAdult": 3.10, "taxChild": 1.55}

# Photos: (file stem, layout class, caption key)
PHOTOS = [
    ("balkon", "big", "c_balcony"),
    ("dnevna2", "", "c_living"),
    ("dnevna1", "", "c_living"),
    ("kuhinja", "", "c_kitchen"),
    ("soba1", "", "c_bedroom"),
    ("izola1", "big", "c_izola"),
    ("tloris", "tall plan", "c_plan"),
    ("kopalnica", "", "c_bathroom"),
    ("hisa1", "", "c_house"),
]


# Arrival and house rules (shown under the amenities card)
ARRIVAL = {
    "sl": ("Prihod in hišni red", [
        ("bi-building", "<b>2. nadstropje:</b> apartma je v drugem nadstropju hiše, do njega vodijo stopnice."),
        ("bi-key", "<b>Samostojni prihod:</b> ključ je v sefu za ključe pri hiši. Po rezervaciji prejmete PDF s slikami parkirnega mesta in lokacije ključa."),
        ("bi-p-circle", "<b>Parkiranje:</b> eno brezplačno parkirno mesto pred hišo."),
        ("bi-slash-circle", "<b>Hišni ljubljenčki</b> niso dovoljeni. <b>Kajenje</b> je dovoljeno samo na balkonu.")]),
    "en": ("Arrival and house rules", [
        ("bi-building", "<b>Second floor:</b> the apartment is on the second floor of the house, reached by stairs."),
        ("bi-key", "<b>Self check-in:</b> the key is in a key safe at the house. After booking you get a PDF with photos of the parking space and the key location."),
        ("bi-p-circle", "<b>Parking:</b> one free space in front of the house."),
        ("bi-slash-circle", "<b>No pets.</b> Smoking is allowed on the balcony only.")]),
    "de": ("Anreise und Hausregeln", [
        ("bi-building", "<b>Zweiter Stock:</b> Die Wohnung liegt im zweiten Stock des Hauses, der Zugang erfolgt über eine Treppe."),
        ("bi-key", "<b>Selbst-Check-in:</b> Der Schlüssel liegt in einem Schlüsselsafe am Haus. Nach der Buchung erhalten Sie ein PDF mit Fotos vom Parkplatz und vom Standort des Schlüssels."),
        ("bi-p-circle", "<b>Parken:</b> ein kostenloser Stellplatz vor dem Haus."),
        ("bi-slash-circle", "<b>Keine Haustiere.</b> Rauchen ist nur auf dem Balkon erlaubt.")]),
    "it": ("Arrivo e regole della casa", [
        ("bi-building", "<b>Secondo piano:</b> l'appartamento si trova al secondo piano della casa, si accede tramite scale."),
        ("bi-key", "<b>Self check-in:</b> la chiave è in una cassetta di sicurezza (key safe) presso la casa. Dopo la prenotazione ricevi un PDF con le foto del parcheggio e della posizione della chiave."),
        ("bi-p-circle", "<b>Parcheggio:</b> un posto auto gratuito davanti alla casa."),
        ("bi-slash-circle", "<b>Animali non ammessi.</b> Si può fumare solo sul balcone.")]),
}

PATH = {"sl": "/", "en": "/en/", "de": "/de/", "it": "/it/"}
LABEL = {"sl": "SLO", "en": "ENG", "de": "DEU", "it": "ITA"}
FC_LOCALE = {"sl": "sl", "en": "en-gb", "de": "de", "it": "it"}
NUM_LOCALE = {"sl": "sl-SI", "en": "en-GB", "de": "de-DE", "it": "it-IT"}

# "This page is also in <your language>" hints, written in the visitor's language
HINTS = {
    "sl": 'Stran je na voljo tudi v slovenščini: <a href="/" data-setlang="sl">preklopi</a>',
    "en": 'This page is also available in English: <a href="/en/" data-setlang="en">switch to English</a>',
    "de": 'Diese Seite gibt es auch auf Deutsch: <a href="/de/" data-setlang="de">auf Deutsch wechseln</a>',
    "it": 'Questa pagina è disponibile anche in italiano: <a href="/it/" data-setlang="it">passa all\'italiano</a>',
}

TEXT = {
"sl": {
    "title": "Apartma Štimec Izola – apartma z balkonom in pogledom na morje",
    "desc": "Apartma 65 m² v mirnem Jagodju nad Izolo: balkon s pogledom na morje, brezplačno parkirišče, klima in WiFi. Do plaže 700 m. Preverite proste termine.",
    "og_title": "Apartma Štimec – pogled na morje v Izoli",
    "h1": "Apartma z balkonom in pogledom na morje v Izoli",
    "sub": "65 m² · do 4 osebe · brezplačno parkirišče · 700 m do plaže",
    "check": "Preveri proste termine", "wa": "WhatsApp",
    "rating": "na Booking.com", "rating_lbl": "Ocena gostov",
    "nav_apt": "Apartma", "nav_photos": "Fotografije", "nav_prices": "Cenik", "nav_loc": "Lokacija", "nav_contact": "Kontakt",
    "hl": [("bi-sun", "Dva balkona", "pogled na morje"), ("bi-car-front", "Brezplačno parkiranje", "pri hiši"),
           ("bi-water", "Plaža 700 m", "približno 9 minut peš"), ("bi-house-heart", "65 m², do 4 osebe", "spalnica + dnevni prostor")],
    "ph_eyebrow": "Fotografije", "ph_h2": "Poglejte si naše slike",
    "ph_lead": "Kliknite na sliko za večji prikaz.",
    "c_balcony": "Balkon s pogledom na morje", "c_living": "Dnevni prostor", "c_kitchen": "Kuhinja", "c_bedroom": "Spalnica",
    "c_bathroom": "Kopalnica", "c_plan": "Tloris apartmaja", "c_house": "Hiša in parkirišče", "c_izola": "Izola iz zraka",
    "c_coast": "Obala pri Izoli", "c_harbour": "Pristanišče v Izoli", "c_beach": "Plaža",
    "band_h2": "Vam je všeč?", "band_p": "Preverite proste termine in takoj vidite ceno.",
    "apt_eyebrow": "Apartma", "apt_h2": "Mirno, svetlo in blizu morja",
    "apt_lead": "Apartma meri 65 m² in je v družinski hiši v mirnem naselju Jagodje nad Izolo. Primeren je za 2 do 4 osebe.",
    "rooms": [("bi-moon-stars", "Spalnica", "Dve enojni postelji, omara, izhod na balkon."),
              ("bi-layout-text-sidebar-reverse", "Dnevni prostor", "Kavč in raztegljivo ležišče za 1–2 osebi, jedilna miza, TV, izhod na velik balkon."),
              ("bi-cup-hot", "Kuhinja", "Hladilnik, zamrzovalnik, pomivalni stroj, opekač, kavni aparat, jedilni kot."),
              ("bi-droplet", "Kopalnica", "Kad s tušem, pralni stroj, sušilec za lase.")],
    "am_h3": "V apartmaju",
    "amen": [("bi-wifi", "Brezplačen WiFi"), ("bi-snow", "Klima (hlajenje in gretje)"), ("bi-tv", "Smart TV z Netflixom"),
             ("bi-p-circle", "Brezplačno zasebno parkirišče"), ("bi-basket", "Posteljnina in brisače"),
             ("bi-moisture", "Pralni stroj"), ("bi-cup-straw", "Pomivalni stroj"), ("bi-sun", "Dva balkona s pogledom na morje")],
    "pr_eyebrow": "Cenik", "pr_h2": "Cene in pogoji", "pr_lead": "Cena velja za celoten apartma na noč, ne glede na število oseb.",
    "seasons": [("Julij in avgust", "glavna sezona, najmanj 3 noči", PRICES["high"]),
                ("Junij in september", "", PRICES["mid"]),
                ("Oktober–maj", "", PRICES["low"])],
    "per_night": "/ noč",
    "rules_h3": "Dobro je vedeti",
    "rules": [("bi-check2-circle", "<b>V ceni:</b> posteljnina, brisače, elektrika, plin."),
              ("bi-stars", "<b>Končno čiščenje:</b> 40 € enkratno."),
              ("bi-receipt", "<b>Turistična taksa:</b> odrasli 3,10 €, otroci 7–17 let 1,55 €, otroci do 7 let brezplačno (na osebo na noč)."),
              ("bi-clock", "<b>Prihod</b> od 15:00, <b>odhod</b> do 10:00."),
              ("bi-calendar-check", "<b>Rezervacija</b> je potrjena po plačilu 30 % akontacije."),
              ("bi-cash-coin", "<b>Plačilo:</b> gotovina ob prihodu ali nakazilo na račun."),
              ("bi-calendar-x", "<b>Odpoved:</b> več kot 30 dni pred prihodom 100 % vračilo, 14–30 dni 50 %, manj kot 14 dni brez vračila.")],
    "bk_eyebrow": "Rezervacija", "bk_h2": "Prosti termini in povpraševanje",
    "bk_lead": "Rdeči dnevi so zasedeni. Izberite datume v koledarju ali v obrazcu in takoj boste videli ceno. Odgovorimo po e-pošti s potrditvijo.",
    "free": "prosto", "booked": "zasedeno",
    "f_arr": "Prihod", "f_dep": "Odhod", "f_adults": "Odrasli", "f_kids": "Otroci 7–17", "f_small": "Otroci do 7",
    "f_name": "Ime in priimek", "f_email": "E-pošta", "f_phone": "Telefon (neobvezno)", "f_msg": "Sporočilo (neobvezno)",
    "f_send": "Pošlji povpraševanje",
    "subject": "Povpraševanje – Apartma Štimec",
    "t": {"estHint": "Izberite datume in videli boste ceno.", "estBadDates": "Odhod mora biti po prihodu.",
          "estBooked": "Nekateri izbrani dnevi so že zasedeni.", "estMin": "Julij in avgust: najmanj 3 noči.",
          "estMax": "Največ 4 osebe.", "night": "noč", "nights": "noči", "cleaning": "Končno čiščenje",
          "tax": "Turistična taksa", "total": "Skupaj (okvirno)", "estNote": "Končno ceno potrdimo v odgovoru.",
          "sent": "Hvala! Odgovorimo vam po e-pošti.", "failed": "Pošiljanje ni uspelo. Pišite nam na WhatsApp ali e-pošto."},
    "loc_eyebrow": "Lokacija", "loc_h2": "Jagodje, Izola",
    "loc_lead": "Jagodje je mirno stanovanjsko naselje na robu Izole. Do morja in trgovine pridete peš, do starega mestnega jedra je kratka vožnja ali sprehod.",
    "dist": [("Plaža", "700 m"), ("Trgovina", "250 m"), ("Staro mestno jedro Izole", "1,5 km")],
    "directions": "Navodila za pot",
    "ct_eyebrow": "Kontakt", "ct_h2": "Pišite ali pokličite",
    "ct_lead": "Vprašanja pred rezervacijo? Najhitreje nas dosežete na WhatsApp.",
    "ct_wa": "Pišite nam", "ct_phone": "Telefon", "ct_mail": "E-pošta",
    "cookie": "Z Google Analytics štejemo obiske strani. Piškotke uporabimo samo z vašim dovoljenjem.",
    "cookie_yes": "Sprejmi", "cookie_no": "Zavrni",
    "mb_book": "Prosti termini",
    "lb_close": "Zapri", "lb_prev": "Prejšnja", "lb_next": "Naslednja",
},
"en": {
    "title": "Apartment Štimec Izola – sea-view holiday apartment with parking",
    "desc": "65 m² holiday apartment in quiet Jagodje above Izola, Slovenia: sea-view balcony, free private parking, air conditioning and WiFi. Beach 700 m. Check availability.",
    "og_title": "Apartment Štimec – sea view in Izola, Slovenia",
    "h1": "Sea-view apartment with balcony in Izola",
    "sub": "65 m² · up to 4 guests · free parking · 700 m to the beach",
    "check": "Check availability", "wa": "WhatsApp",
    "rating": "on Booking.com", "rating_lbl": "Guest rating",
    "nav_apt": "Apartment", "nav_photos": "Photos", "nav_prices": "Prices", "nav_loc": "Location", "nav_contact": "Contact",
    "hl": [("bi-sun", "Two balconies", "with sea view"), ("bi-car-front", "Free parking", "at the house"),
           ("bi-water", "Beach 700 m", "about 9 minutes on foot"), ("bi-house-heart", "65 m², up to 4", "bedroom + living room")],
    "ph_eyebrow": "Photos", "ph_h2": "Take a look at our photos",
    "ph_lead": "Click a photo to see it larger.",
    "c_balcony": "Balcony with sea view", "c_living": "Living room", "c_kitchen": "Kitchen", "c_bedroom": "Bedroom",
    "c_bathroom": "Bathroom", "c_plan": "Floor plan", "c_house": "The house and parking", "c_izola": "Izola from above",
    "c_coast": "Coast near Izola", "c_harbour": "Izola harbour", "c_beach": "Beach",
    "band_h2": "Like what you see?", "band_p": "Check free dates and see the price straight away.",
    "apt_eyebrow": "The apartment", "apt_h2": "Quiet, bright and close to the sea",
    "apt_lead": "The 65 m² apartment is in a family house in Jagodje, a quiet residential area above Izola. It suits 2 to 4 guests.",
    "rooms": [("bi-moon-stars", "Bedroom", "Two single beds, wardrobe, door to the balcony."),
              ("bi-layout-text-sidebar-reverse", "Living room", "Sofa and extendable bed for 1–2 people, dining table, TV, door to the large balcony."),
              ("bi-cup-hot", "Kitchen", "Fridge, freezer, dishwasher, toaster, coffee maker, dining corner."),
              ("bi-droplet", "Bathroom", "Bathtub with shower, washing machine, hair dryer.")],
    "am_h3": "What's included",
    "amen": [("bi-wifi", "Free WiFi"), ("bi-snow", "Air conditioning (cooling and heating)"), ("bi-tv", "Smart TV with Netflix"),
             ("bi-p-circle", "Free private parking"), ("bi-basket", "Bed linen and towels"),
             ("bi-moisture", "Washing machine"), ("bi-cup-straw", "Dishwasher"), ("bi-sun", "Two sea-view balconies")],
    "pr_eyebrow": "Prices", "pr_h2": "Prices and terms", "pr_lead": "Prices are for the whole apartment per night, regardless of the number of guests.",
    "seasons": [("July and August", "high season, minimum 3 nights", PRICES["high"]),
                ("June and September", "", PRICES["mid"]),
                ("October–May", "", PRICES["low"])],
    "per_night": "/ night",
    "rules_h3": "Good to know",
    "rules": [("bi-check2-circle", "<b>Included:</b> bed linen, towels, electricity, gas."),
              ("bi-stars", "<b>Final cleaning:</b> €40, once per stay."),
              ("bi-receipt", "<b>Tourist tax:</b> adults €3.10, children 7–17 €1.55, under 7 free (per person per night)."),
              ("bi-clock", "<b>Check-in</b> from 15:00, <b>check-out</b> by 10:00."),
              ("bi-calendar-check", "<b>Booking</b> is confirmed after a 30% deposit."),
              ("bi-cash-coin", "<b>Payment:</b> cash on arrival or bank transfer."),
              ("bi-calendar-x", "<b>Cancellation:</b> more than 30 days before arrival full refund, 14–30 days 50%, less than 14 days no refund.")],
    "bk_eyebrow": "Booking", "bk_h2": "Availability and booking request",
    "bk_lead": "Red days are booked. Pick your dates in the calendar or the form and you'll see the price right away. We confirm by email.",
    "free": "free", "booked": "booked",
    "f_arr": "Arrival", "f_dep": "Departure", "f_adults": "Adults", "f_kids": "Children 7–17", "f_small": "Children under 7",
    "f_name": "Full name", "f_email": "Email", "f_phone": "Phone (optional)", "f_msg": "Message (optional)",
    "f_send": "Send request",
    "subject": "Booking request – Apartment Štimec",
    "t": {"estHint": "Choose your dates to see the price.", "estBadDates": "Departure must be after arrival.",
          "estBooked": "Some of these dates are already booked.", "estMin": "July and August: minimum 3 nights.",
          "estMax": "Maximum 4 guests.", "night": "night", "nights": "nights", "cleaning": "Final cleaning",
          "tax": "Tourist tax", "total": "Total (approx.)", "estNote": "We confirm the final price in our reply.",
          "sent": "Thank you! We'll reply by email.", "failed": "Sending failed. Please message us on WhatsApp or by email."},
    "loc_eyebrow": "Location", "loc_h2": "Jagodje, Izola",
    "loc_lead": "Jagodje is a quiet residential area on the edge of Izola. The sea and the shop are within walking distance, and the old town is a short drive or a longer walk away.",
    "dist": [("Beach", "700 m"), ("Shop", "250 m"), ("Izola old town", "1.5 km")],
    "directions": "Get directions",
    "ct_eyebrow": "Contact", "ct_h2": "Message or call us",
    "ct_lead": "Questions before you book? WhatsApp is the fastest way to reach us.",
    "ct_wa": "Message us", "ct_phone": "Phone", "ct_mail": "Email",
    "cookie": "We use Google Analytics to count visits. Cookies are set only if you agree.",
    "cookie_yes": "Accept", "cookie_no": "Decline",
    "mb_book": "Check dates",
    "lb_close": "Close", "lb_prev": "Previous", "lb_next": "Next",
},
"de": {
    "title": "Ferienwohnung Izola mit Meerblick und Parkplatz – Apartma Štimec",
    "desc": "Ferienwohnung mit 65 m² im ruhigen Jagodje oberhalb von Izola, Slowenien: Balkon mit Meerblick, kostenloser Privatparkplatz, Klimaanlage, WLAN. Strand 700 m.",
    "og_title": "Apartma Štimec – Ferienwohnung mit Meerblick in Izola",
    "h1": "Ferienwohnung mit Balkon und Meerblick in Izola",
    "sub": "65 m² · bis 4 Personen · kostenloser Parkplatz · 700 m zum Strand",
    "check": "Freie Termine prüfen", "wa": "WhatsApp",
    "rating": "auf Booking.com", "rating_lbl": "Gästebewertung",
    "nav_apt": "Wohnung", "nav_photos": "Fotos", "nav_prices": "Preise", "nav_loc": "Lage", "nav_contact": "Kontakt",
    "hl": [("bi-sun", "Zwei Balkone", "mit Meerblick"), ("bi-car-front", "Kostenloser Parkplatz", "direkt am Haus"),
           ("bi-water", "Strand 700 m", "ca. 9 Minuten zu Fuß"), ("bi-house-heart", "65 m², bis 4 Personen", "Schlafzimmer + Wohnraum")],
    "ph_eyebrow": "Fotos", "ph_h2": "Sehen Sie sich unsere Fotos an",
    "ph_lead": "Zum Vergrößern auf ein Foto klicken.",
    "c_balcony": "Balkon mit Meerblick", "c_living": "Wohnraum", "c_kitchen": "Küche", "c_bedroom": "Schlafzimmer",
    "c_bathroom": "Badezimmer", "c_plan": "Grundriss", "c_house": "Haus und Parkplatz", "c_izola": "Izola von oben",
    "c_coast": "Küste bei Izola", "c_harbour": "Hafen von Izola", "c_beach": "Strand",
    "band_h2": "Gefällt es Ihnen?", "band_p": "Prüfen Sie freie Termine und sehen Sie den Preis sofort.",
    "apt_eyebrow": "Die Wohnung", "apt_h2": "Ruhig, hell und nah am Meer",
    "apt_lead": "Die 65 m² große Wohnung liegt in einem Familienhaus in Jagodje, einem ruhigen Wohnviertel oberhalb von Izola. Ideal für 2 bis 4 Personen.",
    "rooms": [("bi-moon-stars", "Schlafzimmer", "Zwei Einzelbetten, Kleiderschrank, Zugang zum Balkon."),
              ("bi-layout-text-sidebar-reverse", "Wohnraum", "Sofa und Ausziehbett für 1–2 Personen, Esstisch, TV, Zugang zum großen Balkon."),
              ("bi-cup-hot", "Küche", "Kühlschrank, Gefrierschrank, Geschirrspüler, Toaster, Kaffeemaschine, Essecke."),
              ("bi-droplet", "Badezimmer", "Badewanne mit Dusche, Waschmaschine, Föhn.")],
    "am_h3": "Ausstattung",
    "amen": [("bi-wifi", "Kostenloses WLAN"), ("bi-snow", "Klimaanlage (Kühlen und Heizen)"), ("bi-tv", "Smart-TV mit Netflix"),
             ("bi-p-circle", "Kostenloser Privatparkplatz"), ("bi-basket", "Bettwäsche und Handtücher"),
             ("bi-moisture", "Waschmaschine"), ("bi-cup-straw", "Geschirrspüler"), ("bi-sun", "Zwei Balkone mit Meerblick")],
    "pr_eyebrow": "Preise", "pr_h2": "Preise und Bedingungen", "pr_lead": "Die Preise gelten für die ganze Wohnung pro Nacht, unabhängig von der Personenzahl.",
    "seasons": [("Juli und August", "Hauptsaison, mindestens 3 Nächte", PRICES["high"]),
                ("Juni und September", "", PRICES["mid"]),
                ("Oktober–Mai", "", PRICES["low"])],
    "per_night": "/ Nacht",
    "rules_h3": "Gut zu wissen",
    "rules": [("bi-check2-circle", "<b>Inklusive:</b> Bettwäsche, Handtücher, Strom, Gas."),
              ("bi-stars", "<b>Endreinigung:</b> 40 € einmalig."),
              ("bi-receipt", "<b>Kurtaxe:</b> Erwachsene 3,10 €, Kinder 7–17 Jahre 1,55 €, unter 7 Jahren frei (pro Person und Nacht)."),
              ("bi-clock", "<b>Anreise</b> ab 15:00, <b>Abreise</b> bis 10:00."),
              ("bi-calendar-check", "<b>Die Buchung</b> ist nach einer Anzahlung von 30 % bestätigt."),
              ("bi-cash-coin", "<b>Zahlung:</b> bar bei Ankunft oder per Überweisung."),
              ("bi-calendar-x", "<b>Stornierung:</b> mehr als 30 Tage vor Anreise volle Erstattung, 14–30 Tage 50 %, weniger als 14 Tage keine Erstattung.")],
    "bk_eyebrow": "Buchung", "bk_h2": "Freie Termine und Anfrage",
    "bk_lead": "Rote Tage sind belegt. Wählen Sie Ihre Daten im Kalender oder im Formular, dann sehen Sie sofort den Preis. Wir bestätigen per E-Mail.",
    "free": "frei", "booked": "belegt",
    "f_arr": "Anreise", "f_dep": "Abreise", "f_adults": "Erwachsene", "f_kids": "Kinder 7–17", "f_small": "Kinder unter 7",
    "f_name": "Vor- und Nachname", "f_email": "E-Mail", "f_phone": "Telefon (optional)", "f_msg": "Nachricht (optional)",
    "f_send": "Anfrage senden",
    "subject": "Anfrage – Apartma Štimec",
    "t": {"estHint": "Wählen Sie Ihre Daten, um den Preis zu sehen.", "estBadDates": "Die Abreise muss nach der Anreise liegen.",
          "estBooked": "Einige dieser Tage sind bereits belegt.", "estMin": "Juli und August: mindestens 3 Nächte.",
          "estMax": "Höchstens 4 Personen.", "night": "Nacht", "nights": "Nächte", "cleaning": "Endreinigung",
          "tax": "Kurtaxe", "total": "Gesamt (ca.)", "estNote": "Den endgültigen Preis bestätigen wir in unserer Antwort.",
          "sent": "Vielen Dank! Wir antworten Ihnen per E-Mail.", "failed": "Senden fehlgeschlagen. Bitte schreiben Sie uns per WhatsApp oder E-Mail."},
    "loc_eyebrow": "Lage", "loc_h2": "Jagodje, Izola",
    "loc_lead": "Jagodje ist ein ruhiges Wohnviertel am Rand von Izola. Meer und Supermarkt erreichen Sie zu Fuß, die Altstadt mit einer kurzen Fahrt oder einem längeren Spaziergang.",
    "dist": [("Strand", "700 m"), ("Supermarkt", "250 m"), ("Altstadt Izola", "1,5 km")],
    "directions": "Route planen",
    "ct_eyebrow": "Kontakt", "ct_h2": "Schreiben Sie uns oder rufen Sie an",
    "ct_lead": "Fragen vor der Buchung? Am schnellsten erreichen Sie uns per WhatsApp.",
    "ct_wa": "Nachricht schreiben", "ct_phone": "Telefon", "ct_mail": "E-Mail",
    "cookie": "Wir zählen Besuche mit Google Analytics. Cookies setzen wir nur mit Ihrer Zustimmung.",
    "cookie_yes": "Akzeptieren", "cookie_no": "Ablehnen",
    "mb_book": "Freie Termine",
    "lb_close": "Schließen", "lb_prev": "Zurück", "lb_next": "Weiter",
},
"it": {
    "title": "Appartamento a Isola (Izola) con vista mare e parcheggio – Štimec",
    "desc": "Appartamento di 65 m² nella tranquilla Jagodje sopra Isola, Slovenia: balcone con vista mare, parcheggio privato gratuito, aria condizionata e WiFi. Spiaggia a 700 m.",
    "og_title": "Appartamento Štimec – vista mare a Isola (Izola)",
    "h1": "Appartamento con balcone e vista mare a Isola",
    "sub": "65 m² · fino a 4 ospiti · parcheggio gratuito · 700 m dalla spiaggia",
    "check": "Verifica disponibilità", "wa": "WhatsApp",
    "rating": "su Booking.com", "rating_lbl": "Valutazione degli ospiti",
    "nav_apt": "Appartamento", "nav_photos": "Foto", "nav_prices": "Prezzi", "nav_loc": "Posizione", "nav_contact": "Contatti",
    "hl": [("bi-sun", "Due balconi", "con vista mare"), ("bi-car-front", "Parcheggio gratuito", "presso la casa"),
           ("bi-water", "Spiaggia a 700 m", "circa 9 minuti a piedi"), ("bi-house-heart", "65 m², fino a 4", "camera + soggiorno")],
    "ph_eyebrow": "Foto", "ph_h2": "Guarda le nostre foto",
    "ph_lead": "Clicca su una foto per ingrandirla.",
    "c_balcony": "Balcone con vista mare", "c_living": "Soggiorno", "c_kitchen": "Cucina", "c_bedroom": "Camera da letto",
    "c_bathroom": "Bagno", "c_plan": "Planimetria", "c_house": "La casa e il parcheggio", "c_izola": "Isola dall'alto",
    "c_coast": "La costa vicino a Isola", "c_harbour": "Il porto di Isola", "c_beach": "Spiaggia",
    "band_h2": "Ti piace?", "band_p": "Verifica le date libere e vedi subito il prezzo.",
    "apt_eyebrow": "L'appartamento", "apt_h2": "Tranquillo, luminoso e vicino al mare",
    "apt_lead": "L'appartamento di 65 m² si trova in una casa di famiglia a Jagodje, una zona residenziale tranquilla sopra Isola. Adatto da 2 a 4 ospiti.",
    "rooms": [("bi-moon-stars", "Camera da letto", "Due letti singoli, armadio, accesso al balcone."),
              ("bi-layout-text-sidebar-reverse", "Soggiorno", "Divano e letto estraibile per 1–2 persone, tavolo da pranzo, TV, accesso al balcone grande."),
              ("bi-cup-hot", "Cucina", "Frigorifero, congelatore, lavastoviglie, tostapane, macchina del caffè, angolo pranzo."),
              ("bi-droplet", "Bagno", "Vasca con doccia, lavatrice, asciugacapelli.")],
    "am_h3": "Dotazioni",
    "amen": [("bi-wifi", "WiFi gratuito"), ("bi-snow", "Aria condizionata (caldo e freddo)"), ("bi-tv", "Smart TV con Netflix"),
             ("bi-p-circle", "Parcheggio privato gratuito"), ("bi-basket", "Biancheria e asciugamani"),
             ("bi-moisture", "Lavatrice"), ("bi-cup-straw", "Lavastoviglie"), ("bi-sun", "Due balconi con vista mare")],
    "pr_eyebrow": "Prezzi", "pr_h2": "Prezzi e condizioni", "pr_lead": "I prezzi si intendono per l'intero appartamento a notte, indipendentemente dal numero di ospiti.",
    "seasons": [("Luglio e agosto", "alta stagione, minimo 3 notti", PRICES["high"]),
                ("Giugno e settembre", "", PRICES["mid"]),
                ("Ottobre–maggio", "", PRICES["low"])],
    "per_night": "/ notte",
    "rules_h3": "Buono a sapersi",
    "rules": [("bi-check2-circle", "<b>Incluso:</b> biancheria, asciugamani, elettricità, gas."),
              ("bi-stars", "<b>Pulizia finale:</b> 40 € una tantum."),
              ("bi-receipt", "<b>Tassa di soggiorno:</b> adulti 3,10 €, bambini 7–17 anni 1,55 €, sotto i 7 anni gratis (a persona a notte)."),
              ("bi-clock", "<b>Arrivo</b> dalle 15:00, <b>partenza</b> entro le 10:00."),
              ("bi-calendar-check", "<b>La prenotazione</b> è confermata dopo un acconto del 30%."),
              ("bi-cash-coin", "<b>Pagamento:</b> in contanti all'arrivo o con bonifico."),
              ("bi-calendar-x", "<b>Cancellazione:</b> oltre 30 giorni prima dell'arrivo rimborso totale, 14–30 giorni 50%, meno di 14 giorni nessun rimborso.")],
    "bk_eyebrow": "Prenotazione", "bk_h2": "Disponibilità e richiesta",
    "bk_lead": "I giorni rossi sono occupati. Scegli le date nel calendario o nel modulo e vedrai subito il prezzo. Confermiamo via e-mail.",
    "free": "libero", "booked": "occupato",
    "f_arr": "Arrivo", "f_dep": "Partenza", "f_adults": "Adulti", "f_kids": "Bambini 7–17", "f_small": "Bambini sotto i 7",
    "f_name": "Nome e cognome", "f_email": "E-mail", "f_phone": "Telefono (facoltativo)", "f_msg": "Messaggio (facoltativo)",
    "f_send": "Invia richiesta",
    "subject": "Richiesta – Appartamento Štimec",
    "t": {"estHint": "Scegli le date per vedere il prezzo.", "estBadDates": "La partenza deve essere dopo l'arrivo.",
          "estBooked": "Alcune di queste date sono già occupate.", "estMin": "Luglio e agosto: minimo 3 notti.",
          "estMax": "Massimo 4 ospiti.", "night": "notte", "nights": "notti", "cleaning": "Pulizia finale",
          "tax": "Tassa di soggiorno", "total": "Totale (indicativo)", "estNote": "Il prezzo finale lo confermiamo nella risposta.",
          "sent": "Grazie! Ti risponderemo via e-mail.", "failed": "Invio non riuscito. Scrivici su WhatsApp o via e-mail."},
    "loc_eyebrow": "Posizione", "loc_h2": "Jagodje, Isola",
    "loc_lead": "Jagodje è una zona residenziale tranquilla ai margini di Isola. Il mare e il supermercato si raggiungono a piedi, il centro storico con un breve tragitto in auto o una passeggiata.",
    "dist": [("Spiaggia", "700 m"), ("Supermercato", "250 m"), ("Centro storico di Isola", "1,5 km")],
    "directions": "Indicazioni stradali",
    "ct_eyebrow": "Contatti", "ct_h2": "Scrivici o chiamaci",
    "ct_lead": "Domande prima di prenotare? Il modo più rapido è WhatsApp.",
    "ct_wa": "Scrivici", "ct_phone": "Telefono", "ct_mail": "E-mail",
    "cookie": "Usiamo Google Analytics per contare le visite. I cookie vengono impostati solo con il tuo consenso.",
    "cookie_yes": "Accetta", "cookie_no": "Rifiuta",
    "mb_book": "Verifica date",
    "lb_close": "Chiudi", "lb_prev": "Precedente", "lb_next": "Successiva",
},
}


def head(lang, t):
    url = SITE + PATH[lang]
    alts = "\n".join(f'  <link rel="alternate" hreflang="{l}" href="{SITE}{PATH[l]}">' for l in LANGS)
    schema = {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "name": "Apartma Štimec Izola",
        "description": t["desc"],
        "url": url,
        "image": [f"{SITE}/img/og.jpg", f"{SITE}/img/dnevna2.webp", f"{SITE}/img/soba1.webp"],
        "telephone": PHONE,
        "email": EMAIL,
        "priceRange": f"€{PRICES['low']}–€{PRICES['high']}",
        "checkinTime": "15:00",
        "checkoutTime": "10:00",
        "petsAllowed": False,
        "address": {"@type": "PostalAddress", "streetAddress": "Senčna ulica 8", "addressLocality": "Izola",
                    "postalCode": "6310", "addressCountry": "SI"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": MAPS_LINK,
        "sameAs": [BOOKING_URL, FACEBOOK, INSTAGRAM],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in ["Free private parking", "Sea view balcony", "Air conditioning",
                                     "Free WiFi", "Smart TV", "Dishwasher", "Washing machine"]],
    }
    schema = {k: v for k, v in schema.items() if v is not None}
    fc_locale = "" if lang == "en" else \
        f'<script defer src="https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.11/locales/{FC_LOCALE[lang]}.global.min.js"></script>\n  '
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t['title']}</title>
  <meta name="description" content="{t['desc']}">
  <link rel="canonical" href="{url}">
{alts}
  <link rel="alternate" hreflang="x-default" href="{SITE}/en/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{t['og_title']}">
  <meta property="og:description" content="{t['desc']}">
  <meta property="og:image" content="{SITE}/img/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:url" content="{url}">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#16324f" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0f1b28" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="preload" as="image" href="/img/balkon.webp" imagesrcset="/img/balkon-sm.webp 720w, /img/balkon.webp 1448w" imagesizes="100vw">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <link href="/assets/site.css" rel="stylesheet">
  <script defer src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
  {fc_locale}<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
  </script>
</head>"""


def nav(lang, t):
    langs = "".join(
        f'<a href="{PATH[l]}" hreflang="{l}" lang="{l}" data-setlang="{l}"'
        f'{" aria-current=\"true\"" if l == lang else ""}>{LABEL[l]}</a>' for l in LANGS)
    return f"""
<div class="lang-hint" id="lang-hint"><div class="container d-flex justify-content-between align-items-center gap-2">
  <span class="hint-text"></span><button type="button" aria-label="{t['lb_close']}"><i class="bi bi-x-lg"></i></button></div></div>
<nav class="navbar navbar-expand-lg sticky-top site-nav">
  <div class="container">
    <a class="navbar-brand" href="{PATH[lang]}">Apartma Štimec</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav" aria-controls="nav" aria-expanded="false" aria-label="Menu">
      <span class="navbar-toggler-icon"></span></button>
    <div class="collapse navbar-collapse" id="nav">
      <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-1">
        <li class="nav-item"><a class="nav-link" href="#photos">{t['nav_photos']}</a></li>
        <li class="nav-item"><a class="nav-link" href="#apartment">{t['nav_apt']}</a></li>
        <li class="nav-item"><a class="nav-link" href="#prices">{t['nav_prices']}</a></li>
        <li class="nav-item"><a class="nav-link" href="#location">{t['nav_loc']}</a></li>
        <li class="nav-item"><a class="nav-link" href="#contact">{t['nav_contact']}</a></li>
        <li class="nav-item lang-switch ms-lg-3 my-2 my-lg-0">{langs}</li>
        <li class="nav-item ms-lg-3 d-none d-lg-block"><a class="btn btn-navy btn-sm px-3 py-2" href="#booking">{t['check']}</a></li>
      </ul>
    </div>
  </div>
</nav>"""


def body(lang, t):
    wa = f"https://wa.me/{PHONE.lstrip('+')}"
    hl = "".join(f"""
      <div class="col-6 col-lg"><div class="hl"><i class="bi {i}" aria-hidden="true"></i><div><strong>{a}</strong><span>{b}</span></div></div></div>"""
                 for i, a, b in t["hl"])
    hl = f"""
      <div class="col-12 col-lg-auto pe-lg-4"><div class="hl-rating"><span class="score">{RATING}</span><div><strong>{t['rating_lbl']}</strong><span>{RATING} / 10 {t['rating']}</span></div></div></div>""" + hl
    gallery = "".join(f"""
      <button type="button" class="{cls}" data-full="/img/{f}.webp" aria-label="{t[c]}">
        <img src="/img/{f}-sm.webp" alt="{t[c]}" loading="lazy" decoding="async"><span class="cap">{t[c]}</span></button>"""
                      for f, cls, c in PHOTOS)
    rooms = "".join(f"""
      <div class="col-sm-6"><div class="room"><i class="bi {i}" aria-hidden="true"></i><h3>{h}</h3><p>{p}</p></div></div>"""
                    for i, h, p in t["rooms"])
    arrival = "".join(f'<li><i class="bi {i}" aria-hidden="true"></i><span>{r}</span></li>' for i, r in ARRIVAL[lang][1])
    amen = "".join(f'<li><i class="bi {i}" aria-hidden="true"></i>{n}</li>' for i, n in t["amen"])
    seasons = "".join(f"""
        <div class="price-row"><div class="season">{s}{f'<small>{n}</small>' if n else ''}</div>
          <div class="amount">{p} €<small> {t['per_night']}</small></div></div>""" for s, n, p in t["seasons"])
    rules = "".join(f'<li><i class="bi {i}" aria-hidden="true"></i><span>{r}</span></li>' for i, r in t["rules"])
    dist = "".join(f"<li><span>{a}</span><b>{b}</b></li>" for a, b in t["dist"])
    num = lambda id_, label, v, mx: f"""
            <div class="col-4"><label class="form-label" for="{id_}">{label}</label>
              <select class="form-select" id="{id_}" name="{label}">{''.join(f'<option{" selected" if i == v else ""}>{i}</option>' for i in range(0, mx + 1))}</select></div>"""
    site_cfg = {"lang": lang, "fcLocale": FC_LOCALE[lang], "numLocale": NUM_LOCALE[lang], "gaId": GA_ID,
                "prices": PRICES, "t": t["t"], "hints": {l: HINTS[l] for l in LANGS if l != lang}}
    maps_embed = f"https://maps.google.com/maps?q=Sen%C4%8Dna+ulica+8,+6310+Izola&z=16&hl={lang}&output=embed"
    year = date.today().year
    return f"""
<body>
{nav(lang, t)}

<header class="hero">
  <img class="hero-img" src="/img/balkon.webp" srcset="/img/balkon-sm.webp 720w, /img/balkon.webp 1448w" sizes="100vw"
       alt="{t['c_balcony']}" fetchpriority="high" width="1448" height="1086">
  <div class="container">
    <h1>{t['h1']}</h1>
    <p class="hero-sub">{t['sub']}</p>
    <div class="d-flex flex-wrap gap-2">
      <a class="btn btn-navy btn-lg" href="#booking"><i class="bi bi-calendar3 me-2"></i>{t['check']}</a>
      <a class="btn btn-outline-light-pill btn-lg" href="{wa}" target="_blank" rel="noopener"><i class="bi bi-whatsapp me-2"></i>{t['wa']}</a>
    </div>
  </div>
</header>

<div class="highlights">
  <div class="container"><div class="row g-3">{hl}
  </div></div>
</div>

<main>
<section id="photos">
  <div class="container">
    <p class="eyebrow">{t['ph_eyebrow']}</p>
    <h2>{t['ph_h2']}</h2>
    <p class="lead-muted mb-4">{t['ph_lead']}</p>
    <div class="gallery">{gallery}
    </div>
  </div>
</section>

<div class="cta-band">
  <div class="container d-flex flex-wrap justify-content-between align-items-center gap-3">
    <div><h2 class="mb-1">{t['band_h2']}</h2><p>{t['band_p']}</p></div>
    <a class="btn btn-sand btn-lg" href="#booking"><i class="bi bi-calendar3 me-2"></i>{t['check']}</a>
  </div>
</div>

<section id="apartment">
  <div class="container">
    <p class="eyebrow">{t['apt_eyebrow']}</p>
    <h2>{t['apt_h2']}</h2>
    <p class="lead-muted mb-4">{t['apt_lead']}</p>
    <div class="row g-4">
      <div class="col-lg-7"><div class="row g-3">{rooms}
      </div></div>
      <div class="col-lg-5"><div class="room">
        <h3 class="mt-0 mb-3">{t['am_h3']}</h3><ul class="amenities">{amen}</ul></div></div>
    </div>
    <div class="room mt-4"><h3 class="mt-0 mb-2">{ARRIVAL[lang][0]}</h3><ul class="rules rules-2">{arrival}</ul></div>
  </div>
</section>

<section id="prices" class="pt-0">
  <div class="container">
    <p class="eyebrow">{t['pr_eyebrow']}</p>
    <h2>{t['pr_h2']}</h2>
    <p class="lead-muted mb-4">{t['pr_lead']}</p>
    <div class="row g-4">
      <div class="col-lg-5"><div class="price-table">{seasons}
      </div>
      <a class="btn btn-navy w-100 mt-3" href="#booking">{t['check']}</a></div>
      <div class="col-lg-7"><div class="room"><h3 class="mt-0 mb-2">{t['rules_h3']}</h3><ul class="rules">{rules}</ul></div></div>
    </div>
  </div>
</section>

<section id="booking">
  <div class="container">
    <p class="eyebrow">{t['bk_eyebrow']}</p>
    <h2>{t['bk_h2']}</h2>
    <p class="lead-muted mb-4">{t['bk_lead']}</p>
    <div class="row g-4">
      <div class="col-lg-6"><div class="card-soft">
        <div id="calendar"></div>
        <div class="legend"><span class="free">{t['free']}</span><span class="booked">{t['booked']}</span></div>
      </div></div>
      <div class="col-lg-6"><div class="card-soft">
        <form id="request-form" action="{FORMSPREE}" method="POST">
          <input type="text" name="_gotcha" class="d-none" tabindex="-1" autocomplete="off">
          <input type="hidden" name="_subject" value="{t['subject']}">
          <input type="hidden" name="language" value="{lang}">
          <input type="hidden" name="estimate" id="f-estimate">
          <div class="row g-3">
            <div class="col-6"><label class="form-label" for="f-arrival">{t['f_arr']}</label>
              <input type="date" class="form-control" id="f-arrival" name="arrival" required></div>
            <div class="col-6"><label class="form-label" for="f-departure">{t['f_dep']}</label>
              <input type="date" class="form-control" id="f-departure" name="departure" required></div>
            {num('f-adults', t['f_adults'], 2, 4)}{num('f-kids', t['f_kids'], 0, 3)}{num('f-small', t['f_small'], 0, 3)}
            <div class="col-12"><div class="estimate" id="estimate" aria-live="polite"></div></div>
            <div class="col-sm-6"><label class="form-label" for="f-name">{t['f_name']}</label>
              <input type="text" class="form-control" id="f-name" name="name" autocomplete="name" required></div>
            <div class="col-sm-6"><label class="form-label" for="f-email">{t['f_email']}</label>
              <input type="email" class="form-control" id="f-email" name="email" autocomplete="email" required></div>
            <div class="col-12"><label class="form-label" for="f-phone">{t['f_phone']}</label>
              <input type="tel" class="form-control" id="f-phone" name="phone" autocomplete="tel"></div>
            <div class="col-12"><label class="form-label" for="f-msg">{t['f_msg']}</label>
              <textarea class="form-control" id="f-msg" name="message" rows="3"></textarea></div>
            <div class="col-12"><button type="submit" class="btn btn-navy w-100 py-3">{t['f_send']}</button>
              <div id="form-status" class="form-status" role="status"></div></div>
          </div>
        </form>
      </div></div>
    </div>
  </div>
</section>

<section id="location">
  <div class="container">
    <p class="eyebrow">{t['loc_eyebrow']}</p>
    <h2>{t['loc_h2']}</h2>
    <p class="lead-muted mb-4">{t['loc_lead']}</p>
    <div class="row g-4">
      <div class="col-lg-4">
        <p class="mb-2"><i class="bi bi-geo-alt me-2"></i>{ADDRESS}, Slovenija</p>
        <ul class="dist mb-3">{dist}</ul>
        <a class="btn btn-sand" href="{MAPS_LINK}" target="_blank" rel="noopener"><i class="bi bi-sign-turn-right me-2"></i>{t['directions']}</a>
      </div>
      <div class="col-lg-8"><div class="map-wrap">
        <iframe src="{maps_embed}" title="{t['loc_h2']}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      </div></div>
    </div>
  </div>
</section>
</main>

<section id="contact">
  <div class="container">
    <p class="eyebrow">{t['ct_eyebrow']}</p>
    <h2>{t['ct_h2']}</h2>
    <p class="mb-4" style="opacity:.8">{t['ct_lead']}</p>
    <div class="row g-3">
      <div class="col-sm-6 col-lg-3"><a class="contact-tile" href="{wa}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i><div>WhatsApp<small>{t['ct_wa']}</small></div></a></div>
      <div class="col-sm-6 col-lg-3"><a class="contact-tile" href="tel:{PHONE}"><i class="bi bi-telephone"></i><div>{PHONE_SHOW}<small>{t['ct_phone']}</small></div></a></div>
      <div class="col-sm-6 col-lg-3"><a class="contact-tile" href="mailto:{EMAIL}"><i class="bi bi-envelope"></i><div>{EMAIL}<small>{t['ct_mail']}</small></div></a></div>
      <div class="col-sm-6 col-lg-3"><a class="contact-tile" href="{MAPS_LINK}" target="_blank" rel="noopener"><i class="bi bi-geo-alt"></i><div>Senčna ulica 8, Izola<small>{t['directions']}</small></div></a></div>
    </div>
  </div>
</section>

<footer>
  <div class="container d-flex flex-wrap justify-content-between gap-2">
    <span>© {year} Apartma Štimec · {ADDRESS}</span>
    <span><a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook"><i class="bi bi-facebook me-3"></i></a><a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram"><i class="bi bi-instagram"></i></a></span>
  </div>
</footer>

<div class="mobile-bar">
  <a class="mb-wa" href="{wa}" target="_blank" rel="noopener"><i class="bi bi-whatsapp me-1"></i>WhatsApp</a>
  <a class="mb-call" href="tel:{PHONE}" aria-label="{t['ct_phone']}"><i class="bi bi-telephone"></i></a>
  <a class="mb-book" href="#booking"><i class="bi bi-calendar3 me-1"></i>{t['mb_book']}</a>
</div>

<div class="lightbox" id="lightbox" role="dialog" aria-modal="true">
  <button type="button" class="lb-close" aria-label="{t['lb_close']}"><i class="bi bi-x-lg"></i></button>
  <button type="button" class="lb-prev" aria-label="{t['lb_prev']}"><i class="bi bi-chevron-left"></i></button>
  <img alt="">
  <div class="lb-cap"></div>
  <button type="button" class="lb-next" aria-label="{t['lb_next']}"><i class="bi bi-chevron-right"></i></button>
</div>

<div id="cookie-banner" role="dialog" aria-live="polite">
  <p>{t['cookie']}</p>
  <button type="button" class="btn btn-navy btn-sm cb-yes">{t['cookie_yes']}</button>
  <button type="button" class="btn btn-sand btn-sm cb-no">{t['cookie_no']}</button>
</div>

<script>window.SITE = {json.dumps(site_cfg, ensure_ascii=False)};</script>
<script defer src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script defer src="/assets/site.js"></script>
</body>
</html>
"""


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", path)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    for lang in LANGS:
        t = TEXT[lang]
        out = os.path.join(root, "index.html" if PATH[lang] == "/" else lang + "/index.html")
        write(out, head(lang, t) + body(lang, t))

    # old gallery page -> photos section
    write(os.path.join(root, "gallery.html"), f"""<!DOCTYPE html>
<html lang="sl"><head><meta charset="UTF-8"><title>Apartma Štimec</title>
<link rel="canonical" href="{SITE}/"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=/#photos"></head>
<body><a href="/#photos">Apartma Štimec</a></body></html>
""")

    today = date.today().isoformat()
    urls = []
    for lang in LANGS:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{PATH[l]}"/>' for l in LANGS)
        urls.append(f"  <url>\n    <loc>{SITE}{PATH[lang]}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>")
    write(os.path.join(root, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write(os.path.join(root, "robots.txt"), f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
