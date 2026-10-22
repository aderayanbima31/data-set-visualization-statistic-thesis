"""Build a polished PDF version of the completed correlation homework."""

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "correlation_homework_report.pdf"
RESULTS = ROOT / "outputs" / "correlation_results.csv"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8DEE9"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, 9 * mm, "Correlation Analysis Homework | Synthetic teaching dataset")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def main():
    results = pd.read_csv(RESULTS)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleBlue", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=25, leading=30, textColor=colors.HexColor("#1D4ED8"),
        alignment=TA_CENTER, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"], fontSize=11, leading=16,
        textColor=colors.HexColor("#4B5563"), alignment=TA_CENTER, spaceAfter=24,
    ))
    styles.add(ParagraphStyle(
        name="SectionBlue", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=14, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="BodyReadable", parent=styles["BodyText"], fontSize=10.5,
        leading=15, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["BodyText"], fontSize=8.5,
        leading=11, textColor=colors.HexColor("#4B5563"),
    ))
    styles.add(ParagraphStyle(
        name="Callout", parent=styles["BodyText"], fontSize=10, leading=14,
        leftIndent=8, rightIndent=8, spaceBefore=6, spaceAfter=8,
        textColor=colors.HexColor("#1F2937"),
    ))

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="Correlation Analysis Homework",
        author="Derayan Bima A",
    )
    story = []
    story.extend([
        Spacer(1, 22 * mm),
        p("Correlation Analysis Homework", styles["TitleBlue"]),
        p("Analisis Hubungan & Korelasi pada Dataset Migrasi UI", styles["Subtitle"]),
        p("Completed assignment report", styles["BodyReadable"]),
        p(
            "This report applies the five correlation methods requested in the assignment and explains which method fits each variable type.",
            styles["BodyReadable"],
        ),
        Spacer(1, 8 * mm),
        p("Dataset and unit of analysis", styles["SectionBlue"]),
        p(
            "The task catalog contains 36 migration tasks. The observation file contains repeated simulated executions. For relationships involving execution metrics, repeated observations are averaged within each <b>ticket_id</b>, so one task is treated as the unit of analysis.",
            styles["BodyReadable"],
        ),
        p(
            "Important limitation: execution time, token usage, accuracy, test pass rate, and error count are simulated teaching metrics. The results describe this synthetic sample only; they are not measurements of real AI agents, Codex runs, production Android work, or a validated benchmark.",
            styles["Callout"],
        ),
        Spacer(1, 8 * mm),
        p("Variable preparation", styles["SectionBlue"]),
        p(
            "Point-Biserial uses Easy and Hard tasks only so difficulty becomes binary. Contingency Coefficient uses component area and difficulty. Phi uses two binary variables: Hard versus non-Hard and any error versus no error. Spearman uses the ordered ranks Easy=1, Medium=2, Hard=3. Pearson uses task-level mean execution time and mean token usage.",
            styles["BodyReadable"],
        ),
    ])

    table_data = [[
        p("Method", styles["Small"]), p("Variables", styles["Small"]),
        p("n", styles["Small"]), p("Coefficient", styles["Small"]),
        p("p-value", styles["Small"]), p("Decision", styles["Small"]),
    ]]
    for row in results.to_dict("records"):
        pval = "<0.001" if row["p_value"] < 0.001 else f"{row['p_value']:.4f}"
        table_data.append([
            p(str(row["method"]), styles["Small"]),
            p(str(row["variables"]), styles["Small"]),
            p(str(int(row["n"])), styles["Small"]),
            p(f"{row['coefficient']:.4f}", styles["Small"]),
            p(pval, styles["Small"]),
            p(str(row["decision"]).replace(" at alpha=0.05", ""), styles["Small"]),
        ])
    results_table = Table(table_data, colWidths=[31 * mm, 57 * mm, 12 * mm, 23 * mm, 20 * mm, 30 * mm], repeatRows=1)
    results_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([p("Results", styles["SectionBlue"]), results_table])

    story.extend([
        PageBreak(),
        p("Interpretation by method", styles["SectionBlue"]),
        p("<b>1. Point-Biserial.</b> This method fits one binary nominal variable and one continuous variable. It is appropriate for Easy versus Hard tasks and execution time. Hard tasks averaged 130.75 seconds versus 52.51 seconds for Easy tasks, with a strong significant association in this synthetic sample.", styles["BodyReadable"]),
        p("<b>2. Contingency Coefficient.</b> This method fits categorical variables analyzed through a contingency table and chi-square. It is appropriate for component area versus difficulty, but the observed association is not statistically significant.", styles["BodyReadable"]),
        p("<b>3. Phi.</b> This method fits two binary variables only. It is appropriate for Hard versus non-Hard and any error versus no error after the documented binary transformation. The observed association is weak and not statistically significant.", styles["BodyReadable"]),
        p("<b>4. Spearman Rank.</b> This method fits ordinal variables or monotonic relationships without requiring a linear-normal relationship. It is appropriate for ordered difficulty versus execution time and shows a strong positive association.", styles["BodyReadable"]),
        p("<b>5. Pearson Product-Moment.</b> This method fits two continuous variables when the target relationship is linear. It is appropriate for execution time versus token usage and shows a strong positive linear association.", styles["BodyReadable"]),
        p("Formulas used", styles["SectionBlue"]),
        p("Point-Biserial: r<sub>pb</sub> = ((M<sub>1</sub> - M<sub>0</sub>) / s<sub>y</sub>) sqrt(pq).<br/>Contingency Coefficient: CC = sqrt(chi-square / (chi-square + N)).<br/>Phi: phi = (ad - bc) / sqrt((a+b)(c+d)(a+c)(b+d)).<br/>Spearman: rho = 1 - 6 sum(d<sup>2</sup>) / (n(n<sup>2</sup> - 1)).<br/>Pearson: covariance divided by the product of the two standard deviations.", styles["BodyReadable"]),
        p("Final conclusion", styles["SectionBlue"]),
        p("The appropriate correlation method depends on measurement scale. Use Pearson for two continuous metrics, Spearman for ordered difficulty and a metric, Contingency Coefficient for multi-category variables, Phi only for two binary variables, and Point-Biserial for one binary variable paired with one continuous metric. These conclusions are exploratory and limited to the synthetic dataset.", styles["BodyReadable"]),
        Spacer(1, 8 * mm),
        p("Generated from the reproducible analysis script in analysis/correlation_analysis.py. Detailed results and contingency cell counts are available in the accompanying CSV files.", styles["Small"]),
    ])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
