"""PlantVision AI - Antarmuka Streamlit (Sesi 2).

Aplikasi untuk:
- Upload citra daun (satu atau beberapa).
- Klasifikasi penyakit/status daun menggunakan CNN.
- Menampilkan confidence, top-3, penjelasan penyakit, dan Grad-CAM.
- Dashboard distribusi kelas dataset.
- Ekspor hasil prediksi.

Jalankan:
    streamlit run app.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src import knowledge  # noqa: E402
from src.training import grad_cam, muat_model, prediksi  # noqa: E402

DATASET_DIR = ROOT / "data" / "dataset"
MODEL_PATH = ROOT / "models" / "model_cnn.pt"
METADATA_PATH = ROOT / "models" / "metadata.json"

st.set_page_config(page_title="PlantVision AI", page_icon="🌿", layout="wide")


def _model_available() -> bool:
    return MODEL_PATH.exists()


def render_predict_single(image: Image.Image) -> None:
    result = prediksi(image, n_top=3)
    if result is None:
        st.warning("Model belum tersedia. Jalankan `python train.py` terlebih dahulu.")
        return

    top = result["top"][0]
    info = knowledge.cari_kelas(top["kelas"])
    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.image(image, caption="Citra masukan", use_container_width=True)
    with col2:
        st.markdown(f"### {top['tanaman']} — {top['penyakit']}")
        st.metric("Confidence", f"{top['confidence']:.1%}")
        kategori = info.get("kategori", "tidak diketahui")
        risiko = info.get("risiko", "tidak diketahui")
        c1, c2 = st.columns(2)
        c1.metric("Kategori", kategori.capitalize())
        c2.metric("Tingkat Risiko", risiko.capitalize())

    st.markdown("**Top-3 Prediksi**")
    df_top = pd.DataFrame(result["top"])
    df_top["confidence_persen"] = df_top["confidence"] * 100
    fig = px.bar(
        df_top,
        x="confidence_persen",
        y="kelas",
        orientation="h",
        labels={"confidence_persen": "Confidence (%)", "kelas": "Kelas"},
    )
    st.plotly_chart(fig, use_container_width=True)

    if info:
        with st.expander("Penjelasan & Penanganan", expanded=True):
            for label, key in [
                ("Gejala", "gejala"),
                ("Penyebab", "penyebab"),
                ("Penanganan", "penanganan"),
                ("Pencegahan", "pencegahan"),
            ]:
                value = info.get(key)
                if value:
                    st.markdown(f"**{label}:** {value}")

    if _model_available():
        with st.expander("Grad-CAM (bagian citra yang memengaruhi prediksi)"):
            _, _, kelas = muat_model()
            idx = kelas.index(top["kelas"]) if kelas and top["kelas"] in kelas else 0
            overlay, _, persen = grad_cam(image, idx)
            if overlay is not None:
                st.image(overlay, caption=f"Area aktif: {persen:.1f}%", use_container_width=True)


def render_predict_multi(images: list[Image.Image]) -> None:
    rows = []
    progress = st.progress(0.0)
    for i, img in enumerate(images, 1):
        result = prediksi(img, n_top=1)
        if result:
            top = result["top"][0]
            rows.append(
                {
                    "nama_file": getattr(img, "filename", f"gambar_{i}"),
                    "tanaman": top["tanaman"],
                    "penyakit": top["penyakit"],
                    "kelas": top["kelas"],
                    "confidence": round(top["confidence"], 4),
                }
            )
        progress.progress(i / len(images))
    if not rows:
        st.warning("Tidak ada hasil prediksi.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    fig = px.bar(
        df,
        x="nama_file",
        y="confidence",
        color="tanaman",
        labels={"confidence": "Confidence", "nama_file": "Berkas"},
        title="Confidence per citra",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Unduh Hasil Prediksi (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="hasil_prediksi_daun.csv",
        mime="text/csv",
    )


def render_dataset_dashboard() -> None:
    st.subheader("Dashboard Dataset")
    train_dir = DATASET_DIR / "train"
    if not train_dir.exists():
        st.info("Dataset belum tersedia. Jalankan `python scripts/prepare_dataset.py`.")
        return
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    counts = {c: len(list((train_dir / c).glob("*.*"))) for c in classes}
    df = pd.DataFrame({"kelas": list(counts.keys()), "jumlah": list(counts.values())})
    df["tanaman"] = df["kelas"].str.split("___").str[0].str.replace("_", " ")

    c1, c2 = st.columns(2)
    c1.metric("Jumlah Kelas", len(classes))
    c2.metric("Total Gambar (train)", int(df["jumlah"].sum()))

    fig = px.bar(
        df.sort_values("jumlah"),
        x="jumlah",
        y="kelas",
        orientation="h",
        labels={"jumlah": "Jumlah Gambar", "kelas": "Kelas"},
        title="Distribusi Kelas (train)",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.pie(df, names="tanaman", values="jumlah", title="Proporsi per Tanaman")
    st.plotly_chart(fig2, use_container_width=True)

    if METADATA_PATH.exists():
        with st.expander("Metadata model terlatih"):
            st.json(json.loads(METADATA_PATH.read_text(encoding="utf-8")))


def render_knowledge_base() -> None:
    st.subheader("Basis Pengetahuan")
    st.caption("38 kelas daun PlantVillage beserta informasi penyakit.")
    rows = []
    for kode, info in knowledge.PENGETAHUAN.items():
        rows.append(
            {
                "kelas": kode,
                "tanaman": info.get("tanaman"),
                "penyakit": info.get("penyakit"),
                "kategori": info.get("kategori"),
                "risiko": info.get("risiko"),
            }
        )
    df = pd.DataFrame(rows)
    kategori = st.multiselect(
        "Filter kategori", sorted(df["kategori"].dropna().unique().tolist())
    )
    if kategori:
        df = df[df["kategori"].isin(kategori)]
    st.dataframe(df, use_container_width=True)


def main() -> None:
    st.title("🌿 PlantVision AI")
    st.caption(
        "Klasifikasi Penyakit Daun dengan Deep Learning (CNN) - "
        "Sesi 2, mendukung pertanian presisi"
    )

    if not _model_available():
        st.warning(
            "Model belum tersedia. Latih dengan: `python train.py` "
            "(dataset disiapkan via `python scripts/prepare_dataset.py`)."
        )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Prediksi Tunggal", "Prediksi Banyak", "Dashboard Dataset", "Basis Pengetahuan"]
    )
    with tab1:
        uploaded = st.file_uploader(
            "Unggah citra daun", type=["jpg", "jpeg", "png", "webp"], key="single"
        )
        if uploaded:
            render_predict_single(Image.open(uploaded))
        else:
            st.info("Unggah satu citra daun untuk memulai prediksi.")
    with tab2:
        uploads = st.file_uploader(
            "Unggah beberapa citra daun",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="multi",
        )
        if uploads:
            images = []
            for u in uploads:
                img = Image.open(u)
                img.filename = u.name
                images.append(img)
            render_predict_multi(images)
        else:
            st.info("Unggah beberapa citra untuk prediksi batch.")
    with tab3:
        render_dataset_dashboard()
    with tab4:
        render_knowledge_base()


if __name__ == "__main__":
    main()
