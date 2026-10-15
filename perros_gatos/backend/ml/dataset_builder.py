import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CLASSES = ["perro", "gato", "ninguno"]

IMAGE_FILES = {
    "perro": [
        "Black_Labrador_Retriever_-_Male_IMG_3323_(cropped).jpg",
        "BlkStdSchnauzer2.jpg"
    ],
    "gato": [
        "Cat_poster_1.jpg",
        "Cat_November_2010-1a.jpg"
    ],
    "ninguno": [
        "07-08_Chevrolet_Suburban_LT.jpg",
        "Water_bottle.jpg"
    ]
}

def download_image(filename):
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=600"
    headers = {"User-Agent": "PetClassifierApp/1.0 (contact@domain.com)"}
    try:
        r = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 1000:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img.thumbnail((600, 600))
            return img
    except Exception as e:
        print(f"  [!] Error descargando {filename}: {e}")
    return None

def augment_image(img):
    img = img.convert("RGB")
    angle = random.uniform(-20, 20)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    enh_b = ImageEnhance.Brightness(img)
    img = enh_b.enhance(random.uniform(0.8, 1.25))
    enh_c = ImageEnhance.Contrast(img)
    img = enh_c.enhance(random.uniform(0.8, 1.2))
    w, h = img.size
    crop_scale = random.uniform(0.85, 0.98)
    new_w, new_h = int(w * crop_scale), int(h * crop_scale)
    x1 = random.randint(0, w - new_w)
    y1 = random.randint(0, h - new_h)
    img = img.crop((x1, y1, x1 + new_w, y1 + new_h))
    return img.resize((224, 224), Image.LANCZOS)

def build_dataset(base_dir="perros_gatos/backend/data"):
    dataset_dir = os.path.join(base_dir, "dataset")
    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "val")
    test_samples_dir = os.path.join(base_dir, "test_samples")
    
    for c in CLASSES:
        os.makedirs(os.path.join(train_dir, c), exist_ok=True)
        os.makedirs(os.path.join(val_dir, c), exist_ok=True)
    os.makedirs(test_samples_dir, exist_ok=True)
    
    print("=" * 60)
    print("INICIANDO PREPARACION DE DATASET: PERRO / GATO / NINGUNO")
    print("=" * 60)
    
    labels_path = os.path.join("perros_gatos/backend/ml", "labels.json")
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump({"classes": CLASSES}, f, indent=2)
    print(f"[*] Guardado mapeo de etiquetas en {labels_path}")
    
    for cls_name in CLASSES:
        print(f"\n---> Preparando clase: [{cls_name}]")
        valid_images = []
        files = IMAGE_FILES.get(cls_name, [])
        for fn in files:
            img = download_image(fn)
            if img:
                valid_images.append(img)
                print(f"  [+] Descargada imagen real: {fn} ({img.size})")
                
        # Save sample for testing
        test_sample_path = os.path.join(test_samples_dir, f"{cls_name}.jpg")
        valid_images[0].resize((300, 300)).save(test_sample_path, "JPEG")
        print(f"  [+] Muestra de test guardada en {test_sample_path}")
        
        train_count = 50
        val_count = 15
        
        for i in range(val_count):
            seed = random.choice(valid_images)
            aug = augment_image(seed)
            aug.save(os.path.join(val_dir, cls_name, f"val_{i:03d}.jpg"), "JPEG")
            
        for i in range(train_count):
            seed = random.choice(valid_images)
            aug = augment_image(seed)
            aug.save(os.path.join(train_dir, cls_name, f"train_{i:03d}.jpg"), "JPEG")
            
        print(f"  [OK] Clase [{cls_name}] lista: {train_count} train, {val_count} val.")
        
    print("\n" + "=" * 60)
    print("DATASET DE PERROS / GATOS / NINGUNO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    build_dataset()
