# --- Cell 0 ---
import os

def safe_install(pkg, no_deps=True):
    flag = "--no-deps" if no_deps else ""
    os.system(f"pip install -q {flag} {pkg}")

safe_install("grad-cam", no_deps=False)

import re
import cv2
import copy
import json
import time
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from PIL import Image
from collections import Counter, defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim import lr_scheduler
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

import torchvision
from torchvision import models, transforms
import torchvision.transforms.functional as TF

from sklearn.metrics import confusion_matrix, classification_report, f1_score

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD  = np.array([0.229, 0.224, 0.225])

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if torch.cuda.is_available():
    print(f"GPU          : {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version : {torch.version.cuda}")
    print(f"VRAM         : {torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GB")
else:
    print("GPU tidak tersedia.")
print(f"\nDevice : {device}")

print("\n===== Library Version =====")
print("NumPy  :", np.__version__)
print("Torch  :", torch.__version__)
print("TVision:", torchvision.__version__)

# --- Cell 1 ---
CONFIG = {
    'DATA_DIR': '/kaggle/input/datasets/fabiofire/hoya-disease-dataset/data_real_KP',
    'OUTPUT_DIR': '/kaggle/working//outputs',
    'EXCLUDED_FOLDERS': ['Hoya Compacta (Cadangan)', 'Hoya multiflora (Diganti)', 'Hoya bella (Diganti)'],
    'IMG_SIZE': 224, 'BATCH_SIZE': 32, 'NUM_EPOCHS': 60, 'EARLY_STOP_PATIENCE': 15, 'SEED': 42,
    'TRAIN_RATIO': 0.70, 'VAL_RATIO': 0.15, 'TEST_RATIO': 0.15,
    'USE_WEIGHTED_SAMPLER': True, 'USE_CLASS_WEIGHTED_LOSS': False,
    'REMOVE_BACKGROUND': False,
    'USE_CLAHE': True, 'USE_ADAPTIVE_SHARPEN': True, 'BLUR_THRESHOLD': 100.0, 'SHARPEN_STRENGTH': 1.2,
    'DROPOUT': 0.20, 'BACKBONE_LR': 3e-5, 'HEAD_LR': 1.5e-3,
    'BACKBONE': 'densenet121',
    'USE_MIXUP': True, 'MIXUP_ALPHA': 0.15, 'MIXUP_PROB': 0.3, 'LABEL_SMOOTHING': 0.02,
    'USE_AMP': True,
    'USE_SWA': True,   # DenseNet: SWA terbukti membantu, biarkan aktif
    'SWA_EPOCHS': 6, 'SWA_LR': 1e-5,
    'FINETUNE_FROM_CHECKPOINT': True,
    'FINETUNE_CHECKPOINT_PATH': None,
    'FINETUNE_EPOCHS': 15, 'FINETUNE_LR': 5e-6,
}
CONFIG['FINETUNE_CHECKPOINT_PATH'] = os.path.join(CONFIG['OUTPUT_DIR'], 'hoya_multitask_densenet121_better_new.pth')

os.makedirs(CONFIG['OUTPUT_DIR'], exist_ok=True)
set_seed(CONFIG['SEED'])
print("Konfigurasi siap.")

# --- Cell 2 ---
CLASS_ORDER = [
    'Sehat',
    'Bercak Cokelat',
    'Bercak Putih',
    'Daun Layu',
    'Bercak Bintik Hitam',
]

EXCLUDED_DISEASE_CLASSES = ['Bercak Bintik Hitam Putih']

def get_unified_class_name(folder_name):
    lower_name = folder_name.lower()
    if 'sehat' in lower_name:
        return 'Sehat'
    elif ('bintik_hitam' in lower_name or 'bintik-bercak' in lower_name or 'bercak-bintik' in lower_name):
        return 'Bercak Bintik Hitam'
    elif ('bercak_coklat' in lower_name or 'bercak_cokelat' in lower_name):
        return 'Bercak Cokelat'
    elif ('bercak_hitam_putih' in lower_name or 'bercak_putih_hitam' in lower_name or 'bintik_hitam_putih' in lower_name):
        return 'Bercak Bintik Hitam Putih'
    elif 'bercak_putih' in lower_name:
        return 'Bercak Putih'
    elif 'daun_layu' in lower_name:
        return 'Daun Layu'
    return 'Unknown'

def get_base_name(filename):
    name, _ = os.path.splitext(filename)
    name = re.sub(r'_(whitebg|white|putih|bgputih|bg_putih|putihbg|putih_bg)$', '', name, flags=re.IGNORECASE)
    return name.strip()

def is_clean_bg_filename(filename):
    """True = versi background putih (manual), False = versi natural."""
    name, _ = os.path.splitext(filename)
    return bool(re.search(r'_(whitebg|white|putih|bgputih|bg_putih|putihbg|putih_bg)$', name, flags=re.IGNORECASE))

