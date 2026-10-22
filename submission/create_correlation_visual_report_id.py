"""Membuat versi visual PDF laporan korelasi berbahasa Indonesia."""

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
OUTPUT = ROOT / "submission" / "laporan_korelasi_visual_bahasa_indonesia.pdf"


BLUE = colors.HexColor("#1D4ED8")
LIGHT_BLUE = colors.HexColor("#DBEAFE")
PALE_BLUE = colors.HexColor("#EFF6FF")
TEXT = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#4B5563")
GRID = colors.HexColor("#CBD5E1")


def footer(canvas, document):
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D8DEE9"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, 9 * mm, "Analisis Korelasi | Visualisasi rumus dan langkah perhitungan")
    canvas.drawRightString(192 * mm, 9 * mm, f"Halaman {document.page}")
    canvas.restoreState()


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="TitleBlue", parent=s["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, alignment=TA_CENTER, textColor=BLUE, spaceAfter=8))
    s.add(ParagraphStyle(name="Subtitle", parent=s["Normal"], fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=MUTED, spaceAfter=18))
    s.add(ParagraphStyle(name="H1Blue", parent=s["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=BLUE, spaceAfter=8))
    s.add(ParagraphStyle(name="H2Blue", parent=s["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=BLUE, spaceBefore=8, spaceAfter=6))
    s.add(ParagraphStyle(name="BodyID", parent=s["BodyText"], fontSize=9.6, leading=13.3, textColor=TEXT, spaceAfter=5))
    s.add(ParagraphStyle(name="SmallID", parent=s["BodyText"], fontSize=7.8, leading=10, textColor=TEXT))
    s.add(ParagraphStyle(name="Flow", parent=s["BodyText"], fontName="Helvetica-Bold", fontSize=7.4, leading=9, alignment=TA_CENTER, textColor=TEXT))
    s.add(ParagraphStyle(name="Formula", parent=s["BodyText"], fontName="Helvetica-Bold", fontSize=13, leading=17, alignment=TA_CENTER, textColor=BLUE))
    s.add(ParagraphStyle(name="Callout", parent=s["BodyText"], fontSize=9.3, leading=12.8, textColor=TEXT, leftIndent=7, rightIndent=7))
    return s


def P(value, style):
    return Paragraph(value, style)


def pval(value):
    return "&lt;0,001" if value < 0.001 else f"{value:.4f}".replace(".", ",")


def coef(value):
    return f"{value:.4f}".replace(".", ",")


def card(content, style, width=32 * mm, background=PALE_BLUE):
    t = Table([[P(content, style)]], colWidths=[width], rowHeights=[18 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def flow(items, s):
    cells = []
    for index, item in enumerate(items):
        cells.append(card(item, s["Flow"], 30 * mm, LIGHT_BLUE if index % 2 == 0 else PALE_BLUE))
        if index < len(items) - 1:
            cells.append(P(">", s["H2Blue"]))
    widths = []
    for index in range(len(cells)):
        widths.append(30 * mm if index % 2 == 0 else 5 * mm)
    t = Table([cells], colWidths=widths)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return t


def formula_box(formula, meaning, s):
    t = Table([[P(formula, s["Formula"])], [P("<b>Makna rumus:</b> " + meaning, s["Callout"])]], colWidths=[174 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("BACKGROUND", (0, 1), (-1, 1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def info_table(rows, s):
    data = [[P(str(a), s["SmallID"]), P(str(b), s["SmallID"])] for a, b in rows]
    t = Table(data, colWidths=[38 * mm, 136 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def method_page(story, title, subtitle, rows, flow_items, formula, meaning, steps, result, s, extra=None):
    story.append(PageBreak())
    story.extend([P(title, s["H1Blue"]), P(subtitle, s["BodyID"]), info_table(rows, s), Spacer(1, 6), P("Visual alur perhitungan", s["H2Blue"]), flow(flow_items, s), Spacer(1, 8), formula_box(formula, meaning, s), Spacer(1, 8), P("Langkah menghitung", s["H2Blue"])])
    for number, step in enumerate(steps, 1):
        story.append(P(f"<b>{number}.</b> {step}", s["BodyID"]))
    if extra is not None:
        story.extend([Spacer(1, 4), extra])
    story.extend([Spacer(1, 5), P("Hasil pada dataset", s["H2Blue"]), Table([[P(result, s["Callout"])]], colWidths=[174 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#10B981")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))])


def main():
    s = styles()
    results = {row["method"]: row for row in pd.read_csv(RESULTS).to_dict("records")}
    story = [
        Spacer(1, 13 * mm),
        P("Visualisasi Perhitungan Korelasi", s["TitleBlue"]),
        P("Laporan tugas - Bahasa Indonesia", s["Subtitle"]),
        P("Tujuan visual", s["H2Blue"]),
        P("Dokumen ini menjelaskan bukan hanya kapan setiap metode digunakan, tetapi juga bagaimana data bergerak dari tipe variabel, tabel atau ranking, rumus, sampai interpretasi koefisien.", s["BodyID"]),
        P("Semua nilai numerik berasal dari dataset sintetis. Observasi berulang dirata-ratakan berdasarkan ticket_id sehingga unit analisis untuk metrik eksekusi adalah satu task.", s["Callout"]),
        P("Peta pemilihan metode", s["H2Blue"]),
        flow(["Tentukan tipe\nvariabel", "Pilih metode\nyang sesuai", "Hitung\nkoefisien", "Baca arah\ndan kekuatan", "Uji\nsignifikansi"], s),
        Spacer(1, 10),
        info_table([
            ("Biner + numerik", "Point-Biserial"),
            ("Kategori multi-level", "Koefisien Kontingensi"),
            ("Biner + biner", "Phi"),
            ("Ordinal / ranking", "Spearman Rank"),
            ("Numerik kontinu + kontinu", "Pearson Product Moment"),
        ], s),
        P("Skala umum koefisien", s["H2Blue"]),
        flow(["-1\nberlawanan sempurna", "0\ntidak ada hubungan linear", "+1\nsearah sempurna"], s),
    ]

    method_page(story, "1. Korelasi Point-Biserial", "Membandingkan kelompok biner dengan variabel numerik.", [
        ("Tipe X", "Nominal dikotomis: Easy / Hard"), ("Tipe Y", "Numerik kontinu: execution_time_sec"), ("Dataset", "17 task Easy dan Hard"),
    ], ["Easy / Hard", "Kode 0 / 1", "Hitung M0\ndan M1", "Masukkan\nke rumus", "r_pb"],
        "r_pb = ((M1 - M0) / s_y) x akar(pq)", "M1 dan M0 adalah rata-rata Y pada dua kelompok; s_y adalah simpangan baku Y; p dan q adalah proporsi kelompok.", [
            "Ubah kategori Easy dan Hard menjadi kode biner, misalnya Easy=0 dan Hard=1.",
            "Hitung rata-rata execution time untuk masing-masing kelompok: M0 dan M1.",
            "Hitung simpangan baku seluruh execution time serta proporsi p dan q.",
            "Substitusikan semua komponen ke rumus. Tanda koefisien menunjukkan arah hubungan; nilai absolut mendekati 1 berarti hubungan kuat.",
        ],
        f"r_pb = <b>{coef(results['Point-Biserial']['coefficient'])}</b>, p-value = <b>{pval(results['Point-Biserial']['p_value'])}</b>. Rata-rata Easy = 52,51 detik dan Hard = 130,75 detik. Hubungan sangat kuat dan signifikan pada sampel sintetis.", s)

    cc_table = Table([[P("component_area", s["SmallID"]), P("difficulty", s["SmallID"])], [P("App Bar, Balance, ...", s["SmallID"]), P("Easy, Medium, Hard", s["SmallID"])]] , colWidths=[87 * mm, 87 * mm])
    cc_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE), ("GRID", (0, 0), (-1, -1), 0.35, GRID), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    method_page(story, "2. Koefisien Kontingensi (CC)", "Mengukur hubungan antara dua variabel kategorikal.", [
        ("Tipe X", "Kategorikal: component_area"), ("Tipe Y", "Kategorikal: difficulty"), ("Dataset", "36 task pada katalog"),
    ], ["Kategori X", "Kategori Y", "Buat tabel\nkontingensi", "Hitung\nchi-square", "CC"],
        "CC = akar(chi-square / (chi-square + N))", "chi-square mengukur perbedaan antara frekuensi aktual dan frekuensi harapan; N adalah jumlah seluruh observasi.", [
            "Susun baris dan kolom berdasarkan kategori kedua variabel.",
            "Isi setiap sel dengan jumlah task pada kombinasi kategori tersebut.",
            "Hitung frekuensi harapan dan chi-square.",
            "Masukkan chi-square dan N ke rumus CC. Koefisien CC tidak memiliki arah positif/negatif seperti Pearson.",
        ], f"CC = <b>{coef(results['Contingency Coefficient (CC)']['coefficient'])}</b>, p-value = <b>{pval(results['Contingency Coefficient (CC)']['p_value'])}</b>. Hubungan component_area dan difficulty tidak signifikan.", s, cc_table)

    phi_table = Table([[P("", s["SmallID"]), P("Tanpa error", s["SmallID"]), P("Ada error", s["SmallID"])], [P("Non-Hard", s["SmallID"]), P("3", s["SmallID"]), P("23", s["SmallID"])], [P("Hard", s["SmallID"]), P("0", s["SmallID"]), P("10", s["SmallID"])]], colWidths=[42 * mm, 66 * mm, 66 * mm])
    phi_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE), ("BACKGROUND", (0, 1), (0, -1), PALE_BLUE), ("GRID", (0, 0), (-1, -1), 0.35, GRID), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    method_page(story, "3. Korelasi Phi", "Khusus untuk dua variabel biner dengan tabel 2 x 2.", [
        ("Tipe X", "Biner: Hard / Non-Hard"), ("Tipe Y", "Biner: Ada error / Tanpa error"), ("Dataset", "36 task setelah agregasi"),
    ], ["Biner X", "Biner Y", "Tabel 2 x 2", "Hitung\nad - bc", "Phi"],
        "phi = (ad - bc) / akar((a+b)(c+d)(a+c)(b+d))", "a, b, c, dan d adalah empat frekuensi pada tabel 2 x 2. Nilai absolut mendekati 1 menunjukkan hubungan biner yang kuat.", [
            "Pastikan kedua variabel hanya memiliki dua kategori.",
            "Buat tabel 2 x 2 dan isi empat frekuensi a, b, c, d.",
            "Hitung pembilang ad-bc dan penyebut dari total marginal tabel.",
            "Bagi pembilang dengan penyebut untuk memperoleh Phi, lalu evaluasi p-value dari chi-square.",
        ], f"phi = <b>{coef(results['Phi (phi)']['coefficient'])}</b>, p-value = <b>{pval(results['Phi (phi)']['p_value'])}</b>. Hubungan Hard/Non-Hard dengan keberadaan error lemah dan tidak signifikan.", s, phi_table)

    rank_table = Table([[P("Difficulty", s["SmallID"]), P("Ranking", s["SmallID"]), P("Contoh d", s["SmallID"])], [P("Easy", s["SmallID"]), P("1", s["SmallID"]), P("rank X - rank Y", s["SmallID"])], [P("Medium", s["SmallID"]), P("2", s["SmallID"]), P("d lalu d^2", s["SmallID"])], [P("Hard", s["SmallID"]), P("3", s["SmallID"]), P("jumlahkan semua d^2", s["SmallID"])]], colWidths=[52 * mm, 35 * mm, 87 * mm])
    rank_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE), ("GRID", (0, 0), (-1, -1), 0.35, GRID), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    method_page(story, "4. Korelasi Spearman Rank", "Mengukur hubungan berdasarkan urutan atau ranking.", [
        ("Tipe X", "Ordinal: Easy < Medium < Hard"), ("Tipe Y", "Numerik yang dapat diurutkan"), ("Dataset", "Difficulty dan execution time"),
    ], ["Nilai asli", "Ubah ke\nranking", "Hitung\nselisih d", "Kuadratkan\nd^2", "rho"],
        "rho = 1 - 6 jumlah(d^2) / (n(n^2 - 1))", "d adalah selisih ranking setiap pasangan; n adalah jumlah pasangan observasi. Pada data dengan ties, perangkat lunak memakai average rank.", [
            "Ubah nilai setiap variabel menjadi ranking.",
            "Pasangkan ranking X dan ranking Y untuk setiap task.",
            "Hitung d, kuadratkan menjadi d^2, lalu jumlahkan seluruh d^2.",
            "Gunakan rumus rho. Nilai positif tinggi berarti task yang lebih sulit cenderung memiliki execution time lebih tinggi.",
        ], f"rho = <b>{coef(results['Spearman Rank']['coefficient'])}</b>, p-value = <b>{pval(results['Spearman Rank']['p_value'])}</b>. Hubungan difficulty rank dan execution time sangat kuat serta signifikan.", s, rank_table)

    pearson_table = Table([[P("X", s["SmallID"]), P("Y", s["SmallID"]), P("Tujuan", s["SmallID"])], [P("execution_time_sec", s["SmallID"]), P("token_usage", s["SmallID"]), P("Menguji pola linear", s["SmallID"])], [P("Numerik kontinu", s["SmallID"]), P("Numerik kontinu", s["SmallID"]), P("Satu task = satu titik", s["SmallID"])]], colWidths=[62 * mm, 62 * mm, 50 * mm])
    pearson_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE), ("GRID", (0, 0), (-1, -1), 0.35, GRID), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    method_page(story, "5. Korelasi Product Moment Pearson", "Mengukur kekuatan dan arah hubungan linear dua variabel numerik.", [
        ("Tipe X", "Numerik kontinu: execution time"), ("Tipe Y", "Numerik kontinu: token usage"), ("Dataset", "36 rata-rata task"),
    ], ["X dan Y", "Kurangi\nrata-rata", "Hitung\nkovarians", "Bagi dengan\nsimpangan baku", "r"],
        "r = kovarians(X,Y) / (s_x x s_y)", "Kovarians menunjukkan apakah X dan Y bergerak bersama; s_x dan s_y menormalisasi skala agar koefisien berada dari -1 sampai +1.", [
            "Hitung rata-rata X dan Y.",
            "Untuk setiap task, hitung deviasi X dari rata-ratanya dan deviasi Y dari rata-ratanya.",
            "Kalikan deviasi berpasangan untuk memperoleh kovarians.",
            "Bagi kovarians dengan perkalian simpangan baku X dan Y. Nilai positif berarti keduanya cenderung naik bersama.",
        ], f"r = <b>{coef(results['Pearson Product-Moment']['coefficient'])}</b>, p-value = <b>{pval(results['Pearson Product-Moment']['p_value'])}</b>. Execution time dan token usage memiliki hubungan linear positif yang sangat kuat dan signifikan.", s, pearson_table)

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm, title="Visualisasi Perhitungan Korelasi", author="Derayan Bima A")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
