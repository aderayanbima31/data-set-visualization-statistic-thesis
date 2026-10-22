"""Membuat laporan PDF tugas korelasi dalam Bahasa Indonesia."""

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "outputs" / "correlation_results.csv"
OUTPUT = ROOT / "submission" / "laporan_korelasi_bahasa_indonesia.pdf"


def footer(canvas, document):
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D8DEE9"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, 9 * mm, "Analisis Korelasi | Dataset sintetis untuk pembelajaran")
    canvas.drawRightString(192 * mm, 9 * mm, f"Halaman {document.page}")
    canvas.restoreState()


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleBlue", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=24, leading=29, alignment=TA_CENTER,
        textColor=colors.HexColor("#1D4ED8"), spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"], fontSize=11, leading=16,
        alignment=TA_CENTER, textColor=colors.HexColor("#4B5563"), spaceAfter=22,
    ))
    styles.add(ParagraphStyle(
        name="Identity", parent=styles["Normal"], fontSize=10.5, leading=15,
        alignment=TA_CENTER, textColor=colors.HexColor("#4B5563"), spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="SectionBlue", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=13, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="BodyID", parent=styles["BodyText"], fontSize=10.2,
        leading=14.5, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="SmallID", parent=styles["BodyText"], fontSize=8.2,
        leading=10.5, textColor=colors.HexColor("#374151"),
    ))
    styles.add(ParagraphStyle(
        name="CalloutID", parent=styles["BodyText"], fontSize=9.7,
        leading=13.5, leftIndent=8, rightIndent=8, spaceBefore=5, spaceAfter=8,
        textColor=colors.HexColor("#1F2937"),
    ))
    return styles


