from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

def build_pdf(sections, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Optional: slightly tweak body text
    mono_style = ParagraphStyle(
        "Mono",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=10,
        leading=12
    )

    story = []

    for sec in sections:
        title = sec.get("title", "Untitled Section")
        content = sec.get("content", "").strip()

        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        story.append(Spacer(1, 12))

        if content:
            story.append(Preformatted(content, mono_style))
            story.append(Spacer(1, 18))

    doc.build(story)