def compute_blur_score(img_path_or_array):
    if isinstance(img_path_or_array, str):
        img = cv2.imread(img_path_or_array)
        if img is None:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv2.cvtColor(np.array(img_path_or_array), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

print(f"Kelas dipakai ({len(CLASS_ORDER)}): {CLASS_ORDER}")
print(f"Kelas dihapus: {EXCLUDED_DISEASE_CLASSES}")

# --- Cell 3 ---
class AdaptiveSharpen:
    def __init__(self, blur_threshold=100.0, sharpen_strength=1.2):
        self.blur_threshold = blur_threshold
        self.sharpen_strength = sharpen_strength

    def __call__(self, img):
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < self.blur_threshold:
            blurred = cv2.GaussianBlur(img_np, (0, 0), sigmaX=3)
            sharpened = cv2.addWeighted(img_np, 1 + self.sharpen_strength, blurred, -self.sharpen_strength, 0)
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            return Image.fromarray(sharpened)
        return img


class CLAHETransform:
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def __call__(self, img):
        img_np = np.array(img)
        lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        l_eq = self.clahe.apply(l)
        lab_eq = cv2.merge((l_eq, a, b))
        img_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
        return Image.fromarray(img_eq)


class DiscreteRotation:
    def __init__(self, angles):
        self.angles = angles

    def __call__(self, img):
        angle = random.choice(self.angles)
        return TF.rotate(img, angle)

print("AdaptiveSharpen, CLAHE & DiscreteRotation siap.")

# --- Cell 4 ---
class HoyaLeafDataset(Dataset):
    def __init__(self, root_dir, class_order, excluded_disease_classes=None, excluded_folders=None):
        self.root_dir = root_dir
        self.classes = class_order
        self.excluded_disease_classes = excluded_disease_classes or []
        self.excluded_folders = excluded_folders or []

        self.image_paths = []
        self.disease_labels = []
        self.species_labels = []
        self.species_list = []
        self.leaf_ids = []
        self.is_clean_version = []

        species_found = set()
        for species in sorted(os.listdir(root_dir)):
            if species in self.excluded_folders:
                continue
            if os.path.isdir(os.path.join(root_dir, species)):
                species_found.add(species)
        self.species_names = sorted(species_found)
        species_to_idx = {s: i for i, s in enumerate(self.species_names)}

        skipped_unknown = []
        skipped_excluded_class = defaultdict(int)

        for species in self.species_names:
            species_path = os.path.join(root_dir, species)
            for disease_raw in os.listdir(species_path):
                disease_path = os.path.join(species_path, disease_raw)
                if not os.path.isdir(disease_path):
                    continue
                disease_unified = get_unified_class_name(disease_raw)
                if disease_unified in self.excluded_disease_classes:
                    n_imgs = sum(1 for f in os.listdir(disease_path) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
                    skipped_excluded_class[disease_unified] += n_imgs
                    continue
                if disease_unified == 'Unknown':
                    skipped_unknown.append(os.path.join(species, disease_raw))
                    continue
                disease_idx = self.classes.index(disease_unified)
                species_idx = species_to_idx[species]

                for img_name in os.listdir(disease_path):
                    if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(disease_path, img_name)
                        self.image_paths.append(img_path)
                        self.disease_labels.append(disease_idx)
                        self.species_labels.append(species_idx)
                        self.species_list.append(species)
                        self.leaf_ids.append(f"{species}_{get_base_name(img_name)}")
                        self.is_clean_version.append(is_clean_bg_filename(img_name))

        if skipped_unknown:
            print(f"[PERINGATAN] {len(skipped_unknown)} folder dilewati")
        if skipped_excluded_class:
            print("[INFO] Kelas dihapus dari dataset:")
            for cn, n in skipped_excluded_class.items():
                print(f"   - {cn}: {n} gambar dilewati")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert('RGB')
        return image, self.disease_labels[idx], self.species_labels[idx], self.image_paths[idx], self.leaf_ids[idx]


full_dataset = HoyaLeafDataset(
    CONFIG['DATA_DIR'], class_order=CLASS_ORDER,
    excluded_disease_classes=EXCLUDED_DISEASE_CLASSES,
    excluded_folders=CONFIG['EXCLUDED_FOLDERS'],
)
class_names = full_dataset.classes
species_names = full_dataset.species_names

n_clean = sum(full_dataset.is_clean_version)
n_natural = len(full_dataset) - n_clean
print(f"Total gambar: {len(full_dataset)} | Kelas: {len(class_names)} | Spesies: {len(species_names)}")
print(f"Versi background putih (manual): {n_clean} | Versi natural: {n_natural}")

# --- Cell 5 ---
def print_and_plot_distribution(labels, names, title, save_name=None):
    counts = np.bincount(labels, minlength=len(names))
    print(f"--- {title} ---")
    for cn, c in zip(names, counts):
        print(f"  {cn:22s}: {c}")
    plt.figure(figsize=(8, 4))
    bars = plt.barh(names, counts, color='steelblue')
    plt.title(title)
    plt.xlabel('Jumlah Gambar')
    for bar, c in zip(bars, counts):
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, str(c), va='center')
    plt.tight_layout()
    if save_name:
        plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], save_name), dpi=150, bbox_inches='tight')
    plt.show()
    return counts

_ = print_and_plot_distribution(full_dataset.disease_labels, class_names, 'Distribusi Penyakit - Seluruh Data', 'distribusi_penyakit.png')
_ = print_and_plot_distribution(full_dataset.species_labels, species_names, 'Distribusi Spesies - Seluruh Data', 'distribusi_spesies.png')

# --- Cell 6 ---
leaf_to_disease = {}
leaf_to_species = {}
leaf_to_indices = defaultdict(list)
for i, leaf_id in enumerate(full_dataset.leaf_ids):
    leaf_to_indices[leaf_id].append(i)
    leaf_to_disease[leaf_id] = full_dataset.disease_labels[i]
    leaf_to_species[leaf_id] = full_dataset.species_labels[i]

leaves_per_group = defaultdict(list)
for leaf_id in leaf_to_disease:
    key = (leaf_to_disease[leaf_id], leaf_to_species[leaf_id])
    leaves_per_group[key].append(leaf_id)

random.seed(CONFIG['SEED'])
train_leaves, val_leaves, test_leaves = set(), set(), set()

for key, leaves in leaves_per_group.items():
    leaves = leaves.copy()
    random.shuffle(leaves)
    n = len(leaves)
    n_train = max(1, int(round(CONFIG['TRAIN_RATIO'] * n)))
    n_val = max(1, int(round(CONFIG['VAL_RATIO'] * n))) if n - n_train > 1 else 0
    n_train = min(n_train, n)
    n_val = min(n_val, max(0, n - n_train))
    train_leaves.update(leaves[:n_train])
    val_leaves.update(leaves[n_train:n_train + n_val])
    test_leaves.update(leaves[n_train + n_val:])

train_indices, val_indices, test_indices = [], [], []
for leaf_id, idxs in leaf_to_indices.items():
    if leaf_id in train_leaves:
        train_indices.extend(idxs)
    elif leaf_id in val_leaves:
        val_indices.extend(idxs)
    else:
        test_indices.extend(idxs)

print(f"Sebelum filter -> Train: {len(train_indices)} | Val: {len(val_indices)} | Test: {len(test_indices)}")

# --- Cell 7 ---
# Val & Test HARUS pakai versi natural saja -> evaluasi mencerminkan kondisi nyata (webcam/upload)
val_indices = [i for i in val_indices if not full_dataset.is_clean_version[i]]
test_indices = [i for i in test_indices if not full_dataset.is_clean_version[i]]

print(f"Setelah filter  -> Train: {len(train_indices)} (natural+putih) | Val: {len(val_indices)} (natural) | Test: {len(test_indices)} (natural)")

train_disease = [full_dataset.disease_labels[i] for i in train_indices]
train_species = [full_dataset.species_labels[i] for i in train_indices]
val_disease = [full_dataset.disease_labels[i] for i in val_indices]
val_species = [full_dataset.species_labels[i] for i in val_indices]
test_disease = [full_dataset.disease_labels[i] for i in test_indices]
test_species = [full_dataset.species_labels[i] for i in test_indices]

