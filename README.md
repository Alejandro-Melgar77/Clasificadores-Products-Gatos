# 📱 Sistema de Reconocimiento Visual con IA y Apps Móviles

Este repositorio contiene dos proyectos independientes completos, cada uno con su propio **Backend FastAPI con IA** y su **Aplicación Móvil Flutter con soporte de cámara nativa**:

---

## 📂 Organización del Proyecto

```
clasificador IMAGEN/
├── tienda_productos/                  # Proyecto 1: Tienda Inteligente (8 productos)
│   ├── backend/
│   │   ├── app/                      # Servidor FastAPI e inferencia ONNX
│   │   ├── ml/                       # Scripts de dataset, entrenamiento y exportación ONNX
│   │   ├── models/                   # product_model.onnx (~0.26 MB) y .pth
│   │   ├── data/                     # Base de datos SQLite (inventario) y muestras
│   │   ├── Dockerfile                # Despliegue en Render / Hugging Face
│   │   ├── requirements.txt
│   │   └── test_api.py               # Pruebas automatizadas de API
│   └── mobile/                       # App Móvil Flutter con Cámara y Catálogo
│       ├── lib/
│       ├── test/
│       └── pubspec.yaml
│
└── perros_gatos/                      # Proyecto 2: Clasificador Perro / Gato / Ninguno
    ├── backend/
    │   ├── app/                      # Servidor FastAPI e inferencia ONNX (rechazo seguro)
    │   ├── ml/                       # Dataset builder, entrenamiento y exportación ONNX
    │   ├── models/                   # pet_classifier.onnx (~0.26 MB)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── test_api.py               # Pruebas automatizadas
    └── mobile/                       # App Móvil Flutter con Cámara y Medidor de Certeza
        ├── lib/
        ├── test/
        └── pubspec.yaml
```

---

## ⚡ Inicio Rápido (Comandos Principales)

### Proyecto 1: Tienda de Productos
```bash
# 1. Probar backend
python tienda_productos/backend/test_api.py

# 2. Iniciar servidor FastAPI (Puerto 8000)
python -m uvicorn tienda_productos.backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Iniciar App Móvil
cd tienda_productos/mobile
flutter run
```

### Proyecto 2: Perros, Gatos o Ninguno
```bash
# 1. Probar backend
python perros_gatos/backend/test_api.py

# 2. Iniciar servidor FastAPI (Puerto 8001)
python -m uvicorn perros_gatos.backend.app.main:app --host 0.0.0.0 --port 8001 --reload

# 3. Iniciar App Móvil
cd perros_gatos/mobile
flutter run
```

---

## ☁️ Despliegue Gratuito en la Nube
Ambos backends están optimizados para consumir **menos de 90 MB de memoria RAM** gracias al motor de inferencia **ONNX Runtime**, lo que garantiza que no superarán los límites de plataformas gratuitas como **Render (512 MB RAM)** o **Hugging Face Spaces (16 GB RAM)**. Consulta el archivo `README.md` de cada subcarpeta para ver los pasos detallados de despliegue.
