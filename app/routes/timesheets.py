# app/routes/timesheets.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.timesheet import Timesheet
from app.models.file import File
from app.utils.pdf_generator import generate_fortuna_timesheet
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import os
import uuid
import json  # Für die Verarbeitung von JSON-String-Daten

timesheets = Blueprint('timesheets', __name__)

ACTIVITY_CHOICES = [
    ('abnahme', 'Abnahme/Übergabe'),
    ('abzweigdosen', 'Abzweigdosen setzen und verdrahten'),
    ('angebotserstellung', 'Angebotserstellung'),
    ('andere', 'Andere Tätigkeit'),
    ('antennentechnik', 'Antennentechnik installieren'),
    ('app_konfiguration', 'Smart Home App konfigurieren'),
    ('aufmass', 'Aufmaß erstellen'),
    ('aussenbeleuchtung', 'Außenbeleuchtung installieren'),
    ('baustelleneinrichtung', 'Baustelleneinrichtung'),
    ('bauabnahme', 'Bauabnahme elektrischer Anlagen'),
    ('benetzungspruefung', 'Benetzungsprüfung durchführen'),
    ('beratung', 'Kundenberatung'),
    ('bewegungsmelder', 'Bewegungsmelder installieren'),
    ('bma_wartung', 'BMA-Wartung und -Prüfung'),
    ('bluetooth', 'Bluetooth-Geräte einbinden'),
    ('blockheizkraftwerk', 'BHKW elektrisch anschließen'),
    ('brandmeldeanlagen', 'Brandmeldeanlagen installieren/warten'),
    ('cloud_anbindung', 'Cloud-Anbindung einrichten'),
    ('datenauswertung', 'Messdaten auswerten/dokumentieren'),
    ('dali_installation', 'DALI-Installation'),
    ('dali_programmierung', 'DALI-Programmierung'),
    ('dekorationsbeleuchtung', 'Dekorationsbeleuchtung installieren'),
    ('dimmer', 'Dimmer installieren'),
    ('dmx_steuerung', 'DMX-Steuerung einrichten'),
    ('dokumentation', 'Elektrodokumentation erstellen'),
    ('effektbeleuchtung', 'Effektbeleuchtung installieren'),
    ('einbruchschutz', 'Einbruchschutzsysteme installieren'),
    ('einweisung', 'Einweisung Kunden'),
    ('elektrpruefung', 'Elektrische Prüfungen durchführen'),
    ('energiemonitoring', 'Energiemonitoringsystem installieren'),
    ('erdung', 'Erdung/Potentialausgleich installieren'),
    ('fehlersuche', 'Fehlersuche / Reparatur'),
    ('fi_schalter', 'FI-Schalter installieren'),
    ('fotodokumentation', 'Fotodokumentation erstellen'),
    ('gartenbeleuchtung', 'Gartenbeleuchtung installieren'),
    ('glasfaser', 'Glasfaserverkabelung'),
    ('hauptschalter', 'Hauptschalter installieren'),
    ('hausanschluss', 'Hausanschluss herstellen'),
    ('heizungssteuerung', 'Heizungssteuerung installieren'),
    ('hutschiene', 'Hutschienen-Komponenten montieren'),
    ('instandsetzung', 'Instandsetzungsarbeiten'),
    ('industriebeleuchtung', 'Industriebeleuchtung installieren'),
    ('isolationsmessung', 'Isolationsmessung durchführen'),
    ('kabel', 'Kabel verlegen'),
    ('kabeltrassen', 'Kabeltrassen montieren'),
    ('kabelverlegung_erdreich', 'Kabelverlegung im Erdreich'),
    ('klimaanlage', 'Klimaanlage elektrisch anschließen'),
    ('kontaktpflege', 'Kontaktpflege und -überprüfung'),
    ('kurzschlussstrom', 'Kurzschlussstrom messen'),
    ('kücheninstallation', 'Kücheninstallation'),
    ('lan_dose', 'LAN-Dosen installieren'),
    ('lastmanagement', 'Lastmanagementsystem einrichten'),
    ('leitungsschutz', 'Leitungsschutzschalter montieren'),
    ('led_umruestung', 'LED-Umrüstung'),
    ('leerrohre', 'Leerrohre verlegen'),
    ('leuchten', 'Leuchten installieren'),
    ('lichtdesign', 'Lichtdesign umsetzen'),
    ('lichtplanung', 'Lichtplanung'),
    ('lichtsteuerung', 'Lichtsteuerungssysteme installieren'),
    ('lampenwechsel', 'Lampenwechsel'),
    ('materialbeschaffung', 'Materialbeschaffung'),
    ('messdaten', 'Messdaten auswerten/dokumentieren'),
    ('multimedia', 'Multimedia-Anschlüsse installieren'),
    ('netzanschluss', 'Netzanschluss herstellen'),
    ('netzwerkverkabelung', 'Netzwerkverkabelung installieren'),
    ('netzwerkschrank', 'Netzwerkschrank installieren/strukturieren'),
    ('neonbeleuchtung', 'Neonbeleuchtung installieren'),
    ('notbeleuchtung', 'Notbeleuchtung installieren'),
    ('notstromsysteme', 'Notstromsysteme installieren/warten'),
    ('patchpanel', 'Patchpanel verdrahten'),
    ('pendelleuchten', 'Pendelleuchten montieren'),
    ('photovoltaikanlage', 'Photovoltaikanlage anschließen'),
    ('planzeichnung', 'Elektropläne zeichnen'),
    ('poe', 'PoE-Komponenten installieren'),
    ('pool_technik', 'Pool-Technik elektrisch anschließen'),
    ('projektleitung', 'Projektleitung'),
    ('rauchmelder', 'Rauchmelder installieren/warten'),
    ('reinigung', 'Reinigung elektrischer Anlagen'),
    ('revision', 'Revision elektrischer Anlagen'),
    ('revision_plaene', 'Revisionspläne erstellen'),
    ('rolladensteuerung', 'Rolladensteuerung installieren'),
    ('router_setup', 'Router einrichten'),
    ('sauna_elektro', 'Sauna-Elektrik installieren'),
    ('sat_anlagen', 'SAT-Anlagen installieren'),
    ('schaltschrankbau', 'Schaltschrankbau'),
    ('schalter', 'Schalter installieren'),
    ('schleifenimpedanz', 'Schleifenimpedanz messen'),
    ('schmelzsicherungen', 'Schmelzsicherungen einbauen'),
    ('schulung', 'Schulung durchführen'),
    ('sichtpruefung', 'Sichtprüfung durchführen'),
    ('smartmeter', 'Smart Meter installieren'),
    ('smarthome_einrichtung', 'Smart Home Einrichtung/Konfiguration'),
    ('smarthome_fehlersuche', 'Smart Home Fehlersuche und -behebung'),
    ('smarthome_installation', 'Smart Home Installation'),
    ('smarthome_planung', 'Smart Home Planung/Beratung'),
    ('smarthome_wartung', 'Smart Home Wartung'),
    ('spannungspruefung', 'Spannungsprüfung durchführen'),
    ('speichersystem', 'Energiespeichersystem installieren'),
    ('sprachsteuerung', 'Sprachsteuerung einrichten'),
    ('steckdosen', 'Steckdosen installieren'),
    ('stromerzeugung', 'Stromerzeugungsanlage anschließen'),
    ('stromschienen', 'Stromschienen montieren'),
    ('stromzaehler', 'Stromzähler installieren/wechseln'),
    ('telefonanlagen', 'Telefonanlagen installieren'),
    ('terrassen_elektro', 'Terrassenelektrik installieren'),
    ('thermografie', 'Thermografische Untersuchung'),
    ('touchpanel', 'Touch-Panel installieren/konfigurieren'),
    ('transport', 'Transport/Logistik'),
    ('trockenbau_elektro', 'Elektroinstallation im Trockenbau'),
    ('tuersprechanlagen', 'Türsprechanlagen installieren/warten'),
    ('uberwachung', 'Überwachungssysteme installieren'),
    ('unterverteilung', 'Unterverteilung installieren'),
    ('usb_dosen', 'USB-Ladedosen installieren'),
    ('verteilerschrank', 'Verteilerschrank montieren/verdrahten'),
    ('videoanlagen', 'Videoanlagen installieren/warten'),
    ('waende', 'Wände fräsen'),
    ('waermepumpe', 'Wärmepumpe elektrisch anschließen'),
    ('wallbox', 'Wallbox/Ladestation installieren'),
    ('wartung_allgemein', 'Allgemeine Wartungsarbeiten'),
    ('wiederstandsmessung', 'Widerstandsmessung durchführen'),
    ('zigbee', 'Zigbee-Komponenten installieren'),
    ('zeitschaltuhren', 'Zeitschaltuhren einbauen'),
    ('zwave', 'Z-Wave-Komponenten installieren')
]