disease_counts_train = np.bincount(train_disease, minlength=len(class_names))
species_counts_train = np.bincount(train_species, minlength=len(species_names))

for name, labels in [('TRAIN Penyakit', train_disease), ('VAL Penyakit', val_disease), ('TEST Penyakit', test_disease)]:
    _ = print_and_plot_distribution(labels, class_names, f'Distribusi - {name}')
for name, labels in [('TRAIN Spesies', train_species), ('VAL Spesies', val_species), ('TEST Spesies', test_species)]:
    _ = print_and_plot_distribution(labels, species_names, f'Distribusi - {name}')

# --- Cell 8 ---
preprocess_steps = []
if CONFIG['USE_ADAPTIVE_SHARPEN']:
    preprocess_steps.append(AdaptiveSharpen(blur_threshold=CONFIG['BLUR_THRESHOLD'], sharpen_strength=CONFIG['SHARPEN_STRENGTH']))
if CONFIG['USE_CLAHE']:
    preprocess_steps.append(CLAHETransform())

train_transform = transforms.Compose([
    transforms.Resize((int(CONFIG['IMG_SIZE'] * 1.15), int(CONFIG['IMG_SIZE'] * 1.15))),
    *preprocess_steps,
    DiscreteRotation([0, 90, 180, 270]),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomResizedCrop(CONFIG['IMG_SIZE'], scale=(0.75, 1.0)),
    transforms.ColorJitter(brightness=0.15, contrast=0.10, saturation=0.08),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN.tolist(), IMAGENET_STD.tolist()),
    transforms.RandomErasing(p=0.25, scale=(0.02, 0.08), ratio=(0.3, 3.3)),
])

eval_transform = transforms.Compose([
    transforms.Resize((CONFIG['IMG_SIZE'], CONFIG['IMG_SIZE'])),
    *preprocess_steps,
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN.tolist(), IMAGENET_STD.tolist()),
])

print("Pipeline transform siap.")

# --- Cell 9 ---
class CustomSubset(Dataset):
    def __init__(self, dataset, indices, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform

    def __getitem__(self, idx):
        raw_img, disease_label, species_label, path, leaf_id = self.dataset[self.indices[idx]]
        img = self.transform(raw_img) if self.transform else raw_img
        display_img = np.array(raw_img.resize((256, 256)))
        return img, disease_label, species_label, path, display_img

    def __len__(self):
        return len(self.indices)


image_datasets = {
    'train': CustomSubset(full_dataset, train_indices, transform=train_transform),
    'val': CustomSubset(full_dataset, val_indices, transform=eval_transform),
    'test': CustomSubset(full_dataset, test_indices, transform=eval_transform),
}

if CONFIG['USE_WEIGHTED_SAMPLER']:
    disease_w = 1.0 / np.maximum(disease_counts_train, 1)
    species_w = 1.0 / np.maximum(species_counts_train, 1)
    disease_w = disease_w / disease_w.sum() * len(class_names)
    species_w = species_w / species_w.sum() * len(species_names)
    combined_weights = [disease_w[d] * species_w[s] for d, s in zip(train_disease, train_species)]

    max_class_count = int(max(disease_counts_train))
    total_balanced_samples = int(max_class_count * len(class_names))
    sampler = WeightedRandomSampler(weights=combined_weights, num_samples=total_balanced_samples, replacement=True)
    train_loader = DataLoader(image_datasets['train'], batch_size=CONFIG['BATCH_SIZE'], sampler=sampler,
                               num_workers=2, pin_memory=True)
    print("WeightedRandomSampler GABUNGAN (disease x species) aktif.")
else:
    total_balanced_samples = len(image_datasets['train'])
    train_loader = DataLoader(image_datasets['train'], batch_size=CONFIG['BATCH_SIZE'], shuffle=True,
                               num_workers=2, pin_memory=True)

dataloaders = {
    'train': train_loader,
    'val': DataLoader(image_datasets['val'], batch_size=CONFIG['BATCH_SIZE'], shuffle=False, num_workers=2, pin_memory=True),
    'test': DataLoader(image_datasets['test'], batch_size=CONFIG['BATCH_SIZE'], shuffle=False, num_workers=2, pin_memory=True),
}
dataset_sizes = {'train': total_balanced_samples, 'val': len(image_datasets['val']), 'test': len(image_datasets['test'])}
print(dataset_sizes)

# --- Cell 10 ---
samples_per_class = {}
random.seed(123)
indices_shuffled = list(range(len(image_datasets['train'])))
random.shuffle(indices_shuffled)
for idx in indices_shuffled:
    _, disease_label, _, _, _ = full_dataset[image_datasets['train'].indices[idx]]
    if disease_label not in samples_per_class:
        samples_per_class[disease_label] = idx
    if len(samples_per_class) == len(class_names):
        break

sorted_labels = sorted(samples_per_class.keys())
fig, axes = plt.subplots(len(sorted_labels), 2, figsize=(8, 4 * len(sorted_labels)))
fig.suptitle('Visualisasi: Original vs Hasil Augmentasi', fontsize=15, fontweight='bold')
for row, label in enumerate(sorted_labels):
    idx = samples_per_class[label]
    img_tensor, d_lbl, s_lbl, path, display_img = image_datasets['train'][idx]
    axes[row, 0].imshow(display_img)
    axes[row, 0].set_title(f'Asli\n{class_names[d_lbl]}')
    axes[row, 0].axis('off')
    img_disp = img_tensor.numpy().transpose(1, 2, 0)
    img_disp = IMAGENET_STD * img_disp + IMAGENET_MEAN
    img_disp = np.clip(img_disp, 0, 1)
    axes[row, 1].imshow(img_disp)
    axes[row, 1].set_title('Telah Di-Augmentasi')
    axes[row, 1].axis('off')
plt.tight_layout(); plt.subplots_adjust(top=0.95)
plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], 'augmentasi_before_after.png'), dpi=150, bbox_inches='tight')
plt.show()

