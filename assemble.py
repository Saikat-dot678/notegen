from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Base styles
styles = getSampleStyleSheet()

# Configure TOC styles
toc_style = ParagraphStyle(
    name='TOCHeading',
    fontSize=12,
    leftIndent=20,
    firstLineIndent=-20,
    spaceBefore=5,
)
toc = TableOfContents()
toc.levelStyles = [toc_style]

def build_pdf(sections, out_path):
    doc = SimpleDocTemplate(out_path)
    story = []

    # Title page
    story.append(Paragraph("Generated Notes", styles["Title"]))
    story.append(Spacer(1, 0.5*inch))

    # Table of Contents
    story.append(Paragraph("Table of Contents", styles["Heading1"]))
    story.append(toc)
    story.append(PageBreak())

    # Sections
    for sec in sections:
        title = sec.get("title", "Section")
        # Register heading for TOC
        # The second arg is the level (1 for H2)
        toc.addEntry(1, title, len(story))

        # Section heading
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Spacer(1, 0.1*inch))

        # Bullets
        for b in sec.get("bullets", []):
            story.append(Paragraph("• " + b, styles["Normal"]))
        story.append(Spacer(1, 0.2*inch))

        # Diagram
        if sec.get("diagram_path"):
            story.append(Image(sec["diagram_path"], width=4*inch, height=3*inch))
            story.append(Spacer(1, 0.3*inch))

        story.append(PageBreak())

    # Page numbers
    def add_page_number(canvas, doc):
        canvas.drawRightString(
            7.5*inch, 0.5*inch,
            f"Page {doc.page}"
        )

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
