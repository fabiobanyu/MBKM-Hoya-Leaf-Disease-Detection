# Download Non-Hoya Leaf Images untuk Mini-CNN Guard Dataset
# ==========================================================
# Script ini mendownload daun tanaman NON-Hoya dari Kaggle PlantVillage
# sebagai "hard negative" untuk melatih Mini-CNN binary classifier.
#
# Cara Setup Kaggle API:
# 1. Login ke https://www.kaggle.com/settings
# 2. Scroll ke bagian "API" -> klik "Create New Token"
# 3. Set environment variable KAGGLE_API_TOKEN=<token>
# 4. Jalankan script ini: python download_non_hoya_leaves.py

import os
import sys
import random
import shutil
from pathlib import Path

# =============================================================================
# KONFIGURASI
# =============================================================================
OUTPUT_DIR = r"D:\KP\Dataset_Dan_Gambar\negative_leaves"
KAGGLE_DATASET = "abdallahalidev/plantvillage-dataset"
TEMP_DIR = r"D:\KP\Dataset_Dan_Gambar\_temp_plantvillage"

# Jumlah gambar yang diambil per kategori
SAMPLES_PER_CATEGORY = {
    # Daun yang MIRIP Hoya (tebal, waxy, hijau polos) — PALING PENTING
    "similar_to_hoya": 40,  # per subfolder
    # Daun tanaman umum lainnya
    "other_leaves": 25,     # per subfolder
}

# Folder dari PlantVillage yang daunnya MIRIP Hoya (waxy, tebal, hijau polos)
# Ini "hard negatives" — yang paling penting!
SIMILAR_TO_HOYA = [
    "Pepper,_bell___healthy",
    "Potato___healthy", 
    "Soybean___healthy",
    "Raspberry___healthy",
    "Peach___healthy",
    "Apple___healthy",
    "Cherry_(including_sour)___healthy",
    "Grape___healthy",
]

# Folder dari PlantVillage untuk daun sakit (bercak, layu, dll.)
# Ini penting supaya Mini-CNN tidak bingung: "daun sakit non-Hoya ≠ daun sakit Hoya"
OTHER_LEAVES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Strawberry___healthy",
    "Strawberry___Leaf_scorch",
    "Peach___Bacterial_spot",
    "Pepper,_bell___Bacterial_spot",
    "Cherry_(including_sour)___Powdery_mildew",
    "Squash___Powdery_mildew",
    "Orange___Haunglongbing_(Citrus_greening)",
]