# --- Cell 11 ---
class MultiTaskHoyaModel(nn.Module):
    def __init__(self, base, in_features, num_disease, num_species, dropout):
        super().__init__()
        self.base = base
        self.disease_head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(in_features, 256), nn.ReLU(inplace=True),
            nn.BatchNorm1d(256), nn.Dropout(dropout * 0.5), nn.Linear(256, num_disease),
        )
        self.species_head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(in_features, 128), nn.ReLU(inplace=True),
            nn.BatchNorm1d(128), nn.Dropout(dropout * 0.5), nn.Linear(128, num_species),
        )

    def forward(self, x):
        feat = self.base(x)
        return self.disease_head(feat), self.species_head(feat)


def build_model(num_disease, num_species, dropout=0.20, unfreeze='head_only', backbone='densenet121'):
    base = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
    in_features = base.classifier.in_features
    base.classifier = nn.Identity()

    for name, param in base.named_parameters():
        param.requires_grad = False
    if unfreeze in ('block4', 'block3_4'):
        for name, param in base.named_parameters():
            if name.startswith('features.denseblock4') or name.startswith('features.norm5'):
                param.requires_grad = True
    if unfreeze == 'block3_4':
        for name, param in base.named_parameters():
            if name.startswith('features.denseblock3') or name.startswith('features.transition3'):
                param.requires_grad = True

    model = MultiTaskHoyaModel(base, in_features, num_disease, num_species, dropout)
    for p in model.disease_head.parameters(): p.requires_grad = True
    for p in model.species_head.parameters(): p.requires_grad = True
    return model.to(device)


def set_unfreeze_stage(model, stage):
    for name, param in model.named_parameters():
        if name.startswith('disease_head') or name.startswith('species_head'):
            param.requires_grad = True
        elif name.startswith('base.features.denseblock4') or name.startswith('base.features.norm5'):
            param.requires_grad = stage in ('block4', 'block3_4')
        elif name.startswith('base.features.denseblock3') or name.startswith('base.features.transition3'):
            param.requires_grad = (stage == 'block3_4')
        else:
            param.requires_grad = False


model_ft = build_model(len(class_names), len(species_names), dropout=CONFIG['DROPOUT'],
                        unfreeze='head_only', backbone=CONFIG['BACKBONE'])
trainable = sum(p.numel() for p in model_ft.parameters() if p.requires_grad)
total = sum(p.numel() for p in model_ft.parameters())
print(f"Backbone: {CONFIG['BACKBONE']} | Param dilatih (head_only): {trainable:,} / {total:,}")

# --- Cell 12 ---
class FocalLoss(nn.Module):
    """Tersedia untuk eksperimen, TIDAK aktif secara default -> terbukti tidak cocok untuk proyek ini."""
    def __init__(self, alpha=None, gamma=2.0, label_smoothing=0.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.label_smoothing = label_smoothing

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, weight=self.alpha, label_smoothing=self.label_smoothing, reduction='none')
        pt = torch.exp(-ce_loss)
        return (((1 - pt) ** self.gamma) * ce_loss).mean()


disease_weights = torch.tensor(1.0 / np.maximum(disease_counts_train, 1), dtype=torch.float32)
disease_weights = (disease_weights / disease_weights.sum() * len(class_names)).to(device)
species_weights = torch.tensor(1.0 / np.maximum(species_counts_train, 1), dtype=torch.float32)
species_weights = (species_weights / species_weights.sum() * len(species_names)).to(device)

criterion_disease = nn.CrossEntropyLoss(
    weight=disease_weights if CONFIG['USE_CLASS_WEIGHTED_LOSS'] else None,
    label_smoothing=CONFIG['LABEL_SMOOTHING'])
criterion_species = nn.CrossEntropyLoss(
    weight=species_weights if CONFIG['USE_CLASS_WEIGHTED_LOSS'] else None,
    label_smoothing=CONFIG['LABEL_SMOOTHING'])

DISEASE_LOSS_WEIGHT = 1.0
SPECIES_LOSS_WEIGHT = 0.5

params_backbone = [p for n, p in model_ft.named_parameters() if p.requires_grad and n.startswith('base')]
params_head = [p for n, p in model_ft.named_parameters() if p.requires_grad and not n.startswith('base')]

optimizer_ft = optim.AdamW([
    {'params': params_backbone, 'lr': CONFIG['BACKBONE_LR'], 'weight_decay': 1e-4},
    {'params': params_head, 'lr': CONFIG['HEAD_LR'], 'weight_decay': 3e-4},
])
exp_lr_scheduler = lr_scheduler.ReduceLROnPlateau(optimizer_ft, mode='min', factor=0.5, patience=3)
print("Loss ganda & optimizer siap.")

# --- Cell 13 ---
def mixup_data(x, y_disease, y_species, alpha=0.2):
    lam = np.random.beta(alpha, alpha) if alpha > 0 else 1
    index = torch.randperm(x.size(0), device=x.device)
    mixed_x = lam * x + (1 - lam) * x[index]
    return mixed_x, y_disease, y_disease[index], y_species, y_species[index], lam


