"""Build the non-parametric test coursework submission PDF."""

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
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "non_parametric_homework_report.pdf"
RESULTS = ROOT / "outputs" / "non_parametric_results.csv"
GROUP_SUMMARIES = ROOT / "outputs" / "non_parametric_group_summaries.csv"
CONTINGENCY = ROOT / "outputs" / "non_parametric_contingency_table.csv"
DIAGNOSTICS = ROOT / "outputs" / "non_parametric_diagnostics.csv"

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


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=NAVY, spaceBefore=11, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11.2, leading=14, textColor=BLUE, spaceBefore=7, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.2, leading=13, textColor=TEXT, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Small", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=7.6, leading=9.2, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=7.5, leading=9.4, textColor=TEXT,
    ))
    styles.add(ParagraphStyle(
        name="TableCellCenter", parent=styles["TableCell"], alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=9.4, leading=13.5, textColor=NAVY, spaceAfter=0,
    ))
    return styles


def p(text: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(str(text), style)


def make_table(rows, widths, styles, header=True, font_style=None):
    converted = []
    for row_index, row in enumerate(rows):
        row_style = styles["TableHead"] if header and row_index == 0 else styles[font_style or "TableCell"]
        converted.append([p(value, row_style) for value in row])
    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DDE4")),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for row_index in range(1 if header else 0, len(rows)):
        commands.append(("BACKGROUND", (0, row_index), (-1, row_index), PALE if row_index % 2 else colors.white))
    table.setStyle(TableStyle(commands))
    return table


def footer(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#D5DDE4"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Non-Parametric Test | Synthetic migration dataset")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def format_p(value: float) -> str:
    return f"{value:.4g}"


def decision_background(decision: str):
    return GREEN if decision == "Reject H0" else PALE


def build_pdf() -> None:
    styles = build_styles()
    results = pd.read_csv(RESULTS)
    groups = pd.read_csv(GROUP_SUMMARIES)
    contingency = pd.read_csv(CONTINGENCY)
    diagnostics = pd.read_csv(DIAGNOSTICS)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=20 * mm,
        title="Laporan Uji Non-Parametrik", author="Derayan Bima Alamsyah",
    )
    story = [
        Spacer(1, 8 * mm),
        p("LAPORAN UJI NON-PARAMETRIK", styles["ReportTitle"]),
        p("Mann-Whitney, Wilcoxon, Kruskal-Wallis, dan Chi-Square", styles["Subtitle"]),
        HorizontalRule(174 * mm),
        Spacer(1, 8 * mm),
    ]

    cover_rows = [
        ["Mata kuliah", "Statistics for Data Science"],
        ["Tugas", "Non-Parametric Test"],
        ["Nama", "Derayan Bima Alamsyah"],
        ["Tanggal", "22 Oktober 2026"],
        ["Dataset", "Synthetic Android UI migration dataset"],
    ]
    cover_data = [[p(row[0], styles["TableHead"]), p(row[1], styles["TableCell"])] for row in cover_rows]
    cover = Table(cover_data, colWidths=[35 * mm, 139 * mm], hAlign="CENTER")
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE),
        ("BACKGROUND", (1, 0), (1, -1), PALE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DDE4")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([cover, Spacer(1, 11 * mm)])

    summary_text = (
        "Empat uji non-parametrik diterapkan pada dataset migrasi Android sintetis. "
        "Pada alpha = 0.05, Mann-Whitney dan Chi-Square menolak H0, sedangkan Wilcoxon "
        "dan Kruskal-Wallis belum memberikan bukti yang cukup untuk menolak H0."
    )
    story.append(Table([[p(summary_text, styles["Callout"])]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ])))
    story.extend([
        Spacer(1, 6 * mm),
        p("Laporan ini hanya menjelaskan pola dalam sampel sintetis yang tersedia. Nilai waktu eksekusi, token, akurasi, pass rate, dan error count adalah data simulasi untuk pembelajaran, bukan pengukuran agent AI atau benchmark produksi.", styles["Body"]),
        PageBreak(),
    ])

    story.append(p("1. Dataset dan rancangan analisis", styles["Section"]))
    story.append(p(
        "Analisis menggunakan data/migration_tasks.csv yang berisi 36 task dan data/migration_observations.csv yang berisi 180 observasi. Setiap task memiliki lima pengulangan eksekusi sintetis. Untuk uji yang menggunakan task sebagai unit analisis, lima pengulangan dirata-ratakan berdasarkan ticket_id agar satu task tidak dihitung sebagai lima sampel independen.",
        styles["Body"],
    ))
    method_rows = [
        ["Metode", "Perbandingan", "Unit analisis"],
        ["Mann-Whitney U", "Waktu Hard vs Easy", "Satu mean task-level per task"],
        ["Wilcoxon signed-rank", "Akurasi agent A vs B", "Satu pasangan matched task"],
        ["Kruskal-Wallis H", "Waktu antar-component area", "Satu mean task-level per task"],
        ["Chi-Square independence", "Difficulty vs status mayoritas", "Satu status mayoritas per task"],
    ]
    story.append(make_table(method_rows, [36 * mm, 61 * mm, 77 * mm], styles))
    story.append(p("Semua pengujian bersifat dua sisi dengan alpha = 0.05. Effect size disertakan agar keputusan p-value tidak dibaca sebagai ukuran besar-kecilnya perbedaan secara otomatis.", styles["Body"]))

    story.append(p("2. Ringkasan hasil", styles["Section"]))
    result_rows = [["Uji", "Statistik", "df", "p-value", "Effect size", "Keputusan"]]
    row_backgrounds = []
    for _, row in results.iterrows():
        df_value = "-" if pd.isna(row["degrees_of_freedom"]) else f"{row['degrees_of_freedom']:.0f}"
        result_rows.append([
            row["test_type"],
            f"{row['statistic_name']} = {row['statistic']:.3f}",
            df_value,
            format_p(row["p_value_two_sided"]),
            f"{row['effect_size_name']} = {row['effect_size']:.3f}",
            row["decision_at_alpha_0_05"],
        ])
        row_backgrounds.append(decision_background(row["decision_at_alpha_0_05"]))
    result_table = make_table(result_rows, [37 * mm, 25 * mm, 12 * mm, 22 * mm, 48 * mm, 30 * mm], styles)
    for index, background in enumerate(row_backgrounds, start=1):
        result_table.setStyle(TableStyle([("BACKGROUND", (0, index), (-1, index), background)]))
    story.extend([result_table, Spacer(1, 5 * mm)])

    group_rows = [["Test", "Kelompok", "n", "Mean", "Median"]]
    selected_ids = {
        "mann_whitney_difficulty_time": "Mann-Whitney",
        "wilcoxon_agent_accuracy": "Wilcoxon",
        "kruskal_component_area_time": "Kruskal-Wallis",
    }
    for _, row in groups.iterrows():
        group_rows.append([
            selected_ids.get(row["test_id"], row["test_id"]), row["group"],
            int(row["n"]), f"{row['mean']:.3f}", f"{row['median']:.3f}",
        ])
    story.append(p("Ringkasan kelompok", styles["Subsection"]))
    story.append(make_table(group_rows, [38 * mm, 62 * mm, 18 * mm, 26 * mm, 30 * mm], styles))
    story.append(PageBreak())

    story.append(p("3. Interpretasi", styles["Section"]))
    interpretations = [
        "<b>Mann-Whitney:</b> waktu eksekusi task Hard memiliki median 125.530 detik, sedangkan task Easy 49.980 detik. Nilai p = 0.0001028 menunjukkan perbedaan distribusi yang signifikan pada sampel ini. Rank-biserial correlation = 1.000 menunjukkan seluruh nilai Hard lebih tinggi daripada nilai Easy pada data task-level yang digunakan.",
        "<b>Wilcoxon:</b> median akurasi agent A adalah 0.907 dan agent B 0.915. Nilai p = 0.6406, sehingga belum ada bukti yang cukup untuk menyimpulkan perbedaan akurasi berpasangan pada sampel ini. Kesimpulan ini tidak berarti kedua agent pasti sama dalam populasi yang lebih luas.",
        "<b>Kruskal-Wallis:</b> uji omnibus antar-enam component area menghasilkan H = 8.184, df = 5, dan p = 0.1464. Dengan alpha = 0.05, belum ada bukti yang cukup bahwa distribusi waktu eksekusi berbeda antar-area. Karena hasil omnibus tidak signifikan, post-hoc pairwise test tidak dijalankan sebagai bagian dari laporan ini.",
        "<b>Chi-Square:</b> terdapat asosiasi antara difficulty dan status mayoritas task, chi-square = 31.535, df = 2, p = 1.42e-07, dengan Cramer's V = 0.936. Namun, tiga expected cell berada di bawah 5, sehingga hasil perlu dibaca hati-hati dan dapat memerlukan penggabungan kategori atau metode exact pada analisis lanjutan.",
    ]
    for item in interpretations:
        story.append(p(item, styles["Body"]))

    story.append(p("Tabel kontingensi Chi-Square", styles["Subsection"]))
    chi_rows = [["Difficulty", "Passed with fixes", "Passed"]]
    for _, row in contingency.iterrows():
        chi_rows.append([row["row_category"], int(row["Passed with fixes"]), int(row["Passed"])])
    story.append(make_table(chi_rows, [45 * mm, 52 * mm, 52 * mm], styles))
    story.append(p("Status task ditentukan dari status mayoritas lima observasi sintetis pada task tersebut.", styles["Small"]))

    story.append(p("4. Diagnostics dan keterbatasan", styles["Section"]))
    diag_rows = [["Uji", "Diagnostic", "Nilai", "Catatan"]]
    for _, row in diagnostics.iterrows():
        value = "-" if pd.isna(row["value"]) else f"{row['value']:.3f}" if isinstance(row["value"], float) else str(int(row["value"]))
        diag_rows.append([row["test_id"], row["diagnostic"], value, row["flag"]])
    story.append(make_table(diag_rows, [47 * mm, 42 * mm, 20 * mm, 65 * mm], styles))
    story.append(p(
        "Interpretasi dibatasi pada dataset sintetis ini. Data dibuat untuk latihan statistik dan tidak boleh dipresentasikan sebagai data riil Codex, agent AI, aplikasi Android produksi, atau benchmark performa. Hasil signifikan juga tidak membuktikan hubungan sebab-akibat.",
        styles["Body"],
    ))

    story.append(p("5. Reproduksi", styles["Section"]))
    story.append(p(
        "Analisis dapat dijalankan ulang dari root repository dengan perintah berikut:", styles["Body"]
    ))
    story.append(Table([[p("python analysis/non_parametric_analysis.py", styles["TableCell"])]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DDE4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ])))
    story.append(p(
        "Perintah tersebut membaca data mentah tanpa mengubahnya dan menghasilkan tabel hasil, ringkasan kelompok, tabel kontingensi, diagnostics, serta laporan Markdown di folder outputs/.", styles["Body"]
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
