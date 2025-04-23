from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import pandas as pd
import datetime
from pathlib import Path

current_path = Path("C:/Users/luizh/Documents/visual_studio/my_projects/invest_control_v2")


def generate_portfolio_pdf(output_path, portfolio_df, image_paths=None, logo_path=None):
    # Setup document
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=22, spaceAfter=20)
    header_style = ParagraphStyle("HeaderStyle", parent=styles["Heading2"], textColor=colors.darkblue)
    normal_style = styles["Normal"]

    # Header with logo and title
    if logo_path:
        story.append(Image(logo_path, width=3*cm, height=3*cm))
        story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Relatório de Investimentos", title_style))
    story.append(Paragraph(datetime.datetime.today().strftime("%d/%m/%Y"), normal_style))
    story.append(Spacer(1, 1*cm))

    # Add chart images if provided
    if image_paths:
        for image in image_paths:
            story.append(Image(image, width=16*cm, height=8*cm))
            story.append(Spacer(1, 0.5*cm))

    # Section header
    story.append(Paragraph("📊 Posição Consolidada", header_style))
    story.append(Spacer(1, 0.3*cm))

    # Table: format DataFrame
    df = portfolio_df.copy()
    table_data = [df.columns.tolist()] + df.values.tolist()

    table = Table(table_data, hAlign='LEFT', colWidths='*')
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    story.append(table)

    # Add footer/page number later via canvas if needed

    doc.build(story)

    print(f"✅ PDF gerado: {output_path}")

portfolio_df = pd.DataFrame({
    "Ativo": ["AAPL", "TSLA", "IVVB11"],
    "Quantidade": [10, 5, 12],
    "Preço Médio": [150.0, 700.0, 120.0],
    "Valor Atual": [170.0, 720.0, 130.0]
})

generate_portfolio_pdf(
    "relatorio_profissional.pdf",
    portfolio_df,
    image_paths=[current_path/"chart_example.png"],
    logo_path=current_path/"logo.jpg"  # optional
)