def cutmix_data(x, y_disease, y_species, alpha=1.0):
    lam = np.random.beta(alpha, alpha)
    batch_size = x.size(0)
    index = torch.randperm(batch_size, device=x.device)
    H, W = x.size(2), x.size(3)
    cut_ratio = np.sqrt(1.0 - lam)
    cut_h, cut_w = int(H * cut_ratio), int(W * cut_ratio)
    cy, cx = np.random.randint(H), np.random.randint(W)
    y1, y2 = np.clip(cy - cut_h // 2, 0, H), np.clip(cy + cut_h // 2, 0, H)
    x1, x2 = np.clip(cx - cut_w // 2, 0, W), np.clip(cx + cut_w // 2, 0, W)
    x_cut = x.clone()
    x_cut[:, :, y1:y2, x1:x2] = x[index, :, y1:y2, x1:x2]
    lam_adjusted = 1 - ((x2 - x1) * (y2 - y1) / (H * W))
    return x_cut, y_disease, y_disease[index], y_species, y_species[index], lam_adjusted


CHECKPOINT_PATH = os.path.join(CONFIG['OUTPUT_DIR'], f'checkpoint_{CONFIG["BACKBONE"]}.pth')
SAVE_EVERY_N_EPOCH = 3


def train_model(model, dataloaders, dataset_sizes, criterion_d, criterion_s, dw, sw,
                 optimizer, scheduler, num_epochs, patience, unfreeze_schedule=None,
                 use_mixup=False, mixup_alpha=0.2, mixup_prob=0.5, use_cutmix=True, use_amp=True,
                 selection_weight_disease=0.7, selection_weight_species=0.3,
                 checkpoint_path=None, save_every=3):
    since = time.time()
    unfreeze_schedule = unfreeze_schedule or {0: 'head_only'}
    scaler = torch.amp.GradScaler('cuda', enabled=(use_amp and torch.cuda.is_available()))

    start_epoch = 0
    best_model_wts = copy.deepcopy(model.state_dict())
    best_combined_score = 0.0
    best_f1_disease_at_best = 0.0
    epochs_no_improve = 0
    history = {'train_loss': [], 'val_loss': [], 'val_f1_disease': [], 'val_f1_species': [], 'val_combined_score': []}

    if checkpoint_path and os.path.exists(checkpoint_path):
        print(f"Checkpoint ditemukan di {checkpoint_path}, melanjutkan training...")
        ckpt = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(ckpt['model_state'])
        optimizer.load_state_dict(ckpt['optimizer_state'])
        scheduler.load_state_dict(ckpt['scheduler_state'])
        start_epoch = ckpt['epoch'] + 1
        history = ckpt['history']
        best_model_wts = ckpt['best_model_wts']
        best_combined_score = ckpt['best_combined_score']
        best_f1_disease_at_best = ckpt.get('best_f1_disease_at_best', 0.0)
        epochs_no_improve = ckpt['epochs_no_improve']
        print(f"Melanjutkan dari epoch {start_epoch+1}, best combined score: {best_combined_score:.4f}")
        for ep, stage in sorted(unfreeze_schedule.items()):
            if ep <= start_epoch - 1:
                set_unfreeze_stage(model, stage)

    for epoch in range(start_epoch, num_epochs):
        if epoch in unfreeze_schedule:
            stage = unfreeze_schedule[epoch]
            set_unfreeze_stage(model, stage)
            n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
            print(f"[Unfreeze] Epoch {epoch+1}: stage='{stage}' -> {n_train:,} param trainable")

        print(f'Epoch {epoch + 1}/{num_epochs}'); print('-' * 30)

        for phase in ['train', 'val']:
            model.train() if phase == 'train' else model.eval()
            running_loss = 0.0
            preds_d, labels_d, preds_s, labels_s = [], [], [], []

            for inputs, disease_lbl, species_lbl, _, _ in dataloaders[phase]:
                inputs = inputs.to(device, non_blocking=True)
                disease_lbl = disease_lbl.to(device, non_blocking=True)
                species_lbl = species_lbl.to(device, non_blocking=True)
                optimizer.zero_grad()

                apply_mixup = (phase == 'train' and use_mixup and random.random() < mixup_prob)
                use_cutmix_this_batch = apply_mixup and use_cutmix and random.random() < 0.5

                with torch.set_grad_enabled(phase == 'train'):
                    with torch.amp.autocast('cuda', enabled=(use_amp and torch.cuda.is_available())):
                        if apply_mixup:
                            if use_cutmix_this_batch:
                                inputs_mix, da, db, sa, sb, lam = cutmix_data(inputs, disease_lbl, species_lbl, alpha=1.0)
                            else:
                                inputs_mix, da, db, sa, sb, lam = mixup_data(inputs, disease_lbl, species_lbl, mixup_alpha)
                            out_d, out_s = model(inputs_mix)
                            loss_d = lam * criterion_d(out_d, da) + (1 - lam) * criterion_d(out_d, db)
                            loss_s = lam * criterion_s(out_s, sa) + (1 - lam) * criterion_s(out_s, sb)
                        else:
                            out_d, out_s = model(inputs)
                            loss_d = criterion_d(out_d, disease_lbl)
                            loss_s = criterion_s(out_s, species_lbl)
                        loss = dw * loss_d + sw * loss_s
                        pred_d = torch.argmax(out_d, 1)
                        pred_s = torch.argmax(out_s, 1)

                    if phase == 'train':
                        scaler.scale(loss).backward()
                        scaler.step(optimizer)
                        scaler.update()

                running_loss += loss.item() * inputs.size(0)
                if not apply_mixup:
                    preds_d.extend(pred_d.cpu().numpy()); labels_d.extend(disease_lbl.cpu().numpy())
                    preds_s.extend(pred_s.cpu().numpy()); labels_s.extend(species_lbl.cpu().numpy())

            epoch_loss = running_loss / dataset_sizes[phase]
            f1_d = f1_score(labels_d, preds_d, average='macro', zero_division=0) if labels_d else float('nan')
            f1_s = f1_score(labels_s, preds_s, average='macro', zero_division=0) if labels_s else float('nan')
            print(f'{phase.capitalize():5s} Loss: {epoch_loss:.4f}  F1-Disease: {f1_d:.4f}  F1-Species: {f1_s:.4f}')

            if phase == 'train':
                history['train_loss'].append(epoch_loss)
            else:
                history['val_loss'].append(epoch_loss)
                history['val_f1_disease'].append(f1_d)
                history['val_f1_species'].append(f1_s)
                combined_score = selection_weight_disease * f1_d + selection_weight_species * f1_s
                history['val_combined_score'].append(combined_score)
                scheduler.step(epoch_loss)

                if combined_score > best_combined_score:
                    best_combined_score = combined_score
                    best_f1_disease_at_best = f1_d
                    best_model_wts = copy.deepcopy(model.state_dict())
                    epochs_no_improve = 0
                    print(f'  -> Model terbaik baru (Skor gabungan: {best_combined_score:.4f})')
                else:
                    epochs_no_improve += 1
        print()

        if checkpoint_path and ((epoch + 1) % save_every == 0 or epoch == num_epochs - 1):
            torch.save({
                'epoch': epoch, 'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(), 'scheduler_state': scheduler.state_dict(),
                'history': history, 'best_model_wts': best_model_wts,
                'best_combined_score': best_combined_score,
                'best_f1_disease_at_best': best_f1_disease_at_best,
                'epochs_no_improve': epochs_no_improve,
            }, checkpoint_path)
            print(f"  [Checkpoint disimpan di epoch {epoch+1}]")

        if epochs_no_improve >= patience:
            print(f'Early stopping di epoch {epoch + 1}')
            break

    print(f'\nTraining selesai dalam {(time.time()-since)//60:.0f}m {(time.time()-since)%60:.0f}s')
    print(f'Best Combined Score: {best_combined_score:.4f} (F1-Disease saat itu: {best_f1_disease_at_best:.4f})')
    model.load_state_dict(best_model_wts)
    return model, history

# --- Cell 14 ---
UNFREEZE_SCHEDULE = {0: 'head_only', 3: 'block4', 10: 'block3_4'}

if CONFIG['FINETUNE_FROM_CHECKPOINT'] and os.path.exists(CONFIG['FINETUNE_CHECKPOINT_PATH']):
    print(f"Memuat checkpoint lama: {CONFIG['FINETUNE_CHECKPOINT_PATH']}")
    model_ft.load_state_dict(torch.load(CONFIG['FINETUNE_CHECKPOINT_PATH'], map_location=device))
    set_unfreeze_stage(model_ft, 'block3_4')

    finetune_optimizer = optim.AdamW(
        [p for p in model_ft.parameters() if p.requires_grad],
        lr=CONFIG['FINETUNE_LR'], weight_decay=1e-4
    )
    finetune_scheduler = lr_scheduler.ReduceLROnPlateau(finetune_optimizer, mode='min', factor=0.5, patience=2)

    model_ft, history = train_model(
        model_ft, dataloaders, dataset_sizes, criterion_disease, criterion_species,
        DISEASE_LOSS_WEIGHT, SPECIES_LOSS_WEIGHT, finetune_optimizer, finetune_scheduler,
        num_epochs=CONFIG['FINETUNE_EPOCHS'], patience=6,
        unfreeze_schedule={0: 'block3_4'},
        use_mixup=CONFIG['USE_MIXUP'], mixup_alpha=CONFIG['MIXUP_ALPHA'], mixup_prob=CONFIG['MIXUP_PROB'],
        use_cutmix=True, use_amp=CONFIG['USE_AMP'],
        selection_weight_disease=0.7, selection_weight_species=0.3,
        checkpoint_path=CHECKPOINT_PATH, save_every=SAVE_EVERY_N_EPOCH
    )
else:
    model_ft, history = train_model(
        model_ft, dataloaders, dataset_sizes, criterion_disease, criterion_species,
        DISEASE_LOSS_WEIGHT, SPECIES_LOSS_WEIGHT, optimizer_ft, exp_lr_scheduler,
        num_epochs=CONFIG['NUM_EPOCHS'], patience=CONFIG['EARLY_STOP_PATIENCE'],
        unfreeze_schedule=UNFREEZE_SCHEDULE, use_mixup=CONFIG['USE_MIXUP'],
        mixup_alpha=CONFIG['MIXUP_ALPHA'], mixup_prob=CONFIG['MIXUP_PROB'],
        use_cutmix=True, use_amp=CONFIG['USE_AMP'],
        selection_weight_disease=0.7, selection_weight_species=0.3,
        checkpoint_path=CHECKPOINT_PATH, save_every=SAVE_EVERY_N_EPOCH
    )

# --- Cell 15 ---
from torch.optim.swa_utils import AveragedModel, update_bn

if CONFIG['USE_SWA']:
    print(f"\n=== Fine-tuning SWA ({CONFIG['SWA_EPOCHS']} epoch tambahan) ===")
    swa_model = AveragedModel(model_ft)
    swa_optimizer = optim.AdamW(model_ft.parameters(), lr=CONFIG['SWA_LR'], weight_decay=1e-4)

    model_ft.train()
    for epoch in range(CONFIG['SWA_EPOCHS']):
        for inputs, labels_disease, labels_species, _, _ in dataloaders['train']:
            inputs = inputs.to(device)
            labels_disease = labels_disease.to(device)
            labels_species = labels_species.to(device)
            swa_optimizer.zero_grad()
            outputs_disease, outputs_species = model_ft(inputs)
            loss_disease = criterion_disease(outputs_disease, labels_disease)
            loss_species = criterion_species(outputs_species, labels_species)
            loss = DISEASE_LOSS_WEIGHT * loss_disease + SPECIES_LOSS_WEIGHT * loss_species
            loss.backward()
            swa_optimizer.step()
        swa_model.update_parameters(model_ft)
        print(f"  SWA epoch {epoch+1}/{CONFIG['SWA_EPOCHS']} selesai")

    update_bn(dataloaders['train'], swa_model, device=device)

    def quick_eval_combined(m, loader, w_disease=0.7, w_species=0.3):
        m.eval()
        preds_d, labels_d, preds_s, labels_s = [], [], [], []
        with torch.no_grad():
            for inputs, labels_disease, labels_species, _, _ in loader:
                inputs = inputs.to(device)
                outputs_disease, outputs_species = m(inputs)
                preds_d.extend(torch.argmax(outputs_disease, dim=1).cpu().numpy())
                labels_d.extend(labels_disease.numpy())
                preds_s.extend(torch.argmax(outputs_species, dim=1).cpu().numpy())
                labels_s.extend(labels_species.numpy())
        f1_d = f1_score(labels_d, preds_d, average='macro', zero_division=0)
        f1_s = f1_score(labels_s, preds_s, average='macro', zero_division=0)
        return w_disease * f1_d + w_species * f1_s, f1_d, f1_s

    score_normal, f1d_normal, f1s_normal = quick_eval_combined(model_ft, dataloaders['val'])
    score_swa, f1d_swa, f1s_swa = quick_eval_combined(swa_model, dataloaders['val'])
    print(f"\nModel biasa -> Skor: {score_normal:.4f} (D:{f1d_normal:.4f}, S:{f1s_normal:.4f})")
    print(f"SWA model   -> Skor: {score_swa:.4f} (D:{f1d_swa:.4f}, S:{f1s_swa:.4f})")

    if score_swa > score_normal:
        print("-> SWA lebih baik, dipakai sebagai model final.")
        model_ft = swa_model.module
    else:
        print("-> Model biasa masih lebih baik, SWA TIDAK dipakai.")
else:
    print("USE_SWA=False, cell SWA dilewati.")

# --- Cell 16 ---
best_epoch = np.argmax(history['val_combined_score']) + 1
best_val_f1_disease = history['val_f1_disease'][best_epoch - 1]
best_val_f1_species = history['val_f1_species'][best_epoch - 1]
best_combined_score = history['val_combined_score'][best_epoch - 1]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(range(1, len(history['train_loss'])+1), history['train_loss'], 'b-o', label='Train Loss')
axes[0].plot(range(1, len(history['val_loss'])+1), history['val_loss'], 'r-o', label='Val Loss')
axes[0].axvline(best_epoch, color='green', linestyle='--', label='Best epoch')
axes[0].set_title(f'Loss — {CONFIG["BACKBONE"].upper()}')
axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Loss'); axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(range(1, len(history['val_f1_disease'])+1), [f*100 for f in history['val_f1_disease']], 'r-o', label='Val F1-Disease')
axes[1].plot(range(1, len(history['val_f1_species'])+1), [f*100 for f in history['val_f1_species']], 'm-o', label='Val F1-Species')
axes[1].axhline(best_combined_score*100, color='green', linestyle='--', label=f'Best gabungan: {best_combined_score*100:.2f}%')
axes[1].set_title(f'Macro-F1 — {CONFIG["BACKBONE"].upper()}')
axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Macro-F1 (%)'); axes[1].legend(); axes[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], f'training_curves_{CONFIG["BACKBONE"]}.png'), dpi=150, bbox_inches='tight')
plt.show()

print(f"Epoch terbaik: {best_epoch} | F1-Disease: {best_val_f1_disease:.4f} | F1-Species: {best_val_f1_species:.4f}")

# --- Cell 17 ---
def evaluate_with_tta(model, dataloader, device):
    model.eval()
    preds_d, labels_d, preds_s, labels_s = [], [], [], []
    with torch.no_grad():
        for inputs, disease_lbl, species_lbl, _, _ in dataloader:
            inputs = inputs.to(device)
            out_d1, out_s1 = model(inputs)
            out_d2, out_s2 = model(torch.flip(inputs, dims=[3]))
            out_d3, out_s3 = model(torch.flip(inputs, dims=[2]))
            out_d4, out_s4 = model(TF.rotate(inputs, 90))
            out_d5, out_s5 = model(TF.rotate(inputs, 270))
            probs_d = sum(F.softmax(o, 1) for o in [out_d1, out_d2, out_d3, out_d4, out_d5]) / 5
            probs_s = sum(F.softmax(o, 1) for o in [out_s1, out_s2, out_s3, out_s4, out_s5]) / 5
            preds_d.extend(torch.argmax(probs_d, 1).cpu().numpy()); labels_d.extend(disease_lbl.numpy())
            preds_s.extend(torch.argmax(probs_s, 1).cpu().numpy()); labels_s.extend(species_lbl.numpy())
    return labels_d, preds_d, labels_s, preds_s


labels_d, preds_d, labels_s, preds_s = evaluate_with_tta(model_ft, dataloaders['test'], device)

report_dict_disease = classification_report(labels_d, preds_d, target_names=class_names, output_dict=True, zero_division=0)
report_dict_species = classification_report(labels_s, preds_s, target_names=species_names, output_dict=True, zero_division=0)

print("=== CLASSIFICATION REPORT — PENYAKIT ===")
print(classification_report(labels_d, preds_d, target_names=class_names, zero_division=0))
print("\n=== CLASSIFICATION REPORT — SPESIES ===")
print(classification_report(labels_s, preds_s, target_names=species_names, zero_division=0))

cm_d = confusion_matrix(labels_d, preds_d)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_d, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.title(f'Confusion Matrix Penyakit — {CONFIG["BACKBONE"].upper()}')
plt.tight_layout(); plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], f'cm_disease_{CONFIG["BACKBONE"]}.png'), dpi=150); plt.show()

