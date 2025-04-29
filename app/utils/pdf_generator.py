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
                              material_list=None):
    """
    Generate a Fortuna Elektro style construction daily report and timesheet
    
    Parameters:
    - output_path: Path where to save the PDF
    - datum: Date (defaults to today if None)
    - bauvorhaben: Construction project name
    - arbeitskraft: Worker name
    - an_abreise: Arrival and departure information
    - arbeitseinsatz: List of dicts with keys 'von', 'bis', 'std' for work time entries
    - material_list: List of dicts with keys 'material', 'menge' for materials used
    """
    
    # Use current date if none specified
    if datum is None:
        datum = datetime.now().strftime("%d.%m.%Y")
    
    # Initialize default values if needed
    if arbeitseinsatz is None:
        arbeitseinsatz = [{'von': '', 'bis': '', 'std': ''}]
    
    if material_list is None:
        material_list = [{'material': '', 'menge': ''}]
    
    # Create a new PDF with A4 size
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Set font
    c.setFont("Helvetica-Bold", 12)
    
    # Company details (header)
    c.drawString(width - 6*cm, height - 2*cm, "Fortuna Elektro GmbH")
    c.setFont("Helvetica", 10)
    c.drawString(width - 6*cm, height - 2.5*cm, "Lothar-Bucher-Straße 5")
    c.drawString(width - 6*cm, height - 3*cm, "12157 Berlin")
    c.drawString(width - 6*cm, height - 3.5*cm, "+49 (030) 499 657 15")
    c.drawString(width - 6*cm, height - 4*cm, "info@fortuna-elektro.com")
    
    # Form fields
    c.setFont("Helvetica-Bold", 10)
    field_start_y = height - 2*cm
    
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
    
    # Draw field labels and values
    for i, (label, value) in enumerate(zip(field_labels, field_values)):
        y_pos = field_start_y - (i * 0.8*cm)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y_pos, label)
        c.setFont("Helvetica", 10)
        c.drawString(5*cm, y_pos, value)
    
    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 5.5*cm, "Bau-Tagesbericht und Stundennachweis")
    
    # Working time section
    c.setFont("Helvetica-Bold", 10)
    time_table_y = height - 7*cm
    
    # Table header
    c.drawString(2*cm, time_table_y, "Arbeitseinsatz")
    c.drawString(6*cm, time_table_y, "von")
    c.drawString(8*cm, time_table_y, "bis")
    c.drawString(10*cm, time_table_y, "Std")
    
    # Draw lines beneath the headers
    c.line(2*cm, time_table_y - 0.3*cm, 12*cm, time_table_y - 0.3*cm)
    
    # Table rows
    c.setFont("Helvetica", 10)
    for i, einsatz in enumerate(arbeitseinsatz):
        row_y = time_table_y - (1 + i) * 0.8*cm
        c.drawString(6*cm, row_y, str(einsatz['von']))
        c.drawString(8*cm, row_y, str(einsatz['bis']))
        c.drawString(10*cm, row_y, str(einsatz['std']))
        
        # Draw lines for additional rows
        c.line(2*cm, row_y - 0.3*cm, 12*cm, row_y - 0.3*cm)
    
    # Material section
    material_y = time_table_y - (len(arbeitseinsatz) + 2) * 0.8*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, material_y, "Material")
    c.drawString(8*cm, material_y, "Menge")
    
    # Draw lines beneath the headers
    c.line(2*cm, material_y - 0.3*cm, 12*cm, material_y - 0.3*cm)
    
    # Material rows
    c.setFont("Helvetica", 10)
    for i, material in enumerate(material_list):
        row_y = material_y - (1 + i) * 0.8*cm
        c.drawString(2*cm, row_y, str(material['material']))
        c.drawString(8*cm, row_y, str(material['menge']))
        
        # Draw lines for additional rows
        c.line(2*cm, row_y - 0.3*cm, 12*cm, row_y - 0.3*cm)
    
    # Save the PDF
    c.save()
    return output_path

if __name__ == "__main__":
    # Example usage
    output_file = "bautagesbericht_example.pdf"
    
    # Sample data
    arbeitseinsatz_example = [
        {'von': '08:00', 'bis': '12:00', 'std': '4.0'},
        {'von': '13:00', 'bis': '17:00', 'std': '4.0'},
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
        material_list=material_example
    )
    
    print(f"PDF erstellt: {os.path.abspath(output_file)}")