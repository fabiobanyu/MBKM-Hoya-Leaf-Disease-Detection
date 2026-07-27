import os
import io
import json
import base64
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import numpy as np
import cv2
from neo4j import GraphDatabase
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, render_template
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from model_utils import build_model, DiseaseOnlyWrapper
import sys
import importlib

# Resolve the root directory of the project (d:\KP\WebEval)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import Mobile_V3
MiniCNNGuard = Mobile_V3.MiniCNNGuard

app = Flask(__name__, 
            template_folder=os.path.join(ROOT_DIR, 'Frontend', 'templates'),
            static_folder=os.path.join(ROOT_DIR, 'Frontend', 'static'))
app.config['UPLOAD_FOLDER'] = os.path.join(ROOT_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load configuration and labels
MODELS_DIR = os.path.join(ROOT_DIR, 'models')

# Database configuration
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "12345678"

try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    print("Neo4j driver initialized.")
except Exception as e:
    print("Error initializing Neo4j driver:", e)
    neo4j_driver = None

# Load class names
try:
    with open(os.path.join(MODELS_DIR, "class_names.json"), 'r') as f:
        class_names = json.load(f)
    with open(os.path.join(MODELS_DIR, "species_names.json"), 'r') as f:
        species_names = json.load(f)
except FileNotFoundError:
    class_names = []
    species_names = []

# Initialize model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Loading model to {device}...")
model = build_model(num_disease=len(class_names), num_species=len(species_names))

# Load Main DenseNet121 Multitask Model
MAIN_MODEL_PATH = os.path.join(ROOT_DIR, 'models/DenseNet-121 - Final Model.pth')
if not os.path.exists(MAIN_MODEL_PATH):
    MAIN_MODEL_PATH = os.path.join(ROOT_DIR, 'models/hoya_unified_densenet121.pth')

try:
    model.load_state_dict(torch.load(MAIN_MODEL_PATH, map_location=device), strict=False)
    model.to(device)
    model.eval()
    print("Main DenseNet121 model loaded successfully.")
except Exception as e:
    print(f"Error loading main model: {e}")

# Load Standalone Mini-CNN Guard Model
GUARD_MODEL_PATH = os.path.join(ROOT_DIR, 'models/MobileNetV3 Small - Guard Final Model.pth')
guard_model = MiniCNNGuard(pretrained=False).to(device)
if os.path.exists(GUARD_MODEL_PATH):
    guard_model.load_state_dict(torch.load(GUARD_MODEL_PATH, map_location=device))
    guard_model.eval()
    print("Mini-CNN Guard model loaded successfully.")
else:
    print(f"Warning: Mini-CNN Guard model not found at {GUARD_MODEL_PATH}")

target_layers = [model.attention]

cam_model = DiseaseOnlyWrapper(model)
cam = GradCAM(model=cam_model, target_layers=target_layers)

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

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
IMG_SIZE = 224 # Fixed to match the trained model

class LetterboxPad:
    def __init__(self, target_size=(224, 224), fill_color=(0, 0, 0)):
        self.target_size = target_size
        self.fill_color = fill_color

    def __call__(self, img):
        img_w, img_h = img.size
        target_w, target_h = self.target_size
        scale = min(target_w / img_w, target_h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", self.target_size, self.fill_color)
        new_img.paste(img, ((target_w - new_w) // 2, (target_h - new_h) // 2))
        return new_img

eval_transform = transforms.Compose([
    LetterboxPad(target_size=(IMG_SIZE, IMG_SIZE)),
    AdaptiveSharpen(blur_threshold=100.0, sharpen_strength=1.2),
    CLAHETransform(),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = Image.open(file.stream).convert('RGB')
        
        # 1. Cek Resolusi (terlalu kecil)
        width, height = image.size
        if width < 100 or height < 100:
            return jsonify({
                'error': 'Gambar Terdeteksi Bukan Daun Hoya. Ukuran gambar terlalu kecil, harap gunakan foto yang lebih besar.',
                'error_type': 'noise'
            })
            
        # 2. Cek Kualitas Gambar (terlalu buram/burik)
        img_np = np.array(image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 3.0:
            return jsonify({
                'error': 'Gambar Terdeteksi Bukan Daun Hoya. Foto terlalu buram atau tidak fokus, harap foto ulang daun dengan lebih jelas.',
                'error_type': 'noise'
            })
            
        input_tensor = eval_transform(image).unsqueeze(0).to(device)
        
        # Inference
        with torch.no_grad():
            # 3. Standalone Mini-CNN Guard Check (MobileNetV3-Small: Hoya vs Non-Hoya)
            guard_logit = guard_model(input_tensor)
            is_hoya_prob = torch.sigmoid(guard_logit).item()
            print(f"Mini-CNN Guard (MobileNetV3) Hoya probability: {is_hoya_prob*100:.2f}%", flush=True)

            if is_hoya_prob < 0.50:
                return jsonify({
                    'error': 'Gambar Terdeteksi Bukan Daun Hoya. Sistem mendeteksi objek ini bukan daun Hoya (tanaman/objek lain). Harap pastikan foto memperlihatkan daun Hoya.',
                    'error_type': 'noise'
                })

            # 4. Main DenseNet121 Multitask Prediction
            _, disease_out, species_out = model(input_tensor)

            conf_d_all = F.softmax(disease_out, 1)[0]
            conf_s_all = F.softmax(species_out, 1)[0]
            
            conf_d, pred_d = torch.max(conf_d_all, 0)
            conf_s, pred_s = torch.max(conf_s_all, 0)
            
            pred_d_idx = pred_d.item()
            pred_s_idx = pred_s.item()
            
            disease_name = class_names[pred_d_idx]
            species_name = species_names[pred_s_idx]
            
            # 5. Low-Confidence Filter (Academic Research OOD Standard: Disease < 50% or Species < 45%)
            conf_d_pct = round(conf_d.item() * 100, 1)
            conf_s_pct = round(conf_s.item() * 100, 1)
            
            is_low_confidence = (conf_d.item() < 0.50 or conf_s.item() < 0.45)
            if is_low_confidence:
                pct_details = f" (Tingkat Kepastian AI: Penyakit {conf_d_pct}% < 50%, Spesies {conf_s_pct}% < 45%)."
                return jsonify({
                    'error': 'Sistem kesulitan mengenali daun Hoya ini secara pasti. Hal ini biasa terjadi akibat sudut pengambilan foto, pantulan cahaya, atau fokus crop yang kurang pas. Harap coba foto ulang lebih dekat dan terang.' + pct_details,
                    'error_type': 'confidence'
                })
            
            top3_d = torch.topk(conf_d_all, 3)
            top3_diseases = [{'nama': class_names[i], 'confidence': round(v.item()*100, 2)} for v, i in zip(top3_d.values, top3_d.indices)]
            
        # Grad-CAM
        grayscale_cam = cam(input_tensor=input_tensor, targets=[ClassifierOutputTarget(pred_d_idx)])[0]
        
        # Prepare image for visualization (using letterbox)
        letterboxed_img = LetterboxPad(target_size=(IMG_SIZE, IMG_SIZE))(image)
        img_np = np.array(letterboxed_img, dtype=np.float32) / 255.0
        cam_image = show_cam_on_image(img_np, grayscale_cam, use_rgb=True)
        
        # Convert to base64
        cam_pil = Image.fromarray(cam_image)
        buffered = io.BytesIO()
        cam_pil.save(buffered, format="JPEG")
        cam_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        original_buffered = io.BytesIO()
        letterboxed_img.save(original_buffered, format="JPEG")
        orig_b64 = base64.b64encode(original_buffered.getvalue()).decode('utf-8')

        # ---------------------------------------------------------
        # Neo4j Knowledge Graph Query
        # ---------------------------------------------------------
        knowledge_data = []
        if neo4j_driver and disease_name.lower() != 'sehat':
            try:
                with neo4j_driver.session() as session:
                    query = """
                    MATCH (n)
                    WHERE (n:Disease OR n:Pest) AND n.category = $category
                    OPTIONAL MATCH (n)-[:HAS_SYMPTOM]->(s:Symptom)
                    OPTIONAL MATCH (n)-[:FAVORED_BY]->(c:CausalFactor)
                    OPTIONAL MATCH (n)-[:TREATED_WITH]->(t:Treatment)
                    RETURN labels(n)[0] AS type, n.name_id AS d_id, n.name_en AS d_en,
                           collect(DISTINCT {id: s.name_id, en: s.name_en}) AS symptoms,
                           collect(DISTINCT {id: c.name_id, en: c.name_en}) AS causes,
                           collect(DISTINCT {id: t.name_id, en: t.name_en}) AS treatments
                    """
                    result_records = session.run(query, category=disease_name)
                    for record in result_records:
                        # Clean up potentially empty lists of nulls if no relationships exist
                        symptoms = [s for s in record["symptoms"] if s.get("id")]
                        causes = [c for c in record["causes"] if c.get("id")]
                        treatments = [t for t in record["treatments"] if t.get("id")]
                        
                        knowledge_data.append({
                            "type": record["type"],
                            "disease_id": record["d_id"],
                            "disease_en": record["d_en"],
                            "symptoms": symptoms,
                            "causes": causes,
                            "treatments": treatments
                        })
            except Exception as e:
                print("Neo4j query error:", e)

        result = {
            'success': True,
            'disease': {
                'name': disease_name,
                'confidence': round(conf_d.item() * 100, 2),
                'top3': top3_diseases,
                'status': 'sehat' if disease_name.lower() == 'sehat' else 'sakit'
            },
            'species': {
                'name': species_name,
                'confidence': round(conf_s.item() * 100, 2)
            },
            'images': {
                'original': f"data:image/jpeg;base64,{orig_b64}",
                'gradcam': f"data:image/jpeg;base64,{cam_b64}"
            },
            'knowledge': knowledge_data
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