cm_s = confusion_matrix(labels_s, preds_s)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_s, annot=True, fmt='d', cmap='Greens', xticklabels=species_names, yticklabels=species_names)
plt.title(f'Confusion Matrix Spesies — {CONFIG["BACKBONE"].upper()}')
plt.tight_layout(); plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], f'cm_species_{CONFIG["BACKBONE"]}.png'), dpi=150); plt.show()

# --- Cell 18 ---
def plot_metrics_per_class(report_dict, names, title_suffix):
    precisions = [report_dict[c]['precision'] * 100 for c in names]
    recalls = [report_dict[c]['recall'] * 100 for c in names]
    f1s = [report_dict[c]['f1-score'] * 100 for c in names]
    fig, axes = plt.subplots(1, 3, figsize=(18, 0.55 * len(names) + 2))
    for ax, (title, values, color) in zip(axes, [('Precision', precisions, 'steelblue'), ('Recall', recalls, 'darkorange'), ('F1-Score', f1s, 'seagreen')]):
        bars = ax.barh(names, values, color=color)
        ax.set_title(title); ax.set_xlim(0, 100)
        for bar, v in zip(bars, values):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{v:.1f}', va='center')
    plt.suptitle(f'Metrik Per Kelas — {title_suffix}', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], f'metrics_{title_suffix.lower().replace(" ", "_")}.png'), dpi=150, bbox_inches='tight')
    plt.show()

