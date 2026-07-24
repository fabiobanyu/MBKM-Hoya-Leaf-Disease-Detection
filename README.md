# 🍃 Hoya Leaf Disease Detection & Species Identification

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-AI-orange.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20App-lightgrey.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-blue.svg)

> **Proyek MBKM (Merdeka Belajar Kampus Merdeka) / Kerja Praktik**
> 
> *Sistem berbasis Kecerdasan Buatan (AI) untuk mendeteksi penyakit dan mengidentifikasi spesies spesifik pada daun tanaman hias Hoya.*

---

## 📌 Tentang Proyek
Aplikasi web ini menggunakan arsitektur *Deep Learning* tingkat lanjut untuk membantu petani dan pecinta tanaman hias dalam mendiagnosis penyakit pada daun Hoya. Sistem ini mengadopsi pendekatan **Multitask Learning**, di mana AI mampu memprediksi **Jenis Penyakit** sekaligus **Spesies Tanaman** secara bersamaan dari satu gambar yang sama.

### ✨ Fitur Utama:
1. **🛡️ Dual-Model Architecture:** 
   - **Guard Model (MobileNetV3-Small):** Bertugas sebagai satpam untuk menolak gambar yang bukan merupakan daun Hoya (mencegah *noise*).
   - **Main Classifier (DenseNet-121 + CBAM):** Model multitask utama dengan modul *Attention* (CBAM) untuk mendeteksi penyakit dan spesies dengan akurasi tinggi.
2. **🌡️ Explainable AI (Grad-CAM):** Tidak seperti AI konvensional yang bertindak seperti "kotak hitam", sistem ini memunculkan **Peta Panas (Heatmap)** untuk menunjukkan secara persis bagian daun mana yang dicurigai berpenyakit oleh AI.
3. **✂️ Smart Crop UI:** Antarmuka web modern yang mengizinkan pengguna untuk memotong (crop) dan memfokuskan gambar langsung dari browser sebelum dianalisis.
4. **🕸️ Graph Database Integration:** Menggunakan **Neo4j AuraDB** untuk memetakan hubungan kompleks antara Spesies, Penyakit, dan Rekomendasi Penanganan.

---

## 📂 Dataset
*Catatan: File dataset mentah dan model berbobot berat (ratusan MB) tidak diunggah ke repository ini untuk menjaga kebersihan riwayat Git.*

Dataset gambar daun Hoya (sehat dan berpenyakit) yang digunakan untuk melatih model ini tersedia secara publik di Kaggle:
👉 **[Hoya Disease Dataset by fabiobanyucyto](https://www.kaggle.com/datasets/fabiobanyucyto/hoya-disease-dataset)**

---

## 💻 Teknologi yang Digunakan
*   **Machine Learning:** PyTorch, Torchvision, OpenCV
*   **Backend:** Python, Flask, Gunicorn
*   **Frontend:** HTML5, Vanilla CSS (Glassmorphism UI), JavaScript (Cropper.js)
*   **Database:** Neo4j (Graph Database)
*   **Deployment Ready:** Docker & requirements.txt tersedia untuk *cloud hosting* (seperti Hugging Face Spaces / Render).

---
*Dibuat oleh **Fabio Banyu Cyto** sebagai bagian dari dokumentasi dan portofolio riset MBKM.*
