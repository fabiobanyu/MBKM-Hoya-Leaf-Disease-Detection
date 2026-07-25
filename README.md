<div align="center">
  <img src="Frontend/static/hoya.svg" alt="Hoya Leaf Logo" width="100" />
  <h1>🍃 Hoya AI Vision</h1>
  <p><strong>Intelligent Disease Detection & Species Identification System for Hoya Plants</strong></p>

  <p>
    <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white" alt="PyTorch"></a>
    <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"></a>
    <a href="https://neo4j.com/"><img src="https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j"></a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E" alt="JavaScript"></a>
  </p>
  
  <i>Proyek Riset Kolaboratif MBKM (Merdeka Belajar Kampus Merdeka) — BRIN & ITERA</i>
</div>

---

## 👥 Tim Peneliti & Pengembang (MBKM)

Sistem ini dikembangkan secara kolaboratif oleh tim riset mahasiswa dari Institut Teknologi Sumatera (ITERA) di bawah bimbingan Badan Riset dan Inovasi Nasional (BRIN):

| Nama | NIM | Peran Utama (Role) | Fokus Tugas |
| :--- | :---: | :--- | :--- |
| **Feby Wulandari** | `123450042` | 📊 Dataset Collector & Optimization | Akuisisi data lapangan dan teknik augmentasi dataset gambar. |
| **Efi Defiyati** | `123450005` | 🧠 Machine Learning Engineer | Rekayasa arsitektur *Deep Learning* tingkat lanjut untuk klasifikasi. |
| **Nabyla Sharfina** | `123450008` | 🕸️ Knowledge Graph Engineer | Desain skema dan integrasi *database* grafik (Neo4j) medis tanaman. |
| **Fabio Banyu Cyto** | `123450104` | 💻 ML & Web Developer | Integrasi model ke *backend* Flask dan desain UI/UX *frontend* dinamis. |

---

## 📌 Tentang Sistem

**Hoya AI Vision** adalah aplikasi cerdas yang membantu pembudidaya dan peneliti tanaman hias mendiagnosis penyakit pada daun Hoya. Sistem ini mengadopsi pendekatan **Multitask Learning**, di mana AI mampu memprediksi **Jenis Penyakit** sekaligus **Spesies Tanaman** secara bersamaan dari satu gambar yang sama.

### ✨ Fitur Utama:
1. **🛡️ Guard Model (Pencegah *Noise*):** Memfilter gambar yang dimasukkan, otomatis menolak gambar jika bukan daun tanaman Hoya.
2. **🎯 Multitask Classification:** Satu model utama memprediksi kelas penyakit (contoh: *Root Rot*, *Rust*) dan spesies Hoya secara paralel.
3. **🌡️ Explainable AI (Grad-CAM):** Sistem menghasilkan *Heatmap* Peta Panas visual yang membuktikan area daun mana yang menyebabkan AI mendiagnosis penyakit tersebut.
4. **🧠 Knowledge Graph Integration:** Terhubung dengan *database* Neo4j untuk menarik informasi komprehensif, penyebab, dan langkah penanganan cerdas.

---

## ⚙️ Arsitektur & Pipeline Sistem

Alur kerja (pipeline) sistem dirancang untuk memastikan akurasi dan kecepatan, dari pengguna mengunggah gambar hingga mendapat penanganan dari Knowledge Graph.

```mermaid
graph TD
    A([📸 Unggah / Ambil Gambar]) --> B{✂️ Smart Crop UI}
    B --> C[🖼️ Pre-processing Gambar]
    
    subgraph AI Vision Pipeline
        C --> D{🛡️ Guard Model<br/>MobileNetV3-Small}
        D -- "Bukan Daun" --> E([❌ Tolak Gambar])
        D -- "Daun Hoya Valid" --> F[🧠 Main Classifier<br/>DenseNet-121 + CBAM]
        
        F --> G1(🔬 Output 1: Prediksi Penyakit)
        F --> G2(🌱 Output 2: Prediksi Spesies)
        F --> G3(🔥 Output 3: Heatmap Grad-CAM)
    end
    
    G1 --> H[(🕸️ Neo4j Knowledge Graph)]
    G2 --> H
    
    H -- "Query Penanganan & Gejala" --> I([💻 Hasil ditampilkan di Web UI])
    G3 --> I
```

### 🧠 Penjelasan Model:
- **MobileNetV3-Small:** Digunakan sebagai *Guard Model* karena sangat ringan dan cepat, dioptimalkan untuk perangkat *mobile* untuk klasifikasi biner sederhana (Daun Hoya vs Bukan).
- **DenseNet-121 + CBAM:** *Convolutional Block Attention Module* (CBAM) ditambahkan pada arsitektur DenseNet agar AI dapat lebih fokus membedakan tekstur bercak penyakit tanpa tertukar dengan corak unik daun Hoya.

---

## 📂 Dataset Publik

Untuk mendorong perkembangan riset lanjutan pada botani cerdas, dataset gambar daun Hoya (sehat dan berpenyakit) beserta teknik augmentasinya yang kami gunakan tersedia secara publik di Kaggle.

🔗 **[Hoya Disease Dataset di Kaggle](https://www.kaggle.com/datasets/fabiofire/hoya-disease-dataset)**  
*(Oleh: Fabio Banyu Cyto, dkk)*

> **Catatan:** File dataset mentah dan bobot model berukuran besar (`.pth` >100MB) sengaja tidak di-*push* ke repositori GitHub ini untuk menjaga kebersihan dan efisiensi riwayat Git.

---

## 🚀 Cara Menjalankan Secara Lokal

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/fabiobanyu/MBKM-Hoya-Leaf-Disease-Detection.git
   cd MBKM-Hoya-Leaf-Disease-Detection
   ```
2. **Install Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Konfigurasi Neo4j (Knowledge Graph):**
   - Pastikan Neo4j Desktop berjalan di latar belakang.
   - Sesuaikan kredensial (URI, Username, Password) di file `Backend/Backend.py`.
4. **Jalankan Aplikasi:**
   ```bash
   python Backend/Backend.py
   ```
   Aplikasi dapat diakses melalui browser di `http://127.0.0.1:5000`