plot_metrics_per_class(report_dict_disease, class_names, f'Penyakit - {CONFIG["BACKBONE"].upper()}')
plot_metrics_per_class(report_dict_species, species_names, f'Spesies - {CONFIG["BACKBONE"].upper()}')

# --- Cell 19 ---
class DiseaseOnlyWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
    def forward(self, x):
        disease_out, _ = self.model(x)
        return disease_out

model_ft.eval()
cam_model = DiseaseOnlyWrapper(model_ft)
target_layers = [model_ft.base.features.norm5]
cam = GradCAM(model=cam_model, target_layers=target_layers)

inputs, disease_lbl, species_lbl, paths, display_imgs = next(iter(dataloaders['test']))
inputs_gpu = inputs.to(device)
n_show = min(6, len(inputs))
fig, axes = plt.subplots(n_show, 3, figsize=(13, 4 * n_show))
fig.suptitle('Grad-CAM — Fokus HANYA pada Area Gejala Penyakit', fontsize=15, fontweight='bold')

with torch.no_grad():
    out_d, out_s = model_ft(inputs_gpu)
    conf_d, pred_d = torch.max(F.softmax(out_d, 1), 1)
    conf_s, pred_s = torch.max(F.softmax(out_s, 1), 1)

for i in range(n_show):
    rgb_img = display_imgs[i].numpy().astype(np.float32) / 255.0
    pd_, td_, cd_ = pred_d[i].item(), disease_lbl[i].item(), conf_d[i].item()
    ps_ = species_names[pred_s[i].item()]
    grayscale_cam = cam(input_tensor=inputs_gpu[i:i+1], targets=[ClassifierOutputTarget(pd_)])[0]
    grayscale_cam_resized = cv2.resize(grayscale_cam, (rgb_img.shape[1], rgb_img.shape[0]))
    cam_image = show_cam_on_image(rgb_img, grayscale_cam_resized, use_rgb=True)
    axes[i, 0].imshow(rgb_img); axes[i, 0].set_title(f'Asli\nTrue: {class_names[td_]}'); axes[i, 0].axis('off')
    axes[i, 1].imshow(grayscale_cam_resized, cmap='jet'); axes[i, 1].set_title('Heatmap'); axes[i, 1].axis('off')
    status = "[BENAR]" if pd_ == td_ else "[SALAH]"
    color = 'green' if pd_ == td_ else 'red'
    axes[i, 2].imshow(cam_image)
    axes[i, 2].set_title(f'{status} {class_names[pd_]} ({cd_*100:.0f}%)\nSpesies: {ps_}', color=color, fontweight='bold', fontsize=9)
    axes[i, 2].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(CONFIG['OUTPUT_DIR'], f'gradcam_{CONFIG["BACKBONE"]}.png'), dpi=150, bbox_inches='tight')
