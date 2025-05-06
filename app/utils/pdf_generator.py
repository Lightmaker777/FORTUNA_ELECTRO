from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from io import BytesIO

def generate_fortuna_timesheet(output_path, 
                              datum=None,
                              bauvorhaben="",
                              arbeitskraft="",
                              an_abreise="",
                              arbeitseinsatz=None,
                              material_list=None,
                              notes=""):
    
    # Use current date if none specified
    if datum is None:
        datum = datetime.now().strftime("%d.%m.%Y")
    
    # Initialize default values if needed
    if arbeitseinsatz is None:
        arbeitseinsatz = [{'activity': '', 'von': '', 'bis': '', 'std': ''}]
    
    if material_list is None:
        material_list = [{'material': '', 'menge': ''}]
    
    # Farbe für Fortuna Elektro
    FORTUNA_BLUE = colors.HexColor('#003f87')  # Angepasst an die Vorlage
    LIGHT_GRAY = colors.HexColor('#f2f2f2')  # Hellgrau für alternierende Zeilen
    DARK_GRAY = colors.HexColor('#666666')  # Dunkelgrau für Text
    
    # Font einrichten - Fix the font issue by avoiding Arial-Bold
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        # Try to register bold font if available
        try:
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arial_Bold.ttf'))
        except:
            # If Arial-Bold fails, don't worry - we'll handle this later
            pass
        default_font = 'Arial'
    except:
        default_font = 'Helvetica'
    
    # Define the available width for all content - will use this for alignment
    content_width = 17.5*cm  # Total width for all tables
    
    # Erstelle PDF mit ReportLab
    # Entscheide, ob in den Speicher oder in eine Datei geschrieben wird
    
    if output_path == "memory":
        # Wenn in den Speicher geschrieben werden soll (z.B. für Flask)
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            leftMargin=1.5*cm,  # Increased margin to center content 
            rightMargin=1.5*cm, 
            topMargin=1*cm, 
            bottomMargin=1*cm
        )
        elements = []
    else:
        # Wenn in Datei geschrieben werden soll
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4, 
            leftMargin=1.5*cm,  # Increased margin to center content
            rightMargin=1.5*cm, 
            topMargin=1*cm, 
            bottomMargin=1*cm
        )
        elements = []
    
    # Styles definieren
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=default_font,
        fontSize=14,
        textColor=FORTUNA_BLUE,
        spaceAfter=12,
        alignment=1  # Center alignment for title
    )
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName=default_font,
        fontSize=9,
        textColor=DARK_GRAY
    )
    
    # Try to find and load the logo
    logo_paths = [
        os.path.join('static', 'img', 'fortuna-logo.png'),
        os.path.join('app', 'static', 'img', 'fortuna-logo.png'),
        os.path.join('app', 'static', 'fortuna-logo.png'),
        os.path.join('fortuna-logo.png'),
        "static/img/fortuna-logo.png",
        "app/static/img/fortuna-logo.png"
    ]
    
    # Debug information
    print(f"Current working directory: {os.getcwd()}")
    
    # Für die erste Seite definieren wir eine Funktion, die das Logo und die Firmeninfos platziert
    def first_page(canvas, doc):
        canvas.saveState()
        
        # Calculate the left margin position
        left_margin = doc.leftMargin
        
        # Calculate positions to ensure content stays within table width
        logo_x = left_margin
        company_info_x = left_margin + content_width  # Right align at the right edge of content area
        
        # Move logo and address up by 1cm
        logo_y_position = doc.height - 2*cm  # 1cm higher than before
        
        # Logo links platzieren
        logo_found = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    # Logo links oben platzieren, respecting the margin and 1cm higher
                    canvas.drawImage(logo_path, logo_x, logo_y_position, width=3*cm, preserveAspectRatio=True)
                    logo_found = True
                    break
                except Exception as e:
                    print(f"Error loading logo from {logo_path}: {e}")
                    continue
        
        # Firmeninformationen rechts platzieren, ebenfalls 1cm höher
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColorRGB(0, 0.25, 0.53)  # FORTUNA_BLUE als RGB
        canvas.drawRightString(company_info_x, doc.height - 0.5*cm, "Fortuna Elektro GmbH")
        
        canvas.setFillColorRGB(0.4, 0.4, 0.4)  # Dunkelgrau
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(company_info_x, doc.height - 1.0*cm, "Lothar-Bucher-Straße 5")
        canvas.drawRightString(company_info_x, doc.height - 1.5*cm, "12157 Berlin")
        canvas.drawRightString(company_info_x, doc.height - 2.0*cm, "+49 (030) 499 657 15")
        canvas.drawRightString(company_info_x, doc.height - 2.5*cm, "info@fortuna-elektro.com")
        
        canvas.restoreState()
    
    # Wir generieren keinen Header als normales Element, stattdessen wird er beim Build-Prozess hinzugefügt
    elements.append(Spacer(1, 4*cm))  # Platz für Header reservieren
    
    # Titel
    elements.append(Paragraph("Bau-Tagesbericht und Stundennachweis", title_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Informationen zum Auftrag - adjust column widths to match total content width
    col1_width = 3*cm
    col2_width = 5.75*cm
    col3_width = 3*cm
    col4_width = 5.75*cm
    
    auftrag_data = [
        ['Datum:', datum, 'Bauvorhaben:', bauvorhaben],
        ['Arbeitskraft:', arbeitskraft, 'An-/Abreise:', an_abreise]
    ]
    
    auftrag_table = Table(auftrag_data, colWidths=[col1_width, col2_width, col3_width, col4_width])
    auftrag_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), default_font, 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold' if default_font == 'Helvetica' else default_font, 9),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold' if default_font == 'Helvetica' else default_font, 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(auftrag_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Adjust column widths for Arbeitseinsatz to match the total content width
    activity_col_width = 10*cm
    time_col_width = 2.5*cm  # for 'von', 'bis', 'Std' columns
    
    # Arbeitseinsatz Tabellenüberschrift
    arbeitseinsatz_header = [['Arbeitseinsatz', 'von', 'bis', 'Std']]
    arbeitseinsatz_header_table = Table(arbeitseinsatz_header, 
                                         colWidths=[activity_col_width, time_col_width, time_col_width, time_col_width])
    arbeitseinsatz_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), FORTUNA_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONT', (0, 0), (-1, 0), default_font, 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
    ]))
    
    elements.append(arbeitseinsatz_header_table)
    
    # Arbeitseinsatz Daten
    arbeitseinsatz_data = []
    total_hours = 0
    
    # Debug print to see what's in arbeitseinsatz
    print("Arbeitseinsatz entries:", len(arbeitseinsatz))
    for idx, einsatz in enumerate(arbeitseinsatz):
        print(f"Entry {idx}: {einsatz}")
        
        # Here's the fix: Use activityText if available, otherwise fall back to activity
        activity = einsatz.get('activityText', einsatz.get('activity', ''))
        von = einsatz.get('von', '')
        bis = einsatz.get('bis', '')
        std = einsatz.get('std', '')
        
        # Stunden für die Summe berechnen
        try:
            hours = float(std)
            total_hours += hours
        except (ValueError, TypeError):
            pass
        
        arbeitseinsatz_data.append([activity, von, bis, std])
    
    # Stelle sicher, dass mindestens eine Zeile vorhanden ist
    if not arbeitseinsatz_data:
        arbeitseinsatz_data = [['', '', '', '']]
    
    arbeitseinsatz_table = Table(arbeitseinsatz_data, 
                                  colWidths=[activity_col_width, time_col_width, time_col_width, time_col_width])
    
    row_styles = []
    for i in range(len(arbeitseinsatz_data)):
        bg_color = LIGHT_GRAY if i % 2 == 0 else colors.white
        row_styles.append(('BACKGROUND', (0, i), (-1, i), bg_color))
    
    arbeitseinsatz_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), default_font, 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ] + row_styles))
    
    elements.append(arbeitseinsatz_table)
    
    # Summe der Stunden
    if total_hours > 0:
        total_data = [['', '', 'Gesamtstunden:', f"{total_hours:.1f}"]]
        total_table = Table(total_data, 
                            colWidths=[activity_col_width, time_col_width, time_col_width, time_col_width])
        
        # FIX: Use a safer approach for emphasizing text - avoid using custom font names
        # Using a combination of font size and color instead of trying to use a bold font
        total_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), default_font, 9),
            ('TEXTCOLOR', (2, 0), (3, 0), FORTUNA_BLUE),
            # Increase font size slightly and don't reference 'Arial-Bold' directly
            ('FONT', (2, 0), (3, 0), 'Helvetica-Bold' if default_font == 'Helvetica' else default_font, 10),
            ('ALIGN', (2, 0), (3, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(total_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Material table with adjusted column widths
    material_col_width = 15*cm
    amount_col_width = 2.5*cm
    
    # Material Tabellenüberschrift
    material_header = [['Material', 'Menge']]
    material_header_table = Table(material_header, colWidths=[material_col_width, amount_col_width])
    material_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), FORTUNA_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONT', (0, 0), (-1, 0), default_font, 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
    ]))
    
    elements.append(material_header_table)
    
    # Material Daten
    material_data = []
    for material in material_list:
        material_name = material.get('material', '')
        material_amount = material.get('menge', '')
        material_data.append([material_name, material_amount])
    
    # Stelle sicher, dass mindestens eine Zeile vorhanden ist
    if not material_data:
        material_data = [['', '']]
    
    material_table = Table(material_data, colWidths=[material_col_width, amount_col_width])
    
    row_styles = []
    for i in range(len(material_data)):
        bg_color = LIGHT_GRAY if i % 2 == 0 else colors.white
        row_styles.append(('BACKGROUND', (0, i), (-1, i), bg_color))
    
    material_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), default_font, 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ] + row_styles))
    
    elements.append(material_table)
    
    # Notizen hinzufügen, wenn vorhanden, mit angepasster Breite, die der Tabellenbreite entspricht
    if notes:
        elements.append(Spacer(1, 0.5*cm))
        
        # Notizen-Überschrift
        notes_title = Paragraph("Notizen:", title_style)
        elements.append(notes_title)
        
        # Create a notes style with the proper alignment
        notes_style = ParagraphStyle(
            'NotesStyle',
            parent=normal_style,
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0
        )
        
        # Add the notes paragraph with the same width as the tables
        notes_paragraph = Paragraph(notes, notes_style)
        elements.append(notes_paragraph)
    
    # PDF erstellen mit first_page als Template für die erste Seite
    doc.build(elements, onFirstPage=first_page)
    
    # Wenn in den Speicher geschrieben wurde, BytesIO zurückgeben
    if output_path == "memory":
        buffer.seek(0)
        return buffer
    
    return output_path