# Sortieren nach der Beschreibung (zweites Element jedes Tupels)
sorted_choices = sorted(ACTIVITY_CHOICES, key=lambda x: x[1].lower())

MATERIAL_CHOICES = [
    # Kabel und Leitungen
    ('nymj_3x1_5', 'NYM-J 3x1,5 mm²'),
    ('nymj_3x2_5', 'NYM-J 3x2,5 mm²'),
    ('nymj_5x1_5', 'NYM-J 5x1,5 mm²'),
    ('nymj_5x2_5', 'NYM-J 5x2,5 mm²'),
    ('nymj_5x4', 'NYM-J 5x4 mm²'),
    ('nymj_5x6', 'NYM-J 5x6 mm²'),
    ('nymj_5x10', 'NYM-J 5x10 mm²'),
    ('nyy_5x16', 'NYY 5x16 mm²'),
    ('nyy_5x25', 'NYY 5x25 mm²'),
    ('nyy_5x35', 'NYY 5x35 mm²'),
    ('hdi_1x6', 'H07V-K 1x6 mm²'),
    ('hdi_1x10', 'H07V-K 1x10 mm²'),
    ('hdi_1x16', 'H07V-K 1x16 mm²'),
    ('hdi_1x25', 'H07V-K 1x25 mm²'),
    ('ydy_2x1', 'YDY 2x1 mm²'),
    ('netzwerkkabel_cat5e', 'Netzwerkkabel Cat 5e'),
    ('netzwerkkabel_cat6', 'Netzwerkkabel Cat 6'),
    ('netzwerkkabel_cat7', 'Netzwerkkabel Cat 7'),
    ('netzwerkkabel_cat8', 'Netzwerkkabel Cat 8'),
    ('koaxialkabel', 'Koaxialkabel'),
    ('glasfaserkabel', 'Glasfaserkabel'),
    ('telefonkabel', 'Telefonkabel J-Y(St)Y'),
    ('klingeldraht', 'Klingeldraht'),
    ('erdungskabel', 'Erdungskabel'),
    ('schweissleitungen', 'Schweißleitungen'),
    ('steuerleitungen', 'Steuerleitungen'),
    ('brandmeldekabel', 'Brandmeldekabel'),
    ('lautsprecherkabel', 'Lautsprecherkabel'),
    ('solarkabel', 'Solarkabel'),
    ('ysty', 'Y(St)Y Kabel'),
    ('datenkabel', 'Datenkabel'),
    
    # Leerrohre und Kabelkanäle
    ('leerrohr_m16', 'Leerrohr M16'),
    ('leerrohr_m20', 'Leerrohr M20'),
    ('leerrohr_m25', 'Leerrohr M25'),
    ('leerrohr_m32', 'Leerrohr M32'),
    ('leerrohr_m40', 'Leerrohr M40'),
    ('leerrohr_m50', 'Leerrohr M50'),
    ('leerrohr_m63', 'Leerrohr M63'),
    ('kabelkanal_15x15', 'Kabelkanal 15x15 mm'),
    ('kabelkanal_30x30', 'Kabelkanal 30x30 mm'),
    ('kabelkanal_40x40', 'Kabelkanal 40x40 mm'),
    ('kabelkanal_60x40', 'Kabelkanal 60x40 mm'),
    ('kabelkanal_60x60', 'Kabelkanal 60x60 mm'),
    ('kabelkanal_80x60', 'Kabelkanal 80x60 mm'),
    ('kabeltrasse_50', 'Kabeltrasse 50 mm'),
    ('kabeltrasse_100', 'Kabeltrasse 100 mm'),
    ('kabeltrasse_200', 'Kabeltrasse 200 mm'),
    ('kabeltrasse_300', 'Kabeltrasse 300 mm'),
    ('wellrohr', 'Wellrohr'),
    ('spiralschlauch', 'Spiralschlauch'),
    ('erdungskasten', 'Erdungskasten'),
    
    # Schalter und Steckdosen
    ('steckdose_einfach', 'Steckdose einfach'),
    ('steckdose_zweifach', 'Steckdose zweifach'),
    ('steckdose_dreifach', 'Steckdose dreifach'),
    ('schuko_ap', 'Schuko-Steckdose AP'),
    ('schuko_up', 'Schuko-Steckdose UP'),
    ('schuko_feuchtraum', 'Schuko-Steckdose Feuchtraum'),
    ('schuko_aussenbereick', 'Schuko-Steckdose Außenbereich'),
    ('schuko_mit_usb', 'Schuko-Steckdose mit USB'),
    ('cee_steckdose_16a', 'CEE-Steckdose 16A'),
    ('cee_steckdose_32a', 'CEE-Steckdose 32A'),
    ('cee_steckdose_63a', 'CEE-Steckdose 63A'),
    ('ausschalter_einfach', 'Ausschalter einfach'),
    ('ausschalter_zweifach', 'Ausschalter zweifach'),
    ('ausschalter_dreifach', 'Ausschalter dreifach'),
    ('wechselschalter', 'Wechselschalter'),
    ('kreuzschalter', 'Kreuzschalter'),
    ('serienschalter', 'Serienschalter'),
    ('taster', 'Taster'),
    ('dimmer', 'Dimmer'),
    ('jalousie_schalter', 'Jalousie-Schalter'),
    ('bewegungsmelder_innen', 'Bewegungsmelder Innen'),
    ('bewegungsmelder_aussen', 'Bewegungsmelder Außen'),
    ('netzwerkdose', 'Netzwerkdose'),
    ('antennendose', 'Antennendose'),
    ('telefonanschluss', 'Telefonanschluss'),
    ('lan_dosen', 'LAN-Dosen'),
    
    # Unterputzdosen und Abzweigdosen
    ('up_dose_klein', 'Unterputzdose Klein'),
    ('up_dose_tief', 'Unterputzdose Tief'),
    ('up_dose_dreifach', 'Unterputzdose Dreifach'),
    ('ap_abzweigdose', 'Aufputz-Abzweigdose'),
    ('abzweigdose_feuchtraum', 'Abzweigdose Feuchtraum'),
    ('unterputz_abzweigdose', 'Unterputz-Abzweigdose'),
    ('hohlwanddose', 'Hohlwanddose'),
    ('gerätedose', 'Gerätedose'),
    ('verbindungsdose', 'Verbindungsdose'),
    ('betoneinbaudose', 'Betoneinbaudose'),
    
    # Beleuchtung
    ('led_panel', 'LED-Panel'),
    ('led_deckenleuchte', 'LED-Deckenleuchte'),
    ('led_einbaustrahler', 'LED-Einbaustrahler'),
    ('led_aussenleuchte', 'LED-Außenleuchte'),
    ('led_streifen', 'LED-Streifen'),
    ('led_trafo', 'LED-Trafo'),
    ('neonroehre', 'Neonröhre'),
    ('leuchtmittel_e27', 'Leuchtmittel E27'),
    ('leuchtmittel_e14', 'Leuchtmittel E14'),
    ('leuchtmittel_gu10', 'Leuchtmittel GU10'),
    ('leuchtmittel_gu5_3', 'Leuchtmittel GU5.3'),
    ('fassung_e27', 'Fassung E27'),
    ('fassung_e14', 'Fassung E14'),
    ('fassung_gu10', 'Fassung GU10'),
    ('pendelleuchte', 'Pendelleuchte'),
    ('wandleuchte', 'Wandleuchte'),
    ('led_strahler', 'LED-Strahler'),
    ('notbeleuchtung', 'Notbeleuchtung'),
    ('dali_konverter', 'DALI-Konverter'),
    ('dmx_steuerung', 'DMX-Steuerung'),
    ('lichtschiene', 'Lichtschiene'),
    
    # Verteilerbau
    ('sicherungsautomat_b16', 'Sicherungsautomat B16'),
    ('sicherungsautomat_b20', 'Sicherungsautomat B20'),
    ('sicherungsautomat_b25', 'Sicherungsautomat B25'),
    ('sicherungsautomat_b32', 'Sicherungsautomat B32'),
    ('fi_schalter_25a', 'FI-Schalter 25A'),
    ('fi_schalter_40a', 'FI-Schalter 40A'),
    ('fi_schalter_63a', 'FI-Schalter 63A'),
    ('fls_schalter_b16', 'FI/LS-Schalter B16'),
    ('fls_schalter_b20', 'FI/LS-Schalter B20'),
    ('hauptschalter', 'Hauptschalter'),
    ('schmelzsicherung', 'Schmelzsicherung'),
    ('verteilerschrank_klein', 'Verteilerschrank klein'),
    ('verteilerschrank_mittel', 'Verteilerschrank mittel'),
    ('verteilerschrank_gross', 'Verteilerschrank groß'),
    ('zaehlerschrank', 'Zählerschrank'),
    ('reihenklemmen', 'Reihenklemmen'),
    ('diodenklemmen', 'Diodenklemmen'),
    ('hutschiene', 'Hutschiene'),
    ('sammelschienenhalter', 'Sammelschienenhalter'),
    ('sammelschienenabdeckung', 'Sammelschienenabdeckung'),
    ('drehstromzaehler', 'Drehstromzähler'),
    ('wechselstromzaehler', 'Wechselstromzähler'),
    ('smartmeter', 'Smart Meter'),
    ('messgeraet', 'Messgerät'),
    ('überspannungsschutz', 'Überspannungsschutz'),
    ('stromstossschalter', 'Stromstoßschalter'),
    ('zeitschaltuhr', 'Zeitschaltuhr'),
    ('dimmerschalter', 'Dimmerschalter'),
    ('schütz', 'Schütz'),
    ('relais', 'Relais'),
    ('sicherungslasttrenner', 'Sicherungslasttrenner'),
    
    # Verbindungsmaterial
    ('aderendhülsen', 'Aderendhülsen'),
    ('wagoklemmen', 'Wagoklemmen'),
    ('lustklemmen', 'Lustklemmen'),
    ('erdungsklemmen', 'Erdungsklemmen'),
    ('verteilerklemmen', 'Verteilerklemmen'),
    ('kabelbinder_klein', 'Kabelbinder klein'),
    ('kabelbinder_mittel', 'Kabelbinder mittel'),
    ('kabelbinder_gross', 'Kabelbinder groß'),
    ('kabelschellen', 'Kabelschellen'),
    ('isolierband', 'Isolierband'),
    ('schrumpfschlauch', 'Schrumpfschlauch'),
    ('schutzkontaktstecker', 'Schutzkontaktstecker'),
    ('cee_stecker', 'CEE-Stecker'),
    ('verbindungsmuffen', 'Verbindungsmuffen'),
    ('rj45_stecker', 'RJ45-Stecker'),
    ('kabelschuhe', 'Kabelschuhe'),
    ('quetschverbinder', 'Quetschverbinder'),
    ('gießharz', 'Gießharz'),
    ('kupferlitze', 'Kupferlitze'),
    ('kabelmarkierer', 'Kabelmarkierer'),
    
    # Smart Home
    ('knx_aktor', 'KNX-Aktor'),
    ('knx_sensor', 'KNX-Sensor'),
    ('knx_netzteil', 'KNX-Netzteil'),
    ('knx_linienkoppler', 'KNX-Linienkoppler'),
    ('knx_ip_schnittstelle', 'KNX-IP-Schnittstelle'),
    ('knx_temperatursensor', 'KNX-Temperatursensor'),
    ('knx_präsenzmelder', 'KNX-Präsenzmelder'),
    ('smarthome_steckdose', 'Smart Home Steckdose'),
    ('smarthome_schalter', 'Smart Home Schalter'),
    ('smarthome_gateway', 'Smart Home Gateway'),
    ('smarthome_zentrale', 'Smart Home Zentrale'),
    ('smarthome_thermostat', 'Smart Home Thermostat'),
    ('smarthome_rauchmelder', 'Smart Home Rauchmelder'),
    ('smarthome_bewegungsmelder', 'Smart Home Bewegungsmelder'),
    ('smarthome_tuersensor', 'Smart Home Türsensor'),
    ('smarthome_fenstersensor', 'Smart Home Fenstersensor'),
    ('dali_gateway', 'DALI-Gateway'),
    ('dali_sensor', 'DALI-Sensor'),
    ('homematic_aktor', 'HomeMatic Aktor'),
    ('homematic_sensor', 'HomeMatic Sensor'),
    ('philips_hue_bridge', 'Philips Hue Bridge'),
    ('zigbee_gateway', 'ZigBee Gateway'),
    ('z_wave_gateway', 'Z-Wave Gateway'),
    ('wlan_steckdose', 'WLAN-Steckdose'),
    ('bluetooth_dimmer', 'Bluetooth Dimmer'),
    ('touchpanel', 'Touchpanel'),
    ('sprachassistent', 'Sprachassistent'),
    
    # Netzwerk/Kommunikation
    ('router', 'Router'),
    ('wlan_accesspoint', 'WLAN Access Point'),
    ('netzwerkswitch', 'Netzwerk-Switch'),
    ('patchpanel', 'Patchpanel'),
    ('patchkabel', 'Patchkabel'),
    ('netzwerkdose_aufputz', 'Netzwerkdose Aufputz'),
    ('netzwerkdose_unterputz', 'Netzwerkdose Unterputz'),
    ('antennenanschluss', 'Antennenanschluss'),
    ('multimediadose', 'Multimediadose'),
    ('sat_verteiler', 'SAT-Verteiler'),
    ('antennenkabel', 'Antennenkabel'),
    ('telefonverteiler', 'Telefonverteiler'),
    ('glasfaser_anschluss', 'Glasfaser-Anschluss'),
    ('lsa_leiste', 'LSA-Leiste'),
    ('auflegwerkzeug', 'Auflegwerkzeug'),
    ('netzwerkverbinder', 'Netzwerkverbinder'),
    ('server_rack', 'Server-Rack'),
    
    # Sicherheits- und Brandschutztechnik
    ('rauchmelder', 'Rauchmelder'),
    ('brandmelder', 'Brandmelder'),
    ('hitzemelder', 'Hitzemelder'),
    ('brandmeldezentrale', 'Brandmeldezentrale'),
    ('alarmgeber', 'Alarmgeber'),
    ('blitzleuchte', 'Blitzleuchte'),
    ('handmelder', 'Handmelder'),
    ('sirene', 'Sirene'),
    ('ueberwachungskamera', 'Überwachungskamera'),
    ('gegensprechanlage', 'Gegensprechanlage'),
    ('tueroeffner', 'Türöffner'),
    ('schliessanlage', 'Schließanlage'),
    ('zugangskontrolle', 'Zugangskontrolle'),
    ('kartenleser', 'Kartenleser'),
    ('fingerscanner', 'Fingerscanner'),
    ('bewegungsmelder_sicherheit', 'Bewegungsmelder (Sicherheit)'),
    ('glasbruchmelder', 'Glasbruchmelder'),
    ('funk_alarmsystem', 'Funk-Alarmsystem'),
    
    # Energiemanagement
    ('pv_modul', 'PV-Modul'),
    ('wechselrichter', 'Wechselrichter'),
    ('energiespeicher', 'Energiespeicher'),
    ('batteriesystem', 'Batteriesystem'),
    ('stromverteiler', 'Stromverteiler'),
    ('lastabwurfrelais', 'Lastabwurfrelais'),
    ('energiemessgeraet', 'Energiemessgerät'),
    ('lastmanagement', 'Lastmanagement'),
    ('schaltschrank_solar', 'Schaltschrank Solar'),
    ('acdc_wandler', 'AC/DC-Wandler'),
    ('freigabeschalter', 'Freigabeschalter'),
    ('wallbox_11kw', 'Wallbox 11kW'),
    ('wallbox_22kw', 'Wallbox 22kW'),
    ('ladekabel_typ2', 'Ladekabel Typ 2'),
    ('notstromversorgung', 'Notstromversorgung'),
    
    # Befestigungsmaterial
    ('dübel', 'Dübel'),
    ('schrauben', 'Schrauben'),
    ('spreizdübel', 'Spreizdübel'),
    ('hohlraumdübel', 'Hohlraumdübel'),
    ('schlagdübel', 'Schlagdübel'),
    ('montagekleber', 'Montagekleber'),
    ('befestigungsschellen', 'Befestigungsschellen'),
    ('naegel', 'Nägel'),
    ('klebeband', 'Klebeband'),
    ('kabelschellen_nagel', 'Kabelschellen mit Nagel'),
    ('montageband', 'Montageband'),
    ('montageplatte', 'Montageplatte'),
    ('anker', 'Anker'),
    ('gewindestange', 'Gewindestange'),
    
    # Werkzeug (falls auch im Material gelistet)
    ('kabelmesser', 'Kabelmesser'),
    ('abisolierzange', 'Abisolierzange'),
    ('crimpzange', 'Crimpzange'),
    ('seitenschneider', 'Seitenschneider'),
    ('spannungspruefer', 'Spannungsprüfer'),
    ('multimeter', 'Multimeter'),
    ('duspol', 'Duspol'),
    ('leitungsfinder', 'Leitungsfinder'),
    ('kartuschenpistole', 'Kartuschenpistole'),
    ('bohrmaschine', 'Bohrmaschine'),
    ('stemmhammer', 'Stemmhammer'),
    ('stechbeitel', 'Stechbeitel'),
    ('schraubendreher', 'Schraubendreher'),
    ('lsa_werkzeug', 'LSA-Werkzeug'),
    ('kabeltrommel', 'Kabeltrommel'),
    ('laserentfernungsmesser', 'Laserentfernungsmesser'),
    
    # Sonstiges
    ('andere_materialien', 'Andere Materialien')
]
# Sort the MATERIAL_CHOICES alphabetically by the second element (description)
sorted_material_choices = sorted(MATERIAL_CHOICES, key=lambda x: x[1].lower())

