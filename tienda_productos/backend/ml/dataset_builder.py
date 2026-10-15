import os
import sys
import json
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CLASSES = [
    "cocacola",
    "oreo",
    "lays",
    "nescafe",
    "leche_pil",
    "agua_mineral",
    "chocolate_block",
    "cerveza_pacena"
]

PRODUCT_FILES = {
    "cocacola": ["Coca_Cola_Flasche_-_Original_Taste.jpg", "Coca-cola_50cl_can_-_Italia.jpg"],
    "oreo": ["Oreo-Two-Cookies.png"],
    "lays": ["Potato-Chips.jpg"],
    "nescafe": ["Nescafè_instant_coffee,_2019-(01).jpg"],
    "leche_pil": ["Milk_carton.jpg"],
    "agua_mineral": ["Water_bottle.jpg", "Bottled_water.jpg"],
    "chocolate_block": ["Chocolate_bar.jpg", "Dark_chocolate_bar.jpg"],
    "cerveza_pacena": ["Beer_can.jpg"]
}

PRODUCT_BRAND_COLORS = {
    "cocacola": ((220, 20, 30), (255, 255, 255), "Coca-Cola"),
    "oreo": ((0, 45, 120), (255, 255, 255), "OREO"),
    "lays": ((255, 204, 0), (200, 20, 20), "Lay's"),
    "nescafe": ((180, 20, 20), (255, 240, 200), "NESCAFE"),
    "leche_pil": ((0, 90, 180), (255, 255, 255), "PIL LECHE"),
    "agua_mineral": ((0, 160, 220), (255, 255, 255), "VITAL AGUA"),
    "chocolate_block": ((60, 30, 20), (255, 200, 50), "BLOCK CHOCOLATE"),
    "cerveza_pacena": ((218, 165, 32), (180, 0, 0), "PACENA")
}

def create_brand_synthetic_seed(cls_name):
    """Creates a distinct synthetic package seed with brand colors & label."""
    bg_color, fg_color, text = PRODUCT_BRAND_COLORS.get(cls_name, ((100, 100, 100), (255, 255, 255), cls_name))
    img = Image.new("RGB", (400, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # Draw product package body
    draw.rectangle([70, 50, 330, 350], fill=bg_color, outline=(40, 40, 40), width=4)
    # Inner banner
    draw.rectangle([90, 150, 310, 240], fill=fg_color)
    # Text
    draw.text((110, 180), text, fill=bg_color)
    return img

def download_image_from_commons(filename):
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=600"
    headers = {
        "User-Agent": "ProductStoreApp/1.0 (https://github.com/store-app; contact@domain.com)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 1000:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img.thumbnail((600, 600))
            return img
    except Exception as e:
        print(f"  [!] Fallo descarga de {filename}: {e}")
    return None

def augment_image(img):
    """Generates realistic variations mimicking a mobile camera in a store."""
    img = img.convert("RGB")
    
    # 1. Random rotation (-25 to 25 degrees)
    angle = random.uniform(-25, 25)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    
    # 2. Random horizontal flip (50%)
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
    # 3. Brightness variation (simulating store lighting or shadows)
    enh_b = ImageEnhance.Brightness(img)
    img = enh_b.enhance(random.uniform(0.75, 1.3))
    
    # 4. Contrast variation
    enh_c = ImageEnhance.Contrast(img)
    img = enh_c.enhance(random.uniform(0.8, 1.25))
    
    # 5. Color saturation
    enh_col = ImageEnhance.Color(img)
    img = enh_col.enhance(random.uniform(0.8, 1.25))
    
    # 6. Random crop & zoom
    w, h = img.size
    crop_scale = random.uniform(0.82, 0.98)
    new_w, new_h = int(w * crop_scale), int(h * crop_scale)
    x1 = random.randint(0, w - new_w)
    y1 = random.randint(0, h - new_h)
    img = img.crop((x1, y1, x1 + new_w, y1 + new_h))
    
    # 7. Occasional slight blur (simulating phone camera focus)
    if random.random() > 0.6:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 1.0)))
        
    return img.resize((224, 224), Image.LANCZOS)

def build_dataset(base_dir="tienda_productos/backend/data"):
    dataset_dir = os.path.join(base_dir, "dataset")
    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "val")
    test_samples_dir = os.path.join(base_dir, "test_samples")
    
    for c in CLASSES:
        os.makedirs(os.path.join(train_dir, c), exist_ok=True)
        os.makedirs(os.path.join(val_dir, c), exist_ok=True)
    os.makedirs(test_samples_dir, exist_ok=True)
    
    print("=" * 60)
    print("INICIANDO DESCARGA Y PREPARACION DE DATASET (8 PRODUCTOS)")
    print("=" * 60)
    
    # Save labels mapping
    labels_path = os.path.join("tienda_productos/backend/ml", "labels.json")
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump({"classes": CLASSES}, f, indent=2)
    print(f"[*] Guardado mapeo de etiquetas en {labels_path}")
    
    for cls_name in CLASSES:
        print(f"\n---> Preparando clase: [{cls_name}]")
        valid_images = []
        
        # Download real photos
        filenames = PRODUCT_FILES.get(cls_name, [])
        for fn in filenames:
            img = download_image_from_commons(fn)
            if img:
                valid_images.append(img)
                print(f"  [+] Descargada imagen real: {fn} ({img.size})")
                
        # Generate brand synthetic seed
        synthetic_seed = create_brand_synthetic_seed(cls_name)
        valid_images.append(synthetic_seed)
        
        # Save canonical test sample
        test_path = os.path.join(test_samples_dir, f"{cls_name}.jpg")
        valid_images[0].resize((300, 300)).save(test_path, "JPEG")
        print(f"  [+] Muestra de test guardada en {test_path}")
        
        # Generate 45 train images and 12 val images per class
        train_count = 45
        val_count = 12
        
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
    print("EXITO: DATASET DE 8 PRODUCTOS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    build_dataset()