def text(value: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(value, style)


def p_value(value: float) -> str:
    return "<0,001" if value < 0.001 else f"{value:.4f}".replace(".", ",")


def coefficient(value: float) -> str:
    return f"{value:.4f}".replace(".", ",")


def main():
    results = pd.read_csv(RESULTS)
    by_method = {row["method"]: row for row in results.to_dict("records")}
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="Analisis Hubungan dan Korelasi",
        author="Derayan Bima A",
    )
    story = [
        Spacer(1, 18 * mm),
        text("Analisis Hubungan & Korelasi", styles["TitleBlue"]),
        text("Nama: Derayan Bima A", styles["Identity"]),
        text("Dosen Pengampu: Undang Syaripudin, Ph.D., M.Kom.", styles["Identity"]),
        Spacer(1, 12),
        text("1. Tujuan dan data", styles["SectionBlue"]),
        text(
            "Laporan ini menyelesaikan lima metode korelasi yang diminta dalam tugas: Point-Biserial, Koefisien Kontingensi, Phi, Spearman Rank, dan Product Moment Pearson.",
            styles["BodyID"],
        ),
        text(
            "Dataset terdiri dari 36 task migrasi UI dan beberapa observasi eksekusi untuk setiap task. Agar satu task tidak dihitung berkali-kali sebagai observasi independen, nilai numerik dirata-ratakan berdasarkan <b>ticket_id</b> sebelum analisis hubungan dilakukan.",
            styles["BodyID"],
        ),
        text(
            "Catatan penting: execution time, token usage, accuracy score, test pass rate, dan error count merupakan data sintetis untuk pembelajaran. Hasil tidak boleh dianggap sebagai performa AI nyata, benchmark Codex, atau performa produksi.",
            styles["CalloutID"],
        ),
        text("2. Ringkasan hasil", styles["SectionBlue"]),
    ]

    header = ["Metode", "Variabel yang diuji", "n", "Koefisien", "p-value", "Keputusan"]
    rows = [[text(item, styles["SmallID"]) for item in header]]
    for row in results.to_dict("records"):
        rows.append([
            text(str(row["method"]), styles["SmallID"]),
            text(str(row["variables"]), styles["SmallID"]),
            text(str(int(row["n"])), styles["SmallID"]),
            text(coefficient(row["coefficient"]), styles["SmallID"]),
            text(p_value(row["p_value"]), styles["SmallID"]),
            text("Signifikan" if row["p_value"] < 0.05 else "Tidak signifikan", styles["SmallID"]),
        ])
    table = Table(rows, colWidths=[31 * mm, 58 * mm, 10 * mm, 21 * mm, 18 * mm, 31 * mm], repeatRows=1)
    table.setStyle(TableStyle([
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
    story.append(table)

    story.extend([
        PageBreak(),
        text("3. Penjelasan cara kerja setiap metode", styles["SectionBlue"]),
        text(
            "<b>A. Korelasi Point-Biserial</b><br/><b>Kapan digunakan:</b> satu variabel kategorikal nominal dengan tepat dua kategori dan satu variabel numerik kontinu.<br/><b>Cara kerja:</b> data kategori diubah menjadi kode 0 dan 1. Kemudian rata-rata variabel numerik pada kelompok 0 dan kelompok 1 dibandingkan, lalu perbedaan tersebut disesuaikan dengan simpangan baku dan proporsi kedua kelompok.<br/><b>Rumus:</b> r_pb = ((M1 - M0) / s_y) x akar(pq).<br/><b>Penerapan:</b> Easy versus Hard dibandingkan dengan rata-rata execution time. Koefisien = <b>" + coefficient(by_method["Point-Biserial"]["coefficient"]) + "</b>, p-value = <b>" + p_value(by_method["Point-Biserial"]["p_value"]) + "</b>. Hard task memiliki waktu rata-rata 130,75 detik, sedangkan Easy task 52,51 detik. Hubungan sangat kuat dan signifikan pada sampel sintetis ini.",
            styles["BodyID"],
        ),
        text(
            "<b>B. Korelasi Kontingensi (CC)</b><br/><b>Kapan digunakan:</b> dua variabel kategorikal dengan dua kategori atau lebih. Metode ini memakai tabel kontingensi dan statistik chi-square.<br/><b>Cara kerja:</b> frekuensi aktual setiap kombinasi kategori dibandingkan dengan frekuensi harapan. Nilai chi-square kemudian diubah menjadi koefisien CC.<br/><b>Rumus:</b> CC = akar(chi-square / (chi-square + N)).<br/><b>Penerapan:</b> component_area dibandingkan dengan difficulty. Koefisien = <b>" + coefficient(by_method["Contingency Coefficient (CC)"]["coefficient"]) + "</b>, p-value = <b>" + p_value(by_method["Contingency Coefficient (CC)"]["p_value"]) + "</b>. Hubungan tidak signifikan.",
            styles["BodyID"],
        ),
        text(
            "<b>C. Korelasi Phi</b><br/><b>Kapan digunakan:</b> dua variabel kategorikal yang masing-masing hanya memiliki dua kategori, sehingga membentuk tabel 2 x 2.<br/><b>Cara kerja:</b> empat frekuensi sel tabel 2 x 2 digunakan untuk membandingkan pola kemunculan kedua variabel. Nilai Phi juga berkaitan langsung dengan chi-square pada tabel 2 x 2.<br/><b>Rumus:</b> phi = (ad - bc) / akar((a+b)(c+d)(a+c)(b+d)).<br/><b>Penerapan:</b> is_hard dibandingkan dengan has_error. Koefisien = <b>" + coefficient(by_method["Phi (phi)"]["coefficient"]) + "</b>, p-value = <b>" + p_value(by_method["Phi (phi)"]["p_value"]) + "</b>. Hubungan lemah dan tidak signifikan.",
            styles["BodyID"],
        ),
    ])

    story.extend([
        PageBreak(),
        text("3. Penjelasan cara kerja setiap metode (lanjutan)", styles["SectionBlue"]),
        text(
            "<b>D. Korelasi Spearman Rank</b><br/><b>Kapan digunakan:</b> dua variabel ordinal atau hubungan yang ingin dinilai berdasarkan urutan/ranking. Metode ini tidak menuntut hubungan linear dan lebih fleksibel terhadap outlier dibanding Pearson.<br/><b>Cara kerja:</b> setiap nilai diubah menjadi ranking. Selisih ranking untuk setiap pasangan dihitung, dikuadratkan, lalu dijumlahkan. Semakin konsisten urutan kedua variabel, semakin besar nilai rho.<br/><b>Rumus:</b> rho = 1 - 6 jumlah(d^2) / (n(n^2 - 1)).<br/><b>Penerapan:</b> difficulty diubah menjadi Easy=1, Medium=2, Hard=3 dan dibandingkan dengan execution time. Koefisien = <b>" + coefficient(by_method["Spearman Rank"]["coefficient"]) + "</b>, p-value = <b>" + p_value(by_method["Spearman Rank"]["p_value"]) + "</b>. Terdapat hubungan positif yang sangat kuat dan signifikan.",
            styles["BodyID"],
        ),
        text(
            "<b>E. Korelasi Product Moment Pearson</b><br/><b>Kapan digunakan:</b> dua variabel numerik kontinu dengan fokus pada hubungan linear.<br/><b>Cara kerja:</b> setiap nilai dibandingkan dengan rata-ratanya untuk memperoleh kovarians. Kovarians tersebut dibagi dengan perkalian simpangan baku kedua variabel, sehingga koefisien berada pada rentang -1 sampai +1.<br/><b>Penerapan:</b> mean execution time dibandingkan dengan mean token usage. Koefisien = <b>" + coefficient(by_method["Pearson Product-Moment"]["coefficient"]) + "</b>, p-value = <b>" + p_value(by_method["Pearson Product-Moment"]["p_value"]) + "</b>. Hubungan linear positif sangat kuat dan signifikan.",
            styles["BodyID"],
        ),
        text("4. Pemilihan metode yang tepat", styles["SectionBlue"]),
    ])

    selection_rows = [
        [text("Jenis variabel", styles["SmallID"]), text("Metode yang sesuai", styles["SmallID"]), text("Contoh pada dataset", styles["SmallID"])],
        [text("Biner + numerik", styles["SmallID"]), text("Point-Biserial", styles["SmallID"]), text("Easy/Hard + execution time", styles["SmallID"])],
        [text("Kategorikal multi-kategori", styles["SmallID"]), text("Contingency Coefficient", styles["SmallID"]), text("component_area + difficulty", styles["SmallID"])],
        [text("Biner + biner", styles["SmallID"]), text("Phi", styles["SmallID"]), text("is_hard + has_error", styles["SmallID"])],
        [text("Ordinal atau hubungan monotonik", styles["SmallID"]), text("Spearman Rank", styles["SmallID"]), text("difficulty rank + execution time", styles["SmallID"])],
        [text("Numerik kontinu + numerik kontinu", styles["SmallID"]), text("Pearson", styles["SmallID"]), text("execution time + token usage", styles["SmallID"])],
    ]
    selection_table = Table(selection_rows, colWidths=[49 * mm, 42 * mm, 79 * mm], repeatRows=1)
    selection_table.setStyle(TableStyle([
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
    story.extend([
        selection_table,
        Spacer(1, 8),
        text("5. Kesimpulan akhir", styles["SectionBlue"]),
        text(
            "Tidak ada satu metode korelasi yang selalu paling baik. Pemilihannya harus mengikuti skala pengukuran variabel. Pada dataset ini, Pearson paling tepat untuk dua metrik kontinu seperti execution time dan token usage. Spearman tepat untuk difficulty yang bersifat berurutan. Contingency Coefficient tepat untuk variabel kategorikal dengan banyak kategori. Phi hanya digunakan untuk dua variabel biner, sedangkan Point-Biserial digunakan untuk satu variabel biner dan satu variabel numerik. Semua interpretasi dibatasi pada dataset sintetis yang dianalisis.",
            styles["BodyID"],
        ),
        text("Laporan ini dibuat dari script reproducible <b>analysis/correlation_analysis.py</b>. Hasil numerik lengkap tersedia dalam file CSV pendamping.", styles["SmallID"]),
    ])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