def check_kaggle():
    """Cek apakah kaggle CLI tersedia dan API key sudah di-setup."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    access_token = kaggle_dir / "access_token"
    
    has_creds = kaggle_json.exists() or access_token.exists()
    
    # Also check environment variable
    if not has_creds and not os.environ.get("KAGGLE_API_TOKEN"):
        print("=" * 60)
        print("[ERROR] KAGGLE API BELUM DI-SETUP!")
        print("=" * 60)
        print()
        print("Cara setup (1 menit):")
        print("1. Buka: https://www.kaggle.com/settings")
        print("2. Scroll ke bagian 'API'")
        print("3. Klik 'Create New Token'")
        print(f"4. Simpan token ke: {access_token}")
        print("6. Jalankan ulang script ini")
        print()
        return False
    
    if access_token.exists():
        # Set environment variable from file for kaggle package
        token = access_token.read_text().strip()
        os.environ["KAGGLE_API_TOKEN"] = token
        print("[OK] Kaggle access_token ditemukan")

    try:
        import kaggle  # type: ignore[import-not-found]  # noqa: F401
        return True
    except ImportError:
        print("[INFO] Package 'kaggle' belum terinstall.")
        print("   Menginstall otomatis...")
        os.system(f"{sys.executable} -m pip install -q kaggle")
        try:
            import kaggle  # type: ignore[import-not-found]  # noqa: F401
            return True
        except ImportError:
            print("[ERROR] Gagal install kaggle. Coba manual: pip install kaggle")
            return False


def download_plantvillage():
    """Download PlantVillage dataset dari Kaggle."""
    from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore[import-not-found]

    os.makedirs(TEMP_DIR, exist_ok=True)

    # Check if already downloaded
    color_dir = os.path.join(TEMP_DIR, "plantvillage dataset", "color")
    if os.path.exists(color_dir) and len(os.listdir(color_dir)) > 10:
        print(f"[OK] PlantVillage sudah terdownload di {color_dir}")
        return color_dir

    print("[DOWNLOAD] Mendownload PlantVillage dari Kaggle...")
    print(f"   Dataset: {KAGGLE_DATASET}")
    print(f"   Ini mungkin butuh beberapa menit (~3 GB)...")
    print()

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(KAGGLE_DATASET, path=TEMP_DIR, unzip=True)

    if os.path.exists(color_dir):
        print("[OK] Download selesai!")
        return color_dir

    # Try alternative path structure
    for root, dirs, files in os.walk(TEMP_DIR):
        if "color" in dirs:
            color_dir = os.path.join(root, "color")
            print(f"[OK] Download selesai! (ditemukan di {color_dir})")
            return color_dir

    print("[ERROR] Struktur folder tidak sesuai. Cek manual:", TEMP_DIR)
    return None


def sample_images(source_dir, target_dir, folders, samples_per_folder, category_name):
    """Ambil random sample dari setiap folder, simpan ke target_dir."""
    total_copied = 0
    skipped_folders = []

    for folder_name in folders:
        folder_path = os.path.join(source_dir, folder_name)
        if not os.path.exists(folder_path):
            skipped_folders.append(folder_name)
            continue

        images = [f for f in os.listdir(folder_path)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not images:
            skipped_folders.append(folder_name)
            continue

        n_sample = min(samples_per_folder, len(images))
        selected = random.sample(images, n_sample)

        for img_name in selected:
            # Rename to avoid collision: category_foldername_originalname
            clean_folder = folder_name.replace(",", "").replace(" ", "_").replace("(", "").replace(")", "")
            new_name = f"{category_name}_{clean_folder}_{img_name}"
            src = os.path.join(folder_path, img_name)
            dst = os.path.join(target_dir, new_name)
            shutil.copy2(src, dst)
            total_copied += 1

    if skipped_folders:
        print(f"  [WARN] {len(skipped_folders)} folder tidak ditemukan (mungkin beda nama):")
        for sf in skipped_folders[:5]:
            print(f"      - {sf}")
        if len(skipped_folders) > 5:
            print(f"      ... dan {len(skipped_folders) - 5} lainnya")

    return total_copied


def main():
    random.seed(42)
    print("=" * 60)
    print("[*] Download Dataset Daun Non-Hoya")
    print("    Untuk training Mini-CNN Binary Guard")
    print("=" * 60)
    print()

    # Step 1: Check Kaggle
    if not check_kaggle():
        return

    # Step 2: Download PlantVillage
    color_dir = download_plantvillage()
    if not color_dir:
        return

    # List available folders
    available = sorted(os.listdir(color_dir))
    print(f"\n[INFO] Folder tersedia di PlantVillage: {len(available)}")
    for f in available:
        n = len([x for x in os.listdir(os.path.join(color_dir, f)) 
                 if x.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"   {f}: {n} gambar")

    # Step 3: Sample images
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n[OUTPUT] {OUTPUT_DIR}")

    print(f"\n[1/2] Sampling daun MIRIP Hoya (hard negatives)...")
    n1 = sample_images(
        color_dir, OUTPUT_DIR, SIMILAR_TO_HOYA,
        SAMPLES_PER_CATEGORY["similar_to_hoya"], "similar"
    )
    print(f"   → {n1} gambar disalin")

    print(f"\n[2/2] Sampling daun tanaman lain (general negatives)...")
    n2 = sample_images(
        color_dir, OUTPUT_DIR, OTHER_LEAVES,
        SAMPLES_PER_CATEGORY["other_leaves"], "other"
    )
    print(f"   → {n2} gambar disalin")

    total = n1 + n2
    print(f"\n{'=' * 60}")
    print(f"[DONE] Total {total} gambar daun non-Hoya disimpan.")
    print(f"   Lokasi: {OUTPUT_DIR}")
    print(f"   Mirip Hoya (hard negative): {n1}")
    print(f"   Daun lain (general): {n2}")
    print(f"{'=' * 60}")

    # Step 4: Summary
    print(f"\n[SUMMARY] Ringkasan dataset negatif lengkap:")
    neg_pool = r"D:\KP\Dataset_Dan_Gambar\negative_pool"
    n_random = len([f for f in os.listdir(neg_pool) if f.startswith("neg_") and not f.startswith("neg_gen")])
    n_gen = len([f for f in os.listdir(neg_pool) if f.startswith("neg_gen")])
    print(f"   Random (picsum)   : {n_random} (di negative_pool/)")
    print(f"   Generated (shapes): {n_gen} (di negative_pool/)")
    print(f"   Daun non-Hoya     : {total} (di negative_leaves/) ← BARU")
    print(f"   TOTAL NEGATIF     : {n_random + n_gen + total}")

    print(f"\n[NEXT] Langkah selanjutnya:")
    print(f"   Gabungkan semua negatif saat training Mini-CNN.")
    print(f"   Folder negative_leaves/ bisa di-merge ke negative_pool/")
    print(f"   atau dipakai terpisah.")

    # Optional: Clean up temp
    print(f"\n[CLEANUP] Folder temp PlantVillage ({TEMP_DIR}) bisa dihapus manual")
    print(f"   jika tidak diperlukan lagi (~3 GB).")


if __name__ == "__main__":
    main()
