# PlantVision AI — Klasifikasi Penyakit Tanaman dengan CNN (Sesi 2)

## 1. Identitas Proyek

| Item | Keterangan |
|---|---|
| Nama Proyek | PlantVision AI |
| Sesi | 2 dari 6 |
| Judul Penelitian | Deteksi Penyakit Daun Tanaman Menggunakan Deep Learning untuk Mendukung Pertanian Presisi |
| Jenis | Klasifikasi citra multi-kelas (38 kelas) |

## 2. Latar Belakang

Petani sering terlambat mengenali penyakit daun sehingga penanganan menjadi tidak
efektif. Teknologi deep learning pada citra dapat membantu identifikasi dini. Proyek ini
menerapkan CNN ringan untuk mengklasifikasikan daun sehat dan berpenyakit pada dataset
PlantVillage, serta menyediakan penjelasan (Explainable AI) melalui Grad-CAM.

## 3. Tujuan

1. Menyediakan pipeline dataset daun berlabel (ImageFolder).
2. Melatih CNN dengan augmentasi data.
3. Mengklasifikasikan daun sehat dan penyakit pada kelas yang tersedia.
4. Memprediksi satu maupun beberapa citra.
5. Menampilkan confusion matrix dan metrik (accuracy, precision, recall, F1).
6. Menyediakan Grad-CAM sebagai penjelasan prediksi.

## 4. Teknologi

Python, PyTorch, torchvision, NumPy, Pandas, Pillow, Streamlit, Plotly, scikit-learn,
Matplotlib, pytest.

## 5. Sumber Dataset

- **PlantVillage** (spMohanty/PlantVillage-Dataset, lisensi terbuka untuk riset).
  Subset kecil (24 train / 6 val / 6 test per kelas) diunduh otomatis.
- Bila tidak ada internet, pipeline membuat **dataset sintetik** prosedural sebagai
  fallback agar aplikasi tetap berfungsi offline.

> **Catatan penting:** model **tidak** dapat mendeteksi semua penyakit secara universal.
> Keterbatasan kondisi pencahayaan, latar belakang, jenis tanaman, dan kualitas citra
> sangat memengaruhi hasil. Model hanya mengenali kelas yang ada pada dataset pelatihan.

## 6. Struktur Folder

```
Sesi-2-Plant-Disease-Classification/
├── app.py                     # Antarmuka Streamlit
├── train.py                   # Pelatihan & evaluasi
├── requirements.txt
├── src/
│   ├── model.py               # Arsitektur CNN ringan
│   ├── training.py            # Loader, training, evaluasi, prediksi, Grad-CAM
│   ├── dataset_pipeline.py    # Unduh/buat dataset daun
│   └── knowledge.py           # Basis pengetahuan 38 kelas
├── scripts/prepare_dataset.py
├── tests/
├── data/dataset/{train,val,test}/
├── models/                    # model_cnn.pt + metadata.json
└── outputs/
```

## 7. Instalasi

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 8. Cara Menjalankan

```bash
python scripts/prepare_dataset.py   # unduh/siapkan dataset
python train.py                     # latih model
streamlit run app.py                # jalankan antarmuka
```

## 9. Cara Melatih Model

`python train.py` melatih CNN (Adam + CrossEntropy + early stopping) dan menyimpan
`models/model_cnn.pt` beserta `metadata.json`. Jika GPU tidak tersedia, gunakan mode CPU
(default) dengan konfigurasi ringan (batch 32, input 128x128).

## 10. Cara Evaluasi

Metrik dihitung dari confusion matrix pada data uji: accuracy, precision/recall/F1 macro.
Hasil tercatat di `metadata.json` dan dapat dilihat di dashboard aplikasi.

## 11. Contoh Hasil

Metadata model terlatih (dataset PlantVillage, 38 kelas):

| Metrik | Nilai |
|---|---|
| Akurasi train | 0.786 |
| Akurasi validasi | 0.759 |
| Akurasi test | 0.763 |

## 12. Keterbatasan

- Jumlah gambar per kelas kecil (subset), sehingga akurasi belum maksimal.
- Sensitif terhadap pencahayaan, latar belakang, dan kualitas citra.
- Hanya mengenali kelas pada dataset; tidak generalisasi ke tanaman/penyakit lain.

## 13. Pengujian

```bash
python -m pytest tests -q
```

## 14. Referensi

- PlantVillage Dataset (Hughes & Salathé, 2015).
- MobileNet (Howard et al., 2017) — inspirasi arsitektur depthwise separable.
- Grad-CAM (Selvaraju et al., 2017).
