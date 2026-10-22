"""Build the Indonesian submission PDF for the T-test homework."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from create_t_test_report import (
    AMBER,
    BLUE,
    LIGHT_BLUE,
    MUTED,
    NAVY,
    PALE,
    ROOT,
    TEXT,
    build_styles,
    footer,
    make_table,
    paragraph,
    HorizontalRule,
)


OUTPUT = ROOT / "submission" / "tugas_t_test-DerayanBimaA.pdf"
RESULTS = ROOT / "outputs" / "t_test_results.csv"
DIAGNOSTICS = ROOT / "outputs" / "t_test_assumption_checks.csv"


def footer_id(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#D5DDE4"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Tugas T-Test | Dataset migrasi sintetis")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Halaman {doc.page}")
    canvas.restoreState()


def build_indonesian_styles():
    styles = build_styles()
    styles.add(ParagraphStyle(
        name="IdTitle", parent=styles["ReportTitle"], fontName="Helvetica-Bold",
        fontSize=24, leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="IdCallout", parent=styles["Callout"], fontName="Helvetica-Bold",
        fontSize=10, leading=14, textColor=NAVY,
    ))
    styles.add(ParagraphStyle(
        name="IdCode", parent=styles["BodyText"], fontName="Courier",
        fontSize=8.5, leading=10, textColor=colors.white,
    ))
    return styles


def build_pdf():
    styles = build_indonesian_styles()
    results = pd.read_csv(RESULTS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=20 * mm, title="Laporan Tugas T-Test",
        author="Statistics for Data Science",
    )
    story = [
        Spacer(1, 9 * mm),
        paragraph("Laporan Tugas T-Test", styles["IdTitle"]),
        paragraph("Analisis one-sample, paired, dan independent T-test", styles["Subtitle"]),
        HorizontalRule(174 * mm), Spacer(1, 8 * mm),
    ]
    cover_data = [
        [paragraph("Mata kuliah", styles["TableHead"]), paragraph("Statistics for Data Science", styles["TableCell"])],
        [paragraph("Tugas", styles["TableHead"]), paragraph("Analisis T-Test", styles["TableCell"])],
        [paragraph("Nama", styles["TableHead"]), paragraph("Derayan Bima Alamsyah", styles["TableCell"])],
        [paragraph("Dosen", styles["TableHead"]), paragraph("Undang Syaripudin, Ph.D., M.Kom.", styles["TableCell"])],
        [paragraph("Tanggal", styles["TableHead"]), paragraph("7 Oktober 2026", styles["TableCell"])],
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
        "<b>Ringkasan.</b> Tiga jenis T-test yang diminta telah diterapkan pada dataset yang tersedia di repository. One-sample dan independent test menolak hipotesis nol pada alpha = 0.05, sedangkan paired test tidak menolaknya. Semua kesimpulan hanya bersifat deskriptif untuk sampel sintetis ini.", styles["IdCallout"],
    )]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE), ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ])))
    story.append(PageBreak())

    story.append(paragraph("1. Dataset dan metode", styles["Section"]))
    story.append(paragraph(
        "Analisis menggunakan data/migration_tasks.csv dan data/migration_observations.csv. Setiap migration task memiliki lima eksekusi sintetis yang deterministik. Untuk pengujian berbasis waktu, lima eksekusi dirata-ratakan berdasarkan ticket_id terlebih dahulu sehingga unit analisisnya adalah task, bukan setiap pengulangan. Paired test mencocokkan akurasi Agent A dan Agent B berdasarkan ticket_id.", styles["Body"],
    ))
    story.append(paragraph(
        "Semua pengujian bersifat two-sided dengan alpha = 0.05. One-sample test membandingkan rata-rata execution time dengan referensi pengajaran 75 detik. Paired test menggunakan selisih akurasi Agent A dan Agent B. Independent comparison menggunakan Welch's t-test karena varians yang sama tidak diasumsikan. Effect size dan confidence interval 95% juga dihitung.", styles["Body"],
    ))
    story.append(Table([[paragraph(
        "Keterangan data sintetis: execution time, token usage, accuracy, pass rate, dan error count adalah metrik simulasi untuk pembelajaran. Nilai tersebut bukan pengukuran AI-agent nyata, benchmark Codex, pengukuran Android production, atau bukti performa umum.", styles["Body"],
    )]], colWidths=[174 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#C68A00")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])))

    story.append(paragraph("2. Hasil pengujian", styles["Section"]))
    story.append(paragraph("Ringkasan keputusan", styles["Subsection"]))
    result_rows = [["Pengujian", "Perbandingan", "n", "t", "df", "p-value", "Keputusan"]]
    for _, result in results.iterrows():
        if result["test_id"] == "one_sample_execution_time":
            comparison = "Semua task vs referensi 75 detik"
        elif result["test_id"] == "paired_agent_accuracy":
            comparison = "Akurasi Agent A vs Agent B"
        else:
            comparison = "Task sulit vs task mudah"
        result_rows.append([
            {"one_sample_execution_time": "One-sample T-test", "paired_agent_accuracy": "Paired-samples T-test", "independent_difficulty_time": "Independent Welch T-test"}[result["test_id"]],
            comparison, f"{int(result['n_a'])}", f"{result['t_statistic']:.3f}",
            f"{result['degrees_of_freedom']:.2f}", f"{result['p_value_two_sided']:.4g}",
            "Tolak H0" if result["decision_at_alpha_0_05"] == "Reject H0" else "Gagal menolak H0",
        ])
    story.append(make_table(result_rows, [38 * mm, 59 * mm, 12 * mm, 16 * mm, 17 * mm, 17 * mm, 25 * mm], styles, row_bgs=[colors.HexColor("#E8F5EC"), PALE, colors.HexColor("#E8F5EC")]))
    story.append(Spacer(1, 4 * mm))

    detail_rows = [["Pengujian", "Mean A", "Mean B/referensi", "Selisih", "95% CI selisih", "Effect size"]]
    for _, result in results.iterrows():
        detail_rows.append([
            {"one_sample_execution_time": "One-sample", "paired_agent_accuracy": "Paired", "independent_difficulty_time": "Independent Welch"}[result["test_id"]],
            f"{result['mean_a']:.3f}", f"{result['mean_b_or_reference']:.3f}", f"{result['mean_difference_a_minus_b']:.3f}",
            f"[{result['confidence_interval_low']:.3f}, {result['confidence_interval_high']:.3f}]",
            f"{result['effect_size_name']}: {result['effect_size']:.3f}",
        ])
    story.append(make_table(detail_rows, [38 * mm, 22 * mm, 28 * mm, 24 * mm, 39 * mm, 23 * mm], styles))
    story.append(paragraph("Interpretasi", styles["Subsection"]))
    story.append(paragraph(
        "<b>One-sample:</b> rata-rata execution time per task adalah 88.03 detik, atau 13.03 detik di atas referensi 75 detik. Nilai p two-sided = 0.0155, sehingga hipotesis nol ditolak pada alpha = 0.05.", styles["Body"]
    ))
    story.append(paragraph(
        "<b>Paired:</b> rata-rata akurasi Agent A adalah 0.906 dan Agent B adalah 0.901. Selisih rata-rata berpasangan adalah 0.0046 dengan p = 0.4282, sehingga belum ada cukup bukti untuk menolak hipotesis nol tentang selisih rata-rata nol.", styles["Body"]
    ))
    story.append(paragraph(
        "<b>Independent:</b> task sulit memiliki rata-rata waktu 130.75 detik, sedangkan task mudah 52.51 detik. Nilai p Welch = 7.80e-09, sehingga hipotesis nol tentang rata-rata yang sama ditolak. Hasil ini mencerminkan struktur kesulitan pada data sintetis, bukan benchmark production.", styles["Body"]
    ))

    story.append(paragraph("3. Kesimpulan dan reproduksibilitas", styles["Section"]))
    story.append(paragraph(
        "Tiga jenis T-test telah diselesaikan. Pada dataset sintetis ini, tingkat kesulitan task berasosiasi dengan execution time, sedangkan perbandingan akurasi agent yang berpasangan tidak menunjukkan perbedaan rata-rata yang signifikan. Kesimpulan ini hanya bersifat deskriptif dan tidak boleh digeneralisasi di luar sampel sintetis ini.", styles["Body"]
    ))
    story.append(paragraph("Reproduksi dari root repository: <font name='Courier'>python analysis/t_test_analysis.py</font>. Verifikasi: <font name='Courier'>python -m unittest discover -s tests -v</font>.", styles["Small"]))

    doc.build(story, onFirstPage=footer_id, onLaterPages=footer_id)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
