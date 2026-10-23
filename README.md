# Statistics for Data Science — Migration Analysis

Repository ini berisi analisis statistik terhadap metrik sintetis pada skenario migrasi UI Android e-wallet dari komponen legacy menuju Material 3.

## Tujuan project

Project ini menggabungkan empat metode analisis statistik dalam satu notebook:

1. Analisis deskriptif.
2. Korelasi Pearson.
3. Welch independent-samples t-test.
4. Uji non-parametrik Mann–Whitney U.

Analisis dilakukan secara reproducible menggunakan Python, pandas, NumPy, SciPy, dan Matplotlib.

> **Catatan penting:** `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, dan `error_count` adalah metrik sintetis untuk pembelajaran statistik. Nilai tersebut bukan hasil eksekusi AI/Codex yang sebenarnya, bukan benchmark produksi, dan tidak digunakan untuk klaim kausal atau generalisasi ke populasi lain.

## Dataset

Dataset terdiri dari dua file utama:

- `data/migration_tasks.csv` — katalog task migration, satu baris untuk setiap task.
- `data/migration_observations.csv` — catatan execution observation sintetis.

Ringkasan dataset:

- 36 migration tasks.
- 180 execution observations.
- Setiap task memiliki 5 observations.
- `ticket_id` mengidentifikasi task dan dapat muncul beberapa kali.
- `observation_id` mengidentifikasi setiap catatan observasi secara unik.
- Variabel kategorikal: `component_area`, `migration_category`, `difficulty`, `agent_id`, dan `status`.
- Variabel numerik: `execution_time_sec`, `token_usage`, `accuracy_score`, `test_pass_rate`, dan `error_count`.

## Metodologi dan hasil utama

### 1. Analisis deskriptif

Analisis dilakukan pada 180 observations dan mencakup mean, median, mode, standard deviation, variance, kuartil, IQR, frequency, percentage, histogram, boxplot, dan potential outlier dengan aturan 1.5 × IQR.

### 2. Korelasi Pearson

Korelasi menguji hubungan linear antara rata-rata `execution_time_sec` dan rata-rata `token_usage` pada tingkat task. Observasi per task dirata-ratakan sehingga unit analisisnya adalah 36 task.

- `n = 36 task`
- `r = 0.961`
- `p-value = 1.64 × 10^-20`
- Kesimpulan: terdapat asosiasi linear positif yang sangat kuat dan signifikan pada sampel sintetis ini.

### 3. Welch independent-samples t-test

Uji ini membandingkan rata-rata execution time task `Hard` dan `Easy` tanpa mengasumsikan variance kedua kelompok sama.

- Hard: `n = 10`, mean `130.752` detik.
- Easy: `n = 7`, mean `52.506` detik.
- Selisih mean: `78.246` detik.
- `t = 14.002`, `df = 12.089`.
- `p-value = 7.80 × 10^-9`.
- Keputusan: reject H0 pada `alpha = 0.05`.

### 4. Mann–Whitney U

Uji ini membandingkan distribusi execution time task `Hard` dan `Easy` secara non-parametrik.

- Median Hard: `125.530` detik.
- Median Easy: `49.980` detik.
- `U = 70.000`.
- `p-value = 0.000103`.
- Keputusan: reject H0 pada `alpha = 0.05`.

## Struktur repository

```text
.
├── analysis/
│   ├── descriptive_statistics.ipynb
│   ├── uts_combined_analysis.ipynb
│   ├── correlation_analysis.py
│   ├── non_parametric_analysis.py
│   ├── t_test_analysis.py
│   └── generate_synthetic_data.py
├── data/
│   ├── migration_tasks.csv
│   └── migration_observations.csv
├── documentation-plan/docs/
├── outputs/
├── submission/
├── tests/
├── requirements.txt
└── README.md
```

## Menjalankan project

### Membuat virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Menjalankan notebook

```bash
source .venv/bin/activate
./.venv/bin/python -m jupyter lab
```

Kemudian buka `analysis/uts_combined_analysis.ipynb`. Notebook juga dapat dibuka melalui PyCharm dengan interpreter project `.venv`.

Untuk mengeksekusi seluruh cell dari terminal dan menyimpan output ke notebook:

```bash
./.venv/bin/python -m jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace analysis/uts_combined_analysis.ipynb \
  --ExecutePreprocessor.timeout=300
```

Dataset sintetis dapat dibuat ulang dengan seed deterministik:

```bash
./.venv/bin/python analysis/generate_synthetic_data.py
```

Raw CSV di folder `data/` tidak dimodifikasi oleh proses analisis. Ringkasan dan visualisasi ditulis ke folder `outputs/`.

## Output utama

- `uts_descriptive_summary.csv` — statistik deskriptif numerik.
- `uts_categorical_frequencies.csv` — jumlah dan persentase kategori.
- `uts_inferential_summary.csv` — ringkasan hasil Pearson, Welch t-test, dan Mann–Whitney U.
- `uts_outliers.csv` — potential outlier berdasarkan aturan 1.5 × IQR.
- `uts_numeric_histograms.png` — distribusi variabel numerik.
- `uts_numeric_boxplots.png` — median, IQR, dan potential outlier.
- `uts_pearson_time_vs_tokens.png` — visualisasi korelasi Pearson.
- `uts_welch_ttest_mean_comparison.png` — perbandingan mean Easy dan Hard.
- `uts_mann_whitney_distribution.png` — perbandingan distribusi Easy dan Hard.

Kesimpulan analisis hanya berlaku untuk dataset sintetis yang digunakan dalam project ini. Hasil statistik menunjukkan pola pada sampel pembelajaran, bukan hubungan sebab-akibat atau performa produksi.
