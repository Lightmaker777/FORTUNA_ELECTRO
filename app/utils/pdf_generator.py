# app/utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from datetime import datetime


def generate_timesheet_pdf(pdf_path, project, user, date, activity, hours, notes=None):
    """PDF für Stundenberichte generieren"""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    
    # Stile definieren
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Titel
    elements.append(Paragraph("Stundenbericht", title_style))
    elements.append(Spacer(1, 10*mm))
    
    # Projektdetails
    elements.append(Paragraph(f"Projekt: {project.name}", subtitle_style))
    elements.append(Spacer(1, 5*mm))
    
    # Allgemeine Informationen
    data = [
        ["Datum:", date.strftime("%d.%m.%Y")],
        ["Mitarbeiter:", user.username],
        ["Tätigkeit:", activity],
        ["Stunden:", f"{hours:.2f}"]
    ]
    
    table = Table(data, colWidths=[80*mm, 80*mm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10*mm))
    
    # Notizen, falls vorhanden
    if notes:
        elements.append(Paragraph("Notizen:", subtitle_style))
        elements.append(Spacer(1, 2*mm))
        elements.append(Paragraph(notes, normal_style))
        elements.append(Spacer(1, 10*mm))

    # Unterschriftsfeld
    elements.append(Paragraph("Bestätigung:", subtitle_style))
    elements.append(Spacer(1, 20*mm))  # Platz für Unterschrift
    
    # Unterschriftslinien
    sig_data = [
        ["________________________", "________________________"],
        ["Unterschrift Mitarbeiter", "Unterschrift Kunde/Vorgesetzter"]
    ]
    sig_table = Table(sig_data, colWidths=[80*mm, 80*mm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(sig_table)
    
    # Erstelle das PDF
    doc.build(elements)
    
    return pdf_path    