"""
Textora AI - PDF Report Generator
Produces a high-fidelity, branded PDF audit report using reportlab.
"""
import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Custom Brand Colors
COLOR_MIDNIGHT_TEAL = colors.HexColor("#102A2A")
COLOR_FOREST_TEAL = colors.HexColor("#183A38")
COLOR_LIME = colors.HexColor("#6EA300")  # darkened for clean contrast on white PDF
COLOR_CORAL = colors.HexColor("#D9534F")
COLOR_IVORY_BG = colors.HexColor("#F9F8F3")
COLOR_MUTED_TEXT = colors.HexColor("#5A6E68")
COLOR_BORDER = colors.HexColor("#D4DCD9")

def generate_pdf_report(results: Dict[str, Any], document_name: str = "Document") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_MIDNIGHT_TEAL
    )
    
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=COLOR_MUTED_TEXT
    )
    
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=COLOR_FOREST_TEAL,
        spaceBefore=14,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#222222")
    )
    
    badge_style = ParagraphStyle(
        "ScoreBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        textColor=colors.white
    )
    
    badge_sub = ParagraphStyle(
        "ScoreBadgeSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        alignment=1,
        textColor=colors.white
    )
    
    story = []
    
    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>TEXTORA AI</b>", title_style),
            Paragraph(f"<b>Audit Date:</b> {results.get('created_at', 'Recent')}<br/><b>Format:</b> Automated Assessment", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, COLOR_MIDNIGHT_TEAL),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 10))
    
    # Document Metadata Box
    stats = results.get("statistics", {})
    meta_text = (
        f"<b>Document:</b> {document_name} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Words:</b> {stats.get('word_count', 0):,} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Sentences:</b> {stats.get('sentence_count', 0)} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Method:</b> {results.get('method', 'Linguistic Heuristics')}"
    )
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 12))
    
    # 2. Executive Scorecard Box
    scores = results.get("scores", {})
    ai_pct = scores.get("ai_score", 0)
    human_pct = scores.get("human_score", 0)
    classification = results.get("classification", "Inconclusive")
    confidence = results.get("confidence", "Moderate")
    
    # Color based on classification
    cls_bg = COLOR_CORAL if "AI" in classification else (COLOR_LIME if "Human" in classification else COLOR_FOREST_TEAL)
    
    score_cards = [
        [
            Paragraph(f"{ai_pct}%", badge_style),
            Paragraph(f"{human_pct}%", badge_style),
            Paragraph(classification.upper(), badge_style)
        ],
        [
            Paragraph("AI-Like Pattern Signal", badge_sub),
            Paragraph("Human-Like Pattern Signal", badge_sub),
            Paragraph(f"Confidence: {confidence}", badge_sub)
        ]
    ]
    t_scores = Table(score_cards, colWidths=[2.2 * inch, 2.2 * inch, 2.8 * inch])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 1), COLOR_CORAL),
        ('BACKGROUND', (1, 0), (1, 1), COLOR_LIME),
        ('BACKGROUND', (2, 0), (2, 1), cls_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 12))
    
    # Summary Paragraph
    summary_text = f"<b>Analysis Summary:</b> {results.get('summary', '')}"
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 12))
    
    # 3. Linguistic Metrics Table
    story.append(Paragraph("<b>Core Linguistic Indicators</b>", section_heading))
    metrics = results.get("metrics", {})
    burst = metrics.get("burstiness", {})
    lex = metrics.get("lexical_diversity", {})
    read = metrics.get("readability", {})
    form = metrics.get("formulaic_patterns", {})
    
    metrics_table_data = [
        ["Linguistic Dimension", "Measured Value", "Observed Interpretation"],
        ["Sentence Burstiness (CV)", f"{burst.get('coefficient_of_variation', 0)}", burst.get('burstiness_label', '')],
        ["Type-Token Ratio (TTR)", f"{lex.get('ttr', 0)}", lex.get('diversity_label', '')],
        ["Hapax Ratio (Unique once)", f"{lex.get('hapax_ratio', 0)}", f"{lex.get('hapax_count', 0)} single-occurrence words"],
        ["Reading Grade Level", f"Grade {read.get('flesch_kincaid_grade', 'N/A')}", read.get('flesch_reading_ease_label', '')],
        ["Formulaic Markers", f"{form.get('total_markers', 0)} markers", f"Density: {form.get('density_per_100_words', 0)} per 100 words"]
    ]
    t_metrics = Table(metrics_table_data, colWidths=[1.8 * inch, 1.4 * inch, 4.0 * inch])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_IVORY_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_FOREST_TEAL),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))
    
    # 4. Detected Clichés & Tropes (if any)
    matched = form.get("matched_phrases", [])
    if matched:
        story.append(Paragraph("<b>Detected Formulaic Patterns & Tropes</b>", section_heading))
        matched_str = ", ".join([f"'{m}'" for m in matched])
        story.append(Paragraph(f"The following algorithmic patterns were identified: {matched_str}", body_style))
        story.append(Spacer(1, 8))
        
    # 5. Recommendations
    recs = results.get("recommendations", [])
    if recs:
        story.append(Paragraph("<b>Recommendations for Clarity & Originality</b>", section_heading))
        for r in recs[:3]:
            rec_p = Paragraph(f"• <b>{r.get('title', '')}</b> ({r.get('category', '')}): {r.get('description', '')}", body_style)
            story.append(rec_p)
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 8))
        
    # 6. Sample Sentence Breakdown
    sentences_data = results.get("sentence_breakdown", {}).get("sentences", [])
    if sentences_data:
        story.append(Paragraph("<b>Representative Sentence Analysis</b>", section_heading))
        s_table_data = [["#", "Sentence Excerpt", "Signal", "Observable Notes"]]
        for s in sentences_data[:6]:
            text_snippet = s.get("text", "")
            if len(text_snippet) > 80:
                text_snippet = text_snippet[:77] + "..."
            sig = s.get("signal", "mixed").upper()
            notes = "; ".join(s.get("reasons", [])) or "Standard structure"
            s_table_data.append([str(s.get("index", 1)), text_snippet, sig, notes])
            
        t_sentences = Table(s_table_data, colWidths=[0.3 * inch, 3.2 * inch, 0.9 * inch, 2.8 * inch])
        t_sentences.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_IVORY_BG),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ]))
        story.append(t_sentences)
        story.append(Spacer(1, 14))
        
    # 7. Mandatory Ethical & Probabilistic Disclaimer
    disclaimer_text = (
        "<b>Important Disclaimer:</b> This report provides an automated assessment of writing patterns. "
        "It does not establish authorship, and false positives or false negatives are possible. "
        "Stylistic characteristics can overlap between human and machine-generated texts."
    )
    disclaimer_p = Paragraph(disclaimer_text, ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=COLOR_MUTED_TEXT
    ))
    
    t_disc = Table([[disclaimer_p]], colWidths=[7.2 * inch])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), COLOR_IVORY_BG),
        ('BOX', (0, 0), (0, 0), 1, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ('LEFTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
    ]))
    story.append(KeepTogether(t_disc))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
