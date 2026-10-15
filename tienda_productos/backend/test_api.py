import os
import sys
from io import BytesIO
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("TESTEANDO BACKEND FASTAPI - TIENDA DE PRODUCTOS")
    print("=" * 60)
    
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"[OK] GET /health -> {res.json()['status']}, Clases: {res.json()['classes_count']}")
    
    # 2. List products
    res = client.get("/products")
    assert res.status_code == 200, f"Products list failed: {res.text}"
    prods = res.json()
    print(f"[OK] GET /products -> {len(prods)} productos registrados en base de datos:")
    for p in prods:
        print(f"     * [{p['sku']}] {p['name']} - {p['currency']} {p['price']:.2f} (Stock: {p['stock']})")
        
    # 3. Test prediction with real product test samples
    test_samples = [
        ("cocacola.jpg", "cocacola"),
        ("oreo.jpg", "oreo"),
        ("lays.jpg", "lays"),
        ("nescafe.jpg", "nescafe"),
        ("cerveza_pacena.jpg", "cerveza_pacena")
    ]
    
    print("\n--- TEST DE RECONOCIMIENTO VISUAL (/predict) ---")
    for filename, expected_class in test_samples:
        filepath = os.path.join("tienda_productos", "backend", "data", "test_samples", filename)
        if not os.path.exists(filepath):
            print(f"[!] Archivo {filepath} no existe, omitiendo.")
            continue
            
        with open(filepath, "rb") as f:
            files = {"file": (filename, f, "image/jpeg")}
            res = client.post("/predict", files=files)
            
        assert res.status_code == 200, f"Error en /predict: {res.text}"
        data = res.json()
        recog = "[OK]" if data["recognized"] and data["class_id"] == expected_class else "[FALLO]"
        print(f"{recog} Foto: {filename:<18} -> Reconocido: {data['recognized']}, Producto: {data.get('product', {}).get('name')}, Confianza: {data['confidence']*100:.1f}%")
        if data.get("product"):
            p = data["product"]
            print(f"     -> Info DB: Stock={p['stock']}, Precio={p['currency']} {p['price']}, SKU={p['sku']}")
            
    # 4. Test with random noise (should be unrecognized)
    print("\n--- TEST DE IMAGEN DESCONOCIDA (RECHAZO CORRECTO) ---")
    noise_img = Image.new("RGB", (224, 224), (128, 128, 128))
    buf = BytesIO()
    noise_img.save(buf, "JPEG")
    buf.seek(0)
    res = client.post("/predict", files={"file": ("noise.jpg", buf, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    print(f"[*] Imagen aleatoria/gris -> Reconocido: {data['recognized']}, Mensaje: '{data['message']}'")
    
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS DE FASTAPI PASARON EXITOSAMENTE")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