plt.show()

# --- Cell 20 ---
class TemperatureScaler(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, x):
        disease_out, species_out = self.model(x)
        return disease_out / self.temperature, species_out

    def calibrate(self, val_loader, device, max_iter=50):
        self.to(device)
        logits_list, labels_list = [], []
        self.model.eval()
        with torch.no_grad():
            for inputs, disease_lbl, species_lbl, _, _ in val_loader:
                inputs = inputs.to(device)
                out_d, _ = self.model(inputs)
                logits_list.append(out_d)
                labels_list.append(disease_lbl.to(device))
        logits = torch.cat(logits_list)
        labels = torch.cat(labels_list)
        optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=max_iter)
        nll_criterion = nn.CrossEntropyLoss()
        def eval_step():
            optimizer.zero_grad()
            loss = nll_criterion(logits / self.temperature, labels)
            loss.backward()
            return loss
        optimizer.step(eval_step)
        print(f"Temperature terkalibrasi: {self.temperature.item():.3f}")
        return self.temperature.item()

temp_scaler = TemperatureScaler(model_ft)
best_temperature = temp_scaler.calibrate(dataloaders['val'], device)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'temperature.json'), 'w') as f:
    json.dump({'temperature': best_temperature}, f)

# --- Cell 21 ---
def predict_for_website(model, pil_image, eval_transform, class_names, species_names,
                         temperature_d=1.0, n_aug=4, device=device, sehat_label='Sehat'):
    model.eval()
    probs_d_all, probs_s_all = [], []
    with torch.no_grad():
        img_t = eval_transform(pil_image).unsqueeze(0).to(device)
        out_d, out_s = model(img_t)
        probs_d_all.append(F.softmax(out_d / temperature_d, dim=1))
        probs_s_all.append(F.softmax(out_s, dim=1))
        tta_transform = transforms.Compose([
            transforms.Resize((CONFIG['IMG_SIZE'], CONFIG['IMG_SIZE'])),
            transforms.RandomHorizontalFlip(p=0.5), transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1), transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN.tolist(), IMAGENET_STD.tolist()),
        ])
        for _ in range(n_aug):
            img_t = tta_transform(pil_image).unsqueeze(0).to(device)
            out_d, out_s = model(img_t)
            probs_d_all.append(F.softmax(out_d / temperature_d, dim=1))
            probs_s_all.append(F.softmax(out_s, dim=1))
    avg_d = torch.mean(torch.cat(probs_d_all, 0), 0)
    avg_s = torch.mean(torch.cat(probs_s_all, 0), 0)
    pred_disease_idx = torch.argmax(avg_d).item()
    pred_species_idx = torch.argmax(avg_s).item()
    disease_name = class_names[pred_disease_idx]
    species_name = species_names[pred_species_idx]
    is_healthy = (disease_name == sehat_label)
    top3_idx = torch.topk(avg_d, min(3, len(class_names))).indices.cpu().numpy()
    top3_conf = torch.topk(avg_d, min(3, len(class_names))).values.cpu().numpy()
    return {
        "spesies": {"nama": species_name, "confidence": round(float(avg_s[pred_species_idx].item())*100, 1)},
        "gejala": {
            "status": "sehat" if is_healthy else "sakit",
            "nama_tampilan": "Tidak terkendala gejala (sehat)" if is_healthy else disease_name,
            "nama_kelas_model": disease_name,
            "confidence": round(float(avg_d[pred_disease_idx].item())*100, 1),
            "top3": [{"nama": class_names[i], "confidence": round(float(c)*100, 1)} for i, c in zip(top3_idx, top3_conf)],
        },
        "faktor_penyebab": None, "penanganan": None,
    }

sample_path = full_dataset.image_paths[test_indices[0]]
sample_img = Image.open(sample_path).convert('RGB')
hasil = predict_for_website(model_ft, sample_img, eval_transform, class_names, species_names, temperature_d=best_temperature)
print(hasil)

# --- Cell 22 ---
model_ft.eval()
example_input = torch.randn(1, 3, CONFIG['IMG_SIZE'], CONFIG['IMG_SIZE']).to(device)
traced_model = torch.jit.trace(model_ft, example_input)
traced_model.save(os.path.join(CONFIG['OUTPUT_DIR'], f'hoya_multitask_{CONFIG["BACKBONE"]}_traced.pt'))

deployment_meta = {
    'class_names': class_names, 'species_names': species_names,
    'img_size': CONFIG['IMG_SIZE'],
    'normalize_mean': IMAGENET_MEAN.tolist(), 'normalize_std': IMAGENET_STD.tolist(),
    'temperature': best_temperature, 'backbone': CONFIG['BACKBONE'],
}
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'deployment_meta.json'), 'w') as f:
    json.dump(deployment_meta, f, indent=2, ensure_ascii=False)

torch.save(model_ft.state_dict(), os.path.join(CONFIG['OUTPUT_DIR'], f'hoya_multitask_{CONFIG["BACKBONE"]}_final.pth'))
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'class_names.json'), 'w') as f:
    json.dump(class_names, f, indent=2, ensure_ascii=False)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'species_names.json'), 'w') as f:
    json.dump(species_names, f, indent=2, ensure_ascii=False)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'training_history.json'), 'w') as f:
    json.dump(history, f, indent=2)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'classification_report_disease.json'), 'w') as f:
    json.dump(report_dict_disease, f, indent=2)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'classification_report_species.json'), 'w') as f:
    json.dump(report_dict_species, f, indent=2)
with open(os.path.join(CONFIG['OUTPUT_DIR'], 'config.json'), 'w') as f:
    json.dump(CONFIG, f, indent=2)

print(f"Semua artefak tersimpan di: {CONFIG['OUTPUT_DIR']}")
print(sorted(os.listdir(CONFIG['OUTPUT_DIR'])))

