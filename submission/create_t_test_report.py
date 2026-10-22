"""Build the submission PDF for the T-test homework."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "t_test_homework_report.pdf"
RESULTS = ROOT / "outputs" / "t_test_results.csv"
DIAGNOSTICS = ROOT / "outputs" / "t_test_assumption_checks.csv"

NAVY = colors.HexColor("#14324A")
BLUE = colors.HexColor("#2F6F9F")
LIGHT_BLUE = colors.HexColor("#EAF3F8")
PALE = colors.HexColor("#F6F8FA")
GREEN = colors.HexColor("#E8F5EC")
AMBER = colors.HexColor("#FFF4D6")
TEXT = colors.HexColor("#243342")
MUTED = colors.HexColor("#5E6B76")


class HorizontalRule(Flowable):
    def __init__(self, width: float, color=BLUE, thickness: float = 1.0):
        super().__init__()
        self.width = width
        self.height = thickness + 2
        self.color = color
        self.thickness = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1, self.width, 1)


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=24, leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=NAVY, spaceBefore=13, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11.5, leading=14, textColor=BLUE, spaceBefore=8, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.4, leading=13.2, textColor=TEXT, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8.1, leading=10.5, textColor=MUTED, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=7.8, leading=9.5, textColor=colors.white, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=7.6, leading=9.5, textColor=TEXT,
    ))
    styles.add(ParagraphStyle(
        name="TableCellCenter", parent=styles["TableCell"], alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=NAVY, spaceAfter=0,
    ))
    styles.add(ParagraphStyle(
        name="ReportCode", parent=styles["BodyText"], fontName="Courier",
        fontSize=8.5, leading=10, textColor=colors.white,
    ))
    return styles


def cell(text: object, styles, centered: bool = False) -> Paragraph:
    style = styles["TableCellCenter" if centered else "TableCell"]
    return paragraph(str(text), style)


def make_table(data, widths, styles, header=True, row_bgs=None):
    converted = []
    for row_index, row in enumerate(data):
        converted.append([
            paragraph(str(value), styles["TableHead"] if header and row_index == 0 else styles["TableCell"])
            for value in row
        ])
    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DDE4")),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ])
    start_row = 1 if header else 0
    for row_index in range(start_row, len(data)):
        bg = row_bgs[row_index - start_row] if row_bgs else (PALE if row_index % 2 else colors.white)
        commands.append(("BACKGROUND", (0, row_index), (-1, row_index), bg))
    table.setStyle(TableStyle(commands))
    return table


def footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D5DDE4"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "T-Test Homework | Synthetic migration dataset")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def result_rows(results: pd.DataFrame, styles):
    rows = [["Test", "Comparison", "n", "t", "df", "p-value", "Decision"]]
    for _, result in results.iterrows():
        rows.append([
            result["test_type"],
            f"{result['group_a']} vs {result['group_b_or_reference']}",
            f"{int(result['n_a'])}",
            f"{result['t_statistic']:.3f}",
            f"{result['degrees_of_freedom']:.2f}",
            f"{result['p_value_two_sided']:.4g}",
            result["decision_at_alpha_0_05"],
        ])
    return rows


def build_pdf():
    styles = build_styles()
    results = pd.read_csv(RESULTS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=20 * mm, title="T-Test Homework Report",
        author="Statistics for Data Science",
    )
    story = []

    story.extend([
        Spacer(1, 9 * mm),
        paragraph("T-Test Homework Report", styles["ReportTitle"]),
        paragraph("One-sample, paired-samples, and independent-samples analysis", styles["Subtitle"]),
        HorizontalRule(174 * mm),
        Spacer(1, 8 * mm),
    ])
    cover_data = [
        [paragraph("Course", styles["TableHead"]), paragraph("Statistics for Data Science", styles["TableCell"])],
        [paragraph("Assignment", styles["TableHead"]), paragraph("T-Test analysis", styles["TableCell"])],
        [paragraph("Student", styles["TableHead"]), paragraph("Derayan Bima Alamsyah", styles["TableCell"])],
        [paragraph("Lecturer", styles["TableHead"]), paragraph("Undang Syaripudin, Ph.D., M.Kom.", styles["TableCell"])],
        [paragraph("Date", styles["TableHead"]), paragraph("October 7, 2026", styles["TableCell"])],
    ]
    cover = Table(cover_data, colWidths=[34 * mm, 140 * mm], hAlign="CENTER")
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE), ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), PALE), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DDE4")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cover)
    story.append(Spacer(1, 12 * mm))
    story.append(Table([[paragraph(
        "<b>Executive summary.</b> The required three T-test types were applied to the existing repository dataset. The one-sample and independent tests reject their null hypotheses at alpha = 0.05; the paired comparison does not. All conclusions are descriptive and limited to this synthetic teaching sample.",
        styles["Callout"],
    )]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE), ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ])))
    story.append(PageBreak())

    story.append(paragraph("1. Dataset and method", styles["Section"]))
    story.append(paragraph(
        "The analysis uses data/migration_tasks.csv and data/migration_observations.csv. Each migration task has five deterministic synthetic executions. For time-based tests, repeated executions are averaged within ticket_id before testing so that a task, rather than each repeat, is the unit of analysis. The paired test matches agent-specific accuracy by ticket_id.",
        styles["Body"],
    ))
    story.append(paragraph(
        "All tests are two-sided at alpha = 0.05. The one-sample test uses the task-level mean execution time. The paired test uses a paired t-test on agent-A minus agent-B accuracy. The independent comparison uses Welch's t-test because equal variances are not assumed. Effect sizes and 95% confidence intervals are also reported in the generated CSV results.",
        styles["Body"],
    ))
    story.append(Table([[paragraph(
        "Synthetic-data disclosure: execution time, token usage, accuracy, pass rate, and error count are simulated teaching metrics. They are not real AI-agent measurements, Codex benchmarks, production Android measurements, or evidence of general performance.", styles["Body"],
    )]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#C68A00")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])))

    story.append(paragraph("2. Results", styles["Section"]))
    story.append(paragraph("Summary decisions", styles["Subsection"]))
    story.append(make_table(result_rows(results, styles), [38 * mm, 59 * mm, 12 * mm, 16 * mm, 17 * mm, 17 * mm, 25 * mm], styles, row_bgs=[GREEN, PALE, GREEN]))
    story.append(Spacer(1, 4 * mm))

    detail_rows = [["Test", "Mean A", "Mean B/reference", "Difference", "95% CI for difference", "Effect size"]]
    for _, result in results.iterrows():
        detail_rows.append([
            result["test_type"], f"{result['mean_a']:.3f}", f"{result['mean_b_or_reference']:.3f}",
            f"{result['mean_difference_a_minus_b']:.3f}",
            f"[{result['confidence_interval_low']:.3f}, {result['confidence_interval_high']:.3f}]",
            f"{result['effect_size_name']}: {result['effect_size']:.3f}",
        ])
    story.append(make_table(detail_rows, [38 * mm, 22 * mm, 28 * mm, 24 * mm, 39 * mm, 23 * mm], styles))

    story.append(paragraph("Interpretation", styles["Subsection"]))
    story.append(paragraph(
        "<b>One-sample:</b> the mean task-level execution time is 88.03 seconds, 13.03 seconds above the 75-second teaching reference. The two-sided p-value is 0.0155, so the null hypothesis is rejected at alpha = 0.05.", styles["Body"]
    ))
    story.append(paragraph(
        "<b>Paired:</b> agent A's mean task-level accuracy is 0.906 versus 0.901 for agent B. The mean paired difference is 0.0046 and p = 0.4282, so there is not enough evidence in this synthetic sample to reject a zero mean difference.", styles["Body"]
    ))
    story.append(paragraph(
        "<b>Independent:</b> hard tasks average 130.75 seconds versus 52.51 seconds for easy tasks. Welch's p-value is 7.80e-09, so the null hypothesis of equal means is rejected. This reflects the generated difficulty structure, not a production benchmark.", styles["Body"]
    ))

    story.append(paragraph("3. Conclusion and reproducibility", styles["Section"]))
    story.append(paragraph(
        "The three requested T-test types were completed. In this synthetic dataset, task difficulty is associated with execution time, while the matched agent-accuracy comparison does not show a statistically significant mean difference. These findings are descriptive only and should not be generalized beyond this generated sample.", styles["Body"]
    ))
    story.append(paragraph("Reproduksi dari root repository: <font name='Courier'>python analysis/t_test_analysis.py</font>. Verifikasi: <font name='Courier'>python -m unittest discover -s tests -v</font>.", styles["Small"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
