"""PDF generation for clinical recommendations."""
import os
import base64
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.config import settings


def generate_recommendation_pdf(
    case_data: Dict,
    user_data: Dict,
    output_path: str
) -> str:
    """
    Generate a professional PDF report for clinical recommendations.
    
    Args:
        case_data: Dictionary containing case information
        user_data: Dictionary containing clinician information
        output_path: Path where PDF will be saved
        
    Returns:
        Path to generated PDF
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=50
    )
    
    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("H. pylori Clinical Decision Support", title_style))
    story.append(Paragraph("Assessment Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Institution/Clinician Info
    institution = user_data.get('institution', 'Medical Institution')
    clinician_name = user_data.get('full_name', user_data.get('username', 'Clinician'))
    specialty = user_data.get('specialty', 'General Practice')
    
    info_data = [
        ['Institution:', institution],
        ['Clinician:', clinician_name],
        ['Specialty:', specialty],
        ['License:', user_data.get('license_number', 'N/A')],
        ['Report Date:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Information (if available)
    patient_name = case_data.get('patient_name', case_data.get('patient_pseudo_id', 'N/A'))
    story.append(Paragraph("Patient Information", heading_style))
    patient_data = [
        ['Patient ID:', patient_name],
        ['Assessment Date:', case_data.get('created_at', datetime.now().strftime('%Y-%m-%d'))]
    ]
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Assessment Results
    story.append(Paragraph("Assessment Results", heading_style))
    
    screen_prob = case_data.get('screen_prob')
    if screen_prob is not None:
        risk_level = "HIGH RISK" if screen_prob >= 0.6 else "MODERATE RISK" if screen_prob >= 0.4 else "LOW RISK"
        risk_color = colors.red if screen_prob >= 0.6 else colors.orange if screen_prob >= 0.4 else colors.green
        
        results_data = [
            ['H. pylori Infection Probability:', f'{screen_prob*100:.1f}%'],
            ['Risk Level:', risk_level]
        ]
        
        if case_data.get('stage_pred'):
            results_data.append(['Resistance Stage:', case_data['stage_pred'].upper()])
        
        results_table = Table(results_data, colWidths=[3*inch, 3*inch])
        results_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(results_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Clinical Recommendations
    story.append(Paragraph("Clinical Recommendations", heading_style))
    
    # Use edited recommendations if available, otherwise original
    recommendations = case_data.get('edited_recommendations', case_data.get('recommendations', []))
    
    for i, rec in enumerate(recommendations, 1):
        # Clean up recommendation text (remove emojis for PDF)
        clean_rec = rec.replace('🔴', '•').replace('🟡', '•').replace('🟢', '•').replace('⚠', '!').replace('ℹ️', 'NOTE:')
        story.append(Paragraph(f"{i}. {clean_rec}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Notes (if any)
    if case_data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Clinical Notes", heading_style))
        story.append(Paragraph(case_data['notes'], styles['Normal']))
    
    # Signature
    story.append(Spacer(1, 0.4*inch))
    
    signature_data = case_data.get('signature_data') or user_data.get('digital_signature')
    if signature_data:
        try:
            # Decode base64 signature
            signature_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            signature_img = Image(BytesIO(signature_bytes), width=2*inch, height=1*inch)
            story.append(Paragraph("Digitally Signed By:", heading_style))
            story.append(signature_img)
        except:
            pass
    
    story.append(Paragraph(f"<b>{clinician_name}</b>", styles['Normal']))
    story.append(Paragraph(f"{specialty}", styles['Normal']))
    story.append(Paragraph(f"Signed on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    
    # Disclaimer
    story.append(Spacer(1, 0.5*inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "<b>CLINICAL DISCLAIMER:</b> This report is generated by a Clinical Decision Support System. "
        "All recommendations are suggestions only and must be reviewed and approved by a qualified healthcare provider. "
        "Final clinical decisions rest with the treating physician. This system does not replace clinical judgment.",
        disclaimer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return output_path

