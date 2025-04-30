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
    ('abzweigdose_feuchtraum', 'Abzweigdose Feuchtraum'),
    ('acdc_wandler', 'AC/DC-Wandler'),
    ('aderendhülsen', 'Aderendhülsen'),
    ('abisolierzange', 'Abisolierzange'),
    ('alarmgeber', 'Alarmgeber'),
    ('andere_materialien', 'Andere Materialien'),
    ('anker', 'Anker'),
    ('antennenanschluss', 'Antennenanschluss'),
    ('antennendose', 'Antennendose'),
    ('antennenkabel', 'Antennenkabel'),
    ('ap_abzweigdose', 'Aufputz-Abzweigdose'),
    ('auflegwerkzeug', 'Auflegwerkzeug'),
    ('ausschalter_dreifach', 'Ausschalter dreifach'),
    ('ausschalter_einfach', 'Ausschalter einfach'),
    ('ausschalter_zweifach', 'Ausschalter zweifach'),
    ('batteriesystem', 'Batteriesystem'),
    ('befestigungsschellen', 'Befestigungsschellen'),
    ('betoneinbaudose', 'Betoneinbaudose'),
    ('bewegungsmelder_aussen', 'Bewegungsmelder Außen'),
    ('bewegungsmelder_innen', 'Bewegungsmelder Innen'),
    ('bewegungsmelder_sicherheit', 'Bewegungsmelder (Sicherheit)'),
    ('blitzleuchte', 'Blitzleuchte'),
    ('bluetooth_dimmer', 'Bluetooth Dimmer'),
    ('bohrmaschine', 'Bohrmaschine'),
    ('brandmelder', 'Brandmelder'),
    ('brandmeldekabel', 'Brandmeldekabel'),
    ('brandmeldezentrale', 'Brandmeldezentrale'),
    ('cee_stecker', 'CEE-Stecker'),
    ('cee_steckdose_16a', 'CEE-Steckdose 16A'),
    ('cee_steckdose_32a', 'CEE-Steckdose 32A'),
    ('cee_steckdose_63a', 'CEE-Steckdose 63A'),
    ('crimpzange', 'Crimpzange'),
    ('dali_gateway', 'DALI-Gateway'),
    ('dali_konverter', 'DALI-Konverter'),
    ('dali_sensor', 'DALI-Sensor'),
    ('datenkabel', 'Datenkabel'),
    ('dimmer', 'Dimmer'),
    ('dimmerschalter', 'Dimmerschalter'),
    ('diodenklemmen', 'Diodenklemmen'),
    ('drehstromzaehler', 'Drehstromzähler'),
    ('dmx_steuerung', 'DMX-Steuerung'),
    ('dübel', 'Dübel'),
    ('duspol', 'Duspol'),
    ('energiemessgeraet', 'Energiemessgerät'),
    ('energiespeicher', 'Energiespeicher'),
    ('erdungskabel', 'Erdungskabel'),
    ('erdungskasten', 'Erdungskasten'),
    ('erdungsklemmen', 'Erdungsklemmen'),
    ('fassung_e14', 'Fassung E14'),
    ('fassung_e27', 'Fassung E27'),
    ('fassung_gu10', 'Fassung GU10'),
    ('fi_schalter_25a', 'FI-Schalter 25A'),
    ('fi_schalter_40a', 'FI-Schalter 40A'),
    ('fi_schalter_63a', 'FI-Schalter 63A'),
    ('fingerscanner', 'Fingerscanner'),
    ('fls_schalter_b16', 'FI/LS-Schalter B16'),
    ('fls_schalter_b20', 'FI/LS-Schalter B20'),
    ('freigabeschalter', 'Freigabeschalter'),
    ('funk_alarmsystem', 'Funk-Alarmsystem'),
    ('gegensprechanlage', 'Gegensprechanlage'),
    ('gerätedose', 'Gerätedose'),
    ('gewindestange', 'Gewindestange'),
    ('gießharz', 'Gießharz'),
    ('glasbruchmelder', 'Glasbruchmelder'),
    ('glasfaser_anschluss', 'Glasfaser-Anschluss'),
    ('glasfaserkabel', 'Glasfaserkabel'),
    ('handmelder', 'Handmelder'),
    ('hauptschalter', 'Hauptschalter'),
    ('hdi_1x6', 'H07V-K 1x6 mm²'),
    ('hdi_1x10', 'H07V-K 1x10 mm²'),
    ('hdi_1x16', 'H07V-K 1x16 mm²'),
    ('hdi_1x25', 'H07V-K 1x25 mm²'),
    ('hitzemelder', 'Hitzemelder'),
    ('hohlraumdübel', 'Hohlraumdübel'),
    ('hohlwanddose', 'Hohlwanddose'),
    ('homematic_aktor', 'HomeMatic Aktor'),
    ('homematic_sensor', 'HomeMatic Sensor'),
    ('hutschiene', 'Hutschiene'),
    ('isolierband', 'Isolierband'),
    ('jalousie_schalter', 'Jalousie-Schalter'),
    ('kabelkanal_15x15', 'Kabelkanal 15x15 mm'),
    ('kabelkanal_30x30', 'Kabelkanal 30x30 mm'),
    ('kabelkanal_40x40', 'Kabelkanal 40x40 mm'),
    ('kabelkanal_60x40', 'Kabelkanal 60x40 mm'),
    ('kabelkanal_60x60', 'Kabelkanal 60x60 mm'),
    ('kabelkanal_80x60', 'Kabelkanal 80x60 mm'),
    ('kabelmesser', 'Kabelmesser'),
    ('kabelmarkierer', 'Kabelmarkierer'),
    ('kabelschellen', 'Kabelschellen'),
    ('kabelschellen_nagel', 'Kabelschellen mit Nagel'),
    ('kabelschuhe', 'Kabelschuhe'),
    ('kabeltrommel', 'Kabeltrommel'),
    ('kabeltrasse_50', 'Kabeltrasse 50 mm'),
    ('kabeltrasse_100', 'Kabeltrasse 100 mm'),
    ('kabeltrasse_200', 'Kabeltrasse 200 mm'),
    ('kabeltrasse_300', 'Kabeltrasse 300 mm'),
    ('kabelbinder_gross', 'Kabelbinder groß'),
    ('kabelbinder_klein', 'Kabelbinder klein'),
    ('kabelbinder_mittel', 'Kabelbinder mittel'),
    ('kartenleser', 'Kartenleser'),
    ('kartuschenpistole', 'Kartuschenpistole'),
    ('klebeband', 'Klebeband'),
    ('klingeldraht', 'Klingeldraht'),
    ('knx_aktor', 'KNX-Aktor'),
    ('knx_ip_schnittstelle', 'KNX-IP-Schnittstelle'),
    ('knx_linienkoppler', 'KNX-Linienkoppler'),
    ('knx_netzteil', 'KNX-Netzteil'),
    ('knx_präsenzmelder', 'KNX-Präsenzmelder'),
    ('knx_sensor', 'KNX-Sensor'),
    ('knx_temperatursensor', 'KNX-Temperatursensor'),
    ('koaxialkabel', 'Koaxialkabel'),
    ('kreuzschalter', 'Kreuzschalter'),
    ('kupferlitze', 'Kupferlitze'),
    ('ladekabel_typ2', 'Ladekabel Typ 2'),
    ('lan_dosen', 'LAN-Dosen'),
    ('laserentfernungsmesser', 'Laserentfernungsmesser'),
    ('lastabwurfrelais', 'Lastabwurfrelais'),
    ('lastmanagement', 'Lastmanagement'),
    ('lautsprecherkabel', 'Lautsprecherkabel'),
    ('led_aussenleuchte', 'LED-Außenleuchte'),
    ('led_deckenleuchte', 'LED-Deckenleuchte'),
    ('led_einbaustrahler', 'LED-Einbaustrahler'),
    ('led_panel', 'LED-Panel'),
    ('led_strahler', 'LED-Strahler'),
    ('led_streifen', 'LED-Streifen'),
    ('led_trafo', 'LED-Trafo'),
    ('leerrohr_m16', 'Leerrohr M16'),
    ('leerrohr_m20', 'Leerrohr M20'),
    ('leerrohr_m25', 'Leerrohr M25'),
    ('leerrohr_m32', 'Leerrohr M32'),
    ('leerrohr_m40', 'Leerrohr M40'),
    ('leerrohr_m50', 'Leerrohr M50'),
    ('leerrohr_m63', 'Leerrohr M63'),
    ('leitungsfinder', 'Leitungsfinder'),
    ('leuchtmittel_e14', 'Leuchtmittel E14'),
    ('leuchtmittel_e27', 'Leuchtmittel E27'),
    ('leuchtmittel_gu10', 'Leuchtmittel GU10'),
    ('leuchtmittel_gu5_3', 'Leuchtmittel GU5.3'),
    ('lichtschiene', 'Lichtschiene'),
    ('lsa_leiste', 'LSA-Leiste'),
    ('lsa_werkzeug', 'LSA-Werkzeug'),
    ('lustklemmen', 'Lustklemmen'),
    ('messgeraet', 'Messgerät'),
    ('montageband', 'Montageband'),
    ('montagekleber', 'Montagekleber'),
    ('montageplatte', 'Montageplatte'),
    ('multimeter', 'Multimeter'),
    ('multimediadose', 'Multimediadose'),
    ('naegel', 'Nägel'),
    ('neonroehre', 'Neonröhre'),
    ('netzwerkdose', 'Netzwerkdose'),
    ('netzwerkdose_aufputz', 'Netzwerkdose Aufputz'),
    ('netzwerkdose_unterputz', 'Netzwerkdose Unterputz'),
    ('netzwerkkabel_cat5e', 'Netzwerkkabel Cat 5e'),
    ('netzwerkkabel_cat6', 'Netzwerkkabel Cat 6'),
    ('netzwerkkabel_cat7', 'Netzwerkkabel Cat 7'),
    ('netzwerkkabel_cat8', 'Netzwerkkabel Cat 8'),
    ('netzwerkswitch', 'Netzwerk-Switch'),
    ('netzwerkverbinder', 'Netzwerkverbinder'),
    ('notbeleuchtung', 'Notbeleuchtung'),
    ('notstromversorgung', 'Notstromversorgung'),
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
    ('patchkabel', 'Patchkabel'),
    ('patchpanel', 'Patchpanel'),
    ('pendelleuchte', 'Pendelleuchte'),
    ('philips_hue_bridge', 'Philips Hue Bridge'),
    ('pv_modul', 'PV-Modul'),
    ('quetschverbinder', 'Quetschverbinder'),
    ('rauchmelder', 'Rauchmelder'),
    ('reihenklemmen', 'Reihenklemmen'),
    ('relais', 'Relais'),
    ('rj45_stecker', 'RJ45-Stecker'),
    ('router', 'Router'),
    ('sammelschienenabdeckung', 'Sammelschienenabdeckung'),
    ('sammelschienenhalter', 'Sammelschienenhalter'),
    ('sat_verteiler', 'SAT-Verteiler'),
    ('schaltschrank_solar', 'Schaltschrank Solar'),
    ('schlagdübel', 'Schlagdübel'),
    ('schliessanlage', 'Schließanlage'),
    ('schmelzsicherung', 'Schmelzsicherung'),
    ('schrauben', 'Schrauben'),
    ('schraubendreher', 'Schraubendreher'),
    ('schrumpfschlauch', 'Schrumpfschlauch'),
    ('schuko_ap', 'Schuko-Steckdose AP'),
    ('schuko_aussenbereick', 'Schuko-Steckdose Außenbereich'),
    ('schuko_feuchtraum', 'Schuko-Steckdose Feuchtraum'),
    ('schuko_mit_usb', 'Schuko-Steckdose mit USB'),
    ('schuko_up', 'Schuko-Steckdose UP'),
    ('schutzkontaktstecker', 'Schutzkontaktstecker'),
    ('schütz', 'Schütz'),
    ('schweissleitungen', 'Schweißleitungen'),
    ('seitenschneider', 'Seitenschneider'),
    ('serienschalter', 'Serienschalter'),
    ('server_rack', 'Server-Rack'),
    ('sicherungsautomat_b16', 'Sicherungsautomat B16'),
    ('sicherungsautomat_b20', 'Sicherungsautomat B20'),
    ('sicherungsautomat_b25', 'Sicherungsautomat B25'),
    ('sicherungsautomat_b32', 'Sicherungsautomat B32'),
    ('sicherungslasttrenner', 'Sicherungslasttrenner'),
    ('sirene', 'Sirene'),
    ('smartmeter', 'Smart Meter'),
    ('smarthome_bewegungsmelder', 'Smart Home Bewegungsmelder'),
    ('smarthome_fenstersensor', 'Smart Home Fenstersensor'),
    ('smarthome_gateway', 'Smart Home Gateway'),
    ('smarthome_rauchmelder', 'Smart Home Rauchmelder'),
    ('smarthome_schalter', 'Smart Home Schalter'),
    ('smarthome_steckdose', 'Smart Home Steckdose'),
    ('smarthome_thermostat', 'Smart Home Thermostat'),
    ('smarthome_tuersensor', 'Smart Home Türsensor'),
    ('smarthome_zentrale', 'Smart Home Zentrale'),
    ('solarkabel', 'Solarkabel'),
    ('spannungspruefer', 'Spannungsprüfer'),
    ('sprachassistent', 'Sprachassistent'),
    ('spreizdübel', 'Spreizdübel'),
    ('spiralschlauch', 'Spiralschlauch'),
    ('steckdose_dreifach', 'Steckdose dreifach'),
    ('steckdose_einfach', 'Steckdose einfach'),
    ('steckdose_zweifach', 'Steckdose zweifach'),
    ('stechbeitel', 'Stechbeitel'),
    ('stemmhammer', 'Stemmhammer'),
    ('steuerleitungen', 'Steuerleitungen'),
    ('stromstossschalter', 'Stromstoßschalter'),
    ('stromverteiler', 'Stromverteiler'),
    ('taster', 'Taster'),
    ('telefonanschluss', 'Telefonanschluss'),
    ('telefonkabel', 'Telefonkabel J-Y(St)Y'),
    ('telefonverteiler', 'Telefonverteiler'),
    ('touchpanel', 'Touchpanel'),
    ('tueroeffner', 'Türöffner'),
    ('ueberwachungskamera', 'Überwachungskamera'),
    ('unterputz_abzweigdose', 'Unterputz-Abzweigdose'),
    ('up_dose_dreifach', 'Unterputzdose Dreifach'),
    ('up_dose_klein', 'Unterputzdose Klein'),
    ('up_dose_tief', 'Unterputzdose Tief'),
    ('verbindungsdose', 'Verbindungsdose'),
    ('verbindungsmuffen', 'Verbindungsmuffen'),
    ('verteilerklemmen', 'Verteilerklemmen'),
    ('verteilerschrank_gross', 'Verteilerschrank groß'),
    ('verteilerschrank_klein', 'Verteilerschrank klein'),
    ('verteilerschrank_mittel', 'Verteilerschrank mittel'),
    ('wagoklemmen', 'Wagoklemmen'),
    ('wallbox_11kw', 'Wallbox 11kW'),
    ('wallbox_22kw', 'Wallbox 22kW'),
    ('wandleuchte', 'Wandleuchte'),
    ('wechselrichter', 'Wechselrichter'),
    ('wechselschalter', 'Wechselschalter'),
    ('wechselstromzaehler', 'Wechselstromzähler'),
    ('wellrohr', 'Wellrohr'),
    ('wlan_accesspoint', 'WLAN Access Point'),
    ('wlan_steckdose', 'WLAN-Steckdose'),
    ('ydy_2x1', 'YDY 2x1 mm²'),
    ('ysty', 'Y(St)Y Kabel'),
    ('z_wave_gateway', 'Z-Wave Gateway'),
    ('zaehlerschrank', 'Zählerschrank'),
    ('zeitschaltuhr', 'Zeitschaltuhr'),
    ('zigbee_gateway', 'ZigBee Gateway'),
    ('zugangskontrolle', 'Zugangskontrolle'),
    ('überspannungsschutz', 'Überspannungsschutz'),
]


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