from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from datetime import datetime
import os

def generate_fortuna_timesheet(output_path, 
                              datum=None,
                              bauvorhaben="",
                              arbeitskraft="",
                              an_abreise="",
                              arbeitseinsatz=None,
                              material_list=None,
                              notes=""):
    """
    Generate a Fortuna Elektro style construction daily report and timesheet
    
    Parameters:
    - output_path: Path where to save the PDF
    - datum: Date (defaults to today if None)
    - bauvorhaben: Construction project name
    - arbeitskraft: Worker name
    - an_abreise: Arrival and departure information
    - arbeitseinsatz: List of dicts with keys 'activity', 'von', 'bis', 'std' for work time entries
    - material_list: List of dicts with keys 'material', 'menge' for materials used
    - notes: Additional notes for the report
    """
    
    # Use current date if none specified
    if datum is None:
        datum = datetime.now().strftime("%d.%m.%Y")
    
    # Initialize default values if needed
    if arbeitseinsatz is None:
        arbeitseinsatz = [{'activity': '', 'von': '', 'bis': '', 'std': ''}]
    
    if material_list is None:
        material_list = [{'material': '', 'menge': ''}]
    
    # Create a new PDF with A4 size
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Logo-Pfad - versuchen, einen der möglichen Pfade zu verwenden
    logo_paths = [
        os.path.join('static', 'img', 'fortuna-logo.png'),
        os.path.join('app', 'static', 'img', 'fortuna-logo.png'),
        "\static\img\fortuna-logo.png",
        # Fügen Sie hier weitere mögliche Pfade ein
    ]
    
    # Debug-Information ausgeben
    print(f"Aktuelles Arbeitsverzeichnis: {os.getcwd()}")
    
    logo_found = False
    for logo_path in logo_paths:
        print(f"Prüfe Logo-Pfad: {logo_path}")
        if os.path.exists(logo_path):
            try:
                print(f"Logo gefunden unter: {logo_path}")
                # Logo in der linken oberen Ecke platzieren
                c.drawImage(logo_path, 2*cm, height - 3*cm, width=4*cm, preserveAspectRatio=True)
                logo_found = True
                break
            except Exception as e:
                print(f"Fehler beim Laden des Logos von {logo_path}: {e}")
                continue
    
    # If no logo found or loaded, draw a placeholder text
    if not logo_found:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2.3*cm, "FORTUNA ELEKTRO")
    
    # Company details (header) - Top right
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width - 6*cm, height - 2*cm, "Fortuna Elektro GmbH")
    c.setFont("Helvetica", 9)
    c.drawString(width - 6*cm, height - 2.5*cm, "Lothar-Bucher-Straße 5")
    c.drawString(width - 6*cm, height - 3*cm, "12157 Berlin")
    c.drawString(width - 6*cm, height - 3.5*cm, "+49 (030) 499 657 15")
    c.drawString(width - 6*cm, height - 4*cm, "info@fortuna-elektro.com")
    
    # Title - top center
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 5*cm, "Bau-Tagesbericht und Stundennachweis")
    
    # Form fields
    field_start_y = height - 6*cm  # Moved down to make room for the title
    
    # Left side fields
    field_labels = [
        "Datum:",
        "BV:",
        "Arbeitskraft:",
        "An-u. Abreise:"
    ]
    
    field_values = [
        datum,
        bauvorhaben,
        arbeitskraft,
        an_abreise
    ]
    
    # Draw field labels
    for i, label in enumerate(field_labels):
        y_pos = field_start_y - (i * 0.7*cm)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y_pos, label)
    
    # Draw field values
    for i, value in enumerate(field_values):
        y_pos = field_start_y - (i * 0.7*cm)
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y_pos, value)
    
    # Working time section
    c.setFont("Helvetica-Bold", 10)
    time_table_y = field_start_y - (len(field_labels) * 0.7*cm) - 1*cm
    
    # Table header
    c.drawString(2*cm, time_table_y, "Arbeitseinsatz")
    c.drawString(4*cm, time_table_y, "Tätigkeit")  # Neue Spalte für Tätigkeiten
    c.drawString(8*cm, time_table_y, "von")
    c.drawString(10*cm, time_table_y, "bis")
    c.drawString(12*cm, time_table_y, "Std")
    
    # Draw lines beneath the headers
    c.line(2*cm, time_table_y - 0.3*cm, 14*cm, time_table_y - 0.3*cm)
    
    # Table rows
    c.setFont("Helvetica", 10)
    total_hours = 0
    for i, einsatz in enumerate(arbeitseinsatz):
        row_y = time_table_y - (1 + i) * 0.8*cm
        
        # Add activity/Tätigkeit column
        activity = einsatz.get('activity', '')
        c.drawString(4*cm, row_y, str(activity))
        
        # Original columns
        c.drawString(8*cm, row_y, str(einsatz['von']))
        c.drawString(10*cm, row_y, str(einsatz['bis']))
        c.drawString(12*cm, row_y, str(einsatz['std']))
        
        # Calculate total hours
        try:
            hours = float(einsatz['std'])
            total_hours += hours
        except (ValueError, TypeError):
            pass
        
        # Draw lines for additional rows
        c.line(2*cm, row_y - 0.3*cm, 14*cm, row_y - 0.3*cm)
        
        # Don't draw more than 8 rows to avoid overflowing the page
        if i >= 7:
            break
    
    # Add total hours at the bottom
    if arbeitseinsatz and len(arbeitseinsatz) > 0:
        total_row_y = time_table_y - (min(len(arbeitseinsatz), 8) + 1) * 0.8*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10*cm, total_row_y, "Summe:")
        c.drawString(12*cm, total_row_y, f"{total_hours:.1f}")
        c.line(2*cm, total_row_y - 0.3*cm, 14*cm, total_row_y - 0.3*cm)
    
    # Material section
    material_y = time_table_y - (min(len(arbeitseinsatz), 8) + 2) * 0.8*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, material_y, "Material")
    c.drawString(10*cm, material_y, "Menge")
    
    # Draw lines beneath the headers
    c.line(2*cm, material_y - 0.3*cm, 14*cm, material_y - 0.3*cm)
    
    # Material rows
    c.setFont("Helvetica", 10)
    for i, material in enumerate(material_list):
        row_y = material_y - (1 + i) * 0.8*cm
        c.drawString(2*cm, row_y, str(material['material']))
        c.drawString(10*cm, row_y, str(material['menge']))
        
        # Draw lines for additional rows
        c.line(2*cm, row_y - 0.3*cm, 14*cm, row_y - 0.3*cm)
        
        # Don't draw more than 10 rows to avoid overflowing the page
        if i >= 9:
            break
    
    # Add notes section if provided
    if notes:
        notes_y = material_y - (min(len(material_list), 10) + 2) * 0.8*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, notes_y, "Notizen:")
        c.setFont("Helvetica", 10)
        
        # Split notes into multiple lines if needed
        notes_lines = []
        max_width = 12*cm
        words = notes.split()
        current_line = words[0] if words else ""
        
        for word in words[1:]:
            test_line = current_line + " " + word
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                current_line = test_line
            else:
                notes_lines.append(current_line)
                current_line = word
        
        if current_line:
            notes_lines.append(current_line)
        
        # Draw notes lines
        for i, line in enumerate(notes_lines):
            line_y = notes_y - (1 + i) * 0.5*cm
            c.drawString(2*cm, line_y, line)
            
            if i >= 5:  # Max 6 lines of notes
                break
    
    # Save the PDF
    c.save()
    return output_path

if __name__ == "__main__":
    # Example usage with tätigkeiten (activities)
    output_file = "bautagesbericht_example.pdf"
    
    # Sample data with activities
    arbeitseinsatz_example = [
        {'activity': 'Elektroinstallation', 'von': '08:00', 'bis': '12:00', 'std': '4.0'},
        {'activity': 'Leuchten montieren', 'von': '13:00', 'bis': '17:00', 'std': '4.0'},
    ]
    
    material_example = [
        {'material': 'Kabel 3x1.5mm²', 'menge': '25m'},
        {'material': 'Schalterdosen', 'menge': '6 Stk'},
        {'material': 'Lichtschalter', 'menge': '4 Stk'},
    ]
    
    # Generate the PDF
    generate_fortuna_timesheet(
        output_file,
        datum="29.04.2025",
        bauvorhaben="Bismarckallee 13", 
        arbeitskraft="Max Mustermann",
        an_abreise="07:45 - 17:15",
        arbeitseinsatz=arbeitseinsatz_example,
        material_list=material_example,
        notes="Kundin hat spontan 2 zusätzliche Steckdosen gewünscht. Diese wurden installiert und werden separat berechnet."
    )
    
    print(f"PDF erstellt: {os.path.abspath(output_file)}")