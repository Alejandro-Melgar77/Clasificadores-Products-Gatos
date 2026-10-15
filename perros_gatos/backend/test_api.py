import os
import sys
from io import BytesIO
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("TESTEANDO BACKEND FASTAPI - CLASIFICADOR PERRO / GATO / NINGUNO")
    print("=" * 60)
    
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    print(f"[OK] GET /health -> {res.json()['status']}, Clases: {res.json()['classes']}")
    
    # 2. Test samples
    tests = [
        ("perro.jpg", "perro", "Perro 🐶"),
        ("gato.jpg", "gato", "Gato 🐱"),
        ("ninguno.jpg", "ninguno", "Ninguno ❓"),
    ]
    
    for filename, expected_pred, expected_label in tests:
        filepath = os.path.join("perros_gatos", "backend", "data", "test_samples", filename)
        assert os.path.exists(filepath), f"Falta archivo de prueba: {filepath}"
        
        with open(filepath, "rb") as f:
            files = {"file": (filename, f, "image/jpeg")}
            res = client.post("/predict", files=files)
            
        assert res.status_code == 200, f"Error en /predict: {res.text}"
        data = res.json()
        match = "[OK]" if data["prediction"] == expected_pred else "[FALLO]"
        print(f"{match} Foto: {filename:<14} -> Predicción: {data['label_display']} ({data['confidence']*100:.1f}%)")
        print(f"     -> Probabilidades: {data['probabilities']}")
        
    # 3. Test with random noise / abstract image -> should be 'ninguno'
    print("\n--- TEST DE IMAGEN ARBITRARIA (RECHAZO A NINGUNO) ---")
    noise_img = Image.new("RGB", (224, 224), (200, 200, 200))
    buf = BytesIO()
    noise_img.save(buf, "JPEG")
    buf.seek(0)
    res = client.post("/predict", files={"file": ("noise.jpg", buf, "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    match = "[OK]" if data["prediction"] == "ninguno" else "[FALLO]"
    print(f"{match} Imagen gris/ruido -> Predicción: {data['label_display']} ({data['confidence']*100:.1f}%)")
    print(f"     -> Mensaje: {data['message']}")
    
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS DE CLASIFICADOR DE MASCOTAS PASARON CON ÉXITO")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