sorted_material_choices[:10]  # show first 10 entries as a preview

class TimesheetForm(FlaskForm):
    activity = SelectField('Tätigkeit', choices=ACTIVITY_CHOICES, validators=[DataRequired()])
    other_activity = StringField('Andere Tätigkeit (bitte angeben)')
    hours = FloatField('Stunden', validators=[DataRequired(), NumberRange(min=0.25, max=24)])
    date = DateField('Datum', format='%Y-%m-%d', validators=[DataRequired()])
    notes = TextAreaField('Notizen')
    submit = SubmitField('PDF erstellen und speichern')

@timesheets.route('/project/<int:project_id>/timesheet/new', methods=['GET', 'POST'])
@login_required
def new_timesheet(project_id):
    project = Project.query.get_or_404(project_id)
    form = TimesheetForm()

    if not form.date.data:
        form.date.data = datetime.utcnow().date()

    if form.validate_on_submit():
        try:
            date = form.date.data
            hours = form.hours.data
            notes = form.notes.data
            
            arbeitseinsatz_string = request.form.get('arbeitseinsatz_data', '[]')
            material_string = request.form.get('material_data', '[]')
            
            try:
                arbeitseinsatz_data = json.loads(arbeitseinsatz_string)
                # Überprüfen, ob arbeitseinsatz_data leer ist und erstelle mindestens einen Eintrag
                if not arbeitseinsatz_data:
                    arbeitseinsatz_data = [{'activity': '', 'von': '08:00', 'bis': '17:00', 'std': str(hours)}]
            except json.JSONDecodeError:
                arbeitseinsatz_data = [{'activity': '', 'von': '08:00', 'bis': '17:00', 'std': str(hours)}]
                
            try:
                material_data = json.loads(material_string)
                # Stelle sicher, dass mindestens ein Material-Eintrag vorhanden ist
                if not material_data:
                    material_data = [{'material': '', 'menge': ''}]
            except json.JSONDecodeError:
                material_data = [{'material': '', 'menge': ''}]
                
            an_abreise = request.form.get('an_abreise', '07:45-17:00')  # Standardwert setzen
            arbeitskraft = request.form.get('arbeitskraft', current_user.username)
            
            # Formatieren aller activity-Werte
            for eintrag in arbeitseinsatz_data:
                activity_text = eintrag['activity']
                if activity_text == 'andere' and form.other_activity.data:
                    activity_text = form.other_activity.data.capitalize()
                else:
                    activity_text = dict(ACTIVITY_CHOICES).get(activity_text, activity_text).capitalize()
                eintrag['activity'] = activity_text
                            
            # Aktualisiere die Aktivität im ersten Eintrag der Arbeitszeiten
            if arbeitseinsatz_data and len(arbeitseinsatz_data) > 0:
                arbeitseinsatz_data[0]['activity'] = activity_text

            timesheet = Timesheet(
                date=date,
                activity=activity_text,
                hours=hours,
                notes=notes,
                project_id=project.id,
                user_id=current_user.id
            )

            db.session.add(timesheet)
            db.session.commit()

            pdf_filename = f"stundenbericht_{project.id}_{timesheet.id}_{uuid.uuid4().hex}.pdf"
            pdf_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                f'project_{project.id}',
                'stundenberichte'
            )
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_path = os.path.join(pdf_folder, pdf_filename)

            date_string = date.strftime("%d.%m.%Y")

            # Kopiere das Fortuna-Logo in den statischen Ordner, falls es noch nicht existiert
            logo_source = os.path.join(current_app.root_path, 'static', 'img', 'fortuna-logo.png') 
            logo_destination = os.path.join(current_app.static_folder, 'img')
            
            # Stelle sicher, dass der Zielordner existiert
            os.makedirs(logo_destination, exist_ok=True)
            
            # Nur kopieren, wenn die Datei nicht existiert
            logo_dest_path = os.path.join(logo_destination, 'fortuna-logo.png')
            if not os.path.exists(logo_dest_path) and os.path.exists(logo_source):
                import shutil
                shutil.copy2(logo_source, logo_dest_path)

            generate_fortuna_timesheet(
                pdf_path,
                datum=date_string,
                bauvorhaben=project.name,
                arbeitskraft=arbeitskraft,
                an_abreise=an_abreise,
                arbeitseinsatz=arbeitseinsatz_data,
                material_list=material_data,
                notes=notes
            )

            relative_pdf_path = os.path.join(f'project_{project.id}', 'stundenberichte', pdf_filename)

            timesheet.pdf_path = relative_pdf_path

            pdf_file = File(
                filename=pdf_filename,
                original_filename=f"Stundenbericht_{timesheet.date.strftime('%Y-%m-%d')}.pdf",
                file_type='stundenbericht',
                file_path=relative_pdf_path,
                file_size=os.path.getsize(pdf_path),
                project_id=project.id,
                uploader_id=current_user.id
            )
            db.session.add(pdf_file)
            db.session.commit()

            flash('Stundenbericht wurde erfolgreich erstellt und als PDF gespeichert!', 'success')
            return redirect(url_for('projects.view_project', project_id=project.id))
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Ausführlicheres Logging für Debugging
            db.session.rollback()
            flash(f"Fehler beim Speichern des Stundenberichts: {str(e)}", "danger")
            return redirect(url_for('projects.view_project', project_id=project.id))

    return render_template(
        'timesheets/new_fortuna.html',
        title='Neuer Bau-Tagesbericht',
        form=form,
        project=project,
        activity_choices=ACTIVITY_CHOICES,
        material_choices=MATERIAL_CHOICES
